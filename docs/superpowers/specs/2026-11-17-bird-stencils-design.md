# Bird Stencils — Design

Date: 2026-11-17 · Parent spec: [docs/spec.md §2](../../spec.md) · Frame: [lantern frame design](2026-11-16-lantern-frame-design.md)

## Intent

Twelve stencil artworks, one per unique colony bird (North Carolina and Virginia share the cardinal), laser-cut from 1 mm aluminum. Each bird is **cut out so it glows** amber or palette-tinted against a dark powder-coated field, perched in an Arts & Crafts scene. It's the Grand Californian lantern effect. All four panels on a lantern are identical.

## Goals / non-goals / anti-goals

- **Goals:**
  - Recognizable species silhouettes with real character.
  - A consistent set: the same scale feel, the same ground line, the same stylization.
  - Cut-ready files that pass automated manufacturability checks.
  - Glow previews in each colony's palette.
- **Non-goals:** text, numbers, color-filled artwork, or per-lantern variation.
- **Anti-goals:**
  - Any metal island that falls out when cut.
  - Features under 1 mm.
  - Artwork that reads as clip-art, or that intrudes on a panel edge hidden in the frame grooves.

## Decided

- **Composition:** each bird is posed on a shared, stylized element. The nine songbirds sit on **one shared branch**. The **ruffed grouse** stands on a **drumming log**. The **Delaware Blue Hen** and **Rhode Island Red** stand on a **split-rail fence**. All 12 keep the same ground-line height.
- **Source:** silhouettes are traced from **Audubon's *Birds of America*** (1827–38, public domain). The two hens come from **public-domain 19th-century poultry illustration** (e.g. Harrison Weir).

## Approaches (for isolating each bird from a busy plate)

1. **Semi-automatic: GrabCut + potrace + review** — *chosen.*
   - I set a bounding box, plus a few foreground and background hints, by looking at each plate.
   - OpenCV's GrabCut separates the bird.
   - potrace turns that into smooth curves.
   - I then simplify the result and pose it, with preview renders after each step.
   - Accurate and repeatable. The hints and parameters are saved in the repo, so it can be regenerated.
2. A neural background-removal model (rembg or SAM). It's a multi-GB install, and it tends to keep the plate's plants as part of the "subject".
3. Fully manual tracing by hand. It's the slowest, and it throws away Audubon's accuracy.

## Pipeline (`stencils/`)

```
sources/<bird>.jpg      public-domain plate scan (URL + license recorded in sources.json)
hints/<bird>.json       bbox + fg/bg hint strokes, the plate index, flip/scale/rotate, posing
gen/trace.py            GrabCut mask → cleanup → potrace → bird.svg (normalized)
gen/compose.py          bird + shared perch + panel outline → cut SVG
gen/check.py            manufacturability (below)
gen/preview.py          glow preview PNG in the colony palette
out/<bird>-cut.svg      cut file: panel outline + bird cut-out, mm units
out/<bird>-preview.png  glow preview
```

`make stencils` runs trace → compose → check → preview for all 12. Tests cover the checker on known-good and known-bad shapes.

**Tools:** potrace (`brew install potrace`), plus a repo-local Python venv with `opencv-python-headless` and `numpy`. I'll ask before installing anything.

## Panel geometry

| Item | Value |
|------|-------|
| Panel | 83.4 × 113.7 mm; the stencil outline matches |
| Visible window | ≈ 78 × 95 mm. The posts hide ~2.7 mm per side, the base groove 2 mm, the top rail and haunches ~14 mm at the top |
| Art box | **70 × 85 mm**, centered in the visible window, with a ≥ 4 mm margin to the hidden edges |
| Ground line | Same height on all 12 (the branch, log or fence rail centerline about 25 mm above the visible bottom) |

## Manufacturability checks (automated)

Run on a 20 px/mm raster of the cut file:

- **One piece of metal:** the field (metal) is a single connected region. Islands such as an eye or a leg gap fail unless bridged.
- **Minimum width ≥ 1.0 mm** for both the metal and the cut-outs. Erode and dilate by 0.5 mm, and the topology must not change.
- **Bridges** are about 1.0–1.2 mm wide, added at named points in the hints file. The preview shows them.
- **Nothing outside the art box** except the panel outline.

## Palette mapping (preview only; physical colors come from powder coat and film)

| Role | Source |
|------|--------|
| Metal field | The palette's darkest color |
| Glowing bird | The palette's lightest color, shown lit (warm-shifted) |

## Plate picks (to confirm while tracing)

| Bird | Colonies | Source |
|------|----------|--------|
| American Robin | CT | Audubon |
| Delaware Blue Hen | DE | PD poultry illustration (game-hen type) |
| Brown Thrasher | GA | Audubon |
| Baltimore Oriole | MD | Audubon |
| Black-capped Chickadee | MA | Audubon |
| Purple Finch | NH | Audubon |
| American Goldfinch | NJ | Audubon |
| Eastern Bluebird | NY | Audubon |
| Northern Cardinal | NC, VA | Audubon |
| Ruffed Grouse | PA | Audubon |
| Rhode Island Red | RI | PD poultry illustration |
| Carolina Wren | SC | Audubon |

## Left to the builder

- Exact plate scans and which bird on each plate.
- Each bird's pose (flipped to face the same way, or alternating).
- The branch, log and fence drawings, in the same Arts & Crafts line weight.
- Bridge placement.
