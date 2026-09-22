"""Audit the six Nizam economies and formation materiel at script values.

This is a capacity/dependency audit, not a Victoria 3 market simulation.  It
parses the selected vanilla production methods and unit definitions directly.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SUBJECTS = ("BOS", "ALB", "BUL", "ADA", "ERZ", "TRB")
os.environ.setdefault("VIC3_MOD_DIR", str(ROOT))
local = json.loads((ROOT / ".vic3-tools.local.json").read_text())
sys.path.insert(0, str(Path(local["toolkit"]) / "src"))

from vic3 import mechanics, pdx  # noqa: E402


def numbers(node):
    if not node:
        return
    for item in node.items:
        if item.key and isinstance(item.value, str):
            try:
                yield item.key, float(item.value)
            except ValueError:
                pass


def add_goods(node, multiplier, target, prefix):
    for key, value in numbers(node):
        if key.startswith(prefix) and key.endswith("_add"):
            target[key.removeprefix(prefix).removesuffix("_add")] += value * multiplier


def blank():
    return {
        "inputs": defaultdict(float),
        "outputs": defaultdict(float),
        "upkeep": defaultdict(float),
        "fleet_construction": defaultdict(float),
        "formations": defaultdict(int),
        "building_levels": 0,
        "building_records": 0,
        "army_max_manpower": 0,
        "navy_max_crew": 0,
    }


def main():
    scenario = json.loads((HERE / "scenario.json").read_text())
    catalog = mechanics.catalog()
    rows = {tag: blank() for tag in SUBJECTS}
    sources = set()

    for state in scenario["states"].values():
        for tag in SUBJECTS:
            owner = state.get("industry", {}).get("by_owner", {}).get(tag, {})
            for spec in owner.get("buildings", {}).values():
                if not isinstance(spec, dict) or spec.get("level", 0) <= 0:
                    continue
                level = spec["level"]
                methods = spec.get("production_methods", [])
                if not methods:
                    continue
                rows[tag]["building_levels"] += level
                rows[tag]["building_records"] += 1
                for method in methods:
                    rule = catalog["production_methods"][method]
                    sources.add(rule["source"])
                    script = pdx.parse(rule["script"])
                    modifiers = script.get_node("building_modifiers")
                    workforce = modifiers.get_node("workforce_scaled") if modifiers else None
                    add_goods(workforce, level, rows[tag]["inputs"], "goods_input_")
                    add_goods(workforce, level, rows[tag]["outputs"], "goods_output_")

    for tag in SUBJECTS:
        for law in scenario["countries"][tag]["laws"]["values"]:
            sources.add(catalog["laws"][law]["source"])
        for ig in scenario["countries"][tag]["interest_groups"]["ruling"]:
            sources.add(catalog["interest_groups"][ig]["source"])
        for formation in scenario["countries"][tag]["military"]["formations"]:
            sources.add(catalog["strategic_regions"][formation["hq_region"]]["source"])
            army = formation["type"] == "army"
            table = "combat_units" if army else "ships"
            units = formation.get("units" if army else "ships", [])
            for unit in units:
                count = unit["count"]
                rule = catalog[table][unit["type"]]
                sources.add(rule["source"])
                script = pdx.parse(rule["script"])
                rows[tag]["formations"][unit["type"]] += count
                if army:
                    rows[tag]["army_max_manpower"] += int(rule.get("max_manpower", 0)) * count
                    add_goods(script.get_node("upkeep_modifier"), count, rows[tag]["upkeep"], "goods_input_")
                else:
                    modifier = script.get_node("modifier")
                    rows[tag]["navy_max_crew"] += int(dict(numbers(modifier)).get("ship_crew_max_add", 0)) * count
                    add_goods(script.get_node("materiel_goods"), count, rows[tag]["upkeep"], "goods_input_")
                    add_goods(script.get_node("construction_goods"), count, rows[tag]["fleet_construction"], "goods_input_")

    result = {"scope": "six Nizam subjects: explicit PM output/input and full formation materiel upkeep", "countries": {}}
    for tag, row in rows.items():
        goods = {}
        for good in sorted(set(row["inputs"]) | set(row["outputs"]) | set(row["upkeep"])):
            output = row["outputs"][good]
            inputs = row["inputs"][good]
            upkeep = row["upkeep"][good]
            goods[good] = {
                "explicit_output": round(output, 2),
                "industrial_input": round(inputs, 2),
                "industry_net": round(output - inputs, 2),
                "formation_upkeep": round(upkeep, 2),
                "after_formation_upkeep": round(output - inputs - upkeep, 2),
            }
        dependencies = sorted(good for good, values in goods.items() if values["after_formation_upkeep"] < 0)
        result["countries"][tag] = {
            "selected_building_records": row["building_records"],
            "selected_building_levels": row["building_levels"],
            "formation_counts": dict(sorted(row["formations"].items())),
            "army_max_manpower": row["army_max_manpower"],
            "navy_max_crew": row["navy_max_crew"],
            "goods": goods,
            "trade_dependencies": dependencies,
            "fleet_full_construction_goods": {key: round(value, 2) for key, value in sorted(row["fleet_construction"].items())},
        }

    result["source_sha256"] = {
        source: hashlib.sha256((mechanics.VANILLA / source).read_bytes()).hexdigest()
        for source in sorted(sources)
    }
    result["interpretation"] = {
        "capacity": "nameplate values from explicit selected production methods",
        "dependency": "negative local balance flags intended trade/customs reliance; it is not an opening-day shortage prediction",
        "not_included": [
            "employment, qualifications, throughput and infrastructure",
            "prices, POP consumption, trade routes, convoys and market access",
            "wages, treasury, debt, legitimacy and interest-group clout",
            "mobilization state, readiness, replacement and fleet construction timing",
        ],
    }
    target = HERE / "capacity-audit.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(target)


if __name__ == "__main__":
    main()
