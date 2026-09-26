"""Audit the D5 candidate: same subject network on vanilla types; only colony types change."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VANILLA_TYPES = {"puppet", "protectorate", "vassal", "tributary", "colony", "dominion", "personal_union", "crown_land"}


def main() -> None:
    build = ROOT / "build/diplomacy"
    source = yaml.safe_load((build / "d5-source.yml").read_text())
    candidate = yaml.safe_load((build / "d5-candidate.yml").read_text())
    prior = json.loads((build / "d5-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/d5-candidate/scenario-report.json").read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    errors = []
    if source["states"] != candidate["states"]:
        errors.append("states changed")
    if candidate["subject_types"]:
        errors.append("custom subject types remain")
    strip = lambda rows: [{k: v for k, v in r.items() if k != "type"} for r in rows]
    if strip(source["diplomacy"]["subjects"]) != strip(candidate["diplomacy"]["subjects"]):
        errors.append("subject network changed")
    if any(r["type"] not in VANILLA_TYPES for r in candidate["diplomacy"]["subjects"]):
        errors.append("non-vanilla subject type")
    for tag in set(source["countries"]) | set(candidate["countries"]):
        old = {k: v for k, v in source["countries"].get(tag, {}).items() if k != "country_type" or tag not in plan["colonial"]}
        new = {k: v for k, v in candidate["countries"].get(tag, {}).items() if k != "country_type" or tag not in plan["colonial"]}
        if old != new:
            errors.append(f"{tag}: country fields changed")
    if report["diplomacy"]["overlords"] != prior["diplomacy"]["overlords"]:
        errors.append("reported overlords changed")
    for tag, country in prior["countries"].items():
        if any(report["countries"][tag][k] != country[k] for k in ("population", "building_levels", "laws", "technologies")):
            errors.append(f"{tag}: country content changed")
    if [w for w in report["warnings"] if w not in prior["warnings"]] or report["validation"] != "passed":
        errors.append("new warnings or failed validation")
    if (ROOT / "build/scenarios/d5-candidate/common/subject_types").exists():
        errors.append("custom subject type files are still generated")
    result = {"passed": not errors, "subjects": len(plan["subjects"]), "colonial": len(plan["colonial"]), "errors": errors}
    (build / "d5-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/diplomacy/d5-verification.json (passed={result['passed']})")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
