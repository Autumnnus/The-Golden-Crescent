"""B0: static balance measurement of an 1836 start, vanilla and the active mod side by side.

This is an estimate from source data, not an engine simulation. It reads the installed game (read-only)
and the active Atlas report, and writes build/balance/b0-<world>.json plus build/balance/b0-summary.md.

Model (see README.md for the vanilla sources of every rule):
- Buildings: PM `goods_input/output_*_add` per level at full employment, plus economy of scale
  (+1% throughput per level above 1, cap 20) for groups with `economy_of_scale = yes`.
- Pops: workforce = 25% of population. Building jobs (and 1,000 soldiers per battalion) employ it first;
  the rest are subsistence peasants who put 5% of their buy package on the market. Each worker's
  household consumes 2.5 packages (worker + dependents at half). Wealth = the country's starting wealth
  base (history/population effect; 10 when unset) plus the strata offsets of 00_starting_pop_wealth.txt.
  Package £ are split over a need's goods by weight x market supply (capped at max_supply_share).
- Military: land-unit `upkeep_modifier` goods per battalion; each battalion also employs 1,000 soldiers.
- Markets: a country plus all its (recursive) subjects, unless a grant_own_market pact exists.
- Bureaucracy: 100 + gov-admin output vs 10 per state + 4 per 100k people (x0.75 under the reducing laws)
  + 1 per government-owned level. Institutions are not costed.
- Infrastructure: 3 + population infra (tech rate per 100k, capped; coastal/capital bonuses) + trait adds,
  x (1 + trait/capital mults), + port/railway PM adds; usage = levels x building-group usage per level.
- Value added: output minus input at base prices (a GDP proxy without subsistence and services).
"""

from __future__ import annotations

import argparse
import collections as C
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLKIT = Path(os.environ.get("VIC3_TOOLS_HOME") or json.loads(
    (ROOT / ".vic3-tools.local.json").read_text())["toolkit"])
if sys.version_info < (3, 10):
    runtime = TOOLKIT / ".venv/bin/python"
    os.execv(str(runtime), [str(runtime), __file__, *sys.argv[1:]])
sys.path.insert(0, str(TOOLKIT / "src"))
from vic3 import pdx  # noqa: E402
import yaml  # noqa: E402
from vic3.paths import VANILLA  # noqa: E402

OUT = ROOT / "build/balance"
WORKFORCE = 0.25
HOUSEHOLD = 2.5          # consumption units per worker (worker + 3 dependents at 0.5)
PEASANT_MARKET = 0.05
EOS_CAP = 20
WEALTH_BASE = {"very_high": 13, "high": 12, "medium": 11, "low": 10}
STRATA = {"aristocrats": 15, "capitalists": 15, "academics": 7, "bureaucrats": 7, "clergymen": 7,
          "engineers": 7, "farmers": 7, "officers": 7, "shopkeepers": 7, "laborers": -2, "peasants": -3,
          "clerks": 0, "machinists": 0, "soldiers": 0}
REDUCE_BUR = {"law_hereditary_bureaucrats", "law_crownland_diets", "law_traditionalism",
              "law_consumption_based_taxation"}
MARKET_SUBJECTS = {"puppet", "dominion", "protectorate", "colony", "chartered_company", "vassal",
                   "tributary", "personal_union", "crown_land"}


def nodes(rel: str, suffix=".txt"):
    for path in sorted((VANILLA / rel).glob("*" + suffix)):
        yield path, pdx.parse_file(path)


def num(node, key, default=0.0):
    v = node.get_float(key) if node is not None else None
    return default if v is None else v


def adds(node, pattern: str) -> dict:
    """Numeric `key = value` pairs matching pattern anywhere under node."""
    out = C.Counter()
    if node is None:
        return out
    for k, v in node.pairs():
        if isinstance(v, pdx.Node):
            out.update(adds(v, pattern))
        elif isinstance(v, str):
            m = re.fullmatch(pattern, k)
            if m:
                try:
                    out[m.group(1)] += float(v)
                except ValueError:
                    pass
    return out


# ---------------------------------------------------------------- game rules

class Rules:
    def __init__(self):
        self.pm = {}
        for _, root in nodes("common/production_methods"):
            for name, n in root.pairs():
                if not isinstance(n, pdx.Node):
                    continue
                bm = n.get_node("building_modifiers")
                io = C.Counter()
                for sub in ("workforce_scaled", "unscaled"):
                    blk = bm.get_node(sub) if bm else None
                    for k, v in (blk.pairs() if blk else []):
                        m = re.fullmatch(r"goods_(input|output)_(\w+?)_add", k)
                        if m and isinstance(v, str):
                            io[(m.group(1), m.group(2))] += float(v)
                jobs = adds(bm.get_node("level_scaled") if bm else None, r"building_employment_(\w+)_add")
                cm = n.get_node("country_modifiers")
                sm = n.get_node("state_modifiers")
                self.pm[name] = {"io": io, "jobs": jobs,
                                 "country": adds(cm, r"(country_\w+_add)"),
                                 "state": adds(sm, r"(state_infrastructure_add)"),
                                 "techs": n.get_list("unlocking_technologies")}
        self.groups = {}
        for _, root in nodes("common/building_groups"):
            for name, n in root.pairs():
                if isinstance(n, pdx.Node):
                    self.groups[name] = n
        self.building = {}
        for _, root in nodes("common/buildings"):
            for name, n in root.pairs():
                if isinstance(n, pdx.Node):
                    self.building[name] = {"group": n.get_str("building_group"),
                                           "pmgs": n.get_list("production_method_groups"),
                                           "gov": n.get_str("ownership_type") == "government"
                                           or name in ("building_government_administration", "building_university",
                                                       "building_construction_sector")}
        self.pmg = {}
        for _, root in nodes("common/production_method_groups"):
            for name, n in root.pairs():
                if isinstance(n, pdx.Node):
                    self.pmg[name] = n.get_list("production_methods")
        self.price = {}
        self.traded = {}
        for _, root in nodes("common/goods"):
            for name, n in root.pairs():
                if isinstance(n, pdx.Node) and n.get_float("cost") is not None:
                    self.price[name] = n.get_float("cost")
                    self.traded[name] = n.get_float("traded_quantity") or 10
        self.needs = {}
        for _, root in nodes("common/pop_needs"):
            for name, n in root.pairs():
                if isinstance(n, pdx.Node):
                    self.needs[name] = {"default": n.get_str("default"),
                                        "entries": [(e.get_str("goods"), num(e, "weight", 1), num(e, "max_supply_share", 1))
                                                    for e in n.getall("entry") if isinstance(e, pdx.Node)]}
        self.packages = {}
        for _, root in nodes("common/buy_packages"):
            for name, n in root.pairs():
                m = re.fullmatch(r"wealth_(\d+)", name)
                if m and isinstance(n, pdx.Node):
                    g = n.get_node("goods")
                    self.packages[int(m.group(1))] = {k: float(v) for k, v in g.pairs() if isinstance(v, str)}
        self.tech_infra = {}
        for _, root in nodes("common/technology/technologies"):
            for name, n in root.pairs():
                if isinstance(n, pdx.Node):
                    mod = n.get_node("modifier")
                    a = adds(mod, r"(state_infrastructure_from_population_(?:max_)?add)")
                    if a:
                        self.tech_infra[name] = a
        self.traits = {}
        for _, root in nodes("common/state_traits"):
            for name, n in root.pairs():
                if isinstance(n, pdx.Node):
                    self.traits[name] = adds(n.get_node("modifier"), r"(state_infrastructure_(?:add|mult))")
        self.state_traits, self.coastal = {}, set()
        for _, root in nodes("map_data/state_regions"):
            for name, n in root.pairs():
                if isinstance(n, pdx.Node):
                    self.state_traits[name] = [t.strip('"') for t in n.get_list("traits")]
                    if n.get_str("naval_exit_id"):
                        self.coastal.add(name)
        self.upkeep = {}
        for _, root in nodes("common/combat_unit_types"):
            for name, n in root.pairs():
                if isinstance(n, pdx.Node):
                    u = n.get_node("upkeep_modifier")
                    self.upkeep[name] = {m: float(v) for k, v in (u.pairs() if u else [])
                                         if (m := (re.fullmatch(r"goods_input_(\w+?)_add", k) or [None, None])[1])}

    def group_attr(self, group: str, key: str):
        seen = set()
        while group and group not in seen:
            seen.add(group)
            n = self.groups.get(group)
            if n is None:
                return None
            if key in n:
                return n.get_str(key)
            group = n.get_str("parent_group")
        return None

    def fill_pms(self, building: str, pms: list[str]) -> list[str]:
        out = []
        for g in self.building.get(building, {}).get("pmgs", []):
            opts = self.pmg.get(g, [])
            pick = [p for p in pms if p in opts]
            out.append(pick[0] if pick else (opts[0] if opts else None))
        return [p for p in out if p]


def infra(rules: "Rules", sid: str, techs: set, pop: float, buildings: list, capital: bool, market_capital: bool):
    """(supply, usage) of one state share: 3 + population infrastructure (tech rate per 100k, capped; coastal and
    capital bonuses) + trait adds, x (1 + trait/market-capital mults), + port and railway method adds."""
    traits = rules.state_traits.get(sid, [])
    t_add = sum(rules.traits.get(t, {}).get("state_infrastructure_add", 0) for t in traits)
    t_mult = sum(rules.traits.get(t, {}).get("state_infrastructure_mult", 0) for t in traits) + (0.25 if market_capital else 0)
    rate = sum(rules.tech_infra.get(t, {}).get("state_infrastructure_from_population_add", 0) for t in techs)
    cap = sum(rules.tech_infra.get(t, {}).get("state_infrastructure_from_population_max_add", 0) for t in techs)
    rate_mult = 1.0
    if sid in rules.coastal:
        rate_mult, cap = rate_mult + 0.05, cap + 10
    if capital:
        rate_mult, cap = rate_mult + 0.1, cap + 20
    usage, add = 0.0, 0.0
    for b in buildings:
        grp = rules.building.get(b["type"], {}).get("group")
        usage += b["level"] * float(rules.group_attr(grp, "infrastructure_usage_per_level") or 0)
        for p in b["production_methods"]:
            pm = rules.pm.get(p)
            if pm:
                add += pm["state"].get("state_infrastructure_add", 0) * b["level"]
    supply = (3 + t_add + min(cap, rate * rate_mult * pop / 100000)) * (1 + t_mult) + add
    return supply, usage


# ---------------------------------------------------------------- worlds

def vanilla_world(rules: Rules, tiers: dict) -> dict:
    states = {}
    for _, root in nodes("common/history/buildings"):
        for sk, sv in root.get_node("BUILDINGS").pairs():
            for rk, rv in sv.pairs():
                if not rk.startswith("region_state:") or not isinstance(rv, pdx.Node):
                    continue
                tag = rk.split(":")[1]
                for cb in rv.getall("create_building"):
                    bt = cb.get_str("building").strip('"')
                    own = cb.get_node("add_ownership")
                    lvl = sum(v.get_int("levels", 0) for _, v in (own.pairs() if own else []) if isinstance(v, pdx.Node))
                    pms = rules.fill_pms(bt, [p.strip('"') for p in cb.get_list("activate_production_methods")])
                    states.setdefault(sk[2:], {"owners": {}})["owners"].setdefault(tag, {"population": 0, "buildings": []})[
                        "buildings"].append({"type": bt, "level": lvl or cb.get_int("level", 0), "production_methods": pms})
    index = json.loads((ROOT / "build/index.json").read_text())["countries"]
    countries = C.defaultdict(lambda: {"population": 0, "technologies": [], "laws": [], "wealth": None, "capital": None})
    for _, root in nodes("common/history/pops"):
        for sk, sv in root.get_node("POPS").pairs():
            for rk, rv in sv.pairs():
                if rk.startswith("region_state:") and isinstance(rv, pdx.Node):
                    tag = rk.split(":")[1]
                    size = sum(cp.get_int("size", 0) for cp in rv.getall("create_pop"))
                    countries[tag]["population"] += size
                    st = states.setdefault(sk[2:], {"owners": {}})["owners"].setdefault(tag, {"population": 0, "buildings": []})
                    st["population"] += size
    for _, root in nodes("common/history/countries"):
        for ck, cv in root.get_node("COUNTRIES").pairs() if root.get_node("COUNTRIES") else []:
            if not isinstance(cv, pdx.Node):
                continue
            tag, c = ck.split(":")[-1], countries[ck.split(":")[-1]]
            techs = set()
            for k, v in cv.pairs():
                m = re.fullmatch(r"effect_starting_technology_tier_(\d)_tech", k)
                if m:
                    techs |= set(tiers.get(m.group(1), []))
                if k == "add_technology_researched":
                    techs.add(v)
                if k == "activate_law":
                    c["laws"].append(v.split(":")[-1])
            c["technologies"] = sorted(techs)
            c["capital"] = (index.get(tag) or {}).get("capital")
    for _, root in nodes("common/history/population"):
        for ck, cv in root.get_node("POPULATION").pairs() if root.get_node("POPULATION") else []:
            if isinstance(cv, pdx.Node):
                for k in cv.keys():
                    m = re.fullmatch(r"effect_starting_pop_wealth_(\w+)", k)
                    if m:
                        countries[ck.split(":")[-1]]["wealth"] = m.group(1)
    overlords, own_market = {}, set()
    for _, root in nodes("common/history/diplomacy"):
        dip = root.get_node("DIPLOMACY")
        for ck, cv in (dip.pairs() if dip else []):
            if isinstance(cv, pdx.Node) and ck.startswith("c:"):
                for p in cv.getall("create_diplomatic_pact"):
                    kind, target = p.get_str("type"), (p.get_str("country") or "").split(":")[-1]
                    if kind in MARKET_SUBJECTS:
                        overlords[target] = ck[2:]
                    elif kind == "grant_own_market":
                        own_market.add(target)
    military = military_units(rules, VANILLA / "common/history/military_formations")
    return {"name": "vanilla", "states": states, "countries": dict(countries),
            "overlords": {k: v for k, v in overlords.items() if k not in own_market}, "military": military}


def military_units(rules: Rules, folder: Path) -> dict:
    out = C.defaultdict(C.Counter)
    for path in sorted(folder.glob("*.txt")):
        root = pdx.parse_file(path).get_node("MILITARY_FORMATIONS")
        for ck, cv in (root.pairs() if root else []):
            if not isinstance(cv, pdx.Node):
                continue
            for f in cv.getall("create_military_formation"):
                for u in f.getall("combat_unit"):
                    out[ck.split(":")[-1]][u.get_str("type").split(":")[-1]] += u.get_int("count", 1)
    return {k: dict(v) for k, v in out.items()}


def mod_world(rules: Rules, report_path: Path = ROOT / "build/world-political/active-political-report.json",
              name: str = "mod") -> dict:
    report = json.loads(report_path.read_text())
    wealth = {}
    for path in (ROOT / "common/history/population").glob("*.txt"):
        root = pdx.parse_file(path).get_node("POPULATION")
        for ck, cv in (root.pairs() if root else []):
            if isinstance(cv, pdx.Node):
                for k in cv.keys():
                    m = re.fullmatch(r"effect_starting_pop_wealth_(\w+)", k)
                    if m:
                        wealth[ck.split(":")[-1]] = m.group(1)
    index = json.loads((ROOT / "build/index.json").read_text())["countries"]
    world_src = yaml.safe_load((ROOT / "world/scenario.yml").read_text())["countries"]
    countries = {t: {"population": c["population"], "technologies": c["technologies"], "laws": c["laws"],
                     "wealth": wealth.get(t),
                     "capital": (world_src.get(t) or {}).get("capital") or (index.get(t) or {}).get("capital")}
                 for t, c in report["countries"].items()}
    states = {sid: {"owners": {t: {"population": o["population"], "buildings": o.get("buildings", [])}
                               for t, o in st["owners"].items()}} for sid, st in report["states"].items()}
    military = military_units(rules, ROOT / "common/history/military_formations")
    return {"name": name, "states": states, "countries": countries,
            "overlords": report["diplomacy"]["overlords"], "military": military}


# ---------------------------------------------------------------- measurement

def measure(world: dict, rules: Rules) -> dict:
    ov = world["overlords"]

    def top(t):
        seen = set()
        while t in ov and t not in seen:
            seen.add(t)
            t = ov[t]
        return t

    market = {t: top(t) for t in world["countries"]}
    supply, industry, military, pops = (C.defaultdict(C.Counter) for _ in range(4))
    jobs = C.defaultdict(C.Counter)
    country = C.defaultdict(lambda: {"levels": 0, "va": 0.0, "types": C.Counter(), "gov_levels": 0,
                                     "bureaucracy": 100.0, "innovation": 50.0, "construction": 0.0,
                                     "states": 0, "bur_cost": 0.0, "infra_short": 0, "infra_states": 0,
                                     "trade_capacity": 0.0})
    for sid, st in world["states"].items():
        for tag, o in st["owners"].items():
            if tag not in world["countries"]:
                continue
            m, c = market.get(tag, tag), country[tag]
            techs = set(world["countries"][tag]["technologies"])
            for b in o["buildings"]:
                lvl, bt = b["level"], b["type"]
                grp = rules.building.get(bt, {}).get("group")
                eos = 1 + min(max(lvl - 1, 0), EOS_CAP) * 0.01 if rules.group_attr(grp, "economy_of_scale") == "yes" else 1
                c["levels"] += lvl
                c["types"][bt] += lvl
                if rules.building.get(bt, {}).get("gov"):
                    c["gov_levels"] += lvl
                for p in b["production_methods"]:
                    pm = rules.pm.get(p)
                    if not pm:
                        continue
                    for (kind, g), v in pm["io"].items():
                        (supply if kind == "output" else industry)[m][g] += v * lvl * eos
                        c["va"] += (1 if kind == "output" else -1) * v * lvl * eos * rules.price.get(g, 0)
                    for pop, n in pm["jobs"].items():
                        jobs[tag][pop] += n * lvl
                    c["bureaucracy"] += pm["country"].get("country_bureaucracy_add", 0) * lvl
                    c["innovation"] += pm["country"].get("country_weekly_innovation_add", 0) * lvl
                    c["construction"] += pm["country"].get("country_construction_add", 0) * lvl
                if bt == "building_trade_center":
                    c["trade_capacity"] += 10 * lvl
            pop = o["population"]
            if pop <= 0 and not o["buildings"]:
                continue
            cap_state = world["countries"][tag].get("capital")
            supply_infra, usage = infra(rules, sid, techs, pop, o["buildings"], cap_state == sid,
                                        cap_state == sid and market.get(tag, tag) == tag)
            c["infra_states"] += 1
            if usage > supply_infra:
                c["infra_short"] += 1
            c["states"] += 1
            reduce = 0.75 if REDUCE_BUR & set(world["countries"][tag]["laws"]) else 1.0
            c["bur_cost"] += 10 + 4 * pop / 100000 * reduce
    # military upkeep and soldiers
    for tag, units in world["military"].items():
        if tag not in world["countries"]:
            continue
        for u, n in units.items():
            for g, v in rules.upkeep.get(u, {}).items():
                military[market.get(tag, tag)][g] += v * n
            jobs[tag]["soldiers"] += 1000 * n
    # pop demand
    for tag, cdata in world["countries"].items():
        pop = cdata["population"]
        if pop <= 0:
            continue
        m = market.get(tag, tag)
        wf = WORKFORCE * pop
        j = jobs[tag]
        total_jobs = sum(max(v, 0) for v in j.values())
        scale = min(1.0, wf / total_jobs) if total_jobs else 0
        base = WEALTH_BASE.get(cdata.get("wealth") or "low", 10)
        households = {p: max(v, 0) * scale * HOUSEHOLD for p, v in j.items()}
        households["peasants"] = max(wf - total_jobs * scale, 0) * HOUSEHOLD * PEASANT_MARKET
        country[tag]["employment"] = total_jobs * scale / wf if wf else 0
        for p, units in households.items():
            w = max(1, min(99, base + STRATA.get(p, 0)))
            pkg = rules.packages.get(w) or rules.packages[min(rules.packages, key=lambda k: abs(k - w))]
            for need, money in pkg.items():
                pops[m][need] += money * units / 10000
    # split need £ into goods by market supply
    demand = C.defaultdict(C.Counter)
    for m, needs in pops.items():
        for need, money in needs.items():
            spec = rules.needs.get(need)
            if not spec:
                continue
            s_total = sum(supply[m][g] * rules.price.get(g, 1) for g, _, _ in spec["entries"]) or 1
            weights = {g: w * min(mx, supply[m][g] * rules.price.get(g, 1) / s_total) for g, w, mx in spec["entries"]}
            tw = sum(weights.values())
            if tw <= 0:
                weights, tw = {spec["default"]: 1}, 1
            for g, w in weights.items():
                demand[m][g] += money * w / tw / rules.price.get(g, 1)
    markets = {}
    for m in set(supply) | set(demand) | set(industry):
        goods = set(supply[m]) | set(industry[m]) | set(demand[m]) | set(military[m])
        pop = sum(world["countries"][t]["population"] for t in world["countries"] if market.get(t) == m)
        markets[m] = {"population": pop, "goods": {g: {"supply": round(supply[m][g], 1), "industry": round(industry[m][g], 1),
                                                         "military": round(military[m][g], 1), "pops": round(demand[m][g], 1)}
                                                     for g in sorted(goods)}}
    for tag, c in country.items():
        c["types"] = dict(c["types"])
        c["population"] = world["countries"].get(tag, {}).get("population", 0)
        c["technologies"] = len(world["countries"].get(tag, {}).get("technologies", []))
        c["bur_cost"] += c["gov_levels"]
        c["market"] = market.get(tag, tag)
    return {"world": world["name"], "countries": dict(country), "markets": markets}


def world_goods(res: dict) -> dict:
    tot = C.defaultdict(C.Counter)
    for mk in res["markets"].values():
        for g, v in mk["goods"].items():
            tot[g].update(v)
    return tot


def summary(v: dict, m: dict, rules: Rules) -> str:
    lines = ["# B0 balance measurement — vanilla vs active mod", "",
             "Static estimate; not an engine result. Generated by scenarios/atlas/balance_b0_model/measure.py.", ""]
    for res in (v, m):
        pop = sum(c["population"] for c in res["countries"].values())
        va = sum(c["va"] for c in res["countries"].values())
        lv = sum(c["levels"] for c in res["countries"].values())
        lines.append(f"- **{res['world']}**: population {pop/1e6:.0f} M, building levels {lv}, "
                     f"value added {va/1e6:.2f} M£/week")
    lines += ["", "## World goods: supply / demand (demand = building inputs + military + pops)", "",
              "| good | vanilla S/D | mod S/D | mod supply | mod industry | mod military | mod pops |", "|---|---:|---:|---:|---:|---:|---:|"]
    gv, gm = world_goods(v), world_goods(m)
    for g in sorted(set(gv) | set(gm), key=lambda g: -(gm[g]["supply"] * rules.price.get(g, 1))):
        def r(x):
            d = x["industry"] + x["military"] + x["pops"]
            return f"{x['supply']/d:.2f}" if d else "—"
        x = gm[g]
        lines.append(f"| {g} | {r(gv[g])} | {r(x)} | {x['supply']:.0f} | {x['industry']:.0f} | {x['military']:.0f} | {x['pops']:.0f} |")
    for res in (v, m):
        tot = sum(c["va"] for c in res["countries"].values())
        lines += ["", f"## {res['world']}: top countries by value added", "",
                  "| tag | pop M | VA k£ | share | VA/cap | lvl/M | techs | BUR supply/cost | innovation | construction | infra-short states | employment |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for tag, c in sorted(res["countries"].items(), key=lambda x: -x[1]["va"])[:30]:
            p = max(c["population"], 1)
            lines.append(f"| {tag} | {p/1e6:.1f} | {c['va']/1e3:.0f} | {c['va']/tot*100:.1f}% | {c['va']/p*1000:.1f} | "
                         f"{c['levels']/p*1e6:.1f} | {c['technologies']} | {c['bureaucracy']:.0f}/{c['bur_cost']:.0f} | "
                         f"{c['innovation']:.0f} | {c['construction']:.0f} | {c['infra_short']}/{c['infra_states']} | "
                         f"{c.get('employment', 0)*100:.0f}% |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--report", help="a candidate scenario-report.json instead of the active report")
    parser.add_argument("--name", default="mod", help="output name: build/balance/b0-<name>.json")
    args = parser.parse_args()
    rules = Rules()
    tiers = json.loads((ROOT / "scenarios/atlas/mechanics_m1_institutions/tier-techs.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    mod = mod_world(rules, ROOT / args.report, args.name) if args.report else mod_world(rules)
    for world in (vanilla_world(rules, tiers), mod):
        res = measure(world, rules)
        (OUT / f"b0-{world['name']}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
        results[world["name"]] = res
    suffix = "" if args.name == "mod" else f"-{args.name}"
    (OUT / f"b0-summary{suffix}.md").write_text(summary(results["vanilla"], results[args.name], rules))
    print(f"wrote {OUT.relative_to(ROOT)}/b0-vanilla.json, b0-{args.name}.json, b0-summary{suffix}.md")


if __name__ == "__main__":
    main()
