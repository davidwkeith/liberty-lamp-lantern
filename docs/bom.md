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
| Panel | 83.4 × 113.7 × 3 mm; material TBD | 4 | 54 | One per lantern carries the colony's art |

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

## Candle PCB

| Item | Spec | Per lantern | ×13 (+spares) | Notes |
|------|------|-------------|---------------|-------|
| Candle PCB assembly | Custom: 10–16 V AC/DC input, MCU flame, designed for 4 W peak, firmware cap 3 W default, aluminum-core or heat-spreading LED section | 1 | 15+ | **Placeholder.** Waits on the Cube measurement; see the PCB sub-project |

## Already installed (nothing to buy)

| Item | Notes |
|------|-------|
| FX Luminaire Luxor controller + transformer | The cedar's own dimmable group |
| FX Luxor Cube (LV) | At the base of the tree; 60 W / 5 A max. The load is ≤ 13 W |
| Outdoor project enclosure | Becomes the base junction box |
