# Liberty Lamp Lantern

Printable frame for 13 Craftsman-style hanging lanterns, one per original colony. See the [design spec](docs/spec.md).

![Assembled lantern preview](docs/assembly.png)

## Build

Prereqs: [OpenSCAD](https://openscad.org) (`brew install openscad`) and Node 20+. There are no npm dependencies.

```bash
make            # STLs → build/stl, validate, previews → build/png
make test       # checker unit tests + geometry tests (renders the model)
make clean
make BED=220    # validate against a smaller print bed
```

`make` fails if any part is empty, non-manifold, or larger than the bed. It also fails if parameters conflict: for example, a candle cup wider than the interior, panel grooves that leave too little post between them, or a screw longer than its insert hole.

`make test` also renders the model to check that the roof bears on all four standoffs and that the body has no unsupported overhangs.

To try a different parameter without editing the file:

```bash
openscad -D 'part="body"' -D panel_thickness=2 -o body.stl src/lantern.scad
```

Open `src/lantern.scad` in the OpenSCAD app for a live preview. Set `part` to `"assembly"` to see the whole lantern with stand-in panels.

## Parts (per lantern; print 13 of each)

| Part | Size (mm) | Orientation |
|------|-----------|-------------|
| `body.stl` | 108 × 108 × 134 | upright, base on bed |
| `roof.stl` | 114 × 114 × 54 | peak up, open side on bed |

Assembled height is about 219 mm to the top of the eye bolt (about 194 mm to the roof peak). Neither part needs supports.

## Key parameters

All of these live at the top of [`src/lantern.scad`](src/lantern.scad).

| Parameter | Default | Notes |
|-----------|---------|-------|
| `W` | 102 | body width across the posts |
| `post_w` | 12 | corner post size |
| `panel_h` | 100 | visible panel height |
| `panel_thickness` | 3.0 | set to match the chosen panel material |
| `panel_clearance` | 0.3 | tune after a test print |
| `slot_depth` | 3 | how far panel edges sit into the posts |
| `panel_skin` | 3 | post wall outside each panel |
| `led_d` / `led_h` | 38 / 10 | candle cup; set once the LED module is chosen |
| `cord_od` / `cord_d` | 5.0 / 5.5 | lantern cord OD and its channel (channel ≥ OD + 0.5) |
| `standoff_h` | 6 | vent gap under the roof |
| `insert_d` / `insert_depth` | 4.2 / 8 | M3 heat-set insert hole |

The panel size is computed from these and printed during each build:

```
ECHO: "PANEL (w × h × t): 83.4 × 113.7 × 3 mm, qty 4"
```

## Print settings

- PETG or ASA (it hangs outdoors; avoid PLA)
- 0.2 mm layers, 3 walls, 20% gyroid infill

## Bill of materials

All parts, hardware, cable and hanging gear, per lantern and ×13, are in [docs/bom.md](docs/bom.md). Per lantern, the frame takes 2 M3 heat-set inserts, 2 M3×10 screws, 4 panels (83.4 × 113.7 mm), and a black stainless M6 × 40 eye bolt with its nuts and washers.

## Assembly

1. Feed the lantern cord into the opening in the outer corner of the +X/+Y post, just below the top-rail band. That opening slopes down and outward, so rain drains out of it. Inside, the cord runs down the hollow post, round a 45° elbow, and through the base tunnel into the candle cup. The roof has no cord openings. Outside, let the cord hang in a drip loop **below** the opening before it rises to its connector.
2. Drop the 4 panels in through the slits in the top rail.
3. Fit the eye bolt **before** the roof goes on. From the top, stack the eye bolt, an M6 nut, and a bonded sealing washer on the cap. Underneath the roof, add an M6 × 18 fender washer and a nyloc nut on the seat. Tighten until the sealing washer just compresses.
4. Set the roof on the standoffs (its corner ledges sit on them) and screw it down. The lantern hangs from the eye bolt, so the roof screws carry its weight.

The roof screw wells are open on top; a dab of sealant or a printed plug keeps rain out.

Wiring and hanging the lanterns in the tree, plus the yearly maintenance checklist, are covered in [docs/install.md](docs/install.md).

## Layout

```
src/lantern.scad          parametric model (body, roof, assembly)
scripts/check-stl.mjs     STL validator (empty / non-manifold / bed size / overhang area)
scripts/*.test.mjs        checker unit tests + OpenSCAD geometry tests
docs/spec.md              project spec
docs/superpowers/         design + implementation plan
build/                    generated (gitignored)
```
