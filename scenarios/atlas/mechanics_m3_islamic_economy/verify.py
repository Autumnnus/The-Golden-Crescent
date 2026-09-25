"""Audit the M3 candidate: only planned Islamic industry and Rum's technologies change."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main() -> None:
    build = ROOT / "build/mechanics"
    source = yaml.safe_load((build / "m3-source.yml").read_text())
    candidate = yaml.safe_load((build / "m3-candidate.yml").read_text())
    prior = json.loads((build / "m3-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/m3-candidate/scenario-report.json").read_text())
    plan = yaml.safe_load((HERE / "fill-plan.yml").read_text())
    planned = {(state, tag) for state, owners in plan["states"].items() for tag in owners}
    errors = []
    for field in ("version", "subject_types", "diplomacy"):
        if source[field] != candidate[field]:
            errors.append(f"{field} changed")
    for tag in set(source["countries"]) | set(candidate["countries"]):
        old, new = source["countries"].get(tag, {}), candidate["countries"].get(tag, {})
        if tag == "RUM":
            old, new = ({k: v for k, v in d.items() if k != "technology"} for d in (old, new))
        if old != new:
            errors.append(f"{tag}: country fields changed")
    for state, old in source["states"].items():
        new = candidate["states"][state]
        if {k: v for k, v in old.items() if k != "industry"} != {k: v for k, v in new.items() if k != "industry"}:
            errors.append(f"{state}: non-industry fields changed")
        old_owners = (old.get("industry") or {}).get("by_owner") or {}
        new_owners = (new.get("industry") or {}).get("by_owner") or {}
        for tag in set(old_owners) | set(new_owners):
            if old_owners.get(tag) != new_owners.get(tag) and (state, tag) not in planned:
                errors.append(f"{state}/{tag}: unplanned industry change")
        for tag, orep in report["states"][state]["owners"].items():
            before = prior["states"][state]["owners"][tag]
            if orep["population"] != before["population"]:
                errors.append(f"{state}/{tag}: population changed")
            if (state, tag) not in planned and orep["buildings"] != before["buildings"]:
                errors.append(f"{state}/{tag}: unplanned building change")
    for tag, country in prior["countries"].items():
        if report["countries"][tag]["laws"] != country["laws"]:
            errors.append(f"{tag}: laws changed")
        if tag != "RUM" and report["countries"][tag]["technologies"] != country["technologies"]:
            errors.append(f"{tag}: technologies changed")
    rum = set(report["countries"]["RUM"]["technologies"])
    if not set(plan["rum_technology_additions"]) <= rum or not set(prior["countries"]["RUM"]["technologies"]) <= rum:
        errors.append("RUM lacks the Faz 1B.2 technologies")
    new_warnings = [w for w in report["warnings"] if w not in prior["warnings"]]
    if new_warnings:
        errors.append(f"new warnings: {new_warnings[:5]}")
    if report["validation"] != "passed" or report["diplomacy"] != prior["diplomacy"]:
        errors.append("report validation or diplomacy differs")
    levels = lambda r: sum(c["building_levels"] for c in r["countries"].values())
    result = {"passed": not errors, "shares": len(planned), "building_levels": [levels(prior), levels(report)],
              "rum_levels": [prior["countries"]["RUM"]["building_levels"], report["countries"]["RUM"]["building_levels"]],
              "errors": errors}
    (build / "m3-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/mechanics/m3-verification.json (passed={result['passed']}) levels {result['building_levels']}")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
