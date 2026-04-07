# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository generates RS-274X Gerber files and Excellon drill files for printed circuit board fabrication. Each design is self-contained in a `designs/<name>/` subdirectory with its own specification and generation script.

## Project Structure

```
designs/
  01_battery_bulb/
    spec.md           # English specification of the circuit
    generate.py       # Python script to generate Gerber files
    output/           # Directory containing generated .gbr and .drl files
  02_led_resistor/
    spec.md
    generate.py
    output/
  03_christmas_lights/
    spec.md
    generate.py
    output/
```

Each design follows the same pattern:
- **spec.md** — Human-readable description of the circuit, components, and PCB layout goals
- **generate.py** — Standalone Python script that generates all Gerber and drill files for that design
- **output/** — Contains the generated files (created by the script)

## Gerber Generation Toolchain

**Recommended Library**: `gerber` (PyPI) or `pcb-tools` for RS-274X format support.

**Installation**:
```bash
pip install gerber
```

**Output File Conventions**:
- `copper_top.gbr` — Top copper layer (F.Cu)
- `copper_bottom.gbr` — Bottom copper layer (B.Cu), if 2-layer
- `edge_cuts.gbr` — Board outline/edge cut layer
- `silkscreen_top.gbr` — Top silkscreen (F.SilkS), for labels and reference designators
- `drill.drl` — Excellon format drill file for plated and non-plated holes

**Validation**: Use `gerbv` (install via `brew install gerbv` on macOS) to visually inspect Gerber files:
```bash
gerbv designs/01_battery_bulb/output/*.gbr designs/01_battery_bulb/output/*.drl
```

## Common Commands

**Generate a single design**:
```bash
python designs/01_battery_bulb/generate.py
```

**Generate all designs**:
```bash
python generate_all.py
```

**View generated Gerber files**:
```bash
gerbv designs/01_battery_bulb/output/*.gbr
```

## Design Specifications

### 01_battery_bulb
A minimal circuit: 9V battery powers an incandescent light bulb via a momentary-contact push button. All components are through-hole; single copper layer. Demonstrates basic Gerber generation and hole placement.

### 02_led_resistor
An LED circuit with current-limiting resistors in an array, controlled by a logic IC (e.g., 74HC595 shift register). Slightly more complex than 01 — introduces surface-mount components and multi-layer considerations. Demonstrates shift register sequencing logic on PCB.

### 03_christmas_lights
A microcontroller-based (e.g., ATtiny85) PWM-driven LED array with a shift register for row/column addressing. The PCB design supports non-trivial LED patterns (e.g., chasing, breathing, alternating). Firmware is not in scope; this repository generates the PCB layout only.

## Key Implementation Notes

- **Component Placement**: Use real-world component footprints (SOIC-8, DIP-8, 0603 resistors, etc.). The `gerber` library supports programmatic footprint definition.
- **Trace Routing**: Manually define traces in the copper layer. Ensure adequate spacing and clearances (typically 5-10 mils for hobbyist fabs).
- **Drill Placement**: All holes must be defined in the Excellon drill file with correct diameters for mounting and component leads.
- **Testing**: Always validate generated files with `gerbv` before sending to a fabricator. Check for short circuits, missing traces, and correct layer alignment.
