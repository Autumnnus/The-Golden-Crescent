"""Yol tanimlari.

Vanilla dizini SALT OKUNUR. Bu modulden hicbir yazma islemi vanilla'ya gitmez;
`vanilla()` yalnizca okuma icin kullanilir, `assert_safe_write()` ise mod disina
yazmaya calisan her cagriyi hata ile durdurur.
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_VANILLA = r"C:\Program Files (x86)\Steam\steamapps\common\Victoria 3\game"

# tools/vic3/paths.py -> tools/vic3 -> tools -> <mod root>
MOD_ROOT = Path(__file__).resolve().parents[2]

VANILLA_ROOT = Path(os.environ.get("VIC3_GAME_DIR", DEFAULT_VANILLA))

# Uretilmis ara dosyalar (git disi)
BUILD_DIR = MOD_ROOT / "build"
INDEX_FILE = BUILD_DIR / "index.json"
GEO_FILE = BUILD_DIR / "geo.npz"

# Insan tarafindan yazilan kaynak veri
WORLD_DIR = MOD_ROOT / "world"
WORLD_STATES_DIR = WORLD_DIR / "states"
WORLD_COUNTRIES_DIR = WORLD_DIR / "countries"
WORLD_DEFAULTS = WORLD_DIR / "_defaults.yml"

# Render ciktilari
MAPS_DIR = MOD_ROOT / "build" / "maps"


def vanilla(*parts: str) -> Path:
    """Vanilla oyun dizini altinda bir yol dondurur (yalnizca okuma icin)."""
    return VANILLA_ROOT.joinpath(*parts)


def mod(*parts: str) -> Path:
    """Mod calisma dizini altinda bir yol dondurur."""
    return MOD_ROOT.joinpath(*parts)


def assert_safe_write(path: Path) -> Path:
    """Hedef yolun mod dizini icinde oldugunu dogrular.

    Vanilla kurulumuna ya da mod disina yazmayi deneyen her cagri burada patlar.
    Tum yazma islemleri bu fonksiyondan gecmelidir.
    """
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(MOD_ROOT)
    except ValueError:
        raise PermissionError(
            f"Mod dizini disina yazma engellendi: {resolved}\n"
            f"Izin verilen kok: {MOD_ROOT}"
        ) from None

    vanilla_resolved = VANILLA_ROOT.resolve()
    if resolved == vanilla_resolved or vanilla_resolved in resolved.parents:
        raise PermissionError(f"Vanilla dizinine yazma engellendi: {resolved}")

    return resolved


def check_vanilla_present() -> None:
    if not VANILLA_ROOT.is_dir():
        raise SystemExit(
            f"Victoria 3 oyun dizini bulunamadi: {VANILLA_ROOT}\n"
            f"VIC3_GAME_DIR ortam degiskeni ile farkli bir yol verebilirsin."
        )
