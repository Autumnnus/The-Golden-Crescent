"""Harita gorsellestirme.

Uc mod:
    political  - state'leri sahip ulkenin rengine boyar (mevcut durum)
    reference  - her state'e ayri renk + isim etiketi (konusma referansi)
    diff       - vanilla ile modun farkini gosterir

Ekran goruntusu uzerinden konusabilmenin sarti ortak bir referans haritasi;
`reference` modu tam olarak onun icin var.
"""

from __future__ import annotations

import colorsys
import hashlib
import re
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import geo as geo_mod
from . import index as index_mod
from . import paths

Image.MAX_IMAGE_PIXELS = None

WATER = (58, 84, 112)
UNOWNED = (72, 72, 72)
BORDER = (24, 24, 24)

_COLOR_BLOCK = re.compile(r"^\s*(rgb|hsv|hsv360)?\s*\{\s*([^}]*)\}\s*$")


def parse_color(value: Any, fallback: tuple[int, int, int] = (128, 128, 128)) -> tuple[int, int, int]:
    """Vic3 renk gosterimini RGB'ye cevirir: `{ 62 122 189 }`, `hsv{ .99 .7 .9 }`, [r,g,b]."""
    if value is None:
        return fallback
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return tuple(int(c) for c in value)  # type: ignore[return-value]
    if not isinstance(value, str):
        return fallback

    match = _COLOR_BLOCK.match(value)
    if not match:
        return fallback
    kind = match.group(1) or "rgb"
    parts = [p for p in re.split(r"[\s,]+", match.group(2).strip()) if p]
    try:
        numbers = [float(p) for p in parts[:3]]
    except ValueError:
        return fallback
    if len(numbers) < 3:
        return fallback

    def clamp(value: float) -> int:
        return max(0, min(255, int(round(value))))

    if kind == "rgb":
        if max(numbers) <= 1.0:
            return tuple(clamp(n * 255) for n in numbers)  # type: ignore[return-value]
        return tuple(clamp(n) for n in numbers)  # type: ignore[return-value]
    if kind == "hsv360":
        # hsv360: h 0-360, s ve v 0-100
        numbers = [numbers[0] / 360.0, numbers[1] / 100.0, numbers[2] / 100.0]
    numbers = [min(max(n, 0.0), 1.0) for n in numbers]
    r, g, b = colorsys.hsv_to_rgb(*numbers)
    return (clamp(r * 255), clamp(g * 255), clamp(b * 255))


def stable_color(key: str, saturation: float = 0.55, value: float = 0.85) -> tuple[int, int, int]:
    """Isimden deterministik, birbirinden ayirt edilebilir renk uretir."""
    digest = hashlib.md5(key.encode("utf-8")).digest()
    hue = digest[0] / 255.0
    sat = saturation + (digest[1] / 255.0) * 0.25
    val = value - (digest[2] / 255.0) * 0.25
    r, g, b = colorsys.hsv_to_rgb(hue, min(sat, 1.0), min(val, 1.0))
    return (int(r * 255), int(g * 255), int(b * 255))


# ---------------------------------------------------------------------------
# Kirpma bolgesi
# ---------------------------------------------------------------------------

def bbox_for_states(state_names: Iterable[str], padding: int = 60) -> tuple[int, int, int, int]:
    geometry = geo_mod.load_state_geometry()
    boxes = [geometry[n]["bbox"] for n in state_names if n in geometry]
    if not boxes:
        raise SystemExit("Bu state'ler icin geometri bulunamadi.")
    x0 = min(b[0] for b in boxes) - padding
    y0 = min(b[1] for b in boxes) - padding
    x1 = max(b[2] for b in boxes) + padding
    y1 = max(b[3] for b in boxes) + padding
    return (x0, y0, x1, y1)


def resolve_region(region: str | None) -> tuple[int, int, int, int] | None:
    """`--region` degerini piksel kutusuna cevirir.

    Kabul edilenler: strategic region adi, virgullu state listesi, `x0,y0,x1,y1`.
    """
    if not region:
        return None
    if re.fullmatch(r"\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*", region):
        x0, y0, x1, y1 = (int(p) for p in region.split(","))
        return (x0, y0, x1, y1)

    ix = index_mod.load_index()
    if region in ix["strategic_regions"]:
        return bbox_for_states(ix["strategic_regions"][region])

    names: list[str] = []
    for part in region.split(","):
        part = part.strip()
        if not part:
            continue
        matches = index_mod.find_states(part, ix, limit=1)
        if not matches:
            raise SystemExit(f"Bolge cozulemedi: '{part}'")
        names.append(matches[0])
    return bbox_for_states(names)


# ---------------------------------------------------------------------------
# Cizim
# ---------------------------------------------------------------------------

STATE_ID_CACHE = paths.BUILD_DIR / "state_ids.npy"


def _full_state_id_map(state_names: list[str]) -> np.ndarray:
    """Tum harita icin piksel -> state indeksi (-1 = bilinmeyen). Diske onbelleklenir.

    provinces.png'yi her render'da yeniden cozmek ~15 saniye suruyor; bu onbellek
    tekrarli render'lari birkac saniyeye indiriyor.
    """
    if STATE_ID_CACHE.exists():
        cached = np.load(STATE_ID_CACHE)
        if cached.shape[0] > 0:
            return cached

    ix = index_mod.load_index()
    packed = geo_mod.load_province_image()
    codes = np.unique(packed)

    name_to_slot = {name: i for i, name in enumerate(state_names)}
    code_to_state = np.full(codes.size, -1, dtype=np.int32)
    for hex_id, state_name in ix["province_to_state"].items():
        value = geo_mod.province_hex_to_int(hex_id)
        position = np.searchsorted(codes, value)
        if position < codes.size and codes[position] == value:
            code_to_state[position] = name_to_slot[state_name]

    flat = np.searchsorted(codes, packed.ravel())
    state_ids = code_to_state[flat].reshape(packed.shape).astype(np.int16)

    paths.assert_safe_write(STATE_ID_CACHE)
    paths.BUILD_DIR.mkdir(parents=True, exist_ok=True)
    np.save(STATE_ID_CACHE, state_ids)
    return state_ids


def _state_id_array(crop: tuple[int, int, int, int] | None) -> tuple[np.ndarray, list[str]]:
    """Her piksel icin state indeksi (-1 = bilinmeyen/su) ve state isim listesi."""
    ix = index_mod.load_index()
    state_names = sorted(ix["states"])
    state_ids = _full_state_id_map(state_names)
    height, width = state_ids.shape

    if crop:
        x0 = max(0, crop[0]); y0 = max(0, crop[1])
        x1 = min(width, crop[2]); y1 = min(height, crop[3])
        state_ids = state_ids[y0:y1, x0:x1]

    return state_ids.astype(np.int32), state_names


def render(
    mode: str = "political",
    out: Path | None = None,
    region: str | None = None,
    max_width: int = 2400,
    labels: bool = True,
    borders: bool = True,
) -> Path:
    ix = index_mod.load_index()
    crop = resolve_region(region)
    state_ids, state_names = _state_id_array(crop)

    palette = np.zeros((len(state_names) + 1, 3), dtype=np.uint8)
    palette[len(state_names)] = WATER  # -1 icin

    owner_of = _current_owners(ix)

    for i, name in enumerate(state_names):
        entry = ix["states"][name]
        if entry["is_sea"]:
            palette[i] = WATER
            continue
        if mode == "reference":
            palette[i] = stable_color(name)
        elif mode == "diff":
            vanilla_owner = next(iter(entry["vanilla_owners"]), None)
            new_owner = owner_of.get(name)
            if new_owner is None:
                palette[i] = UNOWNED
            elif new_owner == vanilla_owner:
                palette[i] = (96, 104, 96)
            else:
                palette[i] = (196, 132, 60)
        else:  # political
            tag = owner_of.get(name)
            palette[i] = UNOWNED if tag is None else _country_color(tag, ix)

    rgb = palette[np.where(state_ids < 0, len(state_names), state_ids)]

    if borders:
        differs = np.zeros(state_ids.shape, dtype=bool)
        differs[:-1, :] |= state_ids[:-1, :] != state_ids[1:, :]
        differs[:, :-1] |= state_ids[:, :-1] != state_ids[:, 1:]
        rgb[differs] = BORDER

    image = Image.fromarray(rgb, mode="RGB")

    scale = 1.0
    if image.width > max_width:
        scale = max_width / image.width
        image = image.resize(
            (max_width, max(1, int(image.height * scale))), Image.Resampling.NEAREST
        )

    if labels:
        _draw_labels(image, state_ids, state_names, crop, scale, ix, owner_of, mode)

    out = Path(out) if out else paths.MAPS_DIR / f"{mode}.png"
    if not out.is_absolute():
        out = paths.MOD_ROOT / out
    out = paths.assert_safe_write(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    return out


def _current_owners(ix: dict[str, Any]) -> dict[str, str]:
    """Modun su anki sahiplik durumu: world/ varsa oradan, yoksa vanilla'dan."""
    from .world import WorldError, load_world

    owners: dict[str, str] = {}
    for name, entry in ix["states"].items():
        vanilla_owner = next(iter(entry["vanilla_owners"]), None)
        if vanilla_owner:
            owners[name] = vanilla_owner

    try:
        world = load_world()
    except WorldError:
        return owners

    inherit = str(world.defaults.get("unlisted", "inherit")) == "inherit"
    if not inherit:
        owners = {}
    for name, spec in world.states.items():
        if not spec.slices:
            owners.pop(name, None)
            continue
        if len(spec.slices) == 1:
            owners[name] = spec.slices[0].owner
            continue
        # Bolunmus state: haritada tek renk gosterebiliyoruz, o yuzden EN COK
        # province'a sahip olani seciyoruz. Ilk dilimi almak yaniltiyordu -
        # Sicilya'nin tek province'lik Messina dilimi butun adayi Rum
        # gosteriyordu. Oyun dosyasi zaten province bazinda dogru; bu yalnizca
        # onizleme haritasinin sadelestirmesi.
        entry = ix["states"].get(name)
        if entry is None:
            owners[name] = spec.slices[0].owner
            continue
        try:
            from .build import resolve_ownership
            ownership = resolve_ownership(spec, entry)
        except ValueError:
            owners[name] = spec.slices[0].owner
            continue
        if ownership:
            owners[name] = max(ownership.items(), key=lambda kv: len(kv[1]))[0]
    return owners


_COUNTRY_COLOR_CACHE: dict[str, tuple[int, int, int]] = {}


def _country_color(tag: str, ix: dict[str, Any]) -> tuple[int, int, int]:
    if tag in _COUNTRY_COLOR_CACHE:
        return _COUNTRY_COLOR_CACHE[tag]
    from .world import WorldError, load_world

    color: tuple[int, int, int] | None = None
    try:
        world = load_world()
        spec = world.countries.get(tag)
        if spec is not None and spec.color is not None:
            color = parse_color(spec.color)
    except WorldError:
        pass
    if color is None:
        info = ix["countries"].get(tag)
        color = parse_color(info["color"]) if info else stable_color(tag)
    # Vanilla'da cok sayida ulke ayni gri-mavi rengi paylasiyor; ayirt edilebilsin
    if color == (62, 122, 189):
        color = stable_color(tag)
    _COUNTRY_COLOR_CACHE[tag] = color
    return color


def _load_font(size: int) -> ImageFont.ImageFont:
    for candidate in ("arialbd.ttf", "arial.ttf", "seguisb.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_labels(
    image: Image.Image,
    state_ids: np.ndarray,
    state_names: list[str],
    crop: tuple[int, int, int, int] | None,
    scale: float,
    ix: dict[str, Any],
    owner_of: dict[str, str],
    mode: str,
) -> None:
    geometry = geo_mod.load_state_geometry()
    offset_x = crop[0] if crop else 0
    offset_y = crop[1] if crop else 0

    visible, counts = np.unique(state_ids, return_counts=True)
    draw = ImageDraw.Draw(image)
    font = _load_font(max(10, int(13 * max(scale, 0.6) * 1.4)))

    # Buyuk state'ler once etiketlenir; kucukler yer kalmazsa atlanir
    order = np.argsort(-counts)
    occupied: list[tuple[float, float, float, float]] = []

    for position in order:
        slot = int(visible[position])
        if slot < 0:
            continue
        pixels_visible = int(counts[position])
        if pixels_visible < 400:
            continue
        name = state_names[slot]
        entry = ix["states"][name]
        if entry["is_sea"]:
            continue
        info = geometry.get(name)
        if not info:
            continue

        x = (info["center"][0] - offset_x) * scale
        y = (info["center"][1] - offset_y) * scale
        if not (0 <= x < image.width and 0 <= y < image.height):
            continue

        short = name.removeprefix("STATE_").replace("_", " ").title()
        if mode == "political":
            tag = owner_of.get(name)
            text = f"{short}\n{tag}" if tag else short
        else:
            text = short

        left, top, right, bottom = draw.multiline_textbbox(
            (x, y), text, font=font, anchor="mm", align="center"
        )
        box = (left - 2, top - 2, right + 2, bottom + 2)
        if any(_overlaps(box, other) for other in occupied):
            continue
        occupied.append(box)
        _draw_outlined(draw, (x, y), text, font)


def _overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def _draw_outlined(draw: ImageDraw.ImageDraw, position, text: str, font) -> None:
    x, y = position
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        draw.multiline_text((x + dx, y + dy), text, font=font, fill=(0, 0, 0),
                            anchor="mm", align="center")
    draw.multiline_text((x, y), text, font=font, fill=(255, 255, 255),
                        anchor="mm", align="center")
