"""Build the settled Iberian cores without inventing the four open borders."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-iberia-catalog.json"
TARGET = Path(__file__).with_name("card05.json")

# The remaining SPA/POR areas are intentional temporary compatibility holders.
# Beira, Valencia, Murcia and the Balearics are explicitly open in the written
# atlas, so this card does not manufacture a final owner for them.
COUNTRIES = {
    "VAN": {"name": "Andalusian Federation", "name_tr": "Endülüs Federasyonu", "color": [63, 137, 95], "country_type": "recognized", "tier": "kingdom", "cultures": ["spanish"], "religion": "sunni", "capital": "STATE_LOWER_ANDALUSIA"},
    "VCA": {"name": "Kingdom of Castile", "name_tr": "Kastilya Krallığı", "color": [151, 103, 77], "country_type": "recognized", "tier": "kingdom", "cultures": ["spanish"], "religion": "catholic", "capital": "STATE_NEW_CASTILE"},
    "VAR": {"name": "Crown of Aragon", "name_tr": "Aragon Tacı", "color": [157, 126, 69], "country_type": "recognized", "tier": "kingdom", "cultures": ["catalan"], "religion": "catholic", "capital": "STATE_ARAGON"},
    "VGL": {"name": "Kingdom of Galicia", "name_tr": "Galiçya Krallığı", "color": [83, 128, 151], "country_type": "recognized", "tier": "kingdom", "cultures": ["galician", "portuguese"], "religion": "catholic", "capital": "STATE_GALICIA"},
    "VNV": {"name": "Kingdom of Navarre", "name_tr": "Navarra Krallığı", "color": [134, 85, 99], "country_type": "recognized", "tier": "principality", "cultures": ["basque"], "religion": "catholic", "capital": "STATE_BASQUE_COUNTRY"},
    "SPA": {"name": "Unresolved Spanish Holder", "name_tr": "Geçici İspanyol Sahibi", "color": [125, 125, 125], "country_type": "recognized", "tier": "principality", "cultures": ["spanish"], "religion": "catholic", "capital": "STATE_CANARY_ISLANDS", "companies": {"mode": "replace", "add": [], "remove": []}},
    "POR": {"name": "Unresolved Portuguese Holder", "name_tr": "Geçici Portekiz Sahibi", "color": [125, 125, 125], "country_type": "recognized", "tier": "principality", "cultures": ["portuguese"], "religion": "catholic", "capital": "STATE_BOMBAY", "companies": {"mode": "replace", "add": [], "remove": []}},
}
TARGETS = {
    "STATE_LOWER_ANDALUSIA": ("SPA", "VAN"), "STATE_UPPER_ANDALUSIA": ("SPA", "VAN"),
    "STATE_EXTREMADURA": ("SPA", "VAN"), "STATE_ESTREMADURA": ("POR", "VAN"),
    "STATE_NEW_CASTILE": ("SPA", "VCA"), "STATE_OLD_CASTILE": ("SPA", "VCA"), "STATE_LEON": ("SPA", "VCA"),
    "STATE_ARAGON": ("SPA", "VAR"), "STATE_CATALONIA": ("SPA", "VAR"),
    "STATE_GALICIA": ("SPA", "VGL"), "STATE_ASTURIAS": ("SPA", "VGL"), "STATE_ENTRE_DOURO_E_MINHO": ("POR", "VGL"),
    "STATE_BASQUE_COUNTRY": ("SPC", "VNV"),
}


def refresh_catalog() -> dict:
    subprocess.run([sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", "SPA", "--out", str(CATALOG)], cwd=ROOT, check=True)
    return json.loads(CATALOG.read_text())


def main() -> None:
    by_id = {state["id"]: state for state in refresh_catalog()["states"]}
    missing = set(TARGETS) - set(by_id)
    if missing:
        raise RuntimeError(f"catalog misses required states: {sorted(missing)}")
    states = {}
    for state_id, (old_owner, new_owner) in TARGETS.items():
        parts, saw_owner = [], False
        for owner in by_id[state_id]["owners"]:
            saw_owner |= owner["tag"] == old_owner
            parts.append({"owner": new_owner if owner["tag"] == old_owner or (state_id in {"STATE_ARAGON", "STATE_CATALONIA"} and owner["tag"] == "SPC") or (state_id == "STATE_UPPER_ANDALUSIA" and owner["tag"] == "GBR") else owner["tag"], "provinces": owner["provinces"]})
        if not saw_owner:
            raise RuntimeError(f"{state_id} no longer contains {old_owner}")
        states[state_id] = {"split": parts, "pops": "drop", "buildings": "drop"}
    card = {"version": 2, "title": "Kart 1B — İberya'nın Kesin Çekirdekleri", "description": "Dünya siyasi iskeleti: Endülüs, Kastilya, Aragon, Galiçya ve Navarra'nın yazılı olarak kesin çekirdekleri. Aragon ve Katalonya’daki eski Katalan geçici payları Aragon tacında birleşir; açık sınırlar geçici sahipte kalır; mekanik başlangıç verisi üretmez.", "countries": COUNTRIES, "states": states, "diplomacy": {"mode": "inherit", "reset_countries": ["SPC"]}}
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
