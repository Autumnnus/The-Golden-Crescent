"""Correct the inherited Tonga state so Samoa is a separate local polity."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TONGA = {"x208030", "xD98CDA"}
SAMOA = {"xA7F8A1", "xC00010"}
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="world/scenario.yml")
    parser.add_argument("--out", default="build/demography/oceania-political-source.yml")
    args = parser.parse_args()
    source = (ROOT / args.source).resolve()
    output = (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("input and output must stay in this mod")
    world = yaml.safe_load(source.read_text())
    if "VSM" in world["countries"]:
        raise ValueError("Samoa country already exists")
    state = world["states"]["STATE_TONGA"]
    if len(state["split"]) != 1 or state["split"][0]["owner"] != "TNG":
        raise ValueError("Tonga source owner differs")
    if set(state["split"][0]["provinces"]) != TONGA | SAMOA:
        raise ValueError("Tonga province set differs")
    world["countries"]["VSM"] = {
        "name": "Samoan Council", "name_tr": "Samoa Meclisi", "color": [151, 71, 128],
        "country_type": "decentralized", "tier": "principality",
        "cultures": ["polynesian"], "religion": "animist", "capital": "STATE_TONGA",
    }
    state["split"] = [
        {"owner": "TNG", "provinces": sorted(TONGA)},
        {"owner": "VSM", "provinces": sorted(SAMOA)},
    ]
    world["title"] = "The Golden Crescent — 1836 siyasi dünya ve Samoa düzeltmesi"
    world["description"] = (
        "Önceki siyasi dünya korunur; STATE_TONGA içindeki Tafuna ve Apia/Salelologa "
        "hub province'leri yerel Samoa Meclisi'ne ayrılır."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
