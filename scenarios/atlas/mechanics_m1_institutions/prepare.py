"""Apply the M1 institutional plan (technology tier, full laws, institutions) to a world copy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/mechanics/m1-source.yml")
    parser.add_argument("--out", default="build/mechanics/m1-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())["countries"]
    for tag, row in plan.items():
        entry = world["countries"].setdefault(tag, {})
        if any(key in entry for key in ("technology", "institutions", "interest_groups")):
            raise ValueError(f"{tag}: existing institutional plan would be replaced")
        old_laws = set((entry.get("laws") or {}).get("values", []))
        if not old_laws <= set(row["laws"]):
            raise ValueError(f"{tag}: planned laws drop an existing law {sorted(old_laws - set(row['laws']))}")
        tech = {"mode": "merge", "tier": row["tier"]}
        if row["add_technologies"]:
            tech["add"] = row["add_technologies"]
        entry["technology"] = tech
        entry["laws"] = {"values": row["laws"]}
        if row["institutions"]:
            entry["institutions"] = row["institutions"]
    world["title"] = "The Golden Crescent — 1836 dünya, demografi ve kurumsal iskelet"
    world["description"] = (
        "1836 alternatif siyasi dünya ve tamamlanmış demografi korunur. Başlangıç history'si "
        "olmayan 159 ülkeye yazılı H profillerinden türetilmiş teknoloji kademesi, tam kanun seti "
        "ve okul/sağlık/polis kurumları verilir. Sınırlar, nüfus ve diplomasi değişmez."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)} ({len(plan)} countries)")


if __name__ == "__main__":
    main()
