"""Audit Phase 1B.3 production capacity against formation materiel needs.

All values are nameplate, full-employment script values. Prices, wages,
qualifications, throughput and market access require a Victoria 3 runtime test.
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


def goods_from(node, multiplier, target):
    for key, value in numbers(node):
        if key.startswith("goods_input_") and key.endswith("_add"):
            target[key.removeprefix("goods_input_").removesuffix("_add")] += value * multiplier


def main():
    scenario = json.loads((HERE / "scenario.json").read_text())
    catalog = mechanics.catalog()
    goods_input = defaultdict(float)
    goods_output = defaultdict(float)
    military_upkeep = defaultdict(float)
    fleet_construction = defaultdict(float)
    country_capacity = defaultdict(float)
    state_capacity = defaultdict(float)
    sources = set()
    selected_levels = 0
    selected_records = 0

    for state in scenario["states"].values():
        owner = state.get("industry", {}).get("by_owner", {}).get("RUM", {})
        for spec in owner.get("buildings", {}).values():
            if not isinstance(spec, dict) or spec.get("level", 0) <= 0:
                continue
            level = spec["level"]
            methods = spec.get("production_methods", [])
            if not methods:
                continue
            selected_levels += level
            selected_records += 1
            for method in methods:
                rule = catalog["production_methods"][method]
                sources.add(rule["source"])
                script = pdx.parse(rule["script"])
                modifiers = script.get_node("building_modifiers")
                workforce = modifiers.get_node("workforce_scaled") if modifiers else None
                for key, value in numbers(workforce):
                    good = key.removeprefix("goods_input_").removesuffix("_add")
                    if key.startswith("goods_input_") and key.endswith("_add"):
                        goods_input[good] += value * level
                    elif key.startswith("goods_output_") and key.endswith("_add"):
                        good = key.removeprefix("goods_output_").removesuffix("_add")
                        goods_output[good] += value * level
                for scope_name, target in (("country_modifiers", country_capacity), ("state_modifiers", state_capacity)):
                    scope = script.get_node(scope_name)
                    scaled = scope.get_node("workforce_scaled") if scope else None
                    for key, value in numbers(scaled):
                        target[key] += value * level

    army_manpower = 0
    navy_crew = 0
    formation_counts = defaultdict(int)
    for ig in scenario["countries"]["RUM"]["interest_groups"]["ruling"]:
        sources.add(catalog["interest_groups"][ig]["source"])
    for technology in ("general_staff", "napoleonic_warfare"):
        sources.add(catalog["technologies"][technology]["source"])
    for formation in scenario["countries"]["RUM"]["military"]["formations"]:
        sources.add(catalog["strategic_regions"][formation["hq_region"]]["source"])
        table = "combat_units" if formation["type"] == "army" else "ships"
        rows = formation.get("units" if formation["type"] == "army" else "ships", [])
        for row in rows:
            rule = catalog[table][row["type"]]
            sources.add(rule["source"])
            script = pdx.parse(rule["script"])
            count = row["count"]
            formation_counts[row["type"]] += count
            if table == "combat_units":
                army_manpower += int(rule.get("max_manpower", 0)) * count
                goods_from(script.get_node("upkeep_modifier"), count, military_upkeep)
            else:
                modifier = script.get_node("modifier")
                navy_crew += int(dict(numbers(modifier)).get("ship_crew_max_add", 0)) * count
                goods_from(script.get_node("materiel_goods"), count, military_upkeep)
                goods_from(script.get_node("construction_goods"), count, fleet_construction)

    goods = {}
    for good in sorted(set(goods_input) | set(goods_output) | set(military_upkeep)):
        supplied = goods_output[good]
        industrial = goods_input[good]
        upkeep = military_upkeep[good]
        goods[good] = {
            "explicit_output": round(supplied, 2),
            "industrial_input": round(industrial, 2),
            "industry_net": round(supplied - industrial, 2),
            "formation_upkeep": round(upkeep, 2),
            "after_formation_upkeep": round(supplied - industrial - upkeep, 2),
        }

    result = {
        "scope": "explicit RUM production methods and full formation materiel upkeep",
        "selected_building_records": selected_records,
        "selected_building_levels": selected_levels,
        "formation_counts": dict(sorted(formation_counts.items())),
        "army_max_manpower": army_manpower,
        "navy_max_crew": navy_crew,
        "goods": goods,
        "fleet_full_construction_goods": {key: round(value, 2) for key, value in sorted(fleet_construction.items())},
        "country_capacity": {key: round(value, 2) for key, value in sorted(country_capacity.items())},
        "state_capacity": {key: round(value, 2) for key, value in sorted(state_capacity.items())},
        "source_sha256": {
            source: hashlib.sha256((mechanics.VANILLA / source).read_bytes()).hexdigest()
            for source in sorted(sources)
        },
        "interpretation": {
            "formation_upkeep": "scripted goods_input additions at full unit count; prices and mobilization behavior are not simulated",
            "fleet_full_construction_goods": "historical/replacement stock requirement, not recurring opening-day consumption",
            "not_included": [
                "employment, qualifications and throughput",
                "government and military wages",
                "POP consumption, trade, convoy availability and prices",
                "treasury, debt principal and interest",
                "ship modifications, readiness and repair state",
            ],
        },
    }
    target = HERE / "military-capacity-audit.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(target)


if __name__ == "__main__":
    main()
