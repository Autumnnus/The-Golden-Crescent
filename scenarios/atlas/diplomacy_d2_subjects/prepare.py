"""D2: add the planned subject types and subject relations (plan.yml) to a world copy."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"
TYPE_DEFAULTS = {"overlord_types": ["recognized", "unrecognized"], "subject_types": ["recognized", "unrecognized"],
                 "can_have_subjects": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/diplomacy/d2-source.yml")
    parser.add_argument("--out", default="build/diplomacy/d2-candidate.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    types = world.setdefault("subject_types", {})
    for key, spec in plan["subject_types"].items():
        if key in types:
            raise ValueError(f"subject type {key} already exists")
        types[key] = {"base": spec["base"], "name": spec["name"], "name_tr": spec["name_tr"], **TYPE_DEFAULTS,
                      **{k: v for k, v in spec.items() if k not in ("base", "name", "name_tr")}}
    subjects = world["diplomacy"]["subjects"]
    taken = {s["subject"] for s in subjects}
    overlords = {s["overlord"] for s in subjects}
    for row in plan["subjects"]:
        if row["subject"] in taken or row["subject"] in overlords:
            raise ValueError(f"{row['subject']} is already in a subject relation")
        if row["type"] not in types:
            raise ValueError(f"{row['subject']}: unknown subject type {row['type']}")
        for tag in (row["overlord"], row["subject"]):
            if world["countries"].get(tag, {}).get("country_type") == "decentralized":
                raise ValueError(f"{tag}: decentralized countries cannot take part in subject relations")
        taken.add(row["subject"])
        subjects.append(dict(row))
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, ekonomi ve bağlılık ağı"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}: {len(plan['subject_types'])} subject types, "
          f"{len(plan['subjects'])} new subjects ({len(subjects)} total)")


if __name__ == "__main__":
    main()
