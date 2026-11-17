import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import kisch

FIXTURE_LIB = """(kicad_symbol_lib (version 20241209) (generator "test")
  (symbol "R" (pin_numbers (hide yes)) (in_bom yes) (on_board yes)
    (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
    (property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))
    (symbol "R_0_1" (rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none))))
    (symbol "R_1_1"
      (pin passive line (at 0 3.81 270) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      (pin passive line (at 0 -3.81 90) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
  (symbol "R_Alt" (extends "R")
    (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
    (property "Value" "R_Alt" (at 0 0 90) (effects (font (size 1.27 1.27))))))
"""


class KischTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "Fixture.kicad_sym").write_text(FIXTURE_LIB)
        kisch.KICAD_SYMBOL_DIRS.insert(0, str(self.tmp))
        kisch._lib_cache.clear()

    def tearDown(self):
        kisch.KICAD_SYMBOL_DIRS.remove(str(self.tmp))
        shutil.rmtree(self.tmp)

    def test_parse_dump_roundtrip(self):
        expr = kisch.parse('(a "b \\"q\\"" (c 1.5 -2) (d))')
        self.assertEqual(kisch.parse(kisch.dump(expr)), expr)

    def test_pin_endpoint_transform(self):
        s = kisch.Sheet("t", "t")
        r = s.add("R1", "Fixture:R", "10k", "Resistor_SMD:R_0603_1608Metric", (100, 100))
        # Library Y-up → schematic Y-down: pin 1 (lib y=+3.81) sits above the body.
        self.assertEqual(kisch.pin_endpoints(r), {"1": (100.0, 96.19), "2": (100.0, 103.81)})

    def test_extends_is_flattened(self):
        sym = kisch.load_symbol("Fixture:R_Alt")
        self.assertIsNone(kisch.find1(sym, "extends"))
        self.assertEqual(set(kisch.symbol_pins(sym)), {"1", "2"})

    def test_unconnected_pin_detected(self):
        s = kisch.Sheet("t", "t")
        s.add("R1", "Fixture:R", "10k", "", (100, 100))
        s.connect("R1", "1", "A")
        with self.assertRaisesRegex(ValueError, r"R1\.2 .*unconnected"):
            s.check()

    def test_missing_pin_detected(self):
        s = kisch.Sheet("t", "t")
        s.add("R1", "Fixture:R", "10k", "", (100, 100))
        s.connect("R1", "1", "A")
        s.connect("R1", "2", "B")
        s.connect("R1", "3", "C")
        with self.assertRaisesRegex(ValueError, r"R1\.3 does not exist"):
            s.check()

    def test_labels_land_on_pins(self):
        s = kisch.Sheet("t", "t")
        s.add("R1", "Fixture:R", "10k", "", (100, 100))
        s.connect("R1", "1", "A")
        s.no_connect("R1", "2")
        expr = s.to_sexpr()
        labels = [(x[1], tuple(float(v) for v in kisch.find1(x, "at")[1:3])) for x in kisch.find(expr, "label")]
        self.assertEqual(labels, [("A", (100.0, 96.19))])
        self.assertEqual(len(kisch.find(expr, "no_connect")), 1)

    @unittest.skipUnless(kisch.kicad_cli(), "kicad-cli not installed")
    def test_roundtrip_opens_in_kicad(self):
        s = kisch.Sheet("t", "t")
        s.add("R1", "Fixture:R", "10k", "", (100, 100))
        s.connect("R1", "1", "A")
        s.connect("R1", "2", "B")
        out = self.tmp / "t.kicad_sch"
        s.write(out)
        r = subprocess.run([kisch.kicad_cli(), "sch", "export", "netlist", "-o", str(self.tmp / "t.net"), str(out)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
