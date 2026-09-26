"""Audit the D1 candidate: only the listed native polities change, and they are decentralized."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def strip_state(spec: dict, tags: set) -> dict:
    spec = json.loads(json.dumps(spec))
    for share in spec["population"]["by_owner"].values():
        share.pop("literacy")
    by_owner = (spec.get("industry") or {}).get("by_owner") or {}
    for tag in tags & set(by_owner):
        del by_owner[tag]
    if "industry" in spec and "by_owner" in spec["industry"] and not by_owner:
        del spec["industry"]["by_owner"]
    return spec


def main() -> None:
    build = ROOT / "build/diplomacy"
    source = yaml.safe_load((build / "d1-source.yml").read_text())
    candidate = yaml.safe_load((build / "d1-candidate.yml").read_text())
    prior = json.loads((build / "d1-source-report.json").read_text())
    report = json.loads((ROOT / "build/scenarios/d1-candidate/scenario-report.json").read_text())
    tags = set(yaml.safe_load((HERE / "plan.yml").read_text())["countries"])
    errors = []
    for field in ("version", "subject_types", "diplomacy"):
        if source[field] != candidate[field]:
            errors.append(f"{field} changed")
    for state, old in source["states"].items():
        if strip_state(old, tags) != strip_state(candidate["states"][state], tags):
            errors.append(f"{state}: fields other than literacy and D1 industry changed")
    for tag in set(source["countries"]) | set(candidate["countries"]):
        old, new = source["countries"].get(tag, {}), candidate["countries"].get(tag, {})
        if tag not in tags and {k: v for k, v in old.items() if k != "institutions" or v} != \
                {k: v for k, v in new.items() if k != "institutions" or v}:
            errors.append(f"{tag}: non-D1 country changed")
    for tag, country in report["countries"].items():
        before = prior["countries"][tag]
        if country["population"] != before["population"]:
            errors.append(f"{tag}: population changed")
        if tag in tags:
            if country["building_levels"] or country["technologies"] or "law_chiefdom" not in country["laws"]:
                errors.append(f"{tag}: not a bare decentralized polity")
            if candidate["countries"][tag].get("country_type") != "decentralized":
                errors.append(f"{tag}: country type")
        elif country["building_levels"] != before["building_levels"] or country["laws"] != before["laws"] \
                or country["technologies"] != before["technologies"]:
            errors.append(f"{tag}: non-D1 buildings, laws or technologies changed")
    new_warnings = [w for w in report["warnings"] if w not in prior["warnings"]]
    if new_warnings:
        errors.append(f"new warnings: {new_warnings[:5]}")
    if report["validation"] != "passed" or report["diplomacy"] != prior["diplomacy"]:
        errors.append("report validation or diplomacy differs")
    result = {"passed": not errors, "decentralized": len(tags),
              "population": sum(report["countries"][t]["population"] for t in tags),
              "building_levels_removed": sum(prior["countries"][t]["building_levels"] for t in tags),
              "errors": errors}
    (build / "d1-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/diplomacy/d1-verification.json (passed={result['passed']}) "
          f"{result['decentralized']} countries, {result['population']:,} people, "
          f"{result['building_levels_removed']} levels removed")
    if errors:
        print("\n".join(errors[:40]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
