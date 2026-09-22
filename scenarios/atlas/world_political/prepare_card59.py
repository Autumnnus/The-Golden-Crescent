"""Represent Sokoto's explicit Gobir emirate compact, and no broader fiction."""

from __future__ import annotations

import json
from pathlib import Path


OUT = Path(__file__).with_name("card59.json")


def main() -> None:
    card = {
        "version": 2,
        "title": "Kart 4G — Sokoto ve Gobir emirlik sözleşmesi",
        "description": "Sokoto ortak makamı ile Gobir arasındaki yazılı emirlik sözleşmesini kurar. Bornu, Borgu ve Sahra/Tuareg ağları bu pact'a dahil edilmez; Massina–Timbuktu'nun kent şartı ayrı yerel hukuk kaydıdır.",
        "countries": {},
        "states": {},
        "subject_types": {
            "ve_emirate_compact": {
                "base": "vassal",
                "name": "Emirate Compact",
                "name_tr": "Emirlik Sözleşmesi",
                "overlord_types": ["recognized", "unrecognized"],
                "subject_types": ["recognized", "unrecognized"],
                "can_have_subjects": False,
                "join_overlord_wars": False,
                "income_transfer": 0.05,
            }
        },
        "diplomacy": {
            "mode": "inherit",
            "reset_countries": ["HAU"],
            "subjects": [
                {"overlord": "SOK", "subject": "HAU", "type": "ve_emirate_compact", "liberty_desire": 40}
            ],
        },
    }
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
