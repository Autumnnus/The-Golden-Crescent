"""Produce a bounded, reproducible completion audit for the political preview."""

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
GBR_FINAL = ROOT / "build/world-political/gbr-final-catalog.json"
OUT = ROOT / "build/world-political/political-completion-audit.json"
REPORT = ROOT / "build/world-political/final-political-report.json"
LEDGER = ROOT / "build/world-political/state-decision-ledger.json"
PREVIEW_BUNDLE = ROOT / "build/scenarios/world-political-preview"
WORLD_COVERAGE = ROOT / "build/world-political/remaining-world-audit.json"
DIPLOMACY_CONTRACT = ROOT / "build/world-political/diplomacy-contract-audit.json"
MARKERS = ("temporary", "residual", "geçici")
GBR_SCOPE = {
    "STATE_BAHAMAS": 4,
    "STATE_BERMUDA": 2,
    "STATE_SOUTH_ATLANTIC_ISLANDS": 7,
    "STATE_WEST_INDIES": 11,
}


def owners(spec: dict) -> set[str]:
    if "owner" in spec:
        return {spec["owner"]}
    return {part["owner"] for part in spec.get("split", [])}


def catalog(region: str, out: Path, scenario: Path | None = None) -> dict:
    command = [sys.executable, "scripts/tools.py", "atlas", "catalog", "--region", region]
    if scenario:
        command.extend(["--scenario", str(scenario)])
    command.extend(["--out", str(out)])
    subprocess.run(command, cwd=ROOT, check=True)
    return json.loads(out.read_text())


def main() -> None:
    cards = [(path.name, json.loads(path.read_text())) for path in sorted(HERE.glob("card*.json"))]
    preview = json.loads(PREVIEW.read_text())
    reset = sorted({tag for _, card in cards for tag in card.get("diplomacy", {}).get("reset_countries", [])})

    temporary = []
    for name, card in cards:
        for tag, spec in card.get("countries", {}).items():
            label = " ".join(str(spec.get(key, "")) for key in ("name", "name_tr", "notes")).lower()
            if any(marker in label for marker in MARKERS) and tag not in reset:
                temporary.append({"tag": tag, "declared_by": name, "name": spec.get("name"), "name_tr": spec.get("name_tr")})
    temporary_owners = {row["tag"]: [] for row in temporary}
    for state, spec in preview["states"].items():
        for tag in owners(spec):
            if tag in temporary_owners:
                temporary_owners[tag].append(state)
    for row in temporary:
        row["changed_states_owned"] = temporary_owners[row["tag"]]
        row["status"] = "open" if row["changed_states_owned"] else "definition_only"

    baseline = catalog("world", BASELINE)
    total_states = len(baseline["states"])
    changed = set(preview["states"])
    inherited = [state for state in baseline["states"] if state["id"] not in changed]
    inherited_by_region = Counter(state["region"] for state in inherited)
    changed_by_region = Counter(state["region"] for state in baseline["states"] if state["id"] in changed)

    final_gbr = catalog("GBR", GBR_FINAL, PREVIEW)
    gbr_actual = {
        state["id"]: sum(len(owner["provinces"]) for owner in state["owners"] if owner["tag"] == "GBR")
        for state in final_gbr["states"]
        if any(owner["tag"] == "GBR" for owner in state["owners"])
    }
    if gbr_actual != GBR_SCOPE:
        raise RuntimeError(f"GBR scope drifted: expected {GBR_SCOPE}, got {gbr_actual}")

    # A map can be valid while still inheriting a diplomatic world that belongs
    # to a discarded vanilla scenario. Every retained pact must therefore be
    # deliberately re-authored by a card before political lock—not silently
    # tolerated because its countries still have land.
    subprocess.run(
        [sys.executable, "scripts/tools.py", "atlas", "scenario", "report", str(PREVIEW), "--out", str(REPORT)],
        cwd=ROOT,
        check=True,
    )
    report = json.loads(REPORT.read_text())
    inherited_pacts = [
        pact for pact in report["diplomacy"]["pacts"]
        if pact.get("source") == "inherited"
    ]
    # Scenario build emits an isolated preview bundle and runs Atlas's strict
    # generated-world checker. It catches bad capitals, duplicate province
    # owners and history output errors that source validation leaves as notes.
    subprocess.run(
        [sys.executable, "scripts/tools.py", "atlas", "scenario", "build", str(PREVIEW), "--out", str(PREVIEW_BUNDLE)],
        cwd=ROOT,
        check=True,
    )
    subprocess.run([sys.executable, str(HERE / "political_state_ledger.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(HERE / "remaining_world_audit.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(HERE / "diplomacy_contract_audit.py")], cwd=ROOT, check=True)
    ledger = json.loads(LEDGER.read_text())
    coverage = json.loads(WORLD_COVERAGE.read_text())
    diplomacy_contract = json.loads(DIPLOMACY_CONTRACT.read_text())
    readiness = not temporary and not inherited_pacts and ledger["summary"]["passed"] and coverage["passed"] and diplomacy_contract["passed"]

    payload = {
        "title": "Dünya Siyasi Tamamlanma Denetimi",
        "scope": "Political-owner stage only. Population, economy, laws, technology, military and event work remain outside this preview.",
        "cards": len(cards),
        "states": {"total": total_states, "owner_overrides": len(changed), "inherited_baseline": len(inherited)},
        "coverage_by_region": {
            region: {"owner_overrides": changed_by_region[region], "inherited_baseline": inherited_by_region[region]}
            for region in sorted(set(changed_by_region) | set(inherited_by_region))
        },
        "temporary_country_definitions": temporary,
        "retired_country_tags": reset,
        "permanent_limited_dependency": {
            "tag": "GBR",
            "name": "London Crown Overseas Dependencies",
            "direct_scope": gbr_actual,
            "source": "docs/scenario/diplomasi.md and card09.json",
        },
        "inherited_diplomacy_requiring_explicit_decision": inherited_pacts,
        "state_decision_ledger": ledger["summary"],
        "world_coverage": coverage,
        "diplomacy_contract": {"passed": diplomacy_contract["passed"], "overlords": len(diplomacy_contract["actual_overlords"])},
        "isolated_preview_bundle": str(PREVIEW_BUNDLE.relative_to(ROOT)),
        "ready_for_political_lock": readiness,
        "open_count": sum(row["status"] == "open" for row in temporary),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(
        f"wrote {OUT.relative_to(ROOT)} ({len(cards)} cards, {len(temporary)} temporary definitions, "
        f"{len(inherited_pacts)} inherited pacts, {len(changed)}/{total_states} state overrides; "
        f"political_lock={readiness})"
    )


if __name__ == "__main__":
    main()
