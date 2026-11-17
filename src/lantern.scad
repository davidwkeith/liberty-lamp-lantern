// Liberty Lamp — Craftsman lantern frame (all 13 lanterns are identical)
// Units: mm. Origin: body centered on XY, base on Z=0.
// Render one part:  openscad -D 'part="body"' -o body.stl src/lantern.scad

part = "assembly"; // "body" | "roof" | "assembly"

/* [Envelope] */
W          = 102;   // body width across the posts (4")
post_w     = 12;    // corner post size
base_h     = 16;    // base slab height (holds candle cup + cord tunnel)
panel_h    = 100;   // visible panel height between base and top rail
top_rail_h = 12;    // top rail height
plinth     = 3;     // base flare beyond posts, per side
band       = 1.5;   // top-rail band projection, per side

/* [Panels] */
panel_thickness = 3.0;  // acrylic default; set for mica film carrier etc.
panel_clearance = 0.3;  // added to slot width and removed from panel size
slot_depth      = 3;    // how far panel edges sit into the posts
panel_skin      = 3;    // post wall outside the panel (sets the panel plane)

/* [Candle / wiring] */
led_d  = 38;   // candle cup diameter (LED module TBD)
led_h  = 10;   // candle cup depth
cord_od = 5.0; // lantern cord OD (2×20 AWG outdoor cable)
cord_d  = 5.5; // cord channel diameter
drain_d = 4;   // base drain holes

/* [Roof + fastening] */
standoff_h   = 6;    // vent gap between top rail and roof
eave         = 6;    // roof overhang beyond posts, per side
fascia_h     = 4;    // vertical roof edge below the 45° slope
roof_wall    = 2.4;  // roof shell thickness
cap_w        = 20;   // flat top under the hanging eye
eye_od       = 16;
eye_id       = 8;
eye_t        = 5;
insert_d     = 4.2;  // M3 heat-set insert hole
insert_depth = 8;    // ≥ screw reach below the well floor + 1
screw_len    = 10;   // M3 screw length
boss_d       = 9;
screw_d      = 3.4;  // M3 clearance
screw_head_d = 6.5;  // counterbore for M3 socket head
well_floor   = 3;    // roof material clamped under the screw head
ledge_h      = 3;    // roof corner ledges that bear on the standoffs
cord_elbow   = 7;    // 45° chord easing the cord's turn from post into base

$fn = 48;
eps = 0.01;

// ---- Derived ----
body_h   = base_h + panel_h + top_rail_h;
half     = W / 2;
inner    = half - post_w;                         // interior half-width
plane    = half - panel_skin - (panel_thickness + panel_clearance) / 2; // panel mid-plane
slot_w   = panel_thickness + panel_clearance;
slot_end = inner + slot_depth;                    // panel edge reach into post
web      = plane - slot_w / 2 - slot_end;         // post material between the two grooves
cord_c   = (slot_end + half) / 2;                 // cord channel center (x = y)
boss_c   = inner - 3.5;                           // insert boss center (x = y)
roof_half = half + eave;
roof_rise = roof_half - cap_w / 2;                // 45° from eave to cap
panel_size = [2 * slot_end - 2 * panel_clearance, body_h - (base_h - 2) - panel_clearance];

assert(slot_depth < post_w - 2, "slot_depth must leave ≥2 mm of post");
assert(led_d < 2 * inner, "led_d larger than interior");
assert(cord_d + 2.4 <= half - slot_end, "cord channel too wide for post");
assert(cord_d >= cord_od + 0.5, "cord_d must be ≥ cord_od + 0.5 mm");
assert(web >= 1.6, str("post web between panel grooves is ", web, " mm; need ≥1.6 (thinner panels, shallower slot_depth, or wider post_w)"));
assert(panel_skin >= 1.6, "panel_skin too thin");
assert(led_h <= base_h - 3, "led_h cuts through (or nearly through) the base floor");
assert(insert_depth >= screw_len - well_floor + 1, "screw longer than insert hole; raise insert_depth or use a shorter screw");
assert(insert_d + 3 <= boss_d, "insert too large for boss");
assert(screw_head_d + 2 <= boss_d, "screw head too large for roof well");

echo(str("PANEL (w × h × t): ", panel_size[0], " × ", panel_size[1], " × ", panel_thickness, " mm, qty 4"));
echo(str("ASSEMBLED HEIGHT: ", body_h + standoff_h + fascia_h + roof_rise + 3 + eye_od - 2, " mm"));

// ---- Helpers ----
module sq(w, h) { translate([-w / 2, -w / 2, 0]) cube([w, w, h]); }

// Apply children at the four rotations about Z (one per side/corner).
module four() { for (a = [0, 90, 180, 270]) rotate(a) children(); }

// ---- Body ----
module post() {
  translate([inner, inner, 0]) cube([post_w, post_w, body_h]);
}

module base() {
  hull() {
    sq(W + 2 * plinth, 3);
    sq(W, 6);
  }
  sq(W, base_h);
}

// 45° haunches under both rail strips (either side of the panel slit) so the
// rail underside needs no support or long bridge.
module rail_haunches() {
  z = body_h - top_rail_h;
  pi = plane - slot_w / 2;  // inner strip's panel face
  po = plane + slot_w / 2;  // outer strip's panel face
  l = 2 * inner + 2 * eps;
  hull() {
    translate([-l / 2, inner - eps, z - eps]) cube([l, pi - inner + eps, eps]);
    translate([-l / 2, pi - eps, z - (pi - inner)]) cube([l, eps, eps]);
  }
  hull() {
    translate([-l / 2, po, z - eps]) cube([l, half - po, eps]);
    translate([-l / 2, po, z - (half - po)]) cube([l, eps, eps]);
  }
}

module top_rail() {
  z = body_h - top_rail_h;
  four() rail_haunches();
  translate([0, 0, z]) difference() {
    sq(W, top_rail_h);
    translate([0, 0, -eps]) sq(2 * inner, top_rail_h + 2 * eps);
  }
  // Craftsman band: projects `band` past the posts, with a 45° underside that
  // starts at the panel's outer face so it prints without support.
  po = plane + slot_w / 2;
  drop = half + band - po;
  translate([0, 0, z - drop]) difference() {
    hull() {
      sq(2 * po + 0.02, eps);
      translate([0, 0, drop]) sq(W + 2 * band, top_rail_h * 0.5);
    }
    translate([0, 0, -eps]) sq(2 * po + 0.02, drop + top_rail_h);
  }
}

// Cord-path node: a sphere with a 45° teardrop peak so tunnels print unsupported.
module cord_node(p) {
  translate(p) hull() {
    sphere(d = cord_d);
    translate([0, 0, cord_d / 2 * sqrt(2)]) cube(eps, center = true);
  }
}

// Insert boss tucked into an interior corner, tapered underneath for printing.
module boss() {
  z0 = body_h - top_rail_h - 10;
  difference() {
    hull() {
      translate([boss_c, boss_c, z0 + 10]) cylinder(d = boss_d, h = top_rail_h + standoff_h);
      translate([inner - 0.5, inner - 0.5, z0]) cube([0.5 + eps, 0.5 + eps, top_rail_h + 10 + standoff_h]);
    }
    translate([boss_c, boss_c, body_h + standoff_h - insert_depth]) cylinder(d = insert_d, h = insert_depth + eps);
  }
}

// Post-top standoff, kept clear of both panel grooves and inset 0.5 mm from
// the post's outer faces (a reveal; also avoids coplanar faces in the union).
module standoff() {
  s = slot_end + 0.5;
  translate([s, s, body_h - eps]) cube([half - 0.5 - s, half - 0.5 - s, standoff_h + eps]);
}

module body() {
  difference() {
    union() {
      base();
      four() post();
      top_rail();
      four() standoff();
      for (a = [0, 180]) rotate(a) boss();
    }
    // Panel grooves: posts + rail slits + base channel
    four() translate([-slot_end, plane - slot_w / 2, base_h - 2]) cube([2 * slot_end, slot_w, body_h]);
    // Candle cup + center drain
    translate([0, 0, base_h - led_h]) cylinder(d = led_d + 0.4, h = led_h + eps);
    translate([0, 0, -eps]) cylinder(d = drain_d, h = base_h);
    // Floor drains on the axes (clear of the diagonal cord tunnel)
    four() translate([inner - 10, 0, -eps]) cylinder(d = drain_d, h = base_h + 2 * eps);
    // Cord: down the +X+Y post, then a diagonal tunnel into the candle cup
    tz = base_h - led_h + cord_d / 2;
    ek = cord_elbow / sqrt(2);
    translate([cord_c, cord_c, tz + cord_elbow]) cylinder(d = cord_d, h = body_h + standoff_h);
    hull() {
      cord_node([cord_c, cord_c, tz + cord_elbow]);
      cord_node([cord_c - ek, cord_c - ek, tz]);
    }
    hull() {
      cord_node([cord_c - ek, cord_c - ek, tz]);
      cord_node([0, 0, tz]);
    }
  }
}

// ---- Roof (printed peak-up, sits on the body standoffs) ----
module roof_solid(off = 0) {
  // off > 0 shrinks the solid uniformly (for hollowing)
  hw = roof_half - off;
  translate([0, 0, -eps]) sq(2 * hw, fascia_h + eps);
  translate([0, 0, fascia_h - eps])
    hull() {
      sq(2 * hw, eps);
      translate([0, 0, roof_rise]) sq(max(cap_w - 2 * off, 0.1), eps);
    }
}

module roof() {
  well_r = boss_d / 2;
  difference() {
    union() {
      difference() {
        roof_solid();
        // Hollow: inset by wall, then drop so the 45° faces are roof_wall thick
        // measured normal to the slope (horizontal thickness = wall·√2).
        translate([0, 0, -roof_wall * (sqrt(2) - 1)]) roof_solid(roof_wall);
      }
      // Screw well tubes, clipped to the roof's outer skin
      intersection() {
        roof_solid();
        for (a = [0, 180]) rotate(a) translate([boss_c, boss_c, 0]) cylinder(d = boss_d + 2 * roof_wall, h = fascia_h + roof_rise);
      }
      // Corner ledges: the roof bears on all four standoffs, not just the bosses
      intersection() {
        roof_solid();
        four() translate([slot_end + 0.5, slot_end + 0.5, 0]) cube([roof_half, roof_half, ledge_h]);
      }
      // Flat cap + hanging eye (ring in the XZ plane)
      translate([0, 0, fascia_h + roof_rise - eps]) sq(cap_w, 3);
      translate([0, eye_t / 2, fascia_h + roof_rise + 3 + eye_od / 2 - 2])
        rotate([90, 0, 0]) difference() {
          cylinder(d = eye_od, h = eye_t);
          translate([0, 0, -eps]) cylinder(d = eye_id, h = eye_t + 2 * eps);
        }
    }
    for (a = [0, 180]) rotate(a) translate([boss_c, boss_c, 0]) {
      translate([0, 0, -eps]) cylinder(d = screw_d, h = well_floor + 2 * eps);
      translate([0, 0, well_floor]) cylinder(d = screw_head_d, h = fascia_h + roof_rise);
    }
    // Cord drop through the +X+Y ledge into the hollow post
    translate([cord_c, cord_c, -1]) cylinder(d = cord_d, h = ledge_h + 2);
    // Cord entry beside the eye
    translate([0, eye_t / 2 + cord_d / 2 + 1, fascia_h + roof_rise - 10]) cylinder(d = cord_d, h = 20);
  }
}

// ---- Assembly preview ----
module panels() {
  color("#E8DFC8", 0.45) four()
    translate([-panel_size[0] / 2, plane - panel_thickness / 2, base_h - 2])
      cube([panel_size[0], panel_thickness, panel_size[1]]);
}

module assembly() {
  color("#5a4632") body();
  panels();
  color("#3b4a5a") translate([0, 0, body_h + standoff_h]) roof();
}

if (part == "body") body();
else if (part == "roof") roof();
else if (part == "assembly") assembly();
