"""M1b: country literacy targets from the user's band decisions.

Second decision (25 Sep 2026, after the third game test showed Rum/Isfahan at 70-80%): the
Middle East leads without a gulf between states, and every value is the literacy expected on the
opening screen (prepare.py derives the setup input from it and the country's schools).

- islam_lead   ~48%    Isfahan, the highest in the world
- islam_core   32-36%  Rum, Tabriz, Egypt, Andalusia, Basra
- islam_mid    22-33%  Iran members, Levant, Hijaz, Anatolian and Maghreb states, Turkestan
                       khanates, Bengal, the Mughal state, Gujarat
- islam        13-23%  poorer Islamic states; desert, steppe and decentralized polities lowest
Third decision (25 Sep): Iran is the centre of science and the renaissance, so the states around
it read a little more; so do Rum's and Egypt's neighbours, and Morocco next to Andalusia.
- europe_top   22-25%  Kalmar crowns, Scotland, New England settler states, Poland
- europe       15-20%  west and central Europe (previous demography literacy x 0.55, clamped)
- europe_south  8-14%  south and east Europe, Muscovy and the Russian principalities
- east_asia    10-18%  Jiangnan and Japan 18%, Korea 16%, other Chinese states 10-14%
- rest          2-10%  everyone else

A country is Islamic when its official religion is Sunni/Shia/Ibadi or, for vanilla countries
without an official religion (the engine then uses the primary culture's faith), when most of
its population is Muslim. `previous` is the frozen pre-M1b demography literacy; it is kept from
an existing targets.yml so a rerun on the activated world does not drift.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ISLAM = {"sunni", "shiite", "ibadi"}
LEAD = {"ISF": 0.48}
CORE = {"RUM": 0.35, "TBR": 0.36, "EGY": 0.32, "VAN": 0.34, "BSR": 0.34}
ISLAMIC_MID = {
    # Iran federation members and Herat: the circle around the renaissance centre (25 Sep: +2-4)
    "KHO": 0.33, "MAZ": 0.33, "KRM": 0.30, "HUZ": 0.29, "LUR": 0.26, "HER": 0.29,
    # Rum-bound Anatolian states
    "ADA": 0.31, "TRB": 0.31, "ERZ": 0.27,
    # Levant (Rum/Egypt neighbours), Hijaz, Gulf
    "SYR": 0.31, "LEB": 0.32, "PAL": 0.30, "HDJ": 0.30, "KUW": 0.23, "ZAI": 0.23, "OMA": 0.22,
    # Maghreb: Morocco and Mascara across the strait from Andalusia
    "MAS": 0.28, "CON": 0.26, "MOR": 0.29, "TUN": 0.27, "TRI": 0.25,
    # Turkestan, Caucasus, Volga
    "BUK": 0.30, "KOK": 0.25, "KHI": 0.24, "KSG": 0.26, "VBA": 0.28, "VCR": 0.26, "VTA": 0.24,
    # India
    "BGL": 0.24, "MUG": 0.25, "GJT": 0.24,
    # Colonies of Islamic powers in the Americas
    "VBU": 0.26, "VNE": 0.22,
}
# Poorer named Islamic states (13-23%); unnamed ones use the country-type default below.
ISLAMIC_NAMED = {
    # Rum's Balkan and Kurdish neighbours, Caucasus
    "KUR": 0.23, "BUL": 0.23, "ALB": 0.19, "BOS": 0.21, "VDA": 0.20, "VST": 0.16,
    # Afghan and Baluch neighbours of Iran
    "KAB": 0.21, "KAN": 0.19, "MAK": 0.19, "KAL": 0.19,
    "KZH": 0.15, "KIR": 0.15, "OZH": 0.15, "UZH": 0.15, "VUR": 0.14,
    "HYD": 0.20, "AWA": 0.20, "SIN": 0.17, "KAS": 0.19,
    "YOG": 0.20, "SRK": 0.20, "ACE": 0.20, "JOH": 0.19, "SAK": 0.18, "SEL": 0.18, "BRU": 0.18,
    "SOK": 0.20, "BOR": 0.19, "MSN": 0.18, "FTJ": 0.18, "HAR": 0.19, "MBS": 0.19,
    # Egypt's Nile and desert neighbours
    "VSN": 0.21, "DFR": 0.18, "WAD": 0.16, "LAH": 0.18, "AIT": 0.18, "TUG": 0.16, "FZN": 0.17,
    "VFB": 0.17, "VSI": 0.17,
}
ISLAM_DEFAULT = {"recognized": 0.18, "unrecognized": 0.17, "decentralized": 0.13}
EUROPE_TOP = {"SWE": 0.25, "DEN": 0.25, "NOR": 0.24, "VSC": 0.25, "VNI": 0.24, "VNH": 0.23, "VPA": 0.23,
              "VPL": 0.24, "KRA": 0.22, "VIN": 0.22}
EUROPE_COLONIES = {"VVA", "VDC"}  # European settler states of the Americas outside the top group
EUROPE_SOUTH_REGIONS = {"south_europe", "east_europe", "russia"}
EUROPEAN_RELIGIONS = {"catholic", "protestant", "orthodox"}
EAST_ASIA_TOP = {"JNG": 0.18, "JAP": 0.18, "KOR": 0.16}
CHINA = {"NCH", "YUE", "SHU", "MCH"}


def band_of(tag: str, religion: str | None, kind: str, region: str, previous: float) -> tuple[str, float]:
    if tag in LEAD:
        return "islam_lead", LEAD[tag]
    if tag in CORE:
        return "islam_core", CORE[tag]
    if religion in ISLAM:
        if tag in ISLAMIC_MID:
            return "islam_mid", ISLAMIC_MID[tag]
        return "islam", ISLAMIC_NAMED.get(tag, ISLAM_DEFAULT[kind])
    if tag in EUROPE_TOP:
        return "europe_top", EUROPE_TOP[tag]
    if kind != "decentralized" and (region == "west_europe" or tag in EUROPE_COLONIES):
        return "europe", max(0.15, min(0.20, round(previous * 0.55, 3)))
    if kind != "decentralized" and region in EUROPE_SOUTH_REGIONS and religion in EUROPEAN_RELIGIONS:
        return "europe_south", max(0.08, min(0.14, round(previous * 0.6, 3)))
    if tag in EAST_ASIA_TOP:
        return "east_asia", EAST_ASIA_TOP[tag]
    if tag in CHINA:
        return "east_asia", max(0.10, min(0.14, round(previous * 0.5, 3)))
    return "rest", max(0.02, min(0.10, round(previous * 0.6, 3)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/mechanics/m1b-source.yml")
    parser.add_argument("--report", default="build/mechanics/m1b-source-report.json")
    args = parser.parse_args()
    world = yaml.safe_load((ROOT / args.source).read_text())
    report = json.loads((ROOT / args.report).read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    out = HERE / "targets.yml"
    frozen = yaml.safe_load(out.read_text())["countries"] if out.exists() else {}
    lit, region = defaultdict(lambda: [0, 0]), defaultdict(lambda: defaultdict(int))
    for state, spec in world["states"].items():
        for tag, plan in spec["population"]["by_owner"].items():
            lit[tag][0] += plan["total"]
            lit[tag][1] += plan["total"] * plan["literacy"]
            region[tag][index["states"][state]["region"][3:]] += plan["total"]
    targets = {}
    for tag, country in sorted(report["countries"].items()):
        spec, vanilla = world["countries"].get(tag, {}), index["countries"].get(tag, {})
        religion = spec.get("religion") or vanilla.get("religion") or max(country["religions"], key=country["religions"].get)
        kind = spec.get("country_type") or vanilla.get("country_type")
        main_region = max(region[tag], key=region[tag].get)
        previous = frozen[tag]["previous"] if tag in frozen else round(lit[tag][1] / lit[tag][0], 4)
        band, value = band_of(tag, religion, kind, main_region, previous)
        targets[tag] = {"band": band, "target": value, "previous": previous, "type": kind,
                        "religion": religion, "region": main_region}
    unknown = (set(LEAD) | set(CORE) | set(ISLAMIC_MID) | set(ISLAMIC_NAMED) | set(EUROPE_TOP) | set(EAST_ASIA_TOP) | CHINA) - set(targets)
    if unknown:
        raise ValueError(f"named countries without land: {sorted(unknown)}")
    wrong = sorted(tag for tag in set(ISLAMIC_NAMED) | set(ISLAMIC_MID) if not targets[tag]["band"].startswith("islam"))
    if wrong:
        raise ValueError(f"named Islamic countries outside the Islamic band: {wrong}")
    out.write_text("# Generated by targets.py from the user's band decision; review, do not hand-edit.\n" +
                   yaml.safe_dump({"version": 1, "countries": targets}, allow_unicode=True, sort_keys=True, width=110))
    by = defaultdict(list)
    for tag, row in targets.items():
        by[row["band"]].append((report["countries"][tag]["population"], row["target"], row["previous"]))
    for band, rows in sorted(by.items()):
        pop = sum(p for p, _, _ in rows)
        print(f"{band}: {len(rows)} countries, {pop:,} people, literacy "
              f"{sum(p * v for p, _, v in rows) / pop:.3f} -> {sum(p * t for p, t, _ in rows) / pop:.3f}")


if __name__ == "__main__":
    main()
