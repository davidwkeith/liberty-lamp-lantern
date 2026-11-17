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

- [ ] **Luxor transformer tap** for the cedar's run: 12, 13, 14, or 15 V? Any tap is fine at the 3 W default. **Use 15 V (or 14 V) before raising the cap to 4 W.** At 4 W, 13 lanterns need 4.3 A at 12 V, against the Cube's 5 A limit.
- [ ] After the first lantern is lit in the tree, decide whether to keep the 3 W cap or raise it to 4 W.
- [ ] **Base enclosure:** the inside dimensions, and a photo showing the Cube and the incoming wire. Only needed if the ESP32 fallback is used.

## Survey the tree

- [ ] Pick the 13 hanging spots. Group them by major limb, which sets how many trunk runs there are (target 2–3).
- [ ] Estimate the cable length from the base to each limb's splice point, and from there to each lantern.

## Decide

- [ ] **Cube power budget.** A rectifier feeding a capacitor draws current in short peaks (a power factor of about 0.6), and the buck drivers are about 85% efficient. At the 3 W default cap, 13 lanterns come to about 46 W real and about 70 VA, against the Cube's 60 W rating. Options:
  - lower the default cap to about 2.5 W
  - split the lanterns across two Cubes on the same Luxor group
  - ask FX whether the 60 W is rated in VA, or measure the Cube's current with a test lantern

## Build and test

- [ ] Test-print one body and one roof in **ASA**. Check:
  - panel slot fit (adjust `panel_clearance` if needed)
  - that the heat-set inserts go in cleanly
  - that the roof seats on all four standoffs
  - that the cord threads through the post and elbow
- [ ] OK installing KiCad (`brew install --cask kicad`) when the PCB work starts.
