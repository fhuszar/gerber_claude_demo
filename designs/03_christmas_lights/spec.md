# Design 03: Christmas Light Controller with Microcontroller

## Specification

A sophisticated LED controller using a microcontroller (ATtiny85) with PWM and shift register output to drive addressable Christmas light patterns (chasing, breathing, alternating sequences).

### Components

1. **Microcontroller**: ATtiny85 (SOIC-8 surface mount)
2. **Crystal/Clock**: 8 MHz ceramic resonator (SMD, 2-pad, or internal RC oscillator)
3. **Shift Registers**: 2× 74HC595 (SOIC-16) for 16 addressable LED outputs
4. **LEDs**: 16× 0603 surface-mount LEDs (mix of red/green for dual-color patterns)
5. **Current-Limiting Resistors**: 16× 47–100Ω (0603)
6. **Decoupling Capacitors**: 3× 0.1µF (0603) on VCC rails
7. **Input Button**: 1× momentary SPST push-button (0.1" pitch, through-hole or SMD)
8. **Power Connector**: USB Type-C or 5V barrel jack (0.1" pitch header)
9. **Programming Header**: ISP 6-pin header (2.54mm pitch) for in-circuit programming

### Circuit Topology

```
Power (USB 5V)
  ↓
  ├─ ATtiny85 (microcontroller core)
  │  ├─ Pin 1 (RESET) — tied to VCC via 10kΩ resistor
  │  ├─ Pin 2 (PB3 / OC1B) — PWM output to external amplifier (optional)
  │  ├─ Pins 5,6,7 (GND, PB0/SDA, PB1/SCL) — SPI-like serial interface
  │  └─ Pin 8 (VCC)
  │
  ├─ Shift Register Chain (2× 74HC595)
  │  ├─ First 74HC595 Q0–Q7 → LED bank 1 (red)
  │  └─ Second 74HC595 Q0–Q7 → LED bank 2 (green)
  │     ├─ Daisy-chain: LATCH tied together
  │     ├─ Clock lines tied together
  │     └─ Data lines cascaded (Q7S of first → SER of second)
  │
  ├─ LED Array (16 channels)
  │  └─ Each: resistor → LED → ground plane
  │
  ├─ Input Button
  │  └─ Pulls PB4 to ground on press (with weak internal pull-up)
  │
  └─ Power Management
     ├─ 5V via USB or barrel jack
     └─ Ground plane on bottom layer
```

### PCB Requirements

- **Layer Stack**: 2-layer PCB (top: signals and SMD placement, bottom: continuous ground plane)
- **Board Size**: 100mm × 75mm
- **Trace Width**: 6-mil signal traces, 12-mil power rails
- **Spacing**: 8-mil minimum clearance
- **Via Array**: 20+ plated through-vias (0.3mm drill) distributed for ground return paths
- **Silkscreen**: Component labels, input/output connector pinouts, programming header pin functions
- **Thermal Pads**: Optional; not required for ATtiny85 at typical clock speeds

### Key Signal Paths

1. **SPI Chain**: PB0 (MOSI) → shift register chain; PB2 (SCK) → clock line; PB1 (MISO/LATCH) → latch signal
2. **Button Input**: PB4 (ADC2) with weak pull-up → momentary switch to ground
3. **LED Outputs**: Q0–Q15 of shift register chain → resistor + LED arrays → GND plane
4. **Power Distribution**: USB 5V → VCC trace and vias; continuous GND plane on bottom layer

### Manufacturing Notes

- 2-layer PCB with 1mm FR-4, 2oz copper (for robust power delivery)
- ATtiny85 (SOIC-8) and 74HC595 (SOIC-16) are hand-solderable with a fine-tip soldering iron or reflow oven
- 0603 components preferred for easy manual assembly
- Plated through-holes required for all vias
- Expected firmware runs a state machine to generate:
  - **Chasing Pattern**: LEDs light sequentially across the array (e.g., red chases green)
  - **Breathing Effect**: Gradual fade in/out using PWM
  - **Alternating Strobe**: Rapid on/off for dramatic effect
  - **Button Control**: Cycle through patterns on each press
