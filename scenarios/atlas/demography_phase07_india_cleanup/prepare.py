"""Prepare a narrow India legal/identity correction in an Atlas candidate."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"
OFFICIAL_TYPES = {"bureaucrats", "officers", "aristocrats"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build/demography/india-cleanup-candidate.yml")
    args = parser.parse_args()
    output = (ROOT / args.out).resolve()
    if not output.is_relative_to(ROOT / "build"):
        raise ValueError("candidate output must stay inside this mod's build directory")
    plan = yaml.safe_load((HERE / "plan.yml").read_text(encoding="utf-8"))
    snapshot = json.loads((HERE / "legacy-population-snapshot.json").read_text(encoding="utf-8"))
    world = yaml.safe_load((ROOT / "world/scenario.yml").read_text(encoding="utf-8"))
    world["title"] = "The Golden Crescent — 1836 siyasi dünya ve Hindistan kimlik temizliği"
    world["description"] = (
        "1836 alternatif siyasi dünya: önceki demografi fazlarına ek olarak bağımsız "
        "Bengal'de insan mülkiyeti kaldırıldı ve Hint devletlerindeki miras Britanya "
        "idari kadroları yerel kadrolarla düzeltildi. Diğer Hint nüfus hedefleri geçicidir."
    )
    audit = {"shares": {}, "freed_people": 0, "local_officials": 0}
    for state, rule in plan["shares"].items():
        tag = rule["owner"]
        spec = world["states"][state]
        owners = {part["owner"] for part in spec["split"]} if "split" in spec else {spec["owner"]}
        if tag not in owners or spec.get("pops") != "inherit":
            raise ValueError(f"{state}/{tag}: political share or inheritance differs")
        rows = snapshot[state][tag]
        counts: Counter[tuple[str, str, str | None]] = Counter()
        freed = officials = 0
        for old in rows:
            culture, religion, pop_type, size = (old[k] for k in ("culture", "religion", "pop_type", "size"))
            if tag == "BGL" and pop_type == "slaves":
                pop_type = None
                freed += size
            if culture in {"british", "scottish"} and pop_type in OFFICIAL_TYPES:
                culture, religion = rule["local_culture"], rule["local_religion"]
                officials += size
            counts[culture, religion, pop_type] += size
        total = sum(counts.values())
        shares = [size / total for size in counts.values()]
        shares[-1] = 1.0 - sum(shares[:-1])
        composition = []
        for ((culture, religion, pop_type), size), share in zip(counts.items(), shares):
            row = {"culture": culture, "religion": religion, "share": share}
            if pop_type:
                row["pop_type"] = pop_type
            composition.append(row)
        population = {"total": total, "composition": composition}
        existing = spec.get("population", {}).get("by_owner", {}).get(tag)
        if existing is not None and existing != population:
            raise ValueError(f"{state}/{tag}: existing population differs; preserve manual work")
        spec.setdefault("population", {}).setdefault("by_owner", {})[tag] = population
        audit["shares"][state] = {
            "owner": tag, "population": total, "groups": {
                "/".join(part for part in key if part): size for key, size in counts.items()
            }, "freed_people": freed, "local_officials": officials,
        }
        audit["freed_people"] += freed
        audit["local_officials"] += officials
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    (output.parent / "india-cleanup-plan-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {output.relative_to(ROOT)} ({len(audit['shares'])} shares)")


if __name__ == "__main__":
    main()
