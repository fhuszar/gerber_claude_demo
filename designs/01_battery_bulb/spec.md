# Design 01: Simple Battery & Bulb Circuit

## Specification

A minimal hand-wired circuit demonstrating basic Gerber file generation.

### Components

1. **Battery**: 9V (rectangular snap connector)
2. **Light Bulb**: Incandescent MR16 halogen bulb (GU10 socket)
3. **Switch**: Momentary push-button (SPST, normally-open)
4. **Wiring**: All through-hole connectors and component leads

### Circuit Topology

```
[+9V Battery] —— [Switch] —— [Light Bulb] —— [Ground Return] —— [-9V Battery]
```

### PCB Requirements

- **Layer Stack**: Single copper layer (top-side routing only)
- **Board Size**: 100mm × 50mm
- **Clearance**: 10-mil traces, 20-mil spacing
- **Mounting**: Through-hole mounting pads for battery snap, switch, and light socket
- **Silkscreen**: Label pads as "9V+", "GND", "SW" for clarity

### Holes

- Battery connector: 2 pads (0.1" spacing), 0.1" hole diameter
- Push-button terminals: 4 pads in a rectangle, 0.063" hole diameter
- Light socket: 2 pads (GU10 standard spacing), 0.125" hole diameter

### Manufacturing Notes

- Single-layer PCB suitable for hobbyist fabrication (e.g., FabLabs, JLCPCB with standard 1mm FR-4)
- No plated through-holes required; standard single-sided fabrication
- Minimum trace width: 10 mils (0.25mm)
- All copper on top layer only
