"""Static guardrails for map-only political card sources."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
CARDS = {
    "card00.json": {"version": 1, "countries": 20, "states": 54},
    "card01.json": {"version": 1, "countries": 7, "states": 20},
    "card02.json": {"version": 2, "countries": 15, "states": 21},
    "card03.json": {"version": 2, "countries": 10, "states": 43},
    "card04.json": {"version": 2, "countries": 22, "states": 56},
    "card05.json": {"version": 2, "countries": 7, "states": 13},
    "card06.json": {"version": 1, "countries": 2, "states": 3},
    "card07.json": {"version": 1, "countries": 5, "states": 7},
    "card08.json": {"version": 1, "countries": 2, "states": 2},
    "card09.json": {"version": 1, "countries": 4, "states": 13},
    "card10.json": {"version": 1, "countries": 3, "states": 4},
    "card11.json": {"version": 2, "countries": 0, "states": 7},
    "card12.json": {"version": 1, "countries": 1, "states": 16},
    "card13.json": {"version": 1, "countries": 1, "states": 1},
    "card14.json": {"version": 1, "countries": 1, "states": 5},
    "card15.json": {"version": 2, "countries": 15, "states": 38},
    "card16.json": {"version": 2, "countries": 2, "states": 1},
    "card17.json": {"version": 2, "countries": 8, "states": 8},
    "card18.json": {"version": 2, "countries": 2, "states": 1},
    "card19.json": {"version": 2, "countries": 11, "states": 16},
    "card20.json": {"version": 2, "countries": 2, "states": 1},
    "card21.json": {"version": 1, "countries": 2, "states": 3},
    "card22.json": {"version": 1, "countries": 5, "states": 10},
    "card23.json": {"version": 2, "countries": 2, "states": 1},
    "card24.json": {"version": 2, "countries": 6, "states": 7},
    "card25.json": {"version": 1, "countries": 3, "states": 6},
    "card26.json": {"version": 2, "countries": 2, "states": 1},
    "card27.json": {"version": 1, "countries": 1, "states": 2},
    "card28.json": {"version": 2, "countries": 2, "states": 1},
    "card29.json": {"version": 2, "countries": 2, "states": 2},
    "card30.json": {"version": 2, "countries": 1, "states": 3},
    "card31.json": {"version": 1, "countries": 2, "states": 1},
    "card32.json": {"version": 2, "countries": 6, "states": 5},
    "card33.json": {"version": 1, "countries": 1, "states": 10},
    "card34.json": {"version": 2, "countries": 1, "states": 1},
    "card35.json": {"version": 1, "countries": 1, "states": 2},
    "card36.json": {"version": 2, "countries": 0, "states": 0},
    "card37.json": {"version": 2, "countries": 2, "states": 3},
    "card38.json": {"version": 2, "countries": 2, "states": 4},
    "card39.json": {"version": 2, "countries": 0, "states": 0},
    "card40.json": {"version": 2, "countries": 1, "states": 1},
    "card41.json": {"version": 2, "countries": 1, "states": 8},
    "card42.json": {"version": 2, "countries": 0, "states": 4},
    "card43.json": {"version": 2, "countries": 0, "states": 2},
    "card44.json": {"version": 2, "countries": 0, "states": 12},
    "card45.json": {"version": 2, "countries": 0, "states": 0},
    "card46.json": {"version": 1, "countries": 0, "states": 1},
    "card47.json": {"version": 2, "countries": 3, "states": 3},
    "card48.json": {"version": 1, "countries": 0, "states": 1},
    "card49.json": {"version": 2, "countries": 1, "states": 5},
    "card50.json": {"version": 1, "countries": 0, "states": 2},
    "card51.json": {"version": 1, "countries": 0, "states": 1},
    "card52.json": {"version": 1, "countries": 1, "states": 1},
    "card53.json": {"version": 2, "countries": 3, "states": 3},
    "card54.json": {"version": 1, "countries": 0, "states": 3},
    "card55.json": {"version": 1, "countries": 0, "states": 1},
    "card56.json": {"version": 1, "countries": 0, "states": 2},
    "card57.json": {"version": 1, "countries": 0, "states": 4},
    "card58.json": {"version": 2, "countries": 0, "states": 0},
    "card59.json": {"version": 2, "countries": 0, "states": 0},
    "card60.json": {"version": 2, "countries": 0, "states": 0},
    "card61.json": {"version": 2, "countries": 2, "states": 8},
    "card62.json": {"version": 2, "countries": 12, "states": 0},
    "card63.json": {"version": 2, "countries": 0, "states": 221},
    "card64.json": {"version": 2, "countries": 0, "states": 0},
}


def owners(spec: dict) -> set[str]:
    if "owner" in spec:
        return {spec["owner"]}
    return {part["owner"] for part in spec["split"]}


def main() -> None:
    results = {}
    loaded = {}
    for filename, expected in CARDS.items():
        card = json.loads((HERE / filename).read_text())
        assert card["version"] == expected["version"]
        assert len(card["countries"]) == expected["countries"]
        assert len(card["states"]) == expected["states"]
        assert all(spec["pops"] == "drop" and spec["buildings"] == "drop" for spec in card["states"].values())
        # New map countries with a capital in this card must own it. FRA is a
        # temporary overseas holder; existing Indian states may retain their
        # valid vanilla capital outside this BIC-only replacement card.
        for tag, country in card["countries"].items():
            if tag in {"FRA", "SPA", "POR", "SPC", "PRU", "GBR", "MEX", "RUS", "USA", "HBC", "MEX", "BRZ", "BOL", "ARG", "CHL", "ECU", "SPU", "CLM", "UCA", "DEI"}:
                continue
            capital = country.get("capital")
            if capital not in card["states"]:
                continue
            assert tag in owners(card["states"][capital]), (filename, tag, capital)
        reset_cards = {"card02.json": ["BIC"], "card03.json": ["CHI"], "card04.json": ["RUS"], "card11.json": ["FIN"], "card15.json": ["USA"], "card16.json": ["USA"], "card17.json": ["HBC", "QUE"], "card18.json": ["HBC", "ONT"], "card19.json": ["MEX"], "card20.json": ["MEX"], "card23.json": ["BRZ"], "card24.json": ["BOL"], "card26.json": ["ARG"], "card28.json": ["CHL"], "card29.json": ["ECU"], "card30.json": ["SPU"], "card32.json": ["UCA", "MKT"], "card34.json": ["DEI"], "card37.json": ["BEL", "HAN"], "card38.json": ["PHI"], "card39.json": ["KAS", "JAI", "MEW"], "card40.json": ["RYU"], "card05.json": ["SPC"], "card43.json": ["SPA"], "card45.json": ["POR"], "card47.json": ["FRA"], "card49.json": ["PRU"], "card53.json": ["CLM"], "card56.json": ["PAN"], "card59.json": ["HAU"], "card60.json": ["AUS", "KRA", "CRO", "DEN", "HOL", "SCH", "SWE", "NOR", "NET", "LUX", "EGY", "HDJ", "ABU", "OMA", "MBS", "KAL", "MAK", "BUR", "SHS", "DAI", "SIA", "CAM", "CHP", "CMI", "LUA", "JAP", "EZO"], "card61.json": ["GBR", "SIL", "SAF", "NBS", "NVS"]}
        if filename in reset_cards:
            removed = reset_cards[filename]
            assert card["diplomacy"].get("mode") == "inherit"
            assert card["diplomacy"].get("reset_countries") == removed
            assert all(tag not in owners(spec) for tag in removed for spec in card["states"].values())
        if filename == "card44.json":
            assert "POR" not in {tag for spec in card["states"].values() for tag in owners(spec)}
            assert "FRA" not in owners(card["states"]["STATE_SENEGAL"])
        if filename == "card46.json":
            assert "FRA" not in owners(card["states"]["STATE_GUAYANA"])
            assert owners(card["states"]["STATE_GUAYANA"]) == {"NET"}
        if filename == "card53.json":
            assert owners(card["states"]["STATE_ANTIOQUIA"]) == {"VSI"}
            assert owners(card["states"]["STATE_CAUCA"]) == {"VCQ"}
            assert owners(card["states"]["STATE_GUAVIARE"]) == {"VOR"}
        if filename == "card54.json":
            assert "EGY" not in owners(card["states"]["STATE_KORDOFAN"])
            assert "EGY" not in owners(card["states"]["STATE_ERITREA"])
            assert {"DEN", "NET"}.isdisjoint(owners(card["states"]["STATE_GOLD_COAST"]))
        if filename == "card55.json":
            assert "HDJ" not in owners(card["states"]["STATE_YEMEN"])
            assert {"ZAI", "LAH", "MAH", "KAT"}.issubset(owners(card["states"]["STATE_YEMEN"]))
        if filename == "card52.json":
            assert owners(card["states"]["STATE_PANAMA"]) == {"VIT"}
        if filename == "card51.json":
            assert "GBR" not in owners(card["states"]["STATE_MALAYA"])
            assert "JOH" in owners(card["states"]["STATE_MALAYA"])
        if filename == "card50.json":
            assert owners(card["states"]["STATE_WEST_GALICIA"]) == {"KRA"}
            assert owners(card["states"]["STATE_EAST_GALICIA"]) == {"VPL"}
        if filename == "card49.json":
            assert owners(card["states"]["STATE_EAST_PRUSSIA"]) == {"VPD"}
            assert "VPL" in owners(card["states"]["STATE_WEST_PRUSSIA"])
            assert owners(card["states"]["STATE_LOWER_SILESIA"]) == {"VBO"}
            assert owners(card["states"]["STATE_UPPER_SILESIA"]) == {"VBO"}
        if filename == "card48.json":
            assert owners(card["states"]["STATE_NEWFOUNDLAND"]) == {"VIN"}
        if filename == "card47.json":
            assert owners(card["states"]["STATE_IVORY_COAST"]) >= {"AYI", "KNG", "BLE"}
            assert owners(card["states"]["STATE_INDIAN_OCEAN_TERRITORY"]) == {"VMB"}
            assert {"VLE", "VWI"}.issubset(owners(card["states"]["STATE_WEST_INDIES"]))
        if filename == "card43.json":
            assert owners(card["states"]["STATE_AL_RIF"]) == {"MOR"}
            assert owners(card["states"]["STATE_CANARY_ISLANDS"]) == {"VAN"}
        if filename == "card42.json":
            assert owners(card["states"]["STATE_BEIRA"]) == {"VAN"}
            assert owners(card["states"]["STATE_MURCIA"]) == {"VAN"}
            assert owners(card["states"]["STATE_VALENCIA"]) == {"VAR"}
            assert owners(card["states"]["STATE_BALEARIC_ISLANDS"]) == {"VAR"}
        if filename == "card41.json":
            assert card["diplomacy"]["reset_countries"] == ["NSW", "WAS", "SAS", "TAS", "KAU", "UNT"]
            assert {"NSW", "WAS", "SAS", "TAS"}.isdisjoint({tag for spec in card["states"].values() for tag in owners(spec)})
        if filename == "card40.json":
            assert set(owners(card["states"]["STATE_CEYLON"])) == {"VKN"}
        if filename == "card39.json":
            assert card["diplomacy"]["reset_countries"] == ["KAS", "JAI", "MEW"]
            assert card["diplomacy"]["subjects"] == [
                {"overlord": "MUG", "subject": "KAS", "type": "ve_contractual_vassal", "liberty_desire": 35},
                {"overlord": "MUG", "subject": "JAI", "type": "ve_limited_protection", "liberty_desire": 45},
                {"overlord": "MUG", "subject": "MEW", "type": "ve_limited_protection", "liberty_desire": 45},
            ]
            assert card["subject_types"]["ve_contractual_vassal"]["base"] == "vassal"
            assert card["subject_types"]["ve_limited_protection"]["base"] == "protectorate"
        if filename == "card56.json":
            assert "PAN" not in owners(card["states"]["STATE_PUNJAB"])
            assert owners(card["states"]["STATE_PUNJAB"]) == {"MUG", "BHW"}
            assert "PAN" not in owners(card["states"]["STATE_PASHTUNISTAN"])
            assert "KAB" in owners(card["states"]["STATE_PASHTUNISTAN"])
        if filename == "card57.json":
            assert "OMA" not in {tag for spec in card["states"].values() for tag in owners(spec)}
            assert "ABU" in owners(card["states"]["STATE_ABU_DHABI"])
            assert "MAK" in owners(card["states"]["STATE_BALUCHISTAN"])
            assert "MAK" in owners(card["states"]["STATE_SISTAN"])
            assert "MBS" in owners(card["states"]["STATE_KENYA"])
        if filename == "card58.json":
            assert card["diplomacy"]["relations"] == [
                {"actor": "EGY", "target": "ACE", "value": 25},
                {"actor": "EGY", "target": "SLW", "value": 20},
                {"actor": "OMA", "target": "JOH", "value": 25},
                {"actor": "OMA", "target": "SUL", "value": 10},
                {"actor": "OMA", "target": "MBS", "value": 10},
            ]
        if filename == "card59.json":
            assert card["subject_types"]["ve_emirate_compact"]["base"] == "vassal"
            assert card["diplomacy"]["subjects"] == [
                {"overlord": "SOK", "subject": "HAU", "type": "ve_emirate_compact", "liberty_desire": 40}
            ]
        if filename == "card60.json":
            assert card["subject_types"]["ve_hajj_protection"]["base"] == "protectorate"
            assert card["subject_types"]["ve_mandala_autonomy"]["base"] == "vassal"
            assert card["subject_types"]["ve_japanese_domain"]["base"] == "vassal"
            assert len(card["diplomacy"]["subjects"]) == 7
        if filename == "card61.json":
            assert owners(card["states"]["STATE_SIERRA_LEONE"]) == {"TMN", "MDK"}
            assert "SAF" not in {tag for spec in card["states"].values() for tag in owners(spec)}
            assert owners(card["states"]["STATE_NEW_BRUNSWICK"]) == {"VWM"}
        if filename == "card62.json":
            assert card["countries"]["DIO"]["capital"] == "STATE_SENEGAL"
            assert card["countries"]["ATB"]["capital"] == "STATE_ALASKA"
            assert card["countries"]["TEK"]["capital"] == "STATE_WEST_SAHARA"
        if filename == "card63.json":
            assert "STATE_AUSTRIA" in card["states"]
            assert "STATE_SOUTH_ISLAND" in card["states"]
        if filename == "card64.json":
            assert len(card["diplomacy"]["subjects"]) == 16
            assert {row["subject"] for row in card["diplomacy"]["subjects"]} >= {"BOS", "MOL", "VNE", "VFB", "VNI", "VNH"}
        if filename == "card04.json":
            assert "RUS" not in owners(card["states"]["STATE_NORTH_CAUCASUS"])
            partitions = card["states"]["STATE_NORTH_CAUCASUS"]["split"]
            flattened = [province for part in partitions for province in part["provinces"]]
            assert len(flattened) == len(set(flattened))
        results[filename] = {"countries": len(card["countries"]), "states": len(card["states"])}
        loaded[filename] = card
    # Cards remain isolated previews, but their future V2 merge must be
    # mechanically possible.  A state cannot be independently rewritten by
    # two cards, and a temporary capital cannot be taken by another card.
    state_cards = {}
    country_cards = {}
    for filename, card in loaded.items():
        for state in card["states"]:
            state_cards.setdefault(state, []).append(filename)
        for tag in card["countries"]:
            country_cards.setdefault(tag, []).append(filename)
    duplicate_states = {state: files for state, files in state_cards.items() if len(files) > 1}
    duplicate_countries = {tag: files for tag, files in country_cards.items() if len(files) > 1}
    assert not duplicate_states, f"state overlays require an explicit merge: {duplicate_states}"
    allowed_temporary_duplicates = {"USA": ["card15.json", "card16.json"], "HBC": ["card17.json", "card18.json"], "MEX": ["card10.json", "card19.json", "card20.json"], "BRZ": ["card21.json", "card23.json"], "DEI": ["card33.json", "card34.json"]}
    assert duplicate_countries == allowed_temporary_duplicates or not duplicate_countries, f"country definitions require an explicit merge: {duplicate_countries}"
    for filename, card in loaded.items():
        for tag, country in card["countries"].items():
            if tag in {"FRA", "SPA", "POR", "SPC", "PRU", "GBR", "MEX", "RUS", "USA", "HBC", "MEX", "BRZ", "BOL", "ARG", "CHL", "ECU", "SPU", "CLM", "UCA", "DEI"}:
                continue
            capital = country.get("capital")
            for other_filename, other in loaded.items():
                if other_filename == filename or capital not in other["states"]:
                    continue
                assert tag in owners(other["states"][capital]), (
                    f"{filename}:{tag} capital {capital} is removed by {other_filename}"
                )
    print(json.dumps({"status": "passed", "cards": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print(f"card verification failed: {error}", file=sys.stderr)
        raise
