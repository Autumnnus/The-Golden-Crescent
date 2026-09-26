"""Audit the B2/B3 candidate against plan.yml, targets.yml and the B0 measure (build/balance/b0-b2.json)."""

from __future__ import annotations

import json
import os
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
from vic3 import mechanics  # noqa: E402

INPUTS = ["fabric", "wood", "tools", "iron", "coal", "paper", "steel", "ammunition"]
CONSUMER = ["grain", "clothes", "furniture", "groceries"]


def main() -> None:
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    targets = yaml.safe_load((HERE / "targets.yml").read_text())
    prior = json.loads((ROOT / "build/balance/b2-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/b2-candidate/scenario-report.json").read_text())
    b0 = json.loads((ROOT / "build/balance/b0-b2.json").read_text())
    data = mechanics.catalog()
    errors = []
    # only industry changed
    for tag, country in prior["countries"].items():
        new = report["countries"][tag]
        if any(new[k] != country[k] for k in ("population", "technologies", "laws", "overlord", "military")):
            errors.append(f"{tag}: non-industry content changed")
        if tag not in plan["countries"] and new["building_levels"] != country["building_levels"]:
            errors.append(f"{tag}: buildings changed outside the plan")
    # buildings match the plan
    for state, owners in plan["industry"].items():
        for tag, rows in owners.items():
            have = {b["type"]: b for b in report["states"][state]["owners"][tag]["buildings"]}
            for bt, row in rows.items():
                got = have.get(bt)
                if (row == 0 and got) or (row != 0 and (not got or got["level"] != row["level"]
                                                       or got["production_methods"] != row["production_methods"])):
                    errors.append(f"{state} {tag} {bt}: report differs from plan")
    # technology gates
    for state, st in report["states"].items():
        for tag, share in st["owners"].items():
            if tag not in plan["countries"]:
                continue
            techs = set(report["countries"][tag]["technologies"])
            for b in share["buildings"]:
                need = set(data["buildings"].get(b["type"], {}).get("unlocking_technologies", []))
                bad = [p for p in b["production_methods"]
                       if not set(data["production_methods"].get(p, {}).get("unlocking_technologies", [])) <= techs]
                if (need and not need <= techs) or bad:
                    errors.append(f"{state} {tag} {b['type']}: technology gate")
    # rank and targets
    c = b0["countries"]
    leader = targets["rank_leader"]
    top = max((t for t in c if c[t]["population"] > 0), key=lambda t: c[t]["va"])
    if top != leader:
        errors.append(f"largest economy is {top}, not {leader}")
    # independent countries only: subject plantation colonies (VPI, VFB...) have vanilla-like high export value
    big = [t for t in c if c[t]["population"] >= 1e6 and not report["countries"].get(t, {}).get("overlord")]
    per_head = max(big, key=lambda t: c[t]["va"] / c[t]["population"])
    if per_head != "ISF":
        errors.append(f"highest value added per head is {per_head}, not ISF")
    order = sorted(targets["protagonists"], key=lambda t: -c[t]["va"] / c[t]["population"])
    for tag in targets["protagonists"]:
        row = plan["countries"][tag]
        if c[tag]["va"] < 0.9 * row["va_target"]:
            errors.append(f"{tag}: value added {c[tag]['va']:.0f} below 90% of target {row['va_target']}")
    # state buildings
    for tag, n in targets["railways"].items():   # minimums since the third pass
        got = c[tag]["types"].get("building_railway", 0)
        if got < n:
            errors.append(f"{tag}: {got} railway levels, minimum {n}")
    # fleets are crewed: naval administration x 1,000 sailors covers the M4 fleets' crews
    m4 = yaml.safe_load((ROOT / "scenarios/atlas/mechanics_m4_military/plan.yml").read_text())["countries"]
    uncrewed = []
    for tag, row in m4.items():
        crew = sum(targets["naval_crew"].get(s["type"], 500) * s["count"] for f in row["formations"] for s in f.get("ships", []))
        have = c.get(tag, {}).get("types", {}).get("building_naval_administration", 0) * targets["sailors_per_level"]
        if crew and have < crew:
            uncrewed.append(f"{tag} {have}/{crew}")
    if len(uncrewed) > 2:
        errors.append(f"fleets without enough sailors: {uncrewed[:10]}")
    for tag, n in targets["universities"].items():
        if tag in plan["countries"] and c[tag]["types"].get("building_university", 0) != n:
            errors.append(f"{tag}: {c[tag]['types'].get('building_university', 0)} universities, target {n}")
    innovation = sorted(("ISF", "RUM", "EGY"), key=lambda t: -c[t]["innovation"])
    if innovation != ["ISF", "RUM", "EGY"]:
        errors.append(f"innovation order {innovation}")
    short = [t for t in plan["countries"] if c.get(t, {}).get("infra_short")]
    if short:
        errors.append(f"in-scope countries with infrastructure-short states: {short[:10]}")
    deficit = [t for t in plan["countries"] if plan["countries"][t]["group"] != "rest"
               and c.get(t) and c[t]["bureaucracy"] < c[t]["bur_cost"]]
    if deficit:
        errors.append(f"in-scope countries with a bureaucracy deficit: {deficit[:10]}")
    # world goods near the vanilla band
    world = {}
    for mk in b0["markets"].values():
        for g, x in mk["goods"].items():
            w = world.setdefault(g, [0.0, 0.0])
            w[0] += x["supply"]
            w[1] += x["industry"] + x["military"] + x["pops"]
    ratios = {g: round(world[g][0] / world[g][1], 2) for g in INPUTS + CONSUMER if world.get(g, [0, 0])[1]}
    for g in INPUTS:
        if ratios.get(g, 0) < 0.5:
            errors.append(f"world {g} supply/demand {ratios.get(g)} below 0.5")
    for g in CONSUMER:
        if ratios.get(g, 0) > 1.3:
            errors.append(f"world {g} supply/demand {ratios.get(g)} above 1.3")
    def untouched(warning: str) -> bool:
        """A screening warning about a share whose buildings did not change (Atlas rescreens a whole state)."""
        key = warning.split(":")[0]
        if "/" not in key:
            return False
        state, tag = key.split("/", 1)
        before = prior["states"].get(state, {}).get("owners", {}).get(tag, {}).get("buildings")
        return before is not None and before == report["states"][state]["owners"].get(tag, {}).get("buildings")
    new_warnings = [w for w in report["warnings"] if w not in prior["warnings"] and not untouched(w)]
    if new_warnings:
        errors.append(f"new warnings: {new_warnings[:5]}")
    if report["validation"] != "passed":
        errors.append("report validation failed")
    result = {"passed": not errors, **plan["summary"], "largest_economy": top, "highest_per_head": per_head,
              "protagonists_by_head": order, "world_ratios": ratios, "errors": errors}
    out = ROOT / "build/balance/b2-verification.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)} (passed={result['passed']}) top={top} per_head={per_head} {order} {ratios}")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
