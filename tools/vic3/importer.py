"""Elle yazilmis mevcut mod dosyalarini `world/` kaynagina cevirir.

Pipeline'a gecerken simdiye kadarki emek kaybolmasin diye bir kereye mahsus
calistirilir. Okudugu dosyalari silmez; sadece world/ altina karsiliklarini yazar.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from . import index as index_mod
from . import paths, pdx

_LOC_LINE = re.compile(r'^\s*([A-Za-z0-9_]+)\s*:\s*\d*\s*"(.*)"\s*$')


def _yaml_dump(data: dict[str, Any], header: str) -> str:
    # default_flow_style=None: kisa listeler tek satirda ([62, 122, 189]) kalir
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=None, width=200)
    return header + body


def import_states(dry_run: bool = False) -> dict[str, int]:
    ix = index_mod.load_index()
    states_index = ix["states"]

    by_region_file: dict[str, dict[str, Any]] = defaultdict(dict)
    stats = {"states": 0, "split": 0, "unknown": 0, "files": 0}

    history_dir = paths.mod("common", "history", "states")
    for file in sorted(history_dir.glob("*.txt")):
        if file.name == "00_states.txt":
            continue  # uretilmis dosya, kaynak degil
        root = pdx.parse_file(file)
        for _key, _op, top in root.pairs:
            if not isinstance(top, pdx.Node):
                continue
            for scoped, _o, block in top.pairs:
                if not scoped.startswith("s:") or not isinstance(block, pdx.Node):
                    continue
                state_name = scoped.split(":", 1)[1]
                entry = states_index.get(state_name)
                if entry is None:
                    stats["unknown"] += 1
                    continue

                owners: dict[str, list[str]] = {}
                for create in block.get_all("create_state"):
                    if not isinstance(create, pdx.Node):
                        continue
                    tag = (create.get_str("country") or "").split(":", 1)[-1]
                    if tag:
                        owners.setdefault(tag, []).extend(create.get_list("owned_provinces"))
                if not owners:
                    continue

                homelands = [
                    h.split(":", 1)[-1] for h in block.get_all("add_homeland") if isinstance(h, str)
                ]

                all_provinces = set(entry["provinces"])
                spec: dict[str, Any]
                if len(owners) == 1:
                    tag, provinces = next(iter(owners.items()))
                    if set(provinces) >= all_provinces:
                        spec = {"owner": tag}
                    else:
                        # Eksik province listesi: kalanini sahipsiz birakmak yerine
                        # ayni tag'a tam state veriyoruz ve not dusuyoruz.
                        spec = {
                            "owner": tag,
                            "_note": (
                                f"kaynak dosyada {len(set(provinces))}/{len(all_provinces)} "
                                f"province atanmisti; tam state'e cevrildi"
                            ),
                        }
                else:
                    stats["split"] += 1
                    pieces = []
                    tags = list(owners)
                    for tag in tags[:-1]:
                        pieces.append({"owner": tag, "provinces": owners[tag]})
                    pieces.append({"owner": tags[-1], "rest": True})
                    spec = {"split": pieces}

                if homelands:
                    spec["homelands"] = homelands
                spec["pops"] = "inherit"
                spec["buildings"] = "inherit"

                by_region_file[entry["file"]][state_name] = spec
                stats["states"] += 1

    if dry_run:
        return stats

    paths.WORLD_STATES_DIR.mkdir(parents=True, exist_ok=True)
    for region_file, states in sorted(by_region_file.items()):
        out = paths.WORLD_STATES_DIR / (Path(region_file).stem + ".yml")
        paths.assert_safe_write(out)
        header = (
            f"# {region_file} bolgesindeki state atamalari\n"
            f"# Elle duzenlenir. Oyun dosyalari: python tools/tgc.py build\n\n"
        )
        out.write_text(_yaml_dump(dict(sorted(states.items())), header), encoding="utf-8")
        stats["files"] += 1
    return stats


def import_countries(dry_run: bool = False) -> dict[str, int]:
    ix = index_mod.load_index()
    loc_names = _read_localization()
    stats = {"countries": 0, "files": 0}

    by_file: dict[str, dict[str, Any]] = defaultdict(dict)
    definitions_dir = paths.mod("common", "country_definitions")
    for file in sorted(definitions_dir.glob("*.txt")):
        if file.name == "tgc_countries.txt" or file.name in ix["countries"]:
            pass
        root = pdx.parse_file(file)
        for tag, _op, value in root.pairs:
            if not isinstance(value, pdx.Node):
                continue
            color = value.get("color")
            if isinstance(color, pdx.Node):
                if color.prefix:
                    color_value = f"{color.prefix}{{ {' '.join(color.scalars)} }}"
                else:
                    color_value = [int(c) if c.isdigit() else c for c in color.scalars]
            else:
                color_value = color

            spec: dict[str, Any] = {
                "color": color_value,
                "country_type": value.get_str("country_type", "unrecognized"),
                "tier": value.get_str("tier", "principality"),
                "cultures": value.get_list("cultures"),
                "capital": value.get_str("capital"),
            }
            if tag in loc_names:
                name, adjective = loc_names[tag]
                if name:
                    spec["name"] = name
                if adjective:
                    spec["adjective"] = adjective
            by_file[file.stem][tag] = spec
            stats["countries"] += 1

    if dry_run:
        return stats

    paths.WORLD_COUNTRIES_DIR.mkdir(parents=True, exist_ok=True)
    for stem, countries in sorted(by_file.items()):
        out = paths.WORLD_COUNTRIES_DIR / f"{stem}.yml"
        paths.assert_safe_write(out)
        header = (
            "# Ulke tanimlari. religion_map / culture_map ekleyerek bu ulkenin\n"
            "# miras alinan pop'larini toptan donusturebilirsin.\n\n"
        )
        out.write_text(_yaml_dump(dict(sorted(countries.items())), header), encoding="utf-8")
        stats["files"] += 1
    return stats


def _read_localization() -> dict[str, tuple[str | None, str | None]]:
    """Mod localization'indan tag -> (isim, sifat) cikarir."""
    names: dict[str, tuple[str | None, str | None]] = {}
    loc_root = paths.mod("localization")
    if not loc_root.is_dir():
        return names
    for file in sorted(loc_root.rglob("*_l_english.yml")):
        if "tgc_generated" in file.name:
            continue
        for line in file.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            match = _LOC_LINE.match(line)
            if not match:
                continue
            key, value = match.group(1), match.group(2)
            if key.endswith("_ADJ"):
                tag = key[:-4]
                current = names.get(tag, (None, None))
                names[tag] = (current[0], value)
            elif len(key) == 3 and key.isupper():
                current = names.get(key, (None, None))
                names[key] = (value, current[1])
    return names


def write_starter_files() -> list[str]:
    """world/_defaults.yml ve _aliases.yml yoksa olusturur."""
    written: list[str] = []
    paths.WORLD_DIR.mkdir(parents=True, exist_ok=True)

    if not paths.WORLD_DEFAULTS.exists():
        paths.assert_safe_write(paths.WORLD_DEFAULTS)
        paths.WORLD_DEFAULTS.write_text(
            "# Global ayarlar\n"
            "\n"
            "# world/states altinda tanimlanmayan state'ler ne olsun?\n"
            "#   inherit -> vanilla sahibi/pop'u/binasi aynen korunur (kademeli gelistirme icin)\n"
            "#   drop    -> sahipsiz kalir (tam total conversion icin)\n"
            "unlisted: inherit\n"
            "\n"
            "# Tum miras alinan pop'lara uygulanan carpan\n"
            "pop_scale: 1.0\n"
            "\n"
            "# Global din donusumu: vanilla dini -> mod dini\n"
            "# Ornek:\n"
            "#   religion_map:\n"
            "#     sunni: mujtahidiyya\n"
            "religion_map: {}\n"
            "\n"
            "# Global kultur donusumu\n"
            "culture_map: {}\n",
            encoding="utf-8",
        )
        written.append(str(paths.WORLD_DEFAULTS.relative_to(paths.MOD_ROOT)))

    aliases_file = paths.WORLD_DIR / "_aliases.yml"
    if not aliases_file.exists():
        paths.assert_safe_write(aliases_file)
        aliases_file.write_text(
            "# Serbest/Turkce isim -> STATE_* eslemesi.\n"
            "# Bir bolgeyi Turkce adiyla soyleyince dogru state bulunsun diye.\n"
            "# `python tools/tgc.py find <isim>` once buraya bakar.\n"
            "\n"
            "Tebriz: STATE_TABRIZ\n"
            "Konstantiniyye: STATE_EASTERN_THRACE\n"
            "Istanbul: STATE_EASTERN_THRACE\n"
            "Selanik: STATE_MACEDONIA\n"
            "Sam: STATE_SYRIA\n"
            "Halep: STATE_ALEPPO\n"
            "Musul: STATE_MOSUL\n"
            "Bagdat: STATE_BAGHDAD\n"
            "Kudus: STATE_PALESTINE\n"
            "Kahire: STATE_LOWER_EGYPT\n"
            "Iskenderiye: STATE_LOWER_EGYPT\n"
            "Kurtuba: STATE_ANDALUSIA\n"
            "Isfahan: STATE_ISFAHAN\n"
            "Kasgar: STATE_KASHGAR\n"
            "Diyarbakir: STATE_DIYARBAKIR\n"
            "Erzurum: STATE_ERZURUM\n"
            "Trabzon: STATE_TRABZON\n"
            "Adana: STATE_ADANA\n"
            "Baku: STATE_BAKU\n"
            "Basra: STATE_BASRA\n"
            "Mekke: STATE_HEJAZ\n"
            "Necid: STATE_NEJD\n",
            encoding="utf-8",
        )
        written.append(str(aliases_file.relative_to(paths.MOD_ROOT)))

    return written
