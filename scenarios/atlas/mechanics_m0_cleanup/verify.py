"""Audit the M0 candidate: error sources gone, protected world data unchanged."""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLKIT = Path(os.environ.get("VIC3_TOOLS_HOME") or json.loads(
    (ROOT / ".vic3-tools.local.json").read_text())["toolkit"])
if sys.version_info < (3, 10):
    runtime = TOOLKIT / ".venv/bin/python"
    os.execv(str(runtime), [str(runtime), __file__, *sys.argv[1:]])
sys.path.insert(0, str(TOOLKIT / "src"))
sys.path.insert(0, str(HERE))
from vic3 import pdx  # noqa: E402
from prepare import CLEARED_MILITARY, LIBERTY_RESET, RESTORED_RELATIONS, invalid_ownership  # noqa: E402


def main() -> None:
    build = ROOT / "build/mechanics"
    out = ROOT / "build/scenarios/m0-candidate"
    source = yaml.safe_load((build / "m0-source.yml").read_text())
    candidate = yaml.safe_load((build / "m0-candidate.yml").read_text())
    prior = json.loads((build / "m0-source-report.json").read_text())
    report = json.loads((out / "scenario-report.json").read_text())
    errors = []
    owned = defaultdict(set)
    for state, srep in report["states"].items():
        for tag in srep["owners"]:
            owned[tag].add(state)
    buildings = pdx.parse_file(out / "common/history/buildings/tgc_buildings.txt").get_node("BUILDINGS")
    for sb in buildings.items:
        for ob in sb.value.items:
            tag = ob.key.split(":")[1]
            for record in ob.value.getall("create_building"):
                if invalid_ownership(record, tag, owned):
                    errors.append(f"{sb.key}/{tag}: invalid ownership remains for {record.get_str('building')}")
    diplomacy = (out / "common/history/diplomacy/ve_scenario_diplomacy.txt").read_text(encoding="utf-8-sig")
    for tag in LIBERTY_RESET:
        block = re.search(rf"\nc:{tag} \?= \{{(.*?)\n\}}", diplomacy, re.S)
        if block and "add_liberty_desire" in block.group(1):
            errors.append(f"{tag}: liberty desire without subject pact remains")
    for row in RESTORED_RELATIONS:
        block = re.search(rf"\nc:{row['actor']} \?= \{{(.*?)\n\}}", diplomacy, re.S)
        if not block or f"c:{row['target']}" not in block.group(1):
            errors.append(f"{row['actor']}->{row['target']}: restored relation missing")
    for tag in CLEARED_MILITARY:
        if report["countries"][tag]["military"] != {"battalions": 0, "ships": 0}:
            errors.append(f"{tag}: military not cleared")
    for tag, country in prior["countries"].items():
        if report["countries"][tag]["population"] != country["population"]:
            errors.append(f"{tag}: population changed")
    for field in ("version", "subject_types"):
        if source[field] != candidate[field]:
            errors.append(f"{field} changed")
    for state, old in source["states"].items():
        strip = lambda d: {k: v for k, v in d.items() if k != "industry"}
        if strip(old) != strip(candidate["states"][state]):
            errors.append(f"{state}: non-industry fields changed")
    if report["validation"] != "passed":
        errors.append("report validation failed")
    before = sum(c["building_levels"] for c in prior["countries"].values())
    after = sum(c["building_levels"] for c in report["countries"].values())
    result = {"passed": not errors, "building_levels_before": before, "building_levels_after": after,
              "warnings_before": len(prior["warnings"]), "warnings_after": len(report["warnings"]), "errors": errors}
    (build / "m0-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote build/mechanics/m0-verification.json (passed={result['passed']}, levels {before}->{after}, "
          f"warnings {len(prior['warnings'])}->{len(report['warnings'])})")
    if errors:
        print("\n".join(errors[:30]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
