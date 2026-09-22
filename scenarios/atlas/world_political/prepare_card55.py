"""Close Yemen's state-level border without inventing a unitary Yemen."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build" / "political-yemen-closure-catalog.json"
TARGET = Path(__file__).with_name("card55.json")
STATE = "STATE_YEMEN"


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", "HDJ,LAH,ZAI,MAH,KAT", "--out", str(CATALOG)],
        cwd=ROOT,
        check=True,
    )
    state = next(row for row in json.loads(CATALOG.read_text())["states"] if row["id"] == STATE)
    saw_hedjaz = False
    provinces_by_owner: dict[str, list[str]] = {}
    order: list[str] = []
    for owner in state["owners"]:
        tag = "LAH" if owner["tag"] == "HDJ" else owner["tag"]
        saw_hedjaz |= owner["tag"] == "HDJ"
        if tag not in provinces_by_owner:
            provinces_by_owner[tag] = []
            order.append(tag)
        provinces_by_owner[tag].extend("x" + province[1:].upper() for province in owner["provinces"])
    if not saw_hedjaz:
        raise RuntimeError(f"{STATE} no longer includes the Hedjaz share")
    card = {
        "version": 1,
        "title": "Kart 0D — Yemen'in Yerel Kıyı Düzeni",
        "description": "Yemen yaylaları Zeydi imamlıkta, Aden ve yakın kıyı Lahic'te, doğu kıyı ağları Mahra ile Kathîr'de kalır. Hicaz'ın Yemen state'indeki sınır dışı beş province payı Lahic'e devredilir; Hicaz yalnız kutsal kentler ve kendi kıyısındaki şerifliktir.",
        "countries": {},
        "states": {STATE: {"split": [{"owner": tag, "provinces": provinces_by_owner[tag]} for tag in order], "pops": "drop", "buildings": "drop"}},
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
