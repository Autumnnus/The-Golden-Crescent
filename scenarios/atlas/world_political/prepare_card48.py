"""Move Newfoundland's direct British holding into the documented Vinland core."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = Path(__file__).with_name("card48.json")
STATE = "STATE_NEWFOUNDLAND"

def main() -> None:
    catalog = ROOT / "build/political-gbr-newfoundland-catalog.json"
    subprocess.run([sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", "GBR", "--out", str(catalog)], cwd=ROOT, check=True)
    state = next(item for item in json.loads(catalog.read_text())["states"] if item["id"] == STATE)
    owners = {}
    for row in state["owners"]:
        tag = "VIN" if row["tag"] == "GBR" else row["tag"]
        owners.setdefault(tag, []).extend(row["provinces"])
    if "GBR" not in {row["tag"] for row in state["owners"]}:
        raise RuntimeError("Newfoundland no longer has a British share")
    card = {"version": 1, "title": "Kart 5V — Vinland Newfoundland Çekirdeği", "description": "Dünya siyasi iskeleti: Newfoundland'daki Britanya doğrudan payı, yazılı atlasın Kalmar ortak tacına bağlı Vinland kıyı çekirdeğine aktarılır. Labrador'un istasyon/yerel alan ayrımı bu state dışında karara bağlanacaktır.", "countries": {}, "states": {STATE: {"split": [{"owner": tag, "provinces": provinces} for tag, provinces in owners.items()], "pops": "drop", "buildings": "drop"}}}
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
if __name__ == "__main__": main()
