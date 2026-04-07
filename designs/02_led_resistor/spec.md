# Design 02: LED Resistor Array with Shift Register

## Specification

A moderate-complexity circuit combining discrete LEDs, current-limiting resistors, and a digital logic IC (shift register) for addressable control.

### Components

1. **Microcontroller Interface**: Standard 2.54mm pitch connector (6 pins: VCC, GND, CLK, DATA, LATCH, OE)
2. **Logic IC**: 74HC595 8-bit shift register (SOIC-16 surface mount)
3. **LEDs**: 8× 0603 surface-mount LEDs (red, 1.8V @ 20mA typical)
4. **Resistors**: 8× 0603 current-limiting resistors (100–150Ω, 1/10W)
5. **Decoupling Capacitors**: 2× 0.1µF ceramic (0603), one per VCC rail
6. **Pull-down Resistors**: 1× 10kΩ (0603) on the Output Enable line

### Circuit Topology

```
Microcontroller (CLK, DATA, LATCH) → 74HC595 Shift Register → LED Array (8 channels)
Each LED driven through a current-limiting resistor to ground.
```

### PCB Requirements

- **Layer Stack**: 2-layer PCB (top copper for signals, bottom for ground plane)
- **Board Size**: 75mm × 50mm
- **Trace Width**: 8-mil signal traces, 15-mil power rails
- **Spacing**: 10-mil minimum clearance
- **Via**: Small vias (0.3mm drill) to connect top/bottom layers for ground distribution
- **Silkscreen**: Reference designators (U1, R1–R8, LED1–LED8, C1, C2), pin labels on connector

### Key Traces

1. CLK from connector pin 2 → 74HC595 pin 11 (CLK)
2. DATA from connector pin 3 → 74HC595 pin 14 (SER, serial input)
3. LATCH from connector pin 4 → 74HC595 pin 12 (RCLK, register clock)
4. Q0–Q7 outputs from pins 15–16, 1–4 of 74HC595 → resistor arrays → LED cathodes
5. Continuous ground plane on bottom layer; top layer hosts signal traces and components

### Holes

- Connector: 6 holes (2.54mm pitch), 0.035" diameter
- Via array (12 minimum): 0.3mm diameter plated through-holes connecting top/bottom GND

### Manufacturing Notes

- 2-layer PCB with 1mm FR-4
- Surface-mount components (0603) suitable for pick-and-place machines or hand-soldering with a magnifier
- Plated through-holes required for vias and connector mounting
- Min trace: 8 mils, min clearance: 10 mils
