"""Audit Andalusian POPs, the additive culture, homelands, cities and unchanged borders."""

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
CANDIDATE = ROOT / "build/demography/andalus-candidate.yml"
EXPECTED = ROOT / "build/demography/andalus-plan-audit.json"
BASE_POPS = ROOT / "common/history/pops/tgc_pops.txt"
NEW_POPS = ROOT / "build/scenarios/andalus-demography-candidate/common/history/pops/tgc_pops.txt"
NEW_STATES = ROOT / "build/scenarios/andalus-demography-candidate/common/history/states/tgc_states.txt"
NEW_COUNTRIES = ROOT / "build/scenarios/andalus-demography-candidate/common/country_definitions/tgc_countries.txt"
REPORT = ROOT / "build/demography/andalus-candidate-report.json"
OUT = ROOT / "build/demography/andalus-verification.json"


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
    for key in ("version", "subject_types", "diplomacy"):
        if source.get(key) != candidate.get(key):
            errors.append(f"changed {key}")
    if set(source["countries"]) != set(candidate["countries"]):
        errors.append("changed country tag set")
    for tag, old in source["countries"].items():
        new = candidate["countries"].get(tag, {})
        if tag == "VAN":
            old = {k: v for k, v in old.items() if k != "cultures"}
            new = {k: v for k, v in new.items() if k != "cultures"}
        if old != new:
            errors.append(f"{tag}: country definition besides reviewed culture changed")
    if candidate["countries"]["VAN"]["cultures"] != expected["primary_cultures"]:
        errors.append("VAN primary cultures differ")
    if set(source["states"]) != set(candidate["states"]):
        errors.append("changed state set")
    for state, old in source["states"].items():
        new = candidate["states"].get(state, {})
        old_political = {k: v for k, v in old.items() if k not in {"population", "homelands"}}
        new_political = {k: v for k, v in new.items() if k not in {"population", "homelands"}}
        if old_political != new_political:
            errors.append(f"{state}: political or building data changed")
        if state not in expected["states"] and old.get("homelands") != new.get("homelands"):
            errors.append(f"{state}: unrelated homelands changed")
        old_other = {tag: value for tag, value in old.get("population", {}).get("by_owner", {}).items() if tag != "VAN"}
        new_other = {tag: value for tag, value in new.get("population", {}).get("by_owner", {}).items() if tag != "VAN"}
        if old_other != new_other:
            errors.append(f"{state}: another owner's population plan changed")

    baseline = pdx.parse_file(BASE_POPS).get_node("POPS")
    emitted = pdx.parse_file(NEW_POPS).get_node("POPS")
    changed_states = set(expected["states"])
    for block in baseline.items:
        new_state = emitted.get_node(block.key)
        if new_state is None:
            errors.append(f"{block.key}: emitted state missing")
            continue
        for item in block.value.items:
            if block.key.removeprefix("s:") in changed_states and item.key == "region_state:VAN":
                continue
            other = new_state.get_node(item.key)
            if other is None or pdx.dumps(item.value) != pdx.dumps(other):
                errors.append(f"{block.key}/{item.key}: unrelated POPs changed")

    emitted_states = pdx.parse_file(NEW_STATES).get_node("STATES")
    emitted_countries = pdx.parse_file(NEW_COUNTRIES)
    if "ve_andalusi" not in pdx.dumps(emitted_countries.get_node("VAN")):
        errors.append("VAN emitted primary cultures lack ve_andalusi")
    actual_joint: dict[str, Counter[str]] = {}
    old_slaves = sum(row["size"] for rows in legacy.values() for row in rows if row["pop_type"] == "slaves")
    new_slaves = 0
    for state, design in expected["states"].items():
        node = emitted.get_node("s:" + state).get_node("region_state:VAN")
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
            errors.append(f"{state}: output joint culture/religion/profession differs")
        for key, size in design["fixed_legacy_groups"].items():
            if actual[key] != size:
                errors.append(f"{state}: inherited group {key} changed")
        if report["states"][state]["owners"]["VAN"]["population"] != design["population"]:
            errors.append(f"{state}: report population differs")
        if report["states"][state]["owners"]["VAN"]["settings"].get("literacy") != design["literacy"]:
            errors.append(f"{state}: literacy input differs")
        if design["homelands"]:
            state_node = emitted_states.get_node("s:" + state)
            homelands = [str(item.value).removeprefix("cu:") for item in state_node.items if item.key == "add_homeland"]
            if set(homelands) != set(design["homelands"]):
                errors.append(f"{state}: emitted homelands differ")
        actual_joint[state] = joint
    if old_slaves != new_slaves:
        errors.append("inherited enslaved POP headcount changed")

    cities = yaml.safe_load((HERE / "city-profiles.yml").read_text())["cities"]
    city_by_state: dict[str, Counter[str]] = {}
    for city, profile in cities.items():
        state = profile["state"]
        if state not in actual_joint:
            errors.append(f"{city}: city outside VAN state shares")
            continue
        weights = profile["weights"]
        if sum(weights.values()) != 1000:
            errors.append(f"{city}: weights do not total 1000")
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
                errors.append(f"{state}: city profiles exceed state-share {group}")
        if sum(groups.values()) > expected["states"][state]["population"]:
            errors.append(f"{state}: city profiles exceed state-share total")

    if report["countries"]["VAN"]["population"] != expected["target_population"]:
        errors.append("VAN country population differs")
    literacy = sum(row["population"] * row["literacy"] for row in expected["states"].values()) / expected["target_population"]
    if not .46 <= literacy <= .54:
        errors.append("weighted literacy outside written target")
    result = {
        "passed": not errors and report["validation"] == "passed",
        "state_shares": len(changed_states), "population": expected["target_population"],
        "weighted_literacy_input": literacy, "legacy_enslaved_population": new_slaves,
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
