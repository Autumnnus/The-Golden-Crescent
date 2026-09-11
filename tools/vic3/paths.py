"""Filesystem roots used by the toolchain.

The vanilla install is strictly read-only: it is the reference source of truth
for state regions, country definitions, cultures, religions and every other
vanilla identifier. Nothing in this toolchain ever opens it for writing.
"""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ["MOD", "VANILLA", "BUILD", "WORLD", "LOGS", "vanilla", "mod",
           "assert_read_only"]

# tools/vic3/paths.py -> tools/vic3 -> tools -> mod root
MOD = Path(__file__).resolve().parents[2]
BUILD = MOD / "build"
WORLD = MOD / "world"

_DEFAULT_VANILLA = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Victoria 3\game")

_CANDIDATES = [
    _DEFAULT_VANILLA,
    Path(r"C:\Program Files\Steam\steamapps\common\Victoria 3\game"),
    Path(r"D:\Steam\steamapps\common\Victoria 3\game"),
    Path(r"D:\SteamLibrary\steamapps\common\Victoria 3\game"),
    Path(r"E:\SteamLibrary\steamapps\common\Victoria 3\game"),
]


def _find_vanilla() -> Path:
    env = os.environ.get("VIC3_GAME_DIR")
    if env:
        p = Path(env)
        if (p / "map_data" / "state_regions").is_dir():
            return p
        raise SystemExit(f"VIC3_GAME_DIR does not look like a Victoria 3 game dir: {p}")
    for p in _CANDIDATES:
        if (p / "map_data" / "state_regions").is_dir():
            return p
    raise SystemExit(
        "Victoria 3 install not found. Set VIC3_GAME_DIR to the 'game' directory.")


VANILLA = _find_vanilla()

# Victoria 3 writes its logs next to the mod folder, two levels up from `mod/`.
LOGS = MOD.parents[1] / "logs"


def vanilla(*parts) -> Path:
    return VANILLA.joinpath(*parts)


def mod(*parts) -> Path:
    return MOD.joinpath(*parts)


def assert_read_only(path) -> None:
    """Guard every write: refuse anything that would land in the install."""
    p = Path(path).resolve()
    if p == VANILLA or VANILLA in p.parents:
        raise SystemExit(f"REFUSING to write inside the Victoria 3 install: {p}")


def write_text(path, text: str, bom: bool = True) -> None:
    """Write a game file. Paradox reads UTF-8-BOM; localization requires it."""
    path = Path(path)
    assert_read_only(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    path.write_bytes(data)
