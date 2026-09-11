#!/usr/bin/env python
"""The Golden Crescent - harita modlama araci.

Kullanim:
    python tools/tgc.py index                 vanilla verisini index'le (bir kez / vanilla guncellenince)
    python tools/tgc.py geo                   provinces.png'den komsuluk + geometri hesapla
    python tools/tgc.py import                mevcut elle yazilmis dosyalari world/ formatina cevir
    python tools/tgc.py build                 world/ -> oyun dosyalari
    python tools/tgc.py check                 dogrulama (build oncesi/sonrasi)
    python tools/tgc.py find <isim>           state ara: 'tebriz', 'Erzurum', 'STATE_BASRA'
    python tools/tgc.py show <state>          bir state hakkindaki her seyi dok
    python tools/tgc.py neighbors <state>     komsu state'ler
    python tools/tgc.py country <TAG>         ulkenin state'leri ve toplam nufusu
    python tools/tgc.py map [--mode ...]      harita PNG'si uret
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vic3 import build as build_mod  # noqa: E402
from vic3 import geo as geo_mod  # noqa: E402
from vic3 import importer, index as index_mod, paths, render as render_mod  # noqa: E402
from vic3 import validate as validate_mod  # noqa: E402
from vic3.world import WorldError, load_world, resolve_state_name  # noqa: E402


def cmd_index(args: argparse.Namespace) -> int:
    index_mod.build_index(verbose=True)
    return 0


def cmd_geo(args: argparse.Namespace) -> int:
    geo_mod.build_geo(verbose=True)
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    starters = importer.write_starter_files()
    for path in starters:
        print(f"olusturuldu: {path}")
    country_stats = importer.import_countries()
    state_stats = importer.import_states()
    print(
        f"world/countries: {country_stats['countries']} ulke, {country_stats['files']} dosya"
    )
    print(
        f"world/states:    {state_stats['states']} state "
        f"({state_stats['split']} bolunmus), {state_stats['files']} dosya"
    )
    if state_stats["unknown"]:
        print(f"  UYARI: {state_stats['unknown']} tanimsiz state atlandi")
    print("\nSonraki adim: python tools/tgc.py build")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    try:
        report = build_mod.build(verbose=True)
    except WorldError as exc:
        print(f"HATA - world/ okunamadi: {exc}")
        return 1
    if args.quiet:
        return 0
    for path in report.files:
        print(f"  {path}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    result = validate_mod.validate(check_output=not args.source_only)
    for issue in result.issues:
        print(issue)
    print(f"\n{len(result.errors)} hata, {len(result.warnings)} uyari")
    return 1 if result.errors else 0


def cmd_find(args: argparse.Namespace) -> int:
    ix = index_mod.load_index()
    try:
        world = load_world()
    except WorldError:
        world = None
    query = " ".join(args.query)
    matches = resolve_state_name(query, world) if world else index_mod.find_states(query, ix)
    if not matches:
        print(f"'{query}' icin eslesme yok.")
        return 1
    for name in matches:
        entry = ix["states"][name]
        owner = next(iter(entry["vanilla_owners"]), "-")
        population = sum(
            p["size"] for pops in entry["vanilla_pops"].values() for p in pops
        )
        print(
            f"{name:<34} id={entry['id']:<5} {entry['strategic_region'] or '-':<26} "
            f"vanilla={owner:<4} nufus={population:>9,}"
        )
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    ix = index_mod.load_index()
    matches = resolve_state_name(args.state)
    if not matches:
        print(f"'{args.state}' bulunamadi.")
        return 1
    name = matches[0]
    entry = ix["states"][name]
    adjacency = geo_mod.load_state_adjacency()

    print(f"== {name}  (id {entry['id']})")
    print(f"   bolge        : {entry['strategic_region']}  [{entry['file']}]")
    print(f"   province     : {len(entry['provinces'])} adet, {len(entry['impassable'])} gecilmez")
    print(f"   ekilebilir   : {entry['arable_land']}  {' '.join(entry['arable_resources'])}")
    if entry["capped_resources"]:
        caps = ", ".join(f"{k}={v}" for k, v in entry["capped_resources"].items())
        print(f"   sinirli kayn.: {caps}")
    for resource in entry["resources"]:
        print(f"   kaynak       : {resource['type']} (kesfedilmemis {resource['undiscovered_amount']})")
    if entry["traits"]:
        print(f"   ozellikler   : {' '.join(entry['traits'])}")
    print(f"   komsular     : {', '.join(adjacency.get(name, []))}")
    print(f"   vanilla sahip: {', '.join(entry['vanilla_owners']) or '-'}")
    print(f"   homeland     : {', '.join(entry['vanilla_homelands']) or '-'}")

    total = 0
    print("   vanilla pop  :")
    for tag, pops in entry["vanilla_pops"].items():
        for pop in pops:
            total += pop["size"]
            bits = [pop["culture"]]
            if pop["religion"]:
                bits.append(pop["religion"])
            if pop["pop_type"]:
                bits.append(pop["pop_type"])
            print(f"      {tag}  {' / '.join(bits):<40} {pop['size']:>9,}")
    print(f"      {'TOPLAM':<46} {total:>9,}")

    print("   vanilla bina :")
    for tag, buildings in entry["vanilla_buildings"].items():
        for building in buildings:
            levels = building["levels"]
            print(f"      {tag}  {building['building']:<40} seviye {levels if levels else '-'}")

    try:
        world = load_world()
        spec = world.states.get(name)
        if spec:
            print(f"   >> world/{spec.source_file}: sahip {', '.join(spec.owners)}")
        else:
            print("   >> world/ icinde tanimli degil (vanilla mirasi)")
    except WorldError as exc:
        print(f"   >> world/ okunamadi: {exc}")
    return 0


def cmd_neighbors(args: argparse.Namespace) -> int:
    matches = resolve_state_name(args.state)
    if not matches:
        print(f"'{args.state}' bulunamadi.")
        return 1
    ix = index_mod.load_index()
    adjacency = geo_mod.load_state_adjacency()
    name = matches[0]
    print(f"{name} komsulari:")
    for neighbour in adjacency.get(name, []):
        entry = ix["states"][neighbour]
        kind = "DENIZ" if entry["is_sea"] else (next(iter(entry["vanilla_owners"]), "-"))
        print(f"  {neighbour:<34} {kind}")
    return 0


def cmd_country(args: argparse.Namespace) -> int:
    ix = index_mod.load_index()
    tag = args.tag.upper()
    try:
        world = load_world()
    except WorldError:
        world = None

    owned: list[str] = []
    if world:
        owned = sorted(n for n, s in world.states.items() if tag in s.owners)
    if not owned:
        owned = sorted(n for n, e in ix["states"].items() if tag in e["vanilla_owners"])
        source = "vanilla"
    else:
        source = "world/"

    if not owned:
        print(f"{tag}: hicbir state'e sahip degil.")
        return 1

    total = 0
    print(f"== {tag}  ({source}, {len(owned)} state)")
    for name in owned:
        entry = ix["states"][name]
        population = sum(p["size"] for pops in entry["vanilla_pops"].values() for p in pops)
        total += population
        print(f"   {name:<34} {entry['strategic_region'] or '-':<26} {population:>10,}")
    print(f"   {'TOPLAM (vanilla nufus)':<61} {total:>10,}")

    info = (world.countries.get(tag) if world else None) or ix["countries"].get(tag)
    if info:
        capital = getattr(info, "capital", None) or (info.get("capital") if isinstance(info, dict) else None)
        print(f"   baskent: {capital}")
    return 0


def cmd_regions(args: argparse.Namespace) -> int:
    ix = index_mod.load_index()
    needle = index_mod.normalize(args.filter) if args.filter else ""
    for region in sorted(ix["strategic_regions"]):
        members = [s for s in ix["strategic_regions"][region] if not ix["states"].get(s, {}).get("is_sea")]
        if not members:
            continue
        if needle and needle not in index_mod.normalize(region):
            continue
        print(f"{region:<34} {len(members):>3} state")
    return 0


def cmd_map(args: argparse.Namespace) -> int:
    out = render_mod.render(
        mode=args.mode,
        out=Path(args.out) if args.out else None,
        region=args.region,
        max_width=args.width,
        labels=not args.no_labels,
        borders=not args.no_borders,
    )
    print(f"yazildi: {out.relative_to(paths.MOD_ROOT)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tgc", description="The Golden Crescent harita modlama araci"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("index", help="vanilla verisini index'le").set_defaults(func=cmd_index)
    sub.add_parser("geo", help="komsuluk/geometri onbellegi kur").set_defaults(func=cmd_geo)
    sub.add_parser("import", help="elle yazilmis dosyalari world/ formatina al").set_defaults(
        func=cmd_import
    )

    p_build = sub.add_parser("build", help="world/ -> oyun dosyalari")
    p_build.add_argument("--quiet", action="store_true", help="dosya listesini basma")
    p_build.set_defaults(func=cmd_build)

    p_check = sub.add_parser("check", help="dogrulama")
    p_check.add_argument("--source-only", action="store_true", help="sadece world/ kontrol et")
    p_check.set_defaults(func=cmd_check)

    p_find = sub.add_parser("find", help="state ara")
    p_find.add_argument("query", nargs="+")
    p_find.set_defaults(func=cmd_find)

    p_show = sub.add_parser("show", help="bir state'in tum verisi")
    p_show.add_argument("state")
    p_show.set_defaults(func=cmd_show)

    p_neighbors = sub.add_parser("neighbors", help="komsu state'ler")
    p_neighbors.add_argument("state")
    p_neighbors.set_defaults(func=cmd_neighbors)

    p_country = sub.add_parser("country", help="ulkenin state'leri")
    p_country.add_argument("tag")
    p_country.set_defaults(func=cmd_country)

    p_regions = sub.add_parser("regions", help="strategic region listesi")
    p_regions.add_argument("filter", nargs="?", help="isme gore suz")
    p_regions.set_defaults(func=cmd_regions)

    p_map = sub.add_parser("map", help="harita PNG uret")
    p_map.add_argument("--mode", choices=["political", "reference", "diff"], default="political")
    p_map.add_argument("--region", help="strategic region adi, state listesi ya da x0,y0,x1,y1")
    p_map.add_argument("--out", help="cikti dosyasi")
    p_map.add_argument("--width", type=int, default=2400, help="maksimum genislik (piksel)")
    p_map.add_argument("--no-labels", action="store_true")
    p_map.add_argument("--no-borders", action="store_true")
    p_map.set_defaults(func=cmd_map)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
