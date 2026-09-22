"""Derive the cumulative 1B.2 Atlas source from the accepted 1B.1 preview.

This is a deterministic authoring helper, not an installer. It only rewrites the
two JSON files next to itself. Atlas build output remains under ``build/``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "phase01b_rum_demography"
PARENT_SCENARIO = PARENT / "scenario.json"
PARENT_POPS = ROOT / "build/phase01b/generated/common/history/pops/tgc_pops.txt"


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


GOVERNMENT_PMS = (
    "pm_horizontal_drawer_cabinets",
    "pm_professional_bureaucrats",
    "pm_religious_bureaucrats",
)
UNIVERSITY_PMS = ("pm_philosophy_department", "pm_religious_academia")
CONSTRUCTION_PMS = ("pm_iron_frame_buildings",)
TOOLING_PMS = ("pm_steel", "pm_automation_disabled")
STEEL_PMS = ("pm_blister_steel_process", "pm_automation_disabled")
TEXTILE_BASIC_PMS = ("pm_sewing_machines", "pm_no_luxury_clothes", "pm_mechanized_looms")
TEXTILE_LUXURY_PMS = ("pm_sewing_machines", "pm_craftsman_sewing", "pm_mechanized_looms")
PAPER_PMS = ("pm_sulfite_pulping", "pm_automation_disabled")
COAL_PMS = (
    "pm_atmospheric_engine_pump_building_coal_mine",
    "pm_no_explosives",
    "pm_no_steam_automation",
    "pm_road_carts",
)
IRON_PMS = (
    "pm_atmospheric_engine_pump_building_iron_mine",
    "pm_no_explosives",
    "pm_no_steam_automation",
    "pm_road_carts",
)
LEAD_PMS = (
    "pm_atmospheric_engine_pump_building_lead_mine",
    "pm_no_explosives",
    "pm_no_steam_automation",
    "pm_road_carts",
)
SULFUR_PMS = (
    "pm_atmospheric_engine_pump_building_sulfur_mine",
    "pm_no_explosives",
    "pm_no_steam_automation",
    "pm_road_carts",
)
RAILWAY_PMS = ("pm_early_trains", "pm_no_passenger_trains")
PORT_PMS = ("pm_basic_port",)
SHIPYARD_PMS = ("pm_complex_shipbuilding",)
MOTOR_PMS = ("pm_steam_engines", "pm_automation_disabled")
ARMS_PMS = ("pm_rifles", "pm_automation_disabled")
FOOD_PMS = ("pm_bakery", "pm_cannery", "pm_disabled_distillery", "pm_manual_dough_processing")
CHEMICAL_PMS = ("pm_artificial_fertilizers",)
LOGGING_SOFTWOOD_PMS = ("pm_saw_mills", "pm_no_hardwood", "pm_no_equipment", "pm_road_carts")
LOGGING_HARDWOOD_PMS = ("pm_saw_mills", "pm_hardwood", "pm_no_equipment", "pm_road_carts")
WHEAT_PMS = ("pm_soil_enriching_farming", "pm_no_secondary", "pm_tools")
RICE_PMS = ("pm_soil_enriching_farming_building_rice_farm", "pm_no_secondary", "pm_tools_building_rice_farm")
COTTON_PMS = ("default_building_cotton_plantation", "default_labour", "pm_road_carts")
SILK_PMS = ("default_building_silk_plantation", "pm_road_carts")
LIVESTOCK_PMS = ("pm_open_air_stockyards", "pm_sheep_farms", "pm_standard_fences", "pm_unrefrigerated")


# Absolute levels for the named buildings. Existing unlisted local buildings stay
# in place; deliberately invalid inheritances in split states are set to zero.
INDUSTRY = {
    "STATE_EASTERN_THRACE": {
        "role": "Başkent, makine, askerî tedarik, tersane ve mali idare",
        "buildings": {
            "building_government_administration": building(15, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(8, *UNIVERSITY_PMS, ownership="government"),
            "building_construction_sector": building(8, *CONSTRUCTION_PMS, ownership="government"),
            "building_tooling_workshop": building(18, *TOOLING_PMS),
            "building_steel_mill": building(13, *STEEL_PMS),
            "building_motor_industry": building(5, *MOTOR_PMS),
            "building_arms_industry": building(8, *ARMS_PMS),
            "building_shipyard": building(8, *SHIPYARD_PMS),
            "building_textile_mill": building(12, *TEXTILE_LUXURY_PMS),
            "building_paper_mill": building(10, *PAPER_PMS),
            "building_food_industry": building(8, *FOOD_PMS),
            "building_chemical_plant": building(6, *CHEMICAL_PMS),
            "building_railway": building(6, *RAILWAY_PMS),
            "building_port": building(8, *PORT_PMS),
            "building_iron_mine": building(18, *IRON_PMS),
            "building_logging_camp": building(4, *LOGGING_SOFTWOOD_PMS),
            "building_wheat_farm": building(5, *WHEAT_PMS),
            "building_silk_plantation": building(3, *SILK_PMS),
        },
    },
    "STATE_HUDAVENDIGAR": {
        "role": "Marmara dokuma, alet, motor ve kâğıt havzası",
        "buildings": {
            "building_government_administration": building(8, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(5, *UNIVERSITY_PMS, ownership="government"),
            "building_construction_sector": building(6, *CONSTRUCTION_PMS, ownership="government"),
            "building_tooling_workshop": building(15, *TOOLING_PMS),
            "building_steel_mill": building(10, *STEEL_PMS),
            "building_motor_industry": building(5, *MOTOR_PMS),
            "building_textile_mill": building(18, *TEXTILE_LUXURY_PMS),
            "building_paper_mill": building(8, *PAPER_PMS),
            "building_furniture_manufactory": 8,
            "building_food_industry": building(6, *FOOD_PMS),
            "building_chemical_plant": building(4, *CHEMICAL_PMS),
            "building_railway": building(5, *RAILWAY_PMS),
            "building_port": building(6, *PORT_PMS),
            "building_logging_camp": building(9, *LOGGING_HARDWOOD_PMS),
            "building_wheat_farm": building(5, *WHEAT_PMS),
            "building_cotton_plantation": building(6, *COTTON_PMS),
            "building_silk_plantation": building(4, *SILK_PMS),
        },
    },
    "STATE_KASTAMONU": {
        "role": "Ereğli-Zonguldak kömür ve maden tahliye havzası",
        "buildings": {
            "building_government_administration": building(3, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(2, *UNIVERSITY_PMS, ownership="government"),
            "building_construction_sector": building(3, *CONSTRUCTION_PMS, ownership="government"),
            "building_coal_mine": building(45, *COAL_PMS),
            "building_tooling_workshop": building(4, *TOOLING_PMS),
            "building_railway": building(5, *RAILWAY_PMS),
            "building_port": building(5, *PORT_PMS),
            "building_logging_camp": building(11, *LOGGING_HARDWOOD_PMS),
            "building_fishing_wharf": 5,
            "building_wheat_farm": building(10, *WHEAT_PMS),
            "building_livestock_ranch": building(5, *LIVESTOCK_PMS),
        },
    },
    "STATE_AYDIN": {
        "role": "İzmir ticaret, kömür, dokuma ve tüketim malları havzası",
        "buildings": {
            "building_government_administration": building(5, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(3, *UNIVERSITY_PMS, ownership="government"),
            "building_construction_sector": building(4, *CONSTRUCTION_PMS, ownership="government"),
            "building_coal_mine": building(25, *COAL_PMS),
            "building_textile_mill": building(12, *TEXTILE_LUXURY_PMS),
            "building_furniture_manufactory": 6,
            "building_food_industry": building(5, *FOOD_PMS),
            "building_railway": building(4, *RAILWAY_PMS),
            "building_port": building(6, *PORT_PMS),
            "building_fishing_wharf": 5,
            "building_wheat_farm": building(8, *WHEAT_PMS),
            "building_cotton_plantation": building(8, *COTTON_PMS),
            "building_silk_plantation": building(4, *SILK_PMS),
        },
    },
    "STATE_KONYA": {
        "role": "İç Anadolu tarım aleti, yün, gıda ve hukuk eğitimi merkezi",
        "buildings": {
            "building_government_administration": building(5, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(5, *UNIVERSITY_PMS, ownership="government"),
            "building_construction_sector": building(4, *CONSTRUCTION_PMS, ownership="government"),
            "building_tooling_workshop": building(8, *TOOLING_PMS),
            "building_textile_mill": building(6, *TEXTILE_BASIC_PMS),
            "building_paper_mill": building(4, *PAPER_PMS),
            "building_food_industry": building(8, *FOOD_PMS),
            "building_furniture_manufactory": 4,
            "building_railway": building(3, *RAILWAY_PMS),
            "building_wheat_farm": building(14, *WHEAT_PMS),
            "building_livestock_ranch": building(10, *LIVESTOCK_PMS),
            "building_cotton_plantation": building(5, *COTTON_PMS),
        },
    },
    "STATE_ANKARA": {
        "role": "İç tahıl, hayvancılık ve ikincil devlet tedarik kuşağı",
        "buildings": {
            "building_government_administration": building(6, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(3, *UNIVERSITY_PMS, ownership="government"),
            "building_construction_sector": building(3, *CONSTRUCTION_PMS, ownership="government"),
            "building_tooling_workshop": building(4, *TOOLING_PMS),
            "building_food_industry": building(8, *FOOD_PMS),
            "building_railway": building(2, *RAILWAY_PMS),
            "building_logging_camp": building(9, *LOGGING_SOFTWOOD_PMS),
            "building_wheat_farm": building(20, *WHEAT_PMS),
            "building_livestock_ranch": building(12, *LIVESTOCK_PMS),
        },
    },
    "STATE_BAGHDAD": {
        "role": "Nehir ticareti, kâğıt, eğitim, gıda ve kayıt merkezi",
        "buildings": {
            "building_government_administration": building(6, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(6, *UNIVERSITY_PMS, ownership="government"),
            "building_construction_sector": building(4, *CONSTRUCTION_PMS, ownership="government"),
            "building_paper_mill": building(12, *PAPER_PMS),
            "building_textile_mill": building(6, *TEXTILE_BASIC_PMS),
            "building_food_industry": building(8, *FOOD_PMS),
            "building_furniture_manufactory": 4,
            "building_railway": building(3, *RAILWAY_PMS),
            "building_rice_farm": building(15, *RICE_PMS),
            "building_tobacco_plantation": 4,
        },
    },
    "STATE_ALEPPO": {
        "role": "Kervan ve Akdeniz bağlantılı dokuma, kâğıt ve gıda merkezi",
        "buildings": {
            "building_government_administration": building(4, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(3, *UNIVERSITY_PMS, ownership="government"),
            "building_construction_sector": building(3, *CONSTRUCTION_PMS, ownership="government"),
            "building_textile_mill": building(9, *TEXTILE_BASIC_PMS),
            "building_paper_mill": building(5, *PAPER_PMS),
            "building_food_industry": building(6, *FOOD_PMS),
            "building_furniture_manufactory": 3,
            "building_railway": building(2, *RAILWAY_PMS),
            "building_port": building(4, *PORT_PMS),
            "building_fishing_wharf": 3,
            "building_logging_camp": building(6, *LOGGING_SOFTWOOD_PMS),
            "building_wheat_farm": building(10, *WHEAT_PMS),
            "building_cotton_plantation": building(8, *COTTON_PMS),
        },
    },
    "STATE_ATTICA": {
        "role": "Ege tersane, metal, kimya ve eğitim düğümü",
        "buildings": {
            "building_government_administration": building(4, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(4, *UNIVERSITY_PMS, ownership="government"),
            "building_construction_sector": building(3, *CONSTRUCTION_PMS, ownership="government"),
            "building_shipyard": building(5, *SHIPYARD_PMS),
            "building_arms_industry": building(4, *ARMS_PMS),
            "building_glassworks": 6,
            "building_railway": building(3, *RAILWAY_PMS),
            "building_port": building(5, *PORT_PMS),
            "building_lead_mine": building(10, *LEAD_PMS),
            "building_sulfur_mine": building(8, *SULFUR_PMS),
            "building_logging_camp": building(7, *LOGGING_HARDWOOD_PMS),
            "building_fishing_wharf": 3,
            "building_wheat_farm": building(5, *WHEAT_PMS),
            "building_cotton_plantation": building(5, *COTTON_PMS),
        },
    },
    "STATE_WESTERN_THRACE": {
        "role": "Balkan demir, cam ve dokuma geçişi",
        "buildings": {
            "building_government_administration": building(3, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(2, *UNIVERSITY_PMS, ownership="government"),
            "building_textile_mill": building(4, *TEXTILE_BASIC_PMS),
            "building_glassworks": 6,
            "building_iron_mine": building(21, *IRON_PMS),
            "building_logging_camp": building(5, *LOGGING_HARDWOOD_PMS),
            "building_railway": building(1, *RAILWAY_PMS),
            "building_port": building(4, *PORT_PMS),
            "building_fishing_wharf": 3,
            "building_wheat_farm": building(6, *WHEAT_PMS),
        },
    },
    "STATE_SKOPIA": {
        "role": "Balkan demir, kereste ve tahıl tedariki",
        "buildings": {
            "building_government_administration": building(2, *GOVERNMENT_PMS, ownership="government"),
            "building_iron_mine": building(30, *IRON_PMS),
            "building_logging_camp": building(14, *LOGGING_HARDWOOD_PMS),
            "building_railway": building(2, *RAILWAY_PMS),
            "building_wheat_farm": building(8, *WHEAT_PMS),
            "building_tobacco_plantation": 2,
        },
    },
    "STATE_MACEDONIA": {
        "role": "Selanik gıda, hafif dokuma, tahıl ve kereste düğümü",
        "buildings": {
            "building_government_administration": building(3, *GOVERNMENT_PMS, ownership="government"),
            "building_university": building(2, *UNIVERSITY_PMS, ownership="government"),
            "building_textile_mill": building(4, *TEXTILE_BASIC_PMS),
            "building_food_industry": building(5, *FOOD_PMS),
            "building_railway": building(1, *RAILWAY_PMS),
            "building_logging_camp": building(9, *LOGGING_HARDWOOD_PMS),
            "building_fishing_wharf": 3,
            "building_wheat_farm": building(8, *WHEAT_PMS),
            "building_cotton_plantation": building(5, *COTTON_PMS),
        },
    },
    "STATE_THESSALIA": {
        "role": "Balkan tahıl, hayvancılık ve pamuk hinterlandı",
        "buildings": {
            "building_government_administration": building(2, *GOVERNMENT_PMS, ownership="government"),
            "building_textile_mill": building(3, *TEXTILE_BASIC_PMS),
            "building_railway": building(1, *RAILWAY_PMS),
            "building_logging_camp": building(8, *LOGGING_SOFTWOOD_PMS),
            "building_fishing_wharf": 3,
            "building_wheat_farm": building(20, *WHEAT_PMS),
            "building_livestock_ranch": building(8, *LIVESTOCK_PMS),
            "building_cotton_plantation": building(6, *COTTON_PMS),
        },
    },
    "STATE_PELOPONNESE": {
        "role": "Ege demir, kereste, bağ ve kıyı gıda tedariki",
        "buildings": {
            "building_iron_mine": building(15, *IRON_PMS),
            "building_logging_camp": building(5, *LOGGING_SOFTWOOD_PMS),
            "building_port": building(3, *PORT_PMS),
            "building_fishing_wharf": 3,
            "building_wheat_farm": building(4, *WHEAT_PMS),
            "building_vineyard": 3,
        },
    },
    "STATE_CYPRUS": {
        "role": "Doğu Akdeniz ikmal ve küçük maden adası",
        "buildings": {
            "building_government_administration": building(1, *GOVERNMENT_PMS, ownership="government"),
            "building_iron_mine": building(4, *IRON_PMS),
            "building_sulfur_mine": building(3, *SULFUR_PMS),
            "building_port": building(2, *PORT_PMS),
            "building_fishing_wharf": 2,
            "building_wheat_farm": building(3, *WHEAT_PMS),
        },
    },
    "STATE_BASRA": {
        "role": "Rûm'un kuzey nehir payı; liman ve şehir Basra/Kuveyt yönetimlerindedir",
        "buildings": {
            "building_trade_center": 0,
            "building_port": 0,
            "building_fishing_wharf": 0,
            "building_sulfur_mine": building(10, *SULFUR_PMS),
            "building_rice_farm": building(7, *RICE_PMS),
            "building_tobacco_plantation": 3,
        },
    },
    "STATE_ADANA": {
        "role": "Rûm'un doğu/geçit payı; şehir, liman, tarım ve maden hub'ları Adana emirliğindedir",
        "buildings": {
            "building_port": 0,
            "building_fishing_wharf": 0,
            "building_cotton_plantation": 0,
            "building_livestock_ranch": 0,
            "building_tea_plantation": 0,
            "building_logging_camp": building(4, *LOGGING_HARDWOOD_PMS),
        },
    },
    "STATE_TRABZON": {
        "role": "Samsun-Ordu şehir ve tarım payı; liman/maden/kereste Trabzon atabeyliğindedir",
        "buildings": {
            "building_government_administration": building(2, *GOVERNMENT_PMS, ownership="government"),
            "building_food_industry": building(3, *FOOD_PMS),
            "building_wheat_farm": building(5, *WHEAT_PMS),
            "building_livestock_ranch": building(3, *LIVESTOCK_PMS),
            "building_tea_plantation": 2,
        },
    },
    "STATE_ERZURUM": {
        "role": "Van çevresindeki Rûm tarım payı; kent ve maden Erzurum atabeyliğindedir",
        "buildings": {"building_wheat_farm": building(3, *WHEAT_PMS), "building_livestock_ranch": building(3, *LIVESTOCK_PMS)},
    },
    "STATE_DEIR_EZ_ZOR": {
        "role": "Seyrek nehir ve hayvancılık kuşağı",
        "buildings": {"building_livestock_ranch": building(5, *LIVESTOCK_PMS)},
    },
    "STATE_MALTA": {
        "role": "Merkez Akdeniz ikmal, bakım ve balıkçılık adası",
        "buildings": {
            "building_shipyard": building(2, *SHIPYARD_PMS),
            "building_port": building(2, *PORT_PMS),
            "building_fishing_wharf": 2,
        },
    },
    "STATE_CRETE": {
        "role": "Ada tarımı, kıyı gıdası ve deniz ikmali",
        "buildings": {
            "building_food_industry": building(2, *FOOD_PMS),
            "building_port": building(2, *PORT_PMS),
            "building_fishing_wharf": 2,
            "building_cotton_plantation": building(2, *COTTON_PMS),
        },
    },
    "STATE_IONIAN_ISLANDS": {
        "role": "Batı Ege ikmal ve balıkçılık adaları",
        "buildings": {"building_port": building(2, *PORT_PMS), "building_fishing_wharf": 2, "building_wheat_farm": building(2, *WHEAT_PMS)},
    },
    "STATE_EAST_AEGEAN_ISLANDS": {
        "role": "Anadolu-Ege deniz geçişi",
        "buildings": {"building_port": building(1, *PORT_PMS), "building_fishing_wharf": 2},
    },
    "STATE_WEST_AEGEAN_ISLANDS": {
        "role": "Küçük liman ve balıkçılık ağı",
        "buildings": {"building_port": building(1, *PORT_PMS), "building_fishing_wharf": 2},
    },
}


TECHNOLOGIES = {
    "atmospheric_engine",
    "canneries",
    "dialectics",
    "intensive_agriculture",
    "lathe",
    "mechanical_tools",
    "mechanized_workshops",
    "railways",
    "rifling",
    "screw_frigate",
}


def compiled_rum_pops():
    local = load(ROOT / ".vic3-tools.local.json")
    sys.path.insert(0, str(Path(local["toolkit"]) / "src"))
    from vic3 import pdx

    root = pdx.parse_file(PARENT_POPS).get_node("POPS")
    result = {}
    for state_key, state_node in root.pairs():
        if not state_key.startswith("s:"):
            continue
        region = state_node.get_node("region_state:RUM")
        if not region:
            continue
        rows = []
        for key, node in region.pairs():
            if key != "create_pop":
                continue
            row = {
                "culture": node.get("culture"),
                "religion": node.get("religion"),
                "size": int(node.get("size")),
            }
            if node.get("pop_type"):
                row["pop_type"] = node.get("pop_type")
            rows.append(row)
        result[state_key[2:]] = rows
    return result


def normalized_composition(rows):
    total = sum(row["size"] for row in rows)
    result = []
    running = Decimal(0)
    for index, row in enumerate(rows):
        if index == len(rows) - 1:
            share = Decimal(1) - running
        else:
            share = (Decimal(row["size"]) / Decimal(total)).quantize(Decimal("0.000000000001"))
            running += share
        item = {"culture": row["culture"], "religion": row["religion"], "share": float(share)}
        if row.get("pop_type"):
            item["pop_type"] = "peasants" if row["pop_type"] == "slaves" else row["pop_type"]
        result.append(item)
    return result


def main():
    accepted = load(PARENT / "verification.json")
    if accepted["scenario_sha256"] != sha256(PARENT_SCENARIO):
        raise SystemExit("Faz 1B.1 kaynağı doğrulama kaydından sonra değişmiş; önce 1B.1'i yeniden doğrula.")
    if not PARENT_POPS.exists():
        raise SystemExit("Faz 1B.1 derlenmiş POP kaynağı yok; önce README'deki 1B.1 build komutunu çalıştır.")

    scenario = load(PARENT_SCENARIO)
    pops = compiled_rum_pops()
    expected_states = {row["state"] for row in load(PARENT / "population-plan.json")["regions"]}
    if set(pops) != expected_states or set(INDUSTRY) != expected_states:
        raise SystemExit("Rûm eyalet kapsamı 1B.1 nüfus veya 1B.2 ekonomi planıyla eşleşmiyor.")

    emancipated = 0
    for state, rows in pops.items():
        emancipated += sum(row["size"] for row in rows if row.get("pop_type") == "slaves")
        owner_population = scenario["states"][state]["population"]["by_owner"]["RUM"]
        owner_population["composition"] = normalized_composition(rows)
        scenario["states"][state]["industry"] = {
            "by_owner": {
                "RUM": {
                    "mode": "merge",
                    "buildings": INDUSTRY[state]["buildings"],
                }
            }
        }

    rum = scenario["countries"]["RUM"]
    rum["phase"] = "1B.2"
    rum["technology"]["add"] = sorted(set(rum["technology"].get("add", [])) | TECHNOLOGIES)
    rum["notes"] = (
        "1B.2 preview: 1811 emancipation is represented in starting POP status; industrial, "
        "resource, transport, university and administration backbone is explicit. Military, "
        "IG balance, company definition and runtime budget/market behavior remain pending."
    )
    scenario["title"] = "The Golden Crescent - Phase 1B.2: Rum Emancipation and Economic Backbone"
    scenario["description"] = (
        "PREVIEW ONLY. Cumulative Phase 1A/1B.1 source. RUM directly governs 27,000,000 people. "
        f"All {emancipated:,} inherited slave-status persons keep culture/religion and begin free. "
        "An explicit coal-iron-tools-steel-textile-paper-food-transport-administration backbone is "
        "distributed by resource and hub ownership. This is statically validated design data, not "
        "a runtime GDP, employment, budget or market-access guarantee."
    )

    plan = {
        "phase": "1B.2",
        "parent_scenario_sha256": sha256(PARENT_SCENARIO),
        "parent_pops_sha256": sha256(PARENT_POPS),
        "emancipation": {
            "law_date": 1811,
            "converted_starting_people": emancipated,
            "from_pop_type": "slaves",
            "to_pop_type": "peasants",
            "culture_and_religion_preserved": True,
            "recently_abolished_1836_effect_requested": False,
        },
        "design_limits": {
            "urbanization_target": "20-25%; building employment is only a proxy and must be measured in-engine",
            "budget": "administrative capacity is provisioned; wages, institution cost and tax balance need an engine run",
            "market": "production chains are source-balanced directionally; prices, trade routes and profitability need an engine run",
            "railway": "short industrial and mine links only; no continuous continental network is asserted",
            "companies": "Karadeniz Maden Ortaklığı needs a custom company definition before Atlas can assign it",
        },
        "technology_additions": sorted(TECHNOLOGIES),
        "states": INDUSTRY,
    }
    (HERE / "scenario.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n")
    (HERE / "economy-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {HERE/'scenario.json'}")
    print(f"wrote {HERE/'economy-plan.json'}")
    print(f"converted inherited slave status: {emancipated:,}")


if __name__ == "__main__":
    main()
