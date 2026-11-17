// Roof ∩ one standoff's footprint, 0.5 mm above the roof's underside.
// Non-empty ⇒ the roof bears on that standoff.
include <../../src/lantern.scad>
part = "none";
corner = 0;
s = slot_end + 0.5;
intersection() {
  roof();
  rotate(corner * 90) translate([s, s, -1]) cube([half - 0.5 - s, half - 0.5 - s, 1.5]);
}
