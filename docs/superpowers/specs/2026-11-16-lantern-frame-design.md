# Lantern Frame — STL Build Design

Date: 2026-11-16 · Parent spec: [docs/spec.md](../../spec.md)

## Intent

Set up this repo to generate the printable STLs for the 13 identical Liberty Lamp lantern frames. Panels (the per-colony element) come later; the frame only needs slots sized for them. Everything is parametric so open decisions (LED module, panel material) are one-number changes.

## Goals / non-goals

- **Goals:** one parametric source of truth; `make` produces all STLs + preview renders; parts fit a ~250 mm bed and print without supports where possible; outdoor-durable (PETG/ASA).
- **Non-goals (for now):** colony panels, bird silhouettes, numbering order, electronics, base-of-tree enclosure.
- **Anti-goals:** per-colony frame variants (all 13 frames are identical); anything that needs a GUI CAD tool to regenerate.

## Approaches

1. **OpenSCAD** — *chosen.* Already installed, plain-text parametric, scriptable export, git-friendly. Weak fillets don't matter for a square Craftsman form.
2. CadQuery/build123d — better fillets + STEP, but a Python env for little gain.
3. GUI CAD (Fusion etc.) — most visual, poor versioning/parametrics.

## Decided

- Size: **small**, ~4" (102 mm) square × ~8" (203 mm) overall.
- Tool: OpenSCAD.
- Scope: frame only, panels later.

## Design (my calls — correct any)

**Parts (2 STLs per lantern, ×13):**

1. **Body** — base floor + 4 corner posts + top and bottom rails, printed upright as one piece.
   - Posts 10 mm square; vertical grooves on the inner faces hold the 4 panels, which drop in from the top.
   - Panel slot: `panel_thickness` (default 3.0 mm, acrylic) + 0.3 mm clearance, 4 mm deep. A bottom groove in the base locates the panels.
   - Craftsman detailing: deeper bottom rail and a slight base flare/plinth; simple stepped top rail.
   - Base floor: centered candle cup (`led_d` default 38 mm, `led_h` 10 mm, adjustable), wire hole, 4 drain holes.
   - One post is hollow (5 mm channel) as the cord path from roof to candle cup.
2. **Roof** — a ~45° hipped pyramid with eave overhang, raised on short standoffs so there's a vent gap above the top rail. A hanging eye/loop sits at the peak, and the cord enters there and drops into the hollow post.
   - It attaches with 2 × M3 screws into heat-set inserts in two posts, so it's removable for panel swaps but stays put in wind.

**Build:**

- `src/lantern.scad`: all parameters at the top, with `part = "body" | "roof" | "assembly"`.
- A `Makefile` with `make` → `build/stl/{body,roof}.stl` + `build/png/*.png` previews, and `make clean`. `build/` is gitignored.
- `scripts/check-stl.mjs` (Node, no deps): confirms each STL exported, isn't empty, and fits within the bed size (default 250 mm).
- README: how to build, parameter table, print settings (PETG/ASA, 0.2 mm layers, 3 walls, 13× each part).

## Left to the builder

Exact rail profiles and proportions within the overall envelope; tolerance tuning after a test print.

## Open (not blocking)

LED module dims, panel material/thickness, hanging hardware — all exposed as parameters.
