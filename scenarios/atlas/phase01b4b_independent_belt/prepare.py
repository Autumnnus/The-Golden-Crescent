"""Derive the cumulative Phase 1B.4B independent-belt preview from 1B.4A."""

from __future__ import annotations

import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "phase01b4a_nizam_subjects"
PARENT_SCENARIO = PARENT / "scenario.json"
PARENT_POPS = ROOT / "build/phase01b4a/generated/common/history/pops/tgc_pops.txt"
COUNTRIES = ("KUR", "BSR", "SYR", "LEB", "PAL", "KUW")


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


GOV_HEREDITARY = ("pm_simple_organization", "pm_hereditary_bureaucrats", "pm_religious_bureaucrats")
GOV_PROFESSIONAL = ("pm_simple_organization", "pm_professional_bureaucrats", "pm_religious_bureaucrats")
GOV_SECULAR = ("pm_simple_organization", "pm_professional_bureaucrats", "pm_secular_bureaucrats")
UNIVERSITY_RELIGIOUS = ("pm_scholastic_education", "pm_religious_academia")
UNIVERSITY_SECULAR = ("pm_scholastic_education", "pm_secular_academia")
CONSTRUCTION = ("pm_wooden_buildings",)
TOOLS = ("pm_pig_iron", "pm_automation_disabled")
ARMS = ("pm_muskets", "pm_automation_disabled")
TEXTILE = ("pm_handsewn_clothes", "pm_no_luxury_clothes", "pm_traditional_looms")
PAPER = ("pm_pulp_pressing", "pm_automation_disabled")
FOOD = ("pm_bakery", "pm_disabled_distillery", "pm_manual_dough_processing")
GLASS = ("pm_forest_glass", "pm_manual_glassblowing")
COAL = ("pm_atmospheric_engine_pump_building_coal_mine", "pm_no_explosives", "pm_no_steam_automation", "pm_road_carts")
IRON = ("pm_atmospheric_engine_pump_building_iron_mine", "pm_no_explosives", "pm_no_steam_automation", "pm_road_carts")
SULFUR = ("pm_atmospheric_engine_pump_building_sulfur_mine", "pm_no_explosives", "pm_no_steam_automation", "pm_road_carts")
LOG_SOFT = ("pm_saw_mills", "pm_no_hardwood", "pm_no_equipment", "pm_road_carts")
LOG_HARD = ("pm_saw_mills", "pm_hardwood", "pm_no_equipment", "pm_road_carts")
GRAIN = ("pm_simple_farming", "pm_no_secondary", "pm_tools_disabled")
RICE = ("pm_simple_farming_building_rice_farm", "pm_no_secondary", "pm_tools_disabled")
LIVESTOCK = ("pm_open_air_stockyards", "pm_simple_ranch", "pm_standard_fences", "pm_unrefrigerated")
COTTON = ("default_building_cotton_plantation", "pm_road_carts")
SILK = ("default_building_silk_plantation", "pm_road_carts")
PORT = ("pm_basic_port",)
FISH = ("pm_simple_fishing", "pm_unrefrigerated")
SHIPYARD = ("pm_basic_shipbuilding",)


POPULATION = {
    "STATE_MOSUL": {"KUR": (750_000, 0.30)},
    "STATE_DIYARBAKIR": {"KUR": (950_000, 0.28)},
    "STATE_BASRA": {"BSR": (320_000, 0.42), "KUW": (120_000, 0.30)},
    "STATE_SYRIA": {"SYR": (1_050_000, 0.37)},
    "STATE_TRANSJORDAN": {"SYR": (120_000, 0.20)},
    "STATE_LEBANON": {"LEB": (560_000, 0.43)},
    "STATE_PALESTINE": {"PAL": (650_000, 0.36)},
}


INDUSTRY = {
    "STATE_MOSUL": {"KUR": {
        "building_government_administration": building(4, *GOV_HEREDITARY, ownership="government"),
        "building_university": building(2, *UNIVERSITY_RELIGIOUS, ownership="government"),
        "building_construction_sector": building(1, *CONSTRUCTION, ownership="government"),
        "building_tooling_workshop": building(3, *TOOLS),
        "building_arms_industry": building(2, *ARMS),
        "building_sulfur_mine": building(8, *SULFUR),
        "building_wheat_farm": building(6, *GRAIN),
        "building_livestock_ranch": building(5, *LIVESTOCK),
        "building_cotton_plantation": building(3, *COTTON),
        "building_tobacco_plantation": 2,
    }},
    "STATE_DIYARBAKIR": {"KUR": {
        "building_government_administration": building(2, *GOV_HEREDITARY, ownership="government"),
        "building_university": building(1, *UNIVERSITY_RELIGIOUS, ownership="government"),
        "building_textile_mill": building(3, *TEXTILE),
        "building_coal_mine": building(8, *COAL),
        "building_wheat_farm": building(6, *GRAIN),
        "building_livestock_ranch": building(4, *LIVESTOCK),
        "building_cotton_plantation": building(4, *COTTON),
        "building_tobacco_plantation": 2,
        "building_vineyard": 2,
        "building_tea_plantation": 0,
    }},
    "STATE_BASRA": {
        "BSR": {
            "building_government_administration": building(3, *GOV_SECULAR, ownership="government"),
            "building_university": building(2, *UNIVERSITY_SECULAR, ownership="government"),
            "building_construction_sector": building(1, *CONSTRUCTION, ownership="government"),
            "building_tooling_workshop": building(2, *TOOLS),
            "building_arms_industry": building(1, *ARMS),
            "building_shipyard": building(2, *SHIPYARD),
            "building_paper_mill": building(4, *PAPER),
            "building_food_industry": building(3, *FOOD),
            "building_textile_mill": building(2, *TEXTILE),
        },
        "KUW": {
            "building_port": building(4, *PORT),
            "building_fishing_wharf": building(4, *FISH),
            "building_shipyard": building(1, *SHIPYARD),
        },
    },
    "STATE_SYRIA": {"SYR": {
        "building_government_administration": building(5, *GOV_HEREDITARY, ownership="government"),
        "building_university": building(3, *UNIVERSITY_RELIGIOUS, ownership="government"),
        "building_construction_sector": building(1, *CONSTRUCTION, ownership="government"),
        "building_tooling_workshop": building(3, *TOOLS),
        "building_textile_mill": building(5, *TEXTILE),
        "building_glassworks": building(3, *GLASS),
        "building_paper_mill": building(3, *PAPER),
        "building_arms_industry": building(2, *ARMS),
        "building_millet_farm": building(8, *GRAIN),
        "building_livestock_ranch": building(5, *LIVESTOCK),
        "building_cotton_plantation": building(4, *COTTON),
        "building_silk_plantation": building(3, *SILK),
        "building_tobacco_plantation": 3,
        "building_vineyard": 2,
        "building_logging_camp": building(2, *LOG_SOFT),
    }},
    "STATE_TRANSJORDAN": {"SYR": {
        "building_government_administration": building(1, *GOV_HEREDITARY, ownership="government"),
        "building_sulfur_mine": building(3, *SULFUR),
        "building_millet_farm": building(2, *GRAIN),
        "building_livestock_ranch": building(1, *LIVESTOCK),
        "building_port": building(1, *PORT),
        "building_fishing_wharf": 0,
    }},
    "STATE_LEBANON": {"LEB": {
        "building_government_administration": building(3, *GOV_PROFESSIONAL, ownership="government"),
        "building_university": building(2, *UNIVERSITY_RELIGIOUS, ownership="government"),
        "building_construction_sector": building(1, *CONSTRUCTION, ownership="government"),
        "building_tooling_workshop": building(2, *TOOLS),
        "building_textile_mill": building(3, *TEXTILE),
        "building_paper_mill": building(2, *PAPER),
        "building_food_industry": building(2, *FOOD),
        "building_shipyard": building(2, *SHIPYARD),
        "building_coal_mine": building(6, *COAL),
        "building_logging_camp": building(3, *LOG_HARD),
        "building_port": building(4, *PORT),
        "building_fishing_wharf": building(3, *FISH),
        "building_millet_farm": building(3, *GRAIN),
        "building_silk_plantation": building(3, *SILK),
        "building_vineyard": 2,
    }},
    "STATE_PALESTINE": {"PAL": {
        "building_government_administration": building(3, *GOV_PROFESSIONAL, ownership="government"),
        "building_university": building(2, *UNIVERSITY_RELIGIOUS, ownership="government"),
        "building_construction_sector": building(1, *CONSTRUCTION, ownership="government"),
        "building_tooling_workshop": building(2, *TOOLS),
        "building_glassworks": building(3, *GLASS),
        "building_paper_mill": building(1, *PAPER),
        "building_arms_industry": building(1, *ARMS),
        "building_iron_mine": building(6, *IRON),
        "building_sulfur_mine": building(3, *SULFUR),
        "building_logging_camp": building(3, *LOG_HARD),
        "building_port": building(3, *PORT),
        "building_fishing_wharf": building(3, *FISH),
        "building_millet_farm": building(4, *GRAIN),
        "building_livestock_ranch": building(3, *LIVESTOCK),
        "building_cotton_plantation": building(1, *COTTON),
        "building_tobacco_plantation": 1,
        "building_vineyard": 2,
    }},
}


H8_COMMON = [
    "law_monarchy", "law_autocracy", "law_hereditary_bureaucrats", "law_subjecthood",
    "law_state_religion", "law_peasant_levies", "law_merchant_navy", "law_traditionalism",
    "law_mercantilism", "law_land_based_taxation", "law_tenant_farmers", "law_no_colonial_affairs",
    "law_local_police", "law_no_home_affairs", "law_religious_schools", "law_no_health_system",
    "law_no_workers_rights", "law_child_labor_allowed", "law_women_in_the_fields", "law_no_social_security",
    "law_migration_controls", "law_censorship", "law_anti_strike_laws", "law_debt_slavery",
]

H7_BASRA = [
    "law_presidential_republic", "law_oligarchy", "law_elected_bureaucrats", "law_subjecthood",
    "law_freedom_of_conscience", "law_professional_army", "law_merchant_navy", "law_laissez_faire",
    "law_free_trade", "law_consumption_based_taxation", "law_tenant_farmers", "law_no_colonial_affairs",
    "law_local_police", "law_no_home_affairs", "law_private_schools", "law_charitable_health_system",
    "law_no_workers_rights", "law_child_labor_allowed", "law_women_own_property", "law_no_social_security",
    "law_no_migration_controls", "law_censorship", "law_anti_strike_laws", "law_slavery_banned",
]


def h8_variant(tag: str):
    laws = list(H8_COMMON)
    if tag in {"LEB", "KUW"}:
        laws[laws.index("law_autocracy")] = "law_oligarchy"
    if tag in {"LEB", "PAL"}:
        laws[laws.index("law_hereditary_bureaucrats")] = "law_appointed_bureaucrats"
    if tag == "PAL":
        laws[laws.index("law_state_religion")] = "law_freedom_of_conscience"
    return laws


LAWS = {tag: h8_variant(tag) for tag in ("KUR", "SYR", "LEB", "PAL", "KUW")}
LAWS["BSR"] = H7_BASRA

RULING = {
    "KUR": ["ig_landowners", "ig_armed_forces"],
    "BSR": ["ig_industrialists", "ig_petty_bourgeoisie"],
    "SYR": ["ig_landowners", "ig_devout"],
    "LEB": ["ig_landowners", "ig_petty_bourgeoisie"],
    "PAL": ["ig_devout", "ig_landowners"],
    "KUW": ["ig_landowners", "ig_petty_bourgeoisie"],
}


def army(name, hq, state, irregular, hussars, cannon):
    units = [{"type": "combat_unit_type_irregular_infantry", "state": state, "count": irregular}]
    if hussars:
        units.append({"type": "combat_unit_type_hussars", "state": state, "count": hussars})
    if cannon:
        units.append({"type": "combat_unit_type_cannon_artillery", "state": state, "count": cannon})
    return {"name": name, "type": "army", "hq_region": hq, "units": units}


def fleet(name, hq, state, count):
    return {"name": name, "type": "fleet", "hq_region": hq, "ships": [{"type": "ship_type_frigate", "state": state, "count": count}]}


FORMATIONS = {
    "KUR": [army("Dicle Serhad Kuvveti", "region_near_east", "STATE_MOSUL", 16, 4, 2)],
    "BSR": [
        {"name": "Basra Muhafizlari", "type": "army", "hq_region": "region_near_east", "units": [
            {"type": "combat_unit_type_line_infantry", "state": "STATE_BASRA", "count": 6},
            {"type": "combat_unit_type_hussars", "state": "STATE_BASRA", "count": 1},
            {"type": "combat_unit_type_cannon_artillery", "state": "STATE_BASRA", "count": 1}]},
        fleet("Sattularap Filosu", "region_near_east", "STATE_BASRA", 3),
    ],
    "SYR": [army("Sam Kervan Ordusu", "region_near_east", "STATE_SYRIA", 12, 2, 2)],
    "LEB": [army("Cebel Muhafizlari", "region_near_east", "STATE_LEBANON", 6, 1, 1), fleet("Beyrut Filosu", "region_near_east", "STATE_LEBANON", 3)],
    "PAL": [army("Kudus Muhafizlari", "region_near_east", "STATE_PALESTINE", 8, 1, 1), fleet("Akka Filosu", "region_near_east", "STATE_PALESTINE", 3)],
    "KUW": [army("Kuveyt Muhafizlari", "region_near_east", "STATE_BASRA", 3, 1, 0), fleet("Kuveyt Filosu", "region_near_east", "STATE_BASRA", 4)],
}


def compiled_pops():
    local = load(ROOT / ".vic3-tools.local.json")
    sys.path.insert(0, str(Path(local["toolkit"]) / "src"))
    from vic3 import pdx

    root = pdx.parse_file(PARENT_POPS).get_node("POPS")
    result = {}
    for state_key, state_node in root.pairs():
        state = state_key.removeprefix("s:")
        for tag in COUNTRIES:
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


def composition(rows, emancipate: bool):
    total = sum(row["size"] for row in rows)
    result, running = [], Decimal(0)
    for index, row in enumerate(rows):
        share = Decimal(1) - running if index == len(rows) - 1 else (Decimal(row["size"]) / Decimal(total)).quantize(Decimal("0.000000000001"))
        running += share
        item = {"culture": row["culture"], "religion": row["religion"], "share": float(share)}
        if row.get("pop_type"):
            item["pop_type"] = "peasants" if emancipate and row["pop_type"] == "slaves" else row["pop_type"]
        result.append(item)
    return result


def main():
    accepted = load(PARENT / "verification.json")
    if accepted["scenario_sha256"] != sha256(PARENT_SCENARIO):
        raise SystemExit("Faz 1B.4A kaynağı değişmiş; önce 1B.4A'yı yeniden doğrula.")
    scenario = load(PARENT_SCENARIO)
    pops = compiled_pops()
    expected = {(state, tag) for state, owners in POPULATION.items() for tag in owners}
    if set(pops) != expected:
        raise SystemExit("Bağımsız kuşak POP kapsamı beklenen eyalet/sahip listesiyle eşleşmiyor.")

    freed_basra = 0
    retained = 0
    for state, owners in POPULATION.items():
        state_population = scenario["states"][state].setdefault("population", {}).setdefault("by_owner", {})
        for tag, (total, literacy) in owners.items():
            rows = pops[state, tag]
            slaves = sum(row["size"] for row in rows if row.get("pop_type") == "slaves")
            if tag == "BSR":
                freed_basra += slaves
            else:
                retained += slaves
            state_population[tag] = {
                "total": total,
                "literacy": literacy,
                "composition": composition(rows, emancipate=tag == "BSR"),
            }

    for state, owners in INDUSTRY.items():
        by_owner = scenario["states"][state].setdefault("industry", {}).setdefault("by_owner", {})
        for tag, buildings in owners.items():
            by_owner[tag] = {"mode": "merge", "buildings": buildings}

    for tag in COUNTRIES:
        country = scenario["countries"][tag]
        country["phase"] = "1B.4B"
        country["history_mode"] = "replace"
        additions = ["academia", "artillery", "atmospheric_engine", "law_enforcement"]
        if tag == "BSR":
            additions += ["democracy", "law_enforcement", "line_infantry", "medical_degrees", "romanticism"]
        country["technology"] = {"mode": "replace", "tier": 4, "add": additions}
        country["laws"] = {"mode": "replace", "values": LAWS[tag]}
        institutions = {"institution_schools": 1, "institution_police": 1}
        if tag == "BSR":
            institutions["institution_health_system"] = 1
        country["institutions"] = institutions
        country["interest_groups"] = {"mode": "replace", "ruling": RULING[tag], "strength": {}}
        country["military"] = {"mode": "replace", "formations": FORMATIONS[tag]}
        country["notes"] = (
            "1B.4B preview: explicit independent-belt demography, literacy, written H7/H8-derived laws, "
            "local economy and bounded formations. Treaty guarantees, markets and hub limits are not invented."
        )

    scenario["title"] = "The Golden Crescent - Phase 1B.4B: Independent Middle Eastern Belt"
    scenario["description"] = (
        "PREVIEW ONLY. KUR, BSR, SYR, LEB, PAL and KUW receive explicit joint culture/religion POPs, "
        "literacy, H7/H8-derived institutions and laws, governments, complementary economies and bounded "
        "forces. Basra abolishes inherited slave status; the five H8 states retain their written debt/domestic "
        "slavery baseline. No subject relation or automatic guarantee is added."
    )

    totals = {tag: sum(total for owners in POPULATION.values() for owner, (total, _) in owners.items() if owner == tag) for tag in COUNTRIES}
    plan = {
        "phase": "1B.4B",
        "parent_scenario_sha256": sha256(PARENT_SCENARIO),
        "parent_pops_sha256": sha256(PARENT_POPS),
        "countries": {tag: {"population": totals[tag], "laws": LAWS[tag], "ruling_interest_groups": RULING[tag], "formations": FORMATIONS[tag]} for tag in COUNTRIES},
        "population_by_state": {state: {tag: {"total": total, "literacy": literacy} for tag, (total, literacy) in owners.items()} for state, owners in POPULATION.items()},
        "freed_inherited_slave_status_basra": freed_basra,
        "retained_inherited_slave_status_h8": retained,
        "industry": INDUSTRY,
        "design_limits": {
            "diplomacy": "all six remain independent; the 1712 and 1804 treaty guarantees are not reducible to an automatic subject relation",
            "basra_kuwait_hub": "one vanilla STATE_BASRA port hub belongs to KUW while the city hub belongs to BSR; Atlas cannot create two port hubs inside one state region",
            "market": "complementary capacity and dependencies are directional; tariffs, routes, convoys and prices need engine testing",
            "politics": "ruling IG membership is explicit; clout and legitimacy are runtime outcomes",
            "slavery": "Basra emancipation and H8 debt-slavery starting effects require runtime verification",
        },
    }
    (HERE / "scenario.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n")
    (HERE / "belt-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(HERE / "scenario.json")
    print(HERE / "belt-plan.json")
    print(f"Basra freed status: {freed_basra:,}; H8 retained status: {retained:,}")


if __name__ == "__main__":
    main()
