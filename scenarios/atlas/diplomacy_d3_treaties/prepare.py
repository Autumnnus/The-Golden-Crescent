"""D3: add the planned rivalries (plan.yml) to a world copy as Atlas `diplomacy.pacts`, both directions."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def rivalry_pacts(plan: dict) -> list[dict]:
    return [{"actor": a, "target": b, "type": "rivalry"} for x, y in plan["rivalries"] for a, b in ((x, y), (y, x))]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/diplomacy/d3-source.yml")
    parser.add_argument("--out", default="build/diplomacy/d3-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    pacts = world["diplomacy"].setdefault("pacts", [])
    if pacts:
        raise ValueError("the source already has pacts; D3 expects none")
    pacts.extend(rivalry_pacts(plan))
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, ekonomi, bağlılık ve antlaşmalar"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}: {len(pacts)} rivalry pacts")


if __name__ == "__main__":
    main()
