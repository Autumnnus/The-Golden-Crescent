"""Encode every written 1836 political dependency in the Atlas preview."""

from __future__ import annotations

import json
from pathlib import Path


OUT = Path(__file__).with_name("card64.json")


def main() -> None:
    card = {
        "version": 2,
        "title": "Kart 6C — Başlangıç bağlılık ve taç sözleşmeleri",
        "description": "Yazılı 1836 diplomasisindeki hiyerarşik bağlılıkları dar özel sözleşmelerle, hiyerarşik olmayan ortak taçları ise karşılıklı ilişki göstergeleriyle kurar. Liman hakları ve ortak konseyler ikinci bir toprak sahibi oluşturmaz.",
        "countries": {},
        "states": {},
        "subject_types": {
            "ve_autonomous_compact": {
                "base": "vassal",
                "name": "Autonomous Compact",
                "name_tr": "Özerk Bağlılık Sözleşmesi",
                "overlord_types": ["recognized", "unrecognized"],
                "subject_types": ["recognized", "unrecognized"],
                "can_have_subjects": False,
                "join_overlord_wars": False,
                "income_transfer": 0.05,
            },
            "ve_colonial_charter": {
                "base": "vassal",
                "name": "Colonial Charter",
                "name_tr": "Sömürge Şartı",
                "overlord_types": ["recognized", "unrecognized"],
                "subject_types": ["recognized", "unrecognized"],
                "can_have_subjects": False,
                "join_overlord_wars": False,
                "income_transfer": 0.08,
            },
            "ve_tributary_compact": {
                "base": "protectorate",
                "name": "Limited Tributary Compact",
                "name_tr": "Sınırlı Haraç Sözleşmesi",
                "overlord_types": ["recognized", "unrecognized"],
                "subject_types": ["recognized", "unrecognized"],
                "can_have_subjects": False,
                "join_overlord_wars": False,
                "income_transfer": 0.02,
            },
        },
        "diplomacy": {
            "mode": "inherit",
            "subjects": [
                *[{"overlord": "RUM", "subject": tag, "type": "ve_autonomous_compact", "liberty_desire": 35} for tag in ["BOS", "ALB", "BUL", "ADA", "ERZ", "TRB"]],
                {"overlord": "RUM", "subject": "VBU", "type": "ve_colonial_charter", "liberty_desire": 40},
                {"overlord": "VPL", "subject": "MOL", "type": "ve_tributary_compact", "liberty_desire": 40},
                *[{"overlord": "VAN", "subject": tag, "type": "ve_colonial_charter", "liberty_desire": 45} for tag in ["VNE", "VSI", "VPI"]],
                {"overlord": "VAN", "subject": "VMY", "type": "ve_tributary_compact", "liberty_desire": 55},
                {"overlord": "MOR", "subject": "VFB", "type": "ve_colonial_charter", "liberty_desire": 45},
                *[{"overlord": "VEL", "subject": tag, "type": "ve_colonial_charter", "liberty_desire": 45} for tag in ["VNI", "VVA"]],
                {"overlord": "NET", "subject": "VNH", "type": "ve_colonial_charter", "liberty_desire": 40},
            ],
            "relations": [
                {"actor": "VEL", "target": "VSC", "value": 50},
                {"actor": "VEL", "target": "VIR", "value": 50},
                {"actor": "VSC", "target": "VIR", "value": 50},
                {"actor": "DEN", "target": "VIN", "value": 35},
                {"actor": "SWE", "target": "VIN", "value": 35},
                {"actor": "NOR", "target": "VIN", "value": 35},
                {"actor": "JAP", "target": "RYU", "value": 20},
                {"actor": "YUE", "target": "RYU", "value": 20},
            ],
        },
    }
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
