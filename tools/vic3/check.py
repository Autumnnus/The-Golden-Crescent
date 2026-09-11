"""Validate the generated world before the game ever sees it.

Every rule here exists because it produced a real crash or a silently broken
world once (YENIDEN_KURULUM.md 2 and 3). `check` must report zero errors before
a phase counts as finished.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict

from . import build as build_mod
from . import index as idx
from . import pdx
from .paths import MOD, vanilla
from .world import World, load_world


class Report:
    def __init__(self):
        self.errors: list = []
        self.warnings: list = []

    def error(self, rule: str, msg: str) -> None:
        self.errors.append((rule, msg))

    def warn(self, rule: str, msg: str) -> None:
        self.warnings.append((rule, msg))

    def subtract(self, baseline: "Report") -> None:
        """Demote findings vanilla already has to warnings.

        Vanilla's own data is inconsistent in places — the same province in two
        states, capitals a country does not own. Something that is true of
        vanilla is not a bug we introduced, and chasing one costs hours
        (YENIDEN_KURULUM.md 2.9). Compare every finding against vanilla first.
        """
        known = set(baseline.errors)
        kept, demoted = [], []
        for item in self.errors:
            (kept if item not in known else demoted).append(item)
        self.errors = kept
        for rule, msg in demoted:
            self.warnings.append((rule + " [vanilla]", msg))

    def print(self, verbose: bool = True) -> int:
        by_rule: dict = defaultdict(list)
        for rule, msg in self.errors:
            by_rule[rule].append(msg)
        for rule, msgs in by_rule.items():
            print(f"\nERROR  {rule}  ({len(msgs)})")
            for m in msgs[:25]:
                print(f"   {m}")
            if len(msgs) > 25:
                print(f"   ... {len(msgs) - 25} more")
        if verbose:
            by_rule = defaultdict(list)
            for rule, msg in self.warnings:
                by_rule[rule].append(msg)
            for rule, msgs in by_rule.items():
                print(f"\nwarn   {rule}  ({len(msgs)})")
                for m in msgs[:10]:
                    print(f"   {m}")
                if len(msgs) > 10:
                    print(f"   ... {len(msgs) - 10} more")
        print(f"\n{len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        return 1 if self.errors else 0


# ---------------------------------------------------------------------------
# what the mod itself adds to vanilla's definition tables


def _mod_keys(subdir: str) -> set:
    d = MOD / "common" / subdir
    if not d.is_dir():
        return set()
    keys: set = set()
    for f in sorted(d.glob("*.txt")):
        for key in pdx.parse_file(f).keys():
            keys.add(re.sub(r"^REPLACE_OR_CREATE:", "", key))
    return keys


def _known(index: dict, table: str, subdir: str) -> set:
    return set(index["defs"][table]) | _mod_keys(subdir)


# ---------------------------------------------------------------------------
# rules


def _rule_capitals(rep: Report, res, index: dict) -> None:
    """Every country with land must have a capital among the states it owns.

    Applies to vanilla countries too: redistributing land moves their capital
    out from under them, and the engine answers with
    `Event target link 'capital' returned an invalid object`.
    """
    owned: dict = defaultdict(set)
    for state, owners in res.state_owners.items():
        for tag, _, _ in owners:
            owned[tag].add(state)
    for tag, states in owned.items():
        cdef = res.countries.get(tag)
        if not cdef:
            rep.error("capital", f"{tag} owns land but has no country definition")
            continue
        cap = cdef.get("capital")
        if not cap:
            rep.error("capital", f"{tag} owns land but declares no capital")
        elif cap not in states:
            rep.error("capital",
                      f"{tag} capital {cap} is not owned by {tag} "
                      f"(owns {len(states)} states)")

    # Vanilla history scripts move capitals with set_capital; a country_definitions
    # audit never sees those.
    for fname, rec in index["country_history"].items():
        for field in ("set_capital", "set_market_capital"):
            target = rec.get(field)
            if not target or not target.startswith("STATE_"):
                continue
            tags = rec.get("tags") or []
            for tag in tags:
                if tag in owned and target not in owned[tag]:
                    rep.error("capital",
                              f"{fname}: {field} = {target} but {tag} does not "
                              f"own it; override this file by name")


def _rule_double_owned(rep: Report, res, index: dict) -> None:
    seen: dict = {}
    for state, owners in res.state_owners.items():
        for tag, provs, _ in owners:
            for p in provs:
                if p in seen:
                    rep.error("province-owned-twice",
                              f"{p} claimed by {seen[p]} and {state}/{tag}")
                else:
                    seen[p] = f"{state}/{tag}"


def _rule_decentralized_buildings(rep: Report, res) -> None:
    """Writing a building for a decentralized country is a hard crash.

    The engine never allocates building storage for them, so the write lands
    in unallocated memory: 0xC0000005 on load, with nothing in the logs.
    """
    for state, by_tag in res.state_buildings.items():
        for tag in by_tag:
            if res.country_type(tag) == "decentralized":
                rep.error("decentralized-buildings",
                          f"{state}: buildings written for decentralized {tag}")


def _rule_subject_types(rep: Report, res, index: dict) -> None:
    """subject_type must accept both country_types; a mismatch fails silently."""
    subject_defs = index["defs"]["subject_types"]
    for tag, c in res.world.countries.items():
        if not c.overlord and not c.subject_type:
            continue
        if c.overlord and not c.subject_type:
            rep.error("subject", f"{tag}: overlord {c.overlord} but no subject_type")
            continue
        if c.subject_type and not c.overlord:
            rep.error("subject", f"{tag}: subject_type {c.subject_type} but no overlord")
            continue
        sdef = subject_defs.get(c.subject_type)
        if not sdef:
            rep.error("subject",
                      f"{tag}: unknown subject_type {c.subject_type!r}; "
                      f"valid: {sorted(subject_defs)}")
            continue
        if c.overlord not in res.countries:
            rep.error("subject", f"{tag}: overlord {c.overlord} is not defined")
            continue
        over_type = res.country_type(c.overlord)
        sub_type = c.country_type
        ok_over = sdef["valid_overlord_country_types"]
        ok_sub = sdef["valid_subject_country_types"]
        if ok_over and over_type not in ok_over:
            rep.error("subject",
                      f"{tag}: {c.subject_type} needs an overlord of type "
                      f"{ok_over}, but {c.overlord} is {over_type}")
        if ok_sub and sub_type not in ok_sub:
            rep.error("subject",
                      f"{tag}: {c.subject_type} needs a subject of type {ok_sub}, "
                      f"but {tag} is {sub_type}")
        if sdef.get("overlord_must_be_same_country_type") == "yes" \
                and over_type != sub_type:
            rep.error("subject",
                      f"{tag}: {c.subject_type} requires overlord and subject to "
                      f"share a country_type ({over_type} vs {sub_type})")
        if c.liberty_desire is not None and not c.overlord:
            rep.error("subject",
                      f"{tag}: liberty_desire without a subject pact "
                      f"(engine: 'Subject Pact not found')")


def _rule_landless_diplomacy(rep: Report, res) -> None:
    """Both sides of a diplomatic record must exist on the map.

    Otherwise: `Assertion failed: Attempted to create relations for invalid
    countries!` — redistribution routinely leaves vanilla tags with no land.
    """
    landed = res.landed_tags
    for entry in res.world.diplomacy:
        actor = entry.get("actor") or entry.get("country")
        targets = entry.get("targets") or ([entry["target"]]
                                           if entry.get("target") else [])
        src = entry.get("source", "?")
        if actor and actor not in landed:
            rep.error("landless-diplomacy",
                      f"{src}: {entry.get('kind')} actor {actor} owns no land")
        for t in targets:
            if t not in landed:
                rep.error("landless-diplomacy",
                          f"{src}: {entry.get('kind')} target {t} owns no land")


def _rule_replace_paths(rep: Report) -> None:
    """A declared directory the mod leaves empty deletes that content outright."""
    meta_path = MOD / ".metadata" / "metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    declared = meta.get("game_custom_data", {}).get("replace_paths", [])
    for rel in declared:
        d = MOD / rel
        files = list(d.glob("*.txt")) if d.is_dir() else []
        if not files:
            rep.error("replace_paths",
                      f"{rel} is declared in metadata.json but the mod puts no "
                      f"file there: vanilla content is deleted and nothing "
                      f"replaces it")
    for rel in sorted(build_mod.NEEDS_REPLACE_PATH):
        d = MOD / rel
        if d.is_dir() and list(d.glob("*.txt")) and rel not in declared:
            rep.error("replace_paths",
                      f"{rel} holds mod files but is not in replace_paths: "
                      f"vanilla still runs and every state is created twice")


def _rule_identifiers(rep: Report, res, index: dict) -> None:
    cultures = _known(index, "cultures", "cultures")
    religions = _known(index, "religions", "religions")
    pop_types = set(index["defs"]["pop_types"]) | _mod_keys("pop_types")
    tiers = set(index["defs"]["country_tiers"])
    ctypes = set(index["defs"]["country_types"]) | _mod_keys("country_types")
    states = set(index["states"])

    for tag, c in res.world.countries.items():
        where = f"{c.source}: {tag}"
        for cu in c.cultures:
            if cu not in cultures:
                rep.error("unknown-identifier", f"{where}: culture {cu!r}")
        if c.religion and c.religion not in religions:
            rep.error("unknown-identifier", f"{where}: religion {c.religion!r}")
        if c.country_type not in ctypes:
            rep.error("unknown-identifier", f"{where}: country_type {c.country_type!r}")
        if c.tier not in tiers:
            rep.error("unknown-identifier",
                      f"{where}: tier {c.tier!r}; valid: {sorted(tiers)}")
        if c.capital and c.capital not in states:
            rep.error("unknown-identifier", f"{where}: capital {c.capital!r}")
        for table, name in (("religion_map", "religion_map"),
                            ("religion_split", "religion_split")):
            for key, val in getattr(c, table).items():
                if key not in religions:
                    rep.error("unknown-identifier", f"{where}: {name} key {key!r}")
                targets = val if isinstance(val, dict) else {val: 1}
                for rel in targets:
                    if rel not in religions:
                        rep.error("unknown-identifier",
                                  f"{where}: {name} target {rel!r}")
        for key, val in c.culture_map.items():
            for cu in (key, val):
                if cu not in cultures:
                    rep.error("unknown-identifier", f"{where}: culture_map {cu!r}")
        for cu, split in c.culture_religion_split.items():
            if cu not in cultures:
                rep.error("unknown-identifier",
                          f"{where}: culture_religion_split culture {cu!r}")
            for rel in split:
                if rel not in religions:
                    rep.error("unknown-identifier",
                              f"{where}: culture_religion_split religion {rel!r}")

    for name, spec in res.world.states.items():
        where = f"{spec.source}: {name}"
        if name not in states:
            rep.error("unknown-identifier", f"{where}: no such state region")
            continue
        if index["states"][name]["is_sea"]:
            rep.error("unknown-identifier", f"{where}: is a sea region")
        for share in spec.shares:
            if share.owner not in res.countries:
                rep.error("unknown-identifier",
                          f"{where}: owner {share.owner!r} has no country definition")
        for cu in spec.homelands:
            if cu not in cultures:
                rep.error("unknown-identifier", f"{where}: homeland culture {cu!r}")

    for state, by_tag in res.state_pops.items():
        for tag, pops in by_tag.items():
            for p in pops:
                if p["culture"] not in cultures:
                    rep.error("unknown-identifier",
                              f"{state}/{tag}: pop culture {p['culture']!r}")
                if p.get("religion") and p["religion"] not in religions:
                    rep.error("unknown-identifier",
                              f"{state}/{tag}: pop religion {p['religion']!r}")
                if p.get("pop_type") and p["pop_type"] not in pop_types:
                    rep.error("unknown-identifier",
                              f"{state}/{tag}: pop_type {p['pop_type']!r}")


def _rule_localization(rep: Report) -> None:
    loc_dir = MOD / "localization"
    if not loc_dir.is_dir():
        return
    line_re = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*\d*\s*"')
    per_lang: dict = defaultdict(dict)
    for f in sorted(loc_dir.rglob("*.yml")):
        lang = f.parent.name
        raw = f.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            rep.error("localization",
                      f"{f.relative_to(MOD)}: missing UTF-8 BOM (the game will "
                      f"ignore this file)")
        for n, line in enumerate(pdx.read_text(f).splitlines(), 1):
            m = line_re.match(line)
            if not m:
                continue
            key = m.group(1)
            prev = per_lang[lang].get(key)
            if prev:
                rep.error("localization",
                          f"{f.relative_to(MOD)}:{n}: duplicate key {key} "
                          f"(also {prev})")
            else:
                per_lang[lang][key] = f"{f.relative_to(MOD)}:{n}"


def _rule_religion_sol_modifiers(rep: Report, index: dict) -> None:
    """A mod religion needs SoL static modifiers, and they must stay empty.

    The engine auto-generates `state_<religion>_standard_of_living_add` only for
    its own religions. Missing modifiers log `Missing religion sol static
    modifier`; using the auto-generated type in a mod religion logs
    `Unknown modifier type`.
    """
    mod_religions = _mod_keys("religions")
    if not mod_religions:
        return
    static = MOD / "common" / "static_modifiers"
    defined: dict = {}
    if static.is_dir():
        for f in sorted(static.glob("*.txt")):
            for key, node in pdx.parse_file(f).pairs():
                defined[key] = (f.name, node)
    for rel in sorted(mod_religions):
        for suffix in ("_standard_of_living_modifier_positive",
                       "_standard_of_living_modifier_negative"):
            key = rel + suffix
            if key not in defined:
                rep.error("religion-sol",
                          f"{rel}: static modifier {key} is not defined "
                          f"(engine: 'Missing religion sol static modifier')")
                continue
            fname, node = defined[key]
            bad = [k for k in node.keys() if k.endswith("_standard_of_living_add")]
            if bad:
                rep.error("religion-sol",
                          f"{fname}: {key} uses {bad[0]}, which the engine never "
                          f"generates for a mod religion "
                          f"(logs 'Unknown modifier type'); leave the body empty")


# ---------------------------------------------------------------------------
# entry point


def check(verbose: bool = True) -> int:
    rep = Report()
    index = idx.load()
    world = load_world()

    _rule_replace_paths(rep)
    _rule_localization(rep)
    _rule_religion_sol_modifiers(rep, index)

    if (MOD / "common").is_dir():
        for f in sorted((MOD / "common").rglob("*.txt")):
            try:
                pdx.parse_file(f)
            except pdx.PdxSyntaxError as e:
                rep.error("syntax", str(e))
    if (MOD / "map_data").is_dir():
        for f in sorted((MOD / "map_data").rglob("*.txt")):
            try:
                pdx.parse_file(f)
            except pdx.PdxSyntaxError as e:
                rep.error("syntax", str(e))

    if world:
        res = build_mod.Resolved(world, index)
        _world_rules(rep, res, index)
        _rule_subject_types(rep, res, index)
        _rule_landless_diplomacy(rep, res)

        # Same rules against untouched vanilla, so vanilla's own defects show
        # up as warnings instead of masking the ones we caused.
        baseline = Report()
        _world_rules(baseline, build_mod.Resolved(World(), index), index)
        rep.subtract(baseline)

        if verbose:
            print(f"checked {len(res.state_owners)} states, "
                  f"{len(res.landed_tags)} landed countries, "
                  f"{len(world.countries)} mod country definitions")
    elif verbose:
        print("world/ is empty; checking mod files only")

    return rep.print(verbose)


def _world_rules(rep: Report, res, index: dict) -> None:
    """Rules that can also fire on untouched vanilla, so they get a baseline."""
    _rule_capitals(rep, res, index)
    _rule_double_owned(rep, res, index)
    _rule_decentralized_buildings(rep, res)
    _rule_identifiers(rep, res, index)
