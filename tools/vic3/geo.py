"""Rasterise map_data/provinces.png into a per-pixel state map.

Everything map-shaped is derived from this cache: `tgc.py map`, label
placement, region cropping. It is expensive to build (a 8192x3616 image) and
never changes unless the game is patched, so it lives in build/ and is
git-ignored.

    python tools/tgc.py geo            build once, or after a Victoria 3 patch
"""

from __future__ import annotations

import json
import time

import numpy as np
from PIL import Image

from . import index as idx
from .paths import BUILD, vanilla

Image.MAX_IMAGE_PIXELS = None          # the map is far past Pillow's bomb guard

STATE_IDS = BUILD / "state_ids.npy"          # int16 per pixel, -1 = no state
GEO_META = BUILD / "geo.json"                # bbox / label anchor / area
ADJACENCY = BUILD / "state_adjacency.json"

NO_STATE = -1


def _province_key(rgb: tuple) -> str:
    return "x{:02X}{:02X}{:02X}".format(*rgb)


def is_current() -> bool:
    if not (STATE_IDS.exists() and GEO_META.exists()):
        return False
    src = vanilla("map_data", "provinces.png")
    return STATE_IDS.stat().st_mtime >= src.stat().st_mtime


def build_geo(force: bool = False, verbose: bool = True) -> dict:
    if is_current() and not force:
        if verbose:
            print("  geo cache is current (use --force to rebuild)")
        return json.loads(GEO_META.read_text(encoding="utf-8"))

    t0 = time.time()
    index = idx.load()
    order = sorted(index["states"])                  # stable state <-> int mapping
    state_of = {name: i for i, name in enumerate(order)}

    if verbose:
        print("  reading provinces.png ...", flush=True)
    img = np.asarray(Image.open(vanilla("map_data", "provinces.png")).convert("RGB"))
    h, w, _ = img.shape

    # Pack RGB into one 24-bit integer, then translate through a flat lookup
    # table. A dict lookup per pixel would take minutes; this takes seconds.
    if verbose:
        print(f"  {w}x{h} = {w * h / 1e6:.1f}M pixels, building lookup ...", flush=True)
    packed = (img[:, :, 0].astype(np.uint32) << 16
              | img[:, :, 1].astype(np.uint32) << 8
              | img[:, :, 2].astype(np.uint32))
    lut = np.full(1 << 24, NO_STATE, dtype=np.int16)
    unmapped = 0
    for province, state in index["province_state"].items():
        try:
            code = int(province[1:], 16)
        except ValueError:
            unmapped += 1
            continue
        lut[code] = state_of[state]
    state_ids = lut[packed]

    if verbose:
        print("  measuring states ...", flush=True)
    meta: dict = {}
    flat = state_ids.ravel()
    counts = np.bincount(flat[flat >= 0], minlength=len(order))
    ys, xs = np.nonzero(state_ids >= 0)
    vals = state_ids[ys, xs]
    order_idx = np.argsort(vals, kind="stable")
    vals, ys, xs = vals[order_idx], ys[order_idx], xs[order_idx]
    bounds = np.searchsorted(vals, np.arange(len(order) + 1))

    for i, name in enumerate(order):
        lo, hi = bounds[i], bounds[i + 1]
        if lo == hi:
            continue
        sy, sx = ys[lo:hi], xs[lo:hi]
        cy, cx = float(sy.mean()), float(sx.mean())
        # The centroid of a crescent-shaped state can fall outside it, so the
        # label anchor is the owned pixel nearest the centroid.
        step = max(1, (hi - lo) // 4000)
        py, px = sy[::step], sx[::step]
        j = int(np.argmin((py - cy) ** 2 + (px - cx) ** 2))
        meta[name] = {
            "index": i,
            "pixels": int(counts[i]),
            "bbox": [int(sx.min()), int(sy.min()), int(sx.max()), int(sy.max())],
            "centroid": [round(cx, 1), round(cy, 1)],
            "anchor": [int(px[j]), int(py[j])],
        }

    if verbose:
        print("  computing adjacency ...", flush=True)
    adj: dict = {name: set() for name in order}
    for a, b in ((state_ids[:, :-1], state_ids[:, 1:]),
                 (state_ids[:-1, :], state_ids[1:, :])):
        diff = (a != b) & (a >= 0) & (b >= 0)
        for u, v in np.unique(np.stack([a[diff], b[diff]], axis=1), axis=0):
            adj[order[u]].add(order[v])
            adj[order[v]].add(order[u])

    BUILD.mkdir(parents=True, exist_ok=True)
    np.save(STATE_IDS, state_ids)
    payload = {
        "meta": {"width": w, "height": h, "state_order": order,
                 "seconds": round(time.time() - t0, 1)},
        "states": meta,
    }
    GEO_META.write_text(json.dumps(payload), encoding="utf-8")
    ADJACENCY.write_text(json.dumps({k: sorted(v) for k, v in adj.items()}),
                         encoding="utf-8")
    if verbose:
        painted = int((state_ids >= 0).sum())
        print(f"\ngeo written: {STATE_IDS.name}, {GEO_META.name}, {ADJACENCY.name}")
        print(f"  {len(meta)} states rasterised, "
              f"{painted / (w * h) * 100:.1f}% of the map painted")
        if unmapped:
            print(f"  {unmapped} province id(s) were not hex and were skipped")
        print(f"  {payload['meta']['seconds']}s")
    return payload


def load():
    """(state_ids array, geo metadata dict), building the cache on first use."""
    if not is_current():
        build_geo(verbose=True)
    ids = np.load(STATE_IDS)
    meta = json.loads(GEO_META.read_text(encoding="utf-8"))
    return ids, meta
