"""Capture reviewed source POP rows once, before activating phase 09."""

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
        raise SystemExit("frozen source-pops.json already exists; refusing to overwrite")
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    wanted = {(state, tag) for state, owners in plan["states"].items() for tag in owners}
    source = pdx.parse_file(ROOT / "common/history/pops/tgc_pops.txt").get_node("POPS")
    found = {}
    for state_block in source.items:
        state = state_block.key.removeprefix("s:")
        for owner_block in state_block.value.items:
            tag = owner_block.key.removeprefix("region_state:")
            if (state, tag) not in wanted:
                continue
            rows = []
            for pop in owner_block.value.getall("create_pop"):
                rows.append({"culture": pop.get_str("culture"), "religion": pop.get_str("religion"),
                             "pop_type": pop.get_str("pop_type"), "size": pop.get_int("size")})
            found[f"{state}/{tag}"] = rows
    assert set(found) == {f"{state}/{tag}" for state, tag in wanted}
    output.write_text(json.dumps(found, ensure_ascii=False, indent=2) + "\n")
    print(f"frozen {len(found)} source owner shares")


if __name__ == "__main__":
    main()
