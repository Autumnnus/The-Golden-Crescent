"""Build the India political card, including the final Portuguese harbour shares."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-bic-catalog.json"
TARGET = Path(__file__).with_name("card02.json")

# A target is named only where the written atlas has a political actor. Existing
# non-BIC owners are retained, except for the two temporary Portuguese harbour
# shares which return to their local political actors in this same state rewrite.
BIC_TARGETS = {
    "STATE_AGRA": "MUG", "STATE_ARAKAN": "BUR", "STATE_ASSAM": "ASM", "STATE_AWADH": "AWA",
    "STATE_BIHAR": "BGL", "STATE_BOMBAY": "MAR", "STATE_CENTRAL_PROVINCES": "NAG",
    "STATE_CIRCARS": "HYD", "STATE_DELHI": "MUG", "STATE_EAST_BENGAL": "BGL",
    "STATE_GUJARAT": "GJT", "STATE_HILL_PUNJAB": "PNJ", "STATE_KURNOOL": "HYD",
    "STATE_MADRAS": "TAM", "STATE_MYSORE": "MYS", "STATE_ORISSA": "ORI", "STATE_PEGU": "BUR",
    "STATE_RAJPUTANA": "JAI", "STATE_TENASSERIM": "BUR", "STATE_TRAVANCORE": "TRA",
    "STATE_WEST_BENGAL": "BGL",
}
COUNTRIES = {
    "MUG": {"name": "Mughal Empire", "name_tr": "Gurkanî İmparatorluğu", "color": [45, 112, 66], "country_type": "recognized", "tier": "empire", "cultures": ["hindustani"], "religion": "sunni", "capital": "STATE_DELHI"},
    "PNJ": {"name": "Sikh State", "name_tr": "Sih Devleti", "color": [167, 127, 69], "country_type": "recognized", "tier": "kingdom", "cultures": ["panjabi"], "religion": "sikh", "capital": "STATE_HILL_PUNJAB"},
    "BGL": {"name": "Bengal Sultanate", "name_tr": "Bengal Sultanlığı", "color": [74, 143, 140], "country_type": "recognized", "tier": "kingdom", "cultures": ["bengali"], "religion": "sunni", "capital": "STATE_EAST_BENGAL"},
    "MAR": {"name": "Maratha Confederation", "name_tr": "Maratha Konfederasyonu", "color": [179, 109, 73], "country_type": "recognized", "tier": "kingdom", "cultures": ["marathi"], "religion": "hindu", "capital": "STATE_BOMBAY"},
    "GJT": {"name": "Gujarat Port League", "name_tr": "Gujarat Liman Birliği", "color": [168, 154, 76], "country_type": "recognized", "tier": "principality", "cultures": ["gujarati"], "religion": "sunni", "capital": "STATE_GUJARAT"},
    "TAM": {"name": "Tamil Kingdoms", "name_tr": "Tamil Krallıkları", "color": [144, 86, 145], "country_type": "recognized", "tier": "principality", "cultures": ["tamil"], "religion": "hindu", "capital": "STATE_MADRAS"},
    "ORI": {"name": "Odisha Kingdom", "name_tr": "Orissa Krallığı", "color": [103, 142, 91], "country_type": "recognized", "tier": "principality", "cultures": ["oriya"], "religion": "hindu", "capital": "STATE_ORISSA"},
    # Existing local countries need explicit identities when their BIC share is expanded.
    "AWA": {"name": "Awadh", "name_tr": "Awadh", "color": [122, 179, 97], "country_type": "recognized", "tier": "kingdom", "cultures": ["hindustani"], "religion": "shiite", "capital": "STATE_AWADH"},
    "ASM": {"name": "Assam", "name_tr": "Assam", "color": [163, 5, 77], "country_type": "recognized", "tier": "kingdom", "cultures": ["assamese"], "religion": "hindu", "capital": "STATE_ASSAM"},
    "NAG": {"name": "Nagpur", "name_tr": "Nagpur", "color": [120, 148, 140], "country_type": "recognized", "tier": "principality", "cultures": ["marathi"], "religion": "hindu", "capital": "STATE_CENTRAL_PROVINCES"},
    "HYD": {"name": "Hyderabad", "name_tr": "Haydarabad", "color": [89, 141, 140], "country_type": "recognized", "tier": "kingdom", "cultures": ["telegu"], "religion": "sunni", "capital": "STATE_HYDERABAD"},
    "MYS": {"name": "Mysore", "name_tr": "Mysore", "color": [112, 151, 103], "country_type": "recognized", "tier": "kingdom", "cultures": ["kannada"], "religion": "hindu", "capital": "STATE_MYSORE"},
    "TRA": {"name": "Travancore", "name_tr": "Travankor", "color": [134, 166, 117], "country_type": "recognized", "tier": "principality", "cultures": ["malayalam"], "religion": "hindu", "capital": "STATE_TRAVANCORE"},
    "BUR": {"name": "Burma", "name_tr": "Burma", "color": [109, 168, 127], "country_type": "recognized", "tier": "kingdom", "cultures": ["burmese"], "religion": "theravada", "capital": "STATE_MANDALAY"},
    "JAI": {"name": "Jaipur", "name_tr": "Jaipur", "color": [79, 89, 182], "country_type": "recognized", "tier": "principality", "cultures": ["rajput"], "religion": "hindu", "capital": "STATE_RAJPUTANA"},
}


def refresh_catalog() -> dict:
    subprocess.run([sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "BIC", "--out", str(CATALOG)], cwd=ROOT, check=True)
    return json.loads(CATALOG.read_text())


def main() -> None:
    catalog = refresh_catalog()
    states = {}
    seen = set()
    temporary_targets = {
        ("POR", "STATE_BOMBAY"): "MAR",
        ("POR", "STATE_GUJARAT"): "GJT",
        ("FRA", "STATE_MADRAS"): "TAM",
    }
    for state in catalog["states"]:
        state_id = state["id"]
        has_bic = any(owner["tag"] == "BIC" for owner in state["owners"])
        has_temporary_share = any(
            (owner["tag"], state_id) in temporary_targets for owner in state["owners"]
        )
        if not has_bic and not has_temporary_share:
            continue
        target = BIC_TARGETS.get(state_id)
        if has_bic and target is None:
            raise RuntimeError(f"missing target for BIC share in {state_id}")
        if has_bic:
            seen.add(state_id)
        parts_by_owner = {}
        order = []
        for owner in state["owners"]:
            owner_tag = owner["tag"]
            final_owner = target if owner_tag == "BIC" else temporary_targets.get((owner_tag, state_id), owner_tag)
            # S4 defines the Sikh core as the northern/eastern Punjab hills.
            # PAN's lowland share (and Lahore) is handled separately by card56;
            # only the actual PAN provinces in this already-rewritten state move.
            if state_id == "STATE_HILL_PUNJAB" and owner_tag == "PAN":
                final_owner = "PNJ"
            if final_owner not in parts_by_owner:
                parts_by_owner[final_owner] = []
                order.append(final_owner)
            parts_by_owner[final_owner].extend(owner["provinces"])
        states[state_id] = {
            "split": [{"owner": tag, "provinces": parts_by_owner[tag]} for tag in order],
            "pops": "drop",
            "buildings": "drop",
        }
    if seen != set(BIC_TARGETS):
        raise RuntimeError(f"catalog target mismatch: saw={sorted(seen)} expected={sorted(BIC_TARGETS)}")
    card = {
        "version": 2,
        "title": "Kart 2A — BIC Sonrası Hindistan",
        "description": "Dünya siyasi iskeleti: BIC'nin tüm doğrudan province payları ile Bombay/Gujarat'taki son geçici Portekiz ve Madras'taki Fransız liman payları yerel devletlere aktarılır; nüfus, ekonomi, hukuk, ordu ve yeni diplomasi üretmez.",
        "countries": COUNTRIES,
        "states": states,
        "diplomacy": {"mode": "inherit", "reset_countries": ["BIC"]},
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} BIC replacement state records)")


if __name__ == "__main__":
    main()
