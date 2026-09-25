"""Audit the M1 candidate: only planned institutional country fields change."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIELDS = ("technology", "laws", "institutions")


def main() -> None:
    build = ROOT / "build/mechanics"
    source = yaml.safe_load((build / "m1-source.yml").read_text())
    candidate = yaml.safe_load((build / "m1-candidate.yml").read_text())
    prior = json.loads((build / "m1-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/m1-candidate/scenario-report.json").read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())["countries"]
    tier_techs = json.loads((HERE / "tier-techs.json").read_text())
    errors = []
    for field in ("version", "subject_types", "diplomacy", "states"):
        if source[field] != candidate[field]:
            errors.append(f"{field} changed")
    for tag in set(source["countries"]) | set(candidate["countries"]):
        old, new = source["countries"].get(tag, {}), candidate["countries"].get(tag, {})
        keep = lambda d: {k: v for k, v in d.items() if k not in FIELDS}
        if keep(old) != keep(new):
            errors.append(f"{tag}: non-institutional country fields changed")
        if tag not in plan and old != new:
            errors.append(f"{tag}: unplanned country changed")
    for tag, row in plan.items():
        country = report["countries"][tag]
        expected = set(tier_techs[str(row["tier"])]) | set(row["add_technologies"])
        if not expected <= set(country["technologies"]):
            errors.append(f"{tag}: technologies below tier {row['tier']}")
        if set(country["laws"]) != set(row["laws"]):
            errors.append(f"{tag}: reported laws differ: {sorted(set(country['laws']) ^ set(row['laws']))}")
        if country["population"] != prior["countries"][tag]["population"]:
            errors.append(f"{tag}: population changed")
        if country["building_levels"] != prior["countries"][tag]["building_levels"]:
            errors.append(f"{tag}: buildings changed")
    for tag, country in prior["countries"].items():
        if tag not in plan and report["countries"][tag]["laws"] != country["laws"]:
            errors.append(f"{tag}: non-target laws changed")
    if report["validation"] != "passed" or report["diplomacy"] != prior["diplomacy"]:
        errors.append("report validation or diplomacy differs")
    result = {"passed": not errors, "countries": len(plan), "errors": errors}
    (build / "m1-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/mechanics/m1-verification.json (passed={result['passed']})")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
