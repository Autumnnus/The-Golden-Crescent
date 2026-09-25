"""Audit seven Iran members, other POP blocks, fixed occupations and cities."""

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
CANDIDATE = ROOT / "build/demography/iran-candidate.yml"
EXPECTED = ROOT / "build/demography/iran-plan-audit.json"
BASE_POPS = ROOT / "common/history/pops/tgc_pops.txt"
NEW_POPS = ROOT / "build/scenarios/iran-demography-candidate/common/history/pops/tgc_pops.txt"
REPORT = ROOT / "build/demography/iran-candidate-report.json"
OUT = ROOT / "build/demography/iran-verification.json"


def group_key(pop) -> str:
    key = f"{pop.get_str('culture')}/{pop.get_str('religion')}"
    pop_type = pop.get_str("pop_type")
    return f"{key}/{pop_type}" if pop_type else key


def main() -> None:
    source = yaml.safe_load(SOURCE.read_text())
    candidate = yaml.safe_load(CANDIDATE.read_text())
    expected = json.loads(EXPECTED.read_text())
    report = json.loads(REPORT.read_text())
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
            errors.append(f"{state}: political or building data changed")
        owner = expected["states"].get(state, {}).get("owner")
        old_other = {tag: value for tag, value in old.get("population", {}).get("by_owner", {}).items() if tag != owner}
        new_other = {tag: value for tag, value in new.get("population", {}).get("by_owner", {}).items() if tag != owner}
        if old_other != new_other:
            errors.append(f"{state}: another owner's population changed")

    baseline = pdx.parse_file(BASE_POPS).get_node("POPS")
    emitted = pdx.parse_file(NEW_POPS).get_node("POPS")
    for block in baseline.items:
        new_state = emitted.get_node(block.key)
        if new_state is None:
            errors.append(f"{block.key}: emitted state missing")
            continue
        state = block.key.removeprefix("s:")
        owner = expected["states"].get(state, {}).get("owner")
        for item in block.value.items:
            if owner and item.key == f"region_state:{owner}":
                continue
            other = new_state.get_node(item.key)
            if other is None or pdx.dumps(item.value) != pdx.dumps(other):
                errors.append(f"{block.key}/{item.key}: unrelated POPs changed")

    actual_joint: dict[str, Counter[str]] = {}
    old_slaves = sum(row["size"] for owners in legacy.values() for rows in owners.values()
                     for row in rows if row["pop_type"] == "slaves")
    new_slaves = 0
    for state, design in expected["states"].items():
        owner = design["owner"]
        node = emitted.get_node("s:" + state).get_node("region_state:" + owner)
        actual: Counter[str] = Counter()
        joint: Counter[str] = Counter()
        for pop in node.getall("create_pop"):
            key = group_key(pop)
            size = pop.get_int("size")
            actual[key] += size
            joint["/".join(key.split("/")[:2])] += size
            if pop.get_str("pop_type") == "slaves":
                new_slaves += size
        if dict(actual) != design["groups"]:
            errors.append(f"{state}/{owner}: joint/profession groups differ")
        for group, size in design["fixed_legacy_groups"].items():
            if actual[group] != size:
                errors.append(f"{state}/{owner}: fixed legacy group {group} differs")
        owner_report = report["states"][state]["owners"][owner]
        if owner_report["population"] != design["population"]:
            errors.append(f"{state}/{owner}: report population differs")
        if owner_report["settings"].get("literacy") != design["literacy"]:
            errors.append(f"{state}/{owner}: literacy input differs")
        actual_joint[state] = joint
    if old_slaves != new_slaves:
        errors.append("inherited enslaved POP headcount changed")

    cities = yaml.safe_load((HERE / "city-profiles.yml").read_text())["cities"]
    city_by_state: dict[str, Counter[str]] = {}
    for city, profile in cities.items():
        state = profile["state"]
        if state not in actual_joint or profile["owner"] != expected["states"][state]["owner"]:
            errors.append(f"{city}: city outside matching member share")
            continue
        if sum(profile["weights"].values()) != 1000:
            errors.append(f"{city}: weights do not total 1000")
            continue
        row = city_by_state.setdefault(state, Counter())
        for group, weight in profile["weights"].items():
            amount, residue = divmod(profile["population"] * weight, 1000)
            if residue:
                errors.append(f"{city}/{group}: fractional headcount")
            row[group] += amount
    for state, groups in city_by_state.items():
        for group, amount in groups.items():
            if amount > actual_joint[state][group]:
                errors.append(f"{state}: cities exceed group {group}")
        if sum(groups.values()) > expected["states"][state]["population"]:
            errors.append(f"{state}: cities exceed total share")

    member_literacy = {}
    for tag, target in expected["countries"].items():
        if report["countries"][tag]["population"] != target["population"]:
            errors.append(f"{tag}: member population differs")
        rows = [d for d in expected["states"].values() if d["owner"] == tag]
        literacy = sum(d["population"] * d["literacy"] for d in rows) / target["population"]
        member_literacy[tag] = literacy
        if not target["literacy_range"][0] <= literacy <= target["literacy_range"][1]:
            errors.append(f"{tag}: weighted literacy outside written range")
    result = {
        "passed": not errors and report["validation"] == "passed",
        "member_count": len(expected["countries"]), "state_shares": len(expected["states"]),
        "population": sum(d["population"] for d in expected["countries"].values()),
        "member_literacy_inputs": member_literacy,
        "legacy_enslaved_population": new_slaves,
        "reviewed_city_hubs": len(cities),
        "city_hub_population_estimate": sum(d["population"] for d in cities.values()),
        "other_pop_blocks_unchanged": not any("unrelated POPs changed" in error for error in errors),
        "errors": errors,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (passed={result['passed']})")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
