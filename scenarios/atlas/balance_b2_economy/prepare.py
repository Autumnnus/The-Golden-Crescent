"""B2/B3: write plan.yml's building levels and production methods into a world copy (industry.by_owner, merge)."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/balance/b2-source.yml")
    parser.add_argument("--out", default="build/balance/b2-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    for state, owners in plan["industry"].items():
        industry = world["states"][state].setdefault("industry", {})
        for tag, buildings in owners.items():
            share = industry.setdefault("by_owner", {}).setdefault(tag, {"mode": "merge"})
            share.setdefault("mode", "merge")
            share.setdefault("buildings", {}).update(buildings)
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, diplomasi, ordular, teknoloji ve ekonomi dengesi (B2)"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}: {len(plan['industry'])} states")


if __name__ == "__main__":
    main()
