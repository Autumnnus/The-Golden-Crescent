"""Render maps of the resolved world.

    tgc.py map --mode reference --region 08_middle_east
    tgc.py map --mode political --region STATE_ANATOLIA
    tgc.py map --mode religion

`reference` is the one to draw *before* editing world/: it labels every state
region so the names can be confirmed against what the user described, instead
of guessing a STATE_* id and silently mis-assigning land.
"""

from __future__ import annotations

import colorsys
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .paths import BUILD, assert_read_only
from .atlas import stable_number

OUT_DIR = BUILD / "maps"
MAX_WIDTH = 3200

SEA = (176, 204, 222)
BLANK = (245, 243, 238)
BORDER = (60, 60, 60)
UNOWNED = (215, 212, 205)


# ---------------------------------------------------------------------------
# colour helpers


def _to_rgb(color) -> tuple:
    """Vanilla writes colours as { r g b }, hsv{ h s v } or hsv360{ h s v }."""
    if not color:
        return (150, 150, 150)
    vals = list(color)
    kind = "rgb"
    if isinstance(vals[0], str) and not vals[0].replace(".", "").isdigit():
        kind, vals = vals[0], vals[1:]
    try:
        nums = [float(v) for v in vals[:3]]
    except (TypeError, ValueError):
        return (150, 150, 150)
    if len(nums) < 3:
        return (150, 150, 150)
    if kind == "hsv":                         # h, s, v all 0..1
        return _clamp(colorsys.hsv_to_rgb(*nums), 255)
    if kind == "hsv360":                      # h is 0..360, s and v are 0..100
        return _clamp(colorsys.hsv_to_rgb(nums[0] / 360.0, nums[1] / 100.0,
                                          nums[2] / 100.0), 255)
    if max(nums) <= 1.001:                    # some entries are 0..1 rgb
        return _clamp(nums, 255)
    return _clamp(nums, 1)


def _clamp(nums, scale: float) -> tuple:
    return tuple(max(0, min(255, int(round(v * scale)))) for v in nums[:3])


def _distinct(i: int) -> tuple:
    """Evenly spread hues; used when the point is telling regions apart."""
    h = (i * 0.61803398875) % 1.0
    s = 0.42 + 0.22 * ((i // 3) % 3)
    v = 0.78 + 0.14 * ((i // 7) % 2)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def _readable(bg: tuple) -> tuple:
    return (20, 20, 20) if (0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]) > 140 \
        else (250, 250, 250)


def _font(size: int):
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf",
                 "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# what to paint


def _religion_color(rel: str, index: dict) -> tuple:
    defs = index["defs"]["religions"].get(rel)
    if defs and defs.get("icon"):
        pass
    fixed = {
        "catholic": (214, 160, 60), "protestant": (70, 100, 170),
        "orthodox": (140, 80, 160), "oriental_orthodox": (40, 140, 165),
        "sunni": (35, 140, 90), "shiite": (25, 105, 120), "ibadi": (90, 165, 120),
        "hindu": (225, 130, 60), "sikh": (235, 190, 70), "mahayana": (200, 110, 140),
        "theravada": (220, 150, 90), "gelugpa": (185, 95, 60),
        "confucian": (170, 60, 70), "shinto": (200, 90, 110),
        "jewish": (110, 120, 200), "animist": (130, 150, 80),
        "atheist": (140, 140, 140),
    }
    if rel in fixed:
        return fixed[rel]
    return _distinct(stable_number(rel) % 97)


# ---------------------------------------------------------------------------
# cropping


def _crop_box(region, index: dict, gmeta: dict, adjacency: dict,
              world=None, owners=None):
    if not region or region.lower() == "world":
        return None, "world"
    states = index["states"]
    # Explicit selectors compose without guessing ambiguous fuzzy names.
    if "," in region:
        boxes = [_crop_box(r.strip(), index, gmeta, adjacency, world, owners)[0]
                 for r in region.split(",")]
        if any(b is None for b in boxes):
            return None, "world"
        return (min(b[0] for b in boxes), min(b[1] for b in boxes),
                max(b[2] for b in boxes), max(b[3] for b in boxes)), "selection"
    aliases = world.aliases if world else {}
    alias = next((v for k, v in aliases.items() if k.casefold() == region.casefold()), None)
    if alias:
        wanted = {alias} if isinstance(alias, str) else set(alias)
        wanted = {n if n.startswith("STATE_") else "STATE_" + n.upper() for n in wanted}
        if not wanted <= states.keys():
            raise ValueError(f"Invalid state alias: {region}")
        return _bbox_of(wanted, gmeta), sorted(wanted)[0]
    tag = region.removeprefix("country:").upper()
    if tag in index["countries"] or world and tag in world.countries:
        wanted = {n for n, shares in (owners or {}).items() if any(t == tag for t, _, _ in shares)}
        if not wanted:
            raise ValueError(f"Country {tag} owns no land")
        return _bbox_of(wanted, gmeta), tag


    name = region.upper() if region.upper().startswith("STATE_") else "STATE_" + region.upper()
    if name in states:
        wanted = {name} | {n for n in adjacency.get(name, ()) if not states[n]["is_sea"]}
        return _bbox_of(wanted, gmeta), name

    # A state_regions file stem, e.g. 08_middle_east.
    stems = {s["file"].removesuffix(".txt") for s in states.values()}
    match = [s for s in stems if region.lower() in s.lower()]
    if len(match) == 1:
        wanted = {n for n, s in states.items()
                  if s["file"].removesuffix(".txt") == match[0]}
        return _bbox_of(wanted, gmeta), match[0]
    if len(match) > 1:
        raise SystemExit(f"--region {region!r} matches {sorted(match)}")

    raise SystemExit(
        f"--region {region!r} is neither a state nor a state_regions file.\n"
        f"Try: tgc.py find {region}\n"
        f"Files: {sorted(stems)}")


def _bbox_of(names: set, gmeta: dict):
    boxes = [gmeta["states"][n]["bbox"] for n in names if n in gmeta["states"]]
    if not boxes:
        return None
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes)
    y1 = max(b[3] for b in boxes)
    pad = max(40, (x1 - x0) // 12)
    return (x0 - pad, y0 - pad, x1 + pad + 1, y1 + pad + 1)


# ---------------------------------------------------------------------------
# render


def render(mode: str = "political", region=None, out=None,
           labels: bool = True, width: int = MAX_WIDTH, scenario_path=None,
           baseline="world", borders="country", data=False) -> int:
    from .atlas import Snapshot, write_output
    snap = Snapshot(scenario_path, baseline)
    view = snap.viewport(region, width)
    img = snap.image(view, mode, borders=borders)
    context = snap.context(view)
    notes, colors = {}, {}
    for state in context["states"]:
        owners = state["owners"]
        tags = sorted({o["tag"] for o in owners})
        if mode == "religion":
            notes[state["id"]] = " / ".join(sorted({snap.country(t)["religion"] for t in tags}))
        elif mode == "phase":
            notes[state["id"]] = " / ".join(sorted({str(state["phase"] or snap.country(t)["phase"] or "vanilla") for t in tags}))
        else:
            notes[state["id"]] = " / ".join(tags)
        colors[state["id"]] = BLANK
    if labels:
        _draw_labels(img, {s["id"] for s in context["states"]}, snap.geo,
                     colors, notes, view["box"][:2], view["scale"], snap.index, mode)
    # A title, explicit semantics and a compact legend make exported images self-contained.
    counts = np.bincount(view["pixels"].ravel(), minlength=len(snap.provinces))
    areas = {}
    for i, province in enumerate(snap.provinces[1:], 1):
        tag = province["owner"]
        if tag and counts[i]:
            areas[tag] = areas.get(tag, 0) + int(counts[i])
    tags = sorted(areas, key=lambda t: (-areas[t], t))
    legend = []
    if mode == "political":
        legend = [(snap.country(t)["name"] + " · " + t, snap.country(t)["color"]) for t in tags]
    elif mode == "religion":
        rels = sorted({snap.country(t)["religion"] for t in tags})
        legend = [(r, _religion_color(r, snap.index)) for r in rels]
    elif mode == "changes":
        legend = [("Ownership changed", (230,174,78)), ("Unchanged", (96,116,123))]
    elif mode == "phase":
        phases = {s["phase"] or snap.country(o["tag"])["phase"]
                  for s in context["states"] for o in s["owners"]}
        legend = [(str(p or "vanilla"), _distinct(stable_number(p) % 97) if p else UNOWNED)
                  for p in sorted(phases, key=lambda v: str(v))]
    cols = max(1, img.width // 250)
    shown = legend[:cols * 3]
    footer = 42 + 26 * ((len(shown) + cols - 1) // cols)
    framed = Image.new("RGB", (img.width, img.height + 84 + footer), (20,32,40))
    framed.paste(img, (0,84))
    draw = ImageDraw.Draw(framed)
    title = context["title"][:70]
    draw.text((20,12), title, font=_font(24), fill=(238,223,185))
    subtitle = f"{mode.upper()}  /  {view['label']}  /  1836 source preview"
    draw.text((20,49), subtitle, font=_font(14), fill=(194,209,215))
    for i, (label, color) in enumerate(shown):
        x, y = 20 + (i % cols)*250, img.height + 97 + (i//cols)*26
        draw.rectangle((x,y+3,x+12,y+15), fill=tuple(color))
        draw.text((x+20,y), label[:29], font=_font(13), fill=(231,236,237))
    note = ("Religion = owner's state religion, not population share." if mode == "religion" else
            f"Province ownership · Baseline: {baseline} · {len(snap.changed)} changed states worldwide")
    if len(legend) > len(shown):
        note += f" · +{len(legend)-len(shown)} legend entries in atlas"
    draw.text((20,framed.height-26), note, font=_font(12), fill=(194,209,215))
    path = Path(out) if out else OUT_DIR / f"{mode}_{view['label']}.png"
    if path.suffix.lower() != ".png":
        raise ValueError("map --out must end in .png")
    assert_read_only(path)
    if data:
        assert_read_only(path.with_suffix(".json"))
    path.parent.mkdir(parents=True, exist_ok=True)
    framed.save(path)
    if data:
        write_output(path.with_suffix(".json"), json.dumps(snap.llm_context(view), ensure_ascii=False, indent=2))
    print(f"wrote {path}  ({framed.width}x{framed.height}, mode={mode}, region={view['label']})")
    return 0


def _draw_labels(img, visible, gmeta, colors, notes, offset, scale, index, mode):
    draw = ImageDraw.Draw(img)
    size = 13 if len(visible) > 60 else 16
    font = _font(size)
    loc = index["loc"]
    # Bigger states first, and skip anything too small to carry text.
    ranked = sorted((n for n in visible if n in gmeta["states"]),
                    key=lambda n: -gmeta["states"][n]["pixels"])
    placed: list = []
    for name in ranked:
        m = gmeta["states"][name]
        if m["pixels"] * scale * scale < 900:
            continue
        if index["states"][name]["is_sea"]:
            continue
        x = (m["anchor"][0] - offset[0]) * scale
        y = (m["anchor"][1] - offset[1]) * scale
        if not (0 <= x < img.width and 0 <= y < img.height):
            continue
        text = loc.get(name) or name.removeprefix("STATE_").replace("_", " ").title()
        if mode != "reference" and notes.get(name):
            text = f"{text}\n{notes[name]}"
        box = draw.multiline_textbbox((x, y), text, font=font, anchor="mm",
                                      align="center")
        if box[0] < 0 or box[1] < 0 or box[2] > img.width or box[3] > img.height:
            continue
        if any(not (box[2] < p[0] or box[0] > p[2]
                    or box[3] < p[1] or box[1] > p[3]) for p in placed):
            continue
        placed.append(box)
        fg = _readable(colors.get(name, BLANK))
        bg = (255, 255, 255) if fg[0] < 128 else (0, 0, 0)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            draw.multiline_text((x + dx, y + dy), text, font=font, fill=bg,
                                anchor="mm", align="center")
        draw.multiline_text((x, y), text, font=font, fill=fg, anchor="mm",
                            align="center")
