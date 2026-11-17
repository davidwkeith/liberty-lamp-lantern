# Lantern Frame STL Build — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `make` turns one parametric OpenSCAD file into validated body and roof STLs, plus preview PNGs, for the Liberty Lamp lantern frame.

**Architecture:** `src/lantern.scad` holds every parameter and three modules (`body()`, `roof()`, `assembly()`), and a `part` variable selects which one renders. A Makefile calls the `openscad` CLI. `scripts/check-stl.mjs` is a dependency-free Node checker: it parses each STL and fails the build if the file is empty, non-manifold, or bigger than the bed.

**Tech Stack:** OpenSCAD (`/opt/homebrew/bin/openscad`), GNU make, Node 20+ (ES modules, `node:test`).

**Spec:** `docs/superpowers/specs/2026-11-16-lantern-frame-design.md` (parent: `docs/spec.md`)

## Global Constraints

- Overall envelope: ~102 mm square body × ~203 mm total height (4" × 8").
- All 13 frames identical: no per-colony geometry.
- Parts must fit a 250 mm bed (`BED ?= 250`), and slope ≥45° so they print without supports where possible.
- Defaults: `panel_thickness = 3.0`, `panel_clearance = 0.3`, `slot_depth = 4`, `post_w = 10`, `led_d = 38`, `led_h = 10`, `cord_d = 5`, M3 heat-set insert hole `insert_d = 4.2`, `insert_depth = 6`.
- No npm dependencies. ES modules only.
- `build/` is gitignored. The folder isn't a git repo, so commit steps are skipped unless the user runs `git init`.

## Review Focus

1. **Non-manifold geometry:** coincident faces from unions/differences can make a slicer choke. `check-stl` must flag any edge not shared by exactly 2 triangles (Task 1 test `flags non-manifold`).
2. **Oversized part:** a parameter change pushes a part past the bed size, so `check-stl` must fail on any bounding-box axis > bed (Task 1 test `flags oversize`).
3. **Silent export failure:** OpenSCAD errors can leave a 0-byte or missing file, which the build must reject (Task 1 test `flags empty`).
4. **Bad parameter combinations:** a slot deeper than the post, or a candle cup wider than the interior, should stop the build with a clear message. OpenSCAD `assert()` handles this, and Task 2 verifies it with `-D led_d=200`, which must exit non-zero.
5. **Binary vs ASCII STL:** the export format varies by OpenSCAD version, so the parser must handle both (Task 1 tests for each).

---

### Task 1: STL checker + build scaffold

**Files:**
- Create: `scripts/check-stl.mjs`, `scripts/check-stl.test.mjs`, `Makefile`, `.gitignore`, `src/lantern.scad` (stub: `part = "body"; cube(10);`)

**Interfaces:**
- Produces: `export function parseStl(buf: Buffer): { triangles: number[][][] }` (each triangle is 3 `[x,y,z]` vertices); `export function analyze(tris): { count, size: [x,y,z], nonManifoldEdges: number }`; CLI `node scripts/check-stl.mjs --bed <mm> <file...>` prints one line per file and exits 1 if any file fails.
- Make targets: `all` (default; stl + check + png), `stl`, `check`, `png`, `test`, `clean`. STLs go to `build/stl/{body,roof}.stl` and PNGs to `build/png/{body,roof,assembly}.png`. Until Task 3, `PARTS = body`.

- [ ] **Step 1: Write failing tests** in `scripts/check-stl.test.mjs` (`node:test`, `node:assert/strict`). Build fixtures in-test: an ASCII unit cube (12 facets) and the same cube as binary.
  - `parses ascii cube`: `analyze(parseStl(ascii)).count === 12`, `size` deep-equals `[1,1,1]`, `nonManifoldEdges === 0`.
  - `parses binary cube`: same assertions on the binary buffer.
  - `flags non-manifold`: cube minus one facet gives `nonManifoldEdges > 0`.
  - `flags oversize`: the CLI run via `execFileSync` on a 300 mm cube with `--bed 250` exits 1 and stderr mentions `exceeds bed`.
  - `flags empty`: the CLI on a 0-byte file exits 1, and stderr mentions `empty`.
- [ ] **Step 2: Run** `node --test scripts/` and expect FAIL (module not found).
- [ ] **Step 3: Implement `check-stl.mjs`.** Detect binary when `84 + 50*n === buf.length` (n is the uint32 at offset 80); otherwise parse ASCII `vertex` lines. For manifold checks, key each vertex by its coordinates rounded to 1e-4, then count undirected edges in a Map; any count ≠ 2 is a bad edge. Pass criteria are count > 0, nonManifoldEdges 0, and every size axis ≤ bed.
- [ ] **Step 4: Run** `node --test scripts/` and expect PASS.
- [ ] **Step 5: Makefile + .gitignore.** `OPENSCAD ?= openscad`; STL rule: `$(OPENSCAD) -o $@ -D 'part="$*"' --export-format binstl src/lantern.scad`; PNG rule: `--render --imgsize=800,800 --autocenter --viewall --colorscheme=Tomorrow`; `test: ; node --test scripts/`; `check: stl ; node scripts/check-stl.mjs --bed $(BED) $(STLS)`. Add `build/` and `.DS_Store` to `.gitignore`.
- [ ] **Step 6: Run** `make` and expect `build/stl/body.stl` checked OK (10 mm stub cube) and `build/png/body.png` to exist.

### Task 2: Body

**Files:** Modify `src/lantern.scad`

**Interfaces:**
- Consumes: the Task 1 Makefile (`part` variable).
- Produces: `module body()`; parameters `W=102, post_w, base_h=12, panel_h=116, top_rail_h=12, plinth=3` (base flare), `body_h = base_h + panel_h + top_rail_h` (=140), plus the defaults from Global Constraints. Derived `slot_w = panel_thickness + panel_clearance`. Two diagonal posts get `insert_d × insert_depth` holes in their top faces, and one post (+x,+y) gets a vertical `cord_d` channel that runs into the candle cup through a floor groove.

- [ ] **Step 1: Add asserts** at the top of the file: `assert(slot_depth < post_w - 2, "slot_depth must leave ≥2 mm of post")`, `assert(led_d < W - 2*post_w, "led_d larger than interior")`, `assert(insert_d < post_w - 3, "insert too large for post")`.
- [ ] **Step 2: Verify the asserts fire.** Run `openscad -o /tmp/x.stl -D led_d=200 src/lantern.scad` (use the scratchpad dir). Expect a non-zero exit and output containing `led_d larger than interior`.
- [ ] **Step 3: Implement `body()`.**
  - The base is a solid slab `W+2*plinth` wide at the bottom, stepping to `W`, with a centered candle cup (`led_d+0.4` × `led_h`), a 4× Ø4 drain hole pattern, and perimeter grooves (`slot_w` × 2 mm deep) inset to align with the post slots.
  - Corner posts span the full `body_h`. Each inner face gets a `slot_w`-wide, `slot_depth`-deep groove that's open at the top.
  - The top rail is a hollow square frame with an open center for panel insertion, and a small step for the Craftsman profile.
  - Overlap every union by 0.01 mm to avoid coincident faces.
- [ ] **Step 4: Run** `make` and expect `body.stl OK`, size ≈ `108 × 108 × 140`, `nonManifoldEdges 0`. Inspect `build/png/body.png`.

### Task 3: Roof + assembly

**Files:** Modify `src/lantern.scad`, `Makefile` (`PARTS = body roof`, add `assembly` to PNG only)

**Interfaces:**
- Consumes: `W`, `post_w`, insert hole positions, and cord post position from Task 2.
- Produces:
  - `module roof()`, printed peak-up. Parameters: `eave=6`, `standoff_h=6`, `roof_rise` (45° pitch from `W/2+eave`, so `roof_rise = W/2 + eave` = 57), `eye_od=16`, `eye_id=8`.
  - Geometry: a hollow pyramid (2.4 mm shell) over a `W+2*eave` footprint; 4 standoff pads `standoff_h` tall under the posts (the vent gap); M3 clearance holes (Ø3.4) with counterbores through the two insert-post pads; and a `cord_d` channel from the eye base down to the cord post pad.
  - The hanging eye is a ring at the peak, standing vertically. `module assembly()` places body plus roof at `z = body_h` with translucent stand-in panels.
- [ ] **Step 1: Implement `roof()` and `assembly()`.** Total assembled height must come to 196–210 mm.
- [ ] **Step 2: Run** `make` and expect both STLs to pass the check. The roof size should be ≈ `114 × 114 × ~70`. All three PNGs should exist. Inspect `assembly.png` for alignment of the posts and the cord path.

### Task 4: README

**Files:** Create `README.md`

- [ ] **Step 1: Write the README.** Cover:
  - The project in one line, with a link to `docs/spec.md`.
  - Prereqs: `brew install openscad`, Node 20+.
  - `make` / `make test` / `make clean`, and overriding with `make BED=220` or `-D` params.
  - A parameter table copied from the scad header.
  - Print settings: PETG or ASA, 0.2 mm layers, 3 walls, 20% gyroid. Print the body upright and the roof peak-up. Quantity is 13 of each part.
  - Hardware per lantern: 2× M3 heat-set inserts, 2× M3×10 screws.
- [ ] **Step 2: Run** `make clean && make` and expect a clean build from scratch.
