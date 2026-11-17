// A thin probe rod along the side exit (cord channel → outside the post
// corner, sloping down 30°). Open exit ⇒ the probe misses the body (empty).
// probe_only = true renders the probe alone (a control: it must be non-empty).
include <../../src/lantern.scad>
part = "none";
probe_only = false;
module probe() {
  hull() {
    translate([cord_c, cord_c, cord_exit_z]) sphere(d = 1);
    translate([half + 2, half + 2, cord_exit_z - (half + 2 - cord_c) * sqrt(2) * tan(30)]) sphere(d = 1);
  }
}
if (probe_only) probe();
else intersection() { body(); probe(); }
