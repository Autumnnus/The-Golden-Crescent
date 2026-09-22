"""Build the Caucasus and Russian-core slice of the Middle East political card.

Every RUS share altered here is read from the current Atlas catalog.  North
Caucasus is the only province-level division: the catalog already identifies
the established Chechen and Circassian shares, so the remaining provinces can
be assigned to the documented Dagestan network without guessing a border.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-rus-core-catalog.json"
TARGET = Path(__file__).with_name("card04.json")

# These codes deliberately use the ve_ project namespace in spirit without
# colliding with vanilla three-letter tags.  They are political preview actors,
# not yet active game country definitions.
COUNTRIES = {
    "VGE": {"name": "Kingdom of Georgia", "name_tr": "Gürcistan Krallığı", "color": [118, 141, 171], "country_type": "recognized", "tier": "kingdom", "cultures": ["georgian"], "religion": "orthodox", "capital": "STATE_GREATER_CAUCASUS"},
    "VER": {"name": "Principality of Erevan", "name_tr": "Erevan Prensliği", "color": [174, 117, 86], "country_type": "recognized", "tier": "principality", "cultures": ["armenian"], "religion": "oriental_orthodox", "capital": "STATE_ARMENIA"},
    "VBA": {"name": "Khanate of Baku", "name_tr": "Bakü Hanlığı", "color": [72, 147, 156], "country_type": "recognized", "tier": "principality", "cultures": ["azerbaijani"], "religion": "shiite", "capital": "STATE_AZERBAIJAN"},
    "VDA": {"name": "Dagestan Imamate", "name_tr": "Dağıstan İmametleri", "color": [110, 133, 79], "country_type": "recognized", "tier": "principality", "cultures": ["north_caucasian", "chechen"], "religion": "sunni", "capital": "STATE_NORTH_CAUCASUS"},
    "VCR": {"name": "Crimean Khanate", "name_tr": "Kırım Hanlığı", "color": [157, 124, 75], "country_type": "recognized", "tier": "kingdom", "cultures": ["tatar"], "religion": "sunni", "capital": "STATE_CRIMEA"},
    "VTA": {"name": "Great Tatar Khanate", "name_tr": "Büyük Tatar Hanlığı", "color": [135, 101, 159], "country_type": "recognized", "tier": "kingdom", "cultures": ["tatar"], "religion": "sunni", "capital": "STATE_KAZAN"},
    "VKM": {"name": "Kalmyk Khanate", "name_tr": "Kalmuk Hanlığı", "color": [129, 147, 92], "country_type": "recognized", "tier": "principality", "cultures": ["mongol"], "religion": "gelugpa", "capital": "STATE_KALMYKIA"},
    "VMS": {"name": "Grand Principality of Moscow", "name_tr": "Moskova Büyük Prensliği", "color": [151, 101, 91], "country_type": "recognized", "tier": "kingdom", "cultures": ["russian"], "religion": "orthodox", "capital": "STATE_MOSCOW"},
    "VNG": {"name": "Novgorod Republic", "name_tr": "Novgorod Cumhuriyeti", "color": [75, 125, 146], "country_type": "recognized", "tier": "kingdom", "cultures": ["russian"], "religion": "orthodox", "capital": "STATE_NOVGOROD"},
    "VMA": {"name": "Mari Forest Council", "name_tr": "Mari Orman Meclisi", "color": [92, 138, 100], "country_type": "recognized", "tier": "principality", "cultures": ["mari"], "religion": "animist", "capital": "STATE_VYATKA"},
    "VMO": {"name": "Mordvin River Council", "name_tr": "Mordvin Nehir Meclisi", "color": [122, 138, 92], "country_type": "recognized", "tier": "principality", "cultures": ["mordvin"], "religion": "orthodox", "capital": "STATE_NIZHNY_NOVGOROD"},
    "VUR": {"name": "Ural Confederation", "name_tr": "Ural Konfederasyonu", "color": [116, 117, 91], "country_type": "recognized", "tier": "principality", "cultures": ["bashkir", "udmurt"], "religion": "sunni", "capital": "STATE_URAL"},
    "VOB": {"name": "Ob River Confederation", "name_tr": "Ob Nehri Konfederasyonu", "color": [74, 133, 130], "country_type": "recognized", "tier": "principality", "cultures": ["siberian"], "religion": "animist", "capital": "STATE_OB"},
    "VST": {"name": "Siberian Tatar League", "name_tr": "Sibirya Tatar Birliği", "color": [148, 112, 81], "country_type": "recognized", "tier": "principality", "cultures": ["tatar", "siberian"], "religion": "sunni", "capital": "STATE_TOBOLSK"},
    "VYE": {"name": "Yenisei Confederation", "name_tr": "Yenisey Konfederasyonu", "color": [81, 136, 149], "country_type": "recognized", "tier": "principality", "cultures": ["siberian"], "religion": "animist", "capital": "STATE_KRASNOYARSK"},
    "VBY": {"name": "Buryat Confederation", "name_tr": "Buryat Konfederasyonu", "color": [126, 140, 87], "country_type": "recognized", "tier": "principality", "cultures": ["buryat"], "religion": "gelugpa", "capital": "STATE_BURYATIA"},
    "VSA": {"name": "Sakha Republic", "name_tr": "Saha Cumhuriyeti", "color": [107, 135, 169], "country_type": "recognized", "tier": "principality", "cultures": ["yakut"], "religion": "animist", "capital": "STATE_YAKUTSK"},
    "VOK": {"name": "Okhotsk Coastal Assembly", "name_tr": "Ohotsk Kıyı Meclisi", "color": [83, 128, 154], "country_type": "recognized", "tier": "principality", "cultures": ["siberian"], "religion": "animist", "capital": "STATE_OKHOTSK"},
    "VKA": {"name": "Kamchatka Council", "name_tr": "Kamçatka Meclisi", "color": [105, 130, 106], "country_type": "recognized", "tier": "principality", "cultures": ["siberian"], "religion": "animist", "capital": "STATE_KAMCHATKA"},
    "VCH": {"name": "Chukotka Council", "name_tr": "Çukotka Meclisi", "color": [125, 117, 160], "country_type": "recognized", "tier": "principality", "cultures": ["siberian"], "religion": "animist", "capital": "STATE_CHUKOTKA"},
    "VKL": {"name": "Kolyma Peoples' Council", "name_tr": "Kolıma Halkları Meclisi", "color": [99, 111, 144], "country_type": "recognized", "tier": "principality", "cultures": ["siberian"], "religion": "animist", "capital": "STATE_KOLYMA"},
    "RUS": {"name": "Residual Russian Jurisdictions", "name_tr": "Geçici Rus Yetki Alanları", "color": [125, 125, 125], "country_type": "recognized", "tier": "principality", "cultures": ["russian"], "religion": "orthodox", "capital": "STATE_KARS", "companies": {"mode": "replace", "add": [], "remove": []}},
}
RUS_TARGETS = {
    "STATE_ARMENIA": "VER",
    "STATE_AZERBAIJAN": "VBA",
    "STATE_GREATER_CAUCASUS": "VGE",
    "STATE_CRIMEA": "VCR",
    "STATE_KAZAN": "VTA",
    "STATE_KALMYKIA": "VKM",
    "STATE_MOSCOW": "VMS",
    "STATE_NOVGOROD": "VNG",
    "STATE_ARKHANGELSK": "VNG",
    "STATE_EAST_KARELIA": "VNG",
    "STATE_INGRIA": "VNG",
    "STATE_KOLA": "VNG",
    "STATE_NENETSIA": "VNG",
    "STATE_PSKOV": "VNG",
    "STATE_TVER": "VMS",
    "STATE_RYAZAN": "VMS",
    "STATE_YAROSLAVL": "VMS",
    "STATE_TAMBOV": "VMS",
    "STATE_ORYOL": "VMS",
    "STATE_KURSK": "VMS",
    "STATE_SMOLENSK": "VMS",
    "STATE_ASTRAKHAN": "VTA",
    "STATE_ROSTOV": "VTA",
    "STATE_SAMARA": "VTA",
    "STATE_STAVROPOL": "VTA",
    "STATE_TARTARIA": "VTA",
    "STATE_TAURIDA": "VTA",
    "STATE_UFA": "VTA",
    "STATE_CHUVASHIA": "VMA",
    "STATE_VYATKA": "VMA",
    "STATE_NIZHNY_NOVGOROD": "VMO",
    "STATE_PERM": "VUR",
    "STATE_URAL": "VUR",
    "STATE_OB": "VOB",
    "STATE_SURGUT": "VOB",
    "STATE_TOBOLSK": "VST",
    "STATE_TOMSK": "VST",
    "STATE_KRASNOYARSK": "VYE",
    "STATE_UPPER_YENISEYSK": "VYE",
    "STATE_BURYATIA": "VBY",
    "STATE_IRKUTSK": "VBY",
    "STATE_TRANS_BAIKAL": "VBY",
    "STATE_YAKUTSK": "VSA",
    "STATE_OKHOTSK": "VOK",
    "STATE_KAMCHATKA": "VKA",
    "STATE_CHUKOTKA": "VCH",
    "STATE_KOLYMA": "VKL",
    "STATE_AKMOLINSK": "OZH",
    "STATE_CHELYABINSK": "OZH",
    "STATE_URALSK": "KZH",
    "STATE_BESSARABIA": "MOL",
    "STATE_RIGA": "UBD",
    "STATE_ELIZAVETPOL": "VBA",
    "STATE_DAGESTAN": "VDA",
    "STATE_KUBAN": "VCR",
}


def refresh_catalog() -> dict:
    subprocess.run(
        [sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "RUS", "--out", str(CATALOG)],
        cwd=ROOT,
        check=True,
    )
    return json.loads(CATALOG.read_text())


def direct_replacement(state: dict, target: str) -> dict:
    """Replace exactly the RUS-owned provinces while retaining all other owners."""
    # A few vanilla frontier states list the same province in a local owner and
    # in RUS.  The local arrangement is the more specific boundary: moving the
    # overlapping Russian entry as well would make an invalid double owner.
    local_provinces = {
        province
        for owner in state["owners"]
        if owner["tag"] != "RUS"
        for province in owner["provinces"]
    }
    parts = []
    for owner in state["owners"]:
        provinces = owner["provinces"]
        if owner["tag"] == "RUS":
            provinces = [province for province in provinces if province not in local_provinces]
            if not provinces:
                continue
        parts.append({"owner": target if owner["tag"] == "RUS" else owner["tag"], "provinces": provinces})
    return {"split": parts, "pops": "drop", "buildings": "drop"}


def north_caucasus(state: dict) -> dict:
    existing = {owner["tag"]: set(owner["provinces"]) for owner in state["owners"] if owner["tag"] in {"CHC", "CIR"}}
    if set(existing) != {"CHC", "CIR"}:
        raise RuntimeError(f"North Caucasus local owners changed: {sorted(existing)}")
    all_provinces = set(state["provinces"])
    local = existing["CHC"] | existing["CIR"]
    if not local <= all_provinces or existing["CHC"] & existing["CIR"]:
        raise RuntimeError("North Caucasus local province partitions are invalid")
    dagestan = sorted(all_provinces - local)
    if not dagestan:
        raise RuntimeError("North Caucasus leaves no Dagestan province")
    return {
        "split": [
            {"owner": "CHC", "provinces": sorted(existing["CHC"])},
            {"owner": "CIR", "provinces": sorted(existing["CIR"])},
            {"owner": "VDA", "provinces": dagestan},
        ],
        "pops": "drop",
        "buildings": "drop",
    }


def main() -> None:
    catalog = refresh_catalog()
    by_id = {state["id"]: state for state in catalog["states"]}
    needed = set(RUS_TARGETS) | {"STATE_NORTH_CAUCASUS"}
    missing = needed - set(by_id)
    if missing:
        raise RuntimeError(f"catalog misses required states: {sorted(missing)}")
    states = {state_id: direct_replacement(by_id[state_id], target) for state_id, target in RUS_TARGETS.items()}
    states["STATE_NORTH_CAUCASUS"] = north_caucasus(by_id["STATE_NORTH_CAUCASUS"])
    card = {
        "version": 2,
        "title": "Kart 0B — Kafkasya ve Rus Çekirdekleri",
        "description": "Dünya siyasi iskeleti: Kafkasya, Kırım–Volga ve Moskova–Novgorod egemenlikleri. Sadece doğrulanmış sahibi değiştirir; mekanik başlangıç verisi üretmez.",
        "countries": COUNTRIES,
        "states": states,
        "diplomacy": {"mode": "inherit", "reset_countries": ["RUS"]},
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
