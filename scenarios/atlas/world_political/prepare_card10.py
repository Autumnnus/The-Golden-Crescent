"""Build the first Mexican basin / Maya political slice from exact MEX shares."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-mex-catalog.json"
TARGET = Path(__file__).with_name("card10.json")
TARGETS = {"STATE_MEXICO": "VNE", "STATE_VERACRUZ": "VNE", "STATE_YUCATAN": "VMY", "STATE_CHIAPAS": "VMY"}
COUNTRIES = {
    "VNE": {"name": "New Andalusia", "name_tr": "Yeni Endülüs", "color": [64, 140, 97], "country_type": "recognized", "tier": "kingdom", "cultures": ["nahua"], "religion": "sunni", "capital": "STATE_MEXICO"},
    "VMY": {"name": "Maya League", "name_tr": "Maya Birliği", "color": [87, 137, 128], "country_type": "recognized", "tier": "kingdom", "cultures": ["mayan"], "religion": "animist", "capital": "STATE_YUCATAN"},
    "MEX": {"name": "Unresolved Mexican Interior", "name_tr": "Geçici Meksika İç Bölgesi", "color": [125, 125, 125], "country_type": "recognized", "tier": "principality", "cultures": ["nahua"], "religion": "catholic", "capital": "STATE_RIO_GRANDE", "companies": {"mode": "replace", "add": [], "remove": []}},
}


def main() -> None:
    subprocess.run([sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "MEX", "--out", str(CATALOG)], cwd=ROOT, check=True)
    by_id = {state["id"]: state for state in json.loads(CATALOG.read_text())["states"]}
    states = {}
    for state_id, target in TARGETS.items():
        parts, found = [], False
        for owner in by_id[state_id]["owners"]:
            found |= owner["tag"] == "MEX"
            parts.append({"owner": target if owner["tag"] in {"MEX", "UCA"} and state_id == "STATE_CHIAPAS" else target if owner["tag"] == "MEX" else owner["tag"], "provinces": owner["provinces"]})
        if not found:
            raise RuntimeError(f"{state_id} no longer contains MEX")
        states[state_id] = {"split": parts, "pops": "drop", "buildings": "drop"}
    card = {"version": 1, "title": "Kart 5B — Yeni Endülüs ve Maya Çekirdekleri", "description": "Dünya siyasi iskeleti: Meksika havzası–Veracruz bağlantısı Yeni Endülüs'e, Yucatán ve Chiapas'taki MEX payları Maya Birliği'ne gider. İç Meksika sonraki yerel kartlar için geçici sahibiyle kalır.", "countries": COUNTRIES, "states": states}
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
