"""Audit Indian population groups, city subsets and protected world shares."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLKIT = Path(
    os.environ.get("VIC3_TOOLS_HOME")
    or json.loads((ROOT / ".vic3-tools.local.json").read_text(encoding="utf-8"))["toolkit"]
).expanduser().resolve()
if sys.version_info < (3, 10):
    runtime = TOOLKIT / ".venv/bin/python"
    os.execv(str(runtime), [str(runtime), __file__, *sys.argv[1:]])
sys.path.insert(0, str(TOOLKIT / "src"))
from vic3 import pdx  # noqa: E402


SOURCE = ROOT / "world/scenario.yml"
CANDIDATE = ROOT / "build/demography/indian-core-candidate.yml"
AUDIT = ROOT / "build/demography/indian-core-plan-audit.json"
REPORT = ROOT / "build/demography/indian-core-candidate-report.json"
BASE_POPS = ROOT / "common/history/pops/tgc_pops.txt"
NEW_POPS = ROOT / "build/scenarios/indian-core-candidate/common/history/pops/tgc_pops.txt"
OUT = ROOT / "build/demography/indian-core-verification.json"


def group_key(pop) -> str:
    value = f"{pop.get_str('culture')}/{pop.get_str('religion')}"
    pop_type = pop.get_str("pop_type")
    return f"{value}/{pop_type}" if pop_type else value


def main() -> None:
    source = yaml.safe_load(SOURCE.read_text())
    candidate = yaml.safe_load(CANDIDATE.read_text())
    audit = json.loads(AUDIT.read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    legacy = json.loads((HERE / "legacy-population-snapshot.json").read_text())
    report = json.loads(REPORT.read_text())
    errors = []
    for key in ("version", "countries", "subject_types", "diplomacy"):
        if source.get(key) != candidate.get(key):
            errors.append(f"changed {key}")
    if set(source["states"]) != set(candidate["states"]):
        errors.append("changed state set")
    target = {(row["state"], row["owner"]) for row in audit["shares"].values()}
    for state, old in source["states"].items():
        new = candidate["states"].get(state, {})
        if {k: v for k, v in old.items() if k != "population"} != {k: v for k, v in new.items() if k != "population"}:
            errors.append(f"{state}: political/building fields changed")
        old_by = old.get("population", {}).get("by_owner", {})
        new_by = new.get("population", {}).get("by_owner", {})
        for tag in set(old_by) | set(new_by):
            if (state, tag) not in target and old_by.get(tag) != new_by.get(tag):
                errors.append(f"{state}/{tag}: unrelated population plan changed")
        if state not in plan["states"] and old.get("population") != new.get("population"):
            errors.append(f"{state}: unrelated state population changed")

    before = pdx.parse_file(BASE_POPS).get_node("POPS")
    after = pdx.parse_file(NEW_POPS).get_node("POPS")
    for state_block in before.items:
        new_state = after.get_node(state_block.key)
        if new_state is None:
            errors.append(f"{state_block.key}: emitted state missing")
            continue
        state = state_block.key.removeprefix("s:")
        for owner_block in state_block.value.items:
            tag = owner_block.key.removeprefix("region_state:")
            if (state, tag) in target:
                continue
            other = new_state.get_node(owner_block.key)
            if other is None or pdx.dumps(owner_block.value) != pdx.dumps(other):
                errors.append(f"{state_block.key}/{owner_block.key}: unrelated POPs changed")

    actual_joint: dict[str, Counter[str]] = {}
    protected_profession_total = 0
    for key, design in audit["shares"].items():
        state, tag = design["state"], design["owner"]
        node = after.get_node("s:" + state).get_node("region_state:" + tag)
        actual = Counter()
        joint = Counter()
        for pop in node.getall("create_pop"):
            group = group_key(pop)
            size = pop.get_int("size")
            actual[group] += size
            joint["/".join(group.split("/")[:2])] += size
            if tag == "BGL" and pop.get_str("pop_type") == "slaves":
                errors.append(f"{key}: enslaved POP reintroduced")
            if pop.get_str("culture") in {"british", "scottish"} and pop.get_str("pop_type") in {"bureaucrats", "officers", "aristocrats"}:
                errors.append(f"{key}: colonial administrative POP reintroduced")
        if dict(actual) != design["groups"]:
            errors.append(f"{key}: joint culture/religion/profession differs")
        frozen_fixed = Counter()
        for row in legacy[state][tag]:
            if row["pop_type"]:
                frozen_fixed[f"{row['culture']}/{row['religion']}/{row['pop_type']}"] += row["size"]
        for group, size in frozen_fixed.items():
            if design["fixed_legacy_groups"].get(group) != size or actual[group] != size:
                errors.append(f"{key}: frozen profession {group} differs")
            protected_profession_total += size
        owner_report = report["states"][state]["owners"][tag]
        if owner_report["population"] != design["population"]:
            errors.append(f"{key}: report population differs")
        if owner_report["settings"].get("literacy") != design["literacy"]:
            errors.append(f"{key}: report literacy differs")
        actual_joint[key] = joint

    cities = yaml.safe_load((HERE / "city-profiles.yml").read_text())["cities"]
    city_by_share: dict[str, Counter[str]] = {}
    for city, profile in cities.items():
        key = f"{profile['state']}/{profile['owner']}"
        if key not in actual_joint or profile["hub"] not in {"city", "port", "farm", "mine", "wood"}:
            errors.append(f"{city}: city outside matching share or invalid hub")
            continue
        if sum(profile["weights"].values()) != 1000:
            errors.append(f"{city}: weights do not total 1000")
            continue
        subtotal = city_by_share.setdefault(key, Counter())
        for group, weight in profile["weights"].items():
            amount, residue = divmod(profile["population"] * weight, 1000)
            if residue:
                errors.append(f"{city}/{group}: fractional headcount")
            subtotal[group] += amount
    for key, groups in city_by_share.items():
        for group, amount in groups.items():
            if amount > actual_joint[key][group]:
                errors.append(f"{key}: city profile exceeds {group}")
        if sum(groups.values()) > audit["shares"][key]["population"]:
            errors.append(f"{key}: cities exceed total share")

    literacy_inputs = {}
    for tag, target_country in plan["countries"].items():
        rows = [row for row in audit["shares"].values() if row["owner"] == tag]
        edited_population = sum(row["population"] for row in rows)
        literacy = sum(row["population"] * row["literacy"] for row in rows) / edited_population
        literacy_inputs[tag] = literacy
        if not target_country["literacy_range"][0] <= literacy <= target_country["literacy_range"][1]:
            errors.append(f"{tag}: weighted literacy input outside written range")
        if report["countries"][tag]["population"] != target_country["population"]:
            errors.append(f"{tag}: country population target differs")
    maratha_total = sum(report["countries"][tag]["population"] for tag in ("MAR", "GWA", "IND", "NAG"))
    if maratha_total != plan["maratha_member_total"]:
        errors.append("Maratha members do not add to federation target")
    result = {
        "passed": not errors and report["validation"] == "passed",
        "country_tags": len(plan["countries"]), "edited_state_shares": len(target),
        "maratha_member_total": maratha_total, "weighted_literacy_inputs": literacy_inputs,
        "protected_profession_population": protected_profession_total,
        "reviewed_city_hubs": len(cities),
        "city_hub_population_estimate": sum(row["population"] for row in cities.values()),
        "other_pop_blocks_unchanged": not any("unrelated POPs changed" in error for error in errors),
        "errors": errors,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (passed={result['passed']})")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
