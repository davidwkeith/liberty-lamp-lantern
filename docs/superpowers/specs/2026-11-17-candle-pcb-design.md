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

Revised 2026-11-17 after the schematic review. The source of truth is `pcb/gen/boards.py`.

```
AC1 ─F1 (PTC 1.1 A)─ AC1F ┬─ D1 SMBJ24CA ─ AC2
                          bridge D2–D5 SS36 → VBUS (+) / VNEG (−)
VNEG ─ R9 10 Ω ─ GND          inrush limiter, bypassed by Q1 DMN6075S (S = VNEG, D = GND)
  Q1 gate: R10 470k from VBUS, C10 470n to VNEG (bypass after ~30–50 ms),
           D12 12 V zener clamp, D13 1N4148WS dumps gate charge into VBUS on power loss
VBUS ═ C1 470µ/35V
AC1F/AC2 ─ D7 BAV70 (common cathode, 100 V) ─ VSENSE ─ R1 100k ─┬─ SENSE → PA7
                                                                 ├─ R2 18k ─ GND
                                                                 ├─ C9 1n ─ GND
                                                                 └─ D8 5V1 zener ─ GND
VBUS ─ R4 47 Ω ─ D6 BAT54WS ─ VHOLD ═ C2 100µ/35V, C3 1µ ─ U1 78L05 ─ +5V ═ C4 1µ
U2 ATtiny1614:
  PB0–PB2  CTRL1–3 (each pulled down by R5–R7 4k7)
  PA7      SENSE
  PA5      NTC (R3 10k to +5V)
  PA0      UPDI_MCU ─ R8 470 Ω ─ UPDI test pad
Channel n (×3), AL8860WT, ~196 mA:
  VBUS ─ Rsn 0R51 ─ LEDn+ (SET) ─ [2 LEDs on disc] ─ LEDn− ─ Ln 100 µH ─ SW
  D(8+n) SS36: SW → VBUS · C(4+n) 10 µF/50 V + C(10+n) 100 nF at VIN
J1  cord pads (AC1, AC2)
J2  LED link, 8 pins: LED1+ LED1− LED2+ LED2− LED3+ LED3− NTC GND
```

**LED disc:** 3 strings of 2 × 2200 K LEDs, plus a 10 k NTC (0603) beside the LEDs, wired to J2.

## Numbers

| Item | Value |
|------|-------|
| Channel current | 0.1 V / 0.51 Ω ≈ 196 mA |
| LED power at 100% on all channels | 3 × 2 × ~3.1 V × 0.196 A ≈ 3.65 W (≤ ~3.8 W at +5% sense tolerance), the hardware ceiling |
| Switching frequency | 100 µH with ±15% hysteresis, 20 V in, 6.3 V string: about 600 kHz (it was about 1.9 MHz with 33 µH) |
| Inrush | ≤ 21 V / (10 Ω + wiring) ≈ 2 A per board, decaying with τ ≈ 4.7 ms. The FET bypasses R9 once C1 is full |
| MCU hold-up | 100 µF from ~18 V down to the 78L05's ~7 V dropout at ~10 mA ≈ 0.1 s, far longer than any half-cycle |
| SENSE scaling | 21 V peak × 18/118 ≈ 3.2 V, below the zener knee; the zener clamps surges |
| VBUS max | ~20.5 V nominal, rising to ~24 V at light load and high mains. The TVS clamps at ~39 V, under the AL8860's 40 V maximum. The bridge and driver diodes are 60 V, D7 is 100 V |

### Review decisions (2026-11-17)

- **Kept the SMBJ24CA.** A 26 V-standoff TVS would clamp at about 42 V, over the AL8860's 40 V absolute maximum.
- **Program boards while they're AC-powered.** Powering through TP2 (+5 V) back-feeds the 78L05.
- **Conformal-coat both boards, and route the disc wiring away from GND.** A pinched LED− wire to GND bypasses the AL8860, and only F1 limits the current.
- **To verify against datasheets at layout:**
  - the AL8860's CTRL pull-up and shutdown threshold (the 4k7 pull-down must hold CTRL below shutdown)
  - its minimum on and off times
  - the PTC's derating at 60 °C
- **Open (owner decision in [TODO.md](../../../TODO.md)): the Cube's VA budget.** A capacitor-input rectifier draws current in short peaks, a power factor of about 0.6. At the 3 W default, 13 boards come to about 46 W real and about 70 VA, against the Cube's 60 W rating.

## Pending the Cube measurement ⏳

- **C1's value:** the bulk hold-up for the LED rail. Make it as small as the waveform allows, to cut inrush.
- **The R1/R2 ratio**, if the Cube's output turns out not to be near-sinusoidal.
- **Whether D13 is safe under deep dimming.** If VBUS sags below the gate voltage between pulses, D13 drains the gate and R9 comes back into the circuit. Check it once the waveform is known.

The firmware's decoding strategy follows from the measured waveform. The schematic doesn't change shape either way.

## Left to the builder

- Footprints: standard KiCad libraries, 0603 passives.
- Test points.
- Where the strain-relief slot goes.
- Exact part picks for spec-only BOM rows.
