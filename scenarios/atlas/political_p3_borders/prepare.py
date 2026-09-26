"""P3: apply plan.yml (border revision) to a world copy.

1. Country field changes and new countries (technology tier, laws and institutions of an M1 template).
2. Province moves: a new part inside a state takes `total` people (and the old share's literacy)
   from the old owner's part; its composition and explicit buildings come from the plan.
3. Whole-share transfers, in plan order. A receiver that already has a part in the state absorbs
   the share: provinces, people, literacy (weighted), composition and buildings are summed.
4. Capitals of countries that lost their capital move to their most populous remaining state.
5. Muslim Andalusian America (religion), added Muslim communities, claims.
6. Slave POPs in shares whose new owner bans slavery are freed (same culture and religion).
7. Buildings of every transferred or merged share are rebuilt for the receiver from the source
   world's generated records: summed where both parts had the type, methods the receiver cannot
   use swapped within their group, buildings it cannot build removed. Decentralized receivers
   keep none (Atlas drops them).
8. Diplomacy: subjects, relations and the D3 plan's rivalries (both directions).
9. lineage.yml records, for every share P3 touched, which pre-P3 shares its people came from, so
   the M1b literacy step can be rerun on the P3 world.
"""

from __future__ import annotations

import argparse
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
from vic3 import development as dev, mechanics, pdx  # noqa: E402

HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"
ISLAM = {"sunni", "shiite", "ibadi"}
CHRISTIAN = {"catholic", "protestant", "orthodox"}
KEEP_FAITH = ISLAM | CHRISTIAN | {"jewish"}


def key(row: dict) -> tuple:
    return row["culture"], row["religion"], row.get("pop_type")


def normalize(rows: list[dict]) -> list[dict]:
    """Merge equal cohorts, drop empty ones, round and put the rounding drift on the largest row."""
    merged = {}
    for r in rows:
        k = key(r)
        merged[k] = merged.get(k, 0.0) + r["share"]
    total = sum(merged.values())
    out = []
    for (culture, religion, pop_type), share in merged.items():
        value = round(share / total, 6)
        if value > 0:
            out.append({"culture": culture, "religion": religion, "share": value,
                        **({"pop_type": pop_type} if pop_type else {})})
    drift = round(1 - sum(r["share"] for r in out), 6)
    max(out, key=lambda r: r["share"])["share"] = round(max(out, key=lambda r: r["share"])["share"] + drift, 6)
    return out


def combine(a: dict, b: dict) -> dict:
    """Population share b joins share a."""
    total = a["total"] + b["total"]
    rows = [{**r, "share": r["share"] * a["total"] / total} for r in a["composition"]] + \
           [{**r, "share": r["share"] * b["total"] / total} for r in b["composition"]]
    literacy = round((a["total"] * a["literacy"] + b["total"] * b["literacy"]) / total, 3)
    return {**a, "total": total, "literacy": literacy, "composition": normalize(rows)}


def convert(share: dict, keep: float, target: float | None) -> tuple[float, float]:
    rows = [dict(r) for r in share["composition"]]
    before = sum(r["share"] for r in rows if r["religion"] in ISLAM)
    for r in list(rows):
        if r["religion"] in CHRISTIAN:
            moved = r["share"] * (1 - keep)
            r["share"] -= moved
            rows.append({**r, "religion": "sunni", "share": moved})
    muslim = sum(r["share"] for r in rows if r["religion"] in ISLAM)
    local = [r for r in rows if r["religion"] not in KEEP_FAITH]
    pool = sum(r["share"] for r in local)
    if target is not None and muslim < target and pool > 0:
        fraction = min(1.0, (target - muslim) / pool)
        for r in local:
            moved = r["share"] * fraction
            r["share"] -= moved
            rows.append({**r, "religion": "sunni", "share": moved})
    share["composition"] = normalize(rows)
    return round(before, 3), round(sum(r["share"] for r in share["composition"] if r["religion"] in ISLAM), 3)


def parts(spec: dict, provinces: list[str]) -> list[dict]:
    """The state's parts; a single-owner state becomes a one-part split with all its provinces."""
    if "split" not in spec:
        spec["split"] = [{"owner": spec.pop("owner"), "provinces": list(provinces)}]
    return spec["split"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-dir", default=str(HERE.relative_to(ROOT)),
                        help="package whose plan.yml is applied (P4 reuses this script)")
    parser.add_argument("--name", default="p3", help="build file prefix")
    parser.add_argument("--source")
    parser.add_argument("--out")
    args = parser.parse_args()
    name, pkg = args.name, (ROOT / args.plan_dir).resolve()
    source = (ROOT / (args.source or f"build/political/{name}-source.yml")).resolve()
    output = (ROOT / (args.out or f"build/political/{name}-candidate.yml")).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = {"moves": [], "transfers": [], "countries": {}, "new_countries": {}, "religion": None,
            "communities": [], "claims": {}, **yaml.safe_load((pkg / "plan.yml").read_text())}
    plan["diplomacy"] = {"remove_subjects": [], "subjects": [], "relations": [], **(plan.get("diplomacy") or {})}
    d3 = yaml.safe_load((HERE.parent / "diplomacy_d3_treaties/plan.yml").read_text())
    m1 = yaml.safe_load((HERE.parent / "mechanics_m1_institutions/plan.yml").read_text())["countries"]
    report = json.loads((ROOT / f"build/political/{name}-source-report.json").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    data = mechanics.catalog()
    audit = {"moves": [], "transfers": [], "capitals": {}, "religion": {}, "communities": {},
             "freed_slaves": [], "industry": [], "landless": []}
    lineage = {}  # (state, tag) -> [[pre-P3 tag, people], ...]

    def origin(state: str, tag: str) -> list:
        if (state, tag) not in lineage:
            lineage[(state, tag)] = [[tag, world["states"][state]["population"]["by_owner"][tag]["total"]]]
        return lineage[(state, tag)]

    # 1. countries
    for tag, fields in plan["countries"].items():
        world["countries"].setdefault(tag, {}).update(fields)
    group = lambda law: data["laws"][law]["group"]
    for tag, spec in plan["new_countries"].items():
        if tag in world["countries"] or tag in index["countries"]:
            raise ValueError(f"{tag}: tag already exists")
        like = m1[spec["like"]]
        override = {group(law): law for law in spec.get("laws", [])}
        laws = sorted({override.get(group(law), law) for law in like["laws"]} | set(override.values()))
        world["countries"][tag] = {
            **{k: v for k, v in spec.items() if k not in ("like", "laws")},
            "technology": {"mode": "merge", "tier": like["tier"], **({"add": like["add_technologies"]} if like["add_technologies"] else {})},
            "laws": {"values": laws}, "institutions": like["institutions"]}

    source_build = ROOT / f"build/scenarios/{name}-source/common/history/buildings/tgc_buildings.txt"
    if not source_build.exists():
        raise SystemExit(f"build the source first: atlas scenario build build/political/{name}-source.yml --out build/scenarios/{name}-source")
    records = {}
    for state_block in pdx.parse_file(source_build).get_node("BUILDINGS").items:
        for owner_block in state_block.value.items:
            records[(state_block.key[2:], owner_block.key.split(":")[1])] = \
                [r for r in owner_block.value.getall("create_building") if isinstance(r, pdx.Node)]
    # 2. province moves
    for row in plan["moves"]:
        spec, old, new = world["states"][row["state"]], row["from"], row["to"]
        by_owner = spec["population"]["by_owner"]
        if new in by_owner:
            raise ValueError(f"{row['state']}: {new} already has a part")
        mine = [p for p in parts(spec, index["states"][row["state"]]["provinces"]) if p["owner"] == old]
        provinces = [q for p in mine for q in p["provinces"]]
        missing = set(row["provinces"]) - set(provinces)
        if missing or set(provinces) <= set(row["provinces"]):
            raise ValueError(f"{row['state']}: provinces {sorted(missing)} not in {old}'s parts or its share would vanish")
        for part in mine:  # an owner can hold several separate parts of one state
            part["provinces"] = [p for p in part["provinces"] if p not in row["provinces"]]
        spec["split"] = [p for p in spec["split"] if p["provinces"]]
        spec["split"].append({"owner": new, "provinces": list(row["provinces"])})
        share = by_owner[old]
        src = origin(row["state"], old)
        people = sum(n for _, n in src)
        taken = [[t, round(n * row["total"] / people)] for t, n in src]
        taken[-1][1] += row["total"] - sum(n for _, n in taken)
        lineage[(row["state"], old)] = [[t, n - m] for (t, n), (_, m) in zip(src, taken)]
        lineage[(row["state"], new)] = taken
        share["total"] -= row["total"]
        by_owner[new] = {"total": row["total"], "literacy": share["literacy"],
                         "composition": normalize([dict(r) for r in row.get("composition") or share["composition"]])}
        if row.get("industry") or row.get("take"):
            industry = spec.setdefault("industry", {}).setdefault("by_owner", {})
            gained = industry.setdefault(new, {"mode": "merge", "buildings": {}})["buildings"]
            gained.update(row.get("industry") or {})
            have = defaultdict(int)
            for r in records.get((row["state"], old), []):
                have[str(r.get_str("building"))] += dev.level(r)
            lost = industry.setdefault(old, {"mode": "merge", "buildings": {}})["buildings"]
            for building, level in (row.get("take") or {}).items():
                if have[building] < level:
                    raise ValueError(f"{row['state']}: {old} has {have[building]} {building}, cannot give {level}")
                lost[building] = have[building] - level
                gained[building] = gained.get(building, 0) + level
            if not lost:
                del industry[old]
        audit["moves"].append(f"{row['state']}: {len(row['provinces'])} provinces, {row['total']} people {old} -> {new}")

    # 3. transfers and merges
    touched = defaultdict(list)  # (state, receiver) -> contributors in the source world
    for row in plan["transfers"]:
        state, old, new = row["state"], row["from"], row["to"]
        spec = world["states"][state]
        by_owner = spec["population"]["by_owner"]
        if old not in by_owner:
            raise ValueError(f"{state}: {old} has no share")
        if spec.get("owner") == old:  # single-owner state: keep the owner form
            spec["owner"] = new
            split = []
        else:
            split = parts(spec, index["states"][state]["provinces"])
        mine = [p for p in split if p["owner"] == old]
        theirs = [p for p in split if p["owner"] == new]
        src = origin(state, old)
        if theirs:
            base = origin(state, new)
            for p in mine:
                theirs[0]["provinces"] = theirs[0]["provinces"] + p["provinces"]
                split.remove(p)
            by_owner[new] = combine(by_owner[new], by_owner.pop(old))
            lineage[(state, new)] = base + src
            kind = "merge"
        else:
            for p in mine:
                p["owner"] = new
            by_owner[new] = by_owner.pop(old)
            lineage[(state, new)] = src
            kind = "transfer"
        del lineage[(state, old)]
        industry = (spec.get("industry") or {}).get("by_owner") or {}
        if old in industry:
            moved = industry.pop(old)
            if new in industry:
                industry[new]["buildings"].update({k: v for k, v in moved["buildings"].items()
                                                   if k not in industry[new]["buildings"]})
            else:
                industry[new] = moved
        contributors = touched.pop((state, old), [old])
        touched[(state, new)] = (touched.get((state, new)) or ([new] if kind == "merge" else [])) + contributors
        audit["transfers"].append(f"{state}: {old} -> {new} ({kind})")
    owned = defaultdict(dict)
    for state, spec in world["states"].items():
        for tag, share in spec["population"]["by_owner"].items():
            owned[tag][state] = share["total"]
    losers = {r["from"] for r in plan["transfers"]} | {r["from"] for r in plan["moves"]}
    for tag in sorted(losers):
        entry = world["countries"].get(tag, {})
        capital = entry.get("capital") or index["countries"].get(tag, {}).get("capital")
        if tag not in owned:
            audit["landless"].append(tag)
        elif capital not in owned[tag]:
            world["countries"].setdefault(tag, {})["capital"] = max(owned[tag], key=owned[tag].get)
            audit["capitals"][tag] = f"{capital} -> {world['countries'][tag]['capital']}"
    for tag, spec in {**plan["countries"], **plan["new_countries"]}.items():
        if "capital" in spec and spec["capital"] not in owned.get(tag, {}):
            raise ValueError(f"{tag}: capital {spec['capital']} is not owned")

    # 5. religion, communities, claims
    rel = plan["religion"] or {"owners": [], "keep": 1, "targets": {}}
    for state, spec in world["states"].items():
        if index["states"][state]["region"] not in ("05_north_america", "06_central_america", "07_south_america"):
            continue
        for tag in set(spec["population"]["by_owner"]) & set(rel["owners"]):
            before, after = convert(spec["population"]["by_owner"][tag], rel["keep"], rel["targets"].get(state))
            audit["religion"][f"{state}/{tag}"] = [before, after]
    for row in plan["communities"]:
        share = world["states"][row["state"]]["population"]["by_owner"][row["owner"]]
        added = sum(r["share"] for r in row["rows"])
        rows = [{**r, "share": r["share"] * (1 - added)} for r in share["composition"]] + [dict(r) for r in row["rows"]]
        share["composition"] = normalize(rows)
        audit["communities"][row["state"]] = round(added * share["total"])
    for state, tags in plan["claims"].items():
        spec = world["states"][state]
        current = spec.get("claims")
        if current is None:
            current = list(index["state_history"][state]["claims"])
        spec["claims"] = current + [t for t in tags if t not in current]

    # 6. slaves under an owner that bans slavery
    def laws_of(tag: str) -> set:
        entry = world["countries"].get(tag, {})
        if (entry.get("laws") or {}).get("values"):
            return set(entry["laws"]["values"])
        return set((report["countries"].get(tag) or {}).get("laws", []))
    for (state, tag) in sorted(lineage):
        share = world["states"][state]["population"]["by_owner"].get(tag)
        if share and "law_slavery_banned" in laws_of(tag) and any(r.get("pop_type") == "slaves" for r in share["composition"]):
            freed = sum(r["share"] for r in share["composition"] if r.get("pop_type") == "slaves")
            share["composition"] = normalize([{k: v for k, v in r.items() if not (k == "pop_type" and v == "slaves")}
                                              for r in share["composition"]])
            audit["freed_slaves"].append(f"{state}/{tag}: {round(freed * share['total'])}")

    # 7. buildings of transferred and merged shares, rebuilt for the receiver
    source_world = yaml.safe_load(source.read_text())
    kind_of = lambda tag: world["countries"].get(tag, {}).get("country_type") or index["countries"].get(tag, {}).get("country_type")

    def vanilla_blocks(state: str, tag: str) -> list:
        """Vanilla blocks Atlas dropped because `tag` (decentralized) had the largest overlap."""
        spec = source_world["states"][state]
        split = spec.get("split") or [{"owner": spec["owner"], "provinces": index["states"][state]["provinces"]}]
        mine = {p.upper() for s in split if s["owner"] == tag for p in (s["provinces"] or index["states"][state]["provinces"])}
        out = []
        for van in index["state_history"][state]["owners"]:
            van_provs = {p.upper() for p in van["provinces"]}
            best = max(split, key=lambda s: len({p.upper() for p in (s["provinces"] or index["states"][state]["provinces"])} & van_provs))
            block = index["buildings"].get(state, {}).get("by_country", {}).get(van["country"])
            if best["owner"] == tag and block and mine & van_provs:
                out += dev.building_records(block.get("script", ""))
        return out

    for (state, new), contributors in sorted(touched.items()):
        spec = world["states"][state]
        industry = spec.setdefault("industry", {}).setdefault("by_owner", {})
        if kind_of(new) == "decentralized":
            industry.pop(new, None)
            if not industry:
                spec["industry"].pop("by_owner")
            continue
        own = defaultdict(list)
        for tag in contributors:
            recs = records.get((state, tag)) or (vanilla_blocks(state, tag) if kind_of(tag) == "decentralized" or
                                                 source_world["countries"].get(tag, {}).get("country_type") == "decentralized" else [])
            for r in recs:
                own[str(r.get_str("building"))].append((tag, r))
        country = report["countries"].get(new)
        techs = set(mechanics.prerequisites(set(country["technologies"]), data)) if country else \
            set(mechanics.prerequisites(set(report["countries"][plan["new_countries"][new]["like"]]["technologies"]), data))
        laws = laws_of(new)
        usable = lambda m: m in data["production_methods"] and "slave" not in m \
            and not set(data["production_methods"][m]["unlocking_technologies"]) - techs \
            and not set(data["production_methods"][m]["disallowing_laws"]) & laws
        part = industry.setdefault(new, {"mode": "merge", "buildings": {}})
        for building, rows in sorted(own.items()):
            definition = data["buildings"][building]
            if set(definition["unlocking_technologies"]) - techs:
                part["buildings"][building] = 0
                audit["industry"].append(f"{state}/{new}/{building}: removed, owner lacks technology")
                continue
            owners = {tag for tag, _ in rows}
            pms = [str(pm) for pm in rows[0][1].get_list("activate_production_methods")]
            mine_first = [r for tag, r in rows if tag == new] or [r for _, r in rows]
            pms = [str(pm) for pm in mine_first[0].get_list("activate_production_methods")]
            if len(owners) == 1 and all(usable(pm) for pm in pms) and building not in part["buildings"]:
                continue
            chosen = []
            for grp in definition["production_method_groups"]:
                options = data["production_method_groups"][grp]["production_methods"]
                ok = [m for m in pms if m in options and usable(m)] or [m for m in options if usable(m)]
                if ok:
                    chosen.append(str(ok[0]))
            kind = definition.get("ownership_type")
            part["buildings"][building] = {"level": sum(dev.level(r) for _, r in rows), "production_methods": chosen,
                                       "ownership": "self" if kind == "self" else "government"}
            audit["industry"].append(f"{state}/{new}/{building}: {sorted(owners)} {pms} -> {chosen}")
        if not part["buildings"]:
            del industry[new]
        if not industry:
            del spec["industry"]["by_owner"]
        if not spec["industry"]:
            del spec["industry"]

    # 8. diplomacy
    dip = world["diplomacy"]
    drop = {tuple(p) for p in plan["diplomacy"]["remove_subjects"]}
    before = len(dip["subjects"])
    dip["subjects"] = [s for s in dip["subjects"] if (s["overlord"], s["subject"]) not in drop]
    if before - len(dip["subjects"]) != len(drop):
        raise ValueError("a removed subject relation was not found")
    for row in plan["diplomacy"]["subjects"]:
        if any(s["subject"] == row["subject"] for s in dip["subjects"]):
            raise ValueError(f"{row['subject']} already has an overlord")
        dip["subjects"].append(dict(row))
    dip.setdefault("relations", []).extend(dict(r) for r in plan["diplomacy"]["relations"])
    # rivalries follow the D3 plan exactly, in its order (the political audit compares the list)
    dip["pacts"] = [row for row in dip.get("pacts", []) if row["type"] != "rivalry"] + \
        [{"actor": a, "target": b, "type": "rivalry"} for x, y in d3["rivalries"] for a, b in ((x, y), (y, x))]
    landed = set(owned)
    for s in dip["subjects"]:
        if s["overlord"] not in landed or s["subject"] not in landed:
            raise ValueError(f"subject {s} names a landless country")

    world["title"] = plan.get("title") or "The Golden Crescent — 1836 dünya, kurumlar, ekonomi ve diplomasi (P3 sınır revizyonu)"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    rows = {}
    for (state, tag), src in sorted(lineage.items()):
        if (state, tag) in {(s, t) for s, t in lineage} and world["states"][state]["population"]["by_owner"].get(tag):
            rows.setdefault(state, {})[tag] = src
    (pkg / "lineage.yml").write_text(f"# Generated by political_p3_borders/prepare.py: pre-{name.upper()} origin of every "
                                     f"share {name.upper()} touched ([source tag, people]); read by mechanics_m1b_literacy/prepare.py.\n" +
                                      yaml.safe_dump(rows, sort_keys=True, width=120))
    (ROOT / f"build/political/{name}-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {output.relative_to(ROOT)}: {len(audit['moves'])} moves, {len(audit['transfers'])} transfers, "
          f"{len(audit['capitals'])} capitals, {len(audit['landless'])} landless, {len(audit['religion'])} religion shares, "
          f"{len(audit['freed_slaves'])} freed, {len(audit['industry'])} building fixes")


if __name__ == "__main__":
    main()
