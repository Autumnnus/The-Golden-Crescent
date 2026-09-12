"""One province-accurate snapshot shared by PNG, offline HTML and LLM context."""
from __future__ import annotations

import base64
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image

from . import geo, index as idx, scenario
from .build import Resolved
from .paths import BUILD, WORLD, assert_read_only
from .world import World, load_world

MODES = ("political", "reference", "religion", "phase", "changes")


def stable_number(value):
    result = 2166136261
    for byte in str(value).encode("utf-8"):
        result = ((result ^ byte) * 16777619) & 0xffffffff
    return result


def write_output(path, data):
    path = Path(path)
    assert_read_only(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")


def owner_map(res):
    return {(state, prov): tag for state, owners in res.state_owners.items()
            for tag, provinces, _ in owners for prov in provinces}


class Snapshot:
    def __init__(self, scenario_path=None, baseline="world"):
        self.index = idx.load()
        base = load_world()
        self.scenario = scenario.load(scenario_path) if scenario_path else {
            "version": 1, "title": "The Golden Crescent", "countries": {}, "states": {}}
        if not scenario_path:
            if (WORLD / "scenario.yml").exists():
                self.scenario = scenario.load(WORLD / "scenario.yml")
            else:
                self.scenario["version"] = base.version
        self.world = scenario.overlay(base, self.scenario) if scenario_path else base
        scenario.validate_world(self.world, self.index)
        self.development = None
        if self.world.version >= 2:
            from .worldplan import compile_world
            self.res, _, self.development = compile_world(self.world, self.index)
        else:
            self.res = Resolved(self.world, self.index, contents=False)
        self.baseline_name = baseline
        before = World() if baseline == "vanilla" else base
        self.before = Resolved(before, self.index, contents=False)
        self.base = self.before if baseline == "world" else Resolved(base, self.index, contents=False)
        self.ids, self.geo = geo.load()
        self.codes = np.load(geo.PROVINCE_CODES, mmap_mode="r")
        self.adjacency = json.loads(geo.ADJACENCY.read_text(encoding="utf-8"))
        self.order = self.geo["meta"]["state_order"]
        self.state_numbers = {name: i for i, name in enumerate(self.order)}
        self.current_owners = owner_map(self.res)
        self.before_owners = owner_map(self.before)
        base_owners = owner_map(self.base)
        # Stable compact province IDs; 0 is explicitly outside indexed geometry.
        self.provinces = [None]
        for prov, state in sorted(self.index["province_state"].items()):
            self.provinces.append({"hex": prov, "state": self.state_numbers[state],
                "owner": self.current_owners.get((state, prov)),
                "base": base_owners.get((state, prov)),
                "before": self.before_owners.get((state, prov)),
                "impassable": prov in self.index["states"][state]["impassable"]})
        self.changed = {p["state"] for p in self.provinces[1:]
                        if p["owner"] != p["before"]}
        self.warnings = list(self.res.notes)
        if self.index["meta"].get("duplicate_provinces"):
            self.warnings.append("Vanilla contains duplicate province definitions; the index's first state wins.")
        self.warnings.append("Religion shows the owner's state religion, not population religion.")
        if not base:
            self.warnings.append("world/ is empty: the current mod baseline is vanilla.")

    def country(self, tag, before=False, base=False):
        from .mapdraw import _to_rgb
        res = self.base if base else self.before if before else self.res
        c = res.countries.get(tag, {})
        spec = res.world.countries.get(tag)
        return {"tag": tag, "name": (spec.name_tr or spec.name) if spec and (spec.name_tr or spec.name)
                else self.index["loc"].get(tag, tag),
                "color": list(_to_rgb(c.get("color"))), "religion": c.get("religion") or "none",
                "phase": spec.phase if spec else None, "capital": c.get("capital"),
                "country_type": c.get("country_type"), "source": c.get("source", "vanilla")}

    def colors(self, mode, before=False):
        from .mapdraw import SEA, BLANK, UNOWNED, _distinct, _religion_color
        palette = np.empty((len(self.provinces), 3), dtype=np.uint8)
        palette[0] = BLANK
        refs = {}
        for name in sorted(self.order, key=lambda n: (-len(self.adjacency.get(n, [])), n)):
            used = {refs[n] for n in self.adjacency.get(name, []) if n in refs}
            refs[name] = next(i for i in range(len(used) + 1) if i not in used)
        countries = {tag: self.country(tag, before) for tag in
                     (self.before.countries if before else self.res.countries)}
        for i, p in enumerate(self.provinces[1:], 1):
            name = self.order[p["state"]]
            st = self.index["states"][name]
            tag = p["before"] if before else p["owner"]
            c = countries.get(tag, {})
            if st["is_sea"]:
                color = SEA
            elif mode == "reference":
                color = _distinct(refs[name])
            elif mode == "changes":
                color = (230, 174, 78) if p["owner"] != p["before"] else (96, 116, 123)
            elif not tag:
                color = (182, 177, 160) if p["impassable"] else UNOWNED
            elif mode == "political":
                color = c["color"]
            elif mode == "religion":
                color = _religion_color(c.get("religion", "none"), self.index)
            elif mode == "phase":
                spec = (self.before.world if before else self.world).states.get(name)
                phase = (spec.phase if spec else None) or c.get("phase")
                color = _distinct(stable_number(phase) % 97) if phase else UNOWNED
            else:
                raise ValueError(f"Unknown map mode: {mode}")
            palette[i] = color
        return palette

    def viewport(self, region=None, width=3200):
        from .mapdraw import _crop_box
        if not 320 <= width <= 8192:
            raise ValueError("width must be between 320 and 8192")
        box, label = _crop_box(region, self.index, self.geo, self.adjacency,
                               world=self.world, owners=self.res.state_owners)
        h, w = self.ids.shape
        box = box or (0, 0, w, h)
        x0, y0, x1, y1 = max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3])
        if x1 <= x0 or y1 <= y0:
            raise ValueError("The selected region contains no drawable pixels")
        scale = min(1, width / (x1 - x0))
        size = (max(1, round((x1-x0)*scale)), max(1, round((y1-y0)*scale)))
        # Crop and sample BEFORE expanding to RGB: no full-world RGB allocation.
        codes = Image.fromarray(np.asarray(self.codes[y0:y1, x0:x1], dtype=np.int32))
        codes = np.asarray(codes.resize(size, Image.Resampling.NEAREST), dtype=np.uint32)
        lut = np.zeros(1 << 24, dtype=np.uint32)
        for i, p in enumerate(self.provinces[1:], 1):
            lut[int(p["hex"][1:], 16)] = i
        pixels = lut[codes]
        visible = set(int(v) for v in np.unique(self.ids[y0:y1, x0:x1]) if v >= 0)
        return {"pixels": pixels, "box": [x0, y0, x1, y1], "label": label,
                "scale": scale, "visible": visible, "size": size}

    def image(self, view, mode="political", before=False, borders="country"):
        from .mapdraw import BORDER
        pixels = view["pixels"]
        rgb = self.colors(mode, before)[pixels]
        state_lut = np.array([-1] + [p["state"] for p in self.provinces[1:]], dtype=np.int32)
        state_pixels = state_lut[pixels]
        if borders == "province":
            keys = pixels
        elif borders == "state" or mode in ("reference", "phase"):
            keys = state_pixels
        elif borders == "country":
            owners = sorted({p["before" if before else "owner"] for p in self.provinces[1:]
                             if p["before" if before else "owner"]})
            lookup = {tag: i+1 for i, tag in enumerate(owners)}
            keys = np.array([0] + [lookup.get(p["before" if before else "owner"], 0)
                            for p in self.provinces[1:]], dtype=np.int32)[pixels]
        else:
            return Image.fromarray(rgb)
        edge = np.zeros(pixels.shape, dtype=bool)
        edge[:, :-1] |= keys[:, :-1] != keys[:, 1:]
        edge[:-1, :] |= keys[:-1, :] != keys[1:, :]
        rgb[edge] = BORDER
        return Image.fromarray(rgb)

    def context(self, view):
        states = []
        for i in sorted(view["visible"]):
            name = self.order[i]
            st = self.index["states"][name]
            if st["is_sea"]:
                continue
            spec = self.world.states.get(name)
            aliases = [a for a, target in self.world.aliases.items()
                       if target == name or isinstance(target, list) and name in target]
            owners = [{"tag": t, "provinces": p, "state_type": typ}
                      for t, p, typ in self.res.state_owners.get(name, [])]
            old = [{"tag": t, "provinces": p, "state_type": typ}
                   for t, p, typ in self.before.state_owners.get(name, [])]
            states.append({"id": name, "index": i, "name": self.index["loc"].get(name, name),
                "aliases": aliases, "region": st["region"], "owners": owners, "before": old,
                "changed": i in self.changed, "provinces": st["provinces"],
                "impassable": st["impassable"], "neighbors": [n for n in self.adjacency.get(name, [])
                    if not self.index["states"][n]["is_sea"]],
                "anchor": self.geo["states"][name]["anchor"], "bbox": self.geo["states"][name]["bbox"],
                "source": spec.source if spec else "vanilla", "phase": spec.phase if spec else None,
                "base_phase": self.base.world.states[name].phase if name in self.base.world.states else None,
                "homelands": self.res.state_homelands.get(name, []),
                "arable_land": st["arable_land"], "resources": st["capped_resources"]})
        return {"version": 1, "title": self.scenario.get("title", "The Golden Crescent"),
                "baseline": self.baseline_name, "region": view["label"],
                "geometry": {"box": view["box"], "size": view["size"], "scale": view["scale"]},
                "warnings": self.warnings, "states": states,
                "countries": {tag: self.country(tag) for tag in sorted(self.res.countries)},
                "before_countries": {tag: self.country(tag, True) for tag in sorted(self.before.countries)},
                "base_countries": {tag: self.country(tag, base=True) for tag in sorted(self.base.countries)},
                "scenario": self.scenario,
                "development": self.development,
                "contract": "Scenario version 1/2: countries merge fields; states replace ownership plans. "
                    "Use exact STATE_* ids and province hex strings. Unlisted states inherit world/. "
                    "A split must cover all passable provinces, or include one rest:true share. "
                    "This is an 1836 source preview, not a running save or event simulation. "
                    "For economy, population, military and diplomacy use version 2 and scenario validate/report/build. "
                    "Read tools/LLM_SCENARIO_WORKFLOW.md and query rules for installed identifiers. "
                    "Source validation is not a runtime simulation."}

    def llm_context(self, view):
        """Keep region queries small; browser-only palettes and base copies stay out."""
        data = self.context(view)
        tags = {o["tag"] for s in data["states"] for key in ("owners", "before") for o in s[key]}
        tags.update(self.scenario.get("countries", {}))
        data["country_tags"] = sorted(data["countries"])
        data["countries"] = {t: c for t, c in data["countries"].items() if t in tags}
        if data.get("development"):
            report = data["development"]
            visible = {s["id"] for s in data["states"]}
            data["development"] = {**report, "states":{k:v for k,v in report["states"].items() if k in visible},
                                   "countries":{k:v for k,v in report["countries"].items() if k in tags}}
        del data["base_countries"], data["before_countries"]
        return data


def png_data(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def export_atlas(region=None, out=None, width=4096, scenario_path=None, baseline="world"):
    snap = Snapshot(scenario_path, baseline)
    view = snap.viewport(region, width)
    data = snap.context(view)
    data["catalog_states"] = snap.context({**view, "visible": set(range(len(snap.order)))})["states"]
    data["provinces"] = snap.provinces
    data["fingerprint"] = hashlib.sha256(json.dumps(
        [data["geometry"], snap.provinces, data["base_countries"]], sort_keys=True).encode()).hexdigest()[:16]
    data["palettes"] = {mode: snap.colors(mode).tolist() for mode in MODES}
    pixels = view["pixels"]
    rgb = np.stack([(pixels >> 16) & 255, (pixels >> 8) & 255, pixels & 255], axis=-1).astype(np.uint8)
    data["hitImage"] = png_data(Image.fromarray(rgb))
    data["beforePalette"] = snap.colors("political", before=True).tolist()
    # Escape JSON at the HTML parser boundary; labels are always rendered with textContent.
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    assets = Path(__file__).parent / "atlas_web"
    html = (assets / "atlas.html").read_text(encoding="utf-8")
    html = html.replace("/* ATLAS_CSS */", (assets / "atlas.css").read_text(encoding="utf-8"))
    html = html.replace("/* ATLAS_JS */", (assets / "atlas.js").read_text(encoding="utf-8"))
    html = html.replace("/* ATLAS_DATA */", payload)
    path = Path(out) if out else BUILD / "maps" / f"atlas_{view['label']}.html"
    if path.suffix.lower() != ".html":
        raise ValueError("atlas --out must end in .html")
    # Validate all destinations before the first write.
    assert_read_only(path)
    assert_read_only(path.with_suffix(".json"))
    write_output(path, html)
    write_output(path.with_suffix(".json"), json.dumps(snap.llm_context(view), ensure_ascii=False, indent=2))
    print(f"wrote {path}\nwrote {path.with_suffix('.json')}\n"
          f"{len(data['states'])} land states · {len(snap.changed)} changed states · offline atlas")
    return 0
