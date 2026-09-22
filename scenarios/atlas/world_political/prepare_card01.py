"""Build the first complete European political card: the six French states."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = Path(__file__).with_name("card01.json")

COUNTRIES = {
    "FPA": {"name": "Kingdom of Paris", "name_tr": "Paris Krallığı", "color": [66, 106, 160], "country_type": "recognized", "tier": "kingdom", "cultures": ["french"], "religion": "catholic", "capital": "STATE_ILE_DE_FRANCE"},
    "FBG": {"name": "Kingdom of Burgundy", "name_tr": "Burgonya Krallığı", "color": [130, 86, 166], "country_type": "recognized", "tier": "kingdom", "cultures": ["french"], "religion": "catholic", "capital": "STATE_BURGUNDY"},
    "FBR": {"name": "Duchy of Brittany", "name_tr": "Bretonya Dükalığı", "color": [77, 139, 125], "country_type": "recognized", "tier": "principality", "cultures": ["french"], "religion": "catholic", "capital": "STATE_BRITTANY"},
    "FAQ": {"name": "Kingdom of Aquitaine", "name_tr": "Akitanya Krallığı", "color": [185, 128, 77], "country_type": "recognized", "tier": "kingdom", "cultures": ["french"], "religion": "catholic", "capital": "STATE_AQUITAINE"},
    "FOC": {"name": "Occitan Confederation", "name_tr": "Oksitanya Konfederasyonu", "color": [181, 101, 79], "country_type": "recognized", "tier": "kingdom", "cultures": ["occitan"], "religion": "catholic", "capital": "STATE_LANGUEDOC"},
    "FPR": {"name": "Provence", "name_tr": "Provence", "color": [181, 151, 83], "country_type": "recognized", "tier": "principality", "cultures": ["occitan"], "religion": "catholic", "capital": "STATE_PROVENCE"},
}

# Every FRA-held state is assigned exactly once.  The Lyon/Rhône tariff dispute
# is represented by Burgundy owning the state while Provence keeps Marseille.
STATES = {
    "FPA": ["STATE_ILE_DE_FRANCE", "STATE_PICARDY", "STATE_NORMANDY", "STATE_CHAMPAGNE", "STATE_ORLEANS", "STATE_MAINE_ANJOU", "STATE_FRENCH_LOW_COUNTRIES"],
    "FBG": ["STATE_BURGUNDY", "STATE_FRANCHE_COMTE", "STATE_LORRAINE", "STATE_ALSACE_LORRAINE", "STATE_RHONE"],
    "FBR": ["STATE_BRITTANY"],
    "FAQ": ["STATE_AQUITAINE", "STATE_GUYENNE", "STATE_POITOU"],
    "FOC": ["STATE_LANGUEDOC", "STATE_AUVERGNE_LIMOUSIN"],
    "FPR": ["STATE_CORSICA"],
}
PROVENCE = {
    "split": [
        {"owner": "FPR", "provinces": ["x3040E0", "x31C0DF", "x6D5E3F", "xB040E0", "xB0C060", "xB0C0E0", "xC03918", "xCB9C34"]},
        {"owner": "SAR", "provinces": ["x5080E0"]},
    ]
}


def map_state(owner: str) -> dict:
    return {"owner": owner, "pops": "drop", "buildings": "drop"}


def main() -> None:
    states = {state: map_state(owner) for owner, state_ids in STATES.items() for state in state_ids}
    states["STATE_PROVENCE"] = {**PROVENCE, "pops": "drop", "buildings": "drop"}
    countries = {
        **COUNTRIES,
        # FRA loses every direct state in this card. Its vanilla company would
        # otherwise keep an invalid headquarters in Alsace-Lorraine.
        "FRA": {
        "capital": "STATE_INDIAN_OCEAN_TERRITORY",
            "companies": {"mode": "replace", "add": [], "remove": []},
            "notes": "Geçici: Afrika ve Atlantik kartları henüz FRA'nın denizaşırı paylarını yeniden dağıtmadı.",
        },
    }
    card = {
        "version": 1,
        "title": "Kart 1A — Altı Fransız Devleti",
        "description": "Dünya siyasi iskeletinin yalnız Fransa bölümü. Paris'in kuzey çekirdeği French Low Countries state'ini de içerir. Nüfus, ekonomi, hukuk, ordu ve diplomasi üretmez.",
        "countries": countries,
        "states": states,
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(countries)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
