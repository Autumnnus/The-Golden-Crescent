"""Write the diplomacy-only correction for the Danube political order."""
from __future__ import annotations
import json
from pathlib import Path
OUT = Path(__file__).with_name('card36.json')
def main() -> None:
    card = {
        'version': 2,
        'title': 'Kart 1I — Tuna bağımsızlık düzeltmesi',
        'description': ('Yazılı atlas Macaristan ve Erdel’i bağımsız sayar; '
                        'Habsburg kişisel birliği yoktur. Bu kart yalnız onların '
                        'vanilla Avusturya crown_land başlangıç bağlarını kaldırır.'),
        'countries': {},
        'states': {},
        'diplomacy': {'mode': 'inherit', 'reset_countries': ['HUN', 'TRS']},
    }
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2) + '\n')
if __name__ == '__main__':
    main()
