# TODO — David

Things only you can do: measurements, decisions, and physical checks. Claude's work is tracked in `docs/`.

## Measure (blocks the candle PCB)

- [ ] **Luxor Cube output.** Set the cedar's zone to 100%, then 50%, then 10%. At each level, use the multimeter on the Cube's output leads, with nothing connected (or with a known load), to record:
  - AC volts
  - DC volts
  - Hz and duty %, if your meter has them

  | Level | V AC | V DC | Hz | Duty % |
  |-------|------|------|----|--------|
  | 100% |  |  |  |  |
  | 50%  |  |  |  |  |
  | 10%  |  |  |  |  |

- [ ] **Luxor transformer tap** for the cedar's run: 12, 13, 14, or 15 V? **Use 15 V if possible.** At 4 W per lantern, 13 lanterns need 4.3 A at 12 V, against the Cube's 5 A limit.
- [ ] **Base enclosure:** the inside dimensions, and a photo showing the Cube and the incoming wire. Only needed if the ESP32 fallback is used.

## Survey the tree

- [ ] Pick the 13 hanging spots. Group them by major limb, which sets how many trunk runs there are (target 2–3).
- [ ] Estimate the cable length from the base to each limb's splice point, and from there to each lantern.

## Decide

- [ ] **Panel numbering order:** ratification order (DE = 1 … RI = 13), or the alphabetical order the spec's table uses now?
- [ ] **North Carolina and Virginia both use the Northern Cardinal.** Keep the same silhouette, or vary the pose?
- [ ] **Panel material:** etched acrylic, printed mica-style film, or something else? This sets `panel_thickness`.

## Build and test

- [ ] Test-print one body and one roof in **ASA**. Check:
  - panel slot fit (adjust `panel_clearance` if needed)
  - that the heat-set inserts go in cleanly
  - that the roof seats on all four standoffs
  - that the cord threads through the post and elbow
- [ ] OK installing KiCad (`brew install --cask kicad`) when the PCB work starts.
