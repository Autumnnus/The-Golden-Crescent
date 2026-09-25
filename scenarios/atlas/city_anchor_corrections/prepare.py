"""Preview exact political micro-corrections for Indian city hub ownership."""

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
    parser.add_argument("--out", default="build/city-anchors/candidate.yml")
    args = parser.parse_args()
    output = (ROOT / args.out).resolve()
    if not output.is_relative_to(ROOT / "build"):
        raise ValueError("candidate output must stay in this mod's build directory")
    plan = yaml.safe_load((HERE / "plan.yml").read_text(encoding="utf-8"))
    world = yaml.safe_load((ROOT / "world/scenario.yml").read_text(encoding="utf-8"))
    seen = set()
    changes = []
    for move in plan["moves"]:
        state, province, old, new = (move[key] for key in ("state", "province", "from", "to"))
        if (state, province) in seen or old == new:
            raise ValueError(f"duplicate or empty move: {state}/{province}")
        seen.add((state, province))
        spec = world["states"].get(state)
        if not spec or "split" not in spec:
            raise ValueError(f"{state}: expected split state")
        parts = {part["owner"]: part["provinces"] for part in spec["split"]}
        if old not in parts or new not in parts or province not in parts[old] or province in parts[new]:
            raise ValueError(f"{state}/{province}: owner differs from frozen city-anchor plan")
        if len(parts[old]) < 2:
            raise ValueError(f"{state}/{old}: old owner would lose its final province")
        parts[old].remove(province)
        parts[new].append(province)
        changes.append({"state": state, "province": province, "hub": move["hub"], "from": old, "to": new})
    world["title"] = "The Golden Crescent — 1836 siyasi dünya ve Hint şehir merkezleri"
    world["description"] = (
        "1836 alternatif siyasi dünya: önceki demografi fazları korunur. "
        "Sekiz Hint şehir hub province'i yazılı şehir sahipleriyle eşleştirildi; "
        "diğer siyasi sınırlar değişmedi."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    (output.parent / "plan-audit.json").write_text(json.dumps(changes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output.relative_to(ROOT)} ({len(changes)} province moves)")


if __name__ == "__main__":
    main()
