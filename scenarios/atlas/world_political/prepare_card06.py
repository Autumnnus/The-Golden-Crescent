"""Return the directly occupied French Maghreb provinces to local governments."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-fra-maghreb-catalog.json"
TARGET = Path(__file__).with_name("card06.json")

# The written atlas keeps Algeria's coastal governments distinct; it does not
# impose a synthetic single Algerian state.  Existing MAS and CON cores are
# therefore expanded only by the exact French province shares in their states.
TARGETS = {"STATE_ALGIERS": "MAS", "STATE_ORAN": "MAS", "STATE_CONSTANTINE": "CON"}
COUNTRIES = {
    "MAS": {"name": "Algiers Maritime Government", "name_tr": "Cezayir Denizci Yönetimi", "color": [0, 129, 48], "country_type": "recognized", "tier": "principality", "cultures": ["maghrebi", "berber"], "religion": "sunni", "capital": "STATE_ORAN"},
    "CON": {"name": "Constantine Government", "name_tr": "Konstantin Denizci Yönetimi", "color": [228, 3, 16], "country_type": "recognized", "tier": "principality", "cultures": ["maghrebi", "berber"], "religion": "sunni", "capital": "STATE_CONSTANTINE"},
}


def refresh_catalog() -> dict:
    subprocess.run([sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "FRA", "--out", str(CATALOG)], cwd=ROOT, check=True)
    return json.loads(CATALOG.read_text())


def main() -> None:
    by_id = {state["id"]: state for state in refresh_catalog()["states"]}
    states = {}
    for state_id, local_owner in TARGETS.items():
        if state_id not in by_id:
            raise RuntimeError(f"catalog misses {state_id}")
        parts, saw_french = [], False
        for owner in by_id[state_id]["owners"]:
            saw_french |= owner["tag"] == "FRA"
            parts.append({"owner": local_owner if owner["tag"] == "FRA" else owner["tag"], "provinces": owner["provinces"]})
        if not saw_french:
            raise RuntimeError(f"{state_id} no longer has a French share")
        states[state_id] = {"split": parts, "pops": "drop", "buildings": "drop"}
    card = {"version": 1, "title": "Kart 4A — Mağrip Yerel Egemenlikleri", "description": "Dünya siyasi iskeleti: Fransız doğrudan Cezayir province payları yerel denizci yönetimlere döner. Tunus, Trablus ve Fas zaten yerel sahipte kalır; mekanik başlangıç verisi üretmez.", "countries": COUNTRIES, "states": states}
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
