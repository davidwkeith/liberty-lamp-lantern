// A thin slab through the roof cap, minus the eye-bolt hole. Subtracting the
// roof leaves nothing unless something other than the bolt pierces the cap.
// mode = "control" renders the slab alone (must be non-empty).
include <../../src/lantern.scad>
part = "none";
mode = "check";
module slab() {
  translate([0, 0, fascia_h + roof_rise + 1]) difference() {
    sq(cap_w - 2, 1);
    translate([0, 0, -1]) cylinder(d = bolt_hole_d + 0.5, h = 3);
  }
}
if (mode == "control") slab();
else difference() { slab(); roof(); }
