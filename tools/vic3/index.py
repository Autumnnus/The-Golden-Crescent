"""Build build/index.json: everything the toolchain needs to know about vanilla.

Every later command reads this cache instead of re-parsing the install, so the
index has to be complete enough that `check` can validate an identifier without
touching the game directory again.

Regenerate after a Victoria 3 patch:  python tools/tgc.py index
"""

from __future__ import annotations

import json
import hashlib
import re
import time
from pathlib import Path

from . import pdx
from .paths import BUILD, MOD, VANILLA, vanilla, assert_read_only

INDEX_PATH = BUILD / "index.json"
_INDEX_CACHE = None

# ---------------------------------------------------------------------------
# small helpers


def _files(*parts, pattern: str = "*.txt") -> list[Path]:
    d = vanilla(*parts)
    return sorted(d.glob(pattern)) if d.is_dir() else []


def _top_keys(*parts, pattern: str = "*.txt") -> dict:
    """Top-level `key = { ... }` blocks across a directory, first file wins."""
    out: dict = {}
    for f in _files(*parts, pattern=pattern):
        for key, val in pdx.parse_file(f).pairs():
            if key not in out:
                out[key] = {"file": f.name, "node": val}
    return out


def _strip_prefix(s: str, prefix: str) -> str:
    return s[len(prefix):] if s.startswith(prefix) else s


# ---------------------------------------------------------------------------
# map_data/state_regions


def _index_states() -> tuple[dict, dict, list]:
    states: dict = {}
    province_state: dict = {}
    duplicates: list = []
    for f in _files("map_data", "state_regions"):
        is_sea = f.name.startswith("99_")
        for name, node in pdx.parse_file(f).pairs():
            if not isinstance(node, pdx.Node):
                continue
            provinces = node.get_list("provinces")
            resources = []
            for res in node.getall("resource"):
                if isinstance(res, pdx.Node):
                    resources.append({
                        "type": res.get_str("type"),
                        "discovered_amount": res.get_int("discovered_amount"),
                        "undiscovered_amount": res.get_int("undiscovered_amount"),
                    })
            capped = {}
            cap_node = node.get_node("capped_resources")
            if cap_node:
                for k, v in cap_node.pairs():
                    if isinstance(v, str):
                        capped[k] = int(float(v))
            states[name] = {
                "name": name,
                "id": node.get_int("id"),
                "file": f.name,
                "region": _strip_prefix(f.stem, ""),
                "is_sea": is_sea,
                "provinces": provinces,
                "impassable": node.get_list("impassable"),
                "prime_land": node.get_list("prime_land"),
                "traits": node.get_list("traits"),
                "subsistence_building": node.get_str("subsistence_building"),
                "city": node.get_str("city"),
                "port": node.get_str("port"),
                "farm": node.get_str("farm"),
                "mine": node.get_str("mine"),
                "wood": node.get_str("wood"),
                "arable_land": node.get_int("arable_land"),
                "arable_resources": node.get_list("arable_resources"),
                "capped_resources": capped,
                "resources": resources,
                "naval_exit_id": node.get_int("naval_exit_id"),
            }
            for p in provinces:
                if p in province_state:
                    duplicates.append({"province": p,
                                       "states": [province_state[p], name]})
                else:
                    province_state[p] = name
    return states, province_state, duplicates


# ---------------------------------------------------------------------------
# common/history/states


def _index_state_history() -> dict:
    hist: dict = {}
    for f in _files("common", "history", "states"):
        root = pdx.parse_file(f)
        for _, states_node in root.pairs():          # STATES = { ... }
            if not isinstance(states_node, pdx.Node):
                continue
            for skey, snode in states_node.pairs():   # s:STATE_X = { ... }
                if not isinstance(snode, pdx.Node):
                    continue
                state = _strip_prefix(skey, "s:")
                rec = hist.setdefault(state, {"file": f.name, "owners": [],
                                              "homelands": [], "claims": []})
                for cs in snode.getall("create_state"):
                    if not isinstance(cs, pdx.Node):
                        continue
                    rec["owners"].append({
                        "country": _strip_prefix(cs.get_str("country", ""), "c:"),
                        "provinces": cs.get_list("owned_provinces"),
                        "state_type": cs.get_str("state_type"),
                    })
                for h in snode.getall("add_homeland"):
                    if isinstance(h, str):
                        rec["homelands"].append(_strip_prefix(h, "cu:"))
                for c in snode.getall("add_claim"):
                    if isinstance(c, str):
                        rec["claims"].append(_strip_prefix(c, "c:"))
    return hist


# ---------------------------------------------------------------------------
# common/history/pops


def _pop_record(node: pdx.Node) -> dict:
    rec = {
        "culture": node.get_str("culture"),
        "religion": node.get_str("religion"),
        "size": node.get_int("size", 0),
        "pop_type": node.get_str("pop_type"),
    }
    split = node.get_node("split_religion")
    if split:
        # split_religion = { culture = { religion = fraction ... } }
        out = {}
        for cul, sub in split.pairs():
            if isinstance(sub, pdx.Node):
                out[cul] = {k: float(v) for k, v in sub.pairs()
                            if isinstance(v, str)}
        rec["split_religion"] = out
    return rec


def _index_pops() -> dict:
    pops: dict = {}
    for f in _files("common", "history", "pops"):
        if f.name.startswith("100_"):          # 100_pops_example.txt is a template
            continue
        root = pdx.parse_file(f)
        for _, pops_node in root.pairs():                # POPS = { ... }
            if not isinstance(pops_node, pdx.Node):
                continue
            for skey, snode in pops_node.pairs():        # s:STATE_X = { ... }
                if not isinstance(snode, pdx.Node):
                    continue
                state = _strip_prefix(skey, "s:")
                bucket = pops.setdefault(state, {"file": f.name, "by_country": {}})
                for rkey, rnode in snode.pairs():        # region_state:TAG = { ... }
                    if not isinstance(rnode, pdx.Node):
                        continue
                    tag = _strip_prefix(rkey, "region_state:")
                    lst = bucket["by_country"].setdefault(tag, [])
                    for cp in rnode.getall("create_pop"):
                        if isinstance(cp, pdx.Node):
                            lst.append(_pop_record(cp))
    return pops


# ---------------------------------------------------------------------------
# common/history/buildings
#
# Buildings are kept as serialized script rather than a parsed structure: when
# a state changes hands we re-emit vanilla's blocks verbatim under the new
# owner, rewriting only the c:TAG ownership references. Round-tripping the text
# is safer than modelling every ownership shape create_building accepts.


def _index_buildings() -> dict:
    out: dict = {}
    for f in _files("common", "history", "buildings"):
        root = pdx.parse_file(f)
        for _, b_node in root.pairs():                   # BUILDINGS = { ... }
            if not isinstance(b_node, pdx.Node):
                continue
            for skey, snode in b_node.pairs():           # s:STATE_X = { ... }
                if not isinstance(snode, pdx.Node):
                    continue
                state = _strip_prefix(skey, "s:")
                bucket = out.setdefault(state, {"file": f.name, "by_country": {}})
                for rkey, rnode in snode.pairs():        # region_state:TAG = { ... }
                    if not isinstance(rnode, pdx.Node):
                        continue
                    tag = _strip_prefix(rkey, "region_state:")
                    types = [n.get_str("building")
                             for n in rnode.getall("create_building")
                             if isinstance(n, pdx.Node)]
                    bucket["by_country"][tag] = {
                        "script": pdx.dumps(rnode, indent=0),
                        "types": [t for t in types if t],
                    }
    return out


# ---------------------------------------------------------------------------
# common/country_definitions


def _colour(val) -> list | None:
    if isinstance(val, pdx.TypedBlock):
        return [val.type] + val.node.values()
    if isinstance(val, pdx.Node):
        return val.values()
    return None


def _index_countries() -> dict:
    out: dict = {}
    for f in _files("common", "country_definitions"):
        for tag, node in pdx.parse_file(f).pairs():
            if not isinstance(node, pdx.Node):
                continue
            if tag in out:                # vanilla itself never duplicates here
                continue
            out[tag] = {
                "tag": tag,
                "file": f.name,
                "color": _colour(node.get("color")),
                "country_type": node.get_str("country_type"),
                "tier": node.get_str("tier"),
                "cultures": node.get_list("cultures"),
                "religion": node.get_str("religion"),
                "capital": node.get_str("capital"),
                "is_named_from_capital": node.get_str("is_named_from_capital"),
                "dynamic_country_definition": node.get_str("dynamic_country_definition"),
                "valid_as_home_country_for_separatists":
                    node.get_str("valid_as_home_country_for_separatists"),
            }
    return out


# ---------------------------------------------------------------------------
# common/history/countries  (capital moves hide here, see YENIDEN_KURULUM 2.5)

_CAP_RE = re.compile(r"\b(set_capital|set_market_capital)\s*=\s*([A-Za-z0-9_:]+)")


def _index_country_history() -> dict:
    out: dict = {}
    for f in _files("common", "history", "countries"):
        text = pdx.read_text(f)
        rec = {"file": f.name, "set_capital": None, "set_market_capital": None,
               "tags": []}
        for m in _CAP_RE.finditer(text):
            rec[m.group(1)] = _strip_prefix(m.group(2), "s:")
        root = pdx.parse_file(f)
        for _, c_node in root.pairs():                   # COUNTRIES = { ... }
            if isinstance(c_node, pdx.Node):
                rec["tags"] += [_strip_prefix(k, "c:") for k in c_node.keys()]
        out[f.name] = rec
    return out


# ---------------------------------------------------------------------------
# common/history/diplomacy


def _index_diplomacy() -> dict:
    out: dict = {}
    for f in _files("common", "history", "diplomacy"):
        entries = []
        root = pdx.parse_file(f)
        for kind, blk in root.pairs():     # DIPLOMACY / DIPLOMATIC_PACTS / ...
            if not isinstance(blk, pdx.Node):
                continue
            for ckey, cnode in blk.pairs():
                if not isinstance(cnode, pdx.Node):
                    continue
                subject = _strip_prefix(ckey, "c:")
                for eff, enode in cnode.pairs():
                    targets = []
                    if isinstance(enode, pdx.Node):
                        for k, v in enode.pairs():
                            if isinstance(v, str) and v.startswith("c:"):
                                targets.append(_strip_prefix(v, "c:"))
                    elif isinstance(enode, str) and enode.startswith("c:"):
                        targets.append(_strip_prefix(enode, "c:"))
                    entries.append({"kind": kind, "actor": subject,
                                    "effect": eff, "targets": targets})
        out[f.name] = entries
    return out


# ---------------------------------------------------------------------------
# common/history/military_formations


def _index_formations() -> dict:
    out: dict = {}
    for f in _files("common", "history", "military_formations"):
        text = pdx.read_text(f)
        out[f.name] = {
            "tags": sorted(set(re.findall(r"c:([A-Z0-9]{2,4})\b", text))),
            "states": sorted(set(re.findall(r"\b(STATE_[A-Z0-9_]+)", text))),
        }
    return out


# ---------------------------------------------------------------------------
# definition tables used by `check`


def _index_defs(countries: dict) -> dict:
    cultures = {}
    for f in _files("common", "cultures"):
        for name, node in pdx.parse_file(f).pairs():
            if isinstance(node, pdx.Node):
                cultures[name] = {
                    "religion": node.get_str("religion"),
                    "heritage": node.get_str("heritage"),
                    "language": node.get_str("language"),
                    "traits": node.get_list("traits"),
                }

    religions = {}
    for f in _files("common", "religions"):
        for name, node in pdx.parse_file(f).pairs():
            if isinstance(node, pdx.Node):
                religions[name] = {
                    "heritage": node.get_str("heritage"),
                    "taboos": node.get_list("taboos"),
                    "icon": node.get_str("icon"),
                }

    subject_types = {}
    for f in _files("common", "subject_types"):
        for name, node in pdx.parse_file(f).pairs():
            if isinstance(node, pdx.Node):
                subject_types[_strip_prefix(name, "subject_type_")] = {
                    "key": name,
                    "valid_overlord_country_types":
                        node.get_list("valid_overlord_country_types"),
                    "valid_subject_country_types":
                        node.get_list("valid_subject_country_types"),
                    "valid_overlord_ranks": node.get_list("valid_overlord_ranks"),
                    "valid_subject_ranks": node.get_list("valid_subject_ranks"),
                    "overlord_must_be_higher_rank":
                        node.get_str("overlord_must_be_higher_rank"),
                    "overlord_must_be_same_country_type":
                        node.get_str("overlord_must_be_same_country_type"),
                }

    technologies = {}
    for f in _files("common", "technology", "technologies"):
        for name, node in pdx.parse_file(f).pairs():
            if isinstance(node, pdx.Node):
                technologies[name] = {
                    "era": node.get_str("era"),
                    "category": node.get_str("category"),
                    "unlocking_technologies":
                        node.get_list("unlocking_technologies"),
                }

    buildings = {}
    for f in _files("common", "buildings"):
        for name, node in pdx.parse_file(f).pairs():
            if isinstance(node, pdx.Node):
                buildings[name] = {
                    "group": node.get_str("building_group"),
                    "production_method_groups":
                        node.get_list("production_method_groups"),
                    "required_construction": node.get_int("required_construction"),
                }

    def _names(*parts) -> list:
        return sorted(_top_keys(*parts).keys())

    return {
        "cultures": cultures,
        "religions": religions,
        "subject_types": subject_types,
        "technologies": technologies,
        "buildings": buildings,
        "production_methods": _names("common", "production_methods"),
        "production_method_groups": _names("common", "production_method_groups"),
        "pop_types": _names("common", "pop_types"),
        "goods": _names("common", "goods"),
        "state_traits": _names("common", "state_traits"),
        "country_types": _names("common", "country_types"),
        "country_ranks": _names("common", "country_ranks"),
        "country_tiers": sorted({c["tier"] for c in countries.values()
                                 if c["tier"]}),
        "discrimination_traits": _names("common", "discrimination_traits"),
        "building_groups": _names("common", "building_groups"),
        "institutions": _names("common", "institutions"),
        "laws": _names("common", "laws"),
        "heritages": sorted({c["heritage"] for c in cultures.values()
                             if c["heritage"]}),
    }


# ---------------------------------------------------------------------------
# localization

_LOC_RE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*\d*\s*"(.*)"\s*$')
_LOC_KEEP = re.compile(r"^(STATE_[A-Z0-9_]+|[A-Z]{3}|[A-Z]{3}_ADJ|dyn_c_[a-z0-9_]+)$")


def _index_loc(defs: dict) -> dict:
    """Only the keys the toolchain reports on; the full corpus is far larger."""
    keep_extra = set(defs["cultures"]) | set(defs["religions"])
    out: dict = {}
    root = vanilla("localization", "english")
    if not root.is_dir():
        return out
    for f in sorted(root.rglob("*_l_english.yml")):
        for line in pdx.read_text(f).splitlines():
            m = _LOC_RE.match(line)
            if not m:
                continue
            key, val = m.group(1), m.group(2)
            if key in out:
                continue
            if _LOC_KEEP.match(key) or key in keep_extra:
                out[key] = val
    return out


# ---------------------------------------------------------------------------
# entry point


def source_signature():
    """Detect a different install, game patch, or edited vanilla reference files."""
    rows = []
    for sub in ("map_data/state_regions", "common", "localization/english"):
        for path in sorted((VANILLA / sub).rglob("*")):
            if path.is_file() and path.suffix in (".txt", ".yml"):
                stat = path.stat()
                rows.append((path.relative_to(VANILLA).as_posix(), stat.st_size, stat.st_mtime_ns))
    return {"version": 1, "root": str(VANILLA.resolve()),
            "files": hashlib.sha256(json.dumps(rows).encode()).hexdigest()}


def build_index(verbose: bool = True) -> dict:
    t0 = time.time()

    def step(msg):
        if verbose:
            print(f"  {msg}", flush=True)

    step("map_data/state_regions ...")
    states, province_state, duplicates = _index_states()
    step("common/history/states ...")
    state_history = _index_state_history()
    step("common/history/pops ...")
    pops = _index_pops()
    step("common/history/buildings ...")
    buildings = _index_buildings()
    step("common/country_definitions ...")
    countries = _index_countries()
    step("common/history/countries ...")
    country_history = _index_country_history()
    step("common/history/diplomacy ...")
    diplomacy = _index_diplomacy()
    step("common/history/military_formations ...")
    formations = _index_formations()
    step("definition tables ...")
    defs = _index_defs(countries)
    step("localization ...")
    loc = _index_loc(defs)

    land = [s for s in states.values() if not s["is_sea"]]
    index = {
        "meta": {
            "generated_by": "tools/tgc.py index",
            "source_signature": source_signature(),
            "vanilla_root": str(VANILLA),
            "mod_root": str(MOD),
            "state_count": len(states),
            "land_state_count": len(land),
            "province_count": len(province_state),
            "country_count": len(countries),
            "duplicate_provinces": duplicates,
            "seconds": round(time.time() - t0, 1),
        },
        "states": states,
        "province_state": province_state,
        "state_history": state_history,
        "pops": pops,
        "buildings": buildings,
        "countries": countries,
        "country_history": country_history,
        "diplomacy": diplomacy,
        "military_formations": formations,
        "defs": defs,
        "loc": loc,
    }
    BUILD.mkdir(parents=True, exist_ok=True)
    assert_read_only(INDEX_PATH)
    INDEX_PATH.write_text(json.dumps(index), encoding="utf-8")
    if verbose:
        m = index["meta"]
        print(f"\nindex written: {INDEX_PATH}")
        print(f"  {m['state_count']} states ({m['land_state_count']} land), "
              f"{m['province_count']} provinces, {m['country_count']} countries")
        print(f"  {len(defs['cultures'])} cultures, {len(defs['religions'])} religions, "
              f"{len(defs['buildings'])} building types, "
              f"{len(defs['technologies'])} technologies")
        if duplicates:
            print(f"  note: {len(duplicates)} province(s) claimed by two state "
                  f"regions in vanilla itself")
        print(f"  {m['seconds']}s")
    return index


def load(refresh: bool = False) -> dict:
    """Load the cached index, building it on first use."""
    global _INDEX_CACHE
    if _INDEX_CACHE is not None and not refresh:
        return _INDEX_CACHE
    if refresh or not INDEX_PATH.exists():
        _INDEX_CACHE = build_index(verbose=refresh)
    else:
        try:
            cached = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            cached = {}
        if cached.get("meta", {}).get("source_signature") != source_signature():
            _INDEX_CACHE = build_index(verbose=False)
        else:
            _INDEX_CACHE = cached
    return _INDEX_CACHE
