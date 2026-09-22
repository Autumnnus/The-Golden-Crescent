"""Build the state-scale North American break-up of direct United States rule.

The written atlas distinguishes narrow coast colonies from indigenous interiors.
Victoria states cannot draw that coastal line reliably without a reviewed province
plan, so this card explicitly records only state-scale ownership choices.  USA
is left in the tiny District of Columbia until card16 transfers it, allowing this
regional V2 card to validate in isolation without carrying a country with no
capital.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-usa-catalog.json"
TARGET = Path(__file__).with_name("card15.json")

COUNTRIES = {
    "VNI": {"name": "New England", "name_tr": "Yeni İngiltere", "color": [126, 92, 151], "country_type": "recognized", "tier": "principality", "cultures": ["yankee"], "religion": "protestant", "capital": "STATE_MASSACHUSETTS"},
    "VNH": {"name": "New Netherland", "name_tr": "Yeni Hollanda", "color": [218, 121, 47], "country_type": "recognized", "tier": "principality", "cultures": ["dutch", "yankee"], "religion": "protestant", "capital": "STATE_NEW_YORK"},
    "VPA": {"name": "Pennsylvania Trade Republic", "name_tr": "Pennsylvania Ticaret Cumhuriyeti", "color": [105, 141, 115], "country_type": "recognized", "tier": "principality", "cultures": ["yankee"], "religion": "protestant", "capital": "STATE_PENNSYLVANIA"},
    "VVA": {"name": "Virginia Colony", "name_tr": "Virginia Kolonisi", "color": [151, 101, 91], "country_type": "recognized", "tier": "principality", "cultures": ["dixie"], "religion": "catholic", "capital": "STATE_VIRGINIA"},
    "VBU": {"name": "New Bursa", "name_tr": "Yeni Bursa", "color": [63, 142, 147], "country_type": "recognized", "tier": "principality", "cultures": ["mashriqi"], "religion": "sunni", "capital": "STATE_FLORIDA"},
    "VHD": {"name": "Haudenosaunee Confederacy", "name_tr": "Haudenosaunee Konfederasyonu", "color": [115, 131, 77], "country_type": "unrecognized", "tier": "principality", "cultures": ["iroquoian"], "religion": "animist", "capital": "STATE_OHIO"},
    "VGT": {"name": "Great Lakes Trade League", "name_tr": "Büyük Göller Ticaret Birliği", "color": [71, 133, 146], "country_type": "unrecognized", "tier": "principality", "cultures": ["algonquian"], "religion": "animist", "capital": "STATE_MICHIGAN"},
    "VCE": {"name": "Cherokee Council", "name_tr": "Cherokee Meclisi", "color": [130, 115, 77], "country_type": "unrecognized", "tier": "principality", "cultures": ["cherokee"], "religion": "animist", "capital": "STATE_GEORGIA"},
    "VMC": {"name": "Muscogee Council", "name_tr": "Muscogee Meclisi", "color": [117, 142, 91], "country_type": "unrecognized", "tier": "principality", "cultures": ["muskogean"], "religion": "animist", "capital": "STATE_ALABAMA"},
    "VCO": {"name": "Choctaw Confederacy", "name_tr": "Choctaw Konfederasyonu", "color": [140, 118, 86], "country_type": "unrecognized", "tier": "principality", "cultures": ["muskogean"], "religion": "animist", "capital": "STATE_MISSISSIPPI"},
    "VMR": {"name": "Mississippi River League", "name_tr": "Mississippi Nehir Birliği", "color": [123, 110, 156], "country_type": "unrecognized", "tier": "principality", "cultures": ["algonquian"], "religion": "animist", "capital": "STATE_MISSOURI"},
    "VLA": {"name": "Lakota League", "name_tr": "Lakota Birliği", "color": [135, 101, 159], "country_type": "unrecognized", "tier": "principality", "cultures": ["dakota"], "religion": "animist", "capital": "STATE_NORTH_DAKOTA"},
    "VPW": {"name": "Pawnee Confederacy", "name_tr": "Pawnee Konfederasyonu", "color": [151, 122, 74], "country_type": "unrecognized", "tier": "principality", "cultures": ["algonquian"], "religion": "animist", "capital": "STATE_NEBRASKA"},
    "VUT": {"name": "Ute Mountain Council", "name_tr": "Ute Dağ Meclisi", "color": [111, 126, 130], "country_type": "unrecognized", "tier": "principality", "cultures": ["paiute"], "religion": "animist", "capital": "STATE_COLORADO"},
    "USA": {"name": "Residual United States Jurisdiction", "name_tr": "Geçici ABD Yetki Alanı", "color": [125, 125, 125], "country_type": "recognized", "tier": "principality", "cultures": ["yankee"], "religion": "protestant", "capital": "STATE_DISTRICT_OF_COLUMBIA", "companies": {"mode": "replace", "add": [], "remove": []}},
}

TARGETS = {
    "STATE_MAINE": "VNI", "STATE_NEW_HAMPSHIRE": "VNI", "STATE_VERMONT": "VNI", "STATE_MASSACHUSETTS": "VNI", "STATE_CONNECTICUT": "VNI", "STATE_RHODE_ISLAND": "VNI",
    "STATE_NEW_YORK": "VNH", "STATE_NEW_JERSEY": "VNH", "STATE_PENNSYLVANIA": "VPA", "STATE_DELAWARE": "VPA",
    "STATE_VIRGINIA": "VVA", "STATE_MARYLAND": "VVA", "STATE_NORTH_CAROLINA": "VVA", "STATE_SOUTH_CAROLINA": "VVA", "STATE_WEST_VIRGINIA": "VVA",
    "STATE_FLORIDA": "VBU", "STATE_OHIO": "VHD", "STATE_MICHIGAN": "VGT", "STATE_WISCONSIN": "VGT", "STATE_ILLINOIS": "VGT", "STATE_MINNESOTA": "VGT",
    "STATE_GEORGIA": "VCE", "STATE_TENNESSEE": "VCE", "STATE_ALABAMA": "VMC", "STATE_MISSISSIPPI": "VCO",
    "STATE_ARKANSAS": "VMR", "STATE_LOUISIANA": "VMR", "STATE_KENTUCKY": "VMR", "STATE_MISSOURI": "VMR", "STATE_INDIANA": "VMR",
    "STATE_NORTH_DAKOTA": "VLA", "STATE_SOUTH_DAKOTA": "VLA", "STATE_MONTANA": "VLA", "STATE_WYOMING": "VLA",
    "STATE_IOWA": "VPW", "STATE_KANSAS": "VPW", "STATE_NEBRASKA": "VPW", "STATE_COLORADO": "VUT",
}


def refresh_catalog() -> dict:
    subprocess.run([sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "USA", "--out", str(CATALOG)], cwd=ROOT, check=True)
    return json.loads(CATALOG.read_text())


def replace_usa_share(state: dict, target: str) -> dict:
    parts, found = [], False
    local = {p for entry in state["owners"] if entry["tag"] != "USA" for p in entry["provinces"]}
    for entry in state["owners"]:
        provinces = entry["provinces"]
        if entry["tag"] == "USA":
            found = True
            provinces = [p for p in provinces if p not in local]
            if not provinces:
                continue
        parts.append({"owner": target if entry["tag"] == "USA" else entry["tag"], "provinces": ["x" + p[1:].upper() for p in provinces]})
    if not found:
        raise RuntimeError(f"{state['id']} no longer includes USA")
    return {"split": parts, "pops": "drop", "buildings": "drop"}


def main() -> None:
    catalog = refresh_catalog()
    by_id = {state["id"]: state for state in catalog["states"]}
    missing = set(TARGETS) - set(by_id)
    if missing:
        raise RuntimeError(f"catalog misses: {sorted(missing)}")
    states = {state_id: replace_usa_share(by_id[state_id], target) for state_id, target in TARGETS.items()}
    # Colorado contains both USA and MEX claims. Keep this shared state in one
    # card so the world merge remains order-independent.
    for part in states["STATE_COLORADO"]["split"]:
        if part["owner"] == "MEX":
            part["owner"] = "UTE"
    card = {"version": 2, "title": "Kart 5D — Kuzey Amerika'nın ABD Sonrası Siyasi İskeleti", "description": "Dünya siyasi iskeleti: ABD'nin doğrudan state sahipliği, yazılı Amerika atlasındaki kıyı kolonileri ve yerel meclis/konfederasyonlara aktarılır. Kıyı–iç ayrımı state ölçeğinde zorunlu bir sadeleştirmedir; province ölçeği ve diplomatik bağlar sonraki kartta tasarlanacaktır. District of Columbia, bu kartın tek doğrulama ankrajıdır ve kart16 tarafından ayrı bir şehir yönetimine aktarılır.", "countries": COUNTRIES, "states": states, "diplomacy": {"mode": "inherit", "reset_countries": ["USA"]}}
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} state records)")

if __name__ == "__main__":
    main()
