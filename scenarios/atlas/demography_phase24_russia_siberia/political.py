"""Merge the residual Russian company share on Sakhalin into the local Ainu Mosir share."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
# state, old owner, new owner, expected province count of the old owner in this state
TRANSFERS = (
    ("STATE_SAKHALIN", "ALK", "AIN", 2),
)
# ALK becomes landless; its capital fallback from demography 21 is no longer needed.
REMOVED_COUNTRY_ENTRIES = {"ALK": {"capital": "STATE_SAKHALIN"}}
HEADER = "# Candidate only; active world is unchanged.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/demography/russia-siberia-source.yml")
    parser.add_argument("--out", default="build/demography/russia-siberia-political.yml")
    args = parser.parse_args()
    source = (ROOT / args.source).resolve()
    output = (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source/output must stay inside this mod; output must be under build/")
    world = yaml.safe_load(source.read_text())
    for tag, entry in REMOVED_COUNTRY_ENTRIES.items():
        if world["countries"].get(tag) != entry:
            raise ValueError(f"{tag}: source country entry differs")
        del world["countries"][tag]
    for state, old, new, expected in TRANSFERS:
        spec = world["states"][state]
        if "industry" in spec or "homelands" in spec or spec.get("pops") != "inherit":
            raise ValueError(f"{state}: source differs from expected state")
        if old in spec.get("population", {}).get("by_owner", {}):
            raise ValueError(f"{state}: {old} already has a population plan")
        parts = {part["owner"]: part for part in spec["split"]}
        if len(parts[old]["provinces"]) != expected or new not in parts:
            raise ValueError(f"{state}: {old} source provinces changed")
        parts[new]["provinces"].extend(parts[old]["provinces"])
        spec["split"].remove(parts[old])
    world["title"] = "The Golden Crescent — Sahalin yerel egemenlik düzeltme adayı"
    world["description"] = (
        "Sahalin'de kalan Rus-Amerikan şirketi payının iki province'i yerel Ainu Mosir "
        "payına katılır; şirket topraksız kalır. Diğer sınırlar ve diplomasi korunur."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
