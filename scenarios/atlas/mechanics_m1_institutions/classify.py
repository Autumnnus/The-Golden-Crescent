"""Derive the M1 institutional plan (tier, full law set, schools) for countries without history.

Targets are countries whose generated country history has no starting technology or politics
effect (the new political-map countries). Class rules follow the written H-profiles; named canon
decisions come from overrides.yml. Every chosen law is checked against the tier's technologies
and against disallowing laws; unavailable choices fall back to the next listed option.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ISLAMIC = {"sunni", "shiite", "ibadi"}
EUROPE = {"west_europe", "south_europe", "east_europe"}


def targets() -> list[str]:
    # The target set is frozen by the first plan: after activation these countries have
    # generated technology effects and would no longer be detected.
    if (HERE / "plan.yml").exists():
        return sorted(yaml.safe_load((HERE / "plan.yml").read_text())["countries"])
    text = (ROOT / "common/history/countries/ve_scenario_countries.txt").read_text(encoding="utf-8-sig")
    blocks = dict(re.findall(r"\nc:(\w+) \?= \{(.*?)\n\}", text, re.S))
    report = json.loads((ROOT / "build/world-political/active-political-report.json").read_text())
    return sorted(tag for tag in report["countries"]
                  if not any(k in blocks.get(tag, "") for k in ("effect_starting_technology", "add_technology_researched",
                                                                "effect_starting_politics")))


def country_facts(world: dict, index: dict) -> dict:
    lit, region = defaultdict(lambda: [0, 0]), defaultdict(lambda: defaultdict(int))
    for state, spec in world["states"].items():
        for tag, plan in spec["population"]["by_owner"].items():
            lit[tag][0] += plan["total"]
            lit[tag][1] += plan["total"] * plan["literacy"]
            region[tag][index["states"][state]["region"][3:]] += plan["total"]
    facts = {}
    for tag in lit:
        spec = world["countries"].get(tag, {})
        vanilla = index["countries"].get(tag, {})
        facts[tag] = {
            "type": spec.get("country_type") or vanilla.get("country_type"),
            "religion": spec.get("religion") or vanilla.get("religion"),
            "literacy": lit[tag][1] / lit[tag][0],
            "region": max(region[tag], key=region[tag].get),
            "overlord": None, "laws": (spec.get("laws") or {}).get("values", []),
        }
    for row in world["diplomacy"].get("subjects") or []:
        if row["subject"] in facts:
            facts[row["subject"]]["overlord"] = row["overlord"]
    return facts


def class_tier(tag: str, f: dict) -> int:
    if f["type"] == "decentralized":
        return 7
    if f["type"] == "unrecognized":
        return 5 if f["literacy"] >= 0.10 else 6
    region = f["region"]
    if region in EUROPE or region in ("middle_east", "india", "east_asia"):
        return 3
    if region in ("russia", "central_asia", "north_africa"):
        return 4 if f["literacy"] >= 0.07 else 5
    if region == "siberia":
        return 5 if f["literacy"] >= 0.07 else 6
    return 5 if f["literacy"] >= 0.07 else 6


def schools(literacy: float) -> int:
    # Sweden anchor: religious schools level 3 (+0.30 access) opened at 51% in the 24 Sep test.
    return max(0, min(5, round((literacy - 0.05) / 0.14)))


PUBLIC_BANDS = ("islam_lead", "islam_core")


def islamic_schools(literacy: float, band: str) -> int:
    # M1b (25 Sep): the 24 Sep levels 2-5 opened Rum/Isfahan at 70-80%; setup adds several points
    # per school level on top of the input, so levels stay modest: Isfahan 3, core and mid 2, others 1.
    return {"islam_lead": 3, "islam_core": 2, "islam_mid": 2}.get(band, 1)


class Builder:
    def __init__(self, rules: dict, techs: set[str]):
        self.rules, self.techs, self.laws, self.fallbacks = rules, techs, {}, []

    def ok(self, law: str) -> bool:
        rule = self.rules[law]
        if not set(rule["techs"]) <= self.techs:
            return False
        chosen = set(self.laws.values())
        return not (set(rule["disallowing"]) & chosen) and not any(
            law in self.rules[other]["disallowing"] for other in chosen)

    def pick(self, *options: str | None) -> str:
        for law in options:
            if law and self.ok(law):
                self.laws[self.rules[law]["group"]] = law
                return law
        # None of the preferred laws fits; take the first valid law of the same group and record it.
        group = self.rules[next(law for law in options if law)]["group"]
        for law in sorted(k for k, v in self.rules.items() if v["group"] == group):
            if self.ok(law):
                self.laws[group] = law
                self.fallbacks.append(f"{group}: {law} instead of {[x for x in options if x]}")
                return law
        raise ValueError(f"no available law in {group} for {options}")


def build(tag: str, f: dict, o: dict, rules: dict, tier_techs: dict, goal: dict | None = None) -> dict:
    tier = o.get("tier") or class_tier(tag, f)
    extra = ["democracy"] if o.get("republic") and "democracy" not in tier_techs[str(tier)] else []
    extra += [tech for tech in o.get("add", []) if tech not in tier_techs[str(tier)]]
    decentral = f["type"] == "decentralized"
    band = (goal or {}).get("band", "")
    islamic = f["religion"] in ISLAMIC or band.startswith("islam")
    # M1b literacy targets (mechanics_m1b_literacy/targets.yml) replace the demography average.
    target = goal["target"] if goal else f["literacy"]
    level = islamic_schools(target, band) if band.startswith("islam") and not decentral else schools(target)
    if band.startswith("islam") and not decentral:
        # Golden-age madrasa networks: every Islamic state can run religious schools, the core public ones.
        for tech in ("rationalism",) + (("empiricism",) if band in PUBLIC_BANDS else ()):
            if tech not in tier_techs[str(tier)] and tech not in extra:
                extra.append(tech)
    techs = set(tier_techs[str(tier)]) | set(extra)
    b = Builder(rules, techs)
    existing_slavery = [law for law in f["laws"] if rules[law]["group"] == "lawgroup_slavery"]
    # Order matters: education and land/church are chosen together because they disallow each other.
    if decentral:
        b.pick("law_chiefdom"); b.pick("law_elder_council"); b.pick("law_consumption_based_taxation")
        b.pick("law_isolationism"); b.pick("law_traditionalism"); b.pick("law_peasant_levies")
        b.pick(o.get("land"), "law_serfdom"); b.pick("law_state_religion" if not islamic else "law_people_of_the_book")
        b.pick("law_no_schools"); level = 0
    else:
        b.pick("law_presidential_republic" if o.get("republic") else None, "law_monarchy")
        b.pick(o.get("dist"), "law_landed_voting" if o.get("republic") else None,
               "law_oligarchy" if tier <= 3 or f["type"] == "unrecognized" else "law_autocracy", "law_autocracy")
        church = o.get("church") or ("law_people_of_the_book" if islamic else
                                     "law_freedom_of_conscience" if tier <= 3 and f["region"] not in EUROPE else
                                     "law_state_religion")
        # H9 local councils hold common land rights; they are not manorial or serf economies.
        land = o.get("land") or ("law_peasant_proprietorship" if f["type"] == "unrecognized" else
                                 "law_tenant_farmers" if tier <= 3 else "law_manorialism")
        edu = o.get("edu")
        if not edu:
            if level == 0:
                edu = "law_no_schools"
            elif band in PUBLIC_BANDS:
                edu = "law_public_schools"
            elif tier <= 2 and target >= 0.40 and church != "law_state_religion" and land != "law_serfdom":
                edu = "law_public_schools"
            else:
                edu = "law_religious_schools"
        # Resolve the known conflicts before picking: religious/public schools exclude serfdom,
        # public/private schools exclude state religion.
        if edu in ("law_religious_schools", "law_public_schools") and land == "law_serfdom":
            land = "law_manorialism"
        if edu in ("law_public_schools", "law_private_schools") and church == "law_state_religion":
            church = "law_freedom_of_conscience"
        b.pick(church, "law_state_religion")
        b.pick(land, "law_manorialism", "law_serfdom")
        b.pick(edu, "law_religious_schools", "law_no_schools")
        if b.laws["lawgroup_education_system"] == "law_no_schools":
            level = 0
        b.pick("law_cultural_exclusion" if o.get("citizenship") == "law_cultural_exclusion" else None,
               "law_national_supremacy" if tier <= 5 else "law_subjecthood", "law_subjecthood")
        b.pick("law_appointed_bureaucrats" if tier <= 4 else "law_hereditary_bureaucrats", "law_hereditary_bureaucrats")
        b.pick(o.get("economy"), "law_interventionism" if tier <= 3 else "law_traditionalism", "law_traditionalism")
        b.pick(o.get("trade"), "law_mercantilism" if tier <= 5 else "law_isolationism", "law_isolationism")
        b.pick(o.get("tax"), "law_per_capita_based_taxation" if tier <= 2 else "law_land_based_taxation")
        b.pick("law_professional_army" if tier <= 5 else "law_peasant_levies", "law_peasant_levies")
        b.pick("law_local_police" if tier <= 5 else "law_no_police", "law_no_police")
        b.pick(o.get("health"), "law_no_health_system")
    for options in (("law_right_of_assembly", "law_censorship"), ("law_no_home_affairs",),
                    ("law_no_workers_rights",), ("law_guild_system", "law_combination_acts", "law_right_to_associate"),
                    ("law_child_labor_allowed",), ("law_no_social_security",), ("law_no_colonial_affairs",)):
        b.pick(*options)
    b.pick("law_migration_controls" if not decentral and tier <= 4 else "law_closed_borders")
    b.pick("law_women_own_property" if not islamic and tier <= 3 and not decentral else "law_no_womens_rights")
    b.pick("law_merchant_navy")
    b.pick(existing_slavery[0] if existing_slavery else None, "law_slavery_banned")
    institutions = {"institution_schools": level} if level else {}
    if b.laws.get("lawgroup_health_system") == "law_charitable_health_system":
        institutions["institution_health_system"] = 1
    if b.laws.get("lawgroup_policing") == "law_local_police":
        institutions["institution_police"] = 1
    return {"tier": tier, "add_technologies": extra, "laws": sorted(b.laws.values()),
            "institutions": institutions, "literacy_target": round(target, 3),
            "notes": o.get("notes", "class rule"), "fallbacks": b.fallbacks}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="world/scenario.yml")
    parser.add_argument("--targets", help="M1b literacy targets.yml; without it the demography average is used")
    args = parser.parse_args()
    world = yaml.safe_load((ROOT / args.source).read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    rules = json.loads((HERE / "law-rules.json").read_text())
    tier_techs = json.loads((HERE / "tier-techs.json").read_text())
    overrides = yaml.safe_load((HERE / "overrides.yml").read_text())["countries"]
    facts = country_facts(world, index)
    tags = targets()
    unknown = set(overrides) - set(tags)
    if unknown:
        raise ValueError(f"overrides for countries that already have history: {sorted(unknown)}")
    goals = yaml.safe_load((ROOT / args.targets).read_text())["countries"] if args.targets else {}
    plan = {tag: build(tag, facts[tag], overrides.get(tag, {}), rules, tier_techs, goals.get(tag)) for tag in tags}
    (HERE / "plan.yml").write_text(
        "# Generated by classify.py from overrides.yml and class rules; review, do not hand-edit.\n" +
        yaml.safe_dump({"version": 1, "countries": plan}, allow_unicode=True, sort_keys=True, width=110))
    tiers = defaultdict(int)
    for row in plan.values():
        tiers[row["tier"]] += 1
    print(f"planned {len(plan)} countries; tiers {dict(sorted(tiers.items()))}")


if __name__ == "__main__":
    main()
