"""Build the unambiguous Caribbean core of the Pearl Islands colony system."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = Path(__file__).with_name("card14.json")
CATALOGS = {tag: ROOT / f"build/political-{tag.lower()}-catalog.json" for tag in ("CUB", "GBR", "PCO")}
TARGETS = {
    "STATE_WESTERN_CUBA": ("CUB", "VPI"),
    "STATE_CENTRAL_CUBA": ("CUB", "VPI"),
    "STATE_EASTERN_CUBA": ("CUB", "VPI"),
    "STATE_JAMAICA": ("GBR", "VPI"),
    "STATE_PUERTO_RICO": ("PCO", "VPI"),
}
COUNTRIES = {
    "VPI": {
        "name": "Pearl Islands Colonial Council",
        "name_tr": "İnci Adaları Koloni Meclisi",
        "color": [130, 88, 124],
        "country_type": "recognized",
        "tier": "principality",
        "cultures": ["caribeno"],
        "religion": "catholic",
        "capital": "STATE_WESTERN_CUBA",
    }
}


def load_catalog(tag: str) -> dict[str, dict]:
    path = CATALOGS[tag]
    subprocess.run(
        [sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", tag, "--out", str(path)],
        cwd=ROOT,
        check=True,
    )
    return {state["id"]: state for state in json.loads(path.read_text())["states"]}


def main() -> None:
    catalogs = {tag: load_catalog(tag) for tag in CATALOGS}
    states = {}
    for state_id, (old_owner, new_owner) in TARGETS.items():
        source = catalogs[old_owner][state_id]
        parts, found = [], False
        for owner in source["owners"]:
            found |= owner["tag"] == old_owner
            parts.append({"owner": new_owner if owner["tag"] == old_owner else owner["tag"], "provinces": owner["provinces"]})
        if not found:
            raise RuntimeError(f"{state_id} no longer includes {old_owner}")
        states[state_id] = {"split": parts, "pops": "drop", "buildings": "drop"}
    card = {
        "version": 1,
        "title": "Kart 5C — İnci Adaları Çekirdeği",
        "description": "Dünya siyasi iskeleti: Küba, Jamaika ve Porto Riko'daki doğrudan ada çekirdekleri Endülüs'ün İnci Adaları koloni sistemine geçer. Santo Domingo/Haiti, farklı yerel idaresi için ayrı sınır kartında kararlaştırılır; diplomatik sömürge şartı V2 aşamasına bırakılır.",
        "countries": COUNTRIES,
        "states": states,
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
