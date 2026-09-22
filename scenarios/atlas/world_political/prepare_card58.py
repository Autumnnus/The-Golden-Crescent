"""Record the selected Indian Ocean port-contract climate without new subjects."""

from __future__ import annotations

import json
from pathlib import Path


OUT = Path(__file__).with_name("card58.json")


def main() -> None:
    card = {
        "version": 2,
        "title": "Kart 3F/4F — Hint Okyanusu liman sözleşmeleri",
        "description": "Dört Güneydoğu Asya ve bir Svahili liman sözleşmesinin başlangıç siyasi iklimini kaydeder. Bu ilişkiler state sahibi veya subject yaratmaz; ilgili ev sahibi bütün province egemenliğini korur.",
        "countries": {},
        "states": {},
        "diplomacy": {
            "mode": "inherit",
            "relations": [
                {"actor": "EGY", "target": "ACE", "value": 25},
                {"actor": "EGY", "target": "SLW", "value": 20},
                {"actor": "OMA", "target": "JOH", "value": 25},
                {"actor": "OMA", "target": "SUL", "value": 10},
                {"actor": "OMA", "target": "MBS", "value": 10},
            ],
        },
    }
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
