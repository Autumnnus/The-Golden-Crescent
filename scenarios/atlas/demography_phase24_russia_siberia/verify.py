"""Audit the Sakhalin correction, the Russia–Siberia POP plan and protected world data."""

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
sys.path.insert(0, str(HERE))
from vic3 import pdx  # noqa: E402
from political import REMOVED_COUNTRY_ENTRIES, TRANSFERS  # noqa: E402

BASE = "russia-siberia"
POLITICAL_STATES = {state for state, *_ in TRANSFERS}
MERGED = {f"{state}/{old}" for state, old, _, _ in TRANSFERS}


def grouped(node) -> Counter[str]:
    counts = Counter()
    for pop in node.getall("create_pop"):
        key = f"{pop.get_str('culture')}/{pop.get_str('religion')}"
        if pop.get_str("pop_type"):
            key += f"/{pop.get_str('pop_type')}"
        counts[key] += pop.get_int("size")
    return counts


def without(spec: dict, *keys: str) -> dict:
    return {key: value for key, value in spec.items() if key not in keys}


def main() -> None:
    build = ROOT / "build/demography"
    source = yaml.safe_load((build / f"{BASE}-source.yml").read_text())
    political = yaml.safe_load((build / f"{BASE}-political.yml").read_text())
    candidate = yaml.safe_load((build / f"{BASE}-candidate.yml").read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    frozen = json.loads((HERE / "source-pops.json").read_text())
    audit = json.loads((build / f"{BASE}-audit.json").read_text())
    prior_report = json.loads((build / f"{BASE}-source-report.json").read_text())
    out_dir = ROOT / f"build/scenarios/{BASE}-candidate"
    report = json.loads((out_dir / "scenario-report.json").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    target = set(audit["shares"])
    errors = []
    if len(target) != 56 or set(frozen) != target or set(plan["shares"]) != target:
        errors.append("share scope differs")
    for field in ("version", "subject_types", "diplomacy"):
        if not source[field] == political[field] == candidate[field]:
            errors.append(f"{field} changed")
    # Political correction: only the two planned transfers and the new/overridden countries.
    for state in set(source["states"]) | set(political["states"]):
        old, new = source["states"].get(state), political["states"].get(state)
        if state not in POLITICAL_STATES and old != new:
            errors.append(f"{state}: changed by political correction")
    for state, old_tag, new_tag, count in TRANSFERS:
        old_parts = {p["owner"]: p["provinces"] for p in source["states"][state]["split"]}
        expected = {o: list(p) for o, p in old_parts.items() if o != old_tag}
        expected[new_tag] = expected[new_tag] + old_parts[old_tag]
        if {p["owner"]: p["provinces"] for p in political["states"][state]["split"]} != expected:
            errors.append(f"{state}: split differs beyond {old_tag}->{new_tag}")
        if len(old_parts[old_tag]) != count:
            errors.append(f"{state}: transferred province count differs")
    if set(political["countries"]) != set(source["countries"]) - set(REMOVED_COUNTRY_ENTRIES):
        errors.append("political country set differs")
    for tag, spec in political["countries"].items():
        if spec != source["countries"][tag]:
            errors.append(f"{tag}: political country definition differs")
    # Demography candidate countries: planned cultures and slavery laws only.
    expected_countries = json.loads(json.dumps(political["countries"]))
    for tag, change in plan["country_culture_overrides"].items():
        expected_countries.setdefault(tag, {})["cultures"] = change["to"]
    for tag, change in plan["country_religion_overrides"].items():
        expected_countries.setdefault(tag, {})["religion"] = change["to"]
    for tag, laws in plan["country_laws"].items():
        expected_countries[tag]["laws"] = {"values": laws}
    if candidate["countries"] != expected_countries:
        errors.append("country definitions differ beyond planned culture/law overrides")
    # States: borders/buildings as in the political source; population and homelands planned.
    for state, old in political["states"].items():
        new = candidate["states"][state]
        planned_state = any(key.startswith(state + "/") for key in target)
        if without(old, "population", "homelands") != without(new, "population", "homelands"):
            errors.append(f"{state}: border/building fields changed")
        if planned_state and state not in audit["homelands_skipped"]:
            if "homelands" in old or new.get("homelands") != audit["homelands"][state]["planned"]:
                errors.append(f"{state}: homeland plan differs")
        elif old.get("homelands") != new.get("homelands") or (
                not planned_state and old.get("population") != new.get("population")):
            errors.append(f"{state}: unrelated population/homelands changed")
        old_by = old.get("population", {}).get("by_owner", {})
        new_by = new.get("population", {}).get("by_owner", {})
        for tag in set(old_by) | set(new_by):
            if f"{state}/{tag}" not in target and old_by.get(tag) != new_by.get(tag):
                errors.append(f"{state}/{tag}: protected numeric plan changed")
    # Generated POPs: every non-target share identical to the pre-phase active build.
    base = pdx.parse_file(build / f"{BASE}-source-pops.txt").get_node("POPS")
    actual = pdx.parse_file(out_dir / "common/history/pops/tgc_pops.txt").get_node("POPS")
    seen = set()
    for state_block in base.items:
        for owner_block in state_block.value.items:
            share = f"{state_block.key.removeprefix('s:')}/{owner_block.key.removeprefix('region_state:')}"
            if share in MERGED:
                continue
            state, tag = share.split("/")
            seen.add(share)
            other = actual.get_node("s:" + state)
            other = other.get_node("region_state:" + tag) if other is not None else None
            if other is None:
                errors.append(f"{share}: generated owner missing")
            elif share not in target and pdx.dumps(owner_block.value) != pdx.dumps(other):
                errors.append(f"{share}: protected POPs changed")
    for state_block in actual.items:
        for owner_block in state_block.value.items:
            share = f"{state_block.key.removeprefix('s:')}/{owner_block.key.removeprefix('region_state:')}"
            if share not in seen:
                errors.append(f"{share}: unexpected generated POP owner")
    joint = {}
    slave_tags = set()
    for share, designed in audit["shares"].items():
        state, tag = share.split("/")
        counts = grouped(actual.get_node("s:" + state).get_node("region_state:" + tag))
        expected = Counter(designed["groups"])
        if counts != expected:
            errors.append(f"{share}: joint groups/professions differ: {counts - expected}, {expected - counts}")
        for group, count in designed["fixed_professions"].items():
            if counts[group] != count:
                errors.append(f"{share}: protected profession {group} changed")
        released = sum(row["size"] for row in frozen[share] if row["pop_type"] == "slaves")
        if share in plan["release_slaves"]:
            if designed["released_slaves"] != released or any(g.endswith("/slaves") for g in counts):
                errors.append(f"{share}: slave release differs")
        elif designed["released_slaves"]:
            errors.append(f"{share}: unplanned slave release")
        if any(group.endswith("/slaves") for group in counts):
            slave_tags.add(tag)
        owner = report["states"][state]["owners"][tag]
        if owner["population"] != designed["population"]:
            errors.append(f"{share}: report population differs")
        if owner["settings"].get("literacy") != designed["literacy"]:
            errors.append(f"{share}: report literacy input differs")
        joint[share] = Counter()
        for group, count in counts.items():
            joint[share]["/".join(group.split("/")[:2])] += count
    if slave_tags:
        errors.append(f"unexpected slave POP holders: {sorted(slave_tags)}")
    for tag in slave_tags:
        if not any("slavery" in law or "slave" in law for law in report["countries"][tag]["laws"]):
            errors.append(f"{tag}: preserved slave POPs without a reported slavery law")
    # Country totals and protected countries.
    observed_partial = set()
    for tag, row in audit["countries"].items():
        outside = prior_report["countries"].get(tag, {}).get("population", row["prior_population"]) - \
            row["prior_population"]
        if outside:
            observed_partial.add(tag)
        if report["countries"][tag]["population"] != outside + row["population"]:
            errors.append(f"{tag}: direct population target differs")
        policy = plan["countries"][tag]["literacy_range"]
        if not policy[0] - 1e-9 <= row["weighted_literacy"] <= policy[1] + 1e-9:
            errors.append(f"{tag}: literacy target range differs")
    if observed_partial != set(plan["partial_countries"]):
        errors.append(f"partial-country list differs: {sorted(observed_partial)}")
    transferred_old = {old for _, old, _, _ in TRANSFERS}
    for tag, country in prior_report["countries"].items():
        if tag in plan["countries"] or tag in transferred_old:
            continue
        if report["countries"][tag]["population"] != country["population"]:
            errors.append(f"{tag}: non-target population changed")
    if "ALK" in report["countries"]:
        errors.append("ALK still owns land")
    # Generated homelands follow the plan.
    states_file = pdx.parse_file(out_dir / "common/history/states/tgc_states.txt").get_node("STATES")
    for state, row in audit["homelands"].items():
        node = states_file.get_node("s:" + state)
        generated = [value.removeprefix("cu:") for value in node.getall("add_homeland")]
        if sorted(generated) != sorted(row["planned"]):
            errors.append(f"{state}: generated homelands differ: {generated}")
    # City profiles.
    city_joint = defaultdict(Counter)
    cities = yaml.safe_load((HERE / "city-profiles.yml").read_text())["cities"]
    mod_settings = json.loads((ROOT / ".vic3-tools.json").read_text())
    game_dir = Path(os.environ.get("VIC3_GAME_DIR") or mod_settings.get("game_dir") or
                    Path.home() / "Library/Application Support/Steam/steamapps/common/Victoria 3/game")
    hub_names = (game_dir / "localization/turkish/hub_names_l_turkish.yml").read_text()
    for name, city in cities.items():
        share = f"{city['state']}/{city['owner']}"
        if share not in target or city["hub"] not in {"city", "port", "farm", "mine", "wood"}:
            errors.append(f"{name}: city outside planned share/hub")
            continue
        province = index["states"][city["state"]][city["hub"]]
        parts = candidate["states"][city["state"]]["split"]
        if not province or not any(part["owner"] == city["owner"] and province in part["provinces"] for part in parts):
            errors.append(f"{name}: hub province has a different owner")
        if f'HUB_NAME_{city["state"]}_{city["hub"]}: "{name}"' not in hub_names:
            errors.append(f"{name}: not the installed Turkish hub name")
        if sum(city["weights"].values()) != 1000:
            errors.append(f"{name}: city weights do not total 1000")
        for group, weight in city["weights"].items():
            people, remainder = divmod(city["population"] * weight, 1000)
            if remainder:
                errors.append(f"{name}/{group}: fractional person")
            city_joint[share][group] += people
    for share, counts in city_joint.items():
        if sum(counts.values()) > audit["shares"][share]["population"]:
            errors.append(f"{share}: city subtotal exceeds state population")
        for group, amount in counts.items():
            if amount > joint[share][group]:
                errors.append(f"{share}: city subtotal exceeds {group} POP")
    if report["validation"] != "passed" or report["diplomacy"] != prior_report["diplomacy"]:
        errors.append("report validation or diplomacy differs")
    world_population = sum(row["population"] for row in report["states"].values())
    prior_world = sum(row["population"] for row in prior_report["states"].values())
    delta = sum(row["population"] - row["prior_population"] for row in audit["shares"].values())
    # Merged old-owner shares disappear before the frozen POP snapshot; count them as prior people.
    delta -= sum(prior_report["states"][state]["owners"][old]["population"] for state, old, _, _ in TRANSFERS)
    if world_population != prior_world + delta:
        errors.append("world population differs from planned delta")
    result = {"passed": not errors, "countries": len(plan["countries"]), "shares": len(target),
              "cities": len(cities), "world_population": world_population,
              "prior_world_population": prior_world, "errors": errors}
    out = build / f"{BASE}-verification.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)} (passed={result['passed']})")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
