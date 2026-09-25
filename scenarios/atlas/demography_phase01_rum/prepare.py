"""Prepare Rûm's reviewed joint population plan without changing the map."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = HERE / "plan.yml"
LEGACY = HERE / "legacy-population-snapshot.json"
WORLD = ROOT / "world/scenario.yml"
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def apportion(total: int, weights: dict[str, int]) -> dict[str, int]:
    denominator = sum(weights.values())
    if denominator <= 0 or any(value <= 0 for value in weights.values()):
        raise ValueError("every joint culture/religion weight must be positive")
    exact = {key: Fraction(total * value, denominator) for key, value in weights.items()}
    counts = {key: int(amount) for key, amount in exact.items()}
    remainder = total - sum(counts.values())
    order = sorted(weights, key=lambda key: (-(exact[key] - counts[key]), key))
    for key in order[:remainder]:
        counts[key] += 1
    return counts


def owners(spec: dict) -> set[str]:
    if "split" in spec:
        return {part["owner"] for part in spec["split"]}
    return {spec["owner"]} if "owner" in spec else set()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build/demography/rum-candidate.yml")
    args = parser.parse_args()
    output = (ROOT / args.out).resolve()
    if not output.is_relative_to(ROOT / "build"):
        raise ValueError("candidate output must stay inside this mod's build directory")

    plan = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    old = json.loads((ROOT / plan["population_source"]).read_text(encoding="utf-8"))
    legacy = json.loads(LEGACY.read_text(encoding="utf-8"))
    world = yaml.safe_load(WORLD.read_text(encoding="utf-8"))
    world["title"] = "The Golden Crescent — 1836 siyasi dünya ve Rûm toplumu"
    world["description"] = (
        "1836 alternatif siyasi dünya: ülke, sınır ve bağlılıklar. Rûm'un 25 state payında "
        "nüfus, kültür, din ve okuryazarlık senaryoya göre düzenlenmiştir; diğer bölgelerde "
        "geçici vanilla nüfus aktarımı sürer. Yalnız teknolojiyle uyumlu binalar korunur."
    )
    targets = {row["state"]: row for row in old["regions"]}
    if (plan["country"] != "RUM" or set(plan["states"]) != set(targets)
            or set(targets) != set(legacy)):
        raise ValueError("Rûm plan, target states, and frozen legacy snapshot differ")
    if sum(row["population"] for row in targets.values()) != plan["population_target"]:
        raise ValueError("Rûm state totals do not equal the country target")

    audit = {"country": "RUM", "states": {}, "target_population": plan["population_target"]}
    for state, design in plan["states"].items():
        spec = world["states"].get(state)
        if not spec or "RUM" not in owners(spec) or spec.get("pops") != "inherit":
            raise ValueError(f"{state}: active political share or inherited population missing")
        target = targets[state]
        mix = design["mix"]
        if not mix or any("/" not in key or not isinstance(weight, int) for key, weight in mix.items()):
            raise ValueError(f"{state}: invalid joint culture/religion mix")
        frozen = defaultdict(int)
        for row in legacy[state]:
            frozen[f"{row['culture']}/{row['religion']}"] += row["size"]
        large_omission = {group: size for group, size in frozen.items()
                          if group not in mix and size > sum(frozen.values()) * .05}
        if large_omission:
            raise ValueError(f"{state}: large inherited group omitted from reviewed mix: {large_omission}")
        retained = {group: size for group, size in frozen.items() if group not in mix}
        main_total = target["population"] - sum(retained.values())
        if main_total <= 0:
            raise ValueError(f"{state}: retained population exceeds target")
        counts = apportion(main_total, mix)
        counts.update(retained)
        total = sum(counts.values())
        if total != target["population"]:
            raise ValueError(f"{state}: composition total mismatch")
        # Atlas accepts ratios. Fifteen significant decimal digits preserve the
        # exact integer allocation under its largest-remainder apportionment.
        groups = list(counts)
        shares = [counts[group] / total for group in groups]
        shares[-1] = 1.0 - sum(shares[:-1])
        composition = []
        for group, share in zip(groups, shares):
            culture, religion = group.split("/", 1)
            composition.append({"culture": culture, "religion": religion, "share": share})
        population = {"total": total, "literacy": target["literacy"], "composition": composition}
        previous = spec.get("population", {}).get("by_owner", {}).get("RUM")
        if previous is not None and previous != population:
            raise ValueError(f"{state}: existing Rûm population differs; preserve manual work")
        spec.setdefault("population", {}).setdefault("by_owner", {})["RUM"] = population
        audit["states"][state] = {
            "population": total,
            "literacy": target["literacy"],
            "groups": counts,
            "legacy_groups_retained": retained,
            "legacy_former_slaves": sum(row["size"] for row in legacy[state]
                                        if row["pop_type"] == "slaves"),
            "reason": target["reason"],
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    (output.parent / "rum-plan-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {output.relative_to(ROOT)} ({len(audit['states'])} state shares, {audit['target_population']:,} people)")


if __name__ == "__main__":
    main()
