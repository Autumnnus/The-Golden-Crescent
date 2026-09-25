"""Audit Lehistan–Litvanya POP output, protected legacy professions, cities and unchanged map."""

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
CANDIDATE = ROOT / "build/demography/poland-candidate.yml"
EXPECTED = ROOT / "build/demography/poland-plan-audit.json"
BASE_POPS = ROOT / "common/history/pops/tgc_pops.txt"
NEW_POPS = ROOT / "build/scenarios/poland-demography-candidate/common/history/pops/tgc_pops.txt"
REPORT = ROOT / "build/demography/poland-candidate-report.json"
OUT = ROOT / "build/demography/poland-verification.json"


def group_key(pop) -> str:
    key = f"{pop.get_str('culture')}/{pop.get_str('religion')}"
    pop_type = pop.get_str("pop_type")
    return f"{key}/{pop_type}" if pop_type else key


def main() -> None:
    source = yaml.safe_load(SOURCE.read_text())
    candidate = yaml.safe_load(CANDIDATE.read_text())
    expected = json.loads(EXPECTED.read_text())
    report = json.loads(REPORT.read_text())
    design_plan = yaml.safe_load((HERE / "plan.yml").read_text())
    legacy = json.loads((HERE / "legacy-population-snapshot.json").read_text())
    errors = []
    for key in ("version", "countries", "subject_types", "diplomacy"):
        if source.get(key) != candidate.get(key):
            errors.append(f"changed {key}")
    if set(source["states"]) != set(candidate["states"]):
        errors.append("changed state set")
    for state, old in source["states"].items():
        new = candidate["states"].get(state, {})
        if {k: v for k, v in old.items() if k != "population"} != {k: v for k, v in new.items() if k != "population"}:
            errors.append(f"{state}: changed political or building data")
        protected = set(old.get("population", {}).get("by_owner", {})) - ({"VPL"} if state in expected["states"] else set())
        old_other = {tag: value for tag, value in old.get("population", {}).get("by_owner", {}).items() if tag in protected}
        new_other = {tag: value for tag, value in new.get("population", {}).get("by_owner", {}).items() if tag in protected}
        if old_other != new_other:
            errors.append(f"{state}: changed another owner's population plan")
        if state not in expected["states"] and old.get("population") != new.get("population"):
            errors.append(f"{state}: unplanned state population changed")

    baseline = pdx.parse_file(BASE_POPS).get_node("POPS")
    emitted = pdx.parse_file(NEW_POPS).get_node("POPS")
    changed_states = set(expected["states"])
    for block in baseline.items:
        new_state = emitted.get_node(block.key)
        if new_state is None:
            errors.append(f"{block.key}: emitted state missing")
            continue
        for item in block.value.items:
            if block.key.removeprefix("s:") in changed_states and item.key == "region_state:VPL":
                continue
            other = new_state.get_node(item.key)
            if other is None or pdx.dumps(item.value) != pdx.dumps(other):
                errors.append(f"{block.key}/{item.key}: unrelated POPs changed")

    actual_joint: dict[str, Counter[str]] = {}
    fixed_total = 0
    slave_total = 0
    tatar_total = 0
    for state, plan in expected["states"].items():
        node = emitted.get_node("s:" + state).get_node("region_state:VPL")
        actual: Counter[str] = Counter()
        joint: Counter[str] = Counter()
        for pop in node.getall("create_pop"):
            key = group_key(pop)
            size = pop.get_int("size")
            actual[key] += size
            joint["/".join(key.split("/")[:2])] += size
            if pop.get_str("pop_type") == "slaves":
                slave_total += size
            if pop.get_str("culture") == "tatar" and pop.get_str("religion") == "sunni":
                tatar_total += size
        if dict(actual) != plan["groups"]:
            errors.append(f"{state}: output joint culture/religion/profession differs")
        frozen_fixed = Counter()
        for row in legacy[state]:
            if row["pop_type"]:
                frozen_fixed[f"{row['culture']}/{row['religion']}/{row['pop_type']}"] += row["size"]
        if any(plan["fixed_legacy_groups"].get(key) != size for key, size in frozen_fixed.items()):
            errors.append(f"{state}: frozen profession headcounts not preserved")
        for key, size in plan["fixed_legacy_groups"].items():
            if actual[key] != size:
                errors.append(f"{state}: inherited group {key} changed")
            if len(key.split("/")) == 3:
                fixed_total += size
        if report["states"][state]["owners"]["VPL"]["population"] != plan["population"]:
            errors.append(f"{state}: report population differs")
        if report["states"][state]["owners"]["VPL"]["settings"].get("literacy") != plan["literacy"]:
            errors.append(f"{state}: literacy input differs")
        actual_joint[state] = joint

    cities = yaml.safe_load((HERE / "city-profiles.yml").read_text())["cities"]
    city_by_state: dict[str, Counter[str]] = {}
    for city, profile in cities.items():
        state = profile["state"]
        if state not in actual_joint:
            errors.append(f"{city}: city outside Commonwealth phase")
            continue
        weights = profile["weights"]
        if sum(weights.values()) != 1000:
            errors.append(f"{city}: joint weights do not total 1000")
            continue
        row = city_by_state.setdefault(state, Counter())
        for group, weight in weights.items():
            amount, residue = divmod(profile["population"] * weight, 1000)
            if residue:
                errors.append(f"{city}: {group} has fractional headcount")
            row[group] += amount
    for state, groups in city_by_state.items():
        for group, amount in groups.items():
            if amount > actual_joint[state][group]:
                errors.append(f"{state}: cities exceed state-share {group}")
        if sum(groups.values()) > expected["states"][state]["population"]:
            errors.append(f"{state}: cities exceed total state-share population")

    if report["countries"]["VPL"]["population"] != expected["target_population"]:
        errors.append("Commonwealth country population differs")
    literacy = sum(row["population"] * row["literacy"] for row in expected["states"].values()) / expected["target_population"]
    if not design_plan["literacy_target"][0] <= literacy <= design_plan["literacy_target"][1]:
        errors.append("weighted literacy outside written Commonwealth target")
    old_slaves = sum(row["size"] for rows in legacy.values() for row in rows if row["pop_type"] == "slaves")
    if slave_total != old_slaves:
        errors.append("inherited enslaved POP headcount changed")
    if not 25000 <= tatar_total <= 50000:
        errors.append("Tatar Muslim minority outside planned scale")
    result = {
        "passed": not errors and report["validation"] == "passed",
        "state_shares": len(changed_states), "population": expected["target_population"],
        "weighted_literacy_input": literacy, "legacy_fixed_profession_population": fixed_total,
        "legacy_enslaved_population": slave_total, "tatar_sunni_population": tatar_total,
        "reviewed_city_hubs": len(cities),
        "city_hub_population_estimate": sum(city["population"] for city in cities.values()),
        "other_pop_blocks_unchanged": not any("unrelated POPs changed" in error for error in errors),
        "errors": errors,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (passed={result['passed']})")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
