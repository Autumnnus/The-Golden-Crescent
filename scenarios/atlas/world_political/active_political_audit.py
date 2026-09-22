"""Check that the installed political world matches the reviewed Atlas cards."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
PREVIEW = ROOT / "build/world-political/partial-political-preview.json"
ACTIVE = ROOT / "world/scenario.yml"
REPORT = ROOT / "build/world-political/active-political-report.json"
OUT = ROOT / "build/world-political/active-political-audit.json"
REPLACE_PATHS = {
    "common/history/buildings",
    "common/history/countries",
    "common/history/diplomacy",
    "common/history/military_formations",
    "common/history/pops",
    "common/history/population",
    "common/history/states",
}


def political_state(spec: dict) -> dict:
    return {key: value for key, value in spec.items() if key not in {"pops", "buildings"}}


def main() -> None:
    preview = json.loads(PREVIEW.read_text())
    active = yaml.safe_load(ACTIVE.read_text())
    report = json.loads(REPORT.read_text())
    metadata = json.loads((ROOT / ".metadata/metadata.json").read_text())
    mismatches = []

    for key in ("version", "countries", "subject_types", "diplomacy"):
        if active.get(key) != preview.get(key):
            mismatches.append(key)
    if set(active["states"]) != set(preview["states"]):
        mismatches.append("state IDs")
    else:
        for state in preview["states"]:
            if political_state(active["states"][state]) != political_state(preview["states"][state]):
                mismatches.append(state)

    pop_policies = {state: spec.get("pops") for state, spec in active["states"].items()}
    building_policies = {state: spec.get("buildings") for state, spec in active["states"].items()}
    if any(value != "inherit" for value in pop_policies.values()):
        mismatches.append("population inheritance")
    if any(value not in {"inherit", "drop"} for value in building_policies.values()):
        mismatches.append("building inheritance")
    if len(report["states"]) != len(preview["states"]):
        mismatches.append("reported states")
    if any(not row["population"] for row in report["states"].values()):
        mismatches.append("empty state population")
    if any(not row["population"] for row in report["countries"].values()):
        mismatches.append("empty landed country population")
    if report["diplomacy"] != json.loads(
        (ROOT / "build/world-political/final-political-report.json").read_text()
    )["diplomacy"]:
        mismatches.append("reported diplomacy")
    actual_replace_paths = set(metadata["game_custom_data"]["replace_paths"])
    if actual_replace_paths != REPLACE_PATHS:
        mismatches.append("metadata replace_paths")

    payload = {
        "title": "Etkin siyasi dünya denetimi",
        "political_state_count": len(active["states"]),
        "landed_country_count": len(report["countries"]),
        "population": sum(row["population"] for row in report["states"].values()),
        "building_states_inherited": sum(value == "inherit" for value in building_policies.values()),
        "building_states_deferred": sum(value == "drop" for value in building_policies.values()),
        "building_levels": sum(row["building_levels"] for row in report["countries"].values()),
        "static_report_warnings": report["warnings"],
        "runtime_tested": report["runtime_tested"],
        "mismatches": mismatches,
        "passed": not mismatches and report["validation"] == "passed",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (passed={payload['passed']})")
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
