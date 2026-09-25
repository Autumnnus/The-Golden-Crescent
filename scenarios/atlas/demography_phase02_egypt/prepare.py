"""Prepare Mısır's state-share demographic plan; never edit generated game history."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORLD = ROOT / "world/scenario.yml"
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def apportion(total: int, weights: dict[str, int]) -> dict[str, int]:
    if not weights or any(not isinstance(w, int) or w <= 0 for w in weights.values()):
        raise ValueError("all joint weights must be positive integers")
    denominator = sum(weights.values())
    exact = {key: Fraction(total * weight, denominator) for key, weight in weights.items()}
    counts = {key: int(amount) for key, amount in exact.items()}
    remainder = total - sum(counts.values())
    for key in sorted(weights, key=lambda k: (-(exact[k] - counts[k]), k))[:remainder]:
        counts[key] += 1
    return counts


def owners(spec: dict) -> set[str]:
    if "split" in spec:
        return {part["owner"] for part in spec["split"]}
    return {spec["owner"]} if "owner" in spec else set()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build/demography/egypt-candidate.yml")
    args = parser.parse_args()
    output = (ROOT / args.out).resolve()
    if not output.is_relative_to(ROOT / "build"):
        raise ValueError("candidate output must stay in this mod's build directory")

    plan = yaml.safe_load((HERE / "plan.yml").read_text(encoding="utf-8"))
    legacy = json.loads((HERE / "legacy-population-snapshot.json").read_text(encoding="utf-8"))
    world = yaml.safe_load(WORLD.read_text(encoding="utf-8"))
    if plan["country"] != "EGY" or set(plan["states"]) != set(legacy):
        raise ValueError("Egypt plan and frozen legacy state shares differ")
    if sum(row["population"] for row in plan["states"].values()) != plan["population_target"]:
        raise ValueError("Egypt state shares do not add to country target")

    world["title"] = "The Golden Crescent — 1836 siyasi dünya, Rûm ve Mısır toplumu"
    world["description"] = (
        "1836 alternatif siyasi dünya: ülke, sınır ve bağlılıklar. Rûm ve Mısır'ın "
        "doğrudan state paylarında nüfus, kültür, din ve okuryazarlık düzenlendi; "
        "diğer bölgelerde geçici vanilla nüfus aktarımı sürer. Mısır'daki mevcut "
        "köle ve meslekli POP türleri kanun aşamasına dek korunur."
    )
    audit = {"country": "EGY", "states": {}, "target_population": plan["population_target"]}
    for state, design in plan["states"].items():
        spec = world["states"].get(state)
        if not spec or owners(spec) != {"EGY"} or spec.get("pops") != "inherit":
            raise ValueError(f"{state}: unexpected political share or population inheritance")
        mix = design["mix"]
        if any(group.count("/") != 1 for group in mix):
            raise ValueError(f"{state}: expected culture/religion joint mix")
        frozen_free = defaultdict(int)
        retained = defaultdict(int)
        for row in legacy[state]:
            group = f"{row['culture']}/{row['religion']}"
            if row["pop_type"]:
                retained[f"{group}/{row['pop_type']}"] += row["size"]
            else:
                frozen_free[group] += row["size"]
        large_omission = {group: size for group, size in frozen_free.items()
                          if group not in mix and size > sum(frozen_free.values()) * .05}
        if large_omission:
            raise ValueError(f"{state}: significant inherited group omitted: {large_omission}")
        retained.update({group: size for group, size in frozen_free.items() if group not in mix})
        total = design["population"]
        main_total = total - sum(retained.values())
        if main_total <= 0:
            raise ValueError(f"{state}: fixed legacy POPs exceed target")
        counts = apportion(main_total, mix)
        counts.update(retained)
        if sum(counts.values()) != total:
            raise ValueError(f"{state}: composition does not add to state target")
        groups = list(counts)
        shares = [counts[group] / total for group in groups]
        shares[-1] = 1.0 - sum(shares[:-1])
        composition = []
        for group, share in zip(groups, shares):
            parts = group.split("/")
            row = {"culture": parts[0], "religion": parts[1], "share": share}
            if len(parts) == 3:
                row["pop_type"] = parts[2]
            composition.append(row)
        population = {"total": total, "literacy": design["literacy"], "composition": composition}
        previous = spec.get("population", {}).get("by_owner", {}).get("EGY")
        if previous is not None and previous != population:
            raise ValueError(f"{state}: existing Egypt population differs; preserve manual work")
        spec.setdefault("population", {}).setdefault("by_owner", {})["EGY"] = population
        audit["states"][state] = {
            "population": total, "literacy": design["literacy"], "groups": counts,
            "fixed_legacy_groups": dict(retained), "reason": design["reason"],
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    (output.parent / "egypt-plan-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {output.relative_to(ROOT)} ({len(audit['states'])} state shares, {audit['target_population']:,} people)")


if __name__ == "__main__":
    main()
