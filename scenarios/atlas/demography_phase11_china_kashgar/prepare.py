"""Prepare five Chinese governments and Kashgar with exact POP groups."""

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build/demography/china-kashgar-candidate.yml")
    args = parser.parse_args()
    output = (ROOT / args.out).resolve()
    if not output.is_relative_to(ROOT / "build"):
        raise ValueError("candidate output must stay in this mod's build directory")
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    frozen = json.loads((HERE / "source-pops.json").read_text())
    world = yaml.safe_load((ROOT / "world/scenario.yml").read_text())
    if len(plan["states"]) != 34 or set(plan["countries"]) != {spec["owner"] for spec in plan["states"].values()}:
        raise ValueError("plan country/state coverage differs")
    if set(frozen) != {f"{state}/{spec['owner']}" for state, spec in plan["states"].items()}:
        raise ValueError("frozen POP shares differ from plan")
    by_country = defaultdict(dict)
    for state, design in plan["states"].items():
        tag = design["owner"]
        spec = world["states"].get(state)
        owners = {part["owner"] for part in spec.get("split", [])} if spec else set()
        if spec and "owner" in spec:
            owners.add(spec["owner"])
        if not spec or tag not in owners or spec.get("pops") != "inherit":
            raise ValueError(f"{state}/{tag}: political owner or POP policy changed")
        if tag in spec.get("population", {}).get("by_owner", {}):
            raise ValueError(f"{state}/{tag}: existing population plan would be replaced")
        by_country[tag][f"{state}/{tag}"] = sum(row["size"] for row in frozen[f"{state}/{tag}"])
    for tag, additions in plan["country_primary_culture_additions"].items():
        country = world["countries"].get(tag)
        if not country or not additions or any(culture in country["cultures"] for culture in additions):
            raise ValueError(f"{tag}: planned primary-culture addition already exists or country missing")
        country["cultures"].extend(additions)
    audit = {"shares": {}, "countries": plan["countries"], "core_states": plan["jiangnan_lower_yangtze_core"]}
    assigned = {}
    for tag, design in plan["countries"].items():
        assigned.update(apportion(design["population"], by_country[tag]))
    for state, design in plan["states"].items():
        tag = design["owner"]
        key = f"{state}/{tag}"
        target = assigned[key]
        fixed, free = Counter(), Counter()
        for row in frozen[key]:
            group = f"{row['culture']}/{row['religion']}"
            if row["pop_type"]:
                fixed[f"{group}/{row['pop_type']}"] += row["size"]
            else:
                free[group] += row["size"]
        if target <= sum(fixed.values()):
            raise ValueError(f"{key}: preserved professions exceed target")
        groups = apportion(target - sum(fixed.values()), dict(free))
        groups.update(fixed)
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
        world["states"][state].setdefault("population", {}).setdefault("by_owner", {})[tag] = {
            "total": target, "literacy": design["literacy"], "composition": composition}
        audit["shares"][key] = {"prior_population": by_country[tag][key], "population": target,
                                "literacy": design["literacy"], "groups": dict(groups),
                                "fixed_professions": dict(fixed)}
    core_total = sum(assigned[f"{state}/JNG"] for state in plan["jiangnan_lower_yangtze_core"])
    if not plan["jiangnan_core_range"][0] <= core_total <= plan["jiangnan_core_range"][1]:
        raise ValueError(f"Jiangnan lower Yangtze core outside revised target: {core_total}")
    audit["jiangnan_core_population"] = core_total
    for tag, policy in plan["countries"].items():
        rows = [(row["population"], row["literacy"]) for key, row in audit["shares"].items() if key.endswith("/" + tag)]
        if sum(pop for pop, _ in rows) != policy["population"]:
            raise ValueError(f"{tag}: country total differs")
        literacy = sum(pop * rate for pop, rate in rows) / policy["population"]
        if not policy["literacy_range"][0] <= literacy <= policy["literacy_range"][1]:
            raise ValueError(f"{tag}: weighted literacy outside plan range")
        audit["countries"][tag]["weighted_literacy"] = literacy
    world["title"] = "The Golden Crescent — 1836 siyasi dünya ve Çin–Kaşgar demografisi"
    world["description"] = (
        "1836 alternatif siyasi dünya ve önceki demografi korunur. Beş ayrı Çin "
        "yönetimi ile Kaşgar'ın 34 doğrudan state payında nüfus, ortak kültür-din "
        "ve okuryazarlık girdileri; Yue'nin ana kültürü düzenlendi."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    (output.parent / "china-kashgar-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {output.relative_to(ROOT)} ({len(audit['shares'])} shares; Jiangnan core {core_total:,})")


if __name__ == "__main__":
    main()
