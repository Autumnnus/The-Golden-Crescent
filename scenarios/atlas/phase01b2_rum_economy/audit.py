"""Calculate directional full-employment capacity from explicitly selected PMs.

The result is a source audit, not a Victoria 3 market simulation. Unlisted
inherited buildings, subsistence production, trade and prices are intentionally
outside its scope.
"""

from __future__ import annotations

import json
import os
import sys
import hashlib
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
os.environ.setdefault("VIC3_MOD_DIR", str(ROOT))
local = json.loads((ROOT / ".vic3-tools.local.json").read_text())
sys.path.insert(0, str(Path(local["toolkit"]) / "src"))

from vic3 import mechanics, pdx  # noqa: E402


def numeric_items(node):
    if not node:
        return
    for item in node.items:
        if item.key and isinstance(item.value, str):
            try:
                yield item.key, float(item.value)
            except ValueError:
                pass


def main():
    plan = json.loads((HERE / "economy-plan.json").read_text())
    rules = mechanics.catalog()["production_methods"]
    goods_input = defaultdict(float)
    goods_output = defaultdict(float)
    country_capacity = defaultdict(float)
    state_capacity = defaultdict(float)
    selected_levels = 0
    selected_buildings = 0
    selected_sources = set()

    for state in plan["states"].values():
        for spec in state["buildings"].values():
            if not isinstance(spec, dict):
                continue
            level = spec["level"]
            if level <= 0 or not spec.get("production_methods"):
                continue
            selected_levels += level
            selected_buildings += 1
            for method in spec["production_methods"]:
                selected_sources.add(rules[method]["source"])
                script = pdx.parse(rules[method]["script"])
                modifiers = script.get_node("building_modifiers")
                workforce = modifiers.get_node("workforce_scaled") if modifiers else None
                for key, value in numeric_items(workforce):
                    if key.startswith("goods_input_") and key.endswith("_add"):
                        goods_input[key.removeprefix("goods_input_").removesuffix("_add")] += value * level
                    elif key.startswith("goods_output_") and key.endswith("_add"):
                        goods_output[key.removeprefix("goods_output_").removesuffix("_add")] += value * level
                for scope_name, target in (("country_modifiers", country_capacity), ("state_modifiers", state_capacity)):
                    scope = script.get_node(scope_name)
                    scaled = scope.get_node("workforce_scaled") if scope else None
                    for key, value in numeric_items(scaled):
                        target[key] += value * level

    goods = {}
    for good in sorted(set(goods_input) | set(goods_output)):
        supplied = goods_output[good]
        demanded = goods_input[good]
        goods[good] = {
            "explicit_output": round(supplied, 2),
            "explicit_input": round(demanded, 2),
            "explicit_net": round(supplied - demanded, 2),
        }

    result = {
        "scope": "explicitly selected production methods at full employment",
        "selected_building_records": selected_buildings,
        "selected_building_levels": selected_levels,
        "goods": goods,
        "country_capacity": {key: round(value, 2) for key, value in sorted(country_capacity.items())},
        "state_capacity": {key: round(value, 2) for key, value in sorted(state_capacity.items())},
        "source_sha256": {
            source: hashlib.sha256((mechanics.VANILLA / source).read_bytes()).hexdigest()
            for source in sorted(selected_sources)
        },
        "interpretation": {
            "not_included": [
                "subsistence output and consumption",
                "unlisted inherited/default production methods",
                "trade routes, convoy availability and prices",
                "employment, qualifications and throughput modifiers",
                "government wages and institution bureaucracy expense",
            ],
            "negative_net": "planned domestic/import dependency to inspect in the engine, not a validation error",
            "positive_net": "nameplate capacity, not proof that inputs, workers or buyers exist",
        },
    }
    target = HERE / "capacity-audit.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(target)


if __name__ == "__main__":
    main()
