"""B1: write plan.yml's technology, law, institution, building and army-unit changes into a world copy."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/balance/b1-source.yml")
    parser.add_argument("--out", default="build/balance/b1-candidate.yml")
    parser.add_argument("--countries-only", action="store_true",
                        help="re-apply only country fields (a later package such as B2 owns the buildings now)")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    for tag, row in plan["countries"].items():
        country = world["countries"].setdefault(tag, {})
        country["technology"] = row["technology"]
        if "laws" in row:
            country["laws"] = row["laws"]
        if "institutions" in row:
            country["institutions"] = row["institutions"]
        for f in (country.get("military") or {}).get("formations", []):
            for u in f.get("units", []):
                u["type"] = row.get("unit_remap", {}).get(u["type"], u["type"])
    for state, owners in ({} if args.countries_only else plan["industry"]).items():
        industry = world["states"][state].setdefault("industry", {})
        spec = world["states"][state]
        holders = {spec["owner"]} if "owner" in spec else {s["owner"] for s in spec.get("split", [])}
        for tag, buildings in owners.items():
            if holders and tag not in holders:
                continue  # a later border package moved this share (P5); its buildings were rebuilt there
            share = industry.setdefault("by_owner", {}).setdefault(tag, {"mode": "merge"})
            share.setdefault("mode", "merge")
            share.setdefault("buildings", {}).update(buildings)
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, ekonomi, diplomasi, ordular ve teknoloji dengesi (B1)"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}: {plan['summary']}")


if __name__ == "__main__":
    main()
