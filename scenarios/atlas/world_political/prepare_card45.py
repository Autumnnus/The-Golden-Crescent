"""Remove Portugal after its final four shares are merged into regional cards."""
from __future__ import annotations

import json
from pathlib import Path


TARGET = Path(__file__).with_name("card45.json")


def main() -> None:
    card = {
        "version": 2,
        "title": "Kart 1L — Portekiz Geçici Sahibinin Kapanışı",
        "description": "Portekiz'in son doğrudan payları ilgili Hindistan, Çin ve Takımada kartlarında yerel sahiplere devredildikten sonra miras diplomasi kayıtları temizlenir. Bu siyasi iskelet kartı mekanik başlangıç verisi üretmez.",
        "countries": {},
        "states": {},
        "diplomacy": {"mode": "inherit", "reset_countries": ["POR"]},
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
