"""Return the remaining French Guyana share to the documented Dutch settlement."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = Path(__file__).with_name("card46.json")
STATE = "STATE_GUAYANA"


def main() -> None:
    catalog = ROOT / "build/political-fra-guyana-catalog.json"
    subprocess.run(
        [sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", "FRA", "--out", str(catalog)],
        cwd=ROOT,
        check=True,
    )
    state = next(row for row in json.loads(catalog.read_text())["states"] if row["id"] == STATE)
    owners, order = {}, []
    for row in state["owners"]:
        tag = "NET" if row["tag"] in {"FRA", "GBR"} else row["tag"]
        if tag not in owners:
            owners[tag] = []
            order.append(tag)
        owners[tag].extend(row["provinces"])
    if not {"FRA", "GBR"}.issubset({row["tag"] for row in state["owners"]}):
        raise RuntimeError(f"{STATE} no longer has both French and British shares")
    card = {
        "version": 1,
        "title": "Kart 5T — Guyana Yerleşimleri",
        "description": "Dünya siyasi iskeleti: Guyana'daki Fransız ve Britanya doğrudan province payları, diplomasi defterinin Hollanda Guyana yerleşimi kararına göre Hollanda'ya döner. Yerleşimlerin sonraki şirket/bağlılık statüsü bu kartta değiştirilmez.",
        "countries": {},
        "states": {
            STATE: {
                "split": [{"owner": tag, "provinces": owners[tag]} for tag in order],
                "pops": "drop",
                "buildings": "drop",
            }
        },
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
