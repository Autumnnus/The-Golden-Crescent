"""D5: apply plan.yml to a world copy: vanilla subject types, no custom types, colonial colonies."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/diplomacy/d5-source.yml")
    parser.add_argument("--out", default="build/diplomacy/d5-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    mapping = {(r["overlord"], r["subject"]): r for r in plan["subjects"]}
    for row in world["diplomacy"]["subjects"]:
        target = mapping.pop((row["overlord"], row["subject"]))
        if row["type"] != target["from"]:
            raise ValueError(f"{row['overlord']}>{row['subject']}: source type {row['type']} is not {target['from']}")
        row["type"] = target["to"]
    if mapping:
        raise ValueError(f"planned subjects missing from the source: {sorted(mapping)}")
    world["subject_types"] = {}  # explicit: scenario overlays keep an omitted key
    for tag, row in plan["colonial"].items():
        entry = world["countries"][tag]
        if entry.get("country_type") != row["from"]:
            raise ValueError(f"{tag}: source type {entry.get('country_type')} is not {row['from']}")
        entry["country_type"] = "colonial"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}: {len(plan['subjects'])} subjects on vanilla types, "
          f"{len(plan['colonial'])} colonial countries, custom subject types removed")


if __name__ == "__main__":
    main()
