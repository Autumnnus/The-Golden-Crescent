"""Apply the M3-lite Islamic economy plan (fill-plan.yml) and Rum's 1B.2 technologies to a world copy."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/mechanics/m3-source.yml")
    parser.add_argument("--out", default="build/mechanics/m3-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = yaml.safe_load((HERE / "fill-plan.yml").read_text())
    m1 = yaml.safe_load((HERE.parent / "mechanics_m1_institutions/plan.yml").read_text())["countries"]
    # The 1B.2 technologies missing from Rum's tier 1 package are M1 canon adds (overrides.yml);
    # verify.py checks the full 1B.2 list against the built report.
    row = m1["RUM"]
    world["countries"]["RUM"]["technology"] = {"mode": "merge", "tier": row["tier"], "add": row["add_technologies"]}
    levels = 0
    for state, owners in plan["states"].items():
        industry = world["states"][state].setdefault("industry", {})
        for tag, items in owners.items():
            part = industry.setdefault("by_owner", {}).setdefault(tag, {"mode": "merge", "buildings": {}})
            if part.get("mode", "merge") != "merge":
                raise ValueError(f"{state}/{tag}: industry mode {part['mode']} would be changed")
            for name, item in items.items():
                part["buildings"][name] = item
                levels += item if isinstance(item, int) else item["level"]
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, İslam okuryazarlığı ve ekonomisi"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}: {sum(len(v) for v in plan['states'].values())} shares, {levels} planned levels")


if __name__ == "__main__":
    main()
