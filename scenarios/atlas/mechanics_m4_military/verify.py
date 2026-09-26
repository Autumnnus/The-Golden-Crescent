"""Audit the M4 candidate against plan.yml and targets.yml."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ISLAM = {"sunni", "shiite", "ibadi"}


def main() -> None:
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    targets = yaml.safe_load((HERE / "targets.yml").read_text())
    prior = json.loads((ROOT / "build/mechanics/m4-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/m4-candidate/scenario-report.json").read_text())
    world = yaml.safe_load((ROOT / "build/mechanics/m4-candidate.yml").read_text())
    errors = []
    for tag, row in plan["countries"].items():
        got = report["countries"][tag]["military"]
        if got != {"battalions": row["battalions"], "ships": row["ships"]}:
            errors.append(f"{tag}: report {got} differs from plan {row['battalions']}/{row['ships']}")
        if world["countries"][tag].get("military", {}).get("formations") != row["formations"]:
            errors.append(f"{tag}: world formations differ from the plan")
        if any(f["name"] not in plan["names"] for f in row["formations"]):
            errors.append(f"{tag}: formation without a name")
    for tag, country in prior["countries"].items():
        new = report["countries"][tag]
        if any(new[k] != country[k] for k in ("population", "building_levels", "laws", "technologies", "overlord")):
            errors.append(f"{tag}: non-military content changed")
        if tag not in plan["countries"] and new["military"] != country["military"]:
            errors.append(f"{tag}: military changed outside the plan")
    total = sum(r["battalions"] for r in plan["countries"].values())
    if abs(total - targets["total_battalions"]) > 0.05 * targets["total_battalions"]:
        errors.append(f"total battalions {total} is more than 5% off {targets['total_battalions']}")
    largest = max(plan["countries"], key=lambda t: plan["countries"][t]["ships"])
    if largest != "VAN":
        errors.append(f"largest navy is {largest}, not Andalusia")
    new_warnings = [w for w in report["warnings"] if w not in prior["warnings"]]
    if new_warnings:
        errors.append(f"new warnings: {new_warnings[:5]}")
    if report["validation"] != "passed":
        errors.append("report validation failed")
    result = {"passed": not errors, "countries": len(plan["countries"]), **plan["summary"],
              "largest_navy": largest, "errors": errors}
    out = ROOT / "build/mechanics/m4-verification.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)} (passed={result['passed']}) { {k: v for k, v in result.items() if k != 'errors'} }")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
