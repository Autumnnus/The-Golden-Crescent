"""Validated, in-memory scenario overlays. Never writes to world/ or game files."""
from __future__ import annotations

import copy
import re
from dataclasses import asdict
from pathlib import Path

import yaml

from .world import WorldError, add_countries, add_states


class UniqueLoader(yaml.SafeLoader):
    pass


def _mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, (str, int, float, bool)):
            raise WorldError("scenario: mapping keys must be scalar")
        if key in result:
            raise WorldError(f"scenario: duplicate key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def load(path):
    path = Path(path)
    try:
        data = yaml.load(path.read_text(encoding="utf-8-sig"), Loader=UniqueLoader)
    except (yaml.YAMLError, OSError) as exc:
        raise WorldError(f"{path}: {exc}") from None
    validate_document(data)
    return data


def validate_document(data):
    if not isinstance(data, dict):
        raise WorldError("scenario: expected a JSON/YAML object")
    extra = set(data) - {"version", "title", "description", "countries", "states", "diplomacy", "subject_types"}
    if extra:
        raise WorldError(f"scenario: unknown fields {sorted(extra, key=str)}")
    if type(data.get("version")) is not int or data["version"] not in (1, 2):
        raise WorldError("scenario: version must be 1 or 2")
    for key in ("title", "description"):
        if key in data and not isinstance(data[key], str):
            raise WorldError(f"scenario: {key} must be text")
    for key in ("countries", "states"):
        if not isinstance(data.get(key, {}), dict):
            raise WorldError(f"scenario: {key} must be an object")
        if any(not isinstance(k, str) for k in data.get(key, {})):
            raise WorldError(f"scenario: {key} keys must be strings")
    for name, spec in data.get("states", {}).items():
        if not isinstance(spec, (str, dict)):
            raise WorldError(f"{name}: state must be a tag or object")
        if isinstance(spec, dict) and "split" in spec:
            if not isinstance(spec["split"], list):
                raise WorldError(f"{name}: split must be a list")
            for part in spec["split"]:
                if not isinstance(part, dict):
                    raise WorldError(f"{name}: each split share must be an object")
                if "rest" in part and type(part["rest"]) is not bool:
                    raise WorldError(f"{name}: rest must be true or false")
                if "provinces" in part and not isinstance(part["provinces"], list):
                    raise WorldError(f"{name}: provinces must be a list of hex strings")


def overlay(base, data):
    """Country fields merge; a state ownership plan replaces the previous plan."""
    validate_document(data)
    result = copy.deepcopy(base)
    result.version = max(base.version, data["version"])
    for key, attr in (("diplomacy", "diplomacy_policy"), ("subject_types", "subject_types")):
        if key in data:
            if data["version"] < 2 or not isinstance(data[key], dict):
                raise WorldError(f"{key}: requires a version 2 object")
            setattr(result, attr, copy.deepcopy(data[key]))
    country_data = {}
    for tag, spec in data.get("countries", {}).items():
        if not isinstance(spec, dict):
            raise WorldError(f"scenario: {tag}: expected a country object")
        old = result.countries.pop(tag, None)
        merged = asdict(old) if old else {}
        if not old and data["version"] >= 2:
            from . import index
            vanilla = index.load()["countries"].get(tag, {})
            merged.update({k: vanilla[k] for k in ("country_type", "tier") if k in vanilla})
        for key in ("tag", "source"):
            merged.pop(key, None)
        country_data[tag] = {**merged, **spec}
    try:
        add_countries(result, country_data, Path("scenario.countries"))
    except (TypeError, AttributeError) as exc:
        raise WorldError(f"scenario: malformed country specification: {exc}") from None
    # Parse into a temporary World to keep aliases of the same id from overwriting.
    from .world import World
    patch = World()
    try:
        add_states(patch, data.get("states", {}), Path("scenario.states"))
    except (TypeError, AttributeError) as exc:
        raise WorldError(f"scenario: malformed state specification: {exc}") from None
    result.states.update(patch.states)
    return result


def validate_world(world, index):
    """Fail on misleading ownership rather than silently painting invalid land."""
    known_tags = set(index["countries"]) | set(world.countries)
    for tag, country in world.countries.items():
        if not isinstance(tag, str) or not re.fullmatch(r"[A-Z0-9]{2,4}", tag):
            raise WorldError(f"Invalid country tag: {tag!r}")
        if country.color is not None:
            color = country.color
            if (not isinstance(color, list) or len(color) != 3
                    or any(type(v) not in (int, float) or not 0 <= v <= 255 for v in color)):
                raise WorldError(f"{tag}: color must contain three numbers in 0..255")
        for key in ("name", "name_tr", "religion", "phase"):
            value = getattr(country, key)
            if value is not None and not isinstance(value, str):
                raise WorldError(f"{tag}: {key} must be text")
    for name, spec in world.states.items():
        state = index["states"].get(name)
        if not state or state["is_sea"]:
            raise WorldError(f"{name}: unknown or sea state; resolve it with tgc.py find")
        all_provinces = set(state["provinces"])
        required = all_provinces - set(state["impassable"])
        if not required:
            required = all_provinces
        seen = set()
        if not spec.shares and not spec.ownership_inherit:
            raise WorldError(f"{name}: empty ownership plan")
        for value in [spec.state_type] + [s.state_type for s in spec.shares]:
            if value is not None and value not in ('incorporated', 'unincorporated'):
                raise WorldError(f'{name}: state_type must be incorporated or unincorporated')
        for share in spec.shares:
            if not isinstance(share.owner, str) or share.owner not in known_tags:
                raise WorldError(f"{name}: unknown owner {share.owner!r}; define countries first")
            if share.rest and share.provinces:
                raise WorldError(f"{name}: rest and provinces cannot be used together")
            for prov in share.provinces:
                if prov not in all_provinces:
                    raise WorldError(f"{name}: province {prov} is not in this state")
                if prov in seen:
                    raise WorldError(f"{name}: province {prov} is assigned twice")
                seen.add(prov)
        if not spec.ownership_inherit and not any(s.rest for s in spec.shares) and required - seen:
            raise WorldError(f"{name}: {len(required - seen)} provinces have no owner; add rest: true")
    for name, patch in world.region_patches.items():
        if set(patch) & {"provinces", "impassable"}:
            raise WorldError(f"{name}: geometry patches are not supported by the atlas; "
                             "the vanilla raster would give misleading boundaries")
