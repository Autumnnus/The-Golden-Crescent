"""M4: turn targets.yml into per-country armies, navies and commanders (plan.yml, generated).

Every organized landed country (not decentralized, not excluded) gets:
- battalions = m * population_millions ** exponent (m by M1b band or country), times the colonial and
  subject factors, scaled so the world total meets `total_battalions` (fixed armies are kept as is);
- army formations (one per `armies_per_battalions`, 1..5) in the strategic regions where it holds
  most people, recruited from its most populous state there; infantry/cavalry/artillery by share,
  each with the best unit type its technologies allow;
- a navy of the planned size (or a small default squadron) at its most populous coastal states;
- one general per army and one admiral per fleet, less the commanders its vanilla history already has.
"""

from __future__ import annotations

import json
import math
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
os.chdir(ROOT)
from vic3 import mechanics  # noqa: E402
from vic3.paths import VANILLA  # noqa: E402

KEY_RE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$')
INFANTRY = [("combat_unit_type_skirmish_infantry", "general_staff"), ("combat_unit_type_line_infantry", "line_infantry"),
            ("combat_unit_type_irregular_infantry", None)]
CAVALRY = [("combat_unit_type_hussars", "standing_army"), ("combat_unit_type_lancers", "napoleonic_warfare"),
           ("combat_unit_type_dragoons", "line_infantry")]
ARTILLERY = [("combat_unit_type_mobile_artillery", "napoleonic_warfare"), ("combat_unit_type_cannon_artillery", "artillery")]


def loc(language: str) -> dict:
    """Country/region display text: vanilla, then the mod's generated names, then its replace overrides."""
    out = {}
    paths = list((VANILLA / "localization" / language).rglob("*.yml")) + \
        [ROOT / f"localization/{language}/tgc_generated_countries_l_{language}.yml",
         ROOT / f"localization/replace/{language}/tgc_country_name_overrides_l_{language}.yml"]
    for path in paths:
        if path.exists():
            for line in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
                m = KEY_RE.match(line)
                if m:
                    out[m.group(1)] = m.group(2)
    return out


def apportion(total: int, weights: list[float]) -> list[int]:
    raw = [total * w / sum(weights) for w in weights]
    out = [int(x) for x in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - out[i], reverse=True)[:total - sum(out)]:
        out[i] += 1
    return out


def pick(options, techs):
    return next((unit for unit, tech in options if tech is None or tech in techs), None)


def vanilla_commanders() -> dict:
    """Generals/admirals each tag's vanilla character history creates (templates flagged is_general/is_admiral)."""
    flagged = {}
    for path in (VANILLA / "common/character_templates").glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        for name, body in re.findall(r"^(\w[\w\-]*) = \{(.*?)^\}", text, re.S | re.M):
            if re.search(r"\b(is_general|is_admiral)\s*=\s*yes|\brole\s*=\s*(general|admiral)\b", body):
                flagged[name] = "admiral" if re.search(r"is_admiral\s*=\s*yes|role\s*=\s*admiral", body) else "general"
    counts = defaultdict(lambda: {"general": 0, "admiral": 0})
    for path in (VANILLA / "common/history/characters").glob("*.txt"):
        override = ROOT / "common/history/characters" / path.name
        text = (override if override.exists() else path).read_text(encoding="utf-8-sig", errors="ignore")
        for tag, body in re.findall(r"c:(\w+)\s*\??=\s*\{(.*?)\n\t\}", text, re.S):
            for template in re.findall(r"template\s*=\s*([\w\-]+)", body):
                if template in flagged:
                    counts[tag][flagged[template]] += 1
    return counts


def main() -> None:
    targets = yaml.safe_load((HERE / "targets.yml").read_text())
    world = yaml.safe_load((ROOT / "world/scenario.yml").read_text())
    report = json.loads((ROOT / "build/world-political/active-political-report.json").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    bands = yaml.safe_load((HERE.parent / "mechanics_m1b_literacy/targets.yml").read_text())["countries"]
    regions = json.loads((ROOT / "build/m4-strategic-regions.json").read_text())["entries"]
    data = mechanics.catalog()
    region_of = {s: r for r, v in regions.items() for s in v["states"] if not index["states"].get(s, {}).get("is_sea")}
    kind = lambda t: world["countries"].get(t, {}).get("country_type") or index["countries"].get(t, {}).get("country_type")
    tr, en = loc("turkish"), loc("english")

    owned = defaultdict(dict)   # tag -> state -> people
    ports = defaultdict(set)    # tag -> states where it has a port
    for state, row in report["states"].items():
        for tag, share in row["owners"].items():
            owned[tag][state] = share["population"]
            if any(b["type"] == "building_port" for b in share["buildings"]):
                ports[tag].add(state)
    coastal = lambda s: index["states"][s].get("naval_exit_id") is not None
    countries = [t for t in report["countries"] if kind(t) != "decentralized" and t not in targets["excluded"]]

    # battalions
    fixed = {}
    for tag, package in targets["fixed_armies"].items():
        source = json.loads((HERE.parent / package / "scenario.json").read_text())["countries"][tag]["military"]
        fixed[tag] = [f for f in source["formations"] if f["type"] == "army"]
    band = lambda t: (bands.get(t) or {}).get("band") or targets["default_band"].get(t, "rest")
    raw = {}
    for tag in countries:
        if tag in fixed:
            continue
        m = targets["country_m"].get(tag, targets["bands"][band(tag)])
        value = m * (report["countries"][tag]["population"] / 1e6) ** targets["exponent"]
        if kind(tag) == "colonial":
            value *= targets["colonial_factor"]
        elif report["countries"][tag].get("overlord"):
            value *= targets["subject_factor"]
        raw[tag] = value
    fixed_total = sum(u["count"] for forms in fixed.values() for f in forms for u in f["units"])
    scale = (targets["total_battalions"] - fixed_total) / sum(raw.values())
    battalions = {t: max(targets["min_battalions"], round(v * scale)) for t, v in raw.items()}

    existing = vanilla_commanders()
    plan, names = {}, {}
    for tag in sorted(countries):
        techs = set(mechanics.prerequisites(set(report["countries"][tag]["technologies"]), data))
        adj_tr = world["countries"].get(tag, {}).get("adjective_tr") or tr.get(f"{tag}_ADJ") or tag
        adj_en = world["countries"].get(tag, {}).get("adjective") or en.get(f"{tag}_ADJ") or tag
        by_region = defaultdict(dict)
        for state, people in owned[tag].items():
            if state in region_of:
                by_region[region_of[state]][state] = people
        ranked = sorted(by_region, key=lambda r: -sum(by_region[r].values()))
        formations = []

        used_regions = defaultdict(int)

        def name(key, region, kind_word_tr, kind_word_en, state):
            used_regions[(region, kind_word_en)] += 1
            where_tr, where_en = tr.get(region, region), en.get(region, region)
            if used_regions[(region, kind_word_en)] > 1:  # a second formation in the region: name it by its state
                where_tr, where_en = tr.get(state, state), en.get(state, state)
            names[key] = {"tr": f"{adj_tr} {where_tr} {kind_word_tr}", "en": f"{adj_en} {where_en} {kind_word_en}"}
            return key

        if tag in fixed:
            for k, form in enumerate(fixed[tag], 1):
                key = f"ve_m4_{tag.lower()}_army_{k}"
                names[key] = {"tr": form["name"].replace("Donanmasi", "Donanması"), "en": form["name"]}
                formations.append({**form, "name": key})
        else:
            total = battalions[tag]
            # formation slots: the largest state of each region (by the region's people), then the
            # other large states; strategic regions are wide, so one region may hold two armies
            slots = [(r, max(by_region[r], key=by_region[r].get)) for r in ranked]
            slots += sorted(((r, s) for r in ranked for s in by_region[r] if (r, s) not in slots),
                            key=lambda rs: -by_region[rs[0]][rs[1]])
            count = max(1, min(5, math.ceil(total / targets["armies_per_battalions"]), len(slots)))
            chosen = slots[:count]
            split = apportion(total, [math.sqrt(by_region[r][s]) for r, s in chosen])
            heavy = tag in targets["cavalry_heavy"]
            cav_share = targets["cavalry_share"]["heavy" if heavy else "normal"]
            art_share = targets["artillery_share"].get(band(tag), targets["artillery_share"]["default"])
            inf, cav, art = pick(INFANTRY, techs), pick(CAVALRY, techs), pick(ARTILLERY, techs)
            for k, ((region, state), size) in enumerate(zip(chosen, split), 1):
                if size <= 0:
                    continue
                n_cav = round(size * cav_share) if cav else 0
                n_art = round(size * art_share) if art and size >= 4 else 0
                units = [{"type": inf, "state": state, "count": size - n_cav - n_art}]
                units += [{"type": cav, "state": state, "count": n_cav}] if n_cav else []
                units += [{"type": art, "state": state, "count": n_art}] if n_art else []
                units = [u for u in units if u["count"] > 0]
                formations.append({"name": name(f"ve_m4_{tag.lower()}_army_{k}", region, "Ordusu", "Army", state),
                                   "type": "army", "hq_region": region, "units": units})
        # navy
        shores = sorted((s for s in owned[tag] if coastal(s) and s in region_of),
                        key=lambda s: (s not in ports[tag], -owned[tag][s]))
        if tag in targets["navies"]:
            ships = targets["navies"][tag]
        else:
            low, high, per = targets["navy_default"]["recognized" if kind(tag) in ("recognized", "colonial") else "other"]
            army = sum(u["count"] for f in formations for u in f["units"])
            ships = max(low, min(high, round(army / per)))
        fleets = []
        if shores and ships:
            homes = []
            for s in shores:  # distinct regions first, then a second port in the same region
                if region_of[s] not in {region_of[h] for h in homes}:
                    homes.append(s)
            homes += [s for s in shores if s not in homes]
            homes = homes[:2] if ships >= 24 else homes[:1]
            if tag == "RUM":  # 1B.3 fleets plus the western Mediterranean squadron at the Sicilian station
                source = json.loads((HERE.parent / "phase01b3_rum_military/scenario.json").read_text())["countries"]["RUM"]["military"]
                for k, form in enumerate((f for f in source["formations"] if f["type"] == "fleet"), 1):
                    key = f"ve_m4_rum_fleet_{k}"
                    names[key] = {"tr": form["name"].replace("Donanmasi", "Donanması"), "en": form["name"]}
                    fleets.append({**form, "name": key})
                rest = ships - sum(s["count"] for f in fleets for s in f["ships"])
                homes, parts = ["STATE_SICILY"], [rest]
            else:
                parts = apportion(ships, [0.6, 0.4][:len(homes)] if len(homes) == 2 else [1])
            line = "ship_type_ship_of_the_line" if "drydocks" in techs else None
            for k, (home, n) in enumerate(zip(homes, parts), len(fleets) + 1):
                n_line = round(n * targets["line_ship_share"]) if line and n >= 6 else 0
                rows = [{"type": "ship_type_frigate", "state": home, "count": n - n_line}]
                rows += [{"type": line, "state": home, "count": n_line}] if n_line else []
                fleets.append({"name": name(f"ve_m4_{tag.lower()}_fleet_{k}", region_of[home], "Donanması", "Fleet", home),
                               "type": "fleet", "hq_region": region_of[home], "ships": [r for r in rows if r["count"]]})
        formations += fleets
        # commanders: one per formation, fewer by the vanilla commanders the tag already has
        commanders = []
        for form in formations:
            size = sum(u["count"] for u in form.get("units", form.get("ships", [])))
            general = form["type"] == "army"
            rank = (4 if size >= 100 else 3 if size >= 60 else 2 if size >= 25 else 1) if general else \
                (3 if size >= 30 else 2 if size >= 12 else 1)
            commanders.append({"role": "general" if general else "admiral", "rank": rank, "hq": form["hq_region"]})
        for role in ("general", "admiral"):
            have = existing.get(tag, {}).get(role, 0)
            mine = sorted((c for c in commanders if c["role"] == role), key=lambda c: c["rank"])
            for c in mine[:have]:
                commanders.remove(c)
        plan[tag] = {"band": band(tag), "battalions": sum(u["count"] for f in formations if f["type"] == "army" for u in f["units"]),
                     "ships": sum(s["count"] for f in formations if f["type"] == "fleet" for s in f["ships"]),
                     "formations": formations, "commanders": commanders,
                     "vanilla_commanders": dict(existing.get(tag, {"general": 0, "admiral": 0}))}
    summary = {"countries": len(plan), "battalions": sum(p["battalions"] for p in plan.values()),
               "ships": sum(p["ships"] for p in plan.values()),
               "generals": sum(1 for p in plan.values() for c in p["commanders"] if c["role"] == "general"),
               "admirals": sum(1 for p in plan.values() for c in p["commanders"] if c["role"] == "admiral"),
               "scale": round(scale, 4)}
    (HERE / "plan.yml").write_text("# Generated by plan.py from targets.yml and the active world; review, do not hand-edit.\n" +
                                   yaml.safe_dump({"version": 1, "summary": summary, "names": names, "countries": plan},
                                                  allow_unicode=True, sort_keys=False, width=120))
    print(summary)
    top = sorted(plan.items(), key=lambda kv: -kv[1]["battalions"])[:30]
    print(" ".join(f"{t}:{p['battalions']}/{p['ships']}" for t, p in top))


if __name__ == "__main__":
    main()
