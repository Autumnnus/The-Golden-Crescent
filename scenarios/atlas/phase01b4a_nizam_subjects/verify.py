"""Acceptance checks for the cumulative Phase 1B.4A Nizam preview."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "phase01b3_rum_military"
SUBJECTS = ("BOS", "ALB", "BUL", "ADA", "ERZ", "TRB")
POP_STATES = {
    "STATE_BOSNIA", "STATE_ALBANIA", "STATE_KOSOVO", "STATE_BULGARIA",
    "STATE_NORTHERN_THRACE", "STATE_DOBRUDJA", "STATE_ADANA",
    "STATE_ERZURUM", "STATE_KARS", "STATE_TRABZON",
}
EXPECTED_POPULATION = {"BOS": 950_000, "ALB": 1_450_000, "BUL": 2_100_000, "ADA": 550_000, "ERZ": 800_000, "TRB": 700_000}
EXPECTED_BUILDINGS = {"BOS": 35, "ALB": 52, "BUL": 82, "ADA": 35, "ERZ": 28, "TRB": 26}
EXPECTED_MILITARY = {
    "BOS": {"battalions": 10, "ships": 0}, "ALB": {"battalions": 12, "ships": 3},
    "BUL": {"battalions": 18, "ships": 4}, "ADA": {"battalions": 8, "ships": 3},
    "ERZ": {"battalions": 10, "ships": 0}, "TRB": {"battalions": 8, "ships": 4},
}
EXPECTED_DEPENDENCIES = {
    "BOS": ["coal", "fabric", "paper"],
    "ALB": ["artillery", "clippers", "fabric", "paper", "tools"],
    "BUL": ["clippers", "coal", "fabric", "paper"],
    "ADA": ["artillery", "clippers", "grain", "hardwood", "iron", "paper", "tools", "wood"],
    "ERZ": ["artillery", "clippers", "coal", "paper", "tools"],
    "TRB": ["artillery", "coal", "fabric", "grain", "paper", "tools"],
}

local = json.loads((ROOT / ".vic3-tools.local.json").read_text())
sys.path.insert(0, str(Path(local["toolkit"]) / "src"))
from vic3 import pdx  # noqa: E402


def read(path: Path):
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_key(node, key: str) -> int:
    total = 0
    for item in node.items:
        total += item.key == key
        if isinstance(item.value, pdx.Node):
            total += count_key(item.value, key)
    return total


def emitted_pop_rows(path: Path):
    root = pdx.parse_file(path).get_node("POPS")
    result = {}
    for state_key, state_node in root.pairs():
        state = state_key.removeprefix("s:")
        for tag in SUBJECTS:
            region = state_node.get_node(f"region_state:{tag}")
            if not region:
                continue
            rows = []
            for key, node in region.pairs():
                if key == "create_pop":
                    rows.append((node.get("culture"), node.get("religion"), int(node.get("size")), node.get("pop_type")))
            result[state, tag] = rows
    return result


def main():
    source = read(HERE / "scenario.json")
    plan = read(HERE / "nizam-plan.json")
    audit = read(HERE / "capacity-audit.json")
    parent_source = read(PARENT / "scenario.json")
    parent_report = read(ROOT / "build/phase01b3/report.json")
    report = read(ROOT / "build/phase01b4a/report.json")
    compiled = read(ROOT / "build/phase01b4a/generated/scenario-report.json")

    assert plan["parent_scenario_sha256"] == sha256(PARENT / "scenario.json")
    assert plan["parent_pops_sha256"] == sha256(ROOT / "build/phase01b3/generated/common/history/pops/tgc_pops.txt")
    assert report == {key: value for key, value in compiled.items() if key not in {"files", "output"}}
    assert report["validation"] == "passed" and report["runtime_tested"] is False
    assert report["diplomacy"] == parent_report["diplomacy"]
    added_warnings = [warning for warning in report["warnings"] if warning not in parent_report["warnings"]]
    removed_warnings = [warning for warning in parent_report["warnings"] if warning not in report["warnings"]]
    assert not added_warnings
    assert not removed_warnings

    assert {key: value for key, value in source["countries"].items() if key not in SUBJECTS} == {
        key: value for key, value in parent_source["countries"].items() if key not in SUBJECTS
    }
    for state, current in source["states"].items():
        previous = parent_source["states"][state]
        if state not in POP_STATES:
            assert current == previous, state
            continue
        assert {key: value for key, value in current.items() if key not in {"population", "industry", "split"}} == {
            key: value for key, value in previous.items() if key not in {"population", "industry", "split"}
        }, state
        if state != "STATE_TRABZON":
            assert current.get("split") == previous.get("split"), state

    trabzon = source["states"]["STATE_TRABZON"]
    parent_trabzon = parent_source["states"]["STATE_TRABZON"]
    current_rum = next(row for row in trabzon["split"] if row["owner"] == "RUM")["provinces"]
    current_trb = next(row for row in trabzon["split"] if row["owner"] == "TRB")["provinces"]
    old_rum = next(row for row in parent_trabzon["split"] if row["owner"] == "RUM")["provinces"]
    old_trb = next(row for row in parent_trabzon["split"] if row["owner"] == "TRB")["provinces"]
    assert set(old_rum) - set(current_rum) == {"x146DD9"}
    assert set(current_trb) - set(old_trb) == {"x146DD9"}
    assert trabzon["industry"]["by_owner"]["RUM"]["buildings"]["building_government_administration"] == 0
    assert trabzon["industry"]["by_owner"]["RUM"]["buildings"]["building_food_industry"] == 0

    for tag, previous in parent_report["countries"].items():
        if tag in SUBJECTS or tag == "RUM":
            continue
        assert report["countries"][tag] == previous, tag
    rum = report["countries"]["RUM"]
    old_rum_report = parent_report["countries"]["RUM"]
    assert {key: value for key, value in rum.items() if key != "building_levels"} == {
        key: value for key, value in old_rum_report.items() if key != "building_levels"
    }
    assert rum["building_levels"] == old_rum_report["building_levels"] - 5 == 1241

    total_battalions = total_ships = 0
    for tag in SUBJECTS:
        country = report["countries"][tag]
        assert country["population"] == EXPECTED_POPULATION[tag] == plan["countries"][tag]["population"]
        assert country["building_levels"] == EXPECTED_BUILDINGS[tag]
        assert country["military"] == EXPECTED_MILITARY[tag]
        assert country["laws"] == plan["countries"][tag]["laws"]
        assert country["settings"]["institutions"] == {"institution_schools": 1, "institution_police": 1}
        assert country["settings"]["interest_groups"] == {
            "mode": "replace", "ruling": plan["countries"][tag]["ruling_interest_groups"], "strength": {}
        }
        assert country["settings"]["history_mode"] == "replace"
        assert {"atmospheric_engine", "labor_movement", "law_enforcement", "line_infantry", "medical_degrees", "romanticism"}.issubset(country["technologies"])
        assert audit["countries"][tag]["trade_dependencies"] == EXPECTED_DEPENDENCIES[tag]
        assert audit["countries"][tag]["army_max_manpower"] == EXPECTED_MILITARY[tag]["battalions"] * 1000
        assert audit["countries"][tag]["navy_max_crew"] == EXPECTED_MILITARY[tag]["ships"] * 500
        total_battalions += country["military"]["battalions"]
        total_ships += country["military"]["ships"]
    assert (total_battalions, total_ships) == (66, 14)
    assert plan["freed_inherited_slave_status"] == 17_806

    emitted = emitted_pop_rows(ROOT / "build/phase01b4a/generated/common/history/pops/tgc_pops.txt")
    expected_regions = {(state, tag) for state, owners in plan["population_by_state"].items() for tag in owners}
    assert set(emitted) == expected_regions
    for key, rows in emitted.items():
        assert sum(row[2] for row in rows) == plan["population_by_state"][key[0]][key[1]]["total"], key
        assert all(row[3] != "slaves" for row in rows), key

    country_path = ROOT / "build/phase01b4a/generated/common/history/countries/ve_scenario_countries.txt"
    military_path = ROOT / "build/phase01b4a/generated/common/history/military_formations/ve_scenario_military.txt"
    countries_node = pdx.parse_file(country_path).get_node("COUNTRIES")
    military_node = pdx.parse_file(military_path).get_node("MILITARY_FORMATIONS")
    for tag in SUBJECTS:
        country_node = countries_node.get_node(f"c:{tag}")
        assert count_key(country_node, "activate_law") == 24
        assert count_key(country_node, "set_institution_investment_level") == 2
        assert count_key(country_node, "remove_ruling_interest_group") == 1
        assert count_key(country_node, "add_ruling_interest_group") == 2
        source_counts = Counter()
        for formation in source["countries"][tag]["military"]["formations"]:
            for unit in formation.get("units", []) + formation.get("ships", []):
                source_counts[unit["type"]] += unit["count"]
        emitted_counts = Counter()
        for formation in military_node.get_node(f"c:{tag}").getall("create_military_formation"):
            for effect, prefix in (("combat_unit", "unit_type:"), ("ship", "ship_type:")):
                for unit in formation.getall(effect):
                    emitted_counts[unit.get_str("type").removeprefix(prefix)] += unit.get_int("count")
        assert emitted_counts == source_counts == Counter(audit["countries"][tag]["formation_counts"])

    assert not (ROOT / "world/scenario.yml").exists()
    result = {
        "status": "passed",
        "scope": "six Nizam subjects: demography, laws, institutions, governments, economies and quota-scale formations",
        "scenario_sha256": sha256(HERE / "scenario.json"),
        "plan_sha256": sha256(HERE / "nizam-plan.json"),
        "capacity_audit_sha256": sha256(HERE / "capacity-audit.json"),
        "report_sha256": sha256(ROOT / "build/phase01b4a/report.json"),
        "subject_population": sum(EXPECTED_POPULATION.values()),
        "subject_building_levels": sum(EXPECTED_BUILDINGS.values()),
        "subject_battalions": total_battalions,
        "subject_ships": total_ships,
        "freed_inherited_slave_status": plan["freed_inherited_slave_status"],
        "unchanged_other_countries": len(report["countries"]) - len(SUBJECTS) - 1,
        "rum_population": rum["population"],
        "rum_battalions": rum["military"]["battalions"],
        "rum_ships": rum["military"]["ships"],
        "trabzon_city_owner": "TRB",
        "additional_warnings": [],
        "runtime_tested": False,
        "playable_release": False,
        "remaining_engine_gates": plan["design_limits"],
    }
    target = HERE / "verification.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print(f"verification failed: {error}", file=sys.stderr)
        raise
