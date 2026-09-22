"""Remove vanilla Egyptian rule from the documented independent Sennaar core."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-egy-catalog.json"
TARGET = Path(__file__).with_name("card13.json")
STATE = "STATE_BLUE_NILE"
COUNTRIES = {
    "VSN": {
        "name": "Sultanate of Sennaar",
        "name_tr": "Sennaar Sultanlığı",
        "color": [126, 106, 69],
        "country_type": "recognized",
        "tier": "principality",
        "cultures": ["sudanese"],
        "religion": "sunni",
        "capital": STATE,
    }
}


def main() -> None:
    subprocess.run(
        [sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "EGY", "--out", str(CATALOG)],
        cwd=ROOT,
        check=True,
    )
    states = {state["id"]: state for state in json.loads(CATALOG.read_text())["states"]}
    source = states[STATE]
    parts, found = [], False
    for owner in source["owners"]:
        found |= owner["tag"] == "EGY"
        parts.append({"owner": "VSN" if owner["tag"] == "EGY" else owner["tag"], "provinces": owner["provinces"]})
    if not found:
        raise RuntimeError(f"{STATE} no longer includes EGY")
    card = {
        "version": 1,
        "title": "Kart 4C — Sennaar",
        "description": "Dünya siyasi iskeleti: Mısır'ın doğrudan nehir yönetimi Dongola'da biter; Mavi Nil havzası bağımsız Sennaar Sultanlığı'dır. Kordofan ve Eritre, yazılı kaynak tek bir doğrudan owner belirlemediği için bu karta alınmaz.",
        "countries": COUNTRIES,
        "states": {STATE: {"split": parts, "pops": "drop", "buildings": "drop"}},
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, 1 state record)")


if __name__ == "__main__":
    main()
