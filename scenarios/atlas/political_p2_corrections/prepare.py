"""P2: apply plan.yml, adjectives.yml and the new D2 subjects to a world copy.

1. Ownership transfers of whole state parts. The population share (total, literacy, composition)
   and explicit industry move with the part. Countries that lose their capital get their most
   populous remaining state; countries left without land simply drop out of the report.
2. Country field changes (Kurdistan -> Mosul emirate) and the new Gulf colony (VGZ), which copies
   New Ishbiliya's M1 technology tier, laws and institutions, with New Andalusia's slavery law.
3. Adjectives for every named country (TAG_ADJ), used by subject and dynamic names.
4. Subjects of diplomacy_d2_subjects/plan.yml that the world does not have yet are appended.
5. Balkan composition: Turkish Sunni and total Muslim shares of the listed owner shares.
   Other Muslim groups scale to muslim - turkish, non-Muslims shrink in proportion; Turkish
   becomes a homeland where it reaches 10%.
6. Inherited and explicit buildings of transferred parts are checked against the new owner's
   technologies and laws: unusable methods are swapped within their group (explicit merge item
   with the same level); buildings the owner cannot build are removed.
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


def parts_of(spec: dict) -> list[dict]:
    if "split" in spec:
        return spec["split"]
    return [{"owner": spec["owner"], "provinces": None}]


def transfer(world: dict, state: str, old: str, new: str) -> None:
    spec = world["states"][state]
    if "split" in spec:
        hits = [p for p in spec["split"] if p["owner"] == old]
        if not hits or any(p["owner"] == new for p in spec["split"]):
            raise ValueError(f"{state}: expected a part of {old} and none of {new}")
        for part in hits:
            part["owner"] = new
    elif spec.get("owner") == old:
        spec["owner"] = new
    else:
        raise ValueError(f"{state}: {old} is not the owner")
    by_owner = spec["population"]["by_owner"]
    by_owner[new] = by_owner.pop(old)
    industry = (spec.get("industry") or {}).get("by_owner") or {}
    if old in industry:
        industry[new] = industry.pop(old)


def recompose(share: dict, turkish: float | None, muslim: float) -> None:
    rows = share["composition"]
    total = sum(r["share"] for r in rows)
    for r in rows:
        r["share"] /= total
    muslim_rows = [r for r in rows if r["religion"] in ISLAM]
    other = [r for r in rows if r["religion"] not in ISLAM]
    if turkish is not None:
        turk = [r for r in muslim_rows if r["culture"] == "turkish" and r["religion"] == "sunni"]
        if not turk:
            turk = [{"culture": "turkish", "religion": "sunni", "share": 0.0}]
            rows.append(turk[0])
        rest = [r for r in muslim_rows if r not in turk]
        rest_now = sum(r["share"] for r in rest)
        rest_goal = max(0.0, muslim - turkish)
        if rest_now > 0:
            for r in rest:
                r["share"] *= rest_goal / rest_now
        elif rest_goal > 0:  # converts of the largest local culture (e.g. Pomaks)
            main = max(other, key=lambda r: r["share"])
            rows.append({"culture": main["culture"], "religion": "sunni", "share": rest_goal})
        turk[0]["share"] = turkish
    else:
        now = sum(r["share"] for r in muslim_rows)
        for r in muslim_rows:
            r["share"] *= muslim / now
    other_now = sum(r["share"] for r in other)
    for r in other:
        r["share"] *= (1 - muslim) / other_now
    for r in rows:
        r["share"] = round(r["share"], 6)
    rows[:] = [r for r in rows if r["share"] > 0]
    drift = 1 - sum(r["share"] for r in rows)
    max(rows, key=lambda r: r["share"])["share"] = round(max(rows, key=lambda r: r["share"])["share"] + drift, 6)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/political/p2-source.yml")
    parser.add_argument("--out", default="build/political/p2-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    adjectives = yaml.safe_load((HERE / "adjectives.yml").read_text())["countries"]
    d2 = yaml.safe_load((HERE.parent / "diplomacy_d2_subjects/plan.yml").read_text())
    m1 = yaml.safe_load((HERE.parent / "mechanics_m1_institutions/plan.yml").read_text())["countries"]
    report = json.loads((ROOT / "build/political/p2-source-report.json").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    data = mechanics.catalog()
    audit = {"transfers": [], "capitals": {}, "industry": [], "balkans": {}}

    # 2. countries first, so the new colony exists before it receives land
    for tag, fields in plan["countries"].items():
        world["countries"].setdefault(tag, {}).update(fields)
    for tag, spec in plan["new_countries"].items():
        if tag in world["countries"] or tag in index["countries"]:
            raise ValueError(f"{tag}: tag already exists")
        like = m1[spec["like"]]
        laws = [law for law in like["laws"] if "slavery" not in law] + [spec["slavery"]]
        world["countries"][tag] = {
            **{k: v for k, v in spec.items() if k not in ("like", "slavery")},
            "technology": {"mode": "merge", "tier": like["tier"], **({"add": like["add_technologies"]} if like["add_technologies"] else {})},
            "laws": {"values": sorted(laws)}, "institutions": like["institutions"]}
    # 1. transfers and capitals
    moved = []
    for row in plan["transfers"]:
        transfer(world, row["state"], row["from"], row["to"])
        moved.append((row["state"], row["from"], row["to"]))
        audit["transfers"].append(f"{row['state']}: {row['from']} -> {row['to']}")
    owned = defaultdict(dict)
    for state, spec in world["states"].items():
        for tag, share in spec["population"]["by_owner"].items():
            owned[tag][state] = share["total"]
    for _, old, _ in moved:
        capital = world["countries"].get(old, {}).get("capital") or index["countries"].get(old, {}).get("capital")
        if old in owned and capital not in owned[old]:
            entry = world["countries"].setdefault(old, {})
            entry["capital"] = max(owned[old], key=owned[old].get)
            audit["capitals"][old] = f"{capital} -> {entry['capital']}"
    # 3. adjectives
    for tag, adj in adjectives.items():
        world["countries"][tag]["adjective"] = adj["en"]
        world["countries"][tag]["adjective_tr"] = adj["tr"]
    # 4. subjects
    have = {(s["overlord"], s["subject"]) for s in world["diplomacy"]["subjects"]}
    for row in d2["subjects"]:
        if (row["overlord"], row["subject"]) not in have:
            if any(s["subject"] == row["subject"] for s in world["diplomacy"]["subjects"]):
                raise ValueError(f"{row['subject']} already has an overlord")
            world["diplomacy"]["subjects"].append(dict(row))
    # 5. Balkans
    for state, goal in plan["balkans"].items():
        spec = world["states"][state]
        share = spec["population"]["by_owner"][goal["owner"]]
        before = {k: round(sum(r["share"] for r in share["composition"] if f(r)), 3) for k, f in
                  (("turkish", lambda r: r["culture"] == "turkish" and r["religion"] == "sunni"),
                   ("muslim", lambda r: r["religion"] in ISLAM))}
        recompose(share, goal.get("turkish"), goal["muslim"])
        homelands = spec.get("homelands") or list(index["state_history"].get(state, {}).get("homelands") or [])
        if goal.get("turkish", 0) >= 0.10 and "turkish" not in homelands:
            spec["homelands"] = homelands + ["turkish"]
        audit["balkans"][state] = {"before": before, "after": {"turkish": goal.get("turkish"), "muslim": goal["muslim"]}}
    # 6. buildings of transferred parts, checked for the new owner
    # Records of the old owners as the source world generates them (build of p2-source.yml).
    source_build = ROOT / "build/scenarios/p2-source/common/history/buildings/tgc_buildings.txt"
    if not source_build.exists():
        raise SystemExit("build the source first: atlas scenario build build/political/p2-source.yml --out build/scenarios/p2-source")
    buildings = pdx.parse_file(source_build).get_node("BUILDINGS")
    records = {}
    for state_block in buildings.items:
        for owner_block in state_block.value.items:
            records[(state_block.key[2:], owner_block.key.split(":")[1])] = \
                [r for r in owner_block.value.getall("create_building") if isinstance(r, pdx.Node)]
    for state, old, new in moved:
        country = report["countries"].get(new) or report["countries"][plan["new_countries"][new]["like"]]
        techs = set(mechanics.prerequisites(set(country["technologies"]), data))
        laws = set(m1[new]["laws"]) if new in m1 else set(world["countries"][new]["laws"]["values"]) \
            if new in plan["new_countries"] else set(country["laws"])
        usable = lambda m: m in data["production_methods"] and "slave" not in m \
            and not set(data["production_methods"][m]["unlocking_technologies"]) - techs \
            and not set(data["production_methods"][m]["disallowing_laws"]) & laws
        own = records.get((state, old), [])
        if not own:  # decentralized old owner: Atlas dropped the vanilla block, the new owner inherits it
            own = [r for block in index["buildings"].get(state, {}).get("by_country", {}).values()
                   for r in dev.building_records(block.get("script", ""))]
        industry = world["states"][state].setdefault("industry", {}).setdefault("by_owner", {})
        part = industry.setdefault(new, {"mode": "merge", "buildings": {}})
        for name in sorted({str(r.get_str("building")) for r in own}):
            same = [r for r in own if str(r.get_str("building")) == name]
            definition = data["buildings"][name]
            if set(definition["unlocking_technologies"]) - techs:
                part["buildings"][name] = 0
                audit["industry"].append(f"{state}/{new}/{name}: removed, owner lacks technology")
                continue
            pms = [str(pm) for pm in same[0].get_list("activate_production_methods")]
            if all(usable(pm) for pm in pms):
                continue
            chosen = []
            for group in definition["production_method_groups"]:
                options = data["production_method_groups"][group]["production_methods"]
                ok = [m for m in pms if m in options and usable(m)] or [m for m in options if usable(m)]
                if ok:
                    chosen.append(str(ok[0]))
            item = part["buildings"].get(name)
            if isinstance(item, dict):
                item["production_methods"] = chosen
            else:
                kind = definition.get("ownership_type")
                part["buildings"][name] = {"level": sum(dev.level(r) for r in same), "production_methods": chosen,
                                           "ownership": "self" if kind == "self" else "government"}
            audit["industry"].append(f"{state}/{new}/{name}: {pms} -> {chosen}")
        if not part["buildings"]:
            del industry[new]
        if not industry:
            del world["states"][state]["industry"]["by_owner"]
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, ekonomi ve diplomasi (P2 düzeltmeleri)"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    (ROOT / "build/political/p2-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {output.relative_to(ROOT)}: {len(moved)} transfers, {len(audit['capitals'])} capitals, "
          f"{len(adjectives)} adjectives, {len(plan['balkans'])} Balkan shares, {len(audit['industry'])} building fixes")


if __name__ == "__main__":
    main()
