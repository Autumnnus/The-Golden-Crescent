"""Audit the D2 candidate: only the planned subject types and relations are added."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main() -> None:
    build = ROOT / "build/diplomacy"
    source = yaml.safe_load((build / "d2-source.yml").read_text())
    candidate = yaml.safe_load((build / "d2-candidate.yml").read_text())
    prior = json.loads((build / "d2-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/d2-candidate/scenario-report.json").read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    errors = []
    for field in ("version", "states", "countries"):
        if source[field] != candidate[field]:
            errors.append(f"{field} changed")
    if {k: v for k, v in candidate["subject_types"].items() if k not in plan["subject_types"]} != source["subject_types"]:
        errors.append("existing subject types changed")
    if candidate["diplomacy"]["subjects"] != source["diplomacy"]["subjects"] + plan["subjects"]:
        errors.append("subject list is not source + plan")
    if {k: v for k, v in candidate["diplomacy"].items() if k != "subjects"} != \
            {k: v for k, v in source["diplomacy"].items() if k != "subjects"}:
        errors.append("other diplomacy fields changed")
    expected = dict(prior["diplomacy"]["overlords"])
    expected.update({row["subject"]: row["overlord"] for row in plan["subjects"]})
    if report["diplomacy"]["overlords"] != expected:
        errors.append("reported overlords differ from the plan")
    for tag, country in prior["countries"].items():
        new = report["countries"][tag]
        if any(new[k] != country[k] for k in ("population", "building_levels", "laws", "technologies")):
            errors.append(f"{tag}: country content changed")
    new_warnings = [w for w in report["warnings"] if w not in prior["warnings"]]
    if new_warnings:
        errors.append(f"new warnings: {new_warnings[:5]}")
    if report["validation"] != "passed":
        errors.append("report validation failed")
    result = {"passed": not errors, "subject_types": len(plan["subject_types"]), "new_subjects": len(plan["subjects"]),
              "subjects": len(report["diplomacy"]["overlords"]), "errors": errors}
    (build / "d2-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/diplomacy/d2-verification.json (passed={result['passed']}) {result['subjects']} subjects")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
