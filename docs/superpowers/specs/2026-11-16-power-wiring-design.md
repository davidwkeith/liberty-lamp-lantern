# Power & Wiring — Design

Date: 2026-11-16 · Parent spec: [docs/spec.md](../../spec.md) · Related: [lantern frame](2026-11-16-lantern-frame-design.md)

## Intent

Power 13 lanterns that stay up year-round in the heritage Deodar cedar in the front yard, from the existing FX Luminaire Luxor system. Dimming from the Luxor app and Home Assistant should carry through to the lanterns. The wiring and hanging hardware must not harm the tree.

This is the first of four sub-projects:

1. power & wiring (this doc)
2. candle PCB
3. firmware
4. combined BOM

This doc also sets the electrical requirements the candle PCB has to meet.

## Goals / non-goals / anti-goals

- **Goals:**
  - Luxor on/off, scheduling and dimming control all 13 lanterns as one group.
  - Any single lantern can be taken down without cutting wire.
  - Everything is rated for permanent outdoor exposure: UV, rain, and temperature.
- **Non-goals:**
  - Controlling lanterns individually from Luxor or Home Assistant. Each lantern flickers on its own, but brightness is set for the whole group.
  - Line-voltage (120 V) work.
- **Anti-goals:**
  - Anything fastened into the tree: nails, screws, lag eyes.
  - Ties that could girdle a limb as it grows.
  - Cable carrying a lantern's weight.
  - Visible cable bundles running up the trunk.

## Existing conditions

- An FX Luminaire Luxor controller runs the cedar's zone. Home Assistant already controls on/off and brightness.
- A low-voltage run from the Luxor transformer ends at the base of the tree. There it feeds an **FX Luxor Cube (LV)** and an empty outdoor project enclosure.
- **Only the lanterns are on this Cube and Luxor group.** Their dimming is independent of every other fixture, and the planned Cube measurement reflects the real load.
- The cedar is **not** a legally designated heritage tree, so no permit or arborist sign-off is needed. "Heritage" here describes its age (about 100 years).
- All hanging spots are within reach of the owner's tall ladder. No lift or climber is needed.
- **Cube facts, from FX documentation:**
  - Output tracks the input, at up to 15 V AC.
  - Max load is 60 W / 5 A, and only dimmable loads should be connected.
  - It's potted and rated for direct burial.
  - The **dimming method isn't published**, so it will be measured; see the open items.

## Approaches

1. **Cube → dimmed AC to each lantern; each board reads its own dim level from its supply.** *Chosen.* Native Luxor and Home Assistant dimming, no converter at the base, and the per-lantern independence the spec asks for. Cost: the candle board has to handle the Cube's unknown output waveform.
2. Central AC-to-DC at the base, with an ESP32 pulsing the DC line to dim it and a Home Assistant automation mirroring the Luxor brightness. It keeps DC distribution, but adds a controller and a sync that can drift. **This is the agreed fallback if the Cube's waveform proves unusable.** The cabling is the same under either approach, so it can go in before the measurement. Fitting out the base enclosure waits until after it.
3. No dimming: brightness is fixed in firmware, and the Cube only switches power. Simplest, but it loses something the owner asked for.

**This changes the parent spec:** §3 "12V DC distributed" becomes 12–15 V AC (Luxor-dimmed) distributed. §4's conversion from AC to DC moves into each lantern. The base enclosure becomes the junction box.

## Design

### Load budget

| Item | Value |
|------|-------|
| Per-lantern draw (PCB requirement) | ≤ 1 W |
| 13 lanterns | ≤ 13 W, ≤ ~1.1 A at 12 V |
| Cube capacity | 60 W / 5 A, so ≥ 4× headroom |
| Worst-case drop, 14 AWG, 30 ft run (60 ft round trip, 0.15 Ω) at 1.1 A | ≈ 0.17 V |

### Topology

```
Luxor xfmr ──(existing run)── Cube ── base enclosure (junction)
                                         ├── trunk A (14/2) ── limb splice ──┬─ drop ─ SP13 ─ lantern
                                         │                                   └─ drop ─ SP13 ─ lantern …
                                         ├── trunk B (14/2) ── limb splice ── …
                                         └── trunk C (14/2, if needed) ── …
```

- There are **2–3 trunk runs**, grouped by major limb once the tree survey is done.
- Each trunk ends at a **limb splice point** where the lantern drops branch off.
- **Every lantern has its own drop**, ending in a waterproof connector. There's no daisy-chaining through lanterns, so one lantern coming down never cuts power to another.

### Parts (my calls — correct any)

| Role | Part | Notes |
|------|------|-------|
| Trunk cable | 14/2 low-voltage cable with a round jacket, UV-resistant and direct-burial | Round (not flat zip-cord) so the glands seal. Dark jacket, run up the shaded side of the trunk |
| Lantern drop / cord | 2 × 20 AWG (0.5 mm²) round outdoor cable, UV and oil resistant (PUR or SJOOW-type), about 5 mm OD | The same cable runs inside the lantern to the PCB |
| Lantern connector | SP13 IP68 2-pin, inline male on the lantern cord and female on the drop | Keyed, screw-locking, rated for 5 A. Sits on a short (~30 cm) pigtail at the lantern, not up at the limb, so whoever can reach a lantern can unplug it |
| Limb splices | Gel-filled direct-burial connectors (e.g. 3M DBR/Y-6 or a Wago 221 in a gel box) | Two per drop (one per conductor) at each splice point |
| Base junction | Wago 221 lever connectors inside the existing enclosure; glands or grommets on the cable entries | The enclosure must keep drip and drain paths |
| Hanging | 25 mm (1") polyester webbing sling in a **basket hitch** over the limb (both ends to the quick link; never girth-hitched, which cinches); a 316 stainless quick link; a short length of 316 chain to the roof eye | Pads the bark and spreads the load, with no hardware in the wood |
| Cable dressing, limbs | Soft rubber-coated twist ties, loose, about every 40 cm | Retied each year as the tree grows |
| Cable dressing, trunk | **No ties around the trunk.** The cables lie in the bark furrows on the shaded side and are held only at limb crotches by padded, loose loops | Let out each year; my call to meet the girdling and visibility anti-goals |

### Lantern cord routing

- The cord leaves the roof beside the hanging eye and goes to the SP13 connector on its short pigtail. The drop then runs up the chain to the limb, with a **drip loop** below the connector so water can't follow it into the lantern.
- It gets a strain-relief tie at the eye, so pulling on the cord never loads the PCB joints.
- Inside the lantern, it follows the existing path down the hollow post, through the elbow, and into the candle cup.
- **Model change:** set `cord_d` from 4.5 to the chosen cable's OD + 0.5 mm. That's about 5.5 mm, still inside the post limit of 6.6 mm.

### Electrical requirements handed to the candle PCB

- **Input:** 10–16 V, either AC or DC, non-polarized (bridge rectifier on board), from the Cube's output whatever its dimming waveform.
- **Power:** ≤ 1 W steady.
- **Inrush:** limit it with an NTC or soft-start, so 13 boards switching on together stay well inside what the Cube tolerates.
- **Dimming:** the board works out its brightness from its supply (voltage level, duty cycle or phase angle; TBD by measurement). It keeps a hold-up capacitor so the MCU rides through the Cube's chopping without resetting, and it maps the Luxor's 0–100% onto the flame's brightness.
- **Protection:** a TVS diode on the input against surges on the long outdoor runs, and a conformal coating.
- **Connection:** solder pads or a small terminal for the 2 × 20 AWG cord, sized to fit the candle cup.

## Open items (owner tasks in [TODO.md](../../../TODO.md))

- The Cube's output at 100/50/10%. This blocks the PCB's input and dim-sensing design.
- The Luxor tap voltage for this run.
- The base enclosure's dimensions. These only matter if the ESP32 fallback is needed.
- The tree survey: the 13 hanging spots grouped by limb, and the cable lengths, which give the number of trunks and the total cable to buy.

## Left to the builder

The exact SKUs, colors and lengths of cable, which wait on the survey. Splice-point placement on each limb.
