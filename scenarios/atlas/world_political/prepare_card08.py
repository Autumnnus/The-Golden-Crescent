"""Separate the documented Milanese and Venetian cores from Austria."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-aus-catalog.json"
TARGET = Path(__file__).with_name("card08.json")
TARGETS = {"STATE_LOMBARDY": "VMI", "STATE_VENETIA": "VVE"}
COUNTRIES = {
    "VMI": {"name": "Milanese Republic", "name_tr": "Milano Cumhuriyeti", "color": [110, 140, 151], "country_type": "recognized", "tier": "kingdom", "cultures": ["north_italian"], "religion": "catholic", "capital": "STATE_LOMBARDY"},
    "VVE": {"name": "Venetian Republic", "name_tr": "Venedik Cumhuriyeti", "color": [154, 117, 78], "country_type": "recognized", "tier": "kingdom", "cultures": ["north_italian"], "religion": "catholic", "capital": "STATE_VENETIA"},
}


def main() -> None:
    subprocess.run([sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", "AUS", "--out", str(CATALOG)], cwd=ROOT, check=True)
    by_id = {state["id"]: state for state in json.loads(CATALOG.read_text())["states"]}
    states = {}
    for state_id, target in TARGETS.items():
        parts, found = [], False
        for owner in by_id[state_id]["owners"]:
            found |= owner["tag"] == "AUS"
            parts.append({"owner": target if owner["tag"] == "AUS" else owner["tag"], "provinces": owner["provinces"]})
        if not found:
            raise RuntimeError(f"{state_id} no longer contains AUS")
        states[state_id] = {"split": parts, "pops": "drop", "buildings": "drop"}
    card = {"version": 1, "title": "Kart 1D — Milano ve Venedik", "description": "Dünya siyasi iskeleti: Lombardiya ve Venetia'daki doğrudan Avusturya egemenliği iki bağımsız İtalyan aktöre ayrılır; mekanik başlangıç verisi üretmez.", "countries": COUNTRIES, "states": states}
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
