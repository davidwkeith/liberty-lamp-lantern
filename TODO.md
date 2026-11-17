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

## Gather sources (blocks six bird stencils)

- [ ] **Download the 9 Fuertes plates.** Wikimedia blocks the script's downloads (HTTP 429). For each one, open the page, click **Original file**, and save the image into `stencils/sources/` under the name shown. Then run `make stencils`.

  | Save as | Commons page | Birds |
  |---------|--------------|-------|
  | `fuertes-106.jpg` | [Plate 106](https://commons.wikimedia.org/wiki/File:Birds_of_New_York_(Plate_106)_(7047595507).jpg) | Robin (CT), Bluebird (NY) |
  | `fuertes-101.jpg` | [Plate 101](https://commons.wikimedia.org/wiki/File:Birds_of_New_York_(Plate_101)_(7047594233).jpg) | Brown Thrasher (GA) |
  | `fuertes-78.jpg` | [Plate 78](https://commons.wikimedia.org/wiki/File:Birds_of_New_York_(Plate_78)_(7047588521).jpg) | Goldfinch (NJ) |
  | `fuertes-79.jpg` | [Plate 79](https://commons.wikimedia.org/wiki/File:Birds_of_New_York_(Plate_79)_(7047588733).jpg) | Goldfinch (NJ), alternate |
  | `fuertes-41.jpg` | [Plate 41](https://commons.wikimedia.org/wiki/File:Birds_of_New_York_(Plate_41)_(6815756200).jpg) | Ruffed Grouse (PA) |
  | `fuertes-102.jpg` | [Plate 102](https://commons.wikimedia.org/wiki/File:Birds_of_New_York_(Plate_102)_(7047594497).jpg) | Wrens: Carolina Wren (SC), if it's on the plate |
  | `fuertes-75.jpg` | [Plate 75](https://commons.wikimedia.org/wiki/File:Birds_of_New_York_(Plate_75)_(7047587833).jpg) | Baltimore Oriole (MD), alternate |
  | `fuertes-103.jpg` | [Plate 103](https://commons.wikimedia.org/wiki/File:Birds_of_New_York_(Plate_103)_(6901498002).jpg) | Chickadee (MA), alternate |
  | `fuertes-76.jpg` | [Plate 76](https://commons.wikimedia.org/wiki/File:Birds_of_New_York_(Plate_76)_(6901491228).jpg) | Purple Finch (NH), alternate |

  The first five matter most. The last three are only alternates for stencils that are already done.
- [ ] **Hens (DE, RI):** if you know of a public-domain illustration of a Blue Hen game fowl or a Rhode Island Red, drop it in `stencils/sources/` and tell Claude. Otherwise Claude will keep searching.

## Build and test

- [ ] Test-print one body and one roof in **ASA**. Check:
  - panel slot fit (adjust `panel_clearance` if needed)
  - that the heat-set inserts go in cleanly
  - that the roof seats on all four standoffs
  - that the cord threads through the post and elbow
- [x] OK installing KiCad (`brew install --cask kicad`) when the PCB work starts.
