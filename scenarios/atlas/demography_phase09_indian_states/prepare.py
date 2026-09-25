"""Prepare phase 09 demographic candidate from frozen Indian POP shares."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def apportion(total: int, weights: dict[str, int]) -> dict[str, int]:
    denominator = sum(weights.values())
    if total <= 0 or denominator <= 0:
        raise ValueError("empty population apportionment")
    exact = {key: Fraction(total * weight, denominator) for key, weight in weights.items()}
    counts = {key: int(value) for key, value in exact.items()}
    for key in sorted(weights, key=lambda item: (-(exact[item] - counts[item]), item))[:total - sum(counts.values())]:
        counts[key] += 1
    return counts


def owner_tags(spec: dict) -> set[str]:
    return {part["owner"] for part in spec["split"]} if "split" in spec else {spec["owner"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build/demography/indian-states-candidate.yml")
    args = parser.parse_args()
    output = (ROOT / args.out).resolve()
    if not output.is_relative_to(ROOT / "build"):
        raise ValueError("candidate output must stay in this mod's build directory")
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    frozen = json.loads((HERE / "source-pops.json").read_text())
    world = yaml.safe_load((ROOT / "world/scenario.yml").read_text())
    expected = {f"{state}/{tag}" for state, owners in plan["states"].items() for tag in owners}
    if set(frozen) != expected or set(plan["countries"]) != {tag for owners in plan["states"].values() for tag in owners}:
        raise ValueError("plan countries or frozen shares differ")
    if not set(plan.get("localize_professions", {})) <= expected or not set(plan.get("reclassify_communities", {})) <= expected:
        raise ValueError("transformation refers to an unplanned share")
    audit = {"shares": {}, "countries": plan["countries"], "policy": plan["policy"]}
    totals = defaultdict(int)
    used_profession_rules, used_community_rules = set(), set()
    for state, owners in plan["states"].items():
        spec = world["states"][state]
        if not set(owners) <= owner_tags(spec) or spec.get("pops") != "inherit":
            raise ValueError(f"{state}: owner or POP policy changed")
        for tag, design in owners.items():
            key = f"{state}/{tag}"
            fixed, free = Counter(), Counter()
            for row in frozen[key]:
                group = f"{row['culture']}/{row['religion']}"
                if row["pop_type"]:
                    group += f"/{row['pop_type']}"
                    replacement = plan.get("localize_professions", {}).get(key, {}).get(group)
                    if replacement:
                        used_profession_rules.add((key, group))
                        group = replacement
                    fixed[group] += row["size"]
                else:
                    replacement = plan.get("reclassify_communities", {}).get(key, {}).get(group)
                    if replacement:
                        used_community_rules.add((key, group))
                        group = replacement
                    free[group] += row["size"]
            target = design["population"]
            if target <= sum(fixed.values()):
                raise ValueError(f"{key}: fixed professions exceed target")
            groups = apportion(target - sum(fixed.values()), dict(free))
            groups.update(fixed)
            assert sum(groups.values()) == target
            composition = []
            shares = [count / target for count in groups.values()]
            shares[-1] = 1.0 - sum(shares[:-1])
            for (group, count), share in zip(groups.items(), shares):
                parts = group.split("/")
                if count == 0:
                    continue
                row = {"culture": parts[0], "religion": parts[1], "share": share}
                if len(parts) == 3:
                    row["pop_type"] = parts[2]
                composition.append(row)
            population = {"total": target, "literacy": design["literacy"], "composition": composition}
            if tag in spec.get("population", {}).get("by_owner", {}):
                raise ValueError(f"{key}: existing numeric plan must not be overwritten")
            spec.setdefault("population", {}).setdefault("by_owner", {})[tag] = population
            totals[tag] += target
            audit["shares"][key] = {"population": target, "literacy": design["literacy"],
                                    "groups": dict(groups), "fixed_professions": dict(fixed)}
    expected_profession_rules = {(key, old) for key, rules in plan.get("localize_professions", {}).items() for old in rules}
    expected_community_rules = {(key, old) for key, rules in plan.get("reclassify_communities", {}).items() for old in rules}
    if used_profession_rules != expected_profession_rules or used_community_rules != expected_community_rules:
        raise ValueError("a localization/reclassification source group was absent")
    for tag, policy in plan["countries"].items():
        if totals[tag] != policy["population"]:
            raise ValueError(f"{tag}: sum {totals[tag]} != {policy['population']}")
    world["title"] = "The Golden Crescent — 1836 siyasi dünya ve Hint devletleri demografisi"
    world["description"] = (
        "1836 alternatif siyasi dünya ve önceki demografi fazları korunur. "
        "Hint alt kıtasındaki 15 ek devletin nüfus, ortak kültür-din ve okuryazarlık "
        "girdileri; yerli devletlerin idari meslekleri düzenlendi."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    (output.parent / "indian-states-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {output.relative_to(ROOT)} ({len(audit['shares'])} owner shares, {len(totals)} countries)")


if __name__ == "__main__":
    main()
