"""Audit Nile-Horn-East Africa POPs and protected world data."""

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
    base_name = "nile-horn-east-africa"
    source = yaml.safe_load((ROOT / f"build/demography/{base_name}-source.yml").read_text())
    candidate = yaml.safe_load((ROOT / f"build/demography/{base_name}-candidate.yml").read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    frozen = json.loads((HERE / "source-pops.json").read_text())
    audit = json.loads((ROOT / f"build/demography/{base_name}-audit.json").read_text())
    prior_report = json.loads((ROOT / f"build/demography/{base_name}-source-report.json").read_text())
    report = json.loads((ROOT / f"build/scenarios/{base_name}-candidate/scenario-report.json").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    target = set(audit["shares"])
    errors = []
    if len(target) != 57 or set(frozen) != target:
        errors.append("share scope differs")
    for field in ("version", "subject_types", "diplomacy"):
        if source[field] != candidate[field]:
            errors.append(f"{field} changed")
    if set(candidate["countries"]) != set(source["countries"]) | set(plan["country_culture_overrides"]):
        errors.append("country tag set changed")
    for tag, old in source["countries"].items():
        expected = dict(old)
        change = plan["country_religion_overrides"].get(tag)
        if change:
            if old["religion"] != change["from"]:
                errors.append(f"{tag}: source official religion differs")
            expected["religion"] = change["to"]
        laws = plan["country_law_additions"].get(tag)
        if laws:
            if "laws" in old:
                errors.append(f"{tag}: source laws differ")
            expected["laws"] = {"values": laws}
        if candidate["countries"][tag] != expected:
            errors.append(f"{tag}: country definition changed beyond planned fields")
    for tag, change in plan["country_culture_overrides"].items():
        if tag in source["countries"] or candidate["countries"].get(tag) != {"cultures": change["to"]}:
            errors.append(f"{tag}: country culture override differs")
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
                errors.append(f"{state}/{tag}: protected numeric plan changed")
        if not any(key.startswith(state + "/") for key in target) and old.get("population") != new.get("population"):
            errors.append(f"{state}: unrelated population changed")
    base = pdx.parse_file(ROOT / f"build/demography/{base_name}-source-pops.txt").get_node("POPS")
    actual = pdx.parse_file(ROOT / f"build/scenarios/{base_name}-candidate/common/history/pops/tgc_pops.txt").get_node("POPS")
    for state_block in base.items:
        other_state = actual.get_node(state_block.key)
        if other_state is None:
            errors.append(f"{state_block.key}: generated POP state missing")
            continue
        for owner_block in state_block.value.items:
            share = f"{state_block.key.removeprefix('s:')}/{owner_block.key.removeprefix('region_state:')}"
            other = other_state.get_node(owner_block.key)
            if other is None:
                errors.append(f"{share}: generated owner missing")
            elif share not in target and pdx.dumps(owner_block.value) != pdx.dumps(other):
                errors.append(f"{share}: protected POPs changed")
    joint = {}
    totals = defaultdict(int)
    for share, designed in audit["shares"].items():
        state, tag = share.split("/")
        counts = grouped(actual.get_node("s:" + state).get_node("region_state:" + tag))
        expected = Counter(designed["groups"])
        if counts != expected:
            errors.append(f"{share}: joint groups/professions differ: {counts - expected}, {expected - counts}")
        original_fixed = Counter()
        for row in frozen[share]:
            if row["pop_type"]:
                original_fixed[f"{row['culture']}/{row['religion']}/{row['pop_type']}"] += row["size"]
        if original_fixed != Counter(designed["source_fixed_professions"]):
            errors.append(f"{share}: frozen fixed professions differ")
        expected_fixed = Counter()
        for group, amount in original_fixed.items():
            expected_fixed[plan["fixed_group_relabels"].get(share, {}).get(group, group)] += amount
        if expected_fixed != Counter(designed["fixed_professions"]):
            errors.append(f"{share}: fixed profession relabel differs")
        for group, count in designed["fixed_professions"].items():
            if counts[group] != count:
                errors.append(f"{share}: protected profession {group} changed")
        if report["states"][state]["owners"][tag]["population"] != designed["population"]:
            errors.append(f"{share}: report population differs")
        if report["states"][state]["owners"][tag]["settings"].get("literacy") != designed["literacy"]:
            errors.append(f"{share}: report literacy input differs")
        joint[share] = Counter()
        for group, count in counts.items():
            joint[share]["/".join(group.split("/")[:2])] += count
        totals[tag] += designed["population"]
    observed_partial = set()
    for tag, policy in plan["countries"].items():
        prior_target = sum(row["prior_population"] for share, row in audit["shares"].items()
                           if share.endswith("/" + tag))
        outside = prior_report["countries"][tag]["population"] - prior_target
        if outside:
            observed_partial.add(tag)
        if totals[tag] != policy["population"] or report["countries"][tag]["population"] != outside + policy["population"]:
            errors.append(f"{tag}: direct population target differs")
        if not policy["literacy_range"][0] <= audit["countries"][tag]["weighted_literacy"] <= policy["literacy_range"][1]:
            errors.append(f"{tag}: literacy target range differs")
        has_preserved_slaves = any(
            group.endswith("/slaves") and count > 0
            for share, row in audit["shares"].items() if share.endswith("/" + tag)
            for group, count in row["fixed_professions"].items()
        )
        if has_preserved_slaves and not any("slavery" in law or "slave" in law for law in report["countries"][tag]["laws"]):
            errors.append(f"{tag}: preserved slave POPs without a reported slavery law")
        for law in plan["country_law_additions"].get(tag, []):
            if law in prior_report["countries"][tag]["laws"] or law not in report["countries"][tag]["laws"]:
                errors.append(f"{tag}: planned law addition differs")
    if observed_partial != set(plan["partial_countries"]):
        errors.append("partial-country list differs")
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
        state_spec = candidate["states"][city["state"]]
        parts = state_spec.get("split") or [{"owner": state_spec["owner"], "provinces": index["states"][city["state"]]["provinces"]}]
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
    for tag, country in prior_report["countries"].items():
        if tag not in plan["countries"] and report["countries"][tag]["population"] != country["population"]:
            errors.append(f"{tag}: non-target population changed")
    if report["validation"] != "passed" or report["diplomacy"] != prior_report["diplomacy"]:
        errors.append("report validation or diplomacy differs")
    result = {"passed": not errors, "countries": len(plan["countries"]), "shares": len(target),
              "cities": len(cities), "world_population": sum(row["population"] for row in report["states"].values()),
              "errors": errors}
    out = ROOT / f"build/demography/{base_name}-verification.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)} (passed={result['passed']})")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
