# Bird Stencils — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (owner's standing choice: Native). Steps use checkbox (`- [ ]`) syntax.

**Goal:** `make stencils` produces 12 checked, cut-ready bird stencil SVGs, plus glow previews.

**Architecture:** Python scripts in `stencils/gen/`, run in a repo-local venv (`stencils/.venv`, gitignored), using OpenCV, numpy and the potrace CLI. Per-bird inputs live in `stencils/hints/*.json`; sources go in `stencils/sources/`, with `sources.json` recording each URL and license.

**Tech Stack:** Python 3, opencv-python-headless, numpy, potrace, Homebrew.

**Spec:** `docs/superpowers/specs/2026-11-17-bird-stencils-design.md`

## Global Constraints

- Panel outline: 83.4 × 113.7 mm. Art box: 70 × 85 mm, centered in the ≈ 78 × 95 mm visible window.
- The metal is one connected region. Minimum feature is 1.0 mm for both metal and cut-outs. Bridges are 1.0–1.2 mm.
- Sources are public domain only, with the URL and license recorded. Downloads go in `stencils/sources/` and are run only through `python -I`.

## Review Focus

1. **Islands:** the checker must flag any metal that isn't connected to the field.
2. **Thin features:** the checker must catch a 0.6 mm sliver, in metal or in a cut-out.
3. **Art box overflow:** the checker must flag anything outside the art box.
4. **Species legibility:** the silhouettes are judged from previews, which the owner reviews.

---

### Task 1: Tooling and checker (TDD)

- [ ] **Step 1:** Install potrace, create the venv, and gitignore it.
- [ ] **Step 2:** Write `test_check.py`, with synthetic panels for: a valid panel; an island; a 0.6 mm metal sliver; a 0.6 mm cut-out sliver; a cut outside the art box. Run it and expect FAIL.
- [ ] **Step 3:** Implement `check.py`: rasterize the cut SVG's paths at 20 px/mm, then use connected components plus a morphological open/close at 0.5 mm radius. Run it and expect PASS.

### Task 2: Source plates

- [ ] **Step 1:** Find Wikimedia Commons scans (public domain) of the 10 Audubon plates and 2 PD poultry illustrations, and record them in `sources.json`.
- [ ] **Step 2:** Download them to `stencils/sources/` at ≤ 3000 px on the long side, checking the type and size.

### Task 3: Trace → compose → preview (one bird end to end, then all)

- [ ] **Step 1:** Write `trace.py` (GrabCut from the hints → mask cleanup → potrace → normalized SVG), `compose.py` (pose plus the shared perch plus the panel outline, bridges from the hints), and `preview.py` (palette glow).
- [ ] **Step 2:** Do the cardinal end to end, then review the preview for legibility and fix the hints until it reads well.
- [ ] **Step 3:** Do the remaining 11. `make stencils` must pass every check.
- [ ] **Step 4:** Send the owner a contact sheet of all 12 previews. Commit and push.
