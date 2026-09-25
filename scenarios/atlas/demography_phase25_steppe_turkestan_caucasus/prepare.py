"""Build the steppe, Turkestan, Caucasus and Afghanistan POP candidate."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = "# The Golden Crescent active 1836 political world. Generated game files are owned by Atlas.\n"


def apportion(total: int, weights: dict[str, int]) -> dict[str, int]:
    if total <= 0 or not weights or any(value <= 0 for value in weights.values()):
        raise ValueError("population and weights must be positive")
    denominator = sum(weights.values())
    exact = {key: Fraction(total * weight, denominator) for key, weight in weights.items()}
    counts = {key: int(amount) for key, amount in exact.items()}
    for key in sorted(weights, key=lambda item: (-(exact[item] - counts[item]), item))[:total - sum(counts.values())]:
        counts[key] += 1
    return counts


def share_groups(key: str, design: dict, frozen: list[dict], release: bool) -> tuple[dict, Counter]:
    """Return final joint groups and the preserved profession groups of one share."""
    target = design["population"]
    fixed, inherited = Counter(), Counter()
    for row in frozen:
        group = f"{row['culture']}/{row['religion']}"
        if row["pop_type"] == "slaves" and release:
            continue
        if row["pop_type"]:
            fixed[f"{group}/{row['pop_type']}"] += row["size"]
        else:
            inherited[group] += row["size"]
    if "slave_mix" in design:
        # Keep the preserved slave total exact while re-identifying its culture/faith groups.
        slaves = sum(count for group, count in fixed.items() if group.endswith("/slaves"))
        if "slave_total" in design:
            # Explicit design reduction of an inherited slave count; never an increase.
            if not 0 < design["slave_total"] < slaves:
                raise ValueError(f"{key}: slave_total must reduce the inherited slave count")
            slaves = design["slave_total"]
        if not slaves or release or sum(design["slave_mix"].values()) != 1000:
            raise ValueError(f"{key}: slave_mix needs preserved slaves and 1000 weights")
        fixed = Counter({group: count for group, count in fixed.items() if not group.endswith("/slaves")})
        fixed.update({f"{group}/slaves": count for group, count in apportion(slaves, design["slave_mix"]).items()})
    if release and "mix" not in design:
        raise ValueError(f"{key}: released slaves need an explicit free composition")
    mix = design.get("mix")
    if mix and sum(mix.values()) != 1000:
        raise ValueError(f"{key}: composition weights must total 1000")
    if target <= sum(fixed.values()):
        raise ValueError(f"{key}: preserved professions exceed target")
    counts = apportion(target - sum(fixed.values()), mix or dict(inherited))
    counts.update(fixed)
    return counts, fixed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="build/demography/steppe-turkestan-caucasus-source.yml",
                        help="frozen pre-phase Atlas YAML")
    parser.add_argument("--out", default="build/demography/steppe-turkestan-caucasus-candidate.yml")
    args = parser.parse_args()
    source = (ROOT / args.source).resolve()
    output = (ROOT / args.out).resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT / "build"):
        raise ValueError("source must stay in this mod and output in its build directory")
    plan = yaml.safe_load((HERE / "plan.yml").read_text())
    frozen = json.loads((HERE / "source-pops.json").read_text())
    world = yaml.safe_load(source.read_text())
    index = json.loads((ROOT / "build/index.json").read_text())
    shares = plan["shares"]
    release = set(plan["release_slaves"])
    if len(shares) != 54 or set(shares) != set(frozen) or not release <= set(shares):
        raise ValueError("plan, releases and frozen share coverage differ")
    for tag, change in plan["country_culture_overrides"].items():
        current = world["countries"].get(tag, {}).get("cultures") or index["countries"][tag]["cultures"]
        if current != change["from"]:
            raise ValueError(f"{tag}: expected pre-change primary culture differs")
        world["countries"].setdefault(tag, {})["cultures"] = change["to"]
    for tag, change in plan["country_religion_overrides"].items():
        entry = world["countries"].get(tag, {})
        current = entry.get("religion") if "religion" in entry else index["countries"][tag]["religion"]
        if current != change["from"]:
            raise ValueError(f"{tag}: expected pre-change official religion differs")
        world["countries"].setdefault(tag, {})["religion"] = change["to"]
    for tag, laws in plan["country_laws"].items():
        if "laws" in world["countries"][tag]:
            raise ValueError(f"{tag}: existing law plan would be replaced")
        world["countries"][tag]["laws"] = {"values": laws}
    audit = {"shares": {}, "countries": {}, "homelands": {}}
    state_groups = defaultdict(Counter)
    for key, design in shares.items():
        state, tag = key.split("/")
        spec = world["states"][state]
        if tag not in {part["owner"] for part in spec["split"]} or spec.get("pops") != "inherit":
            raise ValueError(f"{key}: political owner or POP policy changed")
        if tag in spec.get("population", {}).get("by_owner", {}) and key not in plan["replace_planned"]:
            raise ValueError(f"{key}: existing population plan would be replaced")
        counts, fixed = share_groups(key, design, frozen[key], key in release)
        target = design["population"]
        composition = []
        cumulative = 0.0
        rows = [(group, count) for group, count in counts.items() if count]
        for position, (group, count) in enumerate(rows):
            share = 1.0 - cumulative if position == len(rows) - 1 else count / target
            cumulative += share
            parts = group.split("/")
            row = {"culture": parts[0], "religion": parts[1], "share": share}
            if len(parts) == 3:
                row["pop_type"] = parts[2]
            composition.append(row)
            state_groups[state][parts[0]] += count
        spec.setdefault("population", {}).setdefault("by_owner", {})[tag] = {
            "total": target, "literacy": design["literacy"], "composition": composition}
        prior = sum(row["size"] for row in frozen[key])
        released = sum(row["size"] for row in frozen[key] if row["pop_type"] == "slaves" and key in release)
        audit["shares"][key] = {"prior_population": prior, "population": target, "literacy": design["literacy"],
                                "groups": dict(counts), "fixed_professions": dict(fixed),
                                "released_slaves": released, "override": "mix" in design}
    audit["homelands_skipped"] = {}
    for state, cultures in state_groups.items():
        spec = world["states"][state]
        owners = {part["owner"] for part in spec["split"]}
        here = {key.split("/")[1] for key in shares if key.startswith(state + "/")}
        earlier = set(spec["population"]["by_owner"]) - here
        if owners != here | earlier:
            # Another owner is still unplanned; the later package writes this state's homelands.
            audit["homelands_skipped"][state] = sorted(owners - here - earlier)
            continue
        for tag in earlier:
            plan_row = spec["population"]["by_owner"][tag]
            for row in plan_row["composition"]:
                cultures[row["culture"]] += round(plan_row["total"] * row["share"])
        if "homelands" in spec:
            raise ValueError(f"{state}: homeland plan already exists")
        total = sum(cultures.values())
        rule = plan["homeland_rule"]
        inherited = index["state_history"][state]["homelands"]
        kept = [culture for culture in inherited if cultures[culture] >= total * (
            rule["settler_keep_share"] if culture in rule["settler_cultures"] else rule["keep_share"])]
        new = [culture for culture, count in cultures.most_common()
               if count >= rule["new_share"] * total and culture not in kept]
        spec["homelands"] = kept + new
        audit["homelands"][state] = {"inherited": inherited, "planned": spec["homelands"]}
    for tag, policy in plan["countries"].items():
        rows = [(row["population"], row["literacy"]) for key, row in audit["shares"].items()
                if key.endswith("/" + tag)]
        total = sum(pop for pop, _ in rows)
        weighted = sum(pop * rate for pop, rate in rows) / total
        if not policy["literacy_range"][0] - 1e-9 <= weighted <= policy["literacy_range"][1] + 1e-9:
            raise ValueError(f"{tag}: weighted literacy outside plan range ({weighted:.4f})")
        audit["countries"][tag] = {"population": total, "weighted_literacy": weighted,
                                   "prior_population": sum(row["prior_population"] for key, row in
                                                           audit["shares"].items() if key.endswith("/" + tag))}
    world["title"] = "The Golden Crescent — 1836 siyasi dünya ve bozkır–Türkistan–Kafkasya demografisi"
    world["description"] = (
        "1836 alternatif siyasi dünya ve önceki demografi korunur. Kazak bozkırı, Türkistan "
        "hanlıkları, Kafkasya ve Afganistan–Belucistan'da 22 ülkenin 54 doğrudan payı nüfus ve "
        "okuryazarlık girdisi alır; bozkır ve Kafkasya'daki Rus imparatorluk yerleşimi yerel "
        "halklara döner. Sınırlar ve diplomasi değişmez."
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HEADER + yaml.safe_dump(world, allow_unicode=True, sort_keys=False, width=120))
    (output.parent / "steppe-turkestan-caucasus-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {output.relative_to(ROOT)} ({len(audit['shares'])} shares, "
          f"{sum(row['population'] for row in audit['shares'].values())} people)")


if __name__ == "__main__":
    main()
