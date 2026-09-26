"""Audit the D4 candidate: only planned country types change; content and diplomacy stay."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main() -> None:
    build = ROOT / "build/diplomacy"
    source = yaml.safe_load((build / "d4-source.yml").read_text())
    candidate = yaml.safe_load((build / "d4-candidate.yml").read_text())
    prior = json.loads((build / "d4-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/d4-candidate/scenario-report.json").read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())["countries"]
    errors = []
    for field in ("version", "states", "subject_types", "diplomacy"):
        if source[field] != candidate[field]:
            errors.append(f"{field} changed")
    for tag in set(source["countries"]) | set(candidate["countries"]):
        old = {k: v for k, v in source["countries"].get(tag, {}).items() if k != "country_type" or tag not in plan}
        new = {k: v for k, v in candidate["countries"].get(tag, {}).items() if k != "country_type" or tag not in plan}
        if old != new:
            errors.append(f"{tag}: fields other than the planned type changed")
    definitions = (ROOT / "build/scenarios/d4-candidate/common/country_definitions/tgc_countries.txt").read_text(encoding="utf-8-sig")
    for tag, row in plan.items():
        block = definitions.split(f"{tag} = {{", 1)[1].split("\n}", 1)[0] if f"{tag} = {{" in definitions else ""
        if f"country_type = {row['to']}" not in block:
            errors.append(f"{tag}: emitted definition is not {row['to']}")
    for tag, country in prior["countries"].items():
        new = report["countries"][tag]
        if any(new[k] != country[k] for k in ("population", "building_levels", "laws", "technologies")):
            errors.append(f"{tag}: country content changed")
    if report["diplomacy"] != prior["diplomacy"]:
        errors.append("reported diplomacy changed")
    new_warnings = [w for w in report["warnings"] if w not in prior["warnings"]]
    if new_warnings:
        errors.append(f"new warnings: {new_warnings[:5]}")
    if report["validation"] != "passed":
        errors.append("report validation failed")
    result = {"passed": not errors, "changed": len(plan),
              "to_recognized": sum(r["to"] == "recognized" for r in plan.values()),
              "to_unrecognized": sum(r["to"] == "unrecognized" for r in plan.values()), "errors": errors}
    (build / "d4-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/diplomacy/d4-verification.json (passed={result['passed']}) {result}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
