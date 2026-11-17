// A thin slab through the roof cap. Solid cap ⇒ a plain box (12 triangles);
// any hole through the cap adds facets.
include <../../src/lantern.scad>
part = "none";
intersection() {
  roof();
  translate([0, 0, fascia_h + roof_rise + 1]) sq(cap_w - 2, 1);
}
