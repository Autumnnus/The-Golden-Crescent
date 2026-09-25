"""Build mainland Southeast Asian demography and remove the Danish Pegu enclave."""

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
    if total <= 0 or not weights or any(value <= 0 for value in weights.values()):
        raise ValueError("population and weights must be positive")
    denominator = sum(weights.values())
    exact = {key: Fraction(total * weight, denominator) for key, weight in weights.items()}
    counts = {key: int(amount) for key, amount in exact.items()}
    for key in sorted(weights, key=lambda item: (-(exact[item] - counts[item]), item))[:total - sum(counts.values())]:
        counts[key] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build/demography/mainland-seasia-candidate.yml")
    args = parser.parse_args()
    output = (ROOT / args.out).resolve()
    if not output.is_relative_to(ROOT / "build"):
        raise ValueError("candidate output must stay in this mod's build directory")
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    frozen = json.loads((HERE / "source-pops.json").read_text())
    world = yaml.safe_load((ROOT / "world/scenario.yml").read_text())
    states = {f"{name.split('/')[0]}/{spec['owner']}": spec for name, spec in plan["states"].items()}
    transfer = plan["province_transfer"]
    old_key = f"{transfer['state']}/{transfer['old_owner']}"
    new_key = f"{transfer['state']}/{transfer['new_owner']}"
    if len(states) != 28 or set(frozen) != set(states) | {old_key} or new_key not in states:
        raise ValueError("plan and frozen share coverage differ")
    parts = world["states"][transfer["state"]]["split"]
    previous = next((part for part in parts if part["owner"] == transfer["old_owner"]), None)
    receiving = next((part for part in parts if part["owner"] == transfer["new_owner"]), None)
    if not previous or previous["provinces"] != [transfer["province"]] or not receiving:
        raise ValueError("Pegu Danish province ownership changed; refuse transfer")
    if transfer["province"] in receiving["provinces"]:
        raise ValueError("province is already assigned to Burma")
    receiving["provinces"].append(transfer["province"])
    parts.remove(previous)
    by_country = defaultdict(dict)
    for key in states:
        state, tag = key.split("/")
        spec = world["states"].get(state)
        owners = {part["owner"] for part in spec.get("split", [])} if spec else set()
        if spec and "owner" in spec:
            owners.add(spec["owner"])
        if not spec or tag not in owners or spec.get("pops") != "inherit":
            raise ValueError(f"{key}: political owner or POP policy changed")
        if tag in spec.get("population", {}).get("by_owner", {}):
            raise ValueError(f"{key}: existing population plan would be replaced")
        rows = frozen[key] + (frozen[old_key] if key == new_key else [])
        by_country[tag][key] = sum(row["size"] for row in rows)
    if set(by_country) != set(plan["countries"]):
        raise ValueError("country coverage differs")
    assigned = {}
    for tag, design in plan["countries"].items():
        assigned.update(apportion(design["population"], by_country[tag]))
    audit = {"shares": {}, "countries": plan["countries"], "province_transfer": transfer,
             "transferred_population": sum(row["size"] for row in frozen[old_key])}
    for key, design in states.items():
        state, tag = key.split("/")
        target = assigned[key]
        fixed, inherited = Counter(), Counter()
        for row in frozen[key] + (frozen[old_key] if key == new_key else []):
            group = f"{row['culture']}/{row['religion']}"
            if row["pop_type"]:
                fixed[f"{group}/{row['pop_type']}"] += row["size"]
            else:
                inherited[group] += row["size"]
        if target <= sum(fixed.values()):
            raise ValueError(f"{key}: preserved professions exceed target")
        counts = apportion(target - sum(fixed.values()), dict(inherited))
        counts.update(fixed)
        composition = []
        cumulative = 0.0
        for index, (group, count) in enumerate(counts.items()):
            if count == 0:
                continue
            share = 1.0 - cumulative if index == len(counts) - 1 else count / target
            cumulative += share
            parts = group.split("/")
            row = {"culture": parts[0], "religion": parts[1], "share": share}
            if len(parts) == 3:
                row["pop_type"] = parts[2]
            composition.append(row)
        world["states"][state].setdefault("population", {}).setdefault("by_owner", {})[tag] = {
            "total": target, "literacy": design["literacy"], "composition": composition}
        audit["shares"][key] = {"prior_population": by_country[tag][key], "population": target,
                                "literacy": design["literacy"], "groups": dict(counts),
                                "fixed_professions": dict(fixed)}
    for tag, policy in plan["countries"].items():
        rows = [(row["population"], row["literacy"]) for key, row in audit["shares"].items()
                if key.endswith("/" + tag)]
        if sum(pop for pop, _ in rows) != policy["population"]:
            raise ValueError(f"{tag}: country total differs")
        weighted = sum(pop * rate for pop, rate in rows) / policy["population"]
        if not policy["literacy_range"][0] <= weighted <= policy["literacy_range"][1]:
            raise ValueError(f"{tag}: weighted literacy outside plan range")
        audit["countries"][tag]["weighted_literacy"] = weighted
    world["title"] = "The Golden Crescent — 1836 siyasi dünya ve Güneydoğu Asya demografisi"
    world["description"] = (
        "1836 alternatif siyasi dünya ve önceki demografi korunur. Burma'daki son Danimarka Pegu province'i "
        "yerel yönetime aktarılır; Güneydoğu Asya anakarasının 28 doğrudan state payında nüfus, "
        "ortak kültür-din ve okuryazarlık girdileri kurulur."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    (output.parent / "mainland-seasia-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {output.relative_to(ROOT)} ({len(audit['shares'])} shares)")


if __name__ == "__main__":
    main()
