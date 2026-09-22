"""Separate the documented German cores from the remaining Prussian question."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-pru-catalog.json"
TARGET = Path(__file__).with_name("card07.json")

# East/West Prussia and Silesia lack an accepted written owner. They
# intentionally remain PRU here. Posen is handled by the separate documented
# Poland--Lithuania card, rather than being silently folded into Brandenburg.
TARGETS = {
    "STATE_BRANDENBURG": ("PRU", "VBR"),
    "STATE_POMERANIA": ("PRU", "VPM"),
    "STATE_NORTH_RHINE": ("PRU", "VRC"),
    "STATE_RHINELAND": ("PRU", "VRC"),
    "STATE_RUHR": ("PRU", "VRC"),
    "STATE_WESTPHALIA": ("PRU", "VRC"),
    "STATE_ANHALT": ("PRU", "ANH"),
}
COUNTRIES = {
    "VBR": {"name": "Margraviate of Brandenburg", "name_tr": "Brandenburg Marklığı", "color": [83, 119, 152], "country_type": "recognized", "tier": "kingdom", "cultures": ["north_german"], "religion": "protestant", "capital": "STATE_BRANDENBURG"},
    "VPM": {"name": "Duchy of Pomerania", "name_tr": "Pomeranya Dükalığı", "color": [108, 141, 103], "country_type": "recognized", "tier": "principality", "cultures": ["north_german"], "religion": "protestant", "capital": "STATE_POMERANIA"},
    "VRC": {"name": "Rhine City League", "name_tr": "Ren Kent Birliği", "color": [153, 107, 77], "country_type": "recognized", "tier": "principality", "cultures": ["north_german"], "religion": "protestant", "capital": "STATE_RUHR"},
    "ANH": {"name": "Principality of Anhalt", "name_tr": "Anhalt Prensliği", "color": [103, 141, 151], "country_type": "recognized", "tier": "principality", "cultures": ["north_german"], "religion": "protestant", "capital": "STATE_ANHALT"},
    "PRU": {"name": "Unresolved Prussian Remnant", "name_tr": "Geçici Prusya Kalıntısı", "color": [125, 125, 125], "country_type": "recognized", "tier": "principality", "cultures": ["north_german"], "religion": "protestant", "capital": "STATE_EAST_PRUSSIA", "companies": {"mode": "replace", "add": [], "remove": []}},
}


def main() -> None:
    subprocess.run([sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "PRU", "--out", str(CATALOG)], cwd=ROOT, check=True)
    by_id = {state["id"]: state for state in json.loads(CATALOG.read_text())["states"]}
    states = {}
    for state_id, (old_owner, new_owner) in TARGETS.items():
        parts, found = [], False
        for owner in by_id[state_id]["owners"]:
            found |= owner["tag"] == old_owner
            parts.append({"owner": new_owner if owner["tag"] == old_owner else owner["tag"], "provinces": owner["provinces"]})
        if not found:
            raise RuntimeError(f"{state_id} no longer includes {old_owner}")
        states[state_id] = {"split": parts, "pops": "drop", "buildings": "drop"}
    card = {"version": 1, "title": "Kart 1C — Alman Çekirdekleri", "description": "Dünya siyasi iskeleti: Brandenburg, Pomeranya, Ren kent birliği ve Anhalt'ın doğrulanmış çekirdekleri. Doğu/Batı Prusya ve Silezya yazılı karar gelene kadar geçici PRU sahibinde kalır; Posen Lehistan--Litvanya kartındadır.", "countries": COUNTRIES, "states": states}
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
