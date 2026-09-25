"""Audit the Rûm candidate's emitted joint POPs and unchanged political world."""

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
    if not runtime.is_file():
        raise RuntimeError(f"Python 3.10+ runtime is required: {runtime}")
    os.execv(str(runtime), [str(runtime), __file__, *sys.argv[1:]])
sys.path.insert(0, str(TOOLKIT / "src"))
from vic3 import pdx  # noqa: E402


SOURCE = ROOT / "world/scenario.yml"
CANDIDATE = ROOT / "build/demography/rum-candidate.yml"
EXPECTED = ROOT / "build/demography/rum-plan-audit.json"
BASE_POPS = ROOT / "common/history/pops/tgc_pops.txt"
NEW_POPS = ROOT / "build/scenarios/rum-demography-candidate/common/history/pops/tgc_pops.txt"
REPORT = ROOT / "build/demography/rum-candidate-report.json"
CITY_PROFILES = HERE / "city-profiles.yml"
OUT = ROOT / "build/demography/verification.json"


def main() -> None:
    source = yaml.safe_load(SOURCE.read_text())
    candidate = yaml.safe_load(CANDIDATE.read_text())
    expected = json.loads(EXPECTED.read_text())
    report = json.loads(REPORT.read_text())
    errors = []

    for key in ("version", "countries", "subject_types", "diplomacy"):
        if source.get(key) != candidate.get(key):
            errors.append(f"changed {key}")
    if set(source["states"]) != set(candidate["states"]):
        errors.append("changed state set")
    for state, old in source["states"].items():
        new = candidate["states"].get(state, {})
        old_political = {k: v for k, v in old.items() if k != "population"}
        new_political = {k: v for k, v in new.items() if k != "population"}
        if old_political != new_political:
            errors.append(f"{state}: changed political or building data")
        old_population = old.get("population", {})
        new_population = new.get("population", {})
        old_other = {tag: value for tag, value in old_population.get("by_owner", {}).items() if tag != "RUM"}
        new_other = {tag: value for tag, value in new_population.get("by_owner", {}).items() if tag != "RUM"}
        if old_other != new_other:
            errors.append(f"{state}: changed another owner's population plan")

    baseline = pdx.parse_file(BASE_POPS).get_node("POPS")
    emitted = pdx.parse_file(NEW_POPS).get_node("POPS")
    changed_states = set(expected["states"])
    for block in baseline.items:
        old_state = block.value
        new_state = emitted.get_node(block.key)
        if new_state is None:
            errors.append(f"{block.key}: emitted state missing")
            continue
        for item in old_state.items:
            if block.key.removeprefix("s:") in changed_states and item.key == "region_state:RUM":
                continue
            other = new_state.get_node(item.key)
            if other is None or pdx.dumps(item.value) != pdx.dumps(other):
                errors.append(f"{block.key}/{item.key}: unrelated POPs changed")

    freed = 0
    actual_groups: dict[str, Counter[str]] = {}
    for state, plan in expected["states"].items():
        node = emitted.get_node("s:" + state).get_node("region_state:RUM")
        actual: Counter[str] = Counter()
        for pop in node.getall("create_pop"):
            actual[f"{pop.get_str('culture')}/{pop.get_str('religion')}"] += pop.get_int("size")
            if pop.get_str("pop_type") == "slaves":
                errors.append(f"{state}: enslaved POP remains after 1811 abolition")
        if dict(actual) != plan["groups"]:
            errors.append(f"{state}: joint culture/religion counts differ")
        actual_groups[state] = actual
        if report["states"][state]["owners"]["RUM"]["population"] != plan["population"]:
            errors.append(f"{state}: report population differs")
        if report["states"][state]["owners"]["RUM"]["settings"].get("literacy") != plan["literacy"]:
            errors.append(f"{state}: literacy setting differs")
        freed += plan["legacy_former_slaves"]

    cities = yaml.safe_load(CITY_PROFILES.read_text())["cities"]
    city_by_state: dict[str, Counter[str]] = {}
    for city, profile in cities.items():
        state = profile["state"]
        if state not in actual_groups:
            errors.append(f"{city}: city lies outside this Rûm phase")
            continue
        weights = profile["weights"]
        if sum(weights.values()) != 1000:
            errors.append(f"{city}: joint weights must total 1000")
            continue
        if profile["population"] > expected["states"][state]["population"]:
            errors.append(f"{city}: city exceeds state-share population")
        row = city_by_state.setdefault(state, Counter())
        for group, weight in weights.items():
            amount, residue = divmod(profile["population"] * weight, 1000)
            if residue:
                errors.append(f"{city}: city group {group} has fractional people")
            row[group] += amount
    for state, groups in city_by_state.items():
        for group, amount in groups.items():
            if amount > actual_groups[state][group]:
                errors.append(f"{state}: cities exceed state-share {group} population")

    if report["countries"]["RUM"]["population"] != expected["target_population"]:
        errors.append("Rûm country population differs")
    literacy = sum(row["population"] * row["literacy"] for row in expected["states"].values()) / expected["target_population"]
    if not .38 <= literacy <= .44:
        errors.append("weighted literacy is outside written target")
    result = {
        "passed": not errors and report["validation"] == "passed",
        "state_shares": len(changed_states),
        "population": expected["target_population"],
        "weighted_literacy_input": literacy,
        "former_slave_culture_religion_people_preserved_without_slave_type": freed,
        "reviewed_city_hubs": len(cities),
        "city_hub_population_estimate": sum(city["population"] for city in cities.values()),
        "other_pop_blocks_unchanged": not any("unrelated POPs changed" in e for e in errors),
        "errors": errors,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (passed={result['passed']})")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
