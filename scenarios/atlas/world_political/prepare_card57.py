"""Return Omani port enclaves to their written local sovereigns."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "build/world-political/oman-enclave-catalog.json"
OUT = Path(__file__).with_name("card57.json")

# These are foreign port holdings in vanilla, not the Omani homeland or the
# Zanzibar overseas divan. The scenario records them as contracts, so their
# province ownership returns to the named local administration.
TARGETS = {
    "STATE_ABU_DHABI": "ABU",
    "STATE_BALUCHISTAN": "MAK",
    "STATE_SISTAN": "MAK",
    "STATE_KENYA": "MBS",
}

# The vanilla Kenya state lists this coastal province under both an inland
# owner and Witu. A political split must have one owner; Witu is the local
# coastal administration retained by the written Swahili-city arrangement.
DEDUP_WINNERS = {("STATE_KENYA", "x5C1ADA"): "WTU"}


def main() -> None:
    subprocess.run(
        [sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", "OMA", "--out", str(CATALOG)],
        cwd=ROOT,
        check=True,
    )
    catalog = json.loads(CATALOG.read_text())
    by_id = {row["id"]: row for row in catalog["states"]}
    states = {}
    for state_id, local_owner in TARGETS.items():
        state = by_id.get(state_id)
        if state is None:
            raise RuntimeError(f"missing {state_id} from OMA catalog")
        parts: dict[str, list[str]] = {}
        order: list[str] = []
        assigned: dict[str, str] = {}
        for entry in state["owners"]:
            owner = local_owner if entry["tag"] == "OMA" else entry["tag"]
            if owner not in parts:
                parts[owner] = []
                order.append(owner)
            for province in entry["provinces"]:
                province = "x" + province[1:].upper()
                previous = assigned.get(province)
                if previous is None:
                    assigned[province] = owner
                    parts[owner].append(province)
                    continue
                winner = DEDUP_WINNERS.get((state_id, province))
                if winner != owner:
                    continue
                parts[previous].remove(province)
                parts[owner].append(province)
                assigned[province] = owner
        if "OMA" not in {entry["tag"] for entry in state["owners"]}:
            raise RuntimeError(f"{state_id} has no Omani enclave to return")
        states[state_id] = {
            "split": [{"owner": owner, "provinces": parts[owner]} for owner in order],
            "pops": "drop",
            "buildings": "drop",
        }
    card = {
        "version": 1,
        "title": "Kart 4E — Umman'ın sözleşmeli limanları",
        "description": "Abu Dabi, Makran/Bampur ve Mombasa'daki Omani vanilla liman province'leri yerel sahiplere döner. Maskat–Umman çekirdeği, Laristan kıyısı ve Zanzibar divanı değişmez; dış erişim liman sözleşmesidir, doğrudan koloni değildir.",
        "countries": {},
        "states": states,
    }
    OUT.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
