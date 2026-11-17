"""Bird stencil pipeline: trace → compose → check → export → preview.

Usage (from repo root, via `make stencils`):
    stencils/.venv/bin/python -I stencils/gen/stencil.py [bird ...]

Inputs:  stencils/hints/<bird>.json, stencils/sources/<file>
Outputs: stencils/out/<bird>-cut.svg, <bird>-cut.dxf, <bird>-mask.png,
         <bird>-<colony>-preview.png
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402
from check import PX, PANEL, WINDOW, art_box  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HINTS, SOURCES, OUT = ROOT / "hints", ROOT / "sources", ROOT / "out"

# Palette (docs/spec.md §5): colony → (dark field, light glow)
PALETTE = {
    "CT": ("#4A5D7A", "#E8DFC8"), "DE": ("#5C7A82", "#C2A572"), "GA": ("#3D5068", "#8B4A3D"),
    "MD": ("#2B2620", "#B8860B"), "MA": ("#3D4A68", "#B8873A"), "NH": ("#3D5068", "#C08A2E"),
    "NJ": ("#4A6B82", "#C2A572"), "NY": ("#3D4F68", "#E8DFC8"), "NC": ("#3D5068", "#C08A2E"),
    "PA": ("#3D5068", "#C08A2E"), "RI": ("#3D5068", "#E8DFC8"), "SC": ("#2E3A52", "#E8DFC8"),
    "VA": ("#35465C", "#E8DFC8"),
}

GROUND_Y = WINDOW[3] - 25.0  # perch centerline, mm from panel top (same on all 12)


def mm(v: float) -> int:
    return int(round(v * PX))


# ------------------------------------------------------------------ trace

def trace(h: dict) -> np.ndarray:
    """GrabCut the chosen bird out of its plate → tight bool mask (True = bird)."""
    img = cv2.imread(str(SOURCES / h["source"]), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(h["source"])
    x, y, w, hgt = h["rect"]
    pad = 40
    X0, Y0 = max(0, x - pad), max(0, y - pad)
    img = img[Y0:y + hgt + pad, X0:x + w + pad]   # work on the rect + a background ring
    x, y = x - X0, y - Y0
    seeds = np.zeros(img.shape[:2], np.uint8)       # 1 = fg seed, 2 = bg seed
    for px, py, r in h.get("fg", []):
        cv2.circle(seeds, (px - X0, py - Y0), r, 1, -1)
    for px, py, r in h.get("bg", []):
        cv2.circle(seeds, (px - X0, py - Y0), r, 2, -1)
    ring = np.ones(img.shape[:2], bool)
    ring[y:y + hgt, x:x + w] = False
    seeds[ring] = 2

    # Seeded color model: Lab histograms of the fg/bg seeds → per-pixel bird probability
    # (histogram ratio / back-projection).
    lab = cv2.cvtColor(cv2.GaussianBlur(img, (5, 5), 0), cv2.COLOR_BGR2LAB)
    q = (lab // 16).astype(np.int32)                       # 16 bins per channel
    idx = (q[..., 0] * 16 + q[..., 1]) * 16 + q[..., 2]
    fg_h = np.bincount(idx[seeds == 1], minlength=4096).astype(np.float32)
    bg_h = np.bincount(idx[seeds == 2], minlength=4096).astype(np.float32)
    fg_h /= max(fg_h.sum(), 1)
    bg_h /= max(bg_h.sum(), 1)
    prob = (fg_h / (fg_h + bg_h + 1e-6))[idx]
    prob = cv2.GaussianBlur(prob, (0, 0), 3)
    mask = np.where(prob > h.get("prob", 0.6), cv2.GC_PR_FGD, cv2.GC_PR_BGD).astype(np.uint8)
    mask[seeds == 1] = cv2.GC_FGD
    mask[seeds == 2] = cv2.GC_BGD
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(img, mask, None, bgd, fgd, h.get("iters", 5), cv2.GC_INIT_WITH_MASK)
    bird = np.isin(mask, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8)
    # keep the largest blob, smooth, fill small holes (noise), keep real gaps
    n, lab, stats, _ = cv2.connectedComponentsWithStats(bird, connectivity=8)
    if n > 1:
        bird = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    k = max(3, int(min(w, hgt) * h.get("smooth", 0.012)) | 1)
    bird = cv2.morphologyEx(bird, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    bird = cv2.morphologyEx(bird, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    inv = (1 - bird).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    min_hole = h.get("min_hole_frac", 0.002) * bird.sum()
    for i in range(1, n):
        x0, y0, ww, hh, a = stats[i]
        touches_edge = x0 == 0 or y0 == 0 or x0 + ww == inv.shape[1] or y0 + hh == inv.shape[0]
        if not touches_edge and a < min_hole:
            bird[lab == i] = 1
    ys, xs = np.nonzero(bird)
    crop = bird[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(bool)
    if h.get("flip"):
        crop = crop[:, ::-1]
    return crop


# ------------------------------------------------------------------ perches

def _poly(canvas, pts_mm):
    cv2.fillPoly(canvas, [np.array([[mm(x), mm(y)] for x, y in pts_mm], np.int32)], 1)


def _band(canvas, path, w0, w1):
    """Tapered band along a polyline of mm points, width w0 → w1."""
    left, right = [], []
    for i, (x, y) in enumerate(path):
        a = path[min(i + 1, len(path) - 1)]
        b = path[max(i - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = (w0 + (w1 - w0) * i / (len(path) - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    _poly(canvas, left + right[::-1])


def perch(kind: str, twig_at: float = 0.84, twig_lean: float = -3.0) -> np.ndarray:
    c = np.zeros((mm(PANEL[1]), mm(PANEL[0])), np.uint8)
    x0, _, x1, _ = art_box()
    g = GROUND_Y
    if kind == "branch":
        # gentle S-curve, thick at the left (trunk side), tapering right, one up-curving twig
        pts = [(x0 + 2 + t * (x1 - x0 - 6), g + 2.2 * math.sin(t * math.pi * 1.6) - 1.5 * t) for t in np.linspace(0, 1, 40)]
        _band(c, pts, 5.0, 1.6)
        bx_ = x0 + 2 + twig_at * (x1 - x0 - 6)
        by_ = g + 2.2 * math.sin(twig_at * math.pi * 1.6) - 1.5 * twig_at
        tw = [(bx_ + twig_lean * t, by_ - 1.0 - 10 * t + 2 * t * t) for t in np.linspace(0, 1, 15)]
        _band(c, tw, 2.2, 1.2)
        # two Arts & Crafts leaves on the twig tip
        for ang, ln in ((-35, 7.0), (25, 6.0)):
            tip = tw[-1]
            a = math.radians(ang - 90)
            ex, ey = tip[0] + ln * math.cos(a), tip[1] + ln * math.sin(a)
            leaf = []
            for t in np.linspace(0, 1, 16):
                bx, by = tip[0] + (ex - tip[0]) * t, tip[1] + (ey - tip[1]) * t
                wv = 1.6 * math.sin(math.pi * t)
                leaf.append((bx - wv * math.sin(a), by + wv * math.cos(a)))
            for t in np.linspace(1, 0, 16):
                bx, by = tip[0] + (ex - tip[0]) * t, tip[1] + (ey - tip[1]) * t
                wv = 1.6 * math.sin(math.pi * t)
                leaf.append((bx + wv * math.sin(a), by - wv * math.cos(a)))
            _poly(c, leaf)
    elif kind == "log":
        pts = [(x0 + 4 + t * (x1 - x0 - 8), g + 0.6 * math.sin(t * math.pi)) for t in np.linspace(0, 1, 30)]
        _band(c, pts, 8.0, 7.0)
        cv2.circle(c, (mm(x1 - 4), mm(g)), mm(3.6), 1, -1)   # rounded cut end
        cv2.circle(c, (mm(x0 + 4), mm(g)), mm(3.9), 1, -1)
    elif kind == "fence":
        _poly(c, [(x0 + 2, g - 2.2), (x1 - 2, g - 2.6), (x1 - 2, g + 2.0), (x0 + 2, g + 2.4)])     # top rail
        _poly(c, [(x0 + 2, g + 11.0), (x1 - 2, g + 10.6), (x1 - 2, g + 14.0), (x0 + 2, g + 14.4)])  # lower rail
        for px_ in (x0 + 8, x1 - 10):  # posts
            _poly(c, [(px_, g - 5), (px_ + 5, g - 5.6), (px_ + 5, g + 18), (px_, g + 18)])
    else:
        raise ValueError(kind)
    return c.astype(bool)


# ------------------------------------------------------------------ compose

def compose(h: dict, bird: np.ndarray) -> np.ndarray:
    """Place the bird on its perch inside the panel; returns cut mask (True = cut)."""
    cut = perch(h["perch"], h.get("twig_at", 0.84), h.get("twig_lean", -3.0)).astype(np.uint8)
    hmm_ = h["height_mm"]
    scale = mm(hmm_) / bird.shape[0]
    b = cv2.resize(bird.astype(np.uint8), (max(1, int(bird.shape[1] * scale)), mm(hmm_)), interpolation=cv2.INTER_AREA)
    if h.get("rotate"):
        M = cv2.getRotationMatrix2D((b.shape[1] / 2, b.shape[0] / 2), h["rotate"], 1.0)
        b = cv2.warpAffine(b, M, (b.shape[1], b.shape[0]))
    x0, _, x1, _ = art_box()
    cx = (x0 + x1) / 2 + h.get("x_mm", 0.0)
    # feet_frac: where the feet are, as a fraction of the bird's height from its top. The feet
    # sit on the perch top; a long tail may hang below it, as in the plates.
    feet = GROUND_Y - h.get("perch_half_mm", 2.0)
    top = mm(feet - hmm_ * h.get("feet_frac", 1.0))
    left = mm(cx) - b.shape[1] // 2
    cut[top:top + b.shape[0], left:left + b.shape[1]] |= b
    cut = cut.astype(bool)
    # manufacturability fixes: drop metal islands (eye etc.) unless bridged, then bridges, then
    # erase sub-1 mm slivers of both kinds
    for x_a, y_a, x_b, y_b in h.get("bridges", []):
        cv2.line(cut.view(np.uint8), (mm(x_a), mm(y_a)), (mm(x_b), mm(y_b)), 0, mm(1.1))
    metal = (~cut).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(metal, connectivity=4)
    if n > 2:
        field = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        cut = lab != field
    d = mm(check.MIN_FEATURE) | 1
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d + 2, d + 2))
    c8 = cut.astype(np.uint8)
    c8 = cv2.morphologyEx(c8, cv2.MORPH_OPEN, k)   # remove thin cuts
    c8 = cv2.morphologyEx(c8, cv2.MORPH_CLOSE, k)  # remove thin metal
    cut = c8.astype(bool)
    metal = (~cut).astype(np.uint8)  # closing can re-isolate metal; drop again
    n, lab, stats, _ = cv2.connectedComponentsWithStats(metal, connectivity=4)
    if n > 2:
        field = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        cut = lab != field
    return cut


# ------------------------------------------------------------------ export

def export(name: str, cut: np.ndarray):
    """potrace the cut mask → SVG + DXF in mm, plus the panel outline."""
    pbm = OUT / f"{name}.pbm"
    hgt, wid = cut.shape
    with open(pbm, "wb") as f:
        f.write(f"P4\n{wid} {hgt}\n".encode())
        f.write(np.packbits(cut, axis=1).tobytes())
    dims = ["-W", f"{PANEL[0]}mm", "-H", f"{PANEL[1]}mm", "--alphamax", "1.0", "--opttolerance", "0.2", "--turdsize", "20"]
    svg, dxf = OUT / f"{name}-cut.svg", OUT / f"{name}-cut.dxf"
    subprocess.run(["potrace", "-b", "svg", *dims, "-o", str(svg), str(pbm)], check=True)
    subprocess.run(["potrace", "-b", "dxf", *dims, "-o", str(dxf), str(pbm)], check=True)
    pbm.unlink()
    s = svg.read_text()
    outline = (f'<rect x="0" y="0" width="{PANEL[0]}" height="{PANEL[1]}" fill="none" stroke="#ff0000" '
               f'stroke-width="0.1" id="panel-outline"/>')
    # potrace's viewBox is in pt; draw the outline in a mm-scaled group
    s = s.replace("</svg>", f'<g transform="scale({72 / 25.4})">{outline}</g>\n</svg>')
    svg.write_text(s)


# ------------------------------------------------------------------ preview

def _hex(c: str) -> np.ndarray:
    return np.array([int(c[i:i + 2], 16) for i in (5, 3, 1)], np.float32)  # BGR


def preview(name: str, colony: str, cut: np.ndarray) -> Path:
    dark, light = PALETTE[colony]
    s = 0.5  # 10 px/mm
    c = cv2.resize(cut.astype(np.uint8), None, fx=s, fy=s, interpolation=cv2.INTER_AREA).astype(np.float32)
    glow_col = _hex(light) * 0.75 + np.array([60, 150, 255], np.float32) * 0.25  # warm candle shift
    halo = cv2.GaussianBlur(c, (0, 0), 6) * 0.35
    img = np.ones((*c.shape, 3), np.float32) * _hex(dark) * 0.55
    img = img * (1 - c[..., None]) + glow_col * c[..., None]
    img = np.clip(img + halo[..., None] * glow_col * (1 - c[..., None]), 0, 255)
    # frame occlusion: shade what the posts / rail / base hide
    x0, y0, x1, y1 = (int(v * PX * s) for v in WINDOW)
    shade = np.ones(c.shape, np.float32) * 0.35
    shade[y0:y1, x0:x1] = 1.0
    img *= shade[..., None]
    out = OUT / f"{name}-{colony}-preview.png"
    cv2.imwrite(str(out), img.astype(np.uint8))
    return out


# ------------------------------------------------------------------ main

def build(name: str) -> list[str]:
    h = json.loads((HINTS / f"{name}.json").read_text())
    bird = trace(h)
    cv2.imwrite(str(OUT / f"{name}-mask.png"), bird.astype(np.uint8) * 255)
    cut = compose(h, bird)
    probs = check.problems(cut)
    export(name, cut)
    for col in h["colonies"]:
        preview(name, col, cut)
    return probs


def main(argv):
    OUT.mkdir(exist_ok=True)
    names = argv or sorted(p.stem for p in HINTS.glob("*.json"))
    failed = False
    for n in names:
        probs = build(n)
        print(f"{'FAIL' if probs else 'OK  '} {n}" + "".join(f"\n     {p}" for p in probs))
        failed |= bool(probs)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
