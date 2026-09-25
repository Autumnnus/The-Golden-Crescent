"""M0 source fixes for runtime errors seen in the 24 Sep 2026 opening log.

1. Buildings whose inherited ownership points at another state/country/company (Atlas keeps the
   vanilla owner's capital region when it rewrites the owner) become local explicit buildings
   with the same level and production methods.
2. GBR is only the London crown's overseas dependencies here; its inherited European army and
   fleet (HQs in regions it does not hold) are cleared.
3. Eight countries that are no longer subjects inherited vanilla `add_liberty_desire`; their
   inherited diplomacy is reset and the three bilateral relations lost with it are restored.
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLKIT = Path(os.environ.get("VIC3_TOOLS_HOME") or json.loads(
    (ROOT / ".vic3-tools.local.json").read_text())["toolkit"])
if sys.version_info < (3, 10):
    runtime = TOOLKIT / ".venv/bin/python"
    os.execv(str(runtime), [str(runtime), __file__, *sys.argv[1:]])
sys.path.insert(0, str(TOOLKIT / "src"))
os.chdir(ROOT)
from vic3 import mechanics, pdx  # noqa: E402

HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"
LIBERTY_RESET = ["IQU", "KZH", "NPU", "OZH", "SEQ", "SER", "UZH", "WAL"]
RESTORED_RELATIONS = [
    {"actor": "MOL", "target": "WAL", "value": 50},
    {"actor": "MON", "target": "SER", "value": 30},
    {"actor": "WAL", "target": "SER", "value": 20},
]
CLEARED_MILITARY = ["GBR"]


def invalid_ownership(record, tag: str, owned: dict) -> bool:
    for ownership in record.getall("add_ownership"):
        for item in ownership.items:
            if item.key == "company":
                return True
            country = (item.value.get_str("country") or "").replace("c:", "").strip('"')
            region = (item.value.get_str("region") or "").strip('"')
            if item.key == "country" and country != tag:
                return True
            if item.key == "building" and (country not in owned or (region and region not in owned[country])):
                return True
    return False


def main() -> None:
    build = ROOT / "build/mechanics"
    world = yaml.safe_load((build / "m0-source.yml").read_text())
    report = json.loads((build / "m0-source-report.json").read_text())
    data = mechanics.catalog()
    owned = defaultdict(set)
    for state, srep in report["states"].items():
        for tag in srep["owners"]:
            owned[tag].add(state)
    buildings = pdx.parse_file(ROOT / "common/history/buildings/tgc_buildings.txt").get_node("BUILDINGS")
    fixes, audit = defaultdict(dict), {"ownership": [], "military": CLEARED_MILITARY, "liberty_reset": LIBERTY_RESET}
    for state_block in buildings.items:
        state = state_block.key[2:]
        for owner_block in state_block.value.items:
            tag = owner_block.key.split(":")[1]
            records = owner_block.value.getall("create_building")
            bad = {str(r.get_str("building")) for r in records if invalid_ownership(r, tag, owned)}
            if bad:
                # Atlas validates every record of a touched owner; convert records whose methods the
                # owner cannot use as well.
                techs = set(report["countries"][tag]["technologies"])
                laws = set(report["countries"][tag]["laws"])
                for r in records:
                    if set(data["buildings"][str(r.get_str("building"))]["unlocking_technologies"]) - techs:
                        bad.add(str(r.get_str("building")))
                    for pm in map(str, r.get_list("activate_production_methods")):
                        rule = data["production_methods"].get(pm)
                        if rule and (set(rule["unlocking_technologies"]) - techs or set(rule["disallowing_laws"]) & laws):
                            bad.add(str(r.get_str("building")))
            for name in sorted(bad):
                same = [r for r in records if str(r.get_str("building")) == name]
                level = sum(int(float(v)) for r in same for v in _levels(r))
                pms = [str(pm) for pm in same[0].get_list("activate_production_methods")]
                techs = set(report["countries"][tag]["technologies"])
                laws = set(report["countries"][tag]["laws"])
                ok = lambda m: not set(data["production_methods"][m]["unlocking_technologies"]) - techs \
                    and not set(data["production_methods"][m]["disallowing_laws"]) & laws
                kept = []
                for group in data["buildings"][name]["production_method_groups"]:
                    methods = data["production_method_groups"][group]["production_methods"]
                    chosen = [m for m in pms if m in methods]
                    if chosen and ok(chosen[0]):
                        kept.append(chosen[0])
                    elif methods and any(ok(m) for m in methods):
                        kept.append(str(next(m for m in methods if ok(m))))
                pms = kept
                for group in data["buildings"][name]["production_method_groups"]:
                    methods = data["production_method_groups"][group]["production_methods"]
                    if methods and not set(methods) & set(pms):
                        usable = [m for m in methods if not set(data["production_methods"][m]["unlocking_technologies"]) - techs
                                  and not set(data["production_methods"][m]["disallowing_laws"]) & laws]
                        if usable:
                            pms.append(str(usable[0]))
                kind = data["buildings"][name].get("ownership_type")
                if set(data["buildings"][name]["unlocking_technologies"]) - set(report["countries"][tag]["technologies"]):
                    fixes[state].setdefault(tag, {})[name] = 0
                    audit["ownership"].append(f"{state}/{tag}/{name}: removed, owner lacks technology")
                    continue
                fixes[state].setdefault(tag, {})[name] = {
                    "level": level, "production_methods": pms,
                    "ownership": "self" if kind == "self" else "government"}
                audit["ownership"].append(f"{state}/{tag}/{name}")
    for state, owners in fixes.items():
        industry = world["states"][state].setdefault("industry", {})
        for tag, items in owners.items():
            part = industry.setdefault("by_owner", {}).setdefault(tag, {"mode": "merge", "buildings": {}})
            for name, item in items.items():
                previous = part["buildings"].get(name)
                if isinstance(previous, dict) and isinstance(item, dict):
                    previous["ownership"] = item["ownership"]  # keep the M2 level/methods, only localise ownership
                else:
                    part["buildings"][name] = item
    for tag in CLEARED_MILITARY:
        entry = world["countries"].setdefault(tag, {})
        if "military" in entry:
            raise ValueError(f"{tag}: existing military plan would be replaced")
        entry["military"] = {"mode": "replace", "formations": []}
    diplomacy = world["diplomacy"]
    diplomacy["reset_countries"] = sorted(set(diplomacy.get("reset_countries") or []) | set(LIBERTY_RESET))
    diplomacy["relations"] = (diplomacy.get("relations") or []) + RESTORED_RELATIONS
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, temel ekonomi ve log temizliği"
    output = build / "m0-candidate.yml"
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    (build / "m0-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n")
    print(f"ownership fixes {len(audit['ownership'])}; military cleared {CLEARED_MILITARY}; liberty reset {len(LIBERTY_RESET)}")


def _levels(record):
    values = []

    def walk(node):
        for item in node.items:
            if item.key == "levels" and isinstance(item.value, str):
                values.append(item.value)
            elif isinstance(item.value, pdx.Node):
                walk(item.value)
    for ownership in record.getall("add_ownership"):
        walk(ownership)
    return values


if __name__ == "__main__":
    main()
