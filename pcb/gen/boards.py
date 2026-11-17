"""Candle driver board + LED disc netlists → KiCad schematics.

Source of truth for the circuit: docs/superpowers/specs/2026-11-17-candle-pcb-design.md
Run:  python3 pcb/gen/boards.py   (or `make pcb`)
"""

from pathlib import Path

from kisch import Sheet

ROOT = Path(__file__).resolve().parent.parent
G = 2.54  # grid


def at(col: int, row: int, dy: float = 0) -> tuple[float, float]:
    """Grid cell → schematic position (A3, ~40 mm cells), optionally nudged down."""
    return (25.4 + col * 16 * G, 38.1 + row * 16 * G + dy)


def heading(s, text: str, col: int, row: int):
    s.note(text, *at(col, row, -6 * G))


# Footprints (KiCad 9/10 standard libraries)
FP = {
    "R0603": "Resistor_SMD:R_0603_1608Metric",
    "R1206": "Resistor_SMD:R_1206_3216Metric",
    "C0603": "Capacitor_SMD:C_0603_1608Metric",
    "C1206": "Capacitor_SMD:C_1206_3216Metric",
    "CP10": "Capacitor_SMD:CP_Elec_10x10.5",
    "CP6": "Capacitor_SMD:CP_Elec_6.3x7.7",
    "SMA": "Diode_SMD:D_SMA",
    "SMB": "Diode_SMD:D_SMB",
    "SOD323": "Diode_SMD:D_SOD-323",
    "SOT23": "Package_TO_SOT_SMD:SOT-23",
    "SOT89": "Package_TO_SOT_SMD:SOT-89-3",
    "TSOT5": "Package_TO_SOT_SMD:TSOT-23-5",
    "SOIC14": "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
    "PTC1812": "Fuse:Fuse_1812_4532Metric",
    "NTC_DISC": "Varistor:RV_Disc_D7mm_W3.4mm_P5mm",
    "IND6045": "Inductor_SMD:L_Bourns_SRN6045TA",
    "JST8": "Connector_JST:JST_PH_B8B-PH-K_1x08_P2.00mm_Vertical",
    "WIRE2": "Connector_Wire:SolderWire-0.5sqmm_1x02_P4.6mm_D0.9mm_OD2.1mm",
    "TP": "TestPoint:TestPoint_Pad_D1.5mm",
    "LED": "LED_SMD:LED_PLCC_2835",
}

PENDING = {"Pending": "⏳ value set after Cube measurement (TODO.md)"}


def driver() -> Sheet:
    s = Sheet("Liberty Lamp — candle driver", "candle-driver")
    c = s.connect

    # ---- Input: cord, fuse, surge, bridge, inrush, bulk (row 0)
    heading(s, "INPUT: Cube 12–15 V AC (dimmed)", 0, 0)
    s.add("J1", "Connector_Generic:Conn_01x02", "Cord (2×20 AWG)", FP["WIRE2"], at(0, 0))
    c("J1", 1, "AC1"); c("J1", 2, "AC2")
    s.add("F1", "Device:Polyfuse", "PTC 0.5 A hold, ≥30 V", FP["PTC1812"], at(1, 0))
    c("F1", 1, "AC1"); c("F1", 2, "AC1F")
    s.add("D1", "Device:D_TVS", "SMBJ24CA", FP["SMB"], at(2, 0))
    c("D1", 1, "AC1F"); c("D1", 2, "AC2")
    # Schottky bridge (Device:D_Schottky: 1 = K, 2 = A)
    for ref, col, anode, cathode in [("D2", 3, "AC1F", "VRAW"), ("D3", 4, "AC2", "VRAW"), ("D4", 5, "GND", "AC1F"), ("D5", 6, "GND", "AC2")]:
        s.add(ref, "Device:D_Schottky", "SS34", FP["SMA"], at(col, 0))
        c(ref, 2, anode); c(ref, 1, cathode)
    s.add("RT1", "Device:Thermistor_NTC", "NTC 5 Ω, ≥1 A (inrush)", FP["NTC_DISC"], at(7, 0))
    c("RT1", 1, "VRAW"); c("RT1", 2, "VBUS")
    s.add("C1", "Device:C_Polarized", "470µF 35V 105°C", FP["CP10"], at(8, 0), **PENDING)
    c("C1", 1, "VBUS"); c("C1", 2, "GND")

    # ---- Dim sense from the raw AC lines (row 1)
    heading(s, "DIM SENSE: full-wave AC → PA7", 0, 1)
    s.add("D7", "Diode:BAT54C", "BAT54C", FP["SOT23"], at(0, 1))
    c("D7", "@A1", "AC1F"); c("D7", "@A2", "AC2"); c("D7", "@K", "VSENSE")
    s.add("R1", "Device:R", "100k", FP["R0603"], at(1, 1), **PENDING)
    c("R1", 1, "VSENSE"); c("R1", 2, "SENSE")
    s.add("R2", "Device:R", "22k", FP["R0603"], at(2, 1), **PENDING)
    c("R2", 1, "SENSE"); c("R2", 2, "GND")
    s.add("C9", "Device:C", "1nF", FP["C0603"], at(3, 1))
    c("C9", 1, "SENSE"); c("C9", 2, "GND")
    s.add("D8", "Device:D_Zener", "5V1 (MM3Z5V1)", FP["SOD323"], at(4, 1))
    c("D8", 1, "SENSE"); c("D8", 2, "GND")

    # ---- MCU hold-up rail + 5 V regulator (row 1, right)
    heading(s, "MCU RAIL: hold-up + 5 V", 5, 1)
    s.add("D6", "Device:D_Schottky", "BAT54WS", FP["SOD323"], at(5, 1))
    c("D6", 2, "VBUS"); c("D6", 1, "VHOLD")
    s.add("C2", "Device:C_Polarized", "100µF 35V", FP["CP6"], at(6, 1))
    c("C2", 1, "VHOLD"); c("C2", 2, "GND")
    s.add("C3", "Device:C", "1µF 50V", FP["C0603"], at(7, 1))
    c("C3", 1, "VHOLD"); c("C3", 2, "GND")
    s.add("U1", "Regulator_Linear:L78L05_SOT89", "78L05", FP["SOT89"], at(8, 1))
    c("U1", "@VI", "VHOLD"); c("U1", "@VO", "+5V"); c("U1", "@GND", "GND")
    s.add("C4", "Device:C", "100nF", FP["C0603"], at(9, 1))
    c("C4", 1, "+5V"); c("C4", 2, "GND")

    # ---- MCU (row 2)
    heading(s, "MCU: ATtiny1614 — flame + dim decode", 0, 2)
    s.add("U2", "MCU_Microchip_ATtiny:ATtiny1614-SS", "ATtiny1614-SSNR", FP["SOIC14"], at(1, 2))
    for pin, net in [("@VCC", "+5V"), ("@GND", "GND"), ("@PB0", "CTRL1"), ("@PB1", "CTRL2"), ("@PB2", "CTRL3"),
                     ("@PA7", "SENSE"), ("@PA5", "NTC"), ("@PA0", "UPDI")]:
        c("U2", pin, net)
    for pin in ["@PA1", "@PA2", "@PA3", "@PA4", "@PA6", "@PB3"]:
        s.no_connect("U2", pin)
    s.add("C8", "Device:C", "100nF", FP["C0603"], at(3, 2))
    c("C8", 1, "+5V"); c("C8", 2, "GND")
    s.add("R3", "Device:R", "10k", FP["R0603"], at(4, 2))
    c("R3", 1, "+5V"); c("R3", 2, "NTC")
    for i, (ref, net) in enumerate([("TP1", "UPDI"), ("TP2", "+5V"), ("TP3", "GND")]):
        s.add(ref, "Connector:TestPoint", net, FP["TP"], at(5 + i, 2))
        c(ref, 1, net)

    # ---- LED channels (rows 3–4): AL8860 hysteretic buck, high-side sense
    for n in (1, 2, 3):
        col = (n - 1) * 3
        heading(s, f"LED CHANNEL {n}: 233 mA", col, 3)
        u = f"U{n + 2}"
        s.add(u, "liberty:AL8860", "AL8860WT-7", FP["TSOT5"], at(col, 3))
        c(u, "@VIN", "VBUS"); c(u, "@ISENSE", f"LED{n}+"); c(u, "@CTRL", f"CTRL{n}"); c(u, "@LX", f"LX{n}"); c(u, "@GND", "GND")
        s.add(f"Rs{n}", "Device:R", "0R43 1%", FP["R1206"], at(col + 1, 3))
        c(f"Rs{n}", 1, "VBUS"); c(f"Rs{n}", 2, f"LED{n}+")
        s.add(f"L{n}", "Device:L", "33µH ≥1A", FP["IND6045"], at(col + 2, 3))
        c(f"L{n}", 1, f"LED{n}-"); c(f"L{n}", 2, f"LX{n}")
        s.add(f"D{8 + n}", "Device:D_Schottky", "SS34", FP["SMA"], at(col + 1, 4))
        c(f"D{8 + n}", 2, f"LX{n}"); c(f"D{8 + n}", 1, "VBUS")
        s.add(f"C{4 + n}", "Device:C", "10µF 50V X7R", FP["C1206"], at(col + 2, 4))
        c(f"C{4 + n}", 1, "VBUS"); c(f"C{4 + n}", 2, "GND")

    # ---- LED disc link (row 4, right)
    s.add("J2", "Connector_Generic:Conn_01x08", "To LED disc", FP["JST8"], at(9, 4))
    for pin, net in enumerate(["LED1+", "LED1-", "LED2+", "LED2-", "LED3+", "LED3-", "NTC", "GND"], start=1):
        c("J2", pin, net)

    # ---- ERC power flags
    for i, net in enumerate(["VBUS", "VHOLD", "GND"], start=1):
        s.add(f"#FLG0{i}", "power:PWR_FLAG", "PWR_FLAG", "", at(9, 2, (i - 1) * 4 * G), in_bom=False)
        c(f"#FLG0{i}", 1, net)
    return s


def disc() -> Sheet:
    s = Sheet("Liberty Lamp — LED disc (aluminum-core)", "led-disc", paper="A4")
    c = s.connect
    s.add("J1", "Connector_Generic:Conn_01x08", "From driver", FP["JST8"], at(0, 0))
    for pin, net in enumerate(["LED1+", "LED1-", "LED2+", "LED2-", "LED3+", "LED3-", "NTC", "GND"], start=1):
        c("J1", pin, net)
    heading(s, "3 strings × 2 LEDs, 2200 K CRI ≥ 90", 1, 0)
    ref = 1
    for n in (1, 2, 3):
        mid = f"S{n}"
        for k, (anode, cathode) in enumerate([(f"LED{n}+", mid), (mid, f"LED{n}-")]):
            r = f"D{ref}"
            s.add(r, "Device:LED", "2200K CRI≥90 ~1W", FP["LED"], at(1 + k, n - 1))
            c(r, 2, anode); c(r, 1, cathode)  # Device:LED: 1 = K, 2 = A
            ref += 1
    s.add("TH1", "Device:Thermistor_NTC", "10k B3950", FP["R0603"], at(3, 0))
    c("TH1", 1, "NTC"); c("TH1", 2, "GND")
    return s


def main():
    for sheet, name in [(driver(), "candle-driver"), (disc(), "led-disc")]:
        out = ROOT / name / f"{name}.kicad_sch"
        sheet.write(out)
        print(f"wrote {out.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
