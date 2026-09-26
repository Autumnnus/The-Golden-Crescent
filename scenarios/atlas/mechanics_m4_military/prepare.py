"""M4: write plan.yml's armies and navies into a world copy (`military: {mode: replace}` per country).

Commanders and formation names are not Atlas fields; build.py writes them after `atlas build`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/mechanics/m4-source.yml")
    parser.add_argument("--out", default="build/mechanics/m4-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())["countries"]
    for tag, row in plan.items():
        world["countries"].setdefault(tag, {})["military"] = {"mode": "replace", "formations": row["formations"]}
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, ekonomi, diplomasi ve ordular (M4)"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}: military for {len(plan)} countries")


if __name__ == "__main__":
    main()
