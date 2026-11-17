// Eye-bolt mount checks on the roof.
//   mode = "hole":  thin rod down the roof axis ∩ roof → empty if the bolt hole is open
//   mode = "probe": the rod alone (control; must be non-empty)
//   mode = "seat":  roof ∩ a thin washer-sized ring just above the seat → solid seat
include <../../src/lantern.scad>
part = "none";
mode = "hole";
top = fascia_h + roof_rise + 3;
module rod() { translate([0, 0, -1]) cylinder(d = 1, h = top + 10); }
module seat_ring() {
  translate([0, 0, top - 3 - seat_depth + 0.5]) difference() {
    cylinder(d = washer_od, h = 0.5);
    translate([0, 0, -1]) cylinder(d = bolt_hole_d + 1, h = 3);
  }
}
if (mode == "probe") rod();
else if (mode == "hole") intersection() { roof(); rod(); }
else intersection() { roof(); seat_ring(); }
