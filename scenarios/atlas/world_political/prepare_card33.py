"""Build the Indonesian political card, including the final Portuguese Sunda share."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


R = Path(__file__).resolve().parents[3]
O = Path(__file__).with_name("card33.json")
T = {
    "STATE_ACEH": "ACE", "STATE_CELEBES": "SLW", "STATE_CENTRAL_JAVA": "YOG",
    "STATE_EAST_BORNEO": "BNJ", "STATE_EAST_JAVA": "SRK", "STATE_MOLUCCAS": "TID",
    "STATE_NORTH_SUMATRA": "SAK", "STATE_SOUTH_SUMATRA": "JMB", "STATE_SUNDA_ISLANDS": "BAL",
    "STATE_WEST_BORNEO": "PON",
}
C = {
    "DEI": {
        "name": "Residual Dutch East Indies Jurisdiction",
        "name_tr": "Geçici Hollanda Doğu Hint Yetki Alanı",
        "color": [125, 125, 125],
        "country_type": "recognized",
        "tier": "principality",
        "cultures": ["dutch"],
        "religion": "protestant",
        "capital": "STATE_WEST_JAVA",
        "companies": {"mode": "replace", "add": [], "remove": []},
    }
}


def main() -> None:
    catalog = R / "build/political-dei-catalog.json"
    subprocess.run(
        [sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", "DEI", "--out", str(catalog)],
        cwd=R,
        check=True,
    )
    by_id = {state["id"]: state for state in json.loads(catalog.read_text())["states"]}
    states = {}
    for state_id, target in T.items():
        parts_by_owner, order = {}, []
        for row in by_id[state_id]["owners"]:
            final_owner = target if row["tag"] in {"DEI", "POR"} and state_id == "STATE_SUNDA_ISLANDS" else target if row["tag"] == "DEI" else row["tag"]
            if final_owner not in parts_by_owner:
                parts_by_owner[final_owner] = []
                order.append(final_owner)
            parts_by_owner[final_owner].extend(row["provinces"])
        states[state_id] = {
            "split": [{"owner": tag, "provinces": parts_by_owner[tag]} for tag in order],
            "pops": "drop",
            "buildings": "drop",
        }
    card = {
        "version": 1,
        "title": "Kart 3C — Yerel Takımada Yönetimleri",
        "description": "DEI doğrudan payları Aceh, Java sarayları, Borneo sultanlıkları, Sulawesi ve Maluku yerel yönetimlerine aktarılır; Sunda'daki son geçici Portekiz liman payı Bali'ye döner. Batı Java, DEI doğrulama ankrajı olarak sonraki nihai aktarım kartına ayrılmıştır; Mısır/Umman liman imtiyazları diplomasi katmanında kurulacaktır.",
        "countries": C,
        "states": states,
    }
    O.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
