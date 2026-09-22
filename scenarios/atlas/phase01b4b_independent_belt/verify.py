"""Acceptance checks for cumulative Phase 1B.4B."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "phase01b4a_nizam_subjects"
COUNTRIES = ("KUR", "BSR", "SYR", "LEB", "PAL", "KUW")
POP_STATES = {"STATE_MOSUL", "STATE_DIYARBAKIR", "STATE_BASRA", "STATE_SYRIA", "STATE_TRANSJORDAN", "STATE_LEBANON", "STATE_PALESTINE"}
EXPECTED_POPULATION = {"KUR": 1_700_000, "BSR": 320_000, "SYR": 1_170_000, "LEB": 560_000, "PAL": 650_000, "KUW": 120_000}
EXPECTED_BUILDINGS = {"KUR": 68, "BSR": 20, "SYR": 62, "LEB": 41, "PAL": 42, "KUW": 9}
EXPECTED_MILITARY = {
    "KUR": {"battalions": 22, "ships": 0}, "BSR": {"battalions": 8, "ships": 3},
    "SYR": {"battalions": 16, "ships": 0}, "LEB": {"battalions": 8, "ships": 3},
    "PAL": {"battalions": 10, "ships": 3}, "KUW": {"battalions": 4, "ships": 4},
}
EXPECTED_DEPENDENCIES = {
    "KUR": ["artillery", "hardwood", "iron", "paper", "wood"],
    "BSR": ["artillery", "fabric", "grain", "hardwood", "iron", "wood"],
    "SYR": ["artillery", "clippers", "coal", "fabric", "hardwood", "iron", "wood"],
    "LEB": ["artillery", "fabric", "grain", "iron", "wood"],
    "PAL": ["artillery", "clippers", "coal", "wood"],
    "KUW": ["fabric", "grain", "hardwood", "wood"],
}
EXPECTED_REGIONAL_DEPENDENCIES = ["artillery", "fabric", "hardwood", "iron", "wood"]

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
        for tag in COUNTRIES:
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
    plan = read(HERE / "belt-plan.json")
    audit = read(HERE / "capacity-audit.json")
    parent_source = read(PARENT / "scenario.json")
    parent_report = read(ROOT / "build/phase01b4a/report.json")
    report = read(ROOT / "build/phase01b4b/report.json")
    compiled = read(ROOT / "build/phase01b4b/generated/scenario-report.json")

    assert plan["parent_scenario_sha256"] == sha256(PARENT / "scenario.json")
    assert plan["parent_pops_sha256"] == sha256(ROOT / "build/phase01b4a/generated/common/history/pops/tgc_pops.txt")
    assert report == {key: value for key, value in compiled.items() if key not in {"files", "output"}}
    assert report["validation"] == "passed" and report["runtime_tested"] is False
    assert report["warnings"] == parent_report["warnings"]
    assert report["diplomacy"] == parent_report["diplomacy"]

    assert {key: value for key, value in source["countries"].items() if key not in COUNTRIES} == {
        key: value for key, value in parent_source["countries"].items() if key not in COUNTRIES
    }
    for state, current in source["states"].items():
        previous = parent_source["states"][state]
        if state not in POP_STATES:
            assert current == previous, state
        else:
            assert {key: value for key, value in current.items() if key not in {"population", "industry"}} == {
                key: value for key, value in previous.items() if key not in {"population", "industry"}
            }, state

    basra_split = source["states"]["STATE_BASRA"]["split"]
    assert "x807060" in next(row for row in basra_split if row["owner"] == "BSR")["provinces"]
    assert "x00F060" in next(row for row in basra_split if row["owner"] == "KUW")["provinces"]
    basra_industry = source["states"]["STATE_BASRA"]["industry"]["by_owner"]
    assert "building_port" not in basra_industry["BSR"]["buildings"]
    assert basra_industry["KUW"]["buildings"]["building_port"]["level"] == 4

    for tag, previous in parent_report["countries"].items():
        if tag not in COUNTRIES:
            assert report["countries"][tag] == previous, tag

    total_battalions = total_ships = 0
    for tag in COUNTRIES:
        country = report["countries"][tag]
        assert country["population"] == EXPECTED_POPULATION[tag] == plan["countries"][tag]["population"]
        assert country["building_levels"] == EXPECTED_BUILDINGS[tag]
        assert country["military"] == EXPECTED_MILITARY[tag]
        assert country["overlord"] is None
        assert country["laws"] == plan["countries"][tag]["laws"]
        expected_institutions = {"institution_schools": 1, "institution_police": 1}
        if tag == "BSR":
            expected_institutions["institution_health_system"] = 1
        assert country["settings"]["institutions"] == expected_institutions
        assert country["settings"]["interest_groups"] == {
            "mode": "replace", "ruling": plan["countries"][tag]["ruling_interest_groups"], "strength": {}
        }
        assert country["settings"]["history_mode"] == "replace"
        assert {"academia", "artillery", "atmospheric_engine", "law_enforcement"}.issubset(country["technologies"])
        if tag == "BSR":
            assert {"democracy", "line_infantry", "medical_degrees", "romanticism"}.issubset(country["technologies"])
        assert audit["countries"][tag]["trade_dependencies"] == EXPECTED_DEPENDENCIES[tag]
        assert audit["countries"][tag]["army_max_manpower"] == EXPECTED_MILITARY[tag]["battalions"] * 1000
        assert audit["countries"][tag]["navy_max_crew"] == EXPECTED_MILITARY[tag]["ships"] * 500
        total_battalions += country["military"]["battalions"]
        total_ships += country["military"]["ships"]
    assert (total_battalions, total_ships) == (68, 13)
    assert audit["regional_external_dependencies"] == EXPECTED_REGIONAL_DEPENDENCIES
    assert plan["freed_inherited_slave_status_basra"] == 3_530
    assert plan["retained_inherited_slave_status_h8"] == 29_047

    emitted = emitted_pop_rows(ROOT / "build/phase01b4b/generated/common/history/pops/tgc_pops.txt")
    expected_regions = {(state, tag) for state, owners in plan["population_by_state"].items() for tag in owners}
    assert set(emitted) == expected_regions
    emitted_h8_slaves = 0
    for (state, tag), rows in emitted.items():
        assert sum(row[2] for row in rows) == plan["population_by_state"][state][tag]["total"], (state, tag)
        if tag == "BSR":
            assert all(row[3] != "slaves" for row in rows)
        else:
            emitted_h8_slaves += sum(row[2] for row in rows if row[3] == "slaves")
    assert emitted_h8_slaves > 0

    country_path = ROOT / "build/phase01b4b/generated/common/history/countries/ve_scenario_countries.txt"
    military_path = ROOT / "build/phase01b4b/generated/common/history/military_formations/ve_scenario_military.txt"
    countries_node = pdx.parse_file(country_path).get_node("COUNTRIES")
    military_node = pdx.parse_file(military_path).get_node("MILITARY_FORMATIONS")
    for tag in COUNTRIES:
        country_node = countries_node.get_node(f"c:{tag}")
        assert count_key(country_node, "activate_law") == 24
        assert count_key(country_node, "set_institution_investment_level") == (3 if tag == "BSR" else 2)
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
        "scope": "six independent Middle Eastern states: demography, H7/H8 laws, institutions, economies and bounded formations",
        "scenario_sha256": sha256(HERE / "scenario.json"), "plan_sha256": sha256(HERE / "belt-plan.json"),
        "capacity_audit_sha256": sha256(HERE / "capacity-audit.json"),
        "report_sha256": sha256(ROOT / "build/phase01b4b/report.json"),
        "population": sum(EXPECTED_POPULATION.values()), "building_levels": sum(EXPECTED_BUILDINGS.values()),
        "battalions": total_battalions, "ships": total_ships,
        "basra_freed_inherited_slave_status": plan["freed_inherited_slave_status_basra"],
        "h8_retained_inherited_slave_status_before_rescale": plan["retained_inherited_slave_status_h8"],
        "h8_emitted_slave_population": emitted_h8_slaves,
        "regional_external_dependencies": audit["regional_external_dependencies"],
        "unchanged_other_countries": len(report["countries"]) - len(COUNTRIES),
        "additional_warnings": [], "runtime_tested": False, "playable_release": False,
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
