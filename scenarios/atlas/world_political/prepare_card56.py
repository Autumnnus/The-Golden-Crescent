"""Close the Lahore and Peshawar remnants of vanilla Punjab."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/world-political/punjab-lahore-catalog.json"
OUT = Path(__file__).with_name("card56.json")


TARGETS = {
    # S4: the lowland PAN block contains Lahore and belongs to the Gurkanî.
    "STATE_PUNJAB": "MUG",
    # The written atlas has Kabul, Herat and Kandahar—not a fourth Sikh/Punjab
    # western realm. Peshawar's PAN remnant therefore returns to Kabul.
    "STATE_PASHTUNISTAN": "KAB",
}


def main() -> None:
    subprocess.run(
        [sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "PAN", "--out", str(CATALOG)],
        cwd=ROOT,
        check=True,
    )
    catalog = json.loads(CATALOG.read_text())
    by_id = {row["id"]: row for row in catalog["states"]}
    states = {}
    for state_id, target in TARGETS.items():
        state = by_id.get(state_id)
        if state is None:
            raise RuntimeError(f"missing {state_id} from PAN catalog")
        parts: dict[str, list[str]] = {}
        order: list[str] = []
        for entry in state["owners"]:
            owner = target if entry["tag"] == "PAN" else entry["tag"]
            if owner not in parts:
                parts[owner] = []
                order.append(owner)
            parts[owner].extend("x" + province[1:].upper() for province in entry["provinces"])
        if "PAN" not in {entry["tag"] for entry in state["owners"]}:
            raise RuntimeError(f"{state_id} no longer contains its verified PAN block")
        states[state_id] = {
            "split": [{"owner": owner, "provinces": parts[owner]} for owner in order],
            "pops": "drop",
            "buildings": "drop",
        }
    card = {
        "version": 1,
        "title": "Kart 2D — Lahor ve Peşaver sınırı",
        "description": "S4'teki Lahor kararını gerçek STATE_PUNJAB province bloğuna uygular: eski PAN payı Gurkanî'ye geçer; Bahavalpur'un ayrı alt-Pencap payı korunur. Peşaver'deki PAN kalıntısı Kabil'e döner; Sih çekirdeği yalnız kart02'deki Pencap tepelerindedir.",
        "countries": {},
        "states": states,
        "diplomacy": {"mode": "inherit", "reset_countries": ["PAN"]},
    }
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
