"""Assert that the political preview has no implicit state ownership left."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PREVIEW = ROOT / "build/world-political/partial-political-preview.json"
OUT = ROOT / "build/world-political/remaining-world-audit.json"


def main() -> None:
    preview = json.loads(PREVIEW.read_text())
    cards = [json.loads(path.read_text()) for path in sorted(HERE.glob("card*.json"))]
    explicit = {state for card in cards for state in card["states"]}
    source_states = set(preview["states"])
    payload = {
        "title": "Dünya siyasi kapsam denetimi",
        "scope": "Every land state must be explicit in a political card; inherited ownership is forbidden.",
        "preview_state_records": len(source_states),
        "explicit_card_states": len(explicit),
        "unmapped_states": sorted(source_states - explicit),
        "stale_card_states": sorted(explicit - source_states),
        "passed": source_states == explicit == set(preview["states"]),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(payload['unmapped_states'])} unmapped states)")
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
