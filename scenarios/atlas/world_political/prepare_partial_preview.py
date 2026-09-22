"""Assemble every non-overlapping political card into a disposable V2 map preview.

This is deliberately written below build/: it is a visual diagnostic, never an
active world source or a replacement for the per-region completion gate.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TARGET = ROOT / "build/world-political/partial-political-preview.json"


def main() -> None:
    # Card 63 freezes every still-local state as an explicit province split.
    # Regenerate it before validation so a change in any preceding card cannot
    # silently leave a stale retained-border snapshot behind.
    subprocess.run([sys.executable, str(HERE / "prepare_card63.py")], cwd=ROOT, check=True)
    # Keep this checker first: a later card must explicitly merge a shared state
    # instead of silently winning based on filesystem order.
    subprocess.run([sys.executable, str(HERE / "verify_cards.py")], cwd=ROOT, check=True)
    cards = []
    for path in sorted(HERE.glob("card*.json")):
        cards.append((path.name, json.loads(path.read_text())))
    countries, states, reset_countries = {}, {}, []
    subject_types = {}
    diplomacy_rows = {"subjects": [], "relations": [], "pacts": [], "remove": []}
    reset_countries = [tag for _, card in cards for tag in card.get("diplomacy", {}).get("reset_countries", [])]
    for filename, card in cards:
        for key, spec in card.get("subject_types", {}).items():
            if key in subject_types and subject_types[key] != spec:
                raise RuntimeError(f"conflicting subject type {key} from {filename}")
            subject_types[key] = spec
        for field, rows in diplomacy_rows.items():
            for row in card.get("diplomacy", {}).get(field, []):
                if row in rows:
                    raise RuntimeError(f"duplicate diplomacy.{field} row from {filename}: {row}")
                rows.append(row)
        for tag, spec in card["countries"].items():
            if tag in countries:
                if tag not in reset_countries:
                    raise RuntimeError(f"duplicate country {tag} from {filename}")
            countries[tag] = spec
        for state, spec in card["states"].items():
            if state in states:
                raise RuntimeError(f"duplicate state {state} from {filename}")
            states[state] = spec
    reset_countries = list(dict.fromkeys(reset_countries))
    # A regional V2 card can retain a temporary country override solely to
    # clear vanilla company data while neighbouring cards remove its final
    # provinces. The global preview must remove that empty country definition:
    # its inherited capital may correctly no longer exist in the completed map.
    referenced_owners = {
        part["owner"]
        for spec in states.values()
        for part in (spec.get("split") or ([{"owner": spec["owner"]}] if "owner" in spec else []))
    }
    for tag in reset_countries:
        if tag in countries and tag not in referenced_owners:
            del countries[tag]
    preview = {
        "version": 2,
        "title": "Kısmi Dünya Siyasi Önizlemesi — Etkin Değil",
        "description": "Yalnız doğrulanmış siyasi kartların geçici birleşimi. Vanilla sahibi kalan state'ler kesin karar değildir; bu dosya modun world/ kaynağı değildir.",
        "countries": countries,
        "states": states,
        **({"subject_types": subject_types} if subject_types else {}),
        "diplomacy": {"mode": "inherit", "reset_countries": reset_countries, **diplomacy_rows},
    }
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(preview, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(cards)} cards, {len(countries)} countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
