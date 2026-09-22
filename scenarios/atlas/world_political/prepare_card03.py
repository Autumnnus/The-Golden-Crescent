"""Build the China and Inner Asia political card from every CHI province."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/political-chi-catalog.json"
TARGET = Path(__file__).with_name("card03.json")

CHI_TARGETS = {
    "STATE_BEIJING": "NCH", "STATE_ZHILI": "NCH", "STATE_SHANDONG": "NCH", "STATE_SHANXI": "NCH", "STATE_HENAN": "NCH", "STATE_XIAN": "NCH", "STATE_GANSU": "NCH", "STATE_NINGXIA": "NCH", "STATE_QINGHAI": "NCH",
    "STATE_EASTERN_HUBEI": "JNG", "STATE_WESTERN_HUBEI": "JNG", "STATE_HUNAN": "JNG", "STATE_JIANGSU": "JNG", "STATE_JIANGXI": "JNG", "STATE_NANJING": "JNG", "STATE_NORTHERN_ANHUI": "JNG", "STATE_SOUTHERN_ANHUI": "JNG", "STATE_SUZHOU": "JNG", "STATE_ZHEJIANG": "JNG",
    "STATE_CHONGQING": "SHU", "STATE_SICHUAN": "SHU", "STATE_GUIZHOU": "SHU", "STATE_YUNNAN": "SHU",
    "STATE_FUJIAN": "YUE", "STATE_FORMOSA": "YUE", "STATE_GUANGDONG": "YUE", "STATE_GUANGXI": "YUE", "STATE_SHAOZHOU": "YUE",
    "STATE_AMUR": "MCH", "STATE_NORTHERN_MANCHURIA": "MCH", "STATE_OUTER_MANCHURIA": "MCH", "STATE_SOUTHERN_MANCHURIA": "MCH", "STATE_SHENGJING": "MCH",
    "STATE_ALXA": "MGL", "STATE_HINGGAN": "MGL", "STATE_TUVA": "MGL", "STATE_ULIASTAI": "MGL", "STATE_URGA": "MGL",
    "STATE_ALTAI": "DZH", "STATE_DZUNGARIA": "DZH", "STATE_TIANSHAN": "KSG", "STATE_JETISY": "KZH", "STATE_KIRGHIZIA": "KIR",
}
COUNTRIES = {
    "NCH": {"name": "Northern China Empire", "name_tr": "Kuzey Çin İmparatorluğu", "color": [144, 81, 70], "country_type": "recognized", "tier": "empire", "cultures": ["han"], "religion": "confucian", "capital": "STATE_BEIJING"},
    "JNG": {"name": "Jiangnan Republic", "name_tr": "Jiangnan Cumhuriyeti", "color": [73, 142, 152], "country_type": "recognized", "tier": "kingdom", "cultures": ["han"], "religion": "confucian", "capital": "STATE_NANJING"},
    "SHU": {"name": "Shu Kingdom", "name_tr": "Shu Krallığı", "color": [137, 130, 73], "country_type": "recognized", "tier": "kingdom", "cultures": ["han"], "religion": "confucian", "capital": "STATE_SICHUAN"},
    "YUE": {"name": "Yue Confederation", "name_tr": "Yue Konfederasyonu", "color": [82, 151, 105], "country_type": "recognized", "tier": "kingdom", "cultures": ["han", "zhuang"], "religion": "confucian", "capital": "STATE_GUANGDONG"},
    "MCH": {"name": "Manchurian Khanate", "name_tr": "Mançurya Hanlığı", "color": [115, 99, 148], "country_type": "recognized", "tier": "kingdom", "cultures": ["manchu"], "religion": "confucian", "capital": "STATE_SHENGJING"},
    "MGL": {"name": "Mongol Khanates", "name_tr": "Moğol Hanlıkları", "color": [125, 154, 119], "country_type": "recognized", "tier": "kingdom", "cultures": ["mongol"], "religion": "gelugpa", "capital": "STATE_URGA"},
    "DZH": {"name": "Dzungar Khanate", "name_tr": "Cungar Hanlığı", "color": [159, 113, 82], "country_type": "recognized", "tier": "principality", "cultures": ["mongol"], "religion": "gelugpa", "capital": "STATE_DZUNGARIA"},
    "KSG": {"name": "Kashgar Khanate", "name_tr": "Kaşgar Hanlığı", "color": [166, 136, 71], "country_type": "recognized", "tier": "kingdom", "cultures": ["uighur"], "religion": "sunni", "capital": "STATE_TIANSHAN"},
    "KZH": {"name": "Kazakh Zhuz", "name_tr": "Kazak Cüzü", "color": [90, 120, 120], "country_type": "recognized", "tier": "principality", "cultures": ["kazak"], "religion": "sunni", "capital": "STATE_JETISY"},
    "KIR": {"name": "Kyrgyz Confederation", "name_tr": "Kırgız Birlikleri", "color": [105, 124, 161], "country_type": "recognized", "tier": "principality", "cultures": ["kirgiz"], "religion": "sunni", "capital": "STATE_KIRGHIZIA"},
}


def refresh_catalog() -> dict:
    subprocess.run([sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "CHI", "--out", str(CATALOG)], cwd=ROOT, check=True)
    return json.loads(CATALOG.read_text())


def main() -> None:
    catalog = refresh_catalog()
    states = {}
    seen = set()
    portuguese_targets = {"STATE_GUANGDONG": "YUE"}
    for state in catalog["states"]:
        state_id = state["id"]
        has_chi = any(owner["tag"] == "CHI" for owner in state["owners"])
        has_portuguese_share = state_id in portuguese_targets and any(
            owner["tag"] == "POR" for owner in state["owners"]
        )
        if not has_chi and not has_portuguese_share:
            continue
        target = CHI_TARGETS.get(state_id)
        if has_chi and target is None:
            raise RuntimeError(f"missing target for CHI share in {state_id}")
        if has_chi:
            seen.add(state_id)
        parts_by_owner = {}
        order = []
        for row in state["owners"]:
            owner_tag = row["tag"]
            final_owner = target if owner_tag == "CHI" else portuguese_targets.get(state_id, owner_tag) if owner_tag == "POR" else owner_tag
            if final_owner not in parts_by_owner:
                parts_by_owner[final_owner] = []
                order.append(final_owner)
            parts_by_owner[final_owner].extend(row["provinces"])
        states[state_id] = {
            "split": [{"owner": tag, "provinces": parts_by_owner[tag]} for tag in order],
            "pops": "drop", "buildings": "drop",
        }
    if seen != set(CHI_TARGETS):
        raise RuntimeError(f"catalog target mismatch: saw={sorted(seen)} expected={sorted(CHI_TARGETS)}")
    card = {
        "version": 2,
        "title": "Kart 3A — Çin ve İç Asya",
        "description": "Dünya siyasi iskeleti: tüm CHI province payları beş Çin yönetimi ve komşu İç Asya aktörlerine aktarılır; Guangdong'daki son geçici Portekiz liman payı Yue'ye döner; mekanik başlangıç verisi üretmez.",
        "countries": COUNTRIES,
        "states": states,
        "diplomacy": {"mode": "inherit", "reset_countries": ["CHI"]},
    }
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(COUNTRIES)} countries, {len(states)} CHI replacement state records)")


if __name__ == "__main__":
    main()
