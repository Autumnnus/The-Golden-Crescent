"""Close the last French direct holdings with documented local political owners."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = Path(__file__).with_name("card47.json")
TARGETS = {
    "STATE_IVORY_COAST": {"FRA": "AYI"},
    "STATE_INDIAN_OCEAN_TERRITORY": {"FRA": "VMB", "GBR": "VMB"},
    "STATE_WEST_INDIES": {"FRA": None},
}
COUNTRIES = {
    "VMB": {
        "name": "Mascarene Island Council",
        "name_tr": "Mascarene Ada Meclisi",
        "color": [81, 144, 166],
        "country_type": "recognized",
        "tier": "principality",
        "cultures": ["afro_caribbean"],
        "religion": "catholic",
        "capital": "STATE_INDIAN_OCEAN_TERRITORY",
    },
    "VLE": {
        "name": "Leeward Island Council",
        "name_tr": "Leeward Ada Meclisi",
        "color": [146, 108, 166],
        "country_type": "recognized",
        "tier": "principality",
        "cultures": ["afro_caribbean"],
        "religion": "catholic",
        "capital": "STATE_WEST_INDIES",
    },
    "VWI": {
        "name": "Windward Island Council",
        "name_tr": "Windward Ada Meclisi",
        "color": [166, 130, 78],
        "country_type": "recognized",
        "tier": "principality",
        "cultures": ["afro_caribbean"],
        "religion": "catholic",
        "capital": "STATE_WEST_INDIES",
    },
}


def final_owner(state_id: str, tag: str, province: str) -> str:
    if state_id != "STATE_WEST_INDIES":
        return TARGETS[state_id].get(tag, tag)
    if tag != "FRA":
        return tag
    # The two former French island provinces must remain two local political
    # units, rather than becoming a single Lesser Antilles colony.
    return {"x33895B": "VLE", "x9C52CA": "VWI"}[province]


def main() -> None:
    catalog = ROOT / "build/political-fra-final-catalog.json"
    subprocess.run(
        [sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "FRA", "--out", str(catalog)],
        cwd=ROOT,
        check=True,
    )
    source = {state["id"]: state for state in json.loads(catalog.read_text())["states"]}
    states = {}
    for state_id in TARGETS:
        owners, order, saw_french = {}, [], False
        for row in source[state_id]["owners"]:
            for province in row["provinces"]:
                saw_french |= row["tag"] == "FRA"
                tag = final_owner(state_id, row["tag"], province)
                if tag not in owners:
                    owners[tag] = []
                    order.append(tag)
                owners[tag].append(province)
        if not saw_french:
            raise RuntimeError(f"{state_id} no longer has a French share")
        states[state_id] = {
            "split": [{"owner": tag, "provinces": owners[tag]} for tag in order],
            "pops": "drop",
            "buildings": "drop",
        }
    card = {
        "version": 2,
        "title": "Kart 4E/5U — Fransız Denizaşırı Kalıntısının Kapanışı",
        "description": "Dünya siyasi iskeleti: Fildişi Sahili'ndeki Fransız payı mevcut Akan yerel sahibine döner; Mascarene adaları yerel ada meclisine geçer; iki Küçük Antil province'i ayrı Leeward ve Windward meclislerinde kalır. FRA'nın eski başlangıç diplomasi kayıtları temizlenir.",
        "countries": COUNTRIES,
        "states": states,
        "diplomacy": {"mode": "inherit", "reset_countries": ["FRA"]},
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
