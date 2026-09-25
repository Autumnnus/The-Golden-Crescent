"""Replace the Russian Alaska company and Texas republic shares with local polities."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
# state, old owner, new owner, expected province count of the old owner in this state
TRANSFERS = (
    ("STATE_ALASKA", "ALK", "VTU", 287),
    ("STATE_TEXAS", "TEX", "VCD", 81),
)
COUNTRIES = {
    "VTU": {
        "name": "Tlingit-Unangan Coast Council", "name_tr": "Tlingit–Unangan Kıyı Meclisi",
        "color": [70, 110, 140], "country_type": "unrecognized", "tier": "principality",
        "cultures": ["athabaskan", "inuit"], "religion": "animist", "capital": "STATE_ALASKA",
    },
    "VCD": {
        "name": "Caddo Confederacy", "name_tr": "Caddo Konfederasyonu",
        "color": [132, 92, 60], "country_type": "unrecognized", "tier": "principality",
        "cultures": ["caddoan"], "religion": "animist", "capital": "STATE_TEXAS",
    },
    # ALK keeps only its two unchanged Sakhalin provinces, so its capital must move there.
    "ALK": {"capital": "STATE_SAKHALIN"},
}
HEADER = "# Candidate only; active world is unchanged.\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/demography/north-america-source.yml")
    parser.add_argument("--out", default="build/demography/north-america-political.yml")
    args = parser.parse_args()
    source = (ROOT / args.source).resolve()
    output = (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source/output must stay inside this mod; output must be under build/")
    world = yaml.safe_load(source.read_text())
    if set(COUNTRIES) & set(world["countries"]):
        raise ValueError("new or overridden country already exists in source")
    for state, old, new, expected in TRANSFERS:
        spec = world["states"][state]
        if any(key in spec for key in ("population", "homelands", "industry")) or spec.get("pops") != "inherit":
            raise ValueError(f"{state}: source differs from expected pre-demography state")
        parts = [part for part in spec["split"] if part["owner"] == old]
        if len(parts) != 1 or len(parts[0]["provinces"]) != expected:
            raise ValueError(f"{state}: {old} source provinces changed")
        parts[0]["owner"] = new
    # The inherited ALK anchorage and company whaling station need navigation; new local
    # councils start without technologies. The logging camp is kept.
    world["states"]["STATE_ALASKA"]["industry"] = {"by_owner": {"VTU": {
        "mode": "merge", "buildings": {"building_port": 0, "building_whaling_station": 0,
                                       # Post-test fix: the inherited camp belonged to the Russian company.
                                       "building_logging_camp": {"level": 2, "ownership": "self"}}}}}
    # TEX's maize farm needs enclosure; like the other American local councils VCD starts
    # without buildings until the economy phase.
    world["states"]["STATE_TEXAS"]["industry"] = {"by_owner": {"VCD": {
        "mode": "merge", "buildings": {"building_maize_farm": 0, "building_naval_administration": 0}}}}
    sakhalin = {part["owner"]: len(part["provinces"]) for part in world["states"]["STATE_SAKHALIN"]["split"]}
    if sakhalin.get("ALK") != 2:
        raise ValueError("ALK Sakhalin share differs; capital fallback would be invalid")
    world["countries"].update(COUNTRIES)
    world["title"] = "The Golden Crescent — Alaska ve Teksas yerel egemenlik düzeltme adayı"
    world["description"] = (
        "Rus-Amerikan şirketinin Alaska kıyı payı yerel Tlingit–Unangan meclisine, "
        "ABD yerleşim genişlemesinden doğan Teksas cumhuriyetinin payı Caddo "
        "konfederasyonuna aktarılır. Diğer sınırlar ve diplomasi korunur."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    print(f"wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
