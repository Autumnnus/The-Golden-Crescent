"""Acceptance checks for the cumulative Phase 1B.3 Rûm preview."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "phase01b2_rum_economy"
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


def main():
    source = read(HERE / "scenario.json")
    plan = read(HERE / "military-plan.json")
    audit = read(HERE / "military-capacity-audit.json")
    parent_source = read(PARENT / "scenario.json")
    parent_report = read(ROOT / "build/phase01b2/report.json")
    report = read(ROOT / "build/phase01b3/report.json")
    compiled = read(ROOT / "build/phase01b3/generated/scenario-report.json")

    assert plan["parent_scenario_sha256"] == sha256(PARENT / "scenario.json")
    assert plan["parent_report_sha256"] == sha256(ROOT / "build/phase01b2/report.json")
    assert report == {key: value for key, value in compiled.items() if key not in {"files", "output"}}
    assert report["validation"] == "passed" and report["runtime_tested"] is False
    assert report["warnings"] == parent_report["warnings"]
    assert report["diplomacy"] == parent_report["diplomacy"]

    assert {key: value for key, value in source["countries"].items() if key != "RUM"} == {
        key: value for key, value in parent_source["countries"].items() if key != "RUM"
    }
    assert set(source["states"]) == set(parent_source["states"])
    for state, current in source["states"].items():
        previous = parent_source["states"][state]
        assert current.get("owners") == previous.get("owners"), state
        assert current.get("population") == previous.get("population"), state
        assert {key: value for key, value in current.items() if key != "industry"} == {
            key: value for key, value in previous.items() if key != "industry"
        }, state
        if state not in plan["industry_changes"]:
            assert current.get("industry") == previous.get("industry"), state

    for tag, previous in parent_report["countries"].items():
        if tag != "RUM":
            assert report["countries"][tag] == previous, tag

    rum = report["countries"]["RUM"]
    old_rum = parent_report["countries"]["RUM"]
    assert rum["population"] == old_rum["population"] == 27_000_000
    assert rum["cultures"] == old_rum["cultures"]
    assert rum["religions"] == old_rum["religions"]
    assert rum["laws"] == old_rum["laws"]
    assert rum["settings"]["institutions"] == old_rum["settings"]["institutions"]
    assert rum["settings"]["companies"] == old_rum["settings"]["companies"]
    assert rum["settings"]["interest_groups"] == {
        "mode": "replace",
        "ruling": plan["government"]["ruling_interest_groups"],
        "strength": {},
    }
    assert set(plan["technology_additions"]).issubset(rum["technologies"])
    assert {"army_reserves", "line_infantry", "mandatory_service"}.issubset(rum["technologies"])
    assert rum["military"] == {"battalions": 160, "ships": 48}
    assert rum["building_levels"] == old_rum["building_levels"] + 15 == 1246

    source_counts = Counter()
    for formation in source["countries"]["RUM"]["military"]["formations"]:
        assert formation["hq_region"] in {"region_balkans", "region_near_east"}
        for unit in formation.get("units", []) + formation.get("ships", []):
            source_counts[unit["type"]] += unit["count"]
    expected_counts = Counter(plan["military"]["totals"]["army_composition"])
    expected_counts.update(plan["military"]["totals"]["fleet_composition"])
    assert source_counts == expected_counts == Counter(audit["formation_counts"])
    assert audit["army_max_manpower"] == 160_000
    assert audit["navy_max_crew"] == 30_000

    military_goods = {"small_arms", "ammunition", "artillery", "grain", "hardwood"}
    assert all(audit["goods"][good]["after_formation_upkeep"] >= 0 for good in military_goods)
    domestic_chain = {"coal", "engines", "explosives", "fertilizer", "iron", "lead", "paper", "steel", "sulfur", "tools"}
    assert all(audit["goods"][good]["industry_net"] >= 0 for good in domestic_chain)
    assert {good for good, row in audit["goods"].items() if row["industry_net"] < 0} == {
        "dye", "fabric", "meat", "silk", "wood"
    }

    country_path = ROOT / "build/phase01b3/generated/common/history/countries/ve_scenario_countries.txt"
    military_path = ROOT / "build/phase01b3/generated/common/history/military_formations/ve_scenario_military.txt"
    country_history = country_path.read_text()
    country_node = pdx.parse_file(country_path).get_node("COUNTRIES").get_node("c:RUM")
    assert country_node
    assert count_key(country_node, "remove_ruling_interest_group") == 1
    assert count_key(country_node, "add_ruling_interest_group") == 3
    assert "ve_scenario_ig_rum" not in country_history

    military_node = pdx.parse_file(military_path).get_node("MILITARY_FORMATIONS").get_node("c:RUM")
    assert military_node
    emitted_counts = Counter()
    formations = military_node.getall("create_military_formation")
    assert len(formations) == 5
    for formation in formations:
        for effect, prefix in (("combat_unit", "unit_type:"), ("ship", "ship_type:")):
            for unit in formation.getall(effect):
                emitted_counts[unit.get_str("type").removeprefix(prefix)] += unit.get_int("count")
    assert emitted_counts == source_counts

    schema = read(ROOT / "build/phase01b3/research/schema.json")
    country_fields = schema["properties"]["countries"]["additionalProperties"]["properties"]
    assert not {"treasury", "debt", "budget", "modifier"} & set(country_fields)
    assert not (ROOT / "world/scenario.yml").exists()

    result = {
        "status": "passed",
        "scope": "RUM government coalition, professional formations and military supply chain",
        "scenario_sha256": sha256(HERE / "scenario.json"),
        "military_plan_sha256": sha256(HERE / "military-plan.json"),
        "capacity_audit_sha256": sha256(HERE / "military-capacity-audit.json"),
        "report_sha256": sha256(ROOT / "build/phase01b3/report.json"),
        "population": rum["population"],
        "building_levels": rum["building_levels"],
        "battalions": rum["military"]["battalions"],
        "ships": rum["military"]["ships"],
        "army_max_manpower": audit["army_max_manpower"],
        "navy_max_crew": audit["navy_max_crew"],
        "ruling_interest_groups": plan["government"]["ruling_interest_groups"],
        "military_goods_after_upkeep": {
            good: audit["goods"][good]["after_formation_upkeep"] for good in sorted(military_goods)
        },
        "unchanged_other_countries": len(report["countries"]) - 1,
        "additional_warnings": [],
        "runtime_tested": False,
        "playable_release": False,
        "remaining_engine_gates": plan["engine_gates"],
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
