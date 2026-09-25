"""Apply M1b to a world copy: literacy inputs, the regenerated M1 plan and the vanilla-history plan.

1. `target` is the literacy expected on the opening screen. Setup adds a few points per school
   level on top of the input (24-25 Sep tests), so the country input is target - school boost.
   Every state share of the frozen pre-M1b demography (m1b-source.yml) is scaled by
   input / previous, keeping the regional differences of the demography.
2. The 159 M1 countries get technology, laws and institutions from the regenerated
   mechanics_m1_institutions/plan.yml (replacing the M1 values).
3. The vanilla-history Islamic countries in plan.yml get their schools laws, institutions and
   missing technologies merged on top of the vanilla history.
4. Atlas validates every building record of a touched country. Inherited vanilla records whose
   production methods the country cannot use become explicit merge items with the first usable
   method of the same group (same level, local ownership), as in M0.
"""

from __future__ import annotations

import argparse
import json
import os
import re
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
from vic3 import development as dev, mechanics, pdx  # noqa: E402
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"
BOUNDS = (0.01, 0.95)
EDUCATION = {"law_no_schools", "law_religious_schools", "law_private_schools", "law_public_schools", "law_terakoya"}


def boost(edu: str | None, level: int) -> float:
    """Points the setup recalculation adds above the literacy input.

    Calibration: Sweden religious schools 3 opened at 51% from a 46.7% input (+4.3); Rum public
    schools 3 at 47% from 40% (+7); Rum/Isfahan public schools 5 at ~72-80% from 64-70% (+8-11).
    Private schools are assumed to act like religious schools. Japan's terakoya law gives +0.25
    access without an institution (about public schools 2).
    """
    if edu == "law_terakoya":
        return 0.05
    if not level or edu in (None, "law_no_schools"):
        return 0.0
    if edu == "law_public_schools":
        return 0.01 + 0.02 * level
    return 0.015 * level


def education(targets: dict, m1: dict, m1b: dict, report: dict) -> dict:
    """Education law and schools level every country opens with."""
    text = (ROOT / "common/history/countries/ve_scenario_countries.txt").read_text(encoding="utf-8-sig")
    blocks = dict(re.findall(r"\nc:(\w+) \?= \{(.*?)\n\}", text, re.S))
    effects = {"effect_starting_politics_conservative": "law_religious_schools",
               "effect_starting_politics_liberal": "law_private_schools"}
    result = {}
    for tag in targets:
        if tag in m1 or tag in m1b:
            row = m1.get(tag) or m1b[tag]
            laws = row["laws"]
            edu = next((law for law in laws if law in EDUCATION), None)
            level = row["institutions"].get("institution_schools", 0)
        else:
            block = blocks.get(tag, "")
            edu = next((law for law in report["countries"][tag]["laws"] if law in EDUCATION), None)
            edu = edu or next((law for effect, law in effects.items() if effect in block), None)
            levels = re.findall(r"institution = institution_schools\s+level = (\d+)", block)
            level = int(levels[-1]) if levels else 0
        result[tag] = {"education": edu, "schools": level}
    return result


def scale_literacy(world: dict, base: dict, targets: dict, schools: dict) -> dict:
    totals = defaultdict(lambda: [0, 0.0])
    for spec in base["states"].values():
        for tag, share in spec["population"]["by_owner"].items():
            totals[tag][0] += share["total"]
            totals[tag][1] += share["total"] * share["literacy"]
    inputs = {}
    for tag, (people, literate) in totals.items():
        previous = literate / people
        if abs(previous - targets[tag]["previous"]) > 0.0005:
            raise ValueError(f"{tag}: base literacy {previous:.4f} is not the frozen {targets[tag]['previous']}")
        value = max(0.02, targets[tag]["target"] - boost(schools[tag]["education"], schools[tag]["schools"]))
        inputs[tag] = {**schools[tag], "target": targets[tag]["target"], "input": round(value, 4),
                       "factor": value / previous}
    for state, spec in world["states"].items():
        for tag, share in spec["population"]["by_owner"].items():
            old = base["states"][state]["population"]["by_owner"][tag]
            if old["total"] != share["total"]:
                raise ValueError(f"{state}/{tag}: population differs from the frozen base")
            share["literacy"] = round(max(BOUNDS[0], min(BOUNDS[1], old["literacy"] * inputs[tag]["factor"])), 3)
    return inputs


def sanitize(world: dict, m1b: dict, report: dict) -> list[str]:
    data = mechanics.catalog()
    buildings = pdx.parse_file(ROOT / "common/history/buildings/tgc_buildings.txt").get_node("BUILDINGS")
    fixed = []
    for state_block in buildings.items:
        state = state_block.key[2:]
        for owner_block in state_block.value.items:
            tag = owner_block.key.split(":")[1]
            if tag not in m1b:
                continue
            techs = set(report["countries"][tag]["technologies"]) | set(m1b[tag]["add_technologies"])
            laws = set(report["countries"][tag]["laws"]) | set(m1b[tag]["new_laws"])
            usable = lambda m: not set(data["production_methods"][m]["unlocking_technologies"]) - techs \
                and not set(data["production_methods"][m]["disallowing_laws"]) & laws
            records = [r for r in owner_block.value.getall("create_building") if isinstance(r, pdx.Node)]
            names = {str(r.get_str("building")) for r in records}
            explicit = ((world["states"][state].get("industry") or {}).get("by_owner") or {}).get(tag, {}).get("buildings", {})
            for name in sorted(names - set(explicit)):
                same = [r for r in records if str(r.get_str("building")) == name]
                pms = [str(pm) for pm in same[0].get_list("activate_production_methods")]
                if all(usable(pm) for pm in pms if pm in data["production_methods"]):
                    continue
                chosen = []
                for group in data["buildings"][name]["production_method_groups"]:
                    methods = data["production_method_groups"][group]["production_methods"]
                    ok = [m for m in pms if m in methods and usable(m)] or [m for m in methods if usable(m)]
                    if ok:
                        chosen.append(str(ok[0]))
                kind = data["buildings"][name].get("ownership_type")
                item = {"level": sum(dev.level(r) for r in same), "production_methods": chosen,
                        "ownership": "self" if kind == "self" else "government"}
                industry = world["states"][state].setdefault("industry", {})
                part = industry.setdefault("by_owner", {}).setdefault(tag, {"mode": "merge", "buildings": {}})
                part["buildings"][name] = item
                fixed.append(f"{state}/{tag}/{name}: {pms} -> {chosen}")
    return fixed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/mechanics/m1b2-source.yml")
    parser.add_argument("--out", default="build/mechanics/m1b-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    targets = yaml.safe_load((HERE / "targets.yml").read_text())["countries"]
    m1 = yaml.safe_load((HERE.parent / "mechanics_m1_institutions/plan.yml").read_text())["countries"]
    m1b = yaml.safe_load((HERE / "plan.yml").read_text())["countries"]
    if set(m1) & set(m1b):
        raise ValueError(f"countries in both plans: {sorted(set(m1) & set(m1b))}")
    report = json.loads((ROOT / "build/mechanics/m1b-source-report.json").read_text())
    base = yaml.safe_load((ROOT / "build/mechanics/m1b-source.yml").read_text())
    inputs = scale_literacy(world, base, targets, education(targets, m1, m1b, report))
    fixed = sanitize(world, m1b, report)
    for tag, row in m1.items():
        entry = world["countries"][tag]
        if "technology" not in entry:
            raise ValueError(f"{tag}: M1 fields missing; M1b replaces an activated M1")
        tech = {"mode": "merge", "tier": row["tier"]}
        if row["add_technologies"]:
            tech["add"] = row["add_technologies"]
        entry["technology"] = tech
        entry["laws"] = {"values": row["laws"]}
        entry.pop("institutions", None)
        if row["institutions"]:
            entry["institutions"] = row["institutions"]
    for tag, row in m1b.items():
        entry = world["countries"].setdefault(tag, {})
        base_entry = base["countries"].get(tag, {})
        if any(key in base_entry for key in ("technology", "institutions")):
            raise ValueError(f"{tag}: pre-M1b technology/institutions would be replaced")
        # An activated M1b is replaced; the laws come from plan.py (pre-M1b laws + M1b laws).
        for key in ("technology", "laws", "institutions"):
            entry.pop(key, None)
        if row["add_technologies"]:
            entry["technology"] = {"mode": "merge", "add": row["add_technologies"]}
        entry["laws"] = {"values": row["laws"]}
        entry["institutions"] = row["institutions"]
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, temel ekonomi ve İslam okuryazarlığı"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    (ROOT / "build/mechanics/m1b-audit.json").write_text(json.dumps({"method_fixes": fixed, "inputs": inputs},
                                                                   ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {output.relative_to(ROOT)}: literacy for {len(targets)} countries, M1 {len(m1)}, "
          f"vanilla-history {len(m1b)}, method fixes {len(fixed)}")


if __name__ == "__main__":
    main()
