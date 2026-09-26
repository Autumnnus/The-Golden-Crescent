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
D1_PLAN = ROOT / "scenarios/atlas/diplomacy_d1_natives/plan.yml"
D2_PLAN = ROOT / "scenarios/atlas/diplomacy_d2_subjects/plan.yml"
D3_PLAN = ROOT / "scenarios/atlas/diplomacy_d3_treaties/plan.yml"
D4_PLAN = ROOT / "scenarios/atlas/diplomacy_d4_recognition/plan.yml"
D4 = yaml.safe_load(D4_PLAN.read_text())["countries"] if D4_PLAN.exists() else {}
D5_PLAN = ROOT / "scenarios/atlas/diplomacy_d5_vanilla_subjects/plan.yml"
D5 = yaml.safe_load(D5_PLAN.read_text()) if D5_PLAN.exists() else {"subjects": [], "colonial": {}}
P2_DIR = ROOT / "scenarios/atlas/political_p2_corrections"
P2 = yaml.safe_load((P2_DIR / "plan.yml").read_text()) if (P2_DIR / "plan.yml").exists() else \
    {"transfers": [], "countries": {}, "new_countries": {}}
P2_ADJ = yaml.safe_load((P2_DIR / "adjectives.yml").read_text())["countries"] if (P2_DIR / "adjectives.yml").exists() else {}


def load_package(name: str) -> dict:
    """A P3-style political package (political_p3_borders/prepare.py format), in application order."""
    path = ROOT / f"scenarios/atlas/{name}/plan.yml"
    plan = {"moves": [], "transfers": [], "countries": {}, "new_countries": {}, "claims": {},
            **(yaml.safe_load(path.read_text()) if path.exists() else {})}
    plan["diplomacy"] = {"remove_subjects": [], "subjects": [], "relations": [], **(plan.get("diplomacy") or {})}
    return plan


PACKAGES = [load_package("political_p3_borders"), load_package("political_p4_corrections")]
LIVE = []  # the packages the active world contains (set in main)


def package_fields(tag: str) -> dict:
    """Country fields the live packages set; a later package overrides an earlier one."""
    fields = {}
    for plan in LIVE:
        fields.update(plan["countries"].get(tag, {}))
    return fields


M4_PLAN = ROOT / "scenarios/atlas/mechanics_m4_military/plan.yml"
M4 = yaml.safe_load(M4_PLAN.read_text())["countries"] if M4_PLAN.exists() else {}


def split_m4(tag: str, spec: dict, mismatches: list) -> dict:
    """M4 writes every organized country's army and navy (mechanics_m4_military/plan.yml)."""
    if tag not in M4 or "military" not in spec:
        return spec
    if spec["military"] != {"mode": "replace", "formations": M4[tag]["formations"]}:
        mismatches.append(f"country {tag} M4 military")
    return {key: value for key, value in spec.items() if key != "military"}


def split_p3(tag: str, spec: dict, mismatches: list) -> dict:
    """P3/P4 rename a few countries (plan.yml `countries`); their fields replace P2's adjectives."""
    spec = split_m4(tag, spec, mismatches)
    fields = package_fields(tag)
    for field, value in fields.items():
        if spec.get(field) != value:
            mismatches.append(f"country {tag} P3 {field}")
    return {key: value for key, value in spec.items() if key not in fields}


def split_p2(tag: str, spec: dict, mismatches: list) -> dict:
    """P2 adds adjectives to every named country and changes a few country fields (plan.yml)."""
    spec = split_p3(tag, spec, mismatches)
    drop = set()
    if tag in P2_ADJ and "adjective" in spec:
        if (spec.get("adjective"), spec.get("adjective_tr")) != (P2_ADJ[tag]["en"], P2_ADJ[tag]["tr"]):
            mismatches.append(f"country {tag} P2 adjective")
        drop |= {"adjective", "adjective_tr"}
    for field, value in P2["countries"].get(tag, {}).items():
        if spec.get(field) != value:
            mismatches.append(f"country {tag} P2 {field}")
        drop.add(field)
    return {key: value for key, value in spec.items() if key not in drop}
D1 = set(yaml.safe_load(D1_PLAN.read_text())["countries"]) if D1_PLAN.exists() else set()
D1_VANILLA = {"history_mode": "replace", "technology": {"mode": "replace", "tier": 7}, "institutions": {},
              "military": {"mode": "replace", "formations": []}}


def split_d1(tag: str, spec: dict, m1: dict, mismatches: list) -> dict:
    """D1 makes listed native polities decentralized; vanilla tags also get a replaced tier 7 history.
    D4 sets recognition by the scenario rule (Islamic and European sphere recognized)."""
    if tag in D5["colonial"] and spec.get("country_type") == "colonial":
        spec = {key: value for key, value in spec.items() if key != "country_type"}  # D5 colony type
    if tag in D4:
        if spec.get("country_type") != D4[tag]["to"]:
            mismatches.append(f"country {tag} D4 recognition")
        spec = {key: value for key, value in spec.items() if key != "country_type"}
    if tag not in D1:
        return spec
    if spec.get("country_type") != "decentralized":
        mismatches.append(f"country {tag} D1 country type")
    drop = {"country_type"}
    if tag not in m1:
        if any(spec.get(k) != v for k, v in D1_VANILLA.items()) or (spec.get("laws") or {}).get("mode") != "replace" \
                or "law_chiefdom" not in (spec.get("laws") or {}).get("values", []):
            mismatches.append(f"country {tag} D1 vanilla history")
        drop |= set(D1_VANILLA) | {"laws"}
    return {key: value for key, value in spec.items() if key not in drop}
M0_LIBERTY_RESET = ["IQU", "KZH", "NPU", "OZH", "SEQ", "SER", "UZH", "WAL"]
M0_RELATIONS = [{"actor": "MOL", "target": "WAL", "value": 50}, {"actor": "MON", "target": "SER", "value": 30},
                {"actor": "WAL", "target": "SER", "value": 20}]


def split_m1(tag: str, spec: dict, m1: dict, mismatches: list) -> dict:
    """M1/M1b own technology, laws and institutions of their planned countries; check them against the plan."""
    spec = split_p2(tag, spec, mismatches)
    spec = split_d1(tag, spec, m1, mismatches)
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
    # P2 (political_p2_corrections/plan.yml): whole parts change owner.
    first = P2["transfers"][0] if P2["transfers"] else None
    p2_active = bool(first) and first["to"] in active["states"][first["state"]]["population"]["by_owner"]
    for row in P2["transfers"] if p2_active else []:
        expected = expected_states[row["state"]]
        if "split" not in expected:
            assert expected.get("owner") == row["from"], (row["state"], row["from"])
            expected["owner"] = row["to"]
            continue
        parts = [part for part in expected["split"] if part["owner"] == row["from"]]
        assert parts, (row["state"], row["from"])
        for part in parts:
            part["owner"] = row["to"]
    # P3/P4 (political_p3_borders, political_p4_corrections): province moves, whole-share
    # transfers/merges and claims, applied in order. A package is live when its first transfer is.
    index = json.loads((ROOT / "build/index.json").read_text())
    for plan in PACKAGES:
        first = plan["transfers"][0] if plan["transfers"] else None
        if not first or first["from"] in active["states"][first["state"]]["population"]["by_owner"] or \
                first["to"] not in active["states"][first["state"]]["population"]["by_owner"]:
            break
        LIVE.append(plan)
        for row in plan["moves"]:
            expected = expected_states[row["state"]]
            if "split" not in expected:
                expected["split"] = [{"owner": expected.pop("owner"), "provinces": list(index["states"][row["state"]]["provinces"])}]
            for part in (p for p in expected["split"] if p["owner"] == row["from"]):
                part["provinces"] = [p for p in part["provinces"] if p not in row["provinces"]]
            expected["split"] = [p for p in expected["split"] if p["provinces"]]
            expected["split"].append({"owner": row["to"], "provinces": list(row["provinces"])})
        for row in plan["transfers"]:
            expected = expected_states[row["state"]]
            if expected.get("owner") == row["from"]:
                expected["owner"] = row["to"]
                continue
            mine = [p for p in expected["split"] if p["owner"] == row["from"]]
            theirs = [p for p in expected["split"] if p["owner"] == row["to"]]
            assert mine, (row["state"], row["from"])
            for p in mine:
                if theirs:
                    theirs[0]["provinces"] = theirs[0]["provinces"] + p["provinces"]
                    expected["split"].remove(p)
                else:
                    p["owner"] = row["to"]
        for state, tags in plan["claims"].items():
            current = expected_states[state].get("claims")
            current = list(index["state_history"][state]["claims"]) if current is None else current
            expected_states[state]["claims"] = current + [t for t in tags if t not in current]
    report = json.loads(REPORT.read_text())
    metadata = json.loads((ROOT / ".metadata/metadata.json").read_text())
    mismatches = []

    # M0 log cleanup resets eight non-subject countries' inherited liberty desire and restores
    # the three bilateral relations the reset removes (mechanics_m0_cleanup/prepare.py).
    expected_diplomacy = deepcopy(preview.get("diplomacy"))
    if set(M0_LIBERTY_RESET) <= set((active.get("diplomacy") or {}).get("reset_countries") or []):
        expected_diplomacy["reset_countries"] = sorted(set(expected_diplomacy.get("reset_countries") or []) | set(M0_LIBERTY_RESET))
        expected_diplomacy["relations"] = (expected_diplomacy.get("relations") or []) + M0_RELATIONS
    # D2 adds planned subject types and subject relations (diplomacy_d2_subjects/plan.yml).
    d2 = yaml.safe_load(D2_PLAN.read_text()) if D2_PLAN.exists() else {"subject_types": {}, "subjects": []}
    active_subjects = (active.get("diplomacy") or {}).get("subjects") or []
    pair = lambda row: (row["overlord"], row["subject"])
    if d2["subjects"] and pair(d2["subjects"][0]) not in {pair(row) for row in active_subjects}:
        d2 = {"subject_types": {}, "subjects": []}
    expected_diplomacy["subjects"] = (expected_diplomacy.get("subjects") or []) + d2["subjects"]
    # D3 adds mutual rivalries as pacts (diplomacy_d3_treaties/prepare.py); treaties are a separate file.
    d3 = yaml.safe_load(D3_PLAN.read_text()) if D3_PLAN.exists() else {"rivalries": []}
    d3_pacts = [{"actor": a, "target": b, "type": "rivalry"} for x, y in d3["rivalries"] for a, b in ((x, y), (y, x))]
    if not (active.get("diplomacy") or {}).get("pacts"):
        d3_pacts = []
    if d3_pacts:
        expected_diplomacy["pacts"] = (expected_diplomacy.get("pacts") or []) + d3_pacts
    # D5 replaces every custom subject type with a vanilla type (diplomacy_d5_vanilla_subjects/plan.yml).
    d5_types = {(r["overlord"], r["subject"]): r["to"] for r in D5["subjects"]}
    d5_active = bool(d5_types) and not active.get("subject_types")
    if d5_active:
        expected_diplomacy["subjects"] = [{**row, "type": d5_types[(row["overlord"], row["subject"])]}
                                          for row in expected_diplomacy["subjects"]]
    # P3/P4 remove and add vanilla-typed subjects and add relations; their rivalries and treaties are
    # in the D3 plan (see above).
    p3_pairs, p3_relations = set(), []
    for plan in LIVE:
        removed = {tuple(pair) for pair in plan["diplomacy"]["remove_subjects"]}
        expected_diplomacy["subjects"] = [row for row in expected_diplomacy["subjects"] if pair(row) not in removed] + \
            [dict(row) for row in plan["diplomacy"]["subjects"]]
        expected_diplomacy["relations"] = (expected_diplomacy.get("relations") or []) + \
            [dict(row) for row in plan["diplomacy"]["relations"]]
        p3_pairs |= {(row["overlord"], row["subject"]) for row in plan["diplomacy"]["subjects"]}
        p3_relations += plan["diplomacy"]["relations"]
    expected_types = deepcopy(preview.get("subject_types") or {})
    for key, spec in ({} if d5_active else d2["subject_types"]).items():
        current = (active.get("subject_types") or {}).get(key, {})
        if any(current.get(k) != v for k, v in spec.items()):
            mismatches.append(f"subject type {key}")
        expected_types[key] = current
    for key in ("version", "subject_types", "diplomacy"):
        expected = expected_diplomacy if key == "diplomacy" else ({} if d5_active else expected_types) \
            if key == "subject_types" else preview.get(key)
        if active.get(key) != expected:
            mismatches.append(key)
    m1 = yaml.safe_load(M1_PLAN.read_text())["countries"] if M1_PLAN.exists() else {}
    if not any("technology" in active["countries"].get(tag, {}) for tag in m1):
        m1 = {}
    m1b = yaml.safe_load(M1B_PLAN.read_text())["countries"] if M1B_PLAN.exists() else {}
    if not any("institutions" in active["countries"].get(tag, {}) for tag in m1b):
        m1b = {}
    m1 = {**m1, **m1b}
    expected_tags = set(preview["countries"]) | {"VSM", "TUA"} | set(POST_PREVIEW_COUNTRIES) | \
        (set(P2["new_countries"]) if p2_active else set()) | {tag for plan in LIVE for tag in plan["new_countries"]}
    for tag, spec in ((tag, spec) for plan in LIVE for tag, spec in plan["new_countries"].items()):
        current = split_m4(tag, active["countries"].get(tag, {}), mismatches)
        ignore = {"technology", "laws", "institutions"}
        if {k: v for k, v in current.items() if k not in ignore} != \
                {k: v for k, v in spec.items() if k not in ("like", "laws")}:
            mismatches.append(f"country {tag} P3 new country")
    for tag, spec in (P2["new_countries"].items() if p2_active else []):
        current = split_p2(tag, active["countries"].get(tag, {}), mismatches)
        ignore = {"technology", "laws", "institutions"} | ({"country_type"} if tag in D5["colonial"] else set())
        if {k: v for k, v in current.items() if k not in ignore} != \
                {k: v for k, v in spec.items() if k not in ("like", "slavery") and k not in ignore}:
            mismatches.append(f"country {tag} P2 new country")
    # M1b adds entries for vanilla countries that carry only its education fields.
    m1b_only = set(active["countries"]) - expected_tags
    p3_fields = {tag for plan in LIVE for tag in plan["countries"]} | \
        {tag for tag in M4 if "military" in active["countries"].get(tag, {})}
    if expected_tags - set(active["countries"]) or m1b_only - set(m1b) - set(P2["countries"]) - p3_fields or any(
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
            if split_m1(tag, active["countries"][tag], m1, mismatches) != {
                    k: v for k, v in spec.items() if (k != "laws" or tag not in m1) and (k != "country_type" or (tag not in D1 and tag not in D4))}:
                mismatches.append(f"country {tag}")
        for tag, original in preview["countries"].items():
            current = split_m1(tag, active["countries"][tag], m1, mismatches)
            if tag in D1 or tag in D4 or tag in D5["colonial"]:
                original = {key: value for key, value in original.items() if key != "country_type"}
            original = {key: value for key, value in original.items() if key not in P2["countries"].get(tag, {})
                        and key not in package_fields(tag)}
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
                if field == "laws" and (tag in m1 or tag in D1):
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
    d2_pairs = {(row["overlord"], row["subject"]) for row in d2["subjects"]}
    reported["overlords"] = {k: v for k, v in reported.get("overlords", {}).items()
                             if (v, k) not in d2_pairs and (v, k) not in p3_pairs}
    reported["relations"] = [row for row in reported["relations"] if row not in p3_relations]
    d3_keys = {(row["actor"], row["target"], row["type"]) for row in d3_pacts}
    reported["pacts"] = [row for row in reported.get("pacts", []) if (row["actor"], row["target"]) not in d2_pairs
                         and (row["actor"], row["target"]) not in p3_pairs
                         and (row["actor"], row["target"], row["type"]) not in d3_keys
                         and not (d5_active and (row["actor"], row["target"]) in d5_types)]
    final = json.loads((ROOT / "build/world-political/final-political-report.json").read_text())["diplomacy"]
    if d5_active:  # D5 changes the pact type of the preview's own subjects; the network is checked above
        final = {**final, "pacts": [row for row in final.get("pacts", []) if (row["actor"], row["target"]) not in d5_types]}
    if reported != final:
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
