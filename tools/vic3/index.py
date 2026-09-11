"""Vanilla verisini tek bir aranabilir index'e cikarir.

Index olmadan her soru icin 18 tane dev state_regions dosyasini okumak gerekir.
Bu modul hepsini bir kez parse edip `build/index.json` uretir; diger tum araclar
ve Claude bu index uzerinden calisir.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import paths, pdx

SEA_FILE_PREFIX = "99_"


# ---------------------------------------------------------------------------
# state_regions
# ---------------------------------------------------------------------------

def _parse_state_regions(root: Path, source_label: str) -> dict[str, dict[str, Any]]:
    states: dict[str, dict[str, Any]] = {}
    directory = root / "map_data" / "state_regions"
    if not directory.is_dir():
        return states

    for file in sorted(directory.glob("*.txt")):
        node = pdx.parse_file(file)
        is_sea_file = file.name.startswith(SEA_FILE_PREFIX)
        for name, _op, value in node.pairs:
            if not isinstance(value, pdx.Node) or not name.startswith("STATE_"):
                continue

            resources = []
            for res in value.get_all("resource"):
                if not isinstance(res, pdx.Node):
                    continue
                resources.append(
                    {
                        "type": res.get_str("type"),
                        "depleted_type": res.get_str("depleted_type"),
                        "amount": res.get_int("amount"),
                        "undiscovered_amount": res.get_int("undiscovered_amount"),
                    }
                )

            capped: dict[str, int] = {}
            capped_block = value.get_block("capped_resources")
            if capped_block:
                for key, _o, val in capped_block.pairs:
                    if isinstance(val, str):
                        try:
                            capped[key] = int(val)
                        except ValueError:
                            pass

            states[name] = {
                "name": name,
                "id": value.get_int("id"),
                "source": source_label,
                "file": file.name,
                "is_sea": is_sea_file,
                "provinces": value.get_list("provinces"),
                "impassable": value.get_list("impassable"),
                "prime_land": value.get_list("prime_land"),
                "subsistence_building": value.get_str("subsistence_building"),
                "city": value.get_str("city"),
                "port": value.get_str("port"),
                "farm": value.get_str("farm"),
                "mine": value.get_str("mine"),
                "wood": value.get_str("wood"),
                "arable_land": value.get_int("arable_land"),
                "arable_resources": value.get_list("arable_resources"),
                "capped_resources": capped,
                "resources": resources,
                "traits": value.get_list("traits"),
                "naval_exit_id": value.get_int("naval_exit_id"),
                "strategic_region": None,
                "vanilla_owners": {},
                "vanilla_homelands": [],
                "vanilla_pops": {},
                "vanilla_buildings": {},
            }
    return states


# ---------------------------------------------------------------------------
# history/states, history/pops, history/buildings
# ---------------------------------------------------------------------------

def _strip_scope(token: str) -> str:
    """`s:STATE_X` -> `STATE_X`, `c:TUR` -> `TUR`, `cu:turkish` -> `turkish`."""
    return token.split(":", 1)[1] if ":" in token else token


def _parse_history_states(root: Path, states: dict[str, dict[str, Any]]) -> None:
    directory = root / "common" / "history" / "states"
    if not directory.is_dir():
        return
    for file in sorted(directory.glob("*.txt")):
        node = pdx.parse_file(file)
        for _key, _op, top in node.pairs:
            if not isinstance(top, pdx.Node):
                continue
            for scoped, _o, block in top.pairs:
                if not scoped.startswith("s:") or not isinstance(block, pdx.Node):
                    continue
                state_name = _strip_scope(scoped)
                entry = states.get(state_name)
                if entry is None:
                    continue
                for create in block.get_all("create_state"):
                    if not isinstance(create, pdx.Node):
                        continue
                    tag = _strip_scope(create.get_str("country") or "")
                    if not tag:
                        continue
                    entry["vanilla_owners"].setdefault(tag, [])
                    entry["vanilla_owners"][tag].extend(create.get_list("owned_provinces"))
                homelands = [_strip_scope(h) for h in block.get_all("add_homeland") if isinstance(h, str)]
                entry["vanilla_homelands"] = homelands


def _parse_history_pops(root: Path, states: dict[str, dict[str, Any]]) -> None:
    directory = root / "common" / "history" / "pops"
    if not directory.is_dir():
        return
    for file in sorted(directory.glob("*.txt")):
        node = pdx.parse_file(file)
        for _key, _op, top in node.pairs:
            if not isinstance(top, pdx.Node):
                continue
            for scoped, _o, block in top.pairs:
                if not scoped.startswith("s:") or not isinstance(block, pdx.Node):
                    continue
                entry = states.get(_strip_scope(scoped))
                if entry is None:
                    continue
                for rs_key, _o2, rs_block in block.pairs:
                    if not rs_key.startswith("region_state:") or not isinstance(rs_block, pdx.Node):
                        continue
                    tag = _strip_scope(rs_key)
                    pops = []
                    for pop in rs_block.get_all("create_pop"):
                        if not isinstance(pop, pdx.Node):
                            continue
                        pops.append(
                            {
                                "culture": pop.get_str("culture"),
                                "religion": pop.get_str("religion"),
                                "pop_type": pop.get_str("pop_type"),
                                "size": pop.get_int("size", 0),
                            }
                        )
                    entry["vanilla_pops"][tag] = pops


def _parse_history_buildings(root: Path, states: dict[str, dict[str, Any]]) -> None:
    directory = root / "common" / "history" / "buildings"
    if not directory.is_dir():
        return
    for file in sorted(directory.glob("*.txt")):
        node = pdx.parse_file(file)
        for _key, _op, top in node.pairs:
            if not isinstance(top, pdx.Node):
                continue
            for scoped, _o, block in top.pairs:
                if not scoped.startswith("s:") or not isinstance(block, pdx.Node):
                    continue
                entry = states.get(_strip_scope(scoped))
                if entry is None:
                    continue
                for rs_key, _o2, rs_block in block.pairs:
                    if not rs_key.startswith("region_state:") or not isinstance(rs_block, pdx.Node):
                        continue
                    tag = _strip_scope(rs_key)
                    buildings = []
                    for bld in rs_block.get_all("create_building"):
                        if not isinstance(bld, pdx.Node):
                            continue
                        buildings.append(
                            {
                                "building": bld.get_str("building"),
                                "levels": _building_levels(bld),
                                "production_methods": bld.get_list("activate_production_methods"),
                                # Ham govde: `buildings: inherit` icin oldugu gibi yeniden basilir
                                "raw": bld.dumps(indent=0),
                            }
                        )
                    entry["vanilla_buildings"][tag] = buildings


def _building_levels(bld: pdx.Node) -> int | None:
    ownership = bld.get_block("add_ownership")
    if ownership is None:
        return None
    for _k, _o, owner in ownership.pairs:
        if isinstance(owner, pdx.Node):
            levels = owner.get_int("levels")
            if levels is not None:
                return levels
    return None


# ---------------------------------------------------------------------------
# country_definitions / strategic_regions / gecerli id listeleri
# ---------------------------------------------------------------------------

def _parse_country_definitions(root: Path) -> dict[str, dict[str, Any]]:
    countries: dict[str, dict[str, Any]] = {}
    directory = root / "common" / "country_definitions"
    if not directory.is_dir():
        return countries
    for file in sorted(directory.glob("*.txt")):
        node = pdx.parse_file(file)
        for tag, _op, value in node.pairs:
            if not isinstance(value, pdx.Node):
                continue
            color = value.get("color")
            if isinstance(color, pdx.Node):
                color_repr = (color.prefix or "") + "{ " + " ".join(color.scalars) + " }"
            else:
                color_repr = color
            countries[tag] = {
                "tag": tag,
                "file": file.name,
                "color": color_repr,
                "country_type": value.get_str("country_type"),
                "tier": value.get_str("tier"),
                "cultures": value.get_list("cultures"),
                "capital": value.get_str("capital"),
            }
    return countries


def _parse_strategic_regions(root: Path, states: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    regions: dict[str, list[str]] = {}
    directory = root / "common" / "strategic_regions"
    if not directory.is_dir():
        return regions
    for file in sorted(directory.glob("*.txt")):
        node = pdx.parse_file(file)
        for region, _op, value in node.pairs:
            if not isinstance(value, pdx.Node):
                continue
            members = value.get_list("states")
            if not members:
                continue
            regions[region] = members
            for state_name in members:
                if state_name in states:
                    states[state_name]["strategic_region"] = region
    return regions


def _top_level_keys(directory: Path, pattern: str = "*.txt") -> list[str]:
    """Bir common/ klasorundeki tum ust seviye tanim anahtarlarini toplar."""
    keys: set[str] = set()
    if not directory.is_dir():
        return []
    for file in sorted(directory.glob(pattern)):
        try:
            node = pdx.parse_file(file)
        except ValueError:
            continue
        for key, _op, value in node.pairs:
            if isinstance(value, pdx.Node) and key and not key.startswith("@"):
                keys.add(key)
    return sorted(keys)


# ---------------------------------------------------------------------------
# Index kurulumu
# ---------------------------------------------------------------------------

def build_index(verbose: bool = True) -> dict[str, Any]:
    paths.check_vanilla_present()
    vanilla_root = paths.VANILLA_ROOT
    mod_root = paths.MOD_ROOT

    def log(message: str) -> None:
        if verbose:
            print(message)

    log("state_regions okunuyor...")
    states = _parse_state_regions(vanilla_root, "vanilla")

    # Mod kendi state_regions dosyasini koyduysa ayni isimli vanilla dosyasini
    # tamamen degistirir; index'te de mod tanimi kazanir.
    mod_states = _parse_state_regions(mod_root, "mod")
    if mod_states:
        log(f"  mod state_regions: {len(mod_states)} state override ediyor")
        states.update(mod_states)

    log("history/states okunuyor...")
    _parse_history_states(vanilla_root, states)
    log("history/pops okunuyor...")
    _parse_history_pops(vanilla_root, states)
    log("history/buildings okunuyor...")
    _parse_history_buildings(vanilla_root, states)
    log("strategic_regions okunuyor...")
    strategic = _parse_strategic_regions(vanilla_root, states)
    log("country_definitions okunuyor...")
    countries = _parse_country_definitions(vanilla_root)

    log("gecerli id listeleri toplaniyor...")
    common = vanilla_root / "common"
    valid = {
        "cultures": _top_level_keys(common / "cultures"),
        "religions": _top_level_keys(common / "religions"),
        "buildings": _top_level_keys(common / "buildings"),
        "production_methods": _top_level_keys(common / "production_methods"),
        "state_traits": _top_level_keys(common / "state_traits"),
        "pop_types": _top_level_keys(common / "pop_types"),
        "goods": _top_level_keys(common / "goods"),
        "country_types": _top_level_keys(common / "country_types"),
    }
    # Mod kendi kultur/din/trait'lerini ekliyorsa onlar da gecerlidir
    mod_common = mod_root / "common"
    for key, subdir in (
        ("cultures", "cultures"),
        ("religions", "religions"),
        ("buildings", "buildings"),
        ("production_methods", "production_methods"),
        ("state_traits", "state_traits"),
    ):
        extra = _top_level_keys(mod_common / subdir)
        if extra:
            valid[key] = sorted(set(valid[key]) | set(extra))

    # Kulturun varsayilan dini: pop'ta religion yazmadiginda oyun bunu kullanir.
    # Din donusum tablolarini dogru uygulamak icin bilmemiz gerekiyor.
    culture_religion: dict[str, str] = {}
    for culture_dir in (common / "cultures", mod_common / "cultures"):
        if not culture_dir.is_dir():
            continue
        for file in sorted(culture_dir.glob("*.txt")):
            try:
                node = pdx.parse_file(file)
            except ValueError:
                continue
            for key, _op, value in node.pairs:
                if isinstance(value, pdx.Node):
                    religion = value.get_str("religion")
                    if religion:
                        culture_religion[key] = religion

    province_to_state: dict[str, str] = {}
    duplicate_provinces: list[str] = []
    for name, entry in states.items():
        for province in entry["provinces"]:
            if province in province_to_state:
                duplicate_provinces.append(province)
            province_to_state[province] = name

    land_states = [n for n, e in states.items() if not e["is_sea"]]

    index = {
        "meta": {
            "vanilla_root": str(vanilla_root),
            "mod_root": str(mod_root),
            "state_count": len(states),
            "land_state_count": len(land_states),
            "province_count": len(province_to_state),
            "duplicate_provinces": sorted(set(duplicate_provinces)),
        },
        "states": states,
        "countries": countries,
        "strategic_regions": strategic,
        "valid": valid,
        "culture_religion": culture_religion,
        "province_to_state": province_to_state,
    }

    paths.assert_safe_write(paths.INDEX_FILE)
    paths.BUILD_DIR.mkdir(parents=True, exist_ok=True)
    paths.INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")

    log(
        f"Index yazildi: {paths.INDEX_FILE.relative_to(paths.MOD_ROOT)}  "
        f"({len(states)} state / {len(land_states)} kara, "
        f"{len(province_to_state)} province, {len(countries)} ulke)"
    )
    if duplicate_provinces:
        log(f"  UYARI: {len(set(duplicate_provinces))} province birden fazla state'te tanimli")
    return index


_CACHE: dict[str, Any] | None = None


def load_index(rebuild_if_missing: bool = True) -> dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not paths.INDEX_FILE.exists():
        if not rebuild_if_missing:
            raise SystemExit("Index yok. Once: python tools/tgc.py index")
        build_index(verbose=False)
    _CACHE = json.loads(paths.INDEX_FILE.read_text(encoding="utf-8"))
    return _CACHE


# ---------------------------------------------------------------------------
# Arama yardimcilari
# ---------------------------------------------------------------------------

_NORMALIZE = str.maketrans(
    {
        "ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g",
        "ü": "u", "Ü": "u", "ö": "o", "Ö": "o", "ç": "c", "Ç": "c",
        "â": "a", "î": "i", "û": "u", "é": "e",
    }
)


def normalize(text: str) -> str:
    """Turkce karakterleri ve ayiraclari normalize eder (arama icin)."""
    return re.sub(r"[^a-z0-9]+", "", text.lower().translate(_NORMALIZE))


def find_states(query: str, index: dict[str, Any] | None = None, limit: int = 25) -> list[str]:
    """State ismini serbest metinden bulur: 'tebriz', 'Erzurum', 'STATE_BASRA', '398'."""
    index = index or load_index()
    states = index["states"]
    needle = normalize(query)
    if not needle:
        return []

    exact: list[str] = []
    prefix: list[str] = []
    partial: list[str] = []

    for name, entry in states.items():
        short = normalize(name.removeprefix("STATE_"))
        if short == needle or normalize(name) == needle or str(entry.get("id")) == query.strip():
            exact.append(name)
        elif short.startswith(needle):
            prefix.append(name)
        elif needle in short:
            partial.append(name)

    return (exact + sorted(prefix) + sorted(partial))[:limit]
