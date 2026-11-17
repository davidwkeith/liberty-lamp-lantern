# Liberty Lamp Tree Lantern — Design Spec

**Project:** 13 Craftsman-style lanterns, one per original colony, hung in the heritage Deodar cedar in the front yard
**Inspiration:** Lanterns at Disneyland's Grand Californian Hotel

## 1. Concept

Thirteen matching Craftsman-style hanging lanterns ("Liberty lamps"), each representing one of the original 13 colonies. Each lantern carries a state-bird silhouette on its insert panel, rendered in a muted Arts & Crafts palette drawn from that colony's flag colors — not the bright official hues, but desaturated slate-blue / antique-gold / brick-red / bone / charcoal tones consistent with mica-and-copper Craftsman fixtures.

## 2. Housing

- Single candle per lantern (not a 3-up cluster)
- Acrylic/mica-style insert panels (not a pierced-shell design)
- One insert panel per lantern bears the colony name, number (1–13, Continental Congress signing order), and bird silhouette
- FDM-printed frame/housing; insert panels are the swappable/etched element

## 3. Electronics

- Per-lantern flicker IC (not a central flicker controller) — each lantern is independently driven
- New candle/LED module sourced for this build (not reusing the existing flicker-candle module)
- Luxor-dimmed 12–15 V AC (via the FX Luxor Cube) distributed to all 13 lanterns; each lantern's board rectifies its own supply and reads the dim level from it. See [power & wiring design](superpowers/specs/2026-11-16-power-wiring-design.md)

## 4. Power

- Source: existing FX Luminaire Luxor low-voltage landscape lighting circuit
- A line from the Luxor controller already runs to the base of the tree, terminating in an empty off-the-shelf outdoor project enclosure
- An FX Luxor Cube at the base of the tree gives the lanterns their own dimmable Luxor group; the enclosure is the junction box for 2–3 trunk runs (AC–DC conversion happens per lantern, not centrally; fallback: central DC + ESP32 dimming)
- Longest run: base enclosure → farthest lantern position = 30 ft (sizes wire gauge / voltage drop budget)

## 5. Colony Table — Bird & Color Key

| # | Colony | Bird | Muted Craftsman Palette |
|---|--------|------|--------------------------|
| 1 | Connecticut | American Robin | slate blue `#4A5D7A` / bone `#E8DFC8` |
| 2 | Delaware | Delaware Blue Hen | soft colonial blue `#5C7A82` / antique buff `#C2A572` |
| 3 | Georgia | Brown Thrasher | brick red `#8B4A3D` / slate blue `#3D5068` |
| 4 | Maryland | Baltimore Oriole | oxide red `#8B3A3F` / antique gold `#B8860B` / charcoal `#2B2620` |
| 5 | Massachusetts | Black-capped Chickadee | slate blue `#3D4A68` / antique gold `#B8873A` |
| 6 | New Hampshire | Purple Finch | slate blue `#3D5068` / ochre `#C08A2E` |
| 7 | New Jersey | American Goldfinch | antique buff `#C2A572` / slate blue `#4A6B82` |
| 8 | New York | Eastern Bluebird | slate blue `#3D4F68` / bone `#E8DFC8` |
| 9 | North Carolina | Northern Cardinal | brick red `#8B3A3D` / slate blue `#3D5068` / antique gold `#C08A2E` |
| 10 | Pennsylvania | Ruffed Grouse *(state game bird — PA has no official state bird)* | slate blue `#3D5068` / ochre `#C08A2E` |
| 11 | Rhode Island | Rhode Island Red | bone `#E8DFC8` / antique gold `#C2962E` / slate blue `#3D5068` |
| 12 | South Carolina | Carolina Wren | deep indigo-slate `#2E3A52` / bone `#E8DFC8` |
| 13 | Virginia | Northern Cardinal | slate blue `#35465C` / bone `#E8DFC8` |

Each state's palette is a desaturated, warmed-down derivative of its actual flag colors (sourced from flagcolorcodes.com), keeping the identity legible while fitting the overall amber/slate/bronze Craftsman look rather than reading as flags.

## 6. Open / Not Yet Decided

- Insert panel fabrication method (etched acrylic vs. printed mica-style film vs. other) — not finalized
- Exact candle/LED module part — decided: custom MCU candle PCB (design pending Cube measurements)
- Mounting hardware for hanging in the tree
- Wire gauge for the 30 ft run — decided: 14/2 trunks, 2×20 AWG drops (see power & wiring design)
