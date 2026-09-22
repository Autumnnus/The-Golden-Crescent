"""Read-only acceptance checks for the cumulative Phase 1B.2 preview."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "phase01b_rum_demography"


def read(path: Path):
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pop_rows(path: Path):
    local = read(ROOT / ".vic3-tools.local.json")
    sys.path.insert(0, str(Path(local["toolkit"]) / "src"))
    from vic3 import pdx

    root = pdx.parse_file(path).get_node("POPS")
    result = {}
    for state_key, state_node in root.pairs():
        if not state_key.startswith("s:"):
            continue
        region = state_node.get_node("region_state:RUM")
        if not region:
            continue
        rows = []
        for key, node in region.pairs():
            if key == "create_pop":
                rows.append(
                    (
                        node.get("culture"),
                        node.get("religion"),
                        node.get("pop_type") or "generic",
                        int(node.get("size")),
                    )
                )
        result[state_key[2:]] = rows
    return result


def verify():
    source = read(HERE / "scenario.json")
    plan = read(HERE / "economy-plan.json")
    audit = read(HERE / "capacity-audit.json")
    parent_source = read(PARENT / "scenario.json")
    parent_report = read(ROOT / "build/phase01b/report.json")
    report = read(ROOT / "build/phase01b2/report.json")
    compiled = read(ROOT / "build/phase01b2/generated/scenario-report.json")

    assert plan["parent_scenario_sha256"] == sha256(PARENT / "scenario.json")
    assert plan["parent_pops_sha256"] == sha256(ROOT / "build/phase01b/generated/common/history/pops/tgc_pops.txt")
    assert report == {key: value for key, value in compiled.items() if key not in {"files", "output"}}
    assert report["validation"] == "passed" and report["runtime_tested"] is False
    assert report["warnings"] == parent_report["warnings"]
    assert report["diplomacy"] == parent_report["diplomacy"]

    assert {key: value for key, value in source["countries"].items() if key != "RUM"} == {
        key: value for key, value in parent_source["countries"].items() if key != "RUM"
    }
    assert set(source["states"]) == set(parent_source["states"])
    assert set(plan["states"]) == {
        row["state"] for row in read(PARENT / "population-plan.json")["regions"]
    }

    for tag, previous in parent_report["countries"].items():
        if tag != "RUM":
            assert report["countries"][tag] == previous, tag

    rum = report["countries"]["RUM"]
    old_rum = parent_report["countries"]["RUM"]
    assert rum["population"] == 27_000_000
    assert rum["cultures"] == old_rum["cultures"]
    assert rum["religions"] == old_rum["religions"]
    assert rum["laws"] == old_rum["laws"]
    assert rum["settings"]["institutions"] == old_rum["settings"]["institutions"]
    assert rum["military"] == old_rum["military"] == {"battalions": 0, "ships": 0}
    assert rum["building_levels"] == 1231
    assert set(plan["technology_additions"]).issubset(rum["technologies"])

    for state, state_plan in plan["states"].items():
        previous_state = parent_report["states"][state]
        current_state = report["states"][state]
        for tag, previous_owner in previous_state["owners"].items():
            if tag != "RUM":
                assert current_state["owners"][tag] == previous_owner, (state, tag)
        owner = current_state["owners"]["RUM"]
        old_owner = previous_state["owners"]["RUM"]
        assert owner["population"] == old_owner["population"]
        assert owner["cultures"] == old_owner["cultures"]
        assert owner["religions"] == old_owner["religions"]
        buildings = {item["type"]: item for item in owner["buildings"]}
        for building, spec in state_plan["buildings"].items():
            expected_level = spec["level"] if isinstance(spec, dict) else spec
            if expected_level == 0:
                assert building not in buildings, (state, building)
            else:
                assert buildings[building]["level"] == expected_level, (state, building)

    old_pops = pop_rows(ROOT / "build/phase01b/generated/common/history/pops/tgc_pops.txt")
    new_pops = pop_rows(ROOT / "build/phase01b2/generated/common/history/pops/tgc_pops.txt")
    old_status = Counter()
    new_status = Counter()
    for state in old_pops:
        expected = Counter()
        for culture, religion, pop_type, size in old_pops[state]:
            old_status[pop_type] += size
            expected[culture, religion, "peasants" if pop_type == "slaves" else pop_type] += size
        actual = Counter()
        for culture, religion, pop_type, size in new_pops[state]:
            new_status[pop_type] += size
            actual[culture, religion, pop_type] += size
        assert actual == expected, state
    assert old_status["slaves"] == plan["emancipation"]["converted_starting_people"] == 216_325
    assert new_status["slaves"] == 0 and new_status["peasants"] == 216_325
    assert sum(new_status.values()) == 27_000_000

    core_surpluses = {"coal", "engines", "fertilizer", "iron", "paper", "steel", "sulfur", "tools"}
    assert all(audit["goods"][good]["explicit_net"] >= 0 for good in core_surpluses)
    assert {good for good, row in audit["goods"].items() if row["explicit_net"] < 0} == {
        "dye", "fabric", "meat", "silk", "wood"
    }
    assert audit["country_capacity"]["country_bureaucracy_add"] == 3450
    assert audit["country_capacity"]["country_weekly_innovation_add"] == 64.5
    assert audit["state_capacity"]["state_infrastructure_add"] == 913
    assert not (ROOT / "world/scenario.yml").exists()

    return {
        "status": "passed",
        "scope": "RUM emancipation status and economic/administrative backbone",
        "scenario_sha256": sha256(HERE / "scenario.json"),
        "economy_plan_sha256": sha256(HERE / "economy-plan.json"),
        "capacity_audit_sha256": sha256(HERE / "capacity-audit.json"),
        "report_sha256": sha256(ROOT / "build/phase01b2/report.json"),
        "population": rum["population"],
        "freed_starting_people": new_status["peasants"],
        "remaining_slave_pop_type": new_status["slaves"],
        "building_levels": rum["building_levels"],
        "explicit_bureaucracy_capacity": audit["country_capacity"]["country_bureaucracy_add"],
        "explicit_innovation_capacity": audit["country_capacity"]["country_weekly_innovation_add"],
        "unchanged_other_countries": len(report["countries"]) - 1,
        "additional_warnings": [],
        "runtime_tested": False,
        "playable_release": False,
        "remaining_engine_gates": [
            "confirm whether history activate_law emits a recent-emancipation variable during setup",
            "measure employment, qualifications, infrastructure, prices and government budget",
            "create military and government interest-group setup",
            "finish the other twelve regional countries and split-state hubs",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
