"""Put Finland and Iceland inside their documented Kalmar crowns."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FIN_CATALOG = ROOT / "build/political-fin-catalog.json"
DEN_CATALOG = ROOT / "build/political-kalmar-den-catalog.json"
TARGET = Path(__file__).with_name("card11.json")


def refresh(region: str, target: Path) -> dict:
    subprocess.run([sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", region, "--out", str(target)], cwd=ROOT, check=True)
    return json.loads(target.read_text())


def whole_owner(state: dict, old: str, new: str) -> dict:
    parts, found = [], False
    for owner in state["owners"]:
        found |= owner["tag"] == old
        parts.append({"owner": new if owner["tag"] == old else owner["tag"], "provinces": owner["provinces"]})
    if not found:
        raise RuntimeError(f"{state['id']} no longer contains {old}")
    return {"split": parts, "pops": "drop", "buildings": "drop"}


def main() -> None:
    fin = {state["id"]: state for state in refresh("FIN", FIN_CATALOG)["states"]}
    den = {state["id"]: state for state in refresh("DEN", DEN_CATALOG)["states"]}
    fin_states = {state_id: whole_owner(state, "FIN", "SWE") for state_id, state in fin.items() if any(owner["tag"] == "FIN" for owner in state["owners"])}
    if not fin_states:
        raise RuntimeError("FIN catalog has no owned states")
    states = {**fin_states, "STATE_ICELAND": whole_owner(den["STATE_ICELAND"], "DEN", "NOR")}
    card = {"version": 2, "title": "Kart 1F — Kalmar İç Düzenleri", "description": "Dünya siyasi iskeleti: Finlandiya İsveç, İzlanda Norveç tacının iç düzeni olur. Kalmar ortak tacı ve Schleswig–Holstein'ın ayrı diyeti diplomasi kartında tanımlanır.", "countries": {}, "states": states, "diplomacy": {"mode": "inherit", "reset_countries": ["FIN"]}}
    TARGET.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} (0 countries, {len(states)} state records)")


if __name__ == "__main__":
    main()
