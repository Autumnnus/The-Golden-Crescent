#!/usr/bin/env python
"""The Golden Crescent build tool.

    python tools/tgc.py index            rebuild the vanilla cache (after a patch)
    python tools/tgc.py geo              rasterise provinces.png (after a patch)
    python tools/tgc.py build            world/*.yml -> game files
    python tools/tgc.py check            validate; must be 0 errors
    python tools/tgc.py find <name>      resolve a state region by any name
    python tools/tgc.py show <state>     inspect one state region
    python tools/tgc.py map              render a map of the world

world/*.yml is the source of truth. Generated game files are never edited by
hand: `build` deletes its own previous output on every run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10+ required. Use .venv/bin/python tools/tgc.py (see tools/README.md).")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vic3.paths import MOD, VANILLA          # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="tgc.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("index", help="rebuild build/index.json from the vanilla install")

    p_geo = sub.add_parser("geo", help="rasterise provinces.png into build/")
    p_geo.add_argument("--force", action="store_true",
                       help="rebuild even if the cache looks current")

    p_build = sub.add_parser("build", help="generate game files from world/")
    p_build.add_argument("-q", "--quiet", action="store_true")

    p_check = sub.add_parser("check", help="validate the generated world")
    p_check.add_argument("-q", "--quiet", action="store_true",
                         help="errors only, hide warnings")

    p_find = sub.add_parser("find", help="resolve a state region by any name")
    p_find.add_argument("name", nargs="+")
    p_find.add_argument("-n", "--limit", type=int, default=15)

    p_show = sub.add_parser("show", help="inspect one state region")
    p_show.add_argument("state")

    p_map = sub.add_parser("map", help="render a map")
    p_map.add_argument("--mode", default="political",
                       choices=["political", "reference", "religion", "phase", "changes"])
    p_map.add_argument("--region", default=None,
                       help="crop to a region: a state name, a state_regions file "
                            "stem, or 'world'")
    p_map.add_argument("--out", default=None)
    p_map.add_argument("--labels", action="store_true", default=True)
    p_map.add_argument("--no-labels", dest="labels", action="store_false")
    p_map.add_argument("--borders", choices=["country", "state", "province", "none"], default="country")
    p_map.add_argument("--data", action="store_true", help="also write LLM-readable JSON context")
    p_atlas = sub.add_parser("atlas", help="build an offline interactive scenario atlas + JSON context")
    p_atlas.add_argument("--region", default=None, help="world, state, region file, country tag or comma-separated selectors")
    p_atlas.add_argument("--out", default=None, help="output .html path (JSON sidecar is automatic)")
    p_catalog = sub.add_parser("catalog", help="export verified map context as JSON for an LLM")
    p_catalog.add_argument("--region", default=None)
    p_catalog.add_argument("--out", default=None, help="default: JSON to stdout")
    for parser in (p_map, p_atlas, p_catalog):
        parser.add_argument("--scenario", default=None, help="preview a version 1 YAML/JSON overlay without editing world/")
        parser.add_argument("--baseline", choices=["world", "vanilla"], default="world")
        parser.add_argument("--width", type=int, default=4096 if parser is p_atlas else 3200)

    sub.add_parser("paths", help="print the resolved directories")
    sub.add_parser("selftest", help="regression-test the toolchain itself")

    args = ap.parse_args(argv)

    if args.cmd == "paths":
        print(f"mod      {MOD}")
        print(f"vanilla  {VANILLA}   (read-only)")
        print(f"build    {MOD / 'build'}")
        print(f"world    {MOD / 'world'}")
        return 0

    if args.cmd == "selftest":
        import selftest
        return selftest.main()

    if args.cmd == "index":
        from vic3 import index
        index.build_index(verbose=True)
        return 0

    if args.cmd == "geo":
        from vic3 import geo
        geo.build_geo(force=args.force)
        return 0

    if args.cmd == "build":
        from vic3 import build
        build.build(verbose=not args.quiet)
        return 0

    if args.cmd == "check":
        from vic3 import check
        return check.check(verbose=not args.quiet)

    if args.cmd == "find":
        from vic3 import report
        return report.find(" ".join(args.name), limit=args.limit)

    if args.cmd == "show":
        from vic3 import report
        return report.show(args.state)

    if args.cmd == "map":
        from vic3 import mapdraw
        return mapdraw.render(mode=args.mode, region=args.region,
                              out=args.out, labels=args.labels, width=args.width,
                              scenario_path=args.scenario, baseline=args.baseline,
                              borders=args.borders, data=args.data)

    if args.cmd == "atlas":
        from vic3.atlas import export_atlas
        return export_atlas(region=args.region, out=args.out, width=args.width,
                            scenario_path=args.scenario, baseline=args.baseline)

    if args.cmd == "catalog":
        import contextlib
        import json
        from vic3.atlas import Snapshot, write_output
        with contextlib.redirect_stdout(sys.stderr):
            snap = Snapshot(args.scenario, args.baseline)
            data = snap.llm_context(snap.viewport(args.region, args.width))
        payload = json.dumps(data, ensure_ascii=False, indent=2)
        if args.out:
            write_output(args.out, payload)
            print(f"wrote {args.out}")
        else:
            print(payload)
        return 0

    ap.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
