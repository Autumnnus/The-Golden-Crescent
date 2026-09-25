"""Apply the M2 economy plans (restore-plan.yml, later fill-plan.yml) to a world copy."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/mechanics/m2-source.yml")
    parser.add_argument("--out", default="build/mechanics/m2-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    restore = yaml.safe_load((HERE / "restore-plan.yml").read_text())["states"]
    for state, entry in restore.items():
        spec = world["states"][state]
        if spec.get("buildings") != "drop" or "industry" in spec:
            raise ValueError(f"{state}: expected a dropped building policy without an industry plan")
        spec["buildings"] = entry["buildings"]
        spec["industry"] = entry["industry"]
    fill = HERE / "fill-plan.yml"
    if fill.exists():
        for state, owners in yaml.safe_load(fill.read_text())["states"].items():
            industry = world["states"][state].setdefault("industry", {})
            for tag, buildings in owners.items():
                part = industry.setdefault("by_owner", {}).setdefault(tag, {"mode": "merge", "buildings": {}})
                clash = set(buildings) & set(part["buildings"])
                if clash:
                    raise ValueError(f"{state}/{tag}: fill plan repeats restored buildings {sorted(clash)}")
                part["buildings"].update(buildings)
    world["title"] = "The Golden Crescent — 1836 dünya, kurumsal iskelet ve temel ekonomi"
    world["description"] = (
        "1836 alternatif siyasi dünya, demografi ve M1 kurumsal iskelet korunur. Siyasi aşamada "
        "düşürülen 314 state'in vanilla binaları yeni nüfusa göre küçültülüp teknolojiye uygun "
        "üretim yöntemleri ve yerel sahiplikle geri gelir; binası olmayan paylara temel ekonomi eklenir."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)} ({len(restore)} restored states)")


if __name__ == "__main__":
    main()
