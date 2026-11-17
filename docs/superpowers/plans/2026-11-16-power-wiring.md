# Power & Wiring — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the repo in line with the approved power and wiring design. The model's cord channel fits the chosen cable, and there's a BOM covering the frame plus power and wiring, plus an install and maintenance guide the owner can follow on a ladder.

**Architecture:** One parameter change in `src/lantern.scad`, guarded by an assert and a geometry test. Two new Markdown docs, `docs/bom.md` and `docs/install.md`, linked from the README. The PCB and firmware sections of the BOM stay as placeholders for their own sub-projects.

**Tech Stack:** OpenSCAD, Node `node:test`, Markdown.

**Spec:** `docs/superpowers/specs/2026-11-16-power-wiring-design.md` (with `docs/spec.md` and `docs/superpowers/specs/2026-11-16-lantern-frame-design.md`)

## Global Constraints

- Lantern drop and cord: 2 × 20 AWG round outdoor cable, about 5 mm OD. Trunks: 14/2 UV and direct-burial landscape cable. Connectors: SP13 IP68 2-pin, on a ~30 cm pigtail at the lantern.
- Hanging: 25 mm polyester webbing sling, 316 stainless quick link and chain. Nothing is fastened into the tree, and no ties go around the trunk.
- BOM quantities are given per lantern and ×13. Lengths that depend on the tree survey are marked `TBD (survey)` and never guessed.
- Commit with conventional commits, then push to `origin/main`.

## Review Focus

1. **Cable OD changes:** a different cable may need a bigger `cord_d`. The model must reject a channel too small for `cord_od`, which Task 1 tests.
2. **Post limit:** a bigger `cord_d` must still pass the existing post-wall assert (`cord_d + 2.4 ≤ half − slot_end` = 6.6 mm). Task 1's default build test covers this.
3. **BOM drift:** the README's hardware list and the BOM must agree. Task 2 replaces the README list with a link.
4. **Guessed lengths:** survey-dependent quantities must read `TBD (survey)`. Task 2's review step checks this.

---

### Task 1: Size the cord channel to the cable

**Files:** Modify `src/lantern.scad` and `scripts/geometry.test.mjs`

**Interfaces:**
- Produces: parameter `cord_od = 5.0` (the cable's OD; sets `cord_d`), with `cord_d = 5.5` by default. Assert message must contain `cord`.

- [ ] **Step 1: Add test** `rejects {"cord_d":5}` to the existing reject table in `scripts/geometry.test.mjs`, with message regex `/cord/`.
- [ ] **Step 2: Run** `node --test scripts/geometry.test.mjs`. Expected: the new test FAILS (it renders fine today).
- [ ] **Step 3: Add the parameter and assert.** Add `cord_od = 5.0;` under Candle / wiring, set `cord_d = 5.5`, and add `assert(cord_d >= cord_od + 0.5, "cord_d must be ≥ cord_od + 0.5 mm");`.
- [ ] **Step 4: Run** `make test && make`. Expected: all tests pass, and both STLs come out OK and manifold.
- [ ] **Step 5: Commit** `feat: size cord channel for 5 mm 2×20 AWG cable`.

### Task 2: BOM

**Files:** Create `docs/bom.md`; modify `README.md` (replace the "Hardware (per lantern)" section with a link to the BOM)

- [ ] **Step 1: Write `docs/bom.md`** with these sections. Each table has columns `Item | Spec | Per lantern | ×13 (+spares) | Notes`.
  - **Printed:** body, roof, PETG or ASA filament, with a gram estimate if the slicer gives one; otherwise `TBD (slice)`.
  - **Frame hardware:** M3 heat-set inserts (2), M3×10 socket-head screws (2), panels (4, 83.4 × 113.7 × 3 mm, material TBD).
  - **Lantern cord and connector:** about 0.5 m of 2 × 20 AWG cord inside the lantern plus the pigtail, an SP13 male, and an SP13 female on the drop.
  - **Distribution:**
    - 14/2 trunk cable: `TBD (survey)`
    - drop cable: 13 × `TBD (survey)`
    - gel splice connectors: one per drop, plus one per trunk at the limb
    - Wago 221: one per trunk, plus a spare
    - enclosure cable glands: one per trunk, plus one for the feed
  - **Hanging:** webbing sling, 316 quick link, and 316 chain (`TBD (survey)` length) for each lantern; rubber-coated twist ties as a bulk roll.
  - **Candle PCB:** a placeholder row pointing to the PCB sub-project.
  - **Already installed:** the Luxor controller and transformer, the Luxor Cube (LV), and the base enclosure, at quantity 0 to buy.

  Spares: +2 for printed parts, panels and connectors; +10% for fasteners.
- [ ] **Step 2: Review.** Run `grep -n "TBD" docs/bom.md`. Expected: every survey-dependent length shows `TBD (survey)`, and no length is invented.
- [ ] **Step 3: Commit** `docs: add bill of materials (frame + power & wiring)`.

### Task 3: Install and maintenance guide

**Files:** Create `docs/install.md`; modify `README.md` (link to it from the Assembly section)

- [ ] **Step 1: Write `docs/install.md`.** Sections, in order:
  1. Before you start: the Cube readings are recorded in TODO.md, the tree survey is done, and power is off at the Luxor.
  2. Base junction: trunks into the enclosure through glands, Wago 221 to the Cube output, drip loops.
  3. Trunk runs: shaded side, in the bark furrows, padded loose loops only at limb crotches.
  4. Limb splices: a gel connector per drop, ties about every 40 cm.
  5. Hanging a lantern:
     - sling and quick link
     - chain to the eye
     - plug in the SP13
     - drip loop below the connector
     - strain-relief tie at the eye
  6. Power-on check: all 13 light, and dimming 100% → 10% in the Luxor app tracks on every lantern.
  7. **Annual maintenance checklist:**
     - let out the trunk loops and limb ties
     - check the slings for UV wear
     - check that the SP13 seals are seated
     - check the roof screw-well plugs

  Use a ladder-safety note only where a step needs both hands.
- [ ] **Step 2: Review** the guide against the design doc's anti-goals: no fasteners in the wood, no ties around the trunk, cable never carrying load. Expected: every step complies.
- [ ] **Step 3: Commit** `docs: add install and annual maintenance guide`, then `git push`.
