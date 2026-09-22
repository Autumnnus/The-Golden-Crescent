"""Close the documented African foreign-enclave exceptions with local owners."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build" / "political-africa-closure-catalog.json"
TARGET = Path(__file__).with_name("card54.json")
TARGETS = {
    "STATE_KORDOFAN": {"EGY": "DFR"},
    "STATE_ERITREA": {"EGY": "AWS"},
    "STATE_GOLD_COAST": {"DEN": "ASH", "NET": "ASH", "SIL": "ASH"},
}


def main() -> None:
    subprocess.run(
        [sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "DFR,TGR,ASH,EGY,DEN,NET", "--out", str(CATALOG)],
        cwd=ROOT,
        check=True,
    )
    by_id = {state["id"]: state for state in json.loads(CATALOG.read_text())["states"]}
    states = {}
    for state_id, replacements in TARGETS.items():
        parts, found = [], set()
        for owner in by_id[state_id]["owners"]:
            tag = replacements.get(owner["tag"], owner["tag"])
            if owner["tag"] in replacements:
                found.add(owner["tag"])
            parts.append({"owner": tag, "provinces": owner["provinces"]})
        if found != set(replacements):
            raise RuntimeError(f"{state_id} missing expected owners: {set(replacements) - found}")
        states[state_id] = {"split": parts, "pops": "drop", "buildings": "drop"}
    card = {
        "version": 1,
        "title": "Kart 4D — Afrika Yerel Egemenlik Kapanışı",
        "description": "Dünya siyasi iskeleti: Mısır'ın Dongola dışındaki Kordofan ve Eritre doğrudan payları Darfur ile mevcut Afar yönetimine döner. Altın Sahil'deki Danimarka ve Hollanda depo payları Aşanti egemenliğine katılır; liman sözleşmeleri toprak devri değildir.",
        "countries": {},
        "states": states,
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(states)} states)")


if __name__ == "__main__":
    main()
