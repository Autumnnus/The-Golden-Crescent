"""Check that the installed political world matches the reviewed Atlas cards."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
PREVIEW = ROOT / "build/world-political/partial-political-preview.json"
ACTIVE = ROOT / "world/scenario.yml"
REPORT = ROOT / "build/world-political/active-political-report.json"
OUT = ROOT / "build/world-political/active-political-audit.json"
REPLACE_PATHS = {
    "common/history/buildings",
    "common/history/countries",
    "common/history/diplomacy",
    "common/history/military_formations",
    "common/history/pops",
    "common/history/population",
    "common/history/states",
}
POST_PREVIEW_MOVES = (
    ("STATE_HILL_PUNJAB", "xA0F0A0", "PTA", "PNJ"),
    ("STATE_KASHMIR", "x6326A6", "LAD", "KAS"),
    ("STATE_GUJARAT", "xB3D1CD", "JUN", "GJT"),
    ("STATE_RAJPUTANA", "x6E01FB", "MEW", "JOD"),
    ("STATE_RAJPUTANA", "x53A30A", "BIK", "MEW"),
    ("STATE_MALWA", "x746A39", "GWA", "IND"),
    ("STATE_ASSAM", "x30B15A", "NGA", "MNP"),
    ("STATE_ASSAM", "x9A1864", "MGH", "ASM"),
    # Phase 13 removes the one-province Danish Pegu enclave left by the
    # pre-demography India card; the written Southeast Asian atlas excludes it.
    ("STATE_PEGU", "xB030A0", "DEN", "BUR"),
    # Oceania demography separates Samoa-named island provinces from Tonga.
    ("STATE_TONGA", "xA7F8A1", "TNG", "VSM"),
    ("STATE_TONGA", "xC00010", "TNG", "VSM"),
)
POST_PREVIEW_OWNER_TRANSFERS = (
    ("STATE_VRYSTAAT", "ORA", "BST", 17),
    ("STATE_TRANSVAAL", "TRN", "MTB", 11),
    # Russia–Siberia demography merges the last Russian company share into Ainu Mosir.
    ("STATE_SAKHALIN", "ALK", "AIN", 2),
    # Middle East–India demography merges Danish Tranquebar into the Tamil kingdom.
    ("STATE_MADRAS", "DEN", "TAM", 1),
)
# North American demography replaces the Russian Alaska company and the Texas
# republic shares with new local councils; the province lists are unchanged.
POST_PREVIEW_OWNER_RENAMES = (
    ("STATE_ALASKA", "ALK", "VTU", 287),
    ("STATE_TEXAS", "TEX", "VCD", 81),
)
POST_PREVIEW_COUNTRIES = {
    "VTU": {
        "name": "Tlingit-Unangan Coast Council", "name_tr": "Tlingit–Unangan Kıyı Meclisi",
        "color": [70, 110, 140], "country_type": "unrecognized", "tier": "principality",
        "cultures": ["athabaskan", "inuit"], "religion": "animist", "capital": "STATE_ALASKA",
    },
    "VCD": {
        "name": "Caddo Confederacy", "name_tr": "Caddo Konfederasyonu",
        "color": [132, 92, 60], "country_type": "unrecognized", "tier": "principality",
        "cultures": ["caddoan"], "religion": "animist", "capital": "STATE_TEXAS",
    },
    "ARP": {"cultures": ["algonquian"]},
    "BLF": {"cultures": ["algonquian"]},
    "SEQ": {"cultures": ["caddoan", "siouan", "cherokee"]},
    # South American demography (phase 23): local identities of inherited tags.
    "SPU": {"cultures": ["quechua"], "religion": "animist"},
    "NPU": {"cultures": ["quechua", "south_andean"], "religion": "animist"},
    "PRG": {"cultures": ["guarani"], "religion": "animist"},
    "URU": {"cultures": ["patagonian", "guarani"], "religion": "animist"},
    "PRA": {"cultures": ["tupinamba", "amazonian"], "religion": "animist"},
    "PNI": {"cultures": ["guarani"], "religion": "animist"},
    "IQU": {"religion": "animist"},
    # Steppe–Turkestan–Caucasus demography (phase 25).
    "KAF": {"religion": "animist"},
}
# Reviewed country entries whose later demography phases change listed fields.
POST_PREVIEW_COUNTRY_FIELDS = {
    "VCL": {"cultures": (["nahua"], ["hokan"])},
    "VVA": {"laws": (None, {"values": ["law_legacy_slavery"]})},
    "VDC": {"laws": (None, {"values": ["law_legacy_slavery"]})},
    "VNE": {"cultures": (["nahua"], ["nahua", "mexican"])},
    "VBJ": {"cultures": (["nahua"], ["nahua", "tarascan"])},
    "VBP": {"cultures": (["nahua"], ["hokan"])},
    "VDR": {"cultures": (["nahua"], ["oodham"])},
    "VSO": {"cultures": (["nahua"], ["oodham"])},
    "VSR": {"cultures": (["nahua"], ["nahua", "oodham"])},
    "VNP": {"cultures": (["apache"], ["apache", "oodham"])},
    "VSS": {"cultures": (["mayan"], ["nahua"])},
    "VNC": {"cultures": (["mayan"], ["nahua", "miskito"])},
    "VKR": {"cultures": (["mayan"], ["muisca"])},
    "VLE": {"cultures": (["afro_caribbean"], ["afro_antillean"])},
    "VWI": {"cultures": (["afro_caribbean"], ["afro_antillean"])},
    "VPI": {"laws": (None, {"values": ["law_legacy_slavery"]})},
    "VCS": {"cultures": (["chilean"], ["patagonian", "south_andean"]), "religion": ("catholic", "animist")},
    "VOR": {"cultures": (["muisca"], ["amazonian"])},
    "VCU": {"cultures": (["quechua"], ["quechua", "aimara"])},
    "VKC": {"cultures": (["quechua"], ["quechua", "aimara"])},
    "VLP": {"cultures": (["quechua"], ["aimara", "quechua"])},
    "VAK": {"cultures": (["quechua"], ["aimara", "quechua"])},
    "VCQ": {"religion": ("catholic", "animist")},
    "VSI": {"laws": (None, {"values": ["law_legacy_slavery"]})},
    "VFB": {"laws": (None, {"values": ["law_slave_trade"]})},
    "VKM": {"cultures": (["mongol"], ["kalmyk"])},
    # M0 log cleanup: the overseas-dependencies crown keeps no inherited European army or fleet.
    "GBR": {"military": (None, {"mode": "replace", "formations": []})},
    # Middle East–India demography (phase 26).
    "ADA": {"laws": (None, {"values": ["law_debt_slavery"]})},
    "ERZ": {"laws": (None, {"values": ["law_debt_slavery"]})},
    "TRB": {"laws": (None, {"values": ["law_debt_slavery"]})},
    "KUR": {"laws": (None, {"values": ["law_debt_slavery"]})},
    "SYR": {"laws": (None, {"values": ["law_debt_slavery"]})},
    "LEB": {"laws": (None, {"values": ["law_debt_slavery"]})},
    "PAL": {"laws": (None, {"values": ["law_debt_slavery"]})},
    "KUW": {"laws": (None, {"values": ["law_debt_slavery"]})},
    "TAM": {"laws": (None, {"values": ["law_debt_slavery"]})},
    "VMB": {"cultures": (["afro_caribbean"], ["afro_antillean"])},
}
POST_PREVIEW_HOMELANDS = {
    "STATE_CAPE_COLONY": ["sotho", "khoisan"],
    "STATE_NORTHERN_CAPE": ["griqua", "sotho", "khoisan", "tswana"],
    "STATE_VRYSTAAT": ["griqua", "sotho", "nguni"],
    "STATE_TRANSVAAL": ["sotho", "nguni", "tswana", "zulu"],
}


M1_PLAN = ROOT / "scenarios/atlas/mechanics_m1_institutions/plan.yml"
M1B_PLAN = ROOT / "scenarios/atlas/mechanics_m1b_literacy/plan.yml"
M0_LIBERTY_RESET = ["IQU", "KZH", "NPU", "OZH", "SEQ", "SER", "UZH", "WAL"]
M0_RELATIONS = [{"actor": "MOL", "target": "WAL", "value": 50}, {"actor": "MON", "target": "SER", "value": 30},
                {"actor": "WAL", "target": "SER", "value": 20}]


def split_m1(tag: str, spec: dict, m1: dict, mismatches: list) -> dict:
    """M1/M1b own technology, laws and institutions of their planned countries; check them against the plan."""
    if tag not in m1:
        return spec
    row = m1[tag]
    if "tier" in row:
        tech = {"mode": "merge", "tier": row["tier"], **({"add": row["add_technologies"]} if row["add_technologies"] else {})}
    else:  # M1b vanilla-history country: only missing technologies are added
        tech = {"mode": "merge", "add": row["add_technologies"]} if row["add_technologies"] else None
    if spec.get("technology") != tech or spec.get("laws") != {"values": row["laws"]} or \
            spec.get("institutions", {}) != row["institutions"]:
        mismatches.append(f"country {tag} M1 institutions")
    return {key: value for key, value in spec.items() if key not in ("technology", "laws", "institutions")}


def political_state(spec: dict) -> dict:
    return {key: value for key, value in spec.items()
            if key not in {"pops", "buildings", "population", "industry", "homelands"}}


def main() -> None:
    preview = json.loads(PREVIEW.read_text())
    active = yaml.safe_load(ACTIVE.read_text())
    # The frozen preview predates the Indian hub fixes, Pegu enclave correction
    # and the two Samoa-named island province moves.
    expected_states = deepcopy(preview["states"])
    for state, province, old, new in POST_PREVIEW_MOVES:
        if new not in {part["owner"] for part in expected_states[state]["split"]}:
            expected_states[state]["split"].append({"owner": new, "provinces": []})
        parts = {part["owner"]: part["provinces"] for part in expected_states[state]["split"]}
        assert province in parts[old] and province not in parts[new], (state, province)
        parts[old].remove(province)
        parts[new].append(province)
        if not parts[old]:
            expected_states[state]["split"] = [part for part in expected_states[state]["split"]
                                                 if part["owner"] != old]
    for state, old, new, count in POST_PREVIEW_OWNER_TRANSFERS:
        parts = {part["owner"]: part for part in expected_states[state]["split"]}
        assert len(parts[old]["provinces"]) == count, (state, old)
        parts[new]["provinces"].extend(parts[old]["provinces"])
        expected_states[state]["split"].remove(parts[old])
    for state, old, new, count in POST_PREVIEW_OWNER_RENAMES:
        parts = [part for part in expected_states[state]["split"] if part["owner"] == old]
        assert len(parts) == 1 and len(parts[0]["provinces"]) == count, (state, old)
        parts[0]["owner"] = new
    report = json.loads(REPORT.read_text())
    metadata = json.loads((ROOT / ".metadata/metadata.json").read_text())
    mismatches = []

    # M0 log cleanup resets eight non-subject countries' inherited liberty desire and restores
    # the three bilateral relations the reset removes (mechanics_m0_cleanup/prepare.py).
    expected_diplomacy = deepcopy(preview.get("diplomacy"))
    if set(M0_LIBERTY_RESET) <= set((active.get("diplomacy") or {}).get("reset_countries") or []):
        expected_diplomacy["reset_countries"] = sorted(set(expected_diplomacy.get("reset_countries") or []) | set(M0_LIBERTY_RESET))
        expected_diplomacy["relations"] = (expected_diplomacy.get("relations") or []) + M0_RELATIONS
    for key in ("version", "subject_types", "diplomacy"):
        if active.get(key) != (expected_diplomacy if key == "diplomacy" else preview.get(key)):
            mismatches.append(key)
    m1 = yaml.safe_load(M1_PLAN.read_text())["countries"] if M1_PLAN.exists() else {}
    if not any("technology" in active["countries"].get(tag, {}) for tag in m1):
        m1 = {}
    m1b = yaml.safe_load(M1B_PLAN.read_text())["countries"] if M1B_PLAN.exists() else {}
    if not any("institutions" in active["countries"].get(tag, {}) for tag in m1b):
        m1b = {}
    m1 = {**m1, **m1b}
    expected_tags = set(preview["countries"]) | {"VSM", "TUA"} | set(POST_PREVIEW_COUNTRIES)
    # M1b adds entries for vanilla countries that carry only its education fields.
    m1b_only = set(active["countries"]) - expected_tags
    if expected_tags - set(active["countries"]) or m1b_only - set(m1b) or any(
            split_m1(tag, active["countries"][tag], m1, mismatches) for tag in m1b_only):
        mismatches.append("country tags")
    else:
        if split_m1("VSM", active["countries"]["VSM"], m1, mismatches) != {
            "name": "Samoan Council", "name_tr": "Samoa Meclisi", "color": [151, 71, 128],
            "country_type": "decentralized", "tier": "principality",
            "cultures": ["polynesian"], "religion": "animist", "capital": "STATE_TONGA",
        }:
            mismatches.append("country VSM")
        if active["countries"]["TUA"] != {"cultures": ["berber", "tuareg"]}:
            mismatches.append("country TUA primary cultures")
        for tag, spec in POST_PREVIEW_COUNTRIES.items():
            if split_m1(tag, active["countries"][tag], m1, mismatches) != {k: v for k, v in spec.items() if k != "laws" or tag not in m1}:
                mismatches.append(f"country {tag}")
        for tag, original in preview["countries"].items():
            current = split_m1(tag, active["countries"][tag], m1, mismatches)
            if tag == "YUE":
                # Yue demography adds the installed game's yue culture to the
                # confederation's original Han/Zhuang primary-culture list.
                if current.get("cultures") != original.get("cultures", []) + ["yue"]:
                    mismatches.append("country YUE primary cultures")
                original = {key: value for key, value in original.items() if key != "cultures"}
                current = {key: value for key, value in current.items() if key != "cultures"}
            if tag == "VAN":
                # The population phase adds Andalusi as a primary culture while
                # retaining the reviewed name, type, capital and other fields.
                original = {key: value for key, value in original.items() if key != "cultures"}
                current = {key: value for key, value in current.items() if key != "cultures"}
            if tag in {"VTD", "VVS"}:
                # The Philippine demographic phase replaces the inherited
                # colonial court faith while keeping every other country field.
                if original.get("religion") != "catholic" or current.get("religion") != "animist":
                    mismatches.append(f"country {tag} official religion")
                original = {key: value for key, value in original.items() if key != "religion"}
                current = {key: value for key, value in current.items() if key != "religion"}
            if tag == "VSN":
                # Sennaar's inherited slave POPs require an explicit matching
                # starting law; keep every other reviewed country field fixed.
                laws = (active["countries"]["VSN"].get("laws") or {}).get("values", [])
                if "laws" in original or "law_debt_slavery" not in laws:
                    mismatches.append("country VSN slavery law")
                current = {key: value for key, value in current.items() if key != "laws"}
            for field, (before, after) in POST_PREVIEW_COUNTRY_FIELDS.get(tag, {}).items():
                if field == "laws" and tag in m1:
                    continue  # M1 replaces the demography-phase slavery law list with the full law set
                if original.get(field) != before or current.get(field) != after:
                    mismatches.append(f"country {tag} {field}")
                original = {key: value for key, value in original.items() if key != field}
                current = {key: value for key, value in current.items() if key != field}
            if current != original:
                mismatches.append(f"country {tag}")
    if set(active["states"]) != set(preview["states"]):
        mismatches.append("state IDs")
    else:
        for state in preview["states"]:
            if political_state(active["states"][state]) != political_state(expected_states[state]):
                mismatches.append(state)
        for state, cultures in POST_PREVIEW_HOMELANDS.items():
            if active["states"][state].get("homelands") != cultures:
                mismatches.append(f"{state} homelands")

    pop_policies = {state: spec.get("pops") for state, spec in active["states"].items()}
    building_policies = {state: spec.get("buildings") for state, spec in active["states"].items()}
    if any(value != "inherit" for value in pop_policies.values()):
        mismatches.append("population inheritance")
    if any(value not in {"inherit", "drop"} for value in building_policies.values()):
        mismatches.append("building inheritance")
    if len(report["states"]) != len(preview["states"]):
        mismatches.append("reported states")
    if any(not row["population"] for row in report["states"].values()):
        mismatches.append("empty state population")
    if any(not row["population"] for row in report["countries"].values()):
        mismatches.append("empty landed country population")
    reported = deepcopy(report["diplomacy"])
    reported["relations"] = [row for row in reported.get("relations", []) if row not in M0_RELATIONS]
    if reported != json.loads(
        (ROOT / "build/world-political/final-political-report.json").read_text()
    )["diplomacy"]:
        mismatches.append("reported diplomacy")
    actual_replace_paths = set(metadata["game_custom_data"]["replace_paths"])
    if actual_replace_paths != REPLACE_PATHS:
        mismatches.append("metadata replace_paths")

    payload = {
        "title": "Etkin siyasi dünya denetimi",
        "political_state_count": len(active["states"]),
        "landed_country_count": len(report["countries"]),
        "population": sum(row["population"] for row in report["states"].values()),
        "building_states_inherited": sum(value == "inherit" for value in building_policies.values()),
        "building_states_deferred": sum(value == "drop" for value in building_policies.values()),
        "building_levels": sum(row["building_levels"] for row in report["countries"].values()),
        "static_report_warnings": report["warnings"],
        "runtime_tested": report["runtime_tested"],
        "mismatches": mismatches,
        "passed": not mismatches and report["validation"] == "passed",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (passed={payload['passed']})")
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
