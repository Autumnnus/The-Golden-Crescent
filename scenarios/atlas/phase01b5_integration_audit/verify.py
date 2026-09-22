"""Acceptance checks for the Phase 1B.5 static integration audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EXPECTED_REPLACE_PATHS = {
    "common/history/buildings", "common/history/countries", "common/history/diplomacy",
    "common/history/military_formations", "common/history/pops",
    "common/history/population", "common/history/states",
}
EXPECTED_SUBJECTS = {"BOS", "ALB", "BUL", "ADA", "ERZ", "TRB"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    audit_path = HERE / "integration-audit.json"
    audit = json.loads(audit_path.read_text())
    parent_scenario = ROOT / audit["parent"]["scenario"]
    assert audit["parent"]["scenario_sha256"] == sha256(parent_scenario)
    assert audit["parent"]["report_sha256"] == sha256(ROOT / "build/phase01b4b/report.json")
    assert set(audit["replace_paths"]) == EXPECTED_REPLACE_PATHS
    assert audit["replace_paths_match_expected"] is True
    assert audit["generated_replaced_history_references"] == []

    startup = audit["tag_reference_scan"]["unmasked_startup_history"]["summary"]
    runtime = audit["tag_reference_scan"]["runtime_definitions"]["summary"]
    assert startup["files"] > 0 and startup["references"] > 0
    assert runtime["files"] > 0 and runtime["references"] > 0
    assert all(row["effective_reference_count"] > 0 for row in audit["startup_hazards"])
    assert all(row["loaded_despite_atlas_replace_paths"] for row in audit["startup_hazards"])

    pacts = audit["nizam"]["pacts"]
    assert len(pacts) == 6
    assert {p["actor"] for p in pacts} == {"RUM"}
    assert {p["target"] for p in pacts} == EXPECTED_SUBJECTS
    mechanics = audit["nizam"]["mechanics"]
    assert mechanics["income_transfer"] == 0.08
    assert mechanics["income_transfer_basis"] == "subject_income"
    assert mechanics["subject_can_start_own_plays"] is False
    assert mechanics["subject_joins_overlord_wars"] is True
    assert mechanics["subject_can_have_subjects"] is False
    assert mechanics["subject_can_break"] is False
    assert mechanics["annex_on_country_formation"] is True
    assert mechanics["overlord_must_be_higher_rank"] is False
    assert set(audit["independent_belt_overlords"].values()) == {None}

    risk = audit["risk_classification"]
    assert risk == {
        "confirmed_static_parse_or_build_crash": False,
        "startup_behavior_contamination": True,
        "runtime_event_or_on_action_contamination": True,
        "runtime_tested": False,
        "playable_release": False,
    }
    assert not (ROOT / "world/scenario.yml").exists()

    result = {
        "status": "passed",
        "audit_sha256": sha256(audit_path),
        "parent_scenario_sha256": sha256(parent_scenario),
        "unmasked_startup_files": startup["files"],
        "unmasked_startup_references": startup["references"],
        "runtime_definition_files": runtime["files"],
        "runtime_definition_references": runtime["references"],
        "nizam_pacts": len(pacts),
        "confirmed_static_crash": False,
        "runtime_tested": False,
        "playable_release": False,
    }
    target = HERE / "verification.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
