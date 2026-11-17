# Bill of Materials

Covers all 13 Liberty Lamp lanterns plus their distribution wiring.

Sources:
- [lantern frame design](superpowers/specs/2026-11-16-lantern-frame-design.md)
- [power & wiring design](superpowers/specs/2026-11-16-power-wiring-design.md)

Spares: +2 for printed parts, panels and connectors; +10% (rounded up) for fasteners and splices. `TBD (survey)` means the number waits on the tree survey in [TODO.md](../TODO.md). Those lengths are deliberately not guessed.

## Printed parts

Estimates come from PrusaSlicer: 0.2 mm layers, 3 perimeters, 20% gyroid infill, at PETG density (1.27 g/cm³), no supports. ASA is about 1.07 g/cm³, so the same spools go roughly 15% further.

| Item | Spec | Per lantern | ×13 (+spares) | Notes |
|------|------|-------------|---------------|-------|
| Body | `build/stl/body.stl` | 1 | 15 | ~180 g, ~17 h 40 m each |
| Roof | `build/stl/roof.stl` | 1 | 15 | ~69 g, ~6 h each |
| Filament | **ASA** (PETG only if candle-cup temperatures test ≤ 60 °C), 1.75 mm | ~248 g | ~3.7 kg → **5 × 1 kg spools** | One color lot for all 13 so they match; the 5th spool covers purge, test prints and failures |

The total print time is about **306 h** for 13 lanterns, or about 353 h with spares.

## Frame hardware

| Item | Spec | Per lantern | ×13 (+spares) | Notes |
|------|------|-------------|---------------|-------|
| Heat-set insert | M3, ≤ 6 mm long, for a 4.2 mm hole | 2 | 29 | Hole is 8 mm deep |
| Screw | M3×10 socket head, A4 (316) stainless | 2 | 29 | Down through the roof wells |
| Well plug | Outdoor sealant (one tube), or printed plugs | 2 | 1 tube, or 30 plugs | Keeps rain out of the screw wells |
| Eye bolt | M6 × 40 eye bolt (≥ 32 mm thread), **black** stainless (black-oxide or black-coated 316/304), eye ID ≥ 12 mm | 1 | 15 | Carries the lantern; metal takes the chain wear |
| Hex nut | M6, black stainless | 1 | 15 | On top of the cap, under the eye |
| Sealing washer | M6 bonded EPDM/stainless sealing washer | 1 | 15 | Under the top nut; seals the bolt hole |
| Fender washer | M6 × 18 × 1.6, stainless | 1 | 15 | Inside the roof, on the printed seat |
| Nyloc nut | M6, stainless | 1 | 15 | Inside the roof; reachable before the roof is screwed on |
| Panel stencil | ~1 mm aluminum, laser-cut bird cut-out, powder-coated in the colony's dark palette color | 4 | 54 | 83.4 × 113.7 mm; all 4 on a lantern identical; 12 unique artworks |
| Panel cover | 0.75 mm clear UV-stabilized polycarbonate | 8 | 108 | Front and back of each stack |
| Panel glow film | ~0.25 mm mica-look PET/polyester film, tinted to the colony's light palette color | 4 | 54 | Behind the stencil; not natural mica |
| Panel edge seal | Clear outdoor adhesive or clear tape | — | 1 roll/tube | Holds each 4-layer stack together |

## Lantern cord and connector

| Item | Spec | Per lantern | ×13 (+spares) | Notes |
|------|------|-------------|---------------|-------|
| Lantern cord | 2 × 20 AWG (0.5 mm²) round outdoor cable, UV and oil resistant (PUR or SJOOW-type), ~5 mm OD | ~0.5 m | ~7.5 m | Runs inside the lantern plus the ~30 cm pigtail. The model's `cord_od` is 5.0 |
| Connector, lantern side | SP13 IP68 2-pin inline **male** | 1 | 15 | On the pigtail |
| Connector, drop side | SP13 IP68 2-pin inline **female** | 1 | 15 | On the end of the drop |

## Distribution

| Item | Spec | Per lantern | ×13 (+spares) | Notes |
|------|------|-------------|---------------|-------|
| Trunk cable | 14/2 low-voltage cable with a **round jacket**, UV-resistant, direct burial | — | TBD (survey) | 2–3 runs, base to limb splice points. Round, not flat zip-cord, so the glands seal |
| Drop cable | Same 2 × 20 AWG cable as the lantern cord | TBD (survey) | 13 × TBD (survey), +10% | Limb splice, down the chain, to the SP13 female at the lantern |
| Limb splice | Gel-filled direct-burial connector, one conductor each (3M DBR/Y-6 or Wago 221 in a gel box) | 2 | 26, +10% → 29 | Two per drop, one per conductor, at the trunk's limb splice |
| Base junction | Wago 221 lever connector, with enough ports for every trunk plus the Cube lead (221-415 for up to 4 trunks) | — | 2 + 1 spare | One per Cube output conductor, in the existing enclosure |
| Cable gland | IP68, sized to the round 14/2 jacket (and to the existing feed cable) | — | 1 per trunk + 1 for the feed | Through the enclosure wall; keep drain paths |

## Hanging

| Item | Spec | Per lantern | ×13 (+spares) | Notes |
|------|------|-------------|---------------|-------|
| Sling | 25 mm (1") polyester webbing, sewn loop | 1 | 15 | Basket hitch over the limb, both ends to the quick link. Never girth-hitched |
| Quick link | 316 stainless, ~5 mm | 1 | 15 | Sling to chain |
| Chain | 316 stainless, short | TBD (survey) | 13 × TBD (survey), +1 m | Quick link to the eye bolt |
| Tree ties | Soft rubber-coated twist tie, bulk roll | — | 1 roll | Limbs about every 40 cm, plus padded limb loops at each crotch for the trunk cables. Never around the trunk |

## Candle PCB (provisional)

> **Provisional.** These parts come from the requirements in the [power & wiring design](superpowers/specs/2026-11-16-power-wiring-design.md). The schematic isn't drawn yet. Rows marked ⏳ depend on the Cube measurements in [TODO.md](../TODO.md). Where only a spec is given, the exact part gets chosen at the schematic stage. Quantities are per board; the build is **20 boards**: 13, plus 2 spares, plus 5 for the fab's minimum order and bring-up testing.

**Architecture:** two boards per lantern.
- A ~32 mm round **driver board** (FR4, 2-layer, factory-assembled) sits in the candle cup.
- A ~20 mm round **LED disc** (aluminum-core) on a short candle pillar carries the LEDs and spreads their ~3 W of heat away from the printed cup.
- Three independent LED channels let the firmware move the "flame" between them, rather than just flicker one point.

### Driver board

| Block | Part | Spec | Per board | ×20 | Notes |
|-------|------|------|-----------|-----|-------|
| Cord connection | Solder pads + strain-relief slot | 2 pads for 2 × 20 AWG | 1 set | — | Cord is tied through the board slot before soldering |
| Input fuse | Resettable PTC, 1812 | 1.1 A hold, ≥ 30 V rating | 1 | 20 | ~0.5–0.7 A RMS input per board; PTC hold current falls with heat in the cup |
| Surge protection | **SMBJ24CA** (bidirectional TVS) | 24 V standoff, SMB | 1 | 20 | Clamps at ~39 V, under the AL8860's 40 V maximum (don't use a 26 V part) |
| Rectifier | **SS36** Schottky ×4 | 60 V, 3 A, SMA | 4 | 80 | Surge margin above the TVS clamp (~39 V) |
| Inrush limit | 10 Ω 1 W 2512 resistor + **DMN6075S** N-MOSFET bypass | Gate RC 470 kΩ / 470 nF, 12 V zener clamp (MM3Z12), 1N4148WS gate discharge | 1 + 1 + 4 | 20 each | Low-side limiter; the FET shorts out the resistor ~30–50 ms after power-up. Replaces the NTC |
| Bulk capacitor ⏳ | Aluminum electrolytic, 105 °C long-life | 470 µF, 35 V | 1 | 20 | Value depends on the Cube's dimming waveform; use the smallest that holds up, to cut inrush |
| MCU hold-up | 47 Ω + BAT54WS + capacitor | 47 Ω 0603, BAT54WS (SOD-323), 100 µF / 35 V | 1 + 1 + 1 | 20 each | Isolated rail, so the MCU rides through supply chopping. The 47 Ω limits D6's surge current |
| MCU regulator | **78L05**, SOT-89 (e.g. MC78L05ACHT1G) | 5 V, ≥ 30 V input | 1 | 20 | ~3 mA quiescent; the MCU draws only a few mA |
| MCU | **ATtiny1614**-SSNR, SOIC-14 | megaTinyCore, UPDI | 1 | 20 | 3 PWM channels + ADC + analog comparator for dim sensing |
| Dim sense ⏳ | **BAV70** + divider + clamp | BAV70 (100 V, SOT-23), 100 kΩ / 18 kΩ, 5.1 V zener, 1 nF | 1 set | 20 | Reads the raw AC; values confirmed after measurement |
| LED drivers | **AL8860WT-7** buck LED driver, TSOT-25 | 40 V, 1 A, PWM dimming | 3 | 60 | One per channel |
| Driver inductors | Bourns **SRN6045TA-101M** | 100 µH, 6 × 6 mm | 3 | 60 | ~600 kHz switching (33 µH ran ~1.9 MHz) |
| Driver diodes | **SS36** Schottky | 60 V, 3 A, SMA | 3 | 60 | |
| Current sense | Resistor, 1%, 1206 | 0.51 Ω, giving ~196 mA per channel (AL8860: I = 0.1 V / R) | 3 | 60 | 3 ch × 2 LEDs × ~3.1 V × 0.196 A ≈ 3.65 W (≤ ~3.8 W worst case), so the hardware can't exceed 4 W. The firmware's 3 W default cap sits below that |
| CTRL pull-downs | Resistor 0603 | 4.7 kΩ | 3 | 60 | Keep LEDs off while the MCU is in reset or unflashed |
| UPDI protection | Resistor 0603 | 470 Ω | 1 | 20 | In series with the exposed UPDI pad |
| Passives | Decoupling and driver caps | 100 nF, 1 µF, 10 µF / 50 V X7R, plus 100 nF at each AL8860 VIN | ~13 | ~260 | |
| Programming | UPDI test pads | 3 pads (UPDI, 5 V, GND) | 1 set | — | Pogo-pin or clip programming |
| LED link | 6-pin header or pads | 3 channels × (+, −) | 1 | 20 | To the LED disc |

### LED disc

| Block | Part | Spec | Per board | ×20 | Notes |
|-------|------|------|-----------|-----|-------|
| PCB | Aluminum-core (MCPCB), 1-layer | ~20 mm round | 1 | 20 | Spreads the heat; mounts on the candle pillar |
| LEDs | Mid-power warm white | **2200 K**, CRI ≥ 90, 2835 (schematic footprint `LED_SMD:LED_PLCC_2835`; switch if a 3030 part is chosen), ~0.7–1 W class | 6 (3 ch × 2 in series) | 120 | Exact part chosen at layout for a warm "flame" color bin |

### Finishing, tools and fab

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Conformal coating | Acrylic, e.g. MG Chemicals 419D | 1 can | Coat both boards after programming and testing (leave the UPDI pads masked) |
| UPDI programmer | USB-serial adapter + 4.7 kΩ resistor (SerialUPDI), or an Adafruit UPDI Friend | 1 | Flashes all 20 boards |
| PCB fab + assembly | JLCPCB or similar: FR4 driver board + aluminum LED disc | 20 of each | Order after the schematic and layout are reviewed |

## Already installed (nothing to buy)

| Item | Notes |
|------|-------|
| FX Luminaire Luxor controller + transformer | The cedar's own dimmable group |
| FX Luxor Cube (LV) | At the base of the tree; 60 W / 5 A max. The load is ≤ 13 W |
| Outdoor project enclosure | Becomes the base junction box |
