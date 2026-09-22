"""Dismantle the last direct British colonial remnants into local polities."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/world-political/british-remnants-catalog.json"
OUT = Path(__file__).with_name("card61.json")

REPLACEMENTS = {
    "STATE_SIERRA_LEONE": {"SIL": "TMN"},
    "STATE_CAPE_COLONY": {"SAF": "NAM"},
    "STATE_EASTERN_CAPE": {"SAF": "XHO"},
    "STATE_NORTHERN_CAPE": {"SAF": "TSW"},
    "STATE_IDAHO": {"ORG": "NZP"},
    # ORG is redefined below as a local Columbia River council; the direct
    # state owner remains the tag but no longer represents a British colony.
    "STATE_OREGON": {"ORG": "ORG"},
    "STATE_WASHINGTON": {"ORG": "SLS"},
    "STATE_NEW_BRUNSWICK": {"NBS": "VWM", "NVS": "VWM"},
}

COUNTRIES = {
    "ORG": {
        "name": "Columbia River Council", "name_tr": "Kolombiya Nehri Meclisi",
        "color": [91, 134, 139], "country_type": "unrecognized", "tier": "principality",
        "cultures": ["salish"], "religion": "animist", "capital": "STATE_OREGON",
    },
    "VWM": {
        "name": "Wabanaki Maritime Council", "name_tr": "Wabanaki Deniz Meclisi",
        "color": [111, 128, 91], "country_type": "unrecognized", "tier": "principality",
        "cultures": ["algonquian"], "religion": "animist", "capital": "STATE_NEW_BRUNSWICK",
    },
}


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", "SIL,ORG,SAF,NBS,NVS,MKT", "--out", str(CATALOG)],
        cwd=ROOT,
        check=True,
    )
    by_id = {state["id"]: state for state in json.loads(CATALOG.read_text())["states"]}
    states = {}
    for state_id, replacements in REPLACEMENTS.items():
        state = by_id.get(state_id)
        if state is None:
            raise RuntimeError(f"catalog misses {state_id}")
        grouped: dict[str, list[str]] = {}
        order: list[str] = []
        found = set()
        for entry in state["owners"]:
            source = entry["tag"]
            owner = replacements.get(source, source)
            if source in replacements:
                found.add(source)
            if owner not in grouped:
                grouped[owner] = []
                order.append(owner)
            grouped[owner].extend("x" + province[1:].upper() for province in entry["provinces"])
        if found != set(replacements):
            raise RuntimeError(f"{state_id}: missing {set(replacements) - found}")
        states[state_id] = {
            "split": [
                {"owner": owner, "provinces": list(dict.fromkeys(grouped[owner]))}
                for owner in order
            ],
            "pops": "drop", "buildings": "drop",
        }
    card = {
        "version": 2,
        "title": "Kart 4H/5Y — Britanya koloni kalıntılarının kapanışı",
        "description": "Sierra Leone, Cape, Columbia, Maritimes ve Mosquito kıyısındaki son Britanya sömürge/protektora sahipliği yerel devletlere döner. Quebec Vinland, Ontario Anişinabe ve British Columbia Salish eşlemeleri komşu mevcut kartlarda yapılır; Londra yalnız belgelendirilmiş küçük denizaşırı bağımlılıklarını korur.",
        "countries": COUNTRIES,
        "states": states,
        "diplomacy": {"mode": "inherit", "reset_countries": ["GBR", "SIL", "SAF", "NBS", "NVS"]},
    }
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
