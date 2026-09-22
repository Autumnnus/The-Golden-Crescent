"""Derive the cumulative Phase 1B.4A six-subject preview from Phase 1B.3."""

from __future__ import annotations

import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "phase01b3_rum_military"
PARENT_SCENARIO = PARENT / "scenario.json"
PARENT_POPS = ROOT / "build/phase01b3/generated/common/history/pops/tgc_pops.txt"
SUBJECTS = ("BOS", "ALB", "BUL", "ADA", "ERZ", "TRB")


def load(path: Path):
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def building(level: int, *production_methods: str, ownership: str | None = None):
    if not production_methods and ownership is None:
        return level
    result = {"level": level}
    if production_methods:
        result["production_methods"] = list(production_methods)
    if ownership:
        result["ownership"] = ownership
    return result


GOVERNMENT = ("pm_simple_organization", "pm_professional_bureaucrats", "pm_religious_bureaucrats")
UNIVERSITY = ("pm_scholastic_education", "pm_religious_academia")
CONSTRUCTION = ("pm_wooden_buildings",)
TOOLS = ("pm_pig_iron", "pm_automation_disabled")
ARMS = ("pm_muskets", "pm_automation_disabled")
ARTILLERY = ("pm_cannons", "pm_automation_disabled")
TEXTILE = ("pm_handsewn_clothes", "pm_no_luxury_clothes", "pm_traditional_looms")
FOOD = ("pm_bakery", "pm_disabled_distillery", "pm_manual_dough_processing")
IRON = ("pm_atmospheric_engine_pump_building_iron_mine", "pm_no_explosives", "pm_no_steam_automation", "pm_road_carts")
LEAD = ("pm_atmospheric_engine_pump_building_lead_mine", "pm_no_explosives", "pm_no_steam_automation", "pm_road_carts")
COAL = ("pm_atmospheric_engine_pump_building_coal_mine", "pm_no_explosives", "pm_no_steam_automation", "pm_road_carts")
LOG_SOFT = ("pm_saw_mills", "pm_no_hardwood", "pm_no_equipment", "pm_road_carts")
LOG_HARD = ("pm_saw_mills", "pm_hardwood", "pm_no_equipment", "pm_road_carts")
WHEAT = ("pm_simple_farming", "pm_no_secondary", "pm_tools_disabled")
LIVESTOCK = ("pm_open_air_stockyards", "pm_simple_ranch", "pm_standard_fences", "pm_unrefrigerated")
COTTON = ("default_building_cotton_plantation", "default_labour", "pm_road_carts")
PORT = ("pm_basic_port",)
FISH = ("pm_simple_fishing", "pm_unrefrigerated")
SHIPYARD = ("pm_basic_shipbuilding",)


POPULATION = {
    "STATE_BOSNIA": {"BOS": (950_000, 0.31)},
    "STATE_ALBANIA": {"ALB": (1_165_000, 0.27)},
    "STATE_KOSOVO": {"ALB": (285_000, 0.22)},
    "STATE_BULGARIA": {"BUL": (950_000, 0.34)},
    "STATE_NORTHERN_THRACE": {"BUL": (900_000, 0.30)},
    "STATE_DOBRUDJA": {"BUL": (250_000, 0.27)},
    "STATE_ADANA": {"ADA": (550_000, 0.32)},
    "STATE_ERZURUM": {"ERZ": (630_000, 0.27)},
    "STATE_KARS": {"ERZ": (170_000, 0.24)},
    "STATE_TRABZON": {"TRB": (700_000, 0.38)},
}


INDUSTRY = {
    "STATE_BOSNIA": {"BOS": {
        "building_government_administration": building(3, *GOVERNMENT, ownership="government"),
        "building_university": building(1, *UNIVERSITY, ownership="government"),
        "building_construction_sector": building(1, *CONSTRUCTION, ownership="government"),
        "building_tooling_workshop": building(3, *TOOLS),
        "building_arms_industry": building(2, *ARMS),
        "building_artillery_foundry": building(1, *ARTILLERY),
        "building_iron_mine": building(8, *IRON),
        "building_lead_mine": building(3, *LEAD),
        "building_logging_camp": building(6, *LOG_HARD),
        "building_wheat_farm": building(4, *WHEAT),
        "building_livestock_ranch": building(3, *LIVESTOCK),
    }},
    "STATE_ALBANIA": {"ALB": {
        "building_government_administration": building(3, *GOVERNMENT, ownership="government"),
        "building_university": building(1, *UNIVERSITY, ownership="government"),
        "building_construction_sector": building(1, *CONSTRUCTION, ownership="government"),
        "building_textile_mill": building(3, *TEXTILE),
        "building_arms_industry": building(1, *ARMS),
        "building_iron_mine": building(5, *IRON),
        "building_logging_camp": building(5, *LOG_SOFT),
        "building_port": building(2, *PORT),
        "building_fishing_wharf": building(3, *FISH),
        "building_wheat_farm": building(6, *WHEAT),
        "building_livestock_ranch": building(5, *LIVESTOCK),
    }},
    "STATE_KOSOVO": {"ALB": {
        "building_coal_mine": building(4, *COAL),
        "building_lead_mine": building(3, *LEAD),
        "building_logging_camp": building(2, *LOG_HARD),
        "building_wheat_farm": building(4, *WHEAT),
        "building_livestock_ranch": building(4, *LIVESTOCK),
    }},
    "STATE_BULGARIA": {"BUL": {
        "building_government_administration": building(4, *GOVERNMENT, ownership="government"),
        "building_university": building(2, *UNIVERSITY, ownership="government"),
        "building_construction_sector": building(1, *CONSTRUCTION, ownership="government"),
        "building_tooling_workshop": building(3, *TOOLS),
        "building_arms_industry": building(2, *ARMS),
        "building_artillery_foundry": building(1, *ARTILLERY),
        "building_furniture_manufactory": 4,
        "building_port": building(2, *PORT),
        "building_wheat_farm": building(8, *WHEAT),
        "building_livestock_ranch": building(3, *LIVESTOCK),
        "building_logging_camp": building(7, *LOG_HARD),
        "building_vineyard": 2,
    }},
    "STATE_NORTHERN_THRACE": {"BUL": {
        "building_textile_mill": building(4, *TEXTILE),
        "building_furniture_manufactory": 3,
        "building_iron_mine": building(8, *IRON),
        "building_logging_camp": building(6, *LOG_HARD),
        "building_wheat_farm": building(6, *WHEAT),
        "building_tobacco_plantation": 4,
        "building_vineyard": 1,
    }},
    "STATE_DOBRUDJA": {"BUL": {
        "building_port": building(2, *PORT),
        "building_fishing_wharf": building(3, *FISH),
        "building_logging_camp": building(2, *LOG_SOFT),
        "building_wheat_farm": building(3, *WHEAT),
    }},
    "STATE_ADANA": {"ADA": {
        "building_government_administration": building(2, *GOVERNMENT, ownership="government"),
        "building_university": building(1, *UNIVERSITY, ownership="government"),
        "building_construction_sector": building(1, *CONSTRUCTION, ownership="government"),
        "building_textile_mill": building(3, *TEXTILE),
        "building_food_industry": building(2, *FOOD),
        "building_arms_industry": building(1, *ARMS),
        "building_coal_mine": building(8, *COAL),
        "building_port": building(3, *PORT),
        "building_fishing_wharf": building(3, *FISH),
        "building_wheat_farm": building(3, *WHEAT),
        "building_livestock_ranch": building(3, *LIVESTOCK),
        "building_cotton_plantation": building(5, *COTTON),
    }},
    "STATE_ERZURUM": {"ERZ": {
        "building_government_administration": building(2, *GOVERNMENT, ownership="government"),
        "building_university": building(1, *UNIVERSITY, ownership="government"),
        "building_tooling_workshop": building(2, *TOOLS),
        "building_arms_industry": building(1, *ARMS),
        "building_iron_mine": building(6, *IRON),
        "building_lead_mine": building(4, *LEAD),
        "building_logging_camp": building(5, *LOG_HARD),
        "building_livestock_ranch": 0,
        "building_tea_plantation": 0,
    }},
    "STATE_KARS": {"ERZ": {
        "building_port": building(1, *PORT),
        "building_logging_camp": building(2, *LOG_SOFT),
        "building_wheat_farm": building(2, *WHEAT),
        "building_livestock_ranch": building(2, *LIVESTOCK),
        "building_tea_plantation": 0,
    }},
    "STATE_TRABZON": {"TRB": {
        "building_government_administration": building(2, *GOVERNMENT, ownership="government"),
        "building_university": building(1, *UNIVERSITY, ownership="government"),
        "building_tooling_workshop": building(1, *TOOLS),
        "building_arms_industry": building(1, *ARMS),
        "building_shipyard": building(2, *SHIPYARD),
        "building_food_industry": building(2, *FOOD),
        "building_iron_mine": building(6, *IRON),
        "building_logging_camp": building(5, *LOG_HARD),
        "building_port": building(3, *PORT),
        "building_fishing_wharf": building(3, *FISH),
        "building_livestock_ranch": 0,
        "building_tea_plantation": 0,
    }},
}


BASE_LAWS = [
    "law_monarchy", "law_wealth_voting", "law_appointed_bureaucrats", "law_subjecthood",
    "law_freedom_of_conscience", "law_professional_army", "law_merchant_navy",
    "law_agrarianism", "law_mercantilism", "law_land_based_taxation", "law_tenant_farmers",
    "law_no_colonial_affairs", "law_local_police", "law_no_home_affairs",
    "law_religious_schools", "law_charitable_health_system", "law_no_workers_rights",
    "law_restricted_child_labor", "law_women_own_property", "law_no_social_security",
    "law_migration_controls", "law_censorship", "law_anti_strike_laws", "law_slavery_banned",
]

RULING = {
    "BOS": ["ig_landowners", "ig_armed_forces"],
    "ALB": ["ig_landowners", "ig_armed_forces"],
    "BUL": ["ig_landowners", "ig_devout"],
    "ADA": ["ig_landowners", "ig_industrialists"],
    "ERZ": ["ig_landowners", "ig_armed_forces"],
    "TRB": ["ig_landowners", "ig_petty_bourgeoisie"],
}

FORMATIONS = {
    "BOS": [{"name": "Bosna Muhafizlari", "type": "army", "hq_region": "region_balkans", "units": [
        {"type": "combat_unit_type_line_infantry", "state": "STATE_BOSNIA", "count": 7},
        {"type": "combat_unit_type_hussars", "state": "STATE_BOSNIA", "count": 2},
        {"type": "combat_unit_type_cannon_artillery", "state": "STATE_BOSNIA", "count": 1}] }],
    "ALB": [
        {"name": "Arnavutluk Kuvveti", "type": "army", "hq_region": "region_balkans", "units": [
            {"type": "combat_unit_type_line_infantry", "state": "STATE_ALBANIA", "count": 8},
            {"type": "combat_unit_type_hussars", "state": "STATE_KOSOVO", "count": 3},
            {"type": "combat_unit_type_cannon_artillery", "state": "STATE_ALBANIA", "count": 1}]},
        {"name": "Iskodra Filosu", "type": "fleet", "hq_region": "region_balkans", "ships": [
            {"type": "ship_type_frigate", "state": "STATE_ALBANIA", "count": 3}]},
    ],
    "BUL": [
        {"name": "Tuna Ordusu", "type": "army", "hq_region": "region_balkans", "units": [
            {"type": "combat_unit_type_line_infantry", "state": "STATE_BULGARIA", "count": 12},
            {"type": "combat_unit_type_hussars", "state": "STATE_NORTHERN_THRACE", "count": 3},
            {"type": "combat_unit_type_cannon_artillery", "state": "STATE_BULGARIA", "count": 3}]},
        {"name": "Tuna Filosu", "type": "fleet", "hq_region": "region_balkans", "ships": [
            {"type": "ship_type_frigate", "state": "STATE_DOBRUDJA", "count": 4}]},
    ],
    "ADA": [
        {"name": "Cukurova Kuvveti", "type": "army", "hq_region": "region_near_east", "units": [
            {"type": "combat_unit_type_line_infantry", "state": "STATE_ADANA", "count": 5},
            {"type": "combat_unit_type_hussars", "state": "STATE_ADANA", "count": 2},
            {"type": "combat_unit_type_cannon_artillery", "state": "STATE_ADANA", "count": 1}]},
        {"name": "Mersin Filosu", "type": "fleet", "hq_region": "region_near_east", "ships": [
            {"type": "ship_type_frigate", "state": "STATE_ADANA", "count": 3}]},
    ],
    "ERZ": [{"name": "Serhad Ordusu", "type": "army", "hq_region": "region_near_east", "units": [
        {"type": "combat_unit_type_line_infantry", "state": "STATE_ERZURUM", "count": 6},
        {"type": "combat_unit_type_hussars", "state": "STATE_KARS", "count": 3},
        {"type": "combat_unit_type_cannon_artillery", "state": "STATE_ERZURUM", "count": 1}] }],
    "TRB": [
        {"name": "Karadeniz Serhad Kuvveti", "type": "army", "hq_region": "region_near_east", "units": [
            {"type": "combat_unit_type_line_infantry", "state": "STATE_TRABZON", "count": 6},
            {"type": "combat_unit_type_hussars", "state": "STATE_TRABZON", "count": 1},
            {"type": "combat_unit_type_cannon_artillery", "state": "STATE_TRABZON", "count": 1}]},
        {"name": "Trabzon Filosu", "type": "fleet", "hq_region": "region_near_east", "ships": [
            {"type": "ship_type_frigate", "state": "STATE_TRABZON", "count": 4}]},
    ],
}


def compiled_pops():
    local = load(ROOT / ".vic3-tools.local.json")
    sys.path.insert(0, str(Path(local["toolkit"]) / "src"))
    from vic3 import pdx

    root = pdx.parse_file(PARENT_POPS).get_node("POPS")
    result = {}
    for state_key, state_node in root.pairs():
        state = state_key.removeprefix("s:")
        for tag in SUBJECTS:
            region = state_node.get_node(f"region_state:{tag}")
            if not region:
                continue
            rows = []
            for key, node in region.pairs():
                if key != "create_pop":
                    continue
                row = {"culture": node.get("culture"), "religion": node.get("religion"), "size": int(node.get("size"))}
                if node.get("pop_type"):
                    row["pop_type"] = node.get("pop_type")
                rows.append(row)
            result[state, tag] = rows
    return result


def composition(rows):
    total = sum(row["size"] for row in rows)
    result, running = [], Decimal(0)
    for index, row in enumerate(rows):
        share = Decimal(1) - running if index == len(rows) - 1 else (Decimal(row["size"]) / Decimal(total)).quantize(Decimal("0.000000000001"))
        running += share
        item = {"culture": row["culture"], "religion": row["religion"], "share": float(share)}
        if row.get("pop_type"):
            item["pop_type"] = "peasants" if row["pop_type"] == "slaves" else row["pop_type"]
        result.append(item)
    return result


def main():
    accepted = load(PARENT / "verification.json")
    if accepted["scenario_sha256"] != sha256(PARENT_SCENARIO):
        raise SystemExit("Faz 1B.3 kaynağı değişmiş; önce 1B.3'ü yeniden doğrula.")
    scenario = load(PARENT_SCENARIO)
    pops = compiled_pops()
    if set(pops) != {(state, tag) for state, owners in POPULATION.items() for tag in owners}:
        raise SystemExit("Nizam POP kapsamı beklenen eyalet/sahip listesiyle eşleşmiyor.")

    freed = 0
    for state, owners in POPULATION.items():
        state_population = scenario["states"][state].setdefault("population", {}).setdefault("by_owner", {})
        for tag, (total, literacy) in owners.items():
            rows = pops[state, tag]
            freed += sum(row["size"] for row in rows if row.get("pop_type") == "slaves")
            state_population[tag] = {"total": total, "literacy": literacy, "composition": composition(rows)}

    # The written atlas makes Trabzon city the atabegate capital. The Phase 1A
    # split accidentally left the city hub with RUM; move only that verified hex.
    split = scenario["states"]["STATE_TRABZON"]["split"]
    rum_row = next(row for row in split if row["owner"] == "RUM")
    trb_row = next(row for row in split if row["owner"] == "TRB")
    rum_row["provinces"].remove("x146DD9")
    trb_row["provinces"].append("x146DD9")
    trb_row["provinces"].sort()
    rum_trabzon = scenario["states"]["STATE_TRABZON"]["industry"]["by_owner"]["RUM"]["buildings"]
    rum_trabzon["building_government_administration"] = 0
    rum_trabzon["building_food_industry"] = 0

    for state, owners in INDUSTRY.items():
        by_owner = scenario["states"][state].setdefault("industry", {}).setdefault("by_owner", {})
        for tag, buildings in owners.items():
            by_owner[tag] = {"mode": "merge", "buildings": buildings}

    for tag in SUBJECTS:
        country = scenario["countries"][tag]
        country["phase"] = "1B.4A"
        country["history_mode"] = "replace"
        country["technology"] = {
            "mode": "replace",
            "tier": 4,
            "add": [
                "atmospheric_engine",
                "labor_movement",
                "law_enforcement",
                "line_infantry",
                "medical_degrees",
                "romanticism",
            ],
        }
        country["laws"] = {"mode": "replace", "values": BASE_LAWS}
        country["institutions"] = {"institution_schools": 1, "institution_police": 1}
        country["interest_groups"] = {"mode": "replace", "ruling": RULING[tag], "strength": {}}
        country["military"] = {"mode": "replace", "formations": FORMATIONS[tag]}
        country["notes"] = (
            "1B.4A preview: explicit Nizam demography, literacy, H1-derived local laws, ruling coalition, "
            "economic base and quota-scale professional formations. Subject treaty behavior remains the "
            "Phase 1A vassal-derived prototype and requires its own engine gate."
        )

    scenario["title"] = "The Golden Crescent - Phase 1B.4A: Six Nizam Dependencies"
    scenario["description"] = (
        "PREVIEW ONLY. BOS, ALB, BUL, ADA, ERZ and TRB receive explicit joint culture/religion POPs, "
        "literacy, H1-derived laws, institutions, governments, local economies and professional quota "
        "forces. Inherited slave-status POPs begin as peasants. Trabzon's verified city hub is corrected "
        "to its atabegate. Nizam treaty runtime behavior is still a prototype."
    )

    totals = {tag: sum(total for owners in POPULATION.values() for owner, (total, _) in owners.items() if owner == tag) for tag in SUBJECTS}
    plan = {
        "phase": "1B.4A",
        "parent_scenario_sha256": sha256(PARENT_SCENARIO),
        "parent_pops_sha256": sha256(PARENT_POPS),
        "countries": {
            tag: {
                "population": totals[tag],
                "ruling_interest_groups": RULING[tag],
                "formations": FORMATIONS[tag],
                "laws": BASE_LAWS,
            } for tag in SUBJECTS
        },
        "population_by_state": {state: {tag: {"total": total, "literacy": literacy} for tag, (total, literacy) in owners.items()} for state, owners in POPULATION.items()},
        "freed_inherited_slave_status": freed,
        "industry": INDUSTRY,
        "hub_correction": {
            "state": "STATE_TRABZON", "province": "x146DD9", "hub": "city",
            "from": "RUM", "to": "TRB", "reason": "Trabzon is the written and country-definition capital of TRB",
        },
        "design_limits": {
            "nizam": "income transfer and war joining remain the Phase 1A base-vassal prototype; fixed contribution and limited levy are not yet modeled",
            "market": "local capacity and dependencies are directional; customs separation and prices need engine testing",
            "politics": "ruling IG membership is explicit; clout and legitimacy are runtime outcomes",
            "characters": "rulers and commanders are Flavor/character work and are not invented by Atlas",
        },
    }
    (HERE / "scenario.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n")
    (HERE / "nizam-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(HERE / "scenario.json")
    print(HERE / "nizam-plan.json")
    print(f"freed inherited slave status: {freed:,}")


if __name__ == "__main__":
    main()
