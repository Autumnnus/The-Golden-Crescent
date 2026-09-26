"""Audit the P2 candidate against plan.yml."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ISLAM = {"sunni", "shiite", "ibadi"}
ALLOWED_WARNING = "removed inherited army unit in lost state"


def main() -> None:
    build = ROOT / "build/political"
    source = yaml.safe_load((build / "p2-source.yml").read_text())
    candidate = yaml.safe_load((build / "p2-candidate.yml").read_text())
    prior = json.loads((build / "p2-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/p2-candidate/scenario-report.json").read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    adjectives = yaml.safe_load((HERE / "adjectives.yml").read_text())["countries"]
    d2 = yaml.safe_load((HERE.parent / "diplomacy_d2_subjects/plan.yml").read_text())
    errors = []
    moved = {(r["state"], r["to"]): r["from"] for r in plan["transfers"]}
    touched = {r["from"] for r in plan["transfers"]} | {r["to"] for r in plan["transfers"]}
    for state, old in source["states"].items():
        new = candidate["states"][state]
        old_pop, new_pop = old["population"]["by_owner"], new["population"]["by_owner"]
        for tag, share in new_pop.items():
            before = old_pop.get(moved.get((state, tag), tag))
            if before is None or before["total"] != share["total"] or before["literacy"] != share["literacy"]:
                errors.append(f"{state}/{tag}: share total or literacy changed")
            elif state not in plan["balkans"] and before["composition"] != share["composition"]:
                errors.append(f"{state}/{tag}: composition changed outside the Balkan plan")
        if report["states"][state]["population"] != prior["states"][state]["population"]:
            errors.append(f"{state}: population changed")
    for state, goal in plan["balkans"].items():
        rows = candidate["states"][state]["population"]["by_owner"][goal["owner"]]["composition"]
        muslim = sum(r["share"] for r in rows if r["religion"] in ISLAM)
        turkish = sum(r["share"] for r in rows if r["culture"] == "turkish" and r["religion"] == "sunni")
        if abs(muslim - goal["muslim"]) > 0.002 or ("turkish" in goal and abs(turkish - goal["turkish"]) > 0.002) \
                or abs(sum(r["share"] for r in rows) - 1) > 1e-6:
            errors.append(f"{state}: composition {turkish:.3f}/{muslim:.3f} misses {goal}")
    for row in plan["transfers"]:
        if row["to"] not in report["states"][row["state"]]["owners"] or row["from"] in report["states"][row["state"]]["owners"]:
            errors.append(f"{row['state']}: owner is not {row['to']}")
    for tag, adj in adjectives.items():
        entry = candidate["countries"].get(tag, {})
        if (entry.get("adjective"), entry.get("adjective_tr")) != (adj["en"], adj["tr"]):
            errors.append(f"{tag}: adjective")
    expected = dict(prior["diplomacy"]["overlords"])
    expected.update({row["subject"]: row["overlord"] for row in d2["subjects"]})
    if report["diplomacy"]["overlords"] != expected:
        errors.append("reported overlords differ from the D2 plan")
    for tag, country in prior["countries"].items():
        if tag in touched or tag not in report["countries"]:
            continue
        new = report["countries"][tag]
        if any(new[k] != country[k] for k in ("population", "building_levels", "laws", "technologies")):
            errors.append(f"{tag}: untouched country content changed")
    new_warnings = [w for w in report["warnings"] if w not in prior["warnings"] and ALLOWED_WARNING not in w]
    if new_warnings:
        errors.append(f"new warnings: {new_warnings[:5]}")
    if report["validation"] != "passed":
        errors.append("report validation failed")
    result = {"passed": not errors, "transfers": len(plan["transfers"]), "balkan_shares": len(plan["balkans"]),
              "adjectives": len(adjectives), "subjects": len(report["diplomacy"]["overlords"]),
              "countries": len(report["countries"]), "errors": errors}
    (build / "p2-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/political/p2-verification.json (passed={result['passed']}) "
          f"{ {k: v for k, v in result.items() if k != 'errors'} }")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
