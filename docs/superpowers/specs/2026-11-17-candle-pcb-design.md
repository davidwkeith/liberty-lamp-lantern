# Candle PCB — Design

Date: 2026-11-17 · Requirements: [power & wiring design § PCB requirements](2026-11-16-power-wiring-design.md) · Parts: [BOM § Candle PCB](../../bom.md)

## Intent

A per-lantern candle that runs straight off the Luxor Cube's dimmed 12–15 V AC and follows the Luxor's brightness. It renders a realistic, independently moving flame, with enough brightness to show off at 100% and stay subtle when dimmed.

## Goals / non-goals / anti-goals

- **Goals:**
  - Survive years outdoors: surges, heat and condensation.
  - Ride through the Cube's chopping without the MCU resetting.
  - Hardware can't exceed 4 W; firmware defaults to a 3 W cap.
  - Factory-assembled, flashed over UPDI.
- **Non-goals:**
  - Wireless control or per-lantern addressing.
  - Color changes beyond warm white.
- **Anti-goals:**
  - The candle cup's PETG or ASA surface going above 60 °C.
  - Inrush that trips the Cube when 13 boards switch on together.
  - A design that only works with one guessed dimming waveform.

## Approaches

**Board split**
1. **Driver board (FR4) + LED disc (aluminum-core)** — *chosen.* It keeps about 3 W of LED heat off the printed cup.
2. One FR4 board with thermal vias — too hot at 4 W in a 32 mm disc.
3. One aluminum board — single layer, so routing the MCU and three drivers would be cramped.

**LED drive**
1. **3 × AL8860 hysteretic buck** — *chosen.* Efficient across the varying rectified input, and each channel is PWM-dimmable.
2. A linear constant-current string off the bus — wastes the 12 → 21 V headroom as heat.
3. One driver with MOSFET channel switches — the channels couldn't overlap smoothly.

**Dim sensing**
1. **Separate sense diodes from the AC lines**, feeding a divider into the MCU — *chosen.* The MCU sees the raw full-wave waveform whatever the bulk capacitor is doing. Firmware decodes it whether the Cube uses PWM, phase-cut, or a lower amplitude.
2. Sensing the bus voltage — the bulk capacitor smooths away the dimming information.

## Circuit (driver board)

```
AC1 ─F1─┬─D1(TVS)─┬─ bridge D2–D5 ── VRAW ─RT1(NTC)─ VBUS ═ C1 470µ
AC2 ────┘         └───────────────── GND
AC1/AC2 ─ D7 (BAT54C, common cathode) ─ VSENSE ─ R1 100k ─┬─ SENSE → PA7 (ADC AIN7 / AC0 AINP0)
                                                          ├─ R2 22k ─ GND
                                                          ├─ C9 1n ─ GND
                                                          └─ D8 5V1 zener ─ GND
VBUS ─D6(BAT54)─ VHOLD ═ C2 100µ/35V ─ U1 78L05 ─ +5V ═ C3 1µ, C4 100n
U2 ATtiny1614:
  PB0, PB1, PB2  TCA0 WO0..2 → CTRL1..3
  PA7            SENSE
  PA5            LED-disc NTC (10k to +5V)
  PA0            UPDI (test pad)
Channel n (×3):
  VBUS ─ Rsn 0.43Ω ─ LEDn+ ─ [2 LEDs on disc] ─ LEDn− ─ Ln 33µH ─ LX(U)
  U(n+2) AL8860: VIN=VBUS, ISENSE between Rsn and LEDn+, CTRL=CTRLn
  Dn SS34: LX → VBUS · Cin 10µ/50V at VIN
J1  cord pads (AC1, AC2)
J2  LED link, 8 pins: LED1+ LED1− LED2+ LED2− LED3+ LED3− NTC GND
```

**LED disc:** 3 strings of 2 × 2200 K LEDs, plus a 10 k NTC (0603) beside the LEDs, wired to J2.

## Numbers

| Item | Value |
|------|-------|
| Channel current | 0.1 V / 0.43 Ω ≈ 233 mA |
| LED power at 100% on all channels | 3 × 2 × ~2.9 V × 0.233 A ≈ 4.0 W, the hardware ceiling |
| MCU hold-up | 100 µF from ~18 V down to the 78L05's ~7 V dropout at ~3 mA ≈ 0.37 s, far longer than any half-cycle |
| SENSE scaling | 21 V peak × 22/122 ≈ 3.8 V, within 5 V; the zener clamps surges |
| VBUS max | 15 VAC × √2 − Schottky drops ≈ 20.5 V. All parts rated ≥ 30 V; caps 35–50 V |

## Pending the Cube measurement ⏳

- **C1's value:** the bulk hold-up for the LED rail.
- **The R1/R2 ratio**, if the Cube's output turns out not to be near-sinusoidal.

The firmware's decoding strategy follows from the measured waveform. The schematic doesn't change shape either way.

## Left to the builder

- Footprints: standard KiCad libraries, 0603 passives.
- Test points.
- Where the strain-relief slot goes.
- Exact part picks for spec-only BOM rows.
