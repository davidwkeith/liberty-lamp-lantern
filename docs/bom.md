# Bill of Materials

Covers all 13 Liberty Lamp lanterns plus their distribution wiring.

Sources:
- [lantern frame design](superpowers/specs/2026-11-16-lantern-frame-design.md)
- [power & wiring design](superpowers/specs/2026-11-16-power-wiring-design.md)

Spares: +2 for printed parts, panels and connectors; +10% (rounded up) for fasteners and splices. `TBD (survey)` means the number waits on the tree survey in [TODO.md](../TODO.md). Those lengths are deliberately not guessed.

## Printed parts

Estimates come from PrusaSlicer: 0.2 mm layers, 3 perimeters, 20% gyroid infill, PETG at 1.27 g/cm³, no supports.

| Item | Spec | Per lantern | ×13 (+spares) | Notes |
|------|------|-------------|---------------|-------|
| Body | `build/stl/body.stl` | 1 | 15 | ~180 g, ~17 h 40 m each |
| Roof | `build/stl/roof.stl` | 1 | 15 | ~68 g, ~5 h 50 m each |
| Filament | PETG or ASA, 1.75 mm | ~248 g | ~3.7 kg → **4 × 1 kg spools** | Buy one color lot for all 13 so they match |

The total print time is about **306 h** for 13 lanterns, or about 353 h with spares.

## Frame hardware

| Item | Spec | Per lantern | ×13 (+spares) | Notes |
|------|------|-------------|---------------|-------|
| Heat-set insert | M3, ≤ 6 mm long, for a 4.2 mm hole | 2 | 29 | Hole is 8 mm deep |
| Screw | M3×10 socket head, A4 (316) stainless | 2 | 29 | Down through the roof wells |
| Well plug | Dab of outdoor sealant, or a printed plug | 2 | — | Keeps rain out of the screw wells |
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
| Trunk cable | 14/2 low-voltage landscape cable, UV-resistant, direct burial | — | TBD (survey) | 2–3 runs, base to limb splice points |
| Drop cable | Same 2 × 20 AWG cable as the lantern cord | TBD (survey) | 13 × TBD (survey) | Limb splice to the SP13 female |
| Limb splice | Gel-filled direct-burial connector (3M DBR/Y-6 or Wago 221 in a gel box) | 1 | 13 + 1 per trunk, +10% | One per drop at the trunk's limb splice |
| Base junction | Wago 221 lever connector | — | 1 per trunk + 1 spare | At the Cube's output, in the existing enclosure |
| Cable gland | Sized for 14/2, IP68 | — | 1 per trunk + 1 for the feed | Through the enclosure wall; keep drain paths |

## Hanging

| Item | Spec | Per lantern | ×13 (+spares) | Notes |
|------|------|-------------|---------------|-------|
| Sling | 25 mm (1") polyester webbing, sewn loop or girth-hitched | 1 | 15 | Padded, loose over the limb |
| Quick link | 316 stainless, ~5 mm | 1 | 15 | Sling to chain |
| Chain | 316 stainless, short | TBD (survey) | 13 × TBD (survey) | Quick link to the roof eye |
| Tree ties | Soft rubber-coated twist tie, bulk roll | — | 1 roll | Limbs about every 40 cm; padded loops at the trunk crotches only |

## Candle PCB

| Item | Spec | Per lantern | ×13 (+spares) | Notes |
|------|------|-------------|---------------|-------|
| Candle PCB assembly | Custom: 10–16 V AC/DC input, MCU flame, ≤ 1 W | 1 | 15+ | **Placeholder.** Waits on the Cube measurement; see the PCB sub-project |

## Already installed (nothing to buy)

| Item | Notes |
|------|-------|
| FX Luminaire Luxor controller + transformer | The cedar's own dimmable group |
| FX Luxor Cube (LV) | At the base of the tree; 60 W / 5 A max. The load is ≤ 13 W |
| Outdoor project enclosure | Becomes the base junction box |
