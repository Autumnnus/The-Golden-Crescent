"""provinces.png uzerinden cografi hesaplamalar.

Uretilenler (hepsi `build/geo.npz` icinde onbelleklenir):
  - her province'in piksel sayisi, agirlik merkezi ve sinir kutusu
  - province komsuluk grafigi (haritanin dogu-bati sarmasi dikkate alinir)
  - state komsuluk grafigi (hangi state hangi state'e sinir)

Bunlar olmadan "Suriye'ye komsu state'ler hangileri" ya da "bu bolgeyi haritada
nereye ciz" sorularini cevaplayamayiz.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from . import index as index_mod
from . import paths

Image.MAX_IMAGE_PIXELS = None


def province_hex_to_int(token: str) -> int:
    """`x1A2B3C` / `1A2B3C` -> 0x1A2B3C"""
    token = token.strip().strip('"')
    if token[:1] in ("x", "X"):
        token = token[1:]
    return int(token, 16)


def province_int_to_hex(value: int) -> str:
    return f"x{value:06X}"


def load_province_image() -> np.ndarray:
    """provinces.png'yi (H, W) uint32 paketlenmis renk dizisi olarak yukler."""
    paths.check_vanilla_present()
    png = paths.vanilla("map_data", "provinces.png")
    with Image.open(png) as image:
        rgb = np.asarray(image.convert("RGB"), dtype=np.uint32)
    return (rgb[:, :, 0] << 16) | (rgb[:, :, 1] << 8) | rgb[:, :, 2]


def _wrap_x() -> bool:
    default_map = paths.vanilla("map_data", "default.map")
    if not default_map.exists():
        return True
    text = default_map.read_text(encoding="utf-8-sig", errors="replace")
    return "wrap_x = yes" in text


def build_geo(verbose: bool = True) -> dict[str, Any]:
    def log(message: str) -> None:
        if verbose:
            print(message)

    log("provinces.png yukleniyor (8192x3616)...")
    packed = load_province_image()
    height, width = packed.shape

    log("province istatistikleri hesaplaniyor...")
    codes, inverse = np.unique(packed, return_inverse=True)
    inverse = inverse.reshape(packed.shape)
    counts = np.bincount(inverse.ravel(), minlength=codes.size)

    ys, xs = np.mgrid[0:height, 0:width]
    sum_x = np.bincount(inverse.ravel(), weights=xs.ravel(), minlength=codes.size)
    sum_y = np.bincount(inverse.ravel(), weights=ys.ravel(), minlength=codes.size)
    centroid_x = sum_x / np.maximum(counts, 1)
    centroid_y = sum_y / np.maximum(counts, 1)

    min_x = np.full(codes.size, width, dtype=np.int32)
    max_x = np.zeros(codes.size, dtype=np.int32)
    min_y = np.full(codes.size, height, dtype=np.int32)
    max_y = np.zeros(codes.size, dtype=np.int32)
    np.minimum.at(min_x, inverse.ravel(), xs.ravel())
    np.maximum.at(max_x, inverse.ravel(), xs.ravel())
    np.minimum.at(min_y, inverse.ravel(), ys.ravel())
    np.maximum.at(max_y, inverse.ravel(), ys.ravel())
    del xs, ys

    log("komsuluk grafigi cikariliyor...")
    pairs: list[np.ndarray] = []

    # dikey komsuluk
    a = inverse[:-1, :].ravel()
    b = inverse[1:, :].ravel()
    pairs.append(np.stack([a, b], axis=1))
    # yatay komsuluk
    a = inverse[:, :-1].ravel()
    b = inverse[:, 1:].ravel()
    pairs.append(np.stack([a, b], axis=1))
    # harita dogu-bati sariyorsa son sutun ile ilk sutun da komsu
    if _wrap_x():
        pairs.append(np.stack([inverse[:, -1], inverse[:, 0]], axis=1))

    edges = np.concatenate(pairs, axis=0)
    edges = edges[edges[:, 0] != edges[:, 1]]
    edges = np.sort(edges, axis=1)
    edges = np.unique(edges, axis=0)
    del pairs, inverse

    geo = {
        "codes": codes.astype(np.uint32),
        "counts": counts.astype(np.int64),
        "centroid_x": centroid_x.astype(np.float32),
        "centroid_y": centroid_y.astype(np.float32),
        "min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y,
        "edges": edges.astype(np.int32),
        "size": np.array([width, height], dtype=np.int32),
    }

    paths.assert_safe_write(paths.GEO_FILE)
    paths.BUILD_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(paths.GEO_FILE, **geo)
    log(
        f"Geo yazildi: {paths.GEO_FILE.relative_to(paths.MOD_ROOT)}  "
        f"({codes.size} benzersiz province rengi, {edges.shape[0]} komsuluk)"
    )

    _write_state_adjacency(geo, verbose=verbose)
    return geo


_GEO_CACHE: dict[str, Any] | None = None


def load_geo(rebuild_if_missing: bool = True) -> dict[str, Any]:
    global _GEO_CACHE
    if _GEO_CACHE is not None:
        return _GEO_CACHE
    if not paths.GEO_FILE.exists():
        if not rebuild_if_missing:
            raise SystemExit("Geo onbellegi yok. Once: python tools/tgc.py geo")
        return build_geo(verbose=False)
    with np.load(paths.GEO_FILE) as data:
        _GEO_CACHE = {key: data[key] for key in data.files}
    return _GEO_CACHE


STATE_ADJACENCY_FILE = paths.BUILD_DIR / "state_adjacency.json"
STATE_GEOMETRY_FILE = paths.BUILD_DIR / "state_geometry.json"


def _write_state_adjacency(geo: dict[str, Any], verbose: bool = True) -> None:
    ix = index_mod.load_index()
    province_to_state = ix["province_to_state"]

    codes = geo["codes"]
    code_to_slot = {int(code): slot for slot, code in enumerate(codes)}
    slot_to_state: dict[int, str] = {}
    for hex_id, state_name in province_to_state.items():
        slot = code_to_slot.get(province_hex_to_int(hex_id))
        if slot is not None:
            slot_to_state[slot] = state_name

    adjacency: dict[str, set[str]] = {}
    for left, right in geo["edges"]:
        state_a = slot_to_state.get(int(left))
        state_b = slot_to_state.get(int(right))
        if state_a is None or state_b is None or state_a == state_b:
            continue
        adjacency.setdefault(state_a, set()).add(state_b)
        adjacency.setdefault(state_b, set()).add(state_a)

    # state basina geometri: piksel agirlikli merkez + sinir kutusu
    geometry: dict[str, dict[str, Any]] = {}
    counts = geo["counts"]
    cx, cy = geo["centroid_x"], geo["centroid_y"]
    min_x, max_x = geo["min_x"], geo["max_x"]
    min_y, max_y = geo["min_y"], geo["max_y"]

    for state_name, entry in ix["states"].items():
        slots = [code_to_slot.get(province_hex_to_int(p)) for p in entry["provinces"]]
        slots = [s for s in slots if s is not None]
        if not slots:
            continue
        weights = counts[slots].astype(np.float64)
        total = weights.sum()
        if total <= 0:
            continue
        geometry[state_name] = {
            "pixels": int(total),
            "center": [float((cx[slots] * weights).sum() / total),
                       float((cy[slots] * weights).sum() / total)],
            "bbox": [int(min_x[slots].min()), int(min_y[slots].min()),
                     int(max_x[slots].max()), int(max_y[slots].max())],
        }

    paths.assert_safe_write(STATE_ADJACENCY_FILE)
    STATE_ADJACENCY_FILE.write_text(
        json.dumps({k: sorted(v) for k, v in sorted(adjacency.items())}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    paths.assert_safe_write(STATE_GEOMETRY_FILE)
    STATE_GEOMETRY_FILE.write_text(
        json.dumps(geometry, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    if verbose:
        print(f"State komsulugu yazildi: {len(adjacency)} state")


def load_state_adjacency() -> dict[str, list[str]]:
    if not STATE_ADJACENCY_FILE.exists():
        build_geo(verbose=False)
    return json.loads(STATE_ADJACENCY_FILE.read_text(encoding="utf-8"))


def load_state_geometry() -> dict[str, dict[str, Any]]:
    if not STATE_GEOMETRY_FILE.exists():
        build_geo(verbose=False)
    return json.loads(STATE_GEOMETRY_FILE.read_text(encoding="utf-8"))
