import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import kisch

try:
    kisch._lib_file("Device")
    HAVE_LIBS = True
except FileNotFoundError:
    HAVE_LIBS = False


@unittest.skipUnless(HAVE_LIBS, "KiCad symbol libraries not installed")
class AL8860Symbol(unittest.TestCase):
    def test_pinout_matches_datasheet(self):
        """TSOT-25: 1 SW (LX), 2 GND, 3 CTRL, 4 SET (ISENSE), 5 VIN (Diodes Inc. AL8860)."""
        sym = kisch.load_symbol("Driver_LED:AL8860WT")
        pins = kisch.symbol_pins(sym)
        self.assertEqual({n: p["name"] for n, p in pins.items()},
                         {"1": "SW", "2": "GND", "3": "CTRL", "4": "SET", "5": "VIN"})
        fp = [x[2] for x in kisch.find(sym, "property") if x[1] == "Footprint"]
        self.assertEqual(fp, ["Package_TO_SOT_SMD:TSOT-23-5"])


@unittest.skipUnless(HAVE_LIBS, "KiCad symbol libraries not installed")
class DriverNets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import boards
        cls.s = boards.driver()
        cls.s.check()
        cls.nets = cls.s.netlist()

    def on(self, net, ref, pin):
        self.assertIn((ref, self.s.pin_number(ref, pin)), self.nets[net], f"{ref}.{pin} not on {net}")

    def test_bridge(self):
        # Device:D_Schottky: 1 = K, 2 = A
        for ref, anode, cathode in [("D2", "AC1F", "VBUS"), ("D3", "AC2", "VBUS"), ("D4", "VNEG", "AC1F"), ("D5", "VNEG", "AC2")]:
            self.on(anode, ref, "2")
            self.on(cathode, ref, "1")

    def test_bulk_and_holdup_polarity(self):
        self.on("VBUS", "C1", "1"); self.on("GND", "C1", "2")
        self.on("VHOLD", "C2", "1"); self.on("GND", "C2", "2")
        self.on("VHOLD_IN", "D6", "2"); self.on("VHOLD", "D6", "1")

    def test_sense_is_common_cathode_from_ac(self):
        self.on("AC1F", "D7", "1"); self.on("AC2", "D7", "2"); self.on("VSENSE", "D7", "3")  # BAT54C: 1 A1, 2 A2, 3 K
        self.on("SENSE", "U2", "@PA7")

    def test_mcu_pins(self):
        for pin, net in [("@PB0", "CTRL1"), ("@PB1", "CTRL2"), ("@PB2", "CTRL3"), ("@PA5", "NTC"), ("@PA0", "UPDI_MCU"), ("@VCC", "+5V")]:
            self.on(net, "U2", pin)

    def test_channels(self):
        for n in (1, 2, 3):
            self.on("VBUS", f"Rs{n}", "1"); self.on(f"LED{n}+", f"Rs{n}", "2")
            self.on(f"LED{n}+", f"U{n + 2}", "@SET"); self.on("VBUS", f"U{n + 2}", "@VIN")
            self.on(f"LX{n}", f"U{n + 2}", "@SW"); self.on(f"LX{n}", f"L{n}", "2"); self.on(f"LED{n}-", f"L{n}", "1")
            self.on(f"LX{n}", f"D{8 + n}", "2"); self.on("VBUS", f"D{8 + n}", "1")

    def test_led_link_order(self):
        for pin, net in enumerate(["LED1+", "LED1-", "LED2+", "LED2-", "LED3+", "LED3-", "NTC", "GND"], start=1):
            self.on(net, "J2", str(pin))


@unittest.skipUnless(HAVE_LIBS, "KiCad symbol libraries not installed")
class ReviewFixes(unittest.TestCase):
    """Findings from the 2026-11-17 schematic review."""

    @classmethod
    def setUpClass(cls):
        import boards
        cls.s = boards.driver()
        cls.s.check()
        cls.nets = cls.s.netlist()

    def nets_of(self, ref):
        return {net for net, members in self.nets.items() for r, _ in members if r == ref}

    def pin_net(self, ref, pin):
        num = self.s.pin_number(ref, pin)
        return next(net for net, m in self.nets.items() if (ref, num) in m)

    def value(self, ref):
        return self.s.parts[ref].value

    def test_ntc_replaced_by_active_inrush_limiter(self):
        self.assertNotIn("RT1", self.s.parts)
        self.assertEqual(self.pin_net("D4", "2"), "VNEG")  # bridge low side returns via the limiter
        self.assertEqual(self.pin_net("D5", "2"), "VNEG")
        self.assertEqual(self.nets_of("R9"), {"VNEG", "GND"})
        self.assertTrue(self.value("R9").startswith("10Ω"))
        self.assertEqual((self.pin_net("Q1", "@S"), self.pin_net("Q1", "@D"), self.pin_net("Q1", "@G")), ("VNEG", "GND", "GATE"))
        self.assertEqual(self.nets_of("R10"), {"VBUS", "GATE"})
        self.assertEqual(self.nets_of("C10"), {"GATE", "VNEG"})
        self.assertEqual((self.pin_net("D12", "1"), self.pin_net("D12", "2")), ("GATE", "VNEG"))  # zener K, A
        self.assertEqual((self.pin_net("D13", "2"), self.pin_net("D13", "1")), ("GATE", "VBUS"))  # discharge A, K

    def test_inductors_100uH(self):
        for n in (1, 2, 3):
            self.assertTrue(self.value(f"L{n}").startswith("100µH"), self.value(f"L{n}"))

    def test_ctrl_pulldowns(self):
        for n in (1, 2, 3):
            pulls = [r for r, p in self.s.parts.items() if r.startswith("R") and self.nets_of(r) == {f"CTRL{n}", "GND"}]
            self.assertEqual(len(pulls), 1, f"CTRL{n} pull-down")

    def test_sense_resistors_cap_hardware_at_4W(self):
        for n in (1, 2, 3):
            self.assertTrue(self.value(f"Rs{n}").startswith("0R51"))

    def test_surge_ratings(self):
        self.assertEqual(self.s.parts["D7"].lib_id, "Diode:BAV70")
        for ref in ["D2", "D3", "D4", "D5", "D9", "D10", "D11"]:
            self.assertEqual(self.value(ref), "SS36", ref)
        self.assertEqual(self.value("D1"), "SMBJ24CA")  # kept: a 26 V standoff would clamp past the AL8860's 40 V

    def test_holdup_series_resistor(self):
        self.assertEqual(self.nets_of("R4"), {"VBUS", "VHOLD_IN"})
        self.assertEqual(self.pin_net("D6", "2"), "VHOLD_IN")

    def test_minor_fixes(self):
        self.assertTrue(self.value("C4").startswith("1µF"))
        for ref in ("C11", "C12", "C13"):
            self.assertEqual(self.nets_of(ref), {"VBUS", "GND"})
        self.assertEqual(self.pin_net("U2", "@PA0"), "UPDI_MCU")
        self.assertEqual(self.nets_of("R8"), {"UPDI_MCU", "UPDI"})
        self.assertTrue(self.value("R2").startswith("18k"))
        self.assertIn("1.1 A", self.value("F1"))


@unittest.skipUnless(HAVE_LIBS, "KiCad symbol libraries not installed")
class DiscNets(unittest.TestCase):
    def test_strings_and_ntc(self):
        import boards
        s = boards.disc()
        s.check()
        nets = s.netlist()
        for n in (1, 2, 3):
            anodes = [r for r, p in nets[f"LED{n}+"] if r.startswith("D")]
            cathodes = [r for r, p in nets[f"LED{n}-"] if r.startswith("D")]
            self.assertEqual((len(anodes), len(cathodes)), (1, 1))
            self.assertEqual(len(nets[f"S{n}"]), 2)  # two LEDs in series
        self.assertIn(("J1", "7"), nets["NTC"])
        self.assertIn(("TH1", "1"), nets["NTC"])


def _strip_flags(nets):
    return {k: frozenset(x for x in v if not x[0].startswith("#")) for k, v in nets.items()}


def _kicad_nets(path):
    tree = kisch.parse(Path(path).read_text())
    out = {}
    for n in kisch.find(kisch.find1(tree, "nets"), "net"):
        name = kisch.find1(n, "name")[1].lstrip("/")
        nodes = frozenset((kisch.find1(x, "ref")[1], kisch.find1(x, "pin")[1]) for x in kisch.find(n, "node"))
        nodes = frozenset(x for x in nodes if not x[0].startswith("#"))
        if nodes and not name.startswith("unconnected-"):
            out[name] = nodes
    return out


@unittest.skipUnless(HAVE_LIBS and kisch.kicad_cli(), "KiCad not installed")
class ERC(unittest.TestCase):
    def test_both_boards_pass_erc(self):
        import boards
        tmp = Path(tempfile.mkdtemp())
        try:
            for sheet, name in [(boards.driver(), "candle-driver"), (boards.disc(), "led-disc")]:
                sch = tmp / name / f"{name}.kicad_sch"
                sheet.write(sch)
                rpt = tmp / f"{name}.rpt"
                r = subprocess.run([kisch.kicad_cli(), "sch", "erc", "--severity-error", "--exit-code-violations", "-o", str(rpt), str(sch)],
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f"{name} ERC errors:\n{rpt.read_text() if rpt.exists() else r.stderr}")
                # KiCad's own connectivity must equal the generator's netlist exactly:
                # a label one grid step off a pin would silently connect nothing.
                net = tmp / f"{name}.net"
                subprocess.run([kisch.kicad_cli(), "sch", "export", "netlist", "--format", "kicadsexpr", "-o", str(net), str(sch)],
                               check=True, capture_output=True)
                self.assertEqual(_kicad_nets(net), _strip_flags(sheet.netlist()), f"{name}: KiCad netlist differs")
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
