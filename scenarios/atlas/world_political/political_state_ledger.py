"""Prove that every vanilla state has an explicit political decision record.

The map preview intentionally keeps many locally coherent vanilla owners.  That
is permitted only when the region's current political dossier explicitly owns
the retention decision.  This script rejects silent state loss, province drift
and retired direct owners before the political boundary stage is locked.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIEW = ROOT / "build/world-political/partial-political-preview.json"
BASELINE = ROOT / "build/world-political/world-baseline-catalog.json"
FINAL = ROOT / "build/world-political/final-world-catalog.json"
OUT = ROOT / "build/world-political/state-decision-ledger.json"

RETIRED_DIRECT_OWNERS = {
    "FRA", "POR", "SPA", "PRU", "RUS", "USA", "MEX", "BRZ", "ARG", "CHL",
    "BIC", "CHI", "DEI", "PAN", "SIL", "SAF", "NBS", "NVS", "MKT", "ONT",
    "QUE", "HBC", "UCA",
}
GBR_SCOPE = {
    "STATE_BAHAMAS": 4,
    "STATE_BERMUDA": 2,
    "STATE_SOUTH_ATLANTIC_ISLANDS": 7,
    "STATE_WEST_INDIES": 11,
}


def catalog(region: str, out: Path, scenario: Path | None = None) -> dict:
    command = [sys.executable, "scenarios/atlas/world_political/catalog_vanilla.py", "atlas", "catalog", "--baseline", "vanilla", "--region", region]
    if scenario:
        command.extend(["--scenario", str(scenario)])
    command.extend(["--out", str(out)])
    subprocess.run(command, cwd=ROOT, check=True)
    return json.loads(out.read_text())


def owner_counts(state: dict) -> dict[str, int]:
    return {
        owner["tag"]: len(owner["provinces"])
        for owner in state["owners"]
    }


def main() -> None:
    cards = [(path.name, json.loads(path.read_text())) for path in sorted(HERE.glob("card*.json"))]
    state_cards: dict[str, list[str]] = {}
    for filename, card in cards:
        for state in card["states"]:
            state_cards.setdefault(state, []).append(filename)

    baseline = catalog("world", BASELINE)
    final = catalog("world", FINAL, PREVIEW)
    baseline_states = {state["id"]: state for state in baseline["states"]}
    final_states = {state["id"]: state for state in final["states"]}
    errors: list[str] = []
    decisions = []

    for state_id, before in sorted(baseline_states.items()):
        after = final_states.get(state_id)
        if after is None:
            errors.append(f"missing state in final preview: {state_id}")
            continue
        before_provinces = before["provinces"]
        after_provinces = after["provinces"]
        if len(after_provinces) != len(set(after_provinces)):
            errors.append(f"duplicate final province: {state_id}")
        if set(before_provinces) != set(after_provinces):
            errors.append(f"province geometry drift: {state_id}")
        direct = owner_counts(after)
        retired = sorted(set(direct) & RETIRED_DIRECT_OWNERS)
        if retired:
            errors.append(f"retired direct owner in {state_id}: {', '.join(retired)}")
        cards_for_state = state_cards.get(state_id, [])
        if cards_for_state:
            decision = "explicit_card"
            source = cards_for_state
        else:
            errors.append(f"state is not explicitly frozen by a political card: {state_id}")
            decision = "unresolved"
            source = []
        decisions.append({
            "state": state_id,
            "region": before["region"],
            "decision": decision,
            "source": source,
            "direct_owner_provinces": direct,
        })

    gbr_actual = {
        state["id"]: owner_counts(state)["GBR"]
        for state in final["states"]
        if "GBR" in owner_counts(state)
    }
    if gbr_actual != GBR_SCOPE:
        errors.append(f"GBR direct scope drift: expected {GBR_SCOPE}, got {gbr_actual}")

    summary = {
        "total_states": len(baseline_states),
        "explicit_card": sum(row["decision"] == "explicit_card" for row in decisions),
        "reviewed_retention": sum(row["decision"] == "reviewed_retention" for row in decisions),
        "errors": len(errors),
        "passed": not errors,
    }
    payload = {
        "title": "Dünya siyasi state karar defteri",
        "scope": "Every vanilla state must have a card rewrite or a region-dossier retention decision.",
        "summary": summary,
        "gbr_direct_scope": gbr_actual,
        "retired_direct_owners": sorted(RETIRED_DIRECT_OWNERS),
        "errors": errors,
        "states": decisions,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(
        f"wrote {OUT.relative_to(ROOT)} ({summary['explicit_card']} card rewrites, "
        f"{summary['reviewed_retention']} reviewed retentions, {summary['errors']} errors)"
    )
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
