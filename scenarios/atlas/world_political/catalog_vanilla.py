#!/usr/bin/env python3
"""Run an Atlas catalog against vanilla, independent of the active mod world.

Political card generators need the installed game's starting ownership. Once
world/scenario.yml is active, a normal catalog overlays it and can silently
change the inputs to those generators. A disposable empty mod keeps that
baseline stable while leaving the real mod and the game installation untouched.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def main(argv: list[str]) -> None:
    if argv[:2] != ["atlas", "catalog"]:
        raise ValueError("Only 'atlas catalog' is supported")
    args = argv[2:]
    if "--out" not in args:
        raise ValueError("Catalog output must be explicit (--out)")
    out_index = args.index("--out") + 1
    output = (ROOT / args[out_index]).resolve()
    if not output.is_relative_to(ROOT / "build"):
        raise ValueError("Catalog output must stay inside this mod's build directory")

    if "--scenario" in args:
        scenario_index = args.index("--scenario") + 1
        args[scenario_index] = str((ROOT / args[scenario_index]).resolve())

    config = ROOT / ".vic3-tools.local.json"
    if not config.is_file():
        raise ValueError("Shared toolkit is not configured; run scripts/tools.py doctor")
    toolkit = Path(json.loads(config.read_text(encoding="utf-8"))["toolkit"]).expanduser().resolve()
    entry = toolkit / "vic3tools.py"
    if not entry.is_file():
        raise ValueError(f"Shared toolkit entry not found: {entry}")

    scratch_parent = ROOT / "build/world-political"
    scratch_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vanilla-catalog-", dir=scratch_parent) as directory:
        scratch = Path(directory)
        metadata = scratch / ".metadata/metadata.json"
        metadata.parent.mkdir(parents=True)
        metadata.write_text(json.dumps({"name": "Disposable vanilla catalog", "version": "0"}))
        scratch_output = scratch / "build/catalog.json"
        args[out_index] = str(scratch_output)
        subprocess.run(
            [sys.executable, str(entry), "--mod", str(scratch), "atlas", "catalog", *args],
            cwd=ROOT,
            check=True,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(scratch_output, output)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (OSError, ValueError, KeyError) as exc:
        print(f"Hata: {exc}", file=sys.stderr)
        raise SystemExit(1)
