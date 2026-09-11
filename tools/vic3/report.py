"""`find` and `show`: look up state regions without guessing identifiers.

Never hand-write a STATE_* name or a province hex into world/*.yml. Resolve it
here first — vanilla contains several near-identical names (STATE_GEORGIA the
American state and STATE_GREATER_CAUCASUS the Georgian one, three separate
STATE_*_PUNJAB, and so on) and a typo silently produces an unowned region.
"""

from __future__ import annotations

import difflib
import unicodedata

from . import index as idx

# Free-form Turkish / historical names map onto vanilla state ids here.
# Populated as they come up; see world/_aliases.yml for the project-level list.
_BUILTIN_ALIASES = {
    "istanbul": "STATE_EASTERN_THRACE",
    "constantinople": "STATE_EASTERN_THRACE",
    "kostantiniyye": "STATE_EASTERN_THRACE",
    "isfahan": "STATE_ISFAHAN",
    "kahire": "STATE_LOWER_EGYPT",
    "cairo": "STATE_LOWER_EGYPT",
    "endulus": "STATE_LOWER_ANDALUSIA",
    "gırnata": "STATE_LOWER_ANDALUSIA",
    "musul": "STATE_MOSUL",
    "sam": "STATE_SYRIA",
    "gurcistan": "STATE_GREATER_CAUCASUS",
}


def _fold(s: str) -> str:
    """Case- and diacritic-insensitive key, so 'Sam' finds 'Şam'."""
    s = s.replace("ı", "i").replace("I", "i").replace("İ", "i")
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _aliases() -> dict:
    """Built-in aliases plus anything the project added to world/_aliases.yml."""
    out = {_fold(k): v for k, v in _BUILTIN_ALIASES.items()}
    try:
        import yaml
        from .paths import WORLD
        f = WORLD / "_aliases.yml"
        if f.exists():
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            for k, v in data.items():
                out[_fold(str(k))] = v
    except Exception:
        pass
    return out


def _candidates(index: dict) -> dict:
    """Folded search term -> state id. Both the bare id and the English name
    are indexed separately; matching against them concatenated makes every
    ratio too low for difflib to be useful."""
    loc = index["loc"]
    pool: dict = {}
    for name in index["states"]:
        pool.setdefault(_fold(name.removeprefix("STATE_")), name)
        label = loc.get(name)
        if label:
            pool.setdefault(_fold(label), name)
    return pool


def find(query: str, limit: int = 15) -> int:
    index = idx.load()
    states = index["states"]
    loc = index["loc"]
    q = _fold(query)

    alias = _aliases().get(q)
    if alias and alias in states:
        print(f"alias: {query!r} -> {alias}")
        _print_row(alias, states[alias], loc, index)
        return 0

    # A province hex resolves to its state directly.
    if q.startswith("x") and len(q) == 7:
        hexid = "x" + query.lstrip("xX").upper()
        state = index["province_state"].get(hexid)
        if state:
            print(f"province {hexid} belongs to {state}")
            _print_row(state, states[state], loc, index)
            return 0
        print(f"province {hexid} is not in any state region")
        return 1

    exact = [n for n in states if _fold(n) == q or _fold(loc.get(n, "")) == q]
    subs = [n for n in states
            if n not in exact and (q in _fold(n) or q in _fold(loc.get(n, "")))]
    hits = exact + subs

    if not hits:
        pool = _candidates(index)
        close = difflib.get_close_matches(q, list(pool), n=limit, cutoff=0.6)
        if close:
            print(f"no match for {query!r}; did you mean:")
            seen, hits = set(), []
            for c in close:
                if pool[c] not in seen:
                    seen.add(pool[c])
                    hits.append(pool[c])
        else:
            print(f"no state region matches {query!r}")
            return 1

    for name in hits[:limit]:
        _print_row(name, states[name], loc, index)
    if len(hits) > limit:
        print(f"... and {len(hits) - limit} more")
    return 0


def _print_row(name: str, st: dict, loc: dict, index: dict) -> None:
    owners = index["state_history"].get(name, {}).get("owners", [])
    who = ", ".join(o["country"] for o in owners) or ("sea" if st["is_sea"] else "-")
    label = loc.get(name, "")
    kind = "sea " if st["is_sea"] else "land"
    print(f"  {name:<34} {kind}  id={st['id']:<4} prov={len(st['provinces']):<4} "
          f"owner={who:<16} {label}")


def show(state: str) -> int:
    index = idx.load()
    states = index["states"]
    name = state if state.startswith("STATE_") else "STATE_" + state.upper()
    if name not in states:
        print(f"unknown state {state!r}; try: tgc.py find {state}")
        return find(state)

    st = states[name]
    loc = index["loc"]
    hist = index["state_history"].get(name, {})
    pops = index["pops"].get(name, {}).get("by_country", {})
    blds = index["buildings"].get(name, {}).get("by_country", {})

    print(f"{name}   {loc.get(name, '')}")
    print(f"  file          {st['file']}   id={st['id']}"
          f"   {'SEA' if st['is_sea'] else 'land'}")
    print(f"  provinces     {len(st['provinces'])} "
          f"({len(st['impassable'])} impassable, {len(st['prime_land'])} prime)")
    if st["traits"]:
        print(f"  traits        {', '.join(st['traits'])}")
    print(f"  arable_land   {st['arable_land']}   "
          f"{', '.join(st['arable_resources'])}")
    if st["capped_resources"]:
        caps = ", ".join(f"{k}={v}" for k, v in st["capped_resources"].items())
        print(f"  capped        {caps}")
    for r in st["resources"]:
        amt = r["discovered_amount"] or r["undiscovered_amount"]
        print(f"  resource      {r['type']} ({amt})")
    print(f"  subsistence   {st['subsistence_building']}")
    hubs = {k: st[k] for k in ("city", "port", "farm", "mine", "wood") if st[k]}
    print("  hubs          " + ", ".join(f"{k}={v}" for k, v in hubs.items()))

    print(f"\n  vanilla history ({hist.get('file', '-')})")
    for o in hist.get("owners", []):
        extra = f"  state_type={o['state_type']}" if o["state_type"] else ""
        print(f"    owner {o['country']:<5} {len(o['provinces'])} provinces{extra}")
    if hist.get("homelands"):
        print(f"    homelands  {', '.join(hist['homelands'])}")
    if hist.get("claims"):
        print(f"    claims     {', '.join(hist['claims'])}")

    for tag, lst in pops.items():
        total = sum(p["size"] for p in lst)
        print(f"\n  pops [{tag}]  {total:,} in {len(lst)} entries")
        for p in sorted(lst, key=lambda x: -x["size"])[:12]:
            bits = [p["culture"] or "?"]
            if p["religion"]:
                bits.append(p["religion"])
            if p["pop_type"]:
                bits.append(p["pop_type"])
            print(f"    {p['size']:>9,}  {' / '.join(bits)}")
        if len(lst) > 12:
            print(f"    ... {len(lst) - 12} more")

    for tag, b in blds.items():
        print(f"\n  buildings [{tag}]  {len(b['types'])}")
        for t in b["types"]:
            print(f"    {t}")

    print("\n  provinces")
    prov = st["provinces"]
    for i in range(0, len(prov), 10):
        print("    " + " ".join(prov[i:i + 10]))
    return 0
