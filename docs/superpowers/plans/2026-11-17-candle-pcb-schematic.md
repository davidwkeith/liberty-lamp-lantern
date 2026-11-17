# Candle PCB Schematic — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Native KiCad schematics for the candle driver board and the LED disc. They're generated from a script, pass KiCad's electrical rules check (ERC), and are exported as PDFs for review.

**Architecture:**
- `pcb/gen/` holds a dependency-free Python generator. A small library builds `.kicad_sch` S-expressions: it embeds the symbols it uses from KiCad's installed libraries, places parts on a grid, and connects them by **net labels at pin endpoints**, with no hand-routed wires.
- Each board has a declarative netlist module listing references, symbols, values, footprints and nets.
- `make pcb` regenerates the schematics, runs `kicad-cli sch erc`, and exports PDFs.
- The generated files are committed, so the user can open and edit them in KiCad.

**Tech Stack:** KiCad 9 (`kicad-cli`), Python 3 (stdlib only), GNU make.

**Spec:** `docs/superpowers/specs/2026-11-17-candle-pcb-design.md`

## Global Constraints

- The circuit matches the design doc's "Circuit (driver board)" block exactly:
  - references F1, D1–D8, RT1, C1–C9, U1–U5, L1–L3, Rs1–Rs3, R1–R3, J1, J2
  - pin functions as listed (PB0–PB2 → CTRL1–3, PA7 SENSE, PA5 NTC, PA0 UPDI)
- Rows marked ⏳ (C1's value, the R1/R2 ratio) carry their provisional values, with a `⏳` field in the symbol.
- Every symbol has a footprint and MPN/spec fields that agree with `docs/bom.md`.
- Custom symbols go in a project library (`pcb/lib/liberty.kicad_sym`) only when the KiCad library lacks the part. The AL8860 is likely one.
- Generated files must open in KiCad 9 without "rescue" prompts.

## Review Focus

1. **Pin numbering of custom symbols:** an AL8860 symbol with wrong pin numbers would sail through ERC and kill the board. Verify against the datasheet pinout: 1 LX, 2 GND, 3 CTRL, 4 ISENSE, 5 VIN (TSOT-25). Task 2 asserts this.
2. **Label-only connections:** a label one grid step off a pin silently fails to connect. Task 1's test checks every pin of every placed symbol is either labeled or marked no-connect, and ERC must report 0 unconnected pins.
3. **Power flags:** ERC fails on "power input not driven" for nets fed through diodes or regulators unless they're flagged. Task 2 places PWR_FLAGs on VBUS, VHOLD, +5V and GND.
4. **Polarity:** electrolytic, TVS and Schottky orientation. Task 2's netlist test asserts the anode and cathode nets for D2–D7 and C1/C2.
5. **BOM drift:** symbol values and footprints must match `docs/bom.md`. Task 3 cross-checks them.

---

### Task 1: Generator library + test

**Files:** `pcb/gen/kisch.py`, `pcb/gen/test_kisch.py`

**Interfaces:**
- Produces:
  - `Sheet(title)`
  - `.add(ref, lib_id, value, footprint, at, rot=0, fields={})`, returning a `Part`
  - `.connect(ref, pin, net)`
  - `.no_connect(ref, pin)`
  - `.write(path)`
  - `load_symbol(lib_id) -> SExpr` (from the KiCad library dir, with the project library as fallback)
  - `pin_endpoints(part) -> {pin_number: (x, y)}`

- [ ] **Step 1: Write tests** (`python3 -m unittest`):
  - `test_pin_endpoint_transform`: a Device:R at (100, 100) rotated 90° puts its pin endpoints at the expected coordinates.
  - `test_unconnected_pin_detected`: `Sheet.check()` raises when a pin has neither a label nor a no-connect.
  - `test_roundtrip_opens`: the written file parses with `kicad-cli sch export netlist` (skip if kicad-cli is absent).
- [ ] **Step 2:** Run them and expect FAIL (module missing).
- [ ] **Step 3: Implement `kisch.py`** with a minimal S-expression parser and serializer, symbol embedding, the rotation transform, and labels placed at pin endpoints.
- [ ] **Step 4:** Run them and expect PASS.

### Task 2: Driver board + LED disc schematics

**Files:** `pcb/candle-driver/` (`netlist.py`, generated `.kicad_pro`, `.kicad_sch`), `pcb/led-disc/` (same), `pcb/lib/liberty.kicad_sym`, `pcb/gen/test_boards.py`, `Makefile` (`pcb` target)

- [ ] **Step 1: Write tests:**
  - `test_al8860_pinout`: the 1–5 pin mapping above.
  - `test_driver_nets`: spot-check against the design doc:
    - Rs1 between VBUS and LED1+
    - D2–D5 form a bridge (AC1/AC2 → VRAW/GND)
    - D7 is common-cathode onto VSENSE
    - U2 PB0 → CTRL1, PA7 → SENSE
    - J2 has 8 pins in the documented order
  - `test_disc_nets`: 3 strings × 2 LEDs, NTC on J pins 7–8.
- [ ] **Step 2:** Run them and expect FAIL.
- [ ] **Step 3:** Write both netlist modules, plus a custom AL8860 symbol if `Driver_LED` lacks it.
- [ ] **Step 4:** Run `make pcb`. Expected: the tests pass, and `kicad-cli sch erc` reports **0 errors** for both boards. Review any warnings, and record the ones accepted.
- [ ] **Step 5:** Commit `feat(pcb): candle driver + LED disc schematics`.

### Task 3: PDFs, BOM cross-check, docs

- [ ] **Step 1:** Run `make pcb`, which exports `pcb/*/…-schematic.pdf`. Commit the PDFs, so they can be reviewed on GitHub.
- [ ] **Step 2:** Run `kicad-cli sch export bom` for both boards and compare the values and footprints with `docs/bom.md`. Fix whichever side is wrong.
- [ ] **Step 3:** Add a PCB section to the README: how to regenerate, where the PDFs live, and the ⏳ items. Commit and push.
