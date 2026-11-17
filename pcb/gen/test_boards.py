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


class AL8860Symbol(unittest.TestCase):
    def test_pinout_matches_datasheet(self):
        """TSOT-25: 1 LX, 2 GND, 3 CTRL, 4 ISENSE, 5 VIN (Diodes Inc. AL8860)."""
        pins = kisch.symbol_pins(kisch.load_symbol("liberty:AL8860"))
        self.assertEqual({n: p["name"] for n, p in pins.items()},
                         {"1": "LX", "2": "GND", "3": "CTRL", "4": "ISENSE", "5": "VIN"})


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
        for ref, anode, cathode in [("D2", "AC1F", "VRAW"), ("D3", "AC2", "VRAW"), ("D4", "GND", "AC1F"), ("D5", "GND", "AC2")]:
            self.on(anode, ref, "2")
            self.on(cathode, ref, "1")

    def test_bulk_and_holdup_polarity(self):
        self.on("VBUS", "C1", "1"); self.on("GND", "C1", "2")
        self.on("VHOLD", "C2", "1"); self.on("GND", "C2", "2")
        self.on("VBUS", "D6", "2"); self.on("VHOLD", "D6", "1")

    def test_sense_is_common_cathode_from_ac(self):
        self.on("AC1F", "D7", "@A1"); self.on("AC2", "D7", "@A2"); self.on("VSENSE", "D7", "@K")
        self.on("SENSE", "U2", "@PA7")

    def test_mcu_pins(self):
        for pin, net in [("@PB0", "CTRL1"), ("@PB1", "CTRL2"), ("@PB2", "CTRL3"), ("@PA5", "NTC"), ("@PA0", "UPDI"), ("@VCC", "+5V")]:
            self.on(net, "U2", pin)

    def test_channels(self):
        for n in (1, 2, 3):
            self.on("VBUS", f"Rs{n}", "1"); self.on(f"LED{n}+", f"Rs{n}", "2")
            self.on(f"LED{n}+", f"U{n + 2}", "@ISENSE"); self.on("VBUS", f"U{n + 2}", "@VIN")
            self.on(f"LX{n}", f"U{n + 2}", "@LX"); self.on(f"LX{n}", f"L{n}", "2"); self.on(f"LED{n}-", f"L{n}", "1")
            self.on(f"LX{n}", f"D{8 + n}", "2"); self.on("VBUS", f"D{8 + n}", "1")

    def test_led_link_order(self):
        for pin, net in enumerate(["LED1+", "LED1-", "LED2+", "LED2-", "LED3+", "LED3-", "NTC", "GND"], start=1):
            self.on(net, "J2", str(pin))


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
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
