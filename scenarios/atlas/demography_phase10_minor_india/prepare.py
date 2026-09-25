"""Prepare 37 independent minor Indian countries from frozen source POPs."""

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
    if total <= 0 or denominator <= 0 or any(weight <= 0 for weight in weights.values()):
        raise ValueError("population weights must be positive")
    exact = {key: Fraction(total * weight, denominator) for key, weight in weights.items()}
    counts = {key: int(amount) for key, amount in exact.items()}
    for key in sorted(weights, key=lambda item: (-(exact[item] - counts[item]), item))[:total - sum(counts.values())]:
        counts[key] += 1
    return counts


def owners(spec: dict) -> set[str]:
    return {part["owner"] for part in spec["split"]} if "split" in spec else {spec["owner"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build/demography/minor-india-candidate.yml")
    args = parser.parse_args()
    output = (ROOT / args.out).resolve()
    if not output.is_relative_to(ROOT / "build"):
        raise ValueError("candidate output must stay in this mod's build directory")
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    frozen = json.loads((HERE / "source-pops.json").read_text())
    world = yaml.safe_load((ROOT / "world/scenario.yml").read_text())
    tags = set(plan["countries"])
    if len(tags) != 37 or tags & (set(plan["protected_countries"]) | set(plan["deferred_border_countries"])):
        raise ValueError("plan country scope differs")
    by_country = defaultdict(dict)
    for key, rows in frozen.items():
        state, tag = key.split("/")
        if tag not in tags or state not in world["states"]:
            raise ValueError(f"{key}: frozen share outside plan")
        spec = world["states"][state]
        if tag not in owners(spec) or spec.get("pops") != "inherit":
            raise ValueError(f"{key}: political owner or POP inheritance changed")
        by_country[tag][key] = sum(row["size"] for row in rows)
    if set(by_country) != tags:
        raise ValueError("country without source shares")
    overrides = plan.get("joint_mix_overrides", {})
    if not set(overrides) <= set(frozen):
        raise ValueError("mix override outside frozen shares")
    audit = {"shares": {}, "countries": plan["countries"], "policy": plan["policy"]}
    for tag, design in plan["countries"].items():
        totals = apportion(design["population"], by_country[tag])
        for key, target in totals.items():
            state, _ = key.split("/")
            spec = world["states"][state]
            if tag in spec.get("population", {}).get("by_owner", {}):
                raise ValueError(f"{key}: refusing to replace previous numeric plan")
            fixed, free = Counter(), Counter()
            for row in frozen[key]:
                group = f"{row['culture']}/{row['religion']}"
                if row["pop_type"]:
                    fixed[f"{group}/{row['pop_type']}"] += row["size"]
                else:
                    free[group] += row["size"]
            if key in overrides:
                mix = overrides[key]
                if set(mix) != set(free):
                    raise ValueError(f"{key}: override must name every inherited free group")
                free = Counter(mix)
            if target <= sum(fixed.values()):
                raise ValueError(f"{key}: preserved professions exceed target")
            groups = apportion(target - sum(fixed.values()), dict(free))
            groups.update(fixed)
            if sum(groups.values()) != target:
                raise AssertionError(f"{key}: population sum differs")
            shares = [count / target for count in groups.values()]
            shares[-1] = 1.0 - sum(shares[:-1])
            composition = []
            for (group, count), share in zip(groups.items(), shares):
                if count == 0:
                    continue
                parts = group.split("/")
                row = {"culture": parts[0], "religion": parts[1], "share": share}
                if len(parts) == 3:
                    row["pop_type"] = parts[2]
                composition.append(row)
            spec.setdefault("population", {}).setdefault("by_owner", {})[tag] = {
                "total": target, "literacy": design["literacy"], "composition": composition}
            audit["shares"][key] = {"prior_population": by_country[tag][key], "population": target,
                                    "literacy": design["literacy"], "groups": dict(groups),
                                    "fixed_professions": dict(fixed), "mix_override": key in overrides}
    world["title"] = "The Golden Crescent — 1836 siyasi dünya ve küçük Hint devletleri"
    world["description"] = (
        "1836 alternatif siyasi dünya ve önceki demografi fazları korunur. "
        "Otuz yedi küçük Hint devletinin kırk state payı için nüfus, ortak "
        "kültür-din ve okuryazarlık girdileri düzenlendi."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    (output.parent / "minor-india-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {output.relative_to(ROOT)} ({len(audit['shares'])} shares, {len(tags)} countries)")


if __name__ == "__main__":
    main()
