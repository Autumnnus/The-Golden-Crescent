"""Report explicit state-owner POP-plan coverage in the active Atlas world."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGIONS = {
    "00_west_europe": "Batı Avrupa",
    "01_south_europe": "Güney Avrupa",
    "02_east_europe": "Doğu Avrupa",
    "03_north_africa": "Kuzey Afrika / Sahel",
    "04_subsaharan_africa": "Sahra-altı Afrika",
    "05_north_america": "Kuzey Amerika",
    "06_central_america": "Orta Amerika",
    "07_south_america": "Güney Amerika",
    "08_middle_east": "Ortadoğu",
    "09_central_asia": "Orta Asya",
    "10_india": "Hindistan",
    "11_east_asia": "Doğu Asya",
    "12_indonesia": "Endonezya",
    "13_australasia": "Avustralasya",
    "14_siberia": "Sibirya",
    "15_russia": "Rusya",
}


def main() -> None:
    world = yaml.safe_load((ROOT / "world/scenario.yml").read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    by_region = defaultdict(lambda: [0, 0, set()])
    full = partial = untouched = 0
    for state, spec in world["states"].items():
        owners = {part["owner"] for part in spec["split"]} if "split" in spec else {spec["owner"]}
        planned = set(spec.get("population", {}).get("by_owner", {}))
        if not planned <= owners:
            raise ValueError(f"{state}: POP plan contains a non-owner: {sorted(planned - owners)}")
        if "population" in spec and "by_owner" not in spec["population"]:
            raise ValueError(f"{state}: add coverage handling for state-wide population")
        region = index["states"][state]["region"]
        by_region[region][0] += len(owners)
        by_region[region][1] += len(planned)
        if owners == planned:
            full += 1
        elif planned:
            partial += 1
        else:
            untouched += 1
        if owners != planned:
            by_region[region][2].add(state)
    total = sum(row[0] for row in by_region.values())
    done = sum(row[1] for row in by_region.values())
    print(f"State–ülke payı: {done}/{total} (%{done / total * 100:.1f}); kalan {total - done}")
    print(f"State: {full} tam, {partial} kısmi, {untouched} plansız; toplam {full + partial + untouched}")
    print(f"Açık teknik bölge: {sum(row[0] > row[1] for row in by_region.values())}/{len(by_region)}")
    print("Bölge | Planlı pay | Açık pay | Açık state")
    for region, (shares, planned, open_states) in sorted(by_region.items()):
        print(f"{REGIONS.get(region, region)} | {planned}/{shares} | {shares - planned} | {len(open_states)}")
    print("Bu yalnız açık POP planı kapsamıdır; ekonomi, kanun veya motor testi ilerlemesini ölçmez.")


if __name__ == "__main__":
    main()
