"""Remove the two inherited Boer state owners before the final Africa POP plan."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TRANSFERS = (
    ("STATE_VRYSTAAT", "ORA", "BST", 17),
    ("STATE_TRANSVAAL", "TRN", "MTB", 11),
)
HOMELANDS = {
    "STATE_CAPE_COLONY": ["sotho", "khoisan"],
    "STATE_NORTHERN_CAPE": ["griqua", "sotho", "khoisan", "tswana"],
    "STATE_VRYSTAAT": ["griqua", "sotho", "nguni"],
    "STATE_TRANSVAAL": ["sotho", "nguni", "tswana", "zulu"],
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/demography/rest-africa-political-source.yml")
    parser.add_argument("--out", default="build/demography/rest-africa-political-candidate.yml")
    args = parser.parse_args()
    source = (ROOT / args.source).resolve()
    output = (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source/output must stay inside this mod; output must be under build/")
    world = yaml.safe_load(source.read_text())
    for state, old, new, expected_provinces in TRANSFERS:
        spec = world["states"][state]
        if "population" in spec or "homelands" in spec or spec.get("pops") != "inherit":
            raise ValueError(f"{state}: source differs from expected pre-demography state")
        parts = {part["owner"]: part for part in spec["split"]}
        if len(parts[old]["provinces"]) != expected_provinces or old == new:
            raise ValueError(f"{state}: source owner provinces changed")
        parts[new]["provinces"].extend(parts[old]["provinces"])
        spec["split"].remove(parts[old])
    for state, cultures in HOMELANDS.items():
        if "homelands" in world["states"][state]:
            raise ValueError(f"{state}: homeland plan already exists")
        world["states"][state]["homelands"] = cultures
    world["title"] = "The Golden Crescent — Güney Afrika yerel egemenlik düzeltme adayı"
    world["description"] = (
        "Oranje ve Transvaal Boer devletlerinin küçük 1836 toprak payları, "
        "yazılı senaryodaki yerel egemenlik ilkesine uygun olarak Basotho ve "
        "Ndebele yönetimlerine aktarılır; dört state'ten Boer homeland kaldırılır."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("# Candidate only; active world is unchanged.\n" +
                      yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
