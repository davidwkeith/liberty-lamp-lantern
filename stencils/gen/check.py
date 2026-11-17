"""Manufacturability checks for a bird stencil, on a raster mask.

Mask convention: bool array at PX px/mm, origin at the panel's top-left
(top = the edge hidden under the top rail). True = cut away (glows),
False = metal.
"""

from __future__ import annotations

import cv2
import numpy as np

PX = 20                      # px per mm
PANEL = (83.4, 113.7)        # panel w × h, mm (lantern.scad echo)
WINDOW = (2.7, 16.2, 80.7, 111.7)  # visible window x0, y0, x1, y1 (posts, base groove, rail+haunch)
ART = (70.0, 85.0)           # art box w × h, centered in WINDOW
MIN_FEATURE = 1.0            # mm, metal and cut
THIN_AREA = 0.5              # mm²: residue smaller than this is corner rounding, not a feature


def panel_canvas() -> np.ndarray:
    return np.zeros((round(PANEL[1] * PX), round(PANEL[0] * PX)), dtype=bool)


def art_box() -> tuple[float, float, float, float]:
    cx = (WINDOW[0] + WINDOW[2]) / 2
    cy = (WINDOW[1] + WINDOW[3]) / 2
    return (cx - ART[0] / 2, cy - ART[1] / 2, cx + ART[0] / 2, cy + ART[1] / 2)


def _thin(region: np.ndarray) -> list[float]:
    """Areas (mm²) of features narrower than MIN_FEATURE in a binary region."""
    d = int(round(MIN_FEATURE * PX)) | 1  # odd, so the opening is centered (even kernels shift 1 px)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d, d))
    r8 = region.astype(np.uint8)
    opened = cv2.morphologyEx(r8, cv2.MORPH_OPEN, k)
    residue = (r8 & (1 - opened)).astype(np.uint8)
    n, _, stats, _ = cv2.connectedComponentsWithStats(residue, connectivity=8)
    areas = [stats[i, cv2.CC_STAT_AREA] / PX**2 for i in range(1, n)]
    return [a for a in areas if a > THIN_AREA]


def problems(cut: np.ndarray) -> list[str]:
    out = []
    metal = (~cut).astype(np.uint8)
    n, _ = cv2.connectedComponents(metal, connectivity=4)
    if n - 1 != 1:
        out.append(f"metal island(s): {n - 2} piece(s) not attached to the field — bridge or drop them")
    for a in _thin(~cut):
        out.append(f"thin metal: {a:.1f} mm² narrower than {MIN_FEATURE} mm")
    for a in _thin(cut):
        out.append(f"thin cut: {a:.1f} mm² narrower than {MIN_FEATURE} mm")
    x0, y0, x1, y1 = (round(v * PX) for v in art_box())
    outside = cut.copy()
    outside[y0:y1, x0:x1] = False
    if outside.any():
        out.append(f"cut outside the art box: {outside.sum() / PX**2:.1f} mm²")
    return out
