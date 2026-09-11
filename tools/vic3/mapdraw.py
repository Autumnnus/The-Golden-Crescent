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

from . import geo as geo_mod
from . import index as idx
from .paths import BUILD, VANILLA
from .world import load_world

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
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# what to paint


def _resolved_owners():
    """STATE_* -> owning tag (largest share), from world/ merged onto vanilla."""
    from . import build as build_mod
    world = load_world()
    res = build_mod.Resolved(world, idx.load())
    out = {}
    for state, owners in res.state_owners.items():
        best = max(owners, key=lambda o: len(o[1]))
        out[state] = best[0]
    return out, res


def _state_colors(mode: str, index: dict, adjacency: dict) -> tuple:
    """(state -> rgb, state -> label suffix)."""
    states = index["states"]
    colors, notes = {}, {}

    if mode == "reference":
        # Greedy colouring over the adjacency graph so no two touching states
        # share a hue; the map exists to tell them apart.
        assigned: dict = {}
        for name in sorted(states, key=lambda n: -len(adjacency.get(n, ()))):
            used = {assigned[n] for n in adjacency.get(name, ()) if n in assigned}
            k = next(i for i in range(999) if i not in used)
            assigned[name] = k
        for name, st in states.items():
            colors[name] = SEA if st["is_sea"] else _distinct(assigned[name])
        return colors, notes

    owners, res = _resolved_owners()
    for name, st in states.items():
        if st["is_sea"]:
            colors[name] = SEA
            continue
        tag = owners.get(name)
        if not tag:
            colors[name] = UNOWNED
            continue
        notes[name] = tag
        if mode == "political":
            colors[name] = _to_rgb((res.countries.get(tag) or {}).get("color"))
        elif mode == "religion":
            rel = (res.countries.get(tag) or {}).get("religion") or "none"
            notes[name] = rel
            colors[name] = _religion_color(rel, index)
        elif mode == "phase":
            spec = res.world.countries.get(tag)
            phase = (spec.phase if spec and spec.phase else None)
            notes[name] = phase or "vanilla"
            colors[name] = (UNOWNED if phase is None
                            else _distinct(abs(hash(phase)) % 97))
    return colors, notes


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
    return _distinct(abs(hash(rel)) % 97)


# ---------------------------------------------------------------------------
# cropping


def _crop_box(region, index: dict, gmeta: dict, adjacency: dict):
    if not region or region.lower() == "world":
        return None, "world"
    states = index["states"]

    name = region if region.startswith("STATE_") else "STATE_" + region.upper()
    if name in states:
        wanted = {name} | set(adjacency.get(name, ()))
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
    return (x0 - pad, y0 - pad, x1 + pad, y1 + pad)


# ---------------------------------------------------------------------------
# render


def render(mode: str = "political", region=None, out=None,
           labels: bool = True) -> int:
    index = idx.load()
    ids, gmeta = geo_mod.load()
    adjacency = json.loads((BUILD / "state_adjacency.json").read_text(encoding="utf-8"))
    order = gmeta["meta"]["state_order"]

    colors, notes = _state_colors(mode, index, adjacency)

    palette = np.zeros((len(order) + 1, 3), dtype=np.uint8)
    palette[len(order)] = BLANK                       # index for "no state"
    for i, name in enumerate(order):
        palette[i] = colors.get(name, BLANK)

    lookup = np.where(ids < 0, len(order), ids)
    rgb = palette[lookup]

    # Thin state borders: a pixel whose right or lower neighbour is a different
    # state. Cheap, and it keeps small states legible when scaled down.
    edge = np.zeros(ids.shape, dtype=bool)
    edge[:, :-1] |= ids[:, :-1] != ids[:, 1:]
    edge[:-1, :] |= ids[:-1, :] != ids[1:, :]
    rgb[edge] = BORDER

    img = Image.fromarray(rgb, mode="RGB")

    box, label = _crop_box(region, index, gmeta, adjacency)
    if box:
        x0, y0, x1, y1 = box
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(img.width, x1), min(img.height, y1)
        img = img.crop((x0, y0, x1, y1))
        offset = (x0, y0)
        visible = {n for n, m in gmeta["states"].items()
                   if x0 <= m["anchor"][0] <= x1 and y0 <= m["anchor"][1] <= y1}
    else:
        offset = (0, 0)
        visible = set(gmeta["states"])

    scale = min(1.0, MAX_WIDTH / img.width)
    if scale < 1.0:
        img = img.resize((int(img.width * scale), int(img.height * scale)),
                         Image.NEAREST)

    if labels:
        _draw_labels(img, visible, gmeta, colors, notes, offset, scale, index, mode)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = Path(out) if out else OUT_DIR / f"{mode}_{label}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print(f"wrote {path}  ({img.width}x{img.height}, mode={mode}, region={label})")
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
