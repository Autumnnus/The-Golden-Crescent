"""Audit India's legal/identity corrections and all protected POP blocks."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLKIT = Path(
    os.environ.get("VIC3_TOOLS_HOME")
    or json.loads((ROOT / ".vic3-tools.local.json").read_text(encoding="utf-8"))["toolkit"]
).expanduser().resolve()
if sys.version_info < (3, 10):
    runtime = TOOLKIT / ".venv/bin/python"
    os.execv(str(runtime), [str(runtime), __file__, *sys.argv[1:]])
sys.path.insert(0, str(TOOLKIT / "src"))
from vic3 import pdx  # noqa: E402


SOURCE = ROOT / "world/scenario.yml"
CANDIDATE = ROOT / "build/demography/india-cleanup-candidate.yml"
AUDIT = ROOT / "build/demography/india-cleanup-plan-audit.json"
REPORT = ROOT / "build/demography/india-cleanup-candidate-report.json"
BASE_POPS = ROOT / "common/history/pops/tgc_pops.txt"
NEW_POPS = ROOT / "build/scenarios/india-cleanup-candidate/common/history/pops/tgc_pops.txt"
OUT = ROOT / "build/demography/india-cleanup-verification.json"


def group_key(pop) -> str:
    value = f"{pop.get_str('culture')}/{pop.get_str('religion')}"
    pop_type = pop.get_str("pop_type")
    return f"{value}/{pop_type}" if pop_type else value


def main() -> None:
    source = yaml.safe_load(SOURCE.read_text())
    candidate = yaml.safe_load(CANDIDATE.read_text())
    audit = json.loads(AUDIT.read_text())
    report = json.loads(REPORT.read_text())
    errors = []
    for key in ("version", "countries", "subject_types", "diplomacy"):
        if source.get(key) != candidate.get(key):
            errors.append(f"changed {key}")
    if set(source["states"]) != set(candidate["states"]):
        errors.append("changed state set")
    target = {(state, row["owner"]) for state, row in audit["shares"].items()}
    for state, old in source["states"].items():
        new = candidate["states"].get(state, {})
        if {k: v for k, v in old.items() if k != "population"} != {k: v for k, v in new.items() if k != "population"}:
            errors.append(f"{state}: political or building data changed")
        old_by = old.get("population", {}).get("by_owner", {})
        new_by = new.get("population", {}).get("by_owner", {})
        for tag in set(old_by) | set(new_by):
            if (state, tag) not in target and old_by.get(tag) != new_by.get(tag):
                errors.append(f"{state}/{tag}: unrelated population plan changed")
        if state not in audit["shares"] and old.get("population") != new.get("population"):
            errors.append(f"{state}: unrelated state population changed")

    before = pdx.parse_file(BASE_POPS).get_node("POPS")
    after = pdx.parse_file(NEW_POPS).get_node("POPS")
    for state_block in before.items:
        new_state = after.get_node(state_block.key)
        if new_state is None:
            errors.append(f"{state_block.key}: missing output")
            continue
        state = state_block.key.removeprefix("s:")
        for owner_block in state_block.value.items:
            tag = owner_block.key.removeprefix("region_state:")
            if (state, tag) in target:
                continue
            new_owner = new_state.get_node(owner_block.key)
            if new_owner is None or pdx.dumps(owner_block.value) != pdx.dumps(new_owner):
                errors.append(f"{state_block.key}/{owner_block.key}: unrelated POPs changed")

    freed = officials = 0
    for state, plan in audit["shares"].items():
        tag = plan["owner"]
        old_node = before.get_node("s:" + state).get_node("region_state:" + tag)
        new_node = after.get_node("s:" + state).get_node("region_state:" + tag)
        groups = Counter()
        for pop in new_node.getall("create_pop"):
            groups[group_key(pop)] += pop.get_int("size")
            if tag == "BGL" and pop.get_str("pop_type") == "slaves":
                errors.append(f"{state}/{tag}: slave POP remains under H7")
            if pop.get_str("culture") in {"british", "scottish"} and pop.get_str("pop_type") in {"bureaucrats", "officers", "aristocrats"}:
                errors.append(f"{state}/{tag}: inherited colonial official remains")
        if dict(groups) != plan["groups"]:
            errors.append(f"{state}/{tag}: output joint culture/religion/profession differs")
        old_total = sum(pop.get_int("size") for pop in old_node.getall("create_pop"))
        if old_total != sum(groups.values()) or old_total != plan["population"]:
            errors.append(f"{state}/{tag}: total headcount changed")
        if report["states"][state]["owners"][tag]["population"] != old_total:
            errors.append(f"{state}/{tag}: candidate report headcount differs")
        freed += plan["freed_people"]
        officials += plan["local_officials"]
    if freed != audit["freed_people"] or officials != audit["local_officials"]:
        errors.append("conversion ledger differs")
    result = {
        "passed": not errors and report["validation"] == "passed",
        "corrected_state_shares": len(target),
        "freed_bengal_people": freed,
        "localized_colonial_officials": officials,
        "world_population_unchanged": True,
        "errors": errors,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (passed={result['passed']})")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
