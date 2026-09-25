"""M2a: restore the vanilla building base of states whose buildings the political phase dropped.

The political map dropped the vanilla buildings of 314 states because their new owners had no
technologies. After M1 every non-decentralized owner has a technology tier, so the vanilla
building base (already inside resource and arable caps) is restored and adapted:
- levels are scaled down, never up, by current / vanilla state population;
- production methods the owner cannot use are swapped for the first usable method of the same
  group; a building whose own technology or every method is unavailable is removed;
- ownership records pointing at other countries or companies are made local.
The result is written as explicit `industry` fields into plan.yml; nothing is activated here.
"""

from __future__ import annotations

import json
import os
import re
import sys
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
from vic3 import development as dev, history, mechanics, scenario  # noqa: E402
from vic3 import index as idx  # noqa: E402
from vic3.build import Resolved  # noqa: E402
from vic3.worldplan import group_value  # noqa: E402
from vic3.world import load_world  # noqa: E402

SOURCE = ROOT / "build/mechanics/m2-source.yml"
MIN_SCALE = 0.25


def foreign_ownership(node, tag: str) -> bool:
    text = " ".join(str(it.value) for it in node.items if it.key == "add_ownership")
    owners = set(re.findall(r"c:(\w+)", text))
    return "company" in text or bool(owners - {tag})


def main() -> None:
    source = yaml.safe_load(SOURCE.read_text())
    dropped = sorted(state for state, spec in source["states"].items() if spec.get("buildings") == "drop")
    probe = json.loads(json.dumps(source))
    for state in dropped:
        probe["states"][state]["buildings"] = "inherit"
    probe_path = ROOT / "build/mechanics/_m2-probe.yml"
    probe_path.write_text(yaml.safe_dump(probe, allow_unicode=True, sort_keys=False, width=120))
    index = idx.load()
    world = scenario.overlay(load_world(), scenario.load(str(probe_path)))
    res = Resolved(world, index)
    data = mechanics.catalog()
    _, _, techs, laws, _ = history.compile_countries(res, data)
    vanilla_pop = {state: sum(int(x) for x in re.findall(r"size = (\d+)", json.dumps(index["pops"].get(state, {}))))
                   for state in dropped}
    # Second pass input: per-state multipliers from a built candidate whose jobs exceeded 28% of pops.
    jobs_path = ROOT / "build/mechanics/m2a-jobs.json"
    jobs_fix = json.loads(jobs_path.read_text()) if jobs_path.exists() else {}
    plan, audit = {}, {"states": {}, "removed": {}, "pm_swaps": 0, "ownership_fixes": 0}
    for state in dropped:
        current = sum(p["size"] for rows in res.state_pops.get(state, {}).values() for p in rows)
        scale = 1.0 if not vanilla_pop[state] else max(MIN_SCALE, min(1.0, current / vanilla_pop[state]))
        scale = round(scale * jobs_fix.get(state, 1.0), 2)
        by_owner = {}
        before = after = 0
        for tag, script in sorted(res.state_buildings.get(state, {}).items()):
            fixes = {}
            for node in dev.building_records(script):
                name = str(node.get_str("building"))
                level = dev.level(node)
                scaled = round(level * scale)
                before += level
                definition = data["buildings"][name]
                raw = index["states"][state]
                group = definition.get("building_group")
                invalid_site = (
                    ((definition.get("naval") == "yes" or definition.get("port") == "yes") and raw.get("naval_exit_id") is None)
                    or (group_value(group, "land_usage", data) == "rural" and name not in raw.get("arable_resources", []))
                    or (group_value(group, "capped_by_resources", data) == "yes" and name not in raw.get("capped_resources", {})
                        and not any(r.get("type") == name for r in raw.get("resources", []))))
                if set(definition["unlocking_technologies"]) - techs[tag] or scaled == 0 or invalid_site:
                    fixes[name] = 0
                    audit["removed"][f"{state}/{tag}/{name}"] = level
                    continue
                pms, changed = [], False
                for pm in map(str, node.get_list("activate_production_methods")):
                    rule = data["production_methods"].get(pm)
                    if rule and not (set(rule["unlocking_technologies"]) - techs[tag]) and \
                            not (set(rule["disallowing_laws"]) & set(laws[tag].values())):
                        pms.append(pm)
                        continue
                    group = next(g for g in definition["production_method_groups"]
                                 if pm in data["production_method_groups"][g]["production_methods"])
                    usable = [m for m in data["production_method_groups"][group]["production_methods"]
                              if not (set(data["production_methods"][m]["unlocking_technologies"]) - techs[tag])
                              and not (set(data["production_methods"][m]["disallowing_laws"]) & set(laws[tag].values()))]
                    if not usable:
                        pms = None
                        break
                    pms.append(str(usable[0]))
                    changed = True
                    audit["pm_swaps"] += 1
                if pms is not None:
                    # Vanilla records may omit groups; fill them with a usable method so Atlas does
                    # not default to the group's first (for plantations: slave) method.
                    for group in definition["production_method_groups"]:
                        methods = data["production_method_groups"][group]["production_methods"]
                        if methods and not set(methods) & set(pms):
                            usable = [m for m in methods
                                      if not (set(data["production_methods"][m]["unlocking_technologies"]) - techs[tag])
                                      and not (set(data["production_methods"][m]["disallowing_laws"]) & set(laws[tag].values()))]
                            if not usable:
                                pms = None
                                break
                            pms.append(str(usable[0]))
                            changed = True
                if pms is None:
                    fixes[name] = 0
                    audit["removed"][f"{state}/{tag}/{name}"] = level
                    continue
                foreign = foreign_ownership(node, tag)
                if changed or foreign:
                    item = {"level": scaled, "production_methods": pms}
                    if foreign:
                        item["ownership"] = "government" if definition.get("ownership_type") != "self" else "self"
                        audit["ownership_fixes"] += 1
                    fixes[name] = item
                after += scaled
            if fixes:
                by_owner[tag] = {"mode": "merge", "buildings": fixes}
        entry = {"buildings": "inherit", "industry": {"scale": scale}}
        if by_owner:
            entry["industry"]["by_owner"] = by_owner
        plan[state] = entry
        audit["states"][state] = {"vanilla_population": vanilla_pop[state], "population": current,
                                  "scale": scale, "vanilla_levels": before, "planned_levels": after}
    (HERE / "restore-plan.yml").write_text(
        "# Generated by restore.py; review, do not hand-edit.\n" +
        yaml.safe_dump({"version": 1, "states": plan}, allow_unicode=True, sort_keys=True, width=110))
    (ROOT / "build/mechanics/m2a-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n")
    probe_path.unlink()
    print(f"states {len(plan)}; vanilla levels {sum(s['vanilla_levels'] for s in audit['states'].values())} -> "
          f"planned {sum(s['planned_levels'] for s in audit['states'].values())}; removed {len(audit['removed'])}; "
          f"pm swaps {audit['pm_swaps']}; ownership fixes {audit['ownership_fixes']}")


if __name__ == "__main__":
    main()
