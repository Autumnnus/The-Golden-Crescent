"""Generate game files from world/*.yml.

Two engine rules shape everything here (YENIDEN_KURULUM.md 2.1-2.3):

* `common/history/{states,pops,buildings}` are *executed scripts*, not keyed
  databases. A differently-named file does not override vanilla, it runs in
  addition to it, so the same state gets created twice. The only way to silence
  vanilla is `replace_paths` in .metadata/metadata.json — which deletes the
  vanilla content outright. Therefore, once we emit any of those three, we must
  emit the *entire world*, including every state we did not change.

* A directory listed in `replace_paths` that the mod then leaves empty wipes
  that content from the game (this is how a whole world lost its armies and its
  rulers). So `replace_paths` is not hand-maintained: `build` rewrites it from
  the set of directories it actually filled, every run.

* `decentralized` countries cannot own buildings. Vanilla contains exactly zero
  buildings for them; writing one crashes the game on load with an access
  violation and no log line. Buildings inherited into a decentralized owner are
  dropped here, and `check` fails if any survive.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict

from . import index as idx
from . import pdx
from .paths import MOD, write_text
from .world import Country, StateSpec, World, load_world

HEADER = (
    "# OTOMATIK URETILDI - ELLE DUZENLEME\n"
    "# Kaynak: world/{src}\n"
    "# Ureten: python tools/tgc.py build\n"
    "# Bu dosyayi degistirmek istiyorsan world/ altindaki YAML'i degistir ve\n"
    "# yeniden uret; build kendi ciktisini her calismada siler.\n"
)

# Everything build owns, as globs relative to the mod root. All of it is deleted
# before a run so a renamed source file cannot leave an orphan behind. The
# localization pattern spans every language directory: dropping a name_tr used
# to leave a stale Turkish file that nothing regenerated.
OWNED = [
    "common/history/states/tgc_*.txt",
    "common/history/pops/tgc_*.txt",
    "common/history/buildings/tgc_*.txt",
    "common/country_definitions/tgc_*.txt",
    "localization/*/tgc_generated_*.yml",
]

# Directories that must be declared in replace_paths when we emit into them,
# because a differently-named file would run *alongside* vanilla, not over it.
NEEDS_REPLACE_PATH = {
    "common/history/states",
    "common/history/pops",
    "common/history/buildings",
}


class BuildError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# resolved world: world/*.yml merged onto vanilla


class Resolved:
    """The full 1836 world after world/*.yml is applied to vanilla."""

    def __init__(self, world: World, index: dict):
        self.world = world
        self.index = index
        self.countries: dict = {}       # tag -> merged definition dict
        self.state_owners: dict = {}    # STATE_* -> [(tag, [provinces], state_type)]
        self.state_pops: dict = {}      # STATE_* -> {tag: [pop dicts]}
        self.state_buildings: dict = {}  # STATE_* -> {tag: script text}
        self.state_homelands: dict = {}
        self.state_claims: dict = {}
        self.notes: list = []
        self._resolve()

    # -- countries --------------------------------------------------------
    def _resolve(self) -> None:
        """Ownership first, contents second.

        Pops and buildings need to know which tags end up with land — a
        building block inherited from a country that is now landless has to be
        re-pointed at its new owner. That set is only complete once every state
        has been assigned, so contents cannot be resolved in the same pass.
        """
        self._resolve_countries()
        plan = self._resolve_ownership()
        self._landed = {tag for owners in self.state_owners.values()
                        for tag, _, _ in owners}
        self._resolve_contents(plan)

    def _resolve_countries(self) -> None:
        for tag, van in self.index["countries"].items():
            self.countries[tag] = dict(van, source="vanilla", is_new=False)
        for tag, c in self.world.countries.items():
            base = self.countries.get(tag, {})
            self.countries[tag] = {
                "tag": tag,
                "file": base.get("file"),
                "color": c.color or base.get("color"),
                "country_type": c.country_type,
                "tier": c.tier,
                "cultures": c.cultures or base.get("cultures") or [],
                "religion": c.religion or base.get("religion"),
                "capital": c.capital or base.get("capital"),
                "is_named_from_capital": (c.is_named_from_capital
                                          or base.get("is_named_from_capital")),
                "source": "world",
                "is_new": tag not in self.index["countries"],
                "spec": c,
            }

    def country_type(self, tag: str) -> str:
        return (self.countries.get(tag) or {}).get("country_type") or "recognized"

    # -- states: pass 1, ownership ----------------------------------------
    def _resolve_ownership(self) -> dict:
        """Assign every land state, returning the per-state plan for pass 2."""
        states = self.index["states"]
        history = self.index["state_history"]
        plan: dict = {}
        for name, st in states.items():
            if st["is_sea"]:
                continue
            spec = self.world.states.get(name)
            van_owners = history.get(name, {}).get("owners", [])
            owners = (self._vanilla_owners(van_owners) if spec is None
                      else self._spec_owners(name, st, spec))
            if not owners:
                continue
            self.state_owners[name] = owners
            hist = history.get(name, {})
            if spec is None:
                self.state_homelands[name] = list(hist.get("homelands", []))
                self.state_claims[name] = list(hist.get("claims", []))
            else:
                self.state_homelands[name] = (spec.homelands
                                              or list(hist.get("homelands", [])))
                self.state_claims[name] = spec.claims or list(hist.get("claims", []))
            plan[name] = (spec, van_owners)
        return plan

    @staticmethod
    def _vanilla_owners(van_owners: list) -> list:
        return [(o["country"], o["provinces"], o["state_type"])
                for o in van_owners if o["country"]]

    # -- states: pass 2, pops and buildings --------------------------------
    def _resolve_contents(self, plan: dict) -> None:
        for name, (spec, van_owners) in plan.items():
            owners = self.state_owners[name]
            if spec is None:
                # Unlisted state: vanilla pops and buildings verbatim. This
                # deliberately skips religion/culture conversion — a state must
                # be listed in world/ to be converted (2.8).
                self._keep_vanilla(name, owners)
                continue
            self.state_pops[name] = ({} if spec.pops == "drop"
                                     else self._convert_pops(name, owners, van_owners))
            self.state_buildings[name] = ({} if spec.buildings == "drop"
                                          else self._reassign_buildings(
                                              name, owners, van_owners))

    def _keep_vanilla(self, name: str, owners: list) -> None:
        tags = {t for t, _, _ in owners}
        van_pops = self.index["pops"].get(name, {}).get("by_country", {})
        van_blds = self.index["buildings"].get(name, {}).get("by_country", {})
        self.state_pops[name] = {tag: list(lst) for tag, lst in van_pops.items()
                                 if tag in tags}
        kept: dict = {}
        for tag, b in van_blds.items():
            if tag not in tags:
                continue
            if self.country_type(tag) == "decentralized":
                # Vanilla ships empty `region_state:TAG = {}` blocks for its own
                # decentralized countries; dropping those is not worth a note.
                if b["types"]:
                    self.notes.append(
                        f"{name}: dropped {len(b['types'])} vanilla building(s) "
                        f"because world/ made {tag} decentralized")
                continue
            kept[tag] = b["script"]
        self.state_buildings[name] = kept

    def _spec_owners(self, name: str, st: dict, spec: StateSpec) -> list:
        all_prov = [p for p in st["provinces"] if p not in set(st["impassable"])]
        if not all_prov:                      # fully impassable regions exist
            all_prov = list(st["provinces"])

        named: dict = {}
        for share in spec.shares:
            if share.rest:
                continue
            for p in share.provinces:
                if p not in st["provinces"]:
                    raise BuildError(
                        f"{spec.source}: {name}: province {p} is not in this "
                        f"state region (see: tgc.py show {name})")
                named[p] = share.owner

        owners: list = []
        for share in spec.shares:
            if share.rest:
                provs = [p for p in all_prov if p not in named]
            else:
                provs = list(share.provinces)
            if not provs:
                self.notes.append(
                    f"{name}: {share.owner} received no provinces and was skipped")
                continue
            owners.append((share.owner, provs, share.state_type))
        return owners

    # -- pops -------------------------------------------------------------
    def _convert_pops(self, name: str, owners: list, van_owners: list) -> dict:
        van_pops = self.index["pops"].get(name, {}).get("by_country", {})
        if not van_pops:
            return {}
        van_prov = {o["country"]: set(o["provinces"]) for o in van_owners
                    if o["country"]}
        out: dict = defaultdict(list)
        for tag, provs, _ in owners:
            mine = set(provs)
            for van_tag, pop_list in van_pops.items():
                src = van_prov.get(van_tag)
                # Fraction of the old owner's land that this new owner took.
                if not src:
                    frac = 1.0 / len(owners)
                else:
                    frac = len(mine & src) / len(src)
                if frac <= 0:
                    continue
                for pop in pop_list:
                    conv = self._convert_pop(pop, tag, frac)
                    if conv:
                        out[tag] += conv
        return {t: v for t, v in out.items() if v}

    def _convert_pop(self, pop: dict, tag: str, frac: float) -> list:
        c = (self.countries.get(tag) or {}).get("spec")
        culture = pop["culture"]
        religion = pop["religion"] or self._default_religion(culture)
        size = int(round(pop["size"] * frac))
        if size <= 0:
            return []
        if not isinstance(c, Country):
            return [self._pop(culture, religion, size, pop["pop_type"])]

        culture = c.culture_map.get(culture, culture)
        religion = self._default_religion(culture) if religion is None else religion

        # Precedence: per-culture split, then per-religion split, then a plain
        # religion rename. Only the most specific rule that matches applies.
        split = c.culture_religion_split.get(culture)
        if split is None:
            split = c.religion_split.get(religion)
        if split:
            out, spent = [], 0
            items = list(split.items())
            for i, (rel, share) in enumerate(items):
                part = size - spent if i == len(items) - 1 else int(round(size * share))
                spent += part
                if part > 0:
                    out.append(self._pop(culture, rel, part, pop["pop_type"]))
            return out
        religion = c.religion_map.get(religion, religion)
        return [self._pop(culture, religion, size, pop["pop_type"])]

    def _default_religion(self, culture: str):
        cul = self.index["defs"]["cultures"].get(culture)
        return cul["religion"] if cul else None

    @staticmethod
    def _pop(culture, religion, size, pop_type) -> dict:
        rec = {"culture": culture, "size": size}
        if religion:
            rec["religion"] = religion
        if pop_type:
            rec["pop_type"] = pop_type
        return rec

    # -- buildings --------------------------------------------------------
    def _reassign_buildings(self, name: str, owners: list, van_owners: list) -> dict:
        van_blds = self.index["buildings"].get(name, {}).get("by_country", {})
        if not van_blds:
            return {}
        van_prov = {o["country"]: set(o["provinces"]) for o in van_owners
                    if o["country"]}
        out: dict = {}
        for van_tag, blk in van_blds.items():
            # Buildings are not divisible; the largest share of the old owner's
            # land inherits the whole block.
            src = van_prov.get(van_tag) or set()
            best, best_overlap = None, -1
            for tag, provs, _ in owners:
                overlap = len(set(provs) & src) if src else len(provs)
                if overlap > best_overlap:
                    best, best_overlap = tag, overlap
            if best is None:
                continue
            if self.country_type(best) == "decentralized":
                self.notes.append(
                    f"{name}: dropped {len(blk['types'])} building(s) inherited "
                    f"from {van_tag} because {best} is decentralized")
                continue
            out.setdefault(best, []).append(self._retarget(blk["script"], van_tag, best))
        return {tag: "\n".join(parts) for tag, parts in out.items()}

    def _retarget(self, script: str, old_tag: str, new_tag: str) -> str:
        """Point ownership at the new owner, and rescue landless references."""
        script = re.sub(rf"\bc:{old_tag}\b", f"c:{new_tag}", script)

        def fix(m):
            tag = m.group(1)
            return f"c:{new_tag}" if tag not in self.landed_tags else m.group(0)

        return re.sub(r"\bc:([A-Z0-9]{2,4})\b", fix, script)

    # -- derived ----------------------------------------------------------
    @property
    def landed_tags(self) -> set:
        """Tags that end up owning at least one province. Filled by pass 1, so
        it is complete before any pops or buildings are resolved."""
        return self._landed


# ---------------------------------------------------------------------------
# emitters


def _emit_states(res: Resolved) -> str:
    root = ["STATES = {"]
    for name in sorted(res.state_owners):
        root.append(f"\ts:{name} = {{")
        for tag, provs, state_type in res.state_owners[name]:
            root.append("\t\tcreate_state = {")
            root.append(f"\t\t\tcountry = c:{tag}")
            root.append("\t\t\towned_provinces = { " + " ".join(provs) + " }")
            if state_type:
                root.append(f"\t\t\tstate_type = {state_type}")
            root.append("\t\t}")
        for cu in res.state_homelands.get(name, []):
            root.append(f"\t\tadd_homeland = cu:{cu}")
        for c in res.state_claims.get(name, []):
            if c in res.landed_tags:
                root.append(f"\t\tadd_claim = c:{c}")
        root.append("\t}")
    root.append("}")
    return "\n".join(root)


def _emit_pops(res: Resolved) -> str:
    root = ["POPS = {"]
    for name in sorted(res.state_pops):
        by_tag = res.state_pops[name]
        if not by_tag:
            continue
        root.append(f"\ts:{name} = {{")
        for tag in sorted(by_tag):
            root.append(f"\t\tregion_state:{tag} = {{")
            for pop in by_tag[tag]:
                root.append("\t\t\tcreate_pop = {")
                root.append(f"\t\t\t\tculture = {pop['culture']}")
                if pop.get("religion"):
                    root.append(f"\t\t\t\treligion = {pop['religion']}")
                if pop.get("pop_type"):
                    root.append(f"\t\t\t\tpop_type = {pop['pop_type']}")
                root.append(f"\t\t\t\tsize = {pop['size']}")
                root.append("\t\t\t}")
            root.append("\t\t}")
        root.append("\t}")
    root.append("}")
    return "\n".join(root)


def _emit_buildings(res: Resolved) -> str:
    root = ["BUILDINGS = {"]
    for name in sorted(res.state_buildings):
        by_tag = res.state_buildings[name]
        if not by_tag:
            continue
        root.append(f"\ts:{name} = {{")
        for tag in sorted(by_tag):
            root.append(f"\t\tregion_state:{tag} = {{")
            for line in by_tag[tag].splitlines():
                root.append("\t\t\t" + line if line.strip() else "")
            root.append("\t\t}")
        root.append("\t}")
    root.append("}")
    return "\n".join(root)


def _colour_block(color) -> str:
    if not color:
        return ""
    if isinstance(color, (list, tuple)):
        if color and isinstance(color[0], str) and color[0] in ("hsv", "hsv360", "rgb"):
            return f"\tcolor = {color[0]}" + "{ " + " ".join(map(str, color[1:])) + " }\n"
        return "\tcolor = { " + " ".join(str(c) for c in color) + " }\n"
    return ""


def _emit_country_definitions(res: Resolved) -> str:
    """`common/country_definitions` is a keyed database: a duplicate key in a
    differently-named file is silently discarded with `Duplicated key TUR will
    not be created`. Overriding a vanilla tag requires REPLACE_OR_CREATE.
    """
    out: list = []
    for tag in sorted(res.world.countries):
        c = res.world.countries[tag]
        merged = res.countries[tag]
        key = tag if merged["is_new"] else f"REPLACE_OR_CREATE:{tag}"
        out.append(f"{key} = {{")
        out.append(_colour_block(merged["color"]).rstrip("\n"))
        out.append(f"\tcountry_type = {c.country_type}")
        out.append(f"\ttier = {c.tier}")
        cultures = merged["cultures"]
        out.append("\tcultures = { " + " ".join(cultures) + " }")
        if merged["religion"]:
            out.append(f"\treligion = {merged['religion']}")
        if merged["capital"]:
            out.append(f"\tcapital = {merged['capital']}")
        if merged["is_named_from_capital"]:
            out.append(f"\tis_named_from_capital = {merged['is_named_from_capital']}")
        out.append("}")
        out.append("")
    return "\n".join(out)


def _esc(s: str) -> str:
    return s.replace('"', '\\"')


def _emit_localization(res: Resolved, language: str) -> str:
    lines = [f"l_{language}:"]
    for tag in sorted(res.world.countries):
        c = res.world.countries[tag]
        name = (c.name_tr if language == "turkish" else c.name) or c.name
        adj = (c.adjective_tr if language == "turkish" else c.adjective) or c.adjective
        if name:
            lines.append(f' {tag}:0 "{_esc(name)}"')
            # Vanilla dynamic_country_names override the plain tag key, so the
            # dyn_c_* key has to be overridden too where one exists.
            dyn = f"dyn_c_{tag.lower()}"
            if dyn in res.index["loc"]:
                lines.append(f' {dyn}:0 "{_esc(name)}"')
        if adj:
            lines.append(f' {tag}_ADJ:0 "{_esc(adj)}"')
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# metadata


def _sync_replace_paths(written_dirs: set) -> list:
    """Rewrite metadata.json's replace_paths from what build actually emitted.

    Declaring a directory the mod does not fill deletes that content from the
    game, so this list is never maintained by hand.
    """
    meta_path = MOD / ".metadata" / "metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    custom = meta.setdefault("game_custom_data", {})
    wanted = sorted(d for d in written_dirs if d in NEEDS_REPLACE_PATH)
    if custom.get("replace_paths") != wanted:
        custom["replace_paths"] = wanted
        meta_path.write_text(json.dumps(meta, indent="\t", ensure_ascii=False) + "\n",
                             encoding="utf-8")
    return wanted


def _clean_owned() -> int:
    removed, touched = 0, set()
    for pattern in OWNED:
        for f in MOD.glob(pattern):
            touched.add(f.parent)
            f.unlink()
            removed += 1
    # Leave no empty directory behind: an empty dir under a replace_paths entry
    # is exactly the shape that deletes vanilla content and replaces it with
    # nothing.
    for d in sorted(touched, key=lambda p: -len(p.parts)):
        while d != MOD and d.is_dir() and not any(d.iterdir()):
            d.rmdir()
            d = d.parent
    return removed


# ---------------------------------------------------------------------------
# entry point


def build(verbose: bool = True) -> dict:
    world = load_world()
    index = idx.load()
    removed = _clean_owned()

    written: list = []
    dirs: set = set()

    def emit(rel: str, text: str, src: str, bom: bool = True) -> None:
        path = MOD / rel
        body = HEADER.format(src=src) + "\n" + text
        write_text(path, body, bom=bom)
        written.append(rel)
        dirs.add(str(path.parent.relative_to(MOD)).replace("\\", "/"))

    res = None
    if world.states:
        res = Resolved(world, index)
        emit("common/history/states/tgc_states.txt", _emit_states(res), "states/")
        pops = _emit_pops(res)
        if pops.strip() != "POPS = {\n}".strip():
            emit("common/history/pops/tgc_pops.txt", pops, "states/")
        blds = _emit_buildings(res)
        if blds.strip() != "BUILDINGS = {\n}".strip():
            emit("common/history/buildings/tgc_buildings.txt", blds, "states/")

    if world.countries:
        if res is None:
            res = Resolved(world, index)
        emit("common/country_definitions/tgc_countries.txt",
             _emit_country_definitions(res), "countries/")
        emit("localization/english/tgc_generated_countries_l_english.yml",
             _emit_localization(res, "english"), "countries/")
        if any(c.name_tr for c in world.countries.values()):
            emit("localization/turkish/tgc_generated_countries_l_turkish.yml",
                 _emit_localization(res, "turkish"), "countries/")

    replace_paths = _sync_replace_paths(dirs)

    if verbose:
        if removed:
            print(f"  cleaned {removed} previously generated file(s)")
        if not written:
            print("  world/ is empty - nothing to generate (the mod is pure vanilla)")
        for rel in written:
            print(f"  wrote {rel}")
        print(f"  replace_paths = {replace_paths or '[]'}")
        if res:
            print(f"  {len(res.state_owners)} states, "
                  f"{len(res.landed_tags)} countries with land")
            for n in res.notes[:20]:
                print(f"  note: {n}")
            if len(res.notes) > 20:
                print(f"  note: ... {len(res.notes) - 20} more")
    return {"written": written, "replace_paths": replace_paths, "resolved": res,
            "world": world}
