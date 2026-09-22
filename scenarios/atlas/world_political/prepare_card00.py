"""Extract the already verified political layer of Phase 1B.4B into Card 0.

The resulting V1 file is intentionally map-only.  It is a preview source, not
the active V2 world and must not be used to build the mod.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "scenarios/atlas/phase01b4b_independent_belt/scenario.json"
TARGET = Path(__file__).with_name("card00.json")
COUNTRY_FIELDS = ("name", "name_tr", "color", "country_type", "tier", "cultures", "religion", "capital")

# These entries are political decisions already made in docs/scenario/dunya_atlasi.md.
# They deliberately stop at whole states except Laristan, where the verified
# vanilla coastal split lets Kerman retain Bender Abbas without taking Oman or
# Bahrain.  The broader Caucasus and Central Asian card remains separate.
IRAN_COUNTRIES = {
    "ISF": {"name": "Isfahan Shahdom", "name_tr": "İsfahan Şahlığı", "color": [112, 86, 176], "country_type": "recognized", "tier": "kingdom", "cultures": ["persian"], "religion": "shiite", "capital": "STATE_ISFAHAN"},
    "TBR": {"name": "Tabriz Shahdom", "name_tr": "Tebriz Şahlığı", "color": [178, 105, 74], "country_type": "recognized", "tier": "kingdom", "cultures": ["azerbaijani"], "religion": "shiite", "capital": "STATE_TABRIZ"},
    "KHO": {"name": "Khorasan State", "name_tr": "Horasan Devleti", "color": [177, 146, 74], "country_type": "recognized", "tier": "kingdom", "cultures": ["persian"], "religion": "shiite", "capital": "STATE_KHORASAN"},
    "MAZ": {"name": "Mazandaran Shahdom", "name_tr": "Mazenderan Şahlığı", "color": [80, 143, 105], "country_type": "recognized", "tier": "principality", "cultures": ["persian"], "religion": "shiite", "capital": "STATE_MAZANDARAN"},
    "KRM": {"name": "Kerman Emirate", "name_tr": "Kirman Emirliği", "color": [187, 122, 154], "country_type": "recognized", "tier": "principality", "cultures": ["persian"], "religion": "shiite", "capital": "STATE_KERMAN"},
    "LUR": {"name": "Luristan Government", "name_tr": "Luristan Yönetimi", "color": [105, 128, 76], "country_type": "recognized", "tier": "principality", "cultures": ["luri"], "religion": "shiite", "capital": "STATE_LURISTAN"},
    "HUZ": {"name": "Khuzestan Emirate", "name_tr": "Huzistan Emirliği", "color": [74, 145, 158], "country_type": "recognized", "tier": "principality", "cultures": ["mashriqi"], "religion": "shiite", "capital": "STATE_KHUZESTAN"},
}
IRAN_STATES = {
    "STATE_ISFAHAN": "ISF", "STATE_FARS": "ISF", "STATE_IRAKAJEMI": "ISF", "STATE_SEMNAN": "ISF",
    "STATE_TABRIZ": "TBR", "STATE_URMIA": "TBR", "STATE_KHORASAN": "KHO", "STATE_MAZANDARAN": "MAZ",
    "STATE_KERMAN": "KRM", "STATE_LURISTAN": "LUR", "STATE_PERSIAN_KURDISTAN": "LUR", "STATE_KHUZESTAN": "HUZ",
    "STATE_LARISTAN": {
        "split": [
            {"owner": "KRM", "provinces": ["x1BC9CB", "x3FA81D", "x407020", "x517637", "x922EDA", "x9DF415", "xA54E11", "xB67223", "xF14D58"]},
            {"owner": "OMA", "provinces": ["xAAA21C", "x876E91", "x0170A0", "x350DED", "x75B0BE", "x36F270", "x42FC41", "x2F832B", "x8070A0"]},
            {"owner": "BHN", "provinces": ["xB80596"]},
        ]
    },
}
RUS_BORDER_STATES = {"STATE_KARS": "ERZ"}


def main() -> None:
    source = json.loads(SOURCE.read_text())
    countries = {
        tag: {field: country[field] for field in COUNTRY_FIELDS}
        for tag, country in source["countries"].items()
    }
    countries.update(IRAN_COUNTRIES)
    states = {
        state: {
            **{field: spec[field] for field in ("owner", "split") if field in spec},
            # A political card must not accidentally become a runnable economy.
            # Dropping inherited history also avoids technology checks for a port
            # that belongs to a newly introduced map-only country.
            "pops": "drop",
            "buildings": "drop",
        }
        for state, spec in source["states"].items()
        if "owner" in spec or "split" in spec
    }
    for state, owner in IRAN_STATES.items():
        states[state] = {
            **({"owner": owner} if isinstance(owner, str) else owner),
            "pops": "drop",
            "buildings": "drop",
        }
    # Dobrudja is the documented Tuna Emirate/Bulgarian plain.  The earlier
    # political extraction retained one vanilla RUS province; the full northern
    # Eurasia pass must not leave it as an unexplained Russian outpost.
    dobrudja = states.get("STATE_DOBRUDJA")
    if dobrudja and "split" in dobrudja:
        for part in dobrudja["split"]:
            if part["owner"] == "RUS":
                part["owner"] = "BUL"
    # The written atlas places Kars on the Erzurum atabeylik's border line.
    # Pull actual province IDs from the vanilla catalogue instead of encoding a
    # guessed split beside the political decision. The whole state is the
    # border corridor, so the former Ottoman and Russian shares both pass to
    # Erzurum.
    if RUS_BORDER_STATES:
        catalog_path = ROOT / "build/political-card00-rus-catalog.json"
        subprocess.run(
            [sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", "RUS", "--out", str(catalog_path)],
            cwd=ROOT,
            check=True,
        )
        by_id = {state["id"]: state for state in json.loads(catalog_path.read_text())["states"]}
        for state_id, target in RUS_BORDER_STATES.items():
            parts, found = [], False
            for owner in by_id[state_id]["owners"]:
                found |= owner["tag"] == "RUS"
                parts.append({"owner": target, "provinces": owner["provinces"]})
            if not found:
                raise RuntimeError(f"{state_id} no longer includes RUS")
            states[state_id] = {"split": parts, "pops": "drop", "buildings": "drop"}
    referenced_owners = {
        part["owner"]
        for spec in states.values()
        for part in (spec.get("split") or ([{"owner": spec["owner"]}] if "owner" in spec else []))
    }
    for temporary in {"TUR"}:
        if temporary not in referenced_owners:
            countries.pop(temporary, None)
    card = {
        "version": 1,
        "title": "Kart 0 — Ortadoğu ve Balkanlar",
        "description": (
            "The Golden Crescent dünya siyasi iskeleti. Faz 1B.4B'nin yalnız doğrulanmış "
            "sınır ve ülke kimliği katmanını taşır; nüfus, ekonomi, hukuk, ordu ve diplomasi içermez."
        ),
        "countries": countries,
        "states": states,
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(countries)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
