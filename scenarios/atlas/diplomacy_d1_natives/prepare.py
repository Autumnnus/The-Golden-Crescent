"""D1: turn the native polities of plan.yml into decentralized countries on a world copy.

- `country_type: decentralized` for every listed country; people, cultures, religions,
  homelands, borders, capitals and literacy inputs are unchanged.
- The 44 M1 countries get tier 7 and the decentralized law set from the regenerated M1 plan
  (applied afterwards by mechanics_m1b_literacy/prepare.py, which owns the M1 fields).
- The six vanilla tags (SEQ, ORG, PRA, PNI, PRG, URU) switch to `history_mode: replace` with
  tier 7, the same decentralized law set and no formations: their vanilla republic, slavery,
  election and army history does not apply to a decentralized polity.
- Explicit M0/M2 industry items of these countries are removed. Atlas drops inherited vanilla
  buildings of decentralized owners itself; decentralized countries have no economy, as in vanilla.

Run before mechanics_m1b_literacy/prepare.py (which writes the M1 fields and literacy):
    python3 scenarios/atlas/diplomacy_d1_natives/prepare.py
    python3 scenarios/atlas/mechanics_m1b_literacy/prepare.py --source build/diplomacy/d1-stage.yml --out build/diplomacy/d1-candidate.yml
"""

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
    parser.add_argument("--source", default="build/diplomacy/d1-source.yml")
    parser.add_argument("--out", default="build/diplomacy/d1-stage.yml")
    args = parser.parse_args()
    source, output = (ROOT / args.source).resolve(), (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    world = yaml.safe_load(source.read_text())
    tags = yaml.safe_load((HERE / "plan.yml").read_text())["countries"]
    m1 = yaml.safe_load((HERE.parent / "mechanics_m1_institutions/plan.yml").read_text())["countries"]
    decentral_laws = next(row["laws"] for row in m1.values() if row["tier"] == 7 and "law_chiefdom" in row["laws"])
    subjects = {s["subject"] for s in world["diplomacy"]["subjects"]} | {s["overlord"] for s in world["diplomacy"]["subjects"]}
    if subjects & set(tags):
        raise ValueError(f"decentralized countries in subject relations: {sorted(subjects & set(tags))}")
    audit = {"countries": {}, "industry_removed": []}
    for tag in tags:
        entry = world["countries"][tag]
        before = entry.get("country_type")
        entry["country_type"] = "decentralized"
        if tag in m1:
            if m1[tag]["tier"] != 7:
                raise ValueError(f"{tag}: M1 plan was not regenerated with the D1 list")
            kind = "m1"
        else:
            entry["history_mode"] = "replace"
            entry["technology"] = {"mode": "replace", "tier": 7}
            entry["laws"] = {"mode": "replace", "values": decentral_laws}
            entry["institutions"] = {}
            # Vanilla line-infantry formations need technologies a tier 7 polity lacks; vanilla
            # natives (e.g. Lakota) also start without formations.
            entry["military"] = {"mode": "replace", "formations": []}
            kind = "vanilla"
        audit["countries"][tag] = {"kind": kind, "country_type_before": before}
    for state, spec in world["states"].items():
        by_owner = (spec.get("industry") or {}).get("by_owner") or {}
        for tag in sorted(set(by_owner) & set(tags)):
            levels = sum(v if isinstance(v, int) else v.get("level", 0) for v in by_owner[tag]["buildings"].values())
            audit["industry_removed"].append(f"{state}/{tag}: {levels} levels")
            del by_owner[tag]
        if "industry" in spec and not by_owner and "by_owner" in spec["industry"]:
            del spec["industry"]["by_owner"]
    world["title"] = "The Golden Crescent — 1836 dünya, kurumlar, ekonomi ve yerli merkezsiz topluluklar"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    (ROOT / "build/diplomacy/d1-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {output.relative_to(ROOT)}: {len(tags)} decentralized, industry shares removed "
          f"{len(audit['industry_removed'])}")


if __name__ == "__main__":
    main()
