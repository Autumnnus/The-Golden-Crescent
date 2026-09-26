"""D4: apply the recognition plan (plan.yml) to a world copy: only `country_type` changes."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/diplomacy/d4-source.yml")
    parser.add_argument("--out", default="build/diplomacy/d4-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())["countries"]
    for tag, row in plan.items():
        entry = world["countries"].setdefault(tag, {})
        if entry.get("country_type", row["from"]) != row["from"]:
            raise ValueError(f"{tag}: source type {entry.get('country_type')} is not the planned {row['from']}")
        entry["country_type"] = row["to"]
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, ekonomi, bağlılık, antlaşmalar ve tanınma"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}: {len(plan)} country types changed")


if __name__ == "__main__":
    main()
