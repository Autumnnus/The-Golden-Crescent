"""Move inherited capitals after their old state shares changed owner."""

from __future__ import annotations

import json
from pathlib import Path


OUT = Path(__file__).with_name("card62.json")

# These are existing local tags.  A state-level border decision removed each
# vanilla capital share, so retaining the old country definition would leave an
# invalid `capital` event target at game setup.  The replacement is a state the
# country still owns after all political cards are merged.
CAPITALS = {
    "DIO": "STATE_SENEGAL",
    "BGM": "STATE_GONDER",
    "TGR": "STATE_GONDER",
    "GJM": "STATE_GONDER",
    "MTB": "STATE_TRANSVAAL",
    "ATB": "STATE_ALASKA",
    "COO": "STATE_WEST_BENGAL",
    "JEY": "STATE_CIRCARS",
    "DGR": "STATE_MEKONG",
    "AIN": "STATE_SAKHALIN",
    "UZH": "STATE_SYRDARYA",
    "TEK": "STATE_WEST_SAHARA",
}


def main() -> None:
    card = {
        "version": 2,
        "title": "Kart 6A — Yerinden olmuş yerel başkentler",
        "description": "Önceki siyasi state/pay kararları eski başkenti artık ülke sahibinde olmayan yerel aktörlerin başkentini, hâlâ sahip oldukları state'e taşır. Yeni sınır veya ülke yaratmaz.",
        "countries": {tag: {"capital": state} for tag, state in CAPITALS.items()},
        "states": {},
        "diplomacy": {"mode": "inherit"},
    }
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
