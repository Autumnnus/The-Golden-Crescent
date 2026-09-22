"""Build the documented Poland--Lithuania core without inventing Galicia's border."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUS_CATALOG = ROOT / "build/political-rus-catalog.json"
PRU_CATALOG = ROOT / "build/political-pru-catalog.json"
TARGET = Path(__file__).with_name("card12.json")

# The written atlas explicitly gives the Commonwealth a Polish core, Lithuanian
# lands and eastern Ruthen regions.  Krakow and both Galician state regions are
# deliberately omitted: their internal owner/constitutional status has not yet
# been decided, so this card never pretends that the whole historical Galicia is
# one direct province block.
TARGETS = {
    "STATE_GREATER_POLAND": ("RUS", "VPL"),
    "STATE_LESSER_POLAND": ("RUS", "VPL"),
    "STATE_POSEN": ("PRU", "VPL"),
    "STATE_KAUNAS": ("RUS", "VPL"),
    "STATE_BREST": ("RUS", "VPL"),
    "STATE_MINSK": ("RUS", "VPL"),
    "STATE_VOLHYNIA": ("RUS", "VPL"),
    "STATE_CHERNIHIV": ("RUS", "VPL"),
    "STATE_CHERSON": ("RUS", "VPL"),
    "STATE_GALICH": ("RUS", "VPL"),
    "STATE_KHARKOV": ("RUS", "VPL"),
    "STATE_KIEV": ("RUS", "VPL"),
    "STATE_MAZOVIA": ("RUS", "VPL"),
    "STATE_MOGILEV": ("RUS", "VPL"),
    "STATE_VILNIUS": ("RUS", "VPL"),
    "STATE_VITEBSK": ("RUS", "VPL"),
}
COUNTRIES = {
    "VPL": {
        "name": "Polish-Lithuanian Commonwealth",
        "name_tr": "Lehistan-Litvanya Birliği",
        "color": [173, 72, 89],
        "country_type": "recognized",
        "tier": "kingdom",
        "cultures": ["polish"],
        "religion": "catholic",
        "capital": "STATE_GREATER_POLAND",
    },
}


def load_catalog(tag: str, path: Path) -> dict[str, dict]:
    subprocess.run(
        [sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", tag, "--out", str(path)],
        cwd=ROOT,
        check=True,
    )
    return {state["id"]: state for state in json.loads(path.read_text())["states"]}


def main() -> None:
    catalogs = {"RUS": load_catalog("RUS", RUS_CATALOG), "PRU": load_catalog("PRU", PRU_CATALOG)}
    states = {}
    for state_id, (old_owner, new_owner) in TARGETS.items():
        source = catalogs[old_owner]
        if state_id not in source:
            raise RuntimeError(f"{state_id} not found in {old_owner} catalog")
        parts, found = [], False
        for owner in source[state_id]["owners"]:
            found |= owner["tag"] == old_owner
            parts.append({"owner": new_owner if owner["tag"] == old_owner else owner["tag"], "provinces": owner["provinces"]})
        if not found:
            raise RuntimeError(f"{state_id} no longer includes {old_owner}")
        states[state_id] = {"split": parts, "pops": "drop", "buildings": "drop"}
    card = {
        "version": 1,
        "title": "Kart 1G — Lehistan-Litvanya Çekirdeği",
        "description": "Dünya siyasi iskeleti: Varşova merkezli Lehistan-Litvanya'nın Leh, Litvan ve doğu Ruthen çekirdeği. Karadeniz'e kadar uzanan Ruthen state'leri birliğin çok dilli doğu kanadıdır; Kraków ile Avusturya Galiçyası bu kararda yer almaz. Nüfus ve ekonomi verisi taşınmaz.",
        "countries": COUNTRIES,
        "states": states,
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
