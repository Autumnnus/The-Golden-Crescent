"""Audit Phase 1B against unmasked vanilla startup and runtime references."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BUILD = ROOT / "build/phase01b4b/generated"
GAME = Path.home() / "Library/Application Support/Steam/steamapps/common/Victoria 3/game"
TAGS = ("TUR", "GRE", "ION")
TAG_PATTERN = re.compile(r"c:(TUR|GRE|ION)\b|\b(TUR|GRE|ION)\s*=\s*\{")
SCAN_ROOTS = (
    "common/history",
    "common/journal_entries",
    "common/on_actions",
    "common/decisions",
    "common/scripted_triggers",
    "common/scripted_effects",
    "events",
)
EXPECTED_REPLACE_PATHS = {
    "common/history/buildings",
    "common/history/countries",
    "common/history/diplomacy",
    "common/history/military_formations",
    "common/history/pops",
    "common/history/population",
    "common/history/states",
}
STARTUP_HAZARDS = {
    "common/history/characters/gre - greece.txt": "GRE character creation",
    "common/history/characters/ion - ionian islands.txt": "ION character creation",
    "common/history/characters/tur - ottomans.txt": "TUR character creation",
    "common/history/lobbies/00_lobbies.txt": "lobbies targeting GRE/TUR",
    "common/history/treaties/00_historical_treaties.txt": "historical treaty involving TUR",
    "common/history/political_movements/00_movements.txt": "TUR political movement",
    "common/history/power_blocs/00_power_blocs.txt": "TUR power bloc creation",
    "common/history/ai/00_secret_goals.txt": "AI secret goals involving GRE/TUR",
    "common/history/ai/00_strategy.txt": "TUR starting AI strategy",
    "common/history/global/00_global.txt": "global startup effects and checks involving GRE/TUR",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def effective_text(path: Path) -> str:
    """Remove Clausewitz line comments before matching active references."""
    return "\n".join(line.split("#", 1)[0] for line in path.read_text(encoding="utf-8-sig").splitlines())


def direct_references(path: Path) -> Counter[str]:
    result: Counter[str] = Counter()
    for match in TAG_PATTERN.finditer(effective_text(path)):
        result[match.group(1) or match.group(2)] += 1
    return result


def is_replaced(relative: str, replace_paths: set[str]) -> bool:
    return any(relative == prefix or relative.startswith(prefix + "/") for prefix in replace_paths)


def category(relative: str, replace_paths: set[str]) -> str:
    if relative.startswith("common/history/"):
        return "masked_history" if is_replaced(relative, replace_paths) else "unmasked_startup_history"
    return "runtime_definitions"


def scan_game(replace_paths: set[str]) -> dict:
    grouped: dict[str, list[dict]] = {
        "masked_history": [],
        "unmasked_startup_history": [],
        "runtime_definitions": [],
    }
    for root_name in SCAN_ROOTS:
        for path in sorted((GAME / root_name).rglob("*.txt")):
            refs = direct_references(path)
            if not refs:
                continue
            relative = path.relative_to(GAME).as_posix()
            grouped[category(relative, replace_paths)].append(
                {
                    "path": relative,
                    "references": dict(sorted(refs.items())),
                    "total": sum(refs.values()),
                    "sha256": sha256(path),
                }
            )
    return grouped


def totals(files: list[dict]) -> dict:
    by_tag: Counter[str] = Counter()
    for row in files:
        by_tag.update(row["references"])
    return {"files": len(files), "references": sum(by_tag.values()), "by_tag": dict(sorted(by_tag.items()))}


def main() -> None:
    metadata_path = BUILD / ".metadata/metadata.json"
    metadata = json.loads(metadata_path.read_text())
    replace_paths = set(metadata["game_custom_data"]["replace_paths"])
    scans = scan_game(replace_paths)

    generated_history_refs = []
    for path in sorted((BUILD / "common/history").rglob("*.txt")):
        refs = direct_references(path)
        if refs:
            generated_history_refs.append(
                {"path": path.relative_to(BUILD).as_posix(), "references": dict(sorted(refs.items()))}
            )

    hazards = []
    unmasked_by_path = {row["path"]: row for row in scans["unmasked_startup_history"]}
    for path, behavior in STARTUP_HAZARDS.items():
        row = unmasked_by_path.get(path)
        hazards.append(
            {
                "path": path,
                "behavior": behavior,
                "effective_reference_count": row["total"] if row else 0,
                "tags": sorted(row["references"]) if row else [],
                "loaded_despite_atlas_replace_paths": not is_replaced(path, replace_paths),
            }
        )

    report = json.loads((ROOT / "build/phase01b4b/report.json").read_text())
    nizam_pacts = [p for p in report["diplomacy"]["pacts"] if p["type"] == "ve_rum_nizam_dependency"]
    independent_belt = {
        tag: report["countries"][tag]["overlord"] for tag in ("KUR", "BSR", "SYR", "LEB", "PAL", "KUW")
    }

    subject_path = BUILD / "common/subject_types/ve_scenario_subjects.txt"
    action_path = BUILD / "common/diplomatic_actions/ve_scenario_subjects.txt"
    subject = effective_text(subject_path)
    action = effective_text(action_path)
    nizam = {
        "pacts": nizam_pacts,
        "mechanics": {
            "income_transfer": 0.08 if "income_transfer = 0.08" in action else None,
            "income_transfer_basis": "subject_income" if "income_transfer_based_on_second_country = yes" in action else "unknown",
            "subject_can_start_own_plays": "can_start_own_diplomatic_plays = yes" in subject,
            "subject_joins_overlord_wars": "join_overlord_wars = yes" in subject,
            "subject_can_have_subjects": "can_have_subjects = yes" in subject,
            "subject_can_break": "target_can_break = {\n\t\talways = no" not in action,
            "overlord_can_break": "actor_can_break" in action,
            "annex_on_country_formation": "annex_on_country_formation = yes" in subject,
            "overlord_must_be_higher_rank": "overlord_must_be_higher_rank = yes" in subject,
            "uses_overlord_map_color": "use_overlord_map_color = yes" in subject,
            "category": "same_as_vassal" if "category = same_as_vassal" in subject else None,
        },
        "unimplemented_written_terms": [
            "fixed annual contribution",
            "levy quota",
            "customs or shared-market treatment",
            "mutual negotiated termination",
        ],
        "release_gate": "revise contract semantics and engine-test inherited vassal interactions",
    }

    output = {
        "status": "static_audit_passed_with_release_blockers",
        "parent": {
            "scenario": "scenarios/atlas/phase01b4b_independent_belt/scenario.json",
            "scenario_sha256": sha256(ROOT / "scenarios/atlas/phase01b4b_independent_belt/scenario.json"),
            "report_sha256": sha256(ROOT / "build/phase01b4b/report.json"),
            "generated_metadata_sha256": sha256(metadata_path),
        },
        "replace_paths": sorted(replace_paths),
        "replace_paths_match_expected": replace_paths == EXPECTED_REPLACE_PATHS,
        "tag_reference_scan": {
            name: {"summary": totals(rows), "files": rows} for name, rows in scans.items()
        },
        "generated_replaced_history_references": generated_history_refs,
        "startup_hazards": hazards,
        "nizam": nizam,
        "independent_belt_overlords": independent_belt,
        "basra_kuwait_hub_gate": {
            "state_region": "STATE_BASRA",
            "city_hub": {"province": "x807060", "owner": "BSR"},
            "port_hub": {"province": "x00F060", "owner": "KUW"},
            "decision": "defer a second physical port until a separately reviewed state-region/province split",
        },
        "risk_classification": {
            "confirmed_static_parse_or_build_crash": False,
            "startup_behavior_contamination": True,
            "runtime_event_or_on_action_contamination": True,
            "runtime_tested": False,
            "playable_release": False,
        },
        "release_blockers": [
            "neutralize unmasked TUR/GRE/ION startup history without broad blind vanilla copies",
            "revise the Nizam contract to match the written contribution, levy, market and termination rules",
            "disable or replace obsolete Ottoman/Greek runtime chains where their triggers can still resolve",
            "resolve or explicitly retain the Basra-Kuwait single-port topology",
            "run an isolated engine startup and observe error/game logs after static blockers are fixed",
        ],
    }
    target = HERE / "integration-audit.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "status": output["status"],
        "scan_totals": {name: value["summary"] for name, value in output["tag_reference_scan"].items()},
        "startup_hazards": sum(row["effective_reference_count"] > 0 for row in hazards),
        "nizam_pacts": len(nizam_pacts),
        "output": str(target.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
