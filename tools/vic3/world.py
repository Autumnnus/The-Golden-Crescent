"""Load world/*.yml — the single source of truth for the mod's world.

Nothing under world/ is a game file. `build` turns it into game files; a game
file is never edited by hand. The schema is documented in tools/README.md and
mirrored by the dataclasses below.

Layout
------
    world/_aliases.yml          free-form name -> STATE_* (used by `find`)
    world/countries/*.yml       TAG -> country spec
    world/states/*.yml          STATE_* -> ownership spec
    world/diplomacy/*.yml       pacts and relations
    world/state_regions/*.yml   patches to map_data/state_regions (use sparingly)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .paths import WORLD

__all__ = ["World", "Country", "StateSpec", "load_world", "WorldError"]


class WorldError(ValueError):
    """A world/*.yml file is malformed. Always names the file and the key."""


# Literacy bands, resolved to a rate at build time.
LITERACY = {
    "very_high": 0.80,
    "high": 0.60,
    "middling": 0.35,
    "low": 0.15,
    "very_low": 0.05,
    "baseline": 0.02,
}

_COUNTRY_KEYS = {
    "color", "country_type", "tier", "cultures", "religion", "tech_tier",
    "literacy", "capital", "name", "adjective", "name_tr", "adjective_tr",
    "religion_map", "religion_split", "culture_religion_split", "culture_map",
    "overlord", "subject_type", "liberty_desire", "market_capital", "notes",
    "coat_of_arms", "is_named_from_capital", "phase",
    "population", "industry", "technology", "laws", "institutions",
    "interest_groups", "companies", "military", "history_mode",
}

_STATE_KEYS = {
    "owner", "pops", "buildings", "split", "homelands", "claims", "state_type",
    "notes", "phase", "population", "industry",
}

_SPLIT_KEYS = {"owner", "provinces", "rest", "state_type"}


@dataclass(slots=True)
class Country:
    tag: str
    source: str = ""                     # file it came from, for error messages
    color: list | None = None
    country_type: str = "recognized"
    tier: str = "kingdom"
    cultures: list = field(default_factory=list)
    religion: str | None = None
    tech_tier: int | None = None
    literacy: str | None = None
    capital: str | None = None
    market_capital: str | None = None
    name: str | None = None
    adjective: str | None = None
    name_tr: str | None = None
    adjective_tr: str | None = None
    religion_map: dict = field(default_factory=dict)
    religion_split: dict = field(default_factory=dict)
    culture_religion_split: dict = field(default_factory=dict)
    culture_map: dict = field(default_factory=dict)
    overlord: str | None = None
    subject_type: str | None = None
    liberty_desire: float | None = None
    coat_of_arms: str | None = None
    is_named_from_capital: str | None = None
    phase: str | None = None
    notes: str | None = None

    population: dict = field(default_factory=dict)
    industry: dict = field(default_factory=dict)
    technology: dict = field(default_factory=dict)
    laws: dict = field(default_factory=dict)
    institutions: dict = field(default_factory=dict)
    interest_groups: dict = field(default_factory=dict)
    companies: dict = field(default_factory=dict)
    military: dict = field(default_factory=dict)
    history_mode: str = "inherit"

    @property
    def is_subject(self) -> bool:
        return bool(self.overlord)

    @property
    def literacy_rate(self):
        if self.literacy is None:
            return None
        return LITERACY[self.literacy] if isinstance(self.literacy, str) else self.literacy


@dataclass(slots=True)
class Share:
    """One owner's share of a state region."""
    owner: str
    provinces: list = field(default_factory=list)   # empty == "the rest"
    rest: bool = False
    state_type: str | None = None


@dataclass(slots=True)
class StateSpec:
    state: str
    source: str = ""
    shares: list = field(default_factory=list)      # list[Share]
    pops: str = "inherit"                           # inherit | drop
    buildings: str = "inherit"                      # inherit | drop
    homelands: list = field(default_factory=list)
    claims: list = field(default_factory=list)
    phase: str | None = None
    notes: str | None = None

    population: dict = field(default_factory=dict)
    industry: dict = field(default_factory=dict)
    ownership_inherit: bool = False
    state_type: str | None = None
    homelands_explicit: bool = False
    claims_explicit: bool = False

    @property
    def owners(self) -> list:
        return [s.owner for s in self.shares]


@dataclass(slots=True)
class World:
    countries: dict = field(default_factory=dict)   # tag -> Country
    states: dict = field(default_factory=dict)      # STATE_* -> StateSpec
    diplomacy: list = field(default_factory=list)
    region_patches: dict = field(default_factory=dict)
    aliases: dict = field(default_factory=dict)

    diplomacy_policy: dict = field(default_factory=dict)
    subject_types: dict = field(default_factory=dict)
    version: int = 1

    def __bool__(self) -> bool:
        return bool(self.countries or self.states or self.diplomacy
                    or self.region_patches or self.diplomacy_policy or self.subject_types)

    def subjects_of(self, tag: str) -> list:
        return [c for c in self.countries.values() if c.overlord == tag]


# ---------------------------------------------------------------------------
# loading


def _yaml_files(subdir: str) -> list[Path]:
    d = WORLD / subdir
    if not d.is_dir():
        return []
    return sorted(p for p in d.rglob("*.yml") if not p.name.startswith("_"))


def _load_yaml(path: Path) -> dict:
    try:
        from .scenario import UniqueLoader
        data = yaml.load(path.read_text(encoding="utf-8-sig"), Loader=UniqueLoader)
    except yaml.YAMLError as e:
        raise WorldError(f"{path.name}: invalid YAML: {e}") from None
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise WorldError(f"{path.name}: top level must be a mapping")
    return data


def _reject_unknown(path: Path, key: str, spec: dict, allowed: set) -> None:
    extra = set(spec) - allowed
    if extra:
        raise WorldError(
            f"{path.name}: {key}: unknown field(s) {sorted(extra)}; "
            f"allowed: {sorted(allowed)}")


def _as_list(v) -> list:
    if v is None:
        return []
    return list(v) if isinstance(v, (list, tuple)) else [v]


def _load_countries(world: World) -> None:
    for path in _yaml_files("countries"):
        add_countries(world, _load_yaml(path), path)


def add_countries(world: World, data: dict, path: Path) -> None:
    for tag, spec in data.items():
        if not isinstance(tag, str) or not tag.isupper() or not 2 <= len(tag) <= 4:
            raise WorldError(f"{path.name}: {tag!r} is not a country tag")
        if tag in world.countries:
            raise WorldError(
                f"{path.name}: {tag} already defined in "
                f"{world.countries[tag].source}")
        if not isinstance(spec, dict):
            raise WorldError(f"{path.name}: {tag}: expected a mapping")
        _reject_unknown(path, tag, spec, _COUNTRY_KEYS)
        lit = spec.get("literacy")
        if lit is not None and not (isinstance(lit, str) and lit in LITERACY) and not (type(lit) in (int, float) and 0 <= lit <= 1):
            raise WorldError(
                f"{path.name}: {tag}: literacy {lit!r} is not one of "
                f"{sorted(LITERACY)}")
        cap = spec.get("capital")
        world.countries[tag] = Country(
            tag=tag,
            source=path.name,
            color=spec.get("color"),
            country_type=spec.get("country_type", "recognized"),
            tier=spec.get("tier", "kingdom"),
            cultures=_as_list(spec.get("cultures")),
            religion=spec.get("religion"),
            tech_tier=spec.get("tech_tier"),
            literacy=lit,
            capital=_qualify_state(cap),
            market_capital=_qualify_state(spec.get("market_capital")),
            name=spec.get("name"),
            adjective=spec.get("adjective"),
            name_tr=spec.get("name_tr"),
            adjective_tr=spec.get("adjective_tr"),
            religion_map=spec.get("religion_map") or {},
            religion_split=spec.get("religion_split") or {},
            culture_religion_split=spec.get("culture_religion_split") or {},
            culture_map=spec.get("culture_map") or {},
            overlord=spec.get("overlord"),
            subject_type=spec.get("subject_type"),
            liberty_desire=spec.get("liberty_desire"),
            coat_of_arms=spec.get("coat_of_arms"),
            is_named_from_capital=spec.get("is_named_from_capital"),
            phase=str(spec["phase"]) if spec.get("phase") is not None else None,
            notes=spec.get("notes"),
            **{k: spec.get(k, {}) for k in ("population", "industry", "technology", "laws", "institutions", "interest_groups", "companies", "military")},
            history_mode=spec.get("history_mode", "inherit"),
        )



def _qualify_state(name):
    if name is None:
        return None
    return name if str(name).startswith("STATE_") else "STATE_" + str(name).upper()


def _load_states(world: World) -> None:
    for path in _yaml_files("states"):
        add_states(world, _load_yaml(path), path)


def add_states(world: World, data: dict, path: Path) -> None:
    for raw_name, spec in data.items():
        state = _qualify_state(raw_name)
        if state in world.states:
            raise WorldError(
                f"{path.name}: {state} already defined in "
                f"{world.states[state].source}")
        # Shorthand: `STATE_X: TAG` means the whole state goes to TAG.
        if isinstance(spec, str):
            spec = {"owner": spec}
        if not isinstance(spec, dict):
            raise WorldError(f"{path.name}: {state}: expected a mapping or a tag")
        _reject_unknown(path, state, spec, _STATE_KEYS)

        shares: list = []
        if "split" in spec:
            if "owner" in spec:
                raise WorldError(
                    f"{path.name}: {state}: use either 'owner' or 'split', "
                    f"not both")
            for i, part in enumerate(spec["split"] or []):
                if not isinstance(part, dict):
                    raise WorldError(
                        f"{path.name}: {state}: split[{i}] must be a mapping")
                _reject_unknown(path, f"{state}.split[{i}]", part, _SPLIT_KEYS)
                if "owner" not in part:
                    raise WorldError(
                        f"{path.name}: {state}: split[{i}] has no owner")
                rest = bool(part.get("rest"))
                provs = [str(p) for p in _as_list(part.get("provinces"))]
                if not rest and not provs:
                    raise WorldError(
                        f"{path.name}: {state}: split[{i}] needs 'provinces' "
                        f"or 'rest: true'")
                shares.append(Share(part["owner"], provs, rest,
                                    part.get("state_type", spec.get("state_type"))))
            if sum(1 for s in shares if s.rest) > 1:
                raise WorldError(
                    f"{path.name}: {state}: only one split part may be 'rest'")
        elif "owner" in spec:
            shares.append(Share(spec["owner"], [], True, spec.get("state_type")))
        elif not any(k in spec for k in ("population", "industry", "homelands", "claims", "state_type")):
            raise WorldError(f"{path.name}: {state}: needs 'owner' or 'split'")

        for key in ("pops", "buildings"):
            val = spec.get(key, "inherit")
            if val not in ("inherit", "drop"):
                raise WorldError(
                    f"{path.name}: {state}: {key} must be 'inherit' or 'drop', "
                    f"got {val!r}")

        world.states[state] = StateSpec(
            state=state,
            source=path.name,
            shares=shares,
            pops=spec.get("pops", "inherit"),
            buildings=spec.get("buildings", "inherit"),
            homelands=_as_list(spec.get("homelands")),
            claims=_as_list(spec.get("claims")),
            phase=str(spec["phase"]) if spec.get("phase") is not None else None,
            notes=spec.get("notes"),
            population=spec.get("population", {}), industry=spec.get("industry", {}),
            ownership_inherit="owner" not in spec and "split" not in spec,
            state_type=spec.get("state_type"),
            homelands_explicit="homelands" in spec, claims_explicit="claims" in spec,
        )



def _load_diplomacy(world: World) -> None:
    for path in _yaml_files("diplomacy"):
        data = _load_yaml(path)
        for kind, entries in data.items():
            for e in entries or []:
                if not isinstance(e, dict):
                    raise WorldError(f"{path.name}: {kind}: entries must be mappings")
                e = dict(e)
                e["kind"] = kind
                e["source"] = path.name
                world.diplomacy.append(e)


def _load_region_patches(world: World) -> None:
    for path in _yaml_files("state_regions"):
        for raw_name, spec in _load_yaml(path).items():
            state = _qualify_state(raw_name)
            if state in world.region_patches:
                raise WorldError(f"{path.name}: {state} patched twice")
            world.region_patches[state] = {"source": path.name, **(spec or {})}


def _load_aliases(world: World) -> None:
    f = WORLD / "_aliases.yml"
    if f.exists():
        world.aliases = _load_yaml(f)


def load_world() -> World:
    w = World()
    if not WORLD.is_dir():
        return w
    _load_countries(w)
    _load_states(w)
    _load_diplomacy(w)
    _load_region_patches(w)
    _load_aliases(w)
    document = WORLD / "scenario.yml"
    if document.exists():
        from . import scenario
        w = scenario.overlay(w, scenario.load(document))
    return w
