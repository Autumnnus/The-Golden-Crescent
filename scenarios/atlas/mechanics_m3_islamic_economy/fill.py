"""M3-lite: a denser consumer economy for the Islamic world (standard of living after M1b).

Higher literacy raises the expected standard of living, and after M2 the Islamic core had only
7-10 building levels per million people (VEL 41, Sweden 28). This planner writes absolute
Atlas building levels for Islamic state shares:

1. Rum takes the reviewed Faz 1B.2 industry plan (25 state shares, ~1,231 levels). Methods the
   current Rum cannot use are swapped for the first usable method of the same group; shared
   arable land and resource caps of split states are re-checked with today's other owners.
2. Every other non-decentralized Islamic share is filled up to a density target
   (core 32, recognized 20, unrecognized 16 levels per million), capped so estimated jobs stay
   under 27% of the share's people. The mix is consumer-first: staple farms, ranches, fishing,
   logging, textiles, furniture, food industry, glass and a cash crop (tea/coffee/tobacco/cotton;
   no distilleries for Muslim consumers). Existing levels and methods are kept.
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
from vic3 import mechanics, pdx  # noqa: E402
from vic3.worldplan import group_value  # noqa: E402

DENSITY = {"islam_core": 32.0, "recognized": 20.0, "unrecognized": 16.0}
JOB_SHARE = 0.27
MIN_SHARE = 50_000
GRAINS = ["building_wheat_farm", "building_rice_farm", "building_maize_farm", "building_millet_farm", "building_rye_farm"]
CASH = ["building_tea_plantation", "building_coffee_plantation", "building_tobacco_plantation", "building_cotton_plantation"]
MIX = [  # (building or group, share of the missing levels)
    ("grain", 0.28), ("building_livestock_ranch", 0.12), ("building_fishing_wharf", 0.08),
    ("building_logging_camp", 0.10), ("building_textile_mill", 0.12), ("building_furniture_manufactory", 0.10),
    ("building_food_industry", 0.08), ("building_glassworks", 0.04), ("cash", 0.08),
]
LEFTOVER = ["grain", "building_livestock_ranch", "building_textile_mill", "building_furniture_manufactory",
            "building_food_industry", "building_logging_camp", "building_fishing_wharf"]


class Economy:
    def __init__(self, world, report, index, targets, m1, rum_add):
        self.world, self.report, self.index, self.data = world, report, index, mechanics.catalog()
        self.targets, self.m1 = targets, m1
        self.techs = {}
        for tag, country in report["countries"].items():
            extra = set(m1.get(tag, {}).get("add_technologies", [])) | (set(rum_add) if tag == "RUM" else set())
            self.techs[tag] = set(mechanics.prerequisites(set(country["technologies"]) | extra, self.data))
        self.laws = {tag: set(m1[tag]["laws"]) if tag in m1 else set(c["laws"]) for tag, c in report["countries"].items()}

    def usable(self, tag, pm):
        rule = self.data["production_methods"].get(pm)
        return bool(rule) and "slave" not in pm and not set(rule["unlocking_technologies"]) - self.techs[tag] \
            and not set(rule["disallowing_laws"]) & self.laws[tag]

    def methods(self, tag, name, wanted=()):
        """Keep wanted methods that the owner can use; fill every group with its first usable method."""
        chosen = []
        for group in self.data["buildings"][name]["production_method_groups"]:
            options = self.data["production_method_groups"][group]["production_methods"]
            # Power-bloc principle methods only work with the principle; prefer the no-effect method.
            options = sorted(options, key=lambda m: "principle" in m)
            keep = [m for m in wanted if m in options and self.usable(tag, m)] or [m for m in options if self.usable(tag, m)]
            if not keep:
                return None
            chosen.append(str(keep[0]))
        return chosen

    def buildable(self, tag, name):
        return name in self.data["buildings"] and not set(self.data["buildings"][name]["unlocking_technologies"]) - self.techs[tag]

    def jobs(self, pms):
        total = 0.0
        for pm in pms:
            bm = pdx.parse(self.data["production_methods"][pm]["script"]).get_node("building_modifiers")
            scaled = bm.get_node("level_scaled") if bm else None
            if scaled:
                total += sum(float(it.value) for it in scaled.items if (it.key or "").startswith("building_employment_")
                             and (it.key or "").endswith("_add") and isinstance(it.value, str))
        return total

    def kind(self, name):
        group = self.data["buildings"][name].get("building_group")
        if group_value(group, "land_usage", self.data) == "rural":
            return "rural"
        if group_value(group, "capped_by_resources", self.data) == "yes":
            return "capped"
        return "urban"


class StateBudget:
    """Shared arable land and resource caps of one state, with today's levels of every owner."""

    def __init__(self, eco: Economy, state: str):
        self.eco, self.raw = eco, eco.index["states"][state]
        self.levels = defaultdict(lambda: defaultdict(int))  # tag -> building -> level
        for tag, orep in eco.report["states"][state]["owners"].items():
            for b in orep["buildings"]:
                self.levels[tag][b["type"]] += b["level"]

    def rural_used(self):
        return sum(n for owner in self.levels.values() for b, n in owner.items()
                   if b in self.eco.data["buildings"] and self.eco.kind(b) == "rural")

    def cap(self, name):
        caps = self.raw.get("capped_resources", {})
        if name in caps:
            return caps[name]
        return sum(r.get("discovered_amount") or 0 for r in self.raw.get("resources", []) if r.get("type") == name)

    def room(self, tag, name):
        """Largest absolute level `tag` may hold for `name` in this state."""
        kind = self.eco.kind(name)
        definition = self.eco.data["buildings"][name]
        if (definition.get("naval") == "yes" or definition.get("port") == "yes" or name == "building_fishing_wharf") \
                and self.raw.get("naval_exit_id") is None:
            return 0
        own = self.levels[tag][name]
        if kind == "rural":
            if name not in self.raw.get("arable_resources", []):
                return 0
            return own + max(0, (self.raw.get("arable_land") or 0) - self.rural_used())
        if kind == "capped":
            others = sum(owner[name] for t, owner in self.levels.items() if t != tag)
            return max(0, self.cap(name) - others)
        return 10 ** 6

    def set(self, tag, name, level):
        self.levels[tag][name] = level


def main() -> None:
    world = yaml.safe_load((ROOT / "build/mechanics/m3-source.yml").read_text())
    report = json.loads((ROOT / "build/mechanics/m3-source-report.json").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    targets = yaml.safe_load((ROOT / "scenarios/atlas/mechanics_m1b_literacy/targets.yml").read_text())["countries"]
    m1 = yaml.safe_load((ROOT / "scenarios/atlas/mechanics_m1_institutions/plan.yml").read_text())["countries"]
    rum_plan = json.loads((ROOT / "scenarios/atlas/phase01b2_rum_economy/economy-plan.json").read_text())
    eco = Economy(world, report, index, targets, m1, rum_plan["technology_additions"])
    plan, audit = defaultdict(dict), {"rum": {"swaps": [], "clipped": [], "levels": 0}, "fill": {}, "added": 0}

    # 1. Rum: Faz 1B.2 plan.
    for state, spec in sorted(rum_plan["states"].items()):
        budget = StateBudget(eco, state)
        items = {}
        for name, item in spec["buildings"].items():
            level = item if isinstance(item, int) else item["level"]
            if level == 0:
                items[name] = 0
                budget.set("RUM", name, 0)
                continue
            if not eco.buildable("RUM", name):
                raise ValueError(f"{state}: RUM cannot build {name}")
            wanted = [] if isinstance(item, int) else item.get("production_methods", [])
            pms = eco.methods("RUM", name, wanted)
            if pms is None:
                raise ValueError(f"{state}: no usable methods for {name}")
            if wanted and set(pms) != set(wanted):
                audit["rum"]["swaps"].append(f"{state}/{name}: {sorted(set(wanted) - set(pms))} -> {sorted(set(pms) - set(wanted))}")
            room = budget.room("RUM", name)
            if level > room:
                audit["rum"]["clipped"].append(f"{state}/{name}: {level} -> {room}")
                level = room
            budget.set("RUM", name, level)
            entry = {"level": level, "production_methods": pms}
            if isinstance(item, dict) and item.get("ownership"):
                entry["ownership"] = item["ownership"]
            items[name] = entry
            audit["rum"]["levels"] += level
        plan[state]["RUM"] = items

    # 2. Other Islamic shares: consumer-first density fill.
    for state, srep in sorted(report["states"].items()):
        budget = StateBudget(eco, state)
        for tag, items in plan.get(state, {}).items():
            for name, item in items.items():
                budget.set(tag, name, item if isinstance(item, int) else item["level"])
        explicit_all = ((world["states"][state].get("industry") or {}).get("by_owner") or {})
        for tag, orep in sorted(srep["owners"].items(), key=lambda kv: -kv[1]["population"]):
            goal = targets[tag]
            if tag == "RUM" or not goal["band"].startswith("islam") or goal["type"] == "decentralized" \
                    or orep["population"] < MIN_SHARE:
                continue
            density = DENSITY["islam_core" if goal["band"] == "islam_core" else goal["type"]]
            existing = defaultdict(int)
            first_pms = {}
            for b in orep["buildings"]:
                existing[b["type"]] += b["level"]
                first_pms.setdefault(b["type"], [str(pm) for pm in b["production_methods"]])
            explicit = explicit_all.get(tag, {}).get("buildings", {})
            need = math.floor(orep["population"] / 1e6 * density) - sum(existing.values())
            job_room = JOB_SHARE * orep["population"] - orep["estimated_jobs"]
            if need <= 0 or job_room <= 0:
                continue
            add, chosen = defaultdict(int), {}

            def put(name, n):
                nonlocal need, job_room
                if n <= 0 or need <= 0 or not eco.buildable(tag, name) or explicit.get(name) == 0:
                    return 0
                if name not in chosen:
                    pms = eco.methods(tag, name, first_pms.get(name, []))
                    if pms is None:
                        return 0
                    chosen[name] = pms
                per_level = max(1.0, eco.jobs(chosen[name]))
                n = min(n, need, int(job_room // per_level),
                        budget.room(tag, name) - budget.levels[tag][name])
                if n <= 0:
                    return 0
                add[name] += n
                budget.set(tag, name, budget.levels[tag][name] + n)
                need -= n
                job_room -= n * per_level
                return n

            def put_group(key, n):
                names = [g for g in GRAINS if g in budget.raw.get("arable_resources", [])] if key == "grain" else \
                    [c for c in CASH if c in budget.raw.get("arable_resources", [])] if key == "cash" else [key]
                done = 0
                for name in names:
                    done += put(name, n - done)
                    if done >= n:
                        break
                return done

            admin = max(1, round(orep["population"] / (1e6 if goal["band"] == "islam_core" else 2e6)))
            put("building_government_administration", admin - existing.get("building_government_administration", 0))
            total = need
            for key, share in MIX:
                put_group(key, max(1, round(total * share)))
            for key in LEFTOVER:
                put_group(key, need)
            if add:
                items = {}
                for name, n in sorted(add.items()):
                    previous = explicit.get(name)
                    base = existing.get(name, 0)
                    item = {"level": base + n, "production_methods": chosen[name]}
                    if isinstance(previous, dict) and previous.get("ownership"):
                        item["ownership"] = previous["ownership"]
                    items[name] = item
                plan[state][tag] = items
                audit["fill"][f"{state}/{tag}"] = {"population": orep["population"], "had": sum(existing.values()),
                                                  "added": dict(add)}
                audit["added"] += sum(add.values())
    (HERE / "fill-plan.yml").write_text(
        "# Generated by fill.py from the M3 source world and report; review, do not hand-edit.\n" +
        yaml.safe_dump({"version": 1, "rum_technology_additions": rum_plan["technology_additions"],
                        "states": {s: dict(v) for s, v in sorted(plan.items())}},
                       allow_unicode=True, sort_keys=True, width=110))
    (ROOT / "build/mechanics/m3-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n")
    print(f"Rum 1B.2 levels {audit['rum']['levels']} (swaps {len(audit['rum']['swaps'])}, clipped "
          f"{len(audit['rum']['clipped'])}); fill shares {len(audit['fill'])}, added {audit['added']}")


if __name__ == "__main__":
    main()
