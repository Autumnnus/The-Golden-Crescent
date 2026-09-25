"""Audit the M2 candidate: only building policies and industry plans change."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ALLOWED_WARNINGS = 2  # single-level buildings in two small Brazilian interior states


def main() -> None:
    build = ROOT / "build/mechanics"
    source = yaml.safe_load((build / "m2-source.yml").read_text())
    candidate = yaml.safe_load((build / "m2-candidate.yml").read_text())
    prior = json.loads((build / "m2-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/m2-candidate/scenario-report.json").read_text())
    restore = yaml.safe_load((HERE / "restore-plan.yml").read_text())["states"]
    fill = yaml.safe_load((HERE / "fill-plan.yml").read_text())["states"]
    errors = []
    for field in ("version", "subject_types", "diplomacy", "countries"):
        if source[field] != candidate[field]:
            errors.append(f"{field} changed")
    for state, old in source["states"].items():
        new = candidate["states"][state]
        strip = lambda d: {k: v for k, v in d.items() if k not in ("buildings", "industry")}
        if strip(old) != strip(new):
            errors.append(f"{state}: non-economic fields changed")
        planned = state in restore or state in fill
        if not planned and (old.get("buildings") != new.get("buildings") or old.get("industry") != new.get("industry")):
            errors.append(f"{state}: unplanned economic change")
        if state in restore and old.get("buildings") != "drop":
            errors.append(f"{state}: restored a state that was not dropped")
    for tag, country in prior["countries"].items():
        if report["countries"][tag]["population"] != country["population"]:
            errors.append(f"{tag}: population changed")
    new_warnings = [w for w in report["warnings"] if w not in prior["warnings"]]
    if len(new_warnings) > ALLOWED_WARNINGS:
        errors.append(f"new warnings: {new_warnings}")
    if report["validation"] != "passed" or report["diplomacy"] != prior["diplomacy"]:
        errors.append("report validation or diplomacy differs")
    levels = sum(c["building_levels"] for c in report["countries"].values())
    result = {"passed": not errors, "restored_states": len(restore), "filled_shares": sum(len(v) for v in fill.values()),
              "building_levels_before": sum(c["building_levels"] for c in prior["countries"].values()),
              "building_levels_after": levels, "new_warnings": new_warnings, "errors": errors}
    (build / "m2-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/mechanics/m2-verification.json (passed={result['passed']}, levels {levels})")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
