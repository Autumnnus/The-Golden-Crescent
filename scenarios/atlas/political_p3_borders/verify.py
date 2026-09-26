"""Audit a P3-style candidate against its plan.yml (P3 by default; P4 passes --plan-dir/--name)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ISLAM = {"sunni", "shiite", "ibadi"}
ALLOWED_WARNING = "removed inherited army unit in lost state"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-dir", default=str(HERE.relative_to(ROOT)))
    parser.add_argument("--name", default="p3")
    args = parser.parse_args()
    name, pkg = args.name, (ROOT / args.plan_dir).resolve()
    build = ROOT / "build/political"
    source = yaml.safe_load((build / f"{name}-source.yml").read_text())
    candidate = yaml.safe_load((build / f"{name}-candidate.yml").read_text())
    prior = json.loads((build / f"{name}-source-report.json").read_text())
    report = json.loads((ROOT / f"build/scenarios/{name}-candidate/scenario-report.json").read_text())
    plan = {"moves": [], "transfers": [], "countries": {}, "new_countries": {}, "religion": None,
            "communities": [], "claims": {}, **yaml.safe_load((pkg / "plan.yml").read_text())}
    plan["diplomacy"] = {"remove_subjects": [], "subjects": [], "relations": [], **(plan.get("diplomacy") or {})}
    lineage = yaml.safe_load((pkg / "lineage.yml").read_text())
    d3 = yaml.safe_load((HERE.parent / "diplomacy_d3_treaties/plan.yml").read_text())
    errors = []

    # people: every state keeps its population; every touched share's people are accounted for
    for state, row in report["states"].items():
        if row["population"] != prior["states"][state]["population"]:
            errors.append(f"{state}: population changed")
    for state, owners in lineage.items():
        by_owner = candidate["states"][state]["population"]["by_owner"]
        for tag, src in owners.items():
            if sum(n for _, n in src) != by_owner[tag]["total"]:
                errors.append(f"{state}/{tag}: lineage people differ from the share")
            before = {t: source["states"][state]["population"]["by_owner"][t] for t, _ in src}
            lit = sum(n * before[t]["literacy"] for t, n in src) / sum(n for _, n in src)
            if abs(lit - by_owner[tag]["literacy"]) > 0.0006:
                errors.append(f"{state}/{tag}: literacy {by_owner[tag]['literacy']} is not the weighted {lit:.4f}")
    # ownership
    for row in plan["moves"]:
        owners = report["states"][row["state"]]["owners"]
        split = {p["owner"]: set(p["provinces"]) for p in candidate["states"][row["state"]]["split"]}
        if not set(row["provinces"]) <= split.get(row["to"], set()) or owners.get(row["to"], {}).get("population") != row["total"]:
            errors.append(f"{row['state']}: move to {row['to']} missing")
    final_from = {}
    for row in plan["transfers"]:
        final_from.setdefault(row["state"], set()).add(row["from"])
    for row in plan["transfers"]:
        owners = report["states"][row["state"]]["owners"]
        if row["from"] in owners:
            errors.append(f"{row['state']}: {row['from']} still owns a part")
        target = row["to"]
        if target in final_from.get(row["state"], set()):
            continue  # passed on by a later transfer
        if target not in owners:
            errors.append(f"{row['state']}: {target} owns no part")
    landless = {t for t in prior["countries"] if t not in report["countries"]}
    losers = {r["from"] for r in plan["transfers"]}
    if landless - losers:
        errors.append(f"unexpected landless countries: {sorted(landless - losers)}")
    for tag in plan["new_countries"]:
        if tag not in report["countries"]:
            errors.append(f"{tag}: new country has no land")
    # religion and communities
    rel = plan["religion"] or {"owners": [], "targets": {}}
    for state, spec in candidate["states"].items():
        for tag in set(spec["population"]["by_owner"]) & set(rel["owners"]):
            if state not in source["states"] or tag not in source["states"][state]["population"]["by_owner"] and \
                    not any(tag == r["to"] and state == r["state"] for r in plan["transfers"]):
                continue
            rows = spec["population"]["by_owner"][tag]["composition"]
            muslim = sum(r["share"] for r in rows if r["religion"] in ISLAM)
            goal = rel["targets"].get(state)
            if goal is not None and muslim < goal - 0.002:
                errors.append(f"{state}/{tag}: Muslim {muslim:.3f} below {goal}")
            if abs(sum(r["share"] for r in rows) - 1) > 1e-6:
                errors.append(f"{state}/{tag}: composition does not sum to 1")
    for row in plan["communities"]:
        rows = candidate["states"][row["state"]]["population"]["by_owner"][row["owner"]]["composition"]
        for want in row["rows"]:
            got = sum(r["share"] for r in rows if r["culture"] == want["culture"] and r["religion"] == want["religion"])
            if got + 1e-6 < want["share"]:
                errors.append(f"{row['state']}: community {want['culture']}/{want['religion']} missing")
    # slavery: no slave POPs under an owner that bans slavery (shares P3 touched; older phases own the rest)
    for state, owners in lineage.items():
        for tag in owners:
            share = candidate["states"][state]["population"]["by_owner"][tag]
            if any(r.get("pop_type") == "slaves" for r in share["composition"]) and \
                    "law_slavery_banned" in (report["countries"].get(tag) or {}).get("laws", []):
                errors.append(f"{state}/{tag}: slaves under law_slavery_banned")
    # claims
    for state, tags in plan["claims"].items():
        if not set(tags) <= set(candidate["states"][state].get("claims") or []):
            errors.append(f"{state}: claims missing")
    # diplomacy
    expected = {k: v for k, v in prior["diplomacy"]["overlords"].items()
                if [v, k] not in plan["diplomacy"]["remove_subjects"] and k not in landless}
    expected.update({row["subject"]: row["overlord"] for row in plan["diplomacy"]["subjects"]})
    if report["diplomacy"]["overlords"] != expected:
        errors.append("reported overlords differ from the plan")
    pacts = candidate["diplomacy"]["pacts"]
    for x, y in d3["rivalries"]:
        for a, b in ((x, y), (y, x)):
            if {"actor": a, "target": b, "type": "rivalry"} not in pacts:
                errors.append(f"rivalry {a}-{b} missing")
    # untouched countries keep their content
    touched = losers | {r["to"] for r in plan["transfers"]} | {r["from"] for r in plan["moves"]} | \
        {r["to"] for r in plan["moves"]}
    for tag, country in prior["countries"].items():
        if tag in touched or tag not in report["countries"]:
            continue
        new = report["countries"][tag]
        if any(new[k] != country[k] for k in ("building_levels", "laws", "technologies")):
            errors.append(f"{tag}: untouched country content changed")
        elif new["population"] != country["population"] and tag not in {r["owner"] for r in plan["communities"]}:
            errors.append(f"{tag}: untouched country population changed")
    new_warnings = [w for w in report["warnings"] if w not in prior["warnings"] and ALLOWED_WARNING not in w]
    if new_warnings:
        errors.append(f"new warnings: {new_warnings[:5]}")
    if report["validation"] != "passed":
        errors.append("report validation failed")
    levels = (sum(c["building_levels"] for c in prior["countries"].values()),
              sum(c["building_levels"] for c in report["countries"].values()))
    result = {"passed": not errors, "moves": len(plan["moves"]), "transfers": len(plan["transfers"]),
              "new_countries": len(plan["new_countries"]), "landless": sorted(landless),
              "countries": [len(prior["countries"]), len(report["countries"])], "building_levels": list(levels),
              "subjects": len(report["diplomacy"]["overlords"]), "errors": errors}
    (build / f"{name}-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/political/{name}-verification.json (passed={result['passed']}) "
          f"{ {k: v for k, v in result.items() if k not in ('errors', 'landless')} }")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
