"""Prepare joint population and literacy plans for six Indian country tags."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def apportion(total: int, weights: dict[str, int]) -> dict[str, int]:
    if not weights or any(not isinstance(weight, int) or weight <= 0 for weight in weights.values()):
        raise ValueError("joint culture/religion weights must be positive integers")
    exact = {key: Fraction(total * weight, sum(weights.values())) for key, weight in weights.items()}
    counts = {key: int(amount) for key, amount in exact.items()}
    remainder = total - sum(counts.values())
    for key in sorted(weights, key=lambda item: (-(exact[item] - counts[item]), item))[:remainder]:
        counts[key] += 1
    return counts


def owners(spec: dict) -> set[str]:
    return {part["owner"] for part in spec["split"]} if "split" in spec else {spec["owner"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build/demography/indian-core-candidate.yml")
    args = parser.parse_args()
    output = (ROOT / args.out).resolve()
    if not output.is_relative_to(ROOT / "build"):
        raise ValueError("candidate output must stay in this mod's build directory")
    plan = yaml.safe_load((HERE / "plan.yml").read_text(encoding="utf-8"))
    legacy = json.loads((HERE / "legacy-population-snapshot.json").read_text(encoding="utf-8"))
    predecessor = json.loads((HERE / "predecessor-population.json").read_text(encoding="utf-8"))
    world = yaml.safe_load((ROOT / "world/scenario.yml").read_text(encoding="utf-8"))
    if set(plan["countries"]) != {"MUG", "BGL", "MAR", "GWA", "IND", "NAG"}:
        raise ValueError("Indian country list changed")
    if sum(plan["countries"][tag]["population"] for tag in ("MAR", "GWA", "IND", "NAG")) != plan["maratha_member_total"]:
        raise ValueError("Maratha member totals differ from federation target")
    world["title"] = "The Golden Crescent — 1836 siyasi dünya ve Hint demografisi"
    world["description"] = (
        "1836 alternatif siyasi dünya: Rûm, Mısır, İran, Endülüs, Britanya, Lehistan "
        "ve Hint çekirdeğinde nüfus, ortak kültür-din ve okuryazarlık girdileri "
        "düzenlendi. Diğer bölgelerde geçici vanilla nüfus aktarımı sürer."
    )
    audit = {"countries": plan["countries"], "maratha_member_total": plan["maratha_member_total"], "shares": {}}
    country_totals = defaultdict(int)
    for state, by_owner in plan["states"].items():
        spec = world["states"].get(state)
        if not spec or not set(by_owner) <= owners(spec) or spec.get("pops") != "inherit":
            raise ValueError(f"{state}: unexpected political owner or POP inheritance")
        for tag, design in by_owner.items():
            if tag not in plan["countries"] or tag not in legacy.get(state, {}):
                raise ValueError(f"{state}/{tag}: unknown country or frozen share")
            mix = design["mix"]
            if any(group.count("/") != 1 for group in mix):
                raise ValueError(f"{state}/{tag}: expected joint culture/religion mix")
            frozen_free = defaultdict(int)
            retained = defaultdict(int)
            for row in legacy[state][tag]:
                group = f"{row['culture']}/{row['religion']}"
                if row["pop_type"]:
                    retained[f"{group}/{row['pop_type']}"] += row["size"]
                else:
                    frozen_free[group] += row["size"]
            omitted = {group: size for group, size in frozen_free.items()
                       if group not in mix and size > sum(frozen_free.values()) * .05}
            if omitted:
                raise ValueError(f"{state}/{tag}: major inherited group omitted: {omitted}")
            retained.update({group: size for group, size in frozen_free.items() if group not in mix})
            total = design["population"]
            free_total = total - sum(retained.values())
            if free_total <= 0:
                raise ValueError(f"{state}/{tag}: retained POPs exceed target")
            groups = apportion(free_total, mix)
            groups.update(retained)
            if sum(groups.values()) != total:
                raise ValueError(f"{state}/{tag}: composition does not add up")
            shares = [count / total for count in groups.values()]
            shares[-1] = 1.0 - sum(shares[:-1])
            composition = []
            for (group, count), share in zip(groups.items(), shares):
                parts = group.split("/")
                row = {"culture": parts[0], "religion": parts[1], "share": share}
                if len(parts) == 3:
                    row["pop_type"] = parts[2]
                composition.append(row)
            population = {"total": total, "literacy": design["literacy"], "composition": composition}
            previous = spec.get("population", {}).get("by_owner", {}).get(tag)
            if previous is not None and previous not in (population, predecessor.get(f"{state}/{tag}")):
                raise ValueError(f"{state}/{tag}: previous population differs from frozen baseline")
            spec.setdefault("population", {}).setdefault("by_owner", {})[tag] = population
            audit["shares"][f"{state}/{tag}"] = {
                "state": state, "owner": tag, "population": total, "literacy": design["literacy"],
                "groups": groups, "fixed_legacy_groups": dict(retained), "reason": design["reason"],
            }
            country_totals[tag] += total
    # Gwalior/Indore each retain a tiny, separately owned Rajputana share.
    for tag in ("GWA", "IND"):
        country_totals[tag] += sum(row["size"] for row in legacy["STATE_RAJPUTANA"][tag])
    for tag, target in plan["countries"].items():
        if country_totals[tag] != target["population"]:
            raise ValueError(f"{tag}: direct state shares total {country_totals[tag]}, not {target['population']}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    (output.parent / "indian-core-plan-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {output.relative_to(ROOT)} ({len(audit['shares'])} state shares)")


if __name__ == "__main__":
    main()
