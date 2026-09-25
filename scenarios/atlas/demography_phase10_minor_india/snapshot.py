"""Freeze installed POP blocks for the 37 minor Indian countries once."""

from __future__ import annotations

import json
import os
import sys
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
from vic3 import pdx  # noqa: E402


def main() -> None:
    output = HERE / "source-pops.json"
    if output.exists():
        raise SystemExit("frozen source-pops.json exists; refusing to replace it")
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    tags = set(plan["countries"])
    if len(tags) != 37 or tags & (set(plan["protected_countries"]) | set(plan["deferred_border_countries"])):
        raise ValueError("minor-country scope changed")
    source = pdx.parse_file(ROOT / "common/history/pops/tgc_pops.txt").get_node("POPS")
    found = {}
    for state_block in source.items:
        state = state_block.key.removeprefix("s:")
        for owner_block in state_block.value.items:
            tag = owner_block.key.removeprefix("region_state:")
            if tag not in tags:
                continue
            if index["states"][state]["region"] != "10_india" and (state, tag) != ("STATE_PASHTUNISTAN", "CHT"):
                raise ValueError(f"{state}/{tag}: country share lies outside selected region")
            rows = [{"culture": pop.get_str("culture"), "religion": pop.get_str("religion"),
                     "pop_type": pop.get_str("pop_type"), "size": pop.get_int("size")}
                    for pop in owner_block.value.getall("create_pop")]
            found[f"{state}/{tag}"] = rows
    if {key.split("/")[1] for key in found} != tags:
        raise ValueError("some planned countries have no landed POPs")
    output.write_text(json.dumps(found, ensure_ascii=False, indent=2) + "\n")
    print(f"frozen {len(found)} state-owner POP shares for {len(tags)} countries")


if __name__ == "__main__":
    main()
