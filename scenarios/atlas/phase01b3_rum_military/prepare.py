"""Derive the cumulative Phase 1B.3 Rûm military preview from Phase 1B.2.

This helper writes only the preview source and its design record next to itself.
It does not activate ``world/`` or install generated content into the mod.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "phase01b2_rum_economy"
PARENT_SCENARIO = PARENT / "scenario.json"
PARENT_REPORT = ROOT / "build/phase01b2/report.json"


def load(path: Path):
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


CHEMICAL_PMS = ("pm_artificial_fertilizers",)
EXPLOSIVES_PMS = ("pm_leblanc_process",)
ARTILLERY_PMS = ("pm_cannons", "pm_automation_disabled")
MUNITION_PMS = ("pm_percussion_caps", "pm_automation_disabled")

TECHNOLOGIES = {"general_staff", "napoleonic_warfare"}

RULING_INTEREST_GROUPS = [
    "ig_landowners",
    "ig_armed_forces",
    "ig_intelligentsia",
]

FORMATIONS = [
    {
        "name": "Balkan Ordusu",
        "type": "army",
        "hq_region": "region_balkans",
        "units": [
            {"type": "combat_unit_type_skirmish_infantry", "state": "STATE_EASTERN_THRACE", "count": 50},
            {"type": "combat_unit_type_hussars", "state": "STATE_EASTERN_THRACE", "count": 8},
            {"type": "combat_unit_type_mobile_artillery", "state": "STATE_EASTERN_THRACE", "count": 8},
        ],
    },
    {
        "name": "Anadolu Ordusu",
        "type": "army",
        "hq_region": "region_near_east",
        "units": [
            {"type": "combat_unit_type_skirmish_infantry", "state": "STATE_HUDAVENDIGAR", "count": 44},
            {"type": "combat_unit_type_hussars", "state": "STATE_HUDAVENDIGAR", "count": 7},
            {"type": "combat_unit_type_mobile_artillery", "state": "STATE_HUDAVENDIGAR", "count": 7},
        ],
    },
    {
        "name": "Irak ve Levant Ordusu",
        "type": "army",
        "hq_region": "region_near_east",
        "units": [
            {"type": "combat_unit_type_skirmish_infantry", "state": "STATE_BAGHDAD", "count": 26},
            {"type": "combat_unit_type_hussars", "state": "STATE_BAGHDAD", "count": 5},
            {"type": "combat_unit_type_mobile_artillery", "state": "STATE_BAGHDAD", "count": 5},
        ],
    },
    {
        "name": "Marmara Donanmasi",
        "type": "fleet",
        "hq_region": "region_balkans",
        "ships": [
            {"type": "ship_type_ship_of_the_line", "state": "STATE_EASTERN_THRACE", "count": 12},
            {"type": "ship_type_frigate", "state": "STATE_EASTERN_THRACE", "count": 14},
        ],
    },
    {
        "name": "Ege ve Levant Donanmasi",
        "type": "fleet",
        "hq_region": "region_near_east",
        "ships": [
            {"type": "ship_type_ship_of_the_line", "state": "STATE_HUDAVENDIGAR", "count": 8},
            {"type": "ship_type_frigate", "state": "STATE_HUDAVENDIGAR", "count": 14},
        ],
    },
]


def building(level: int, production_methods: tuple[str, ...]):
    return {"level": level, "production_methods": list(production_methods)}


def rum_buildings(scenario, state: str):
    return scenario["states"][state]["industry"]["by_owner"]["RUM"]["buildings"]


def main():
    accepted = load(PARENT / "verification.json")
    if accepted["scenario_sha256"] != sha256(PARENT_SCENARIO):
        raise SystemExit("Faz 1B.2 kaynağı doğrulama kaydından sonra değişmiş; önce 1B.2'yi yeniden doğrula.")
    if not PARENT_REPORT.exists():
        raise SystemExit("Faz 1B.2 raporu yok; önce 1B.2 README komutlarını çalıştır.")

    scenario = load(PARENT_SCENARIO)
    parent_report = load(PARENT_REPORT)

    # Current Victoria 3 separates fertilizer and explosives into two buildings.
    # Keep their production-method groups distinct and feed the early ammunition chain.
    capital = rum_buildings(scenario, "STATE_EASTERN_THRACE")
    capital["building_chemical_plant"]["level"] = 8
    capital["building_explosives_factory"] = building(3, EXPLOSIVES_PMS)
    capital["building_artillery_foundry"] = building(3, ARTILLERY_PMS)
    capital["building_munition_plant"] = building(5, MUNITION_PMS)
    rum_buildings(scenario, "STATE_SKOPIA")["building_iron_mine"]["level"] = 32

    rum = scenario["countries"]["RUM"]
    rum["phase"] = "1B.3"
    rum["technology"]["add"] = sorted(set(rum["technology"].get("add", [])) | TECHNOLOGIES)
    rum["interest_groups"] = {
        "mode": "replace",
        "ruling": RULING_INTEREST_GROUPS,
        "strength": {},
    }
    rum["military"] = {"mode": "replace", "formations": FORMATIONS}
    rum["notes"] = (
        "1B.3 preview: the palace-estate, central army and professional bureaucracy form the "
        "starting government; urban industrialists support it without a cabinet seat. A 160-battalion "
        "professional army and 48-ship Mediterranean fleet have an explicit domestic arms, ammunition "
        "and artillery supply chain. Atlas cannot set opening treasury or debt, so the documented war "
        "debt remains an engine/tool gate while military wages and materiel create real running pressure."
    )
    scenario["title"] = "The Golden Crescent - Phase 1B.3: Rum Armed State"
    scenario["description"] = (
        "PREVIEW ONLY. Cumulative Phase 1A/1B.1/1B.2 source. RUM fields a 160-battalion professional "
        "army and a 48-ship Mediterranean fleet, backed by explicitly selected artillery, ammunition, "
        "explosives, sulfur and iron capacity. The palace-estate, armed forces and professional "
        "bureaucratic reformers begin in government. Starting debt is documented but not fabricated "
        "because Atlas has no treasury/debt scenario field."
    )

    comparisons = {}
    for tag in ("EGY", "AUS", "PRU", "FRA", "GBR"):
        country = parent_report["countries"][tag]
        comparisons[tag] = {
            "population": country["population"],
            "battalions": country["military"]["battalions"],
            "ships": country["military"]["ships"],
        }

    plan = {
        "phase": "1B.3",
        "parent_scenario_sha256": sha256(PARENT_SCENARIO),
        "parent_report_sha256": sha256(PARENT_REPORT),
        "government": {
            "ruling_interest_groups": RULING_INTEREST_GROUPS,
            "interpretation": {
                "ig_landowners": "hanedan sarayı ve merkezle uzlaşmış mülk sahibi seçkinler",
                "ig_armed_forces": "merkez profesyonel ordusu",
                "ig_intelligentsia": "meslek bürokrasisi, hukukçu ve teknik reform kadroları",
                "ig_industrialists": "gümrük koruması karşılığında dışarıdan destek; başlangıç kabinesinde değil",
            },
            "strength_modifiers": "none; Atlas absolute clout does not simulate POP wealth, ownership or leaders",
        },
        "military": {
            "formations": FORMATIONS,
            "totals": {
                "battalions": 160,
                "ships": 48,
                "army_composition": {
                    "combat_unit_type_skirmish_infantry": 120,
                    "combat_unit_type_hussars": 20,
                    "combat_unit_type_mobile_artillery": 20,
                },
                "fleet_composition": {"ship_type_ship_of_the_line": 20, "ship_type_frigate": 28},
            },
            "vanilla_comparisons_from_parent_report": comparisons,
        },
        "industry_changes": {
            "STATE_EASTERN_THRACE": {
                "building_chemical_plant": building(8, CHEMICAL_PMS),
                "building_explosives_factory": building(3, EXPLOSIVES_PMS),
                "building_artillery_foundry": building(3, ARTILLERY_PMS),
                "building_munition_plant": building(5, MUNITION_PMS),
            },
            "STATE_SKOPIA": {"building_iron_mine": {"level": 32}},
        },
        "technology_additions": sorted(TECHNOLOGIES),
        "fiscal_pressure": {
            "represented": [
                "standing formation manpower and ship crews",
                "military wages and materiel demanded by the engine",
                "domestic arms, ammunition, artillery and explosive production capacity",
            ],
            "not_represented": [
                "opening debt principal",
                "opening treasury balance",
                "interest rate or scripted repayment schedule",
            ],
            "reason": "Atlas V2 country schema has no treasury, debt, budget or raw-effect field",
        },
        "engine_gates": [
            "measure employment, military wages, goods prices and opening budget",
            "measure legitimacy and clout produced by the three-IG government",
            "confirm formation names, headquarters and naval readiness in the current game build",
            "decide whether Atlas needs an explicit safe starting-debt contract",
        ],
    }

    (HERE / "scenario.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n")
    (HERE / "military-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(HERE / "scenario.json")
    print(HERE / "military-plan.json")


if __name__ == "__main__":
    main()
