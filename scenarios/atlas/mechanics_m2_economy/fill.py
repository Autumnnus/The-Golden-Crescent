"""M2b: add a rule-based basic economy to under-built state shares after the M2a restoration.

For every non-decentralized state share whose building density is below its tier target, the
missing levels are allocated in this order: government administration, staple farms (the
state's allowed arable crops, preferring its main grain), livestock, logging and fishing where
the state has the resource, then basic consumer industry (textiles, furniture, food) where the
owner's technologies allow it. Shared arable land and resource caps of split states are
respected. Levels are absolute Atlas values (existing level + added level).
"""

from __future__ import annotations

import json
import math
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
from vic3 import mechanics  # noqa: E402
from vic3.worldplan import group_value  # noqa: E402

# Building levels per million people targeted for a share, by technology tier.
DENSITY = {1: 7.0, 2: 6.0, 3: 5.0, 4: 4.5, 5: 4.0, 6: 3.0, 7: 0.0}
GRAINS = ["building_rice_farm", "building_wheat_farm", "building_maize_farm", "building_rye_farm",
          "building_millet_farm"]
INDUSTRY = ["building_food_industry", "building_textile_mill", "building_furniture_manufactory"]


def main() -> None:
    report = json.loads((ROOT / "build/scenarios/m2-candidate/scenario-report.json").read_text())
    world = yaml.safe_load((ROOT / "build/mechanics/m2-candidate.yml").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    data = mechanics.catalog()
    m1 = yaml.safe_load((ROOT / "scenarios/atlas/mechanics_m1_institutions/plan.yml").read_text())["countries"]
    tier_techs = json.loads((ROOT / "scenarios/atlas/mechanics_m1_institutions/tier-techs.json").read_text())
    techs = {tag: set(report["countries"][tag]["technologies"]) for tag in report["countries"]}

    def ctype(tag):
        return world["countries"].get(tag, {}).get("country_type") or index["countries"].get(tag, {}).get("country_type")

    def tier(tag):
        if tag in m1:
            return m1[tag]["tier"]
        have = techs[tag]
        return min((int(t) for t, ts in tier_techs.items() if set(ts) <= have), default=7)

    def buildable(tag, name):
        return name in data["buildings"] and not (set(data["buildings"][name]["unlocking_technologies"]) - techs[tag])

    plan, audit = defaultdict(dict), {"shares": {}, "added": 0}
    for state, srep in report["states"].items():
        raw = index["states"][state]
        rural_used = sum(b["level"] for o in srep["owners"].values() for b in o["buildings"]
                         if group_value(data["buildings"].get(b["type"], {}).get("building_group"), "land_usage", data) == "rural")
        arable_left = (raw.get("arable_land") or 0) - rural_used
        used = defaultdict(int)
        for o in srep["owners"].values():
            for b in o["buildings"]:
                used[b["type"]] += b["level"]
        for tag, orep in sorted(srep["owners"].items(), key=lambda kv: -kv[1]["population"]):
            if ctype(tag) == "decentralized" or not orep["population"]:
                continue
            existing = {b["type"]: b["level"] for b in orep["buildings"]}
            explicit = set(((world["states"][state].get("industry") or {}).get("by_owner") or {}).get(tag, {}).get("buildings", {}))
            have = sum(existing.values())
            want = math.floor(orep["population"] / 1e6 * DENSITY[tier(tag)])
            need = want - have
            if need <= 0:
                continue
            add = defaultdict(int)

            def cap_left(name):
                caps = raw.get("capped_resources", {})
                if name in caps:
                    return caps[name] - used[name]
                deposits = [r.get("discovered_amount") or 0 for r in raw.get("resources", []) if r.get("type") == name]
                return sum(deposits) - used[name] if deposits else 0

            def put(name, n):
                nonlocal need, arable_left
                n = min(n, need)
                if n <= 0 or not buildable(tag, name) or name in explicit:
                    return 0
                rural = group_value(data["buildings"][name].get("building_group"), "land_usage", data) == "rural"
                if rural:
                    if name not in raw.get("arable_resources", []):
                        return 0
                    n = min(n, arable_left)
                elif group_value(data["buildings"][name].get("building_group"), "capped_by_resources", data) == "yes":
                    n = min(n, cap_left(name))
                if n <= 0:
                    return 0
                add[name] += n
                used[name] += n
                need -= n
                if rural:
                    arable_left -= n
                return n

            put("building_government_administration", max(1, round(orep["population"] / 2e6)) - existing.get(
                "building_government_administration", 0))
            grains = [g for g in GRAINS if g in raw.get("arable_resources", [])]
            farm_share = max(1, round(need * 0.45))
            for grain in grains:
                farm_share -= put(grain, farm_share)
                if farm_share <= 0:
                    break
            put("building_livestock_ranch", max(1, round(need * 0.25)))
            put("building_logging_camp", max(1, round(need * 0.2)))
            if raw.get("naval_exit_id") is not None:
                put("building_fishing_wharf", max(1, round(need * 0.2)))
            if tier(tag) <= 5:
                for name in INDUSTRY:
                    put(name, max(1, round(need / 3)))
            for grain in grains:  # any remaining need goes back to farming
                put(grain, need)
            if add:
                plan[state][tag] = {name: existing.get(name, 0) + n for name, n in sorted(add.items())}
                audit["shares"][f"{state}/{tag}"] = {"population": orep["population"], "had": have, "target": want,
                                                    "added": dict(add)}
                audit["added"] += sum(add.values())
    (HERE / "fill-plan.yml").write_text(
        "# Generated by fill.py from the M2a candidate report; review, do not hand-edit.\n" +
        yaml.safe_dump({"version": 1, "states": dict(plan)}, allow_unicode=True, sort_keys=True, width=110))
    (ROOT / "build/mechanics/m2b-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n")
    print(f"fill shares {len(audit['shares'])}, added levels {audit['added']}")


if __name__ == "__main__":
    main()
