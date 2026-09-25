"""Check generated phase 09 POPs, protected shares and city subsets."""

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


def groups(node) -> Counter[str]:
    result = Counter()
    for pop in node.getall("create_pop"):
        key = f"{pop.get_str('culture')}/{pop.get_str('religion')}"
        if pop.get_str("pop_type"):
            key += f"/{pop.get_str('pop_type')}"
        result[key] += pop.get_int("size")
    return result


def main() -> None:
    source = yaml.safe_load((ROOT / "build/demography/indian-states-source.yml").read_text())
    candidate = yaml.safe_load((ROOT / "build/demography/indian-states-candidate.yml").read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    audit = json.loads((ROOT / "build/demography/indian-states-audit.json").read_text())
    frozen = json.loads((HERE / "source-pops.json").read_text())
    report = json.loads((ROOT / "build/scenarios/indian-states-candidate/scenario-report.json").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    errors = []
    for key in ("version", "countries", "subject_types", "diplomacy"):
        if source[key] != candidate[key]:
            errors.append(f"{key} changed")
    if set(source["states"]) != set(candidate["states"]):
        errors.append("state set changed")
    target = set(audit["shares"])
    for state, old in source["states"].items():
        new = candidate["states"][state]
        if {k: v for k, v in old.items() if k != "population"} != {k: v for k, v in new.items() if k != "population"}:
            errors.append(f"{state}: nonpopulation fields changed")
        a, b = old.get("population", {}).get("by_owner", {}), new.get("population", {}).get("by_owner", {})
        for tag in set(a) | set(b):
            if f"{state}/{tag}" not in target and a.get(tag) != b.get(tag):
                errors.append(f"{state}/{tag}: protected numeric plan changed")
        if state not in plan["states"] and old.get("population") != new.get("population"):
            errors.append(f"{state}: unrelated population changed")

    base = pdx.parse_file(ROOT / "build/demography/indian-states-source-pops.txt").get_node("POPS")
    actual = pdx.parse_file(ROOT / "build/scenarios/indian-states-candidate/common/history/pops/tgc_pops.txt").get_node("POPS")
    joint = {}
    totals = defaultdict(int)
    for old_state in base.items:
        new_state = actual.get_node(old_state.key)
        if new_state is None:
            errors.append(f"{old_state.key}: missing generated state")
            continue
        for old_owner in old_state.value.items:
            share = f"{old_state.key.removeprefix('s:')}/{old_owner.key.removeprefix('region_state:')}"
            new_owner = new_state.get_node(old_owner.key)
            if new_owner is None:
                errors.append(f"{share}: missing generated owner")
            elif share not in target and pdx.dumps(old_owner.value) != pdx.dumps(new_owner):
                errors.append(f"{share}: protected POPs changed")
    for share, design in audit["shares"].items():
        state, tag = share.split("/")
        owner = actual.get_node("s:" + state).get_node("region_state:" + tag)
        observed = groups(owner)
        expected = Counter(design["groups"])
        if observed != expected:
            errors.append(f"{share}: joint groups/professions differ: {observed - expected}, {expected - observed}")
        for key, count in design["fixed_professions"].items():
            if observed[key] != count:
                errors.append(f"{share}: preserved profession {key} differs")
        old_slaves = sum(row["size"] for row in frozen[share] if row["pop_type"] == "slaves")
        new_slaves = sum(count for key, count in observed.items() if key.endswith("/slaves"))
        if old_slaves != new_slaves:
            errors.append(f"{share}: inherited bonded population changed")
        if any(key.startswith(("british/", "scottish/", "french/")) and key.split("/")[-1] in {"bureaucrats", "officers", "aristocrats"} for key in observed):
            errors.append(f"{share}: foreign colonial official remains")
        if report["states"][state]["owners"][tag]["population"] != design["population"]:
            errors.append(f"{share}: reported population differs")
        if report["states"][state]["owners"][tag]["settings"].get("literacy") != design["literacy"]:
            errors.append(f"{share}: reported literacy input differs")
        totals[tag] += design["population"]
        joint[share] = Counter({"/".join(key.split("/")[:2]): count for key, count in observed.items() if key.count("/") == 1})
        for key, count in observed.items():
            if key.count("/") == 2:
                joint[share]["/".join(key.split("/")[:2])] += count
    for tag, design in plan["countries"].items():
        if totals[tag] != design["population"] or report["countries"][tag]["population"] != design["population"]:
            errors.append(f"{tag}: country direct-population target differs")
        rows = [(row["population"], row["literacy"]) for share, row in audit["shares"].items() if share.endswith("/" + tag)]
        literacy = sum(pop * rate for pop, rate in rows) / sum(pop for pop, _ in rows)
        if not design["literacy_range"][0] <= literacy <= design["literacy_range"][1]:
            errors.append(f"{tag}: literacy range missed")
    urban = defaultdict(Counter)
    cities = yaml.safe_load((HERE / "city-profiles.yml").read_text())["cities"]
    for name, city in cities.items():
        share = f"{city['state']}/{city['owner']}"
        if share not in target or city["hub"] not in {"city", "port", "farm", "mine", "wood"}:
            errors.append(f"{name}: invalid city share or hub")
            continue
        state_spec = index["states"][city["state"]]
        province = state_spec[city["hub"]]
        parts = candidate["states"][city["state"]].get("split") or [
            {"owner": candidate["states"][city["state"]]["owner"], "provinces": state_spec["provinces"]}]
        if not province or not any(p["owner"] == city["owner"] and province in p["provinces"] for p in parts):
            errors.append(f"{name}: named hub not in owner province")
        if sum(city["weights"].values()) != 1000:
            errors.append(f"{name}: city mix does not sum to 1000")
        for group, weight in city["weights"].items():
            amount, residue = divmod(city["population"] * weight, 1000)
            if residue:
                errors.append(f"{name}/{group}: fractional person")
            urban[share][group] += amount
    for share, city_groups in urban.items():
        for group, count in city_groups.items():
            if count > joint[share][group]:
                errors.append(f"{share}: city estimates exceed {group} POP")
        if sum(city_groups.values()) > audit["shares"][share]["population"]:
            errors.append(f"{share}: city estimates exceed POP total")
    if report["validation"] != "passed":
        errors.append("candidate report failed")
    payload = {"passed": not errors, "states": len(plan["states"]), "owner_shares": len(target),
               "countries": len(plan["countries"]), "cities": len(cities), "errors": errors}
    output = ROOT / "build/demography/indian-states-verification.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {output.relative_to(ROOT)} (passed={payload['passed']})")
    if errors:
        print("\n".join(errors[:30]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
