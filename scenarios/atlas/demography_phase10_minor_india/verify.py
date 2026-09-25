"""Audit the minor-India candidate and protect all other country POPs."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLKIT = Path(os.environ.get("VIC3_TOOLS_HOME") or json.loads(
    (ROOT / ".vic3-tools.local.json").read_text())["toolkit"])
if sys.version_info < (3, 10):
    runtime = TOOLKIT / ".venv/bin/python"
    os.execv(str(runtime), [str(runtime), __file__, *sys.argv[1:]])
sys.path.insert(0, str(TOOLKIT / "src"))
from vic3 import pdx  # noqa: E402


def grouped(node) -> Counter[str]:
    counts = Counter()
    for pop in node.getall("create_pop"):
        key = f"{pop.get_str('culture')}/{pop.get_str('religion')}"
        if pop.get_str("pop_type"):
            key += f"/{pop.get_str('pop_type')}"
        counts[key] += pop.get_int("size")
    return counts


def main() -> None:
    source = yaml.safe_load((ROOT / "build/demography/minor-india-source.yml").read_text())
    candidate = yaml.safe_load((ROOT / "build/demography/minor-india-candidate.yml").read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    frozen = json.loads((HERE / "source-pops.json").read_text())
    audit = json.loads((ROOT / "build/demography/minor-india-audit.json").read_text())
    prior_report = json.loads((ROOT / "build/demography/minor-india-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/minor-india-candidate/scenario-report.json").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    errors = []
    target = set(audit["shares"])
    if len(target) != 40 or len(plan["countries"]) != 37:
        errors.append("planned scope count differs")
    for field in ("version", "countries", "subject_types", "diplomacy"):
        if source[field] != candidate[field]:
            errors.append(f"{field} changed")
    if set(source["states"]) != set(candidate["states"]):
        errors.append("state set changed")
    for state, old in source["states"].items():
        new = candidate["states"][state]
        if {k: v for k, v in old.items() if k != "population"} != {k: v for k, v in new.items() if k != "population"}:
            errors.append(f"{state}: border/building fields changed")
        old_by = old.get("population", {}).get("by_owner", {})
        new_by = new.get("population", {}).get("by_owner", {})
        for tag in set(old_by) | set(new_by):
            if f"{state}/{tag}" not in target and old_by.get(tag) != new_by.get(tag):
                errors.append(f"{state}/{tag}: unrelated numeric plan changed")
        if not any(key.startswith(state + "/") for key in target) and old.get("population") != new.get("population"):
            errors.append(f"{state}: unrelated population changed")
    # Every remaining owner in the geographic 10_india group is either
    # explicitly targeted, already profiled, or deferred with Burma/islands.
    for state, details in index["states"].items():
        if details["region"] != "10_india" or state not in candidate["states"]:
            continue
        spec = candidate["states"][state]
        owners = {part["owner"] for part in spec["split"]} if "split" in spec else {spec["owner"]}
        for tag in owners:
            if tag not in set(plan["countries"]) | set(plan["protected_countries"]) | set(plan["deferred_border_countries"]):
                errors.append(f"{state}/{tag}: unclassified Indian owner")
    base = pdx.parse_file(ROOT / "build/demography/minor-india-source-pops.txt").get_node("POPS")
    actual = pdx.parse_file(ROOT / "build/scenarios/minor-india-candidate/common/history/pops/tgc_pops.txt").get_node("POPS")
    for state_block in base.items:
        new_state = actual.get_node(state_block.key)
        if new_state is None:
            errors.append(f"{state_block.key}: generated POP state missing")
            continue
        for owner_block in state_block.value.items:
            share = f"{state_block.key.removeprefix('s:')}/{owner_block.key.removeprefix('region_state:')}"
            other = new_state.get_node(owner_block.key)
            if other is None:
                errors.append(f"{share}: generated owner missing")
            elif share not in target and pdx.dumps(owner_block.value) != pdx.dumps(other):
                errors.append(f"{share}: unrelated POPs changed")
    joint = {}
    sums = defaultdict(int)
    for share, designed in audit["shares"].items():
        state, tag = share.split("/")
        owner = actual.get_node("s:" + state).get_node("region_state:" + tag)
        counts = grouped(owner)
        expected = Counter(designed["groups"])
        if counts != expected:
            errors.append(f"{share}: joint groups/professions differ: {counts - expected}, {expected - counts}")
        previous_slaves = sum(row["size"] for row in frozen[share] if row["pop_type"] == "slaves")
        current_slaves = sum(count for group, count in counts.items() if group.endswith("/slaves"))
        if current_slaves != previous_slaves:
            errors.append(f"{share}: inherited bonded POP count changed")
        for group, count in designed["fixed_professions"].items():
            if counts[group] != count:
                errors.append(f"{share}: fixed profession {group} changed")
        if report["states"][state]["owners"][tag]["population"] != designed["population"]:
            errors.append(f"{share}: reported population differs")
        if report["states"][state]["owners"][tag]["settings"].get("literacy") != designed["literacy"]:
            errors.append(f"{share}: reported literacy input differs")
        joint[share] = Counter()
        for group, count in counts.items():
            joint[share]["/".join(group.split("/")[:2])] += count
        sums[tag] += designed["population"]
    for tag, design in plan["countries"].items():
        if sums[tag] != design["population"] or report["countries"][tag]["population"] != design["population"]:
            errors.append(f"{tag}: country total differs")
    for tag in set(plan["protected_countries"]) | set(plan["deferred_border_countries"]):
        if prior_report["countries"][tag]["population"] != report["countries"][tag]["population"]:
            errors.append(f"{tag}: protected/deferred population changed")
    cities = yaml.safe_load((HERE / "city-profiles.yml").read_text())["cities"]
    city_joint = defaultdict(Counter)
    for name, city in cities.items():
        share = f"{city['state']}/{city['owner']}"
        if share not in target or city["hub"] not in {"city", "port", "farm", "mine", "wood"}:
            errors.append(f"{name}: city outside planned share or hub")
            continue
        province = index["states"][city["state"]][city["hub"]]
        state_spec = candidate["states"][city["state"]]
        parts = state_spec.get("split") or [{"owner": state_spec["owner"], "provinces": index["states"][city["state"]]["provinces"]}]
        if not province or not any(part["owner"] == city["owner"] and province in part["provinces"] for part in parts):
            errors.append(f"{name}: hub province owned by a different country")
        if sum(city["weights"].values()) != 1000:
            errors.append(f"{name}: city weights do not total 1000")
        for group, weight in city["weights"].items():
            persons, remainder = divmod(city["population"] * weight, 1000)
            if remainder:
                errors.append(f"{name}/{group}: fractional city person")
            city_joint[share][group] += persons
    for share, counts in city_joint.items():
        if sum(counts.values()) > audit["shares"][share]["population"]:
            errors.append(f"{share}: city exceeds owner population")
        for group, amount in counts.items():
            if amount > joint[share][group]:
                errors.append(f"{share}: city exceeds {group} POP")
    if report["validation"] != "passed" or report["diplomacy"] != prior_report["diplomacy"]:
        errors.append("report validation or diplomacy changed")
    result = {"passed": not errors, "countries": len(plan["countries"]), "shares": len(target),
              "cities": len(cities), "world_population": sum(row["population"] for row in report["states"].values()),
              "errors": errors}
    out = ROOT / "build/demography/minor-india-verification.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)} (passed={result['passed']})")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
