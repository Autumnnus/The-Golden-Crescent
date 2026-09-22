"""Map the three British crowns while preserving overseas decisions for later."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-gbr-catalog.json"
TARGET = Path(__file__).with_name("card09.json")
TARGETS = {
    "STATE_EAST_ANGLIA": "VEL", "STATE_HOME_COUNTIES": "VEL", "STATE_LANCASHIRE": "VEL", "STATE_MIDLANDS": "VEL", "STATE_WEST_COUNTRY": "VEL", "STATE_YORKSHIRE": "VEL", "STATE_WALES": "VEL",
    "STATE_HIGHLANDS": "VSC", "STATE_LOWLANDS": "VSC",
    "STATE_CONNAUGHT": "VIR", "STATE_LEINSTER": "VIR", "STATE_MUNSTER": "VIR", "STATE_ULSTER": "VIR",
}
COUNTRIES = {
    "VEL": {"name": "Crown of England and Wales", "name_tr": "İngiltere–Galler Tacı", "color": [151, 93, 86], "country_type": "recognized", "tier": "kingdom", "cultures": ["british", "welsh"], "religion": "catholic", "capital": "STATE_HOME_COUNTIES"},
    "VSC": {"name": "Crown of Scotland", "name_tr": "İskoçya Tacı", "color": [87, 126, 156], "country_type": "recognized", "tier": "kingdom", "cultures": ["scottish"], "religion": "protestant", "capital": "STATE_LOWLANDS"},
    "VIR": {"name": "Crown of Ireland", "name_tr": "İrlanda Tacı", "color": [101, 147, 106], "country_type": "recognized", "tier": "kingdom", "cultures": ["irish"], "religion": "catholic", "capital": "STATE_LEINSTER"},
    "GBR": {"name": "London Crown Overseas Dependencies", "name_tr": "Londra Tacı Denizaşırı Bağımlılıkları", "color": [125, 125, 125], "country_type": "recognized", "tier": "principality", "cultures": ["british"], "religion": "catholic", "capital": "STATE_BAHAMAS", "companies": {"mode": "replace", "add": [], "remove": []}},
}


def main() -> None:
    subprocess.run([sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "GBR", "--out", str(CATALOG)], cwd=ROOT, check=True)
    by_id = {state["id"]: state for state in json.loads(CATALOG.read_text())["states"]}
    states = {}
    for state_id, target in TARGETS.items():
        parts, found = [], False
        for owner in by_id[state_id]["owners"]:
            found |= owner["tag"] == "GBR"
            parts.append({"owner": target if owner["tag"] == "GBR" else owner["tag"], "provinces": owner["provinces"]})
        if not found:
            raise RuntimeError(f"{state_id} no longer contains GBR")
        states[state_id] = {"split": parts, "pops": "drop", "buildings": "drop"}
    card = {"version": 1, "title": "Kart 1E — Britanya Ortak Taçları", "description": "Dünya siyasi iskeleti: İngiltere–Galler, İskoçya ve İrlanda ayrı iç taçlar olarak eşlenir. Ortak hükümdarlık diplomaside kurulacak; Bahamalar, Bermuda, Güney Atlantik ve West Indies'teki kalan on bir province Londra Tacı'nın sınırlı denizaşırı doğrudan idaresidir.", "countries": COUNTRIES, "states": states}
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
