#!/usr/bin/env python3
"""
Generate Gerber and drill files for the LED Resistor Array with Shift Register.

This design includes:
- 74HC595 8-bit shift register (SOIC-16)
- 8 red 0603 LEDs
- 8 current-limiting resistors (0603)
- 2 decoupling capacitors (0603)
- 1 pull-down resistor (0603)
- 6-pin microcontroller connector
- Ground plane on bottom layer
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from gerber_utils import GerberFile, DrillFile, mm_to_inch, create_solder_mask, create_paste_layer

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create Gerber layers
copper_top = GerberFile("copper_top")
copper_bottom = GerberFile("copper_bottom")
edge_cuts = GerberFile("edge_cuts")
drill = DrillFile()

# Board dimensions (mm)
BOARD_WIDTH = 75
BOARD_HEIGHT = 50
BOARD_W_IN = mm_to_inch(BOARD_WIDTH)
BOARD_H_IN = mm_to_inch(BOARD_HEIGHT)

def mm_xy(x_mm, y_mm):
    return (mm_to_inch(x_mm), mm_to_inch(y_mm))

# Component placement (in mm)
# 74HC595 IC at center
IC_X, IC_Y = 37.5, 25  # Center of board

# 0603 component dimensions (approx)
# 0603 is 0.06" x 0.03" (1.5mm x 0.8mm)
COMP_PITCH = 1.27  # Standard 50-mil pitch for 0603s

# LED array (8 LEDs in 2 rows of 4)
LED_START_X = 15
LED_START_Y = 35
LED_SPACING_X = 5
LED_SPACING_Y = 5

# Resistor array (parallel to LEDs)
RES_START_X = 15
RES_START_Y = 20

# Decoupling capacitors (near IC)
CAP1_X, CAP1_Y = IC_X - 5, IC_Y + 8
CAP2_X, CAP2_Y = IC_X + 5, IC_Y + 8

# Pull-down resistor
PULLDOWN_X, PULLDOWN_Y = IC_X - 8, IC_Y - 8

# Connector (top of board, 2.54mm pitch)
CONN_X_START = 10
CONN_Y = 45
CONN_PITCH = mm_to_inch(2.54)

# === COPPER TOP LAYER ===

# 0603 pad-to-pad center distance: ~1.5mm (0.059")
PAD_0603_HALF = mm_to_inch(0.75)  # half of pad-to-pad distance

# Define apertures for SMD pads and through-holes
# 0603 pads: 0.04" x 0.03" (rectangular)
smd_pad_0603 = copper_top.add_aperture("rect", 0.04, 0.03)
via_small = copper_top.add_aperture("circle", 0.012)  # 0.012" = 0.3mm via
connector_hole = copper_top.add_aperture("circle", 0.04)

# Add IC pads (SOIC-16: pins 1-8 left side top-to-bottom, 9-16 right side bottom-to-top)
ic_pad = copper_top.add_aperture("rect", 0.024, 0.06)
copper_top.select_aperture(ic_pad)
ic_x, ic_y = mm_xy(IC_X, IC_Y)
# SOIC-16 pin pitch: 0.05" (1.27mm), body width ~0.3" between pad centers
for pin in range(1, 17):
    if pin <= 8:
        offset_y = (pin - 1) * 0.05 - 0.175  # pins 1-8 down left side
        copper_top.flash(ic_x - 0.15, ic_y + offset_y)
    else:
        offset_y = (16 - pin) * 0.05 - 0.175  # pins 9-16 up right side
        copper_top.flash(ic_x + 0.15, ic_y + offset_y)

# Add 0603 LED pads (8 total, 2 pads each)
copper_top.select_aperture(smd_pad_0603)
for i in range(4):
    for j in range(2):
        led_x = mm_to_inch(LED_START_X + i * LED_SPACING_X)
        led_y = mm_to_inch(LED_START_Y + j * LED_SPACING_Y)
        copper_top.flash(led_x - PAD_0603_HALF, led_y)  # pad 1 (anode)
        copper_top.flash(led_x + PAD_0603_HALF, led_y)  # pad 2 (cathode)

# Add 0603 resistor pads (8 total, 2 pads each)
for i in range(4):
    for j in range(2):
        res_x = mm_to_inch(RES_START_X + i * LED_SPACING_X)
        res_y = mm_to_inch(RES_START_Y + j * LED_SPACING_Y)
        copper_top.flash(res_x - PAD_0603_HALF, res_y)  # pad 1
        copper_top.flash(res_x + PAD_0603_HALF, res_y)  # pad 2

# Add capacitor pads (2 pads each)
for cap_x, cap_y in [(CAP1_X, CAP1_Y), (CAP2_X, CAP2_Y)]:
    cx, cy = mm_xy(cap_x, cap_y)
    copper_top.flash(cx - PAD_0603_HALF, cy)
    copper_top.flash(cx + PAD_0603_HALF, cy)

# Add pull-down resistor (2 pads)
px, py = mm_xy(PULLDOWN_X, PULLDOWN_Y)
copper_top.flash(px - PAD_0603_HALF, py)
copper_top.flash(px + PAD_0603_HALF, py)

# Add connector holes (6-pin, 2.54mm pitch)
copper_top.select_aperture(connector_hole)
for i in range(6):
    conn_x = mm_to_inch(CONN_X_START + i * 2.54)
    conn_y = mm_to_inch(CONN_Y)
    copper_top.flash(conn_x, conn_y)

# Add signal traces (simplified routing)
trace = copper_top.add_aperture("circle", 0.008)  # 8-mil trace
copper_top.select_aperture(trace)

# Connector to IC traces
ic_x_in, ic_y_in = mm_xy(IC_X, IC_Y)
conn_x_start_in = mm_to_inch(CONN_X_START)
conn_y_in = mm_to_inch(CONN_Y)

# VCC and GND traces to caps
copper_top.move_to(ic_x_in, ic_y_in)
copper_top.line_to(ic_x_in - 0.5, ic_y_in)
copper_top.move_to(ic_x_in - 0.5, ic_y_in)
copper_top.line_to(ic_x_in - 0.5, ic_y_in + 0.5)

# === COPPER BOTTOM LAYER (Ground Plane) ===
# Fill the bottom layer with a solid ground plane using region fill
copper_bottom.fill_rectangle(0, 0, BOARD_W_IN, BOARD_H_IN)

# Add vias for ground connection (distributed across board, both layers)
via_bottom = copper_bottom.add_aperture("circle", 0.012)
copper_bottom.select_aperture(via_bottom)
copper_top.select_aperture(via_small)
for x_via in [20, 35, 50, 65]:
    for y_via in [15, 30, 45]:
        copper_bottom.flash(mm_to_inch(x_via), mm_to_inch(y_via))
        copper_top.flash(mm_to_inch(x_via), mm_to_inch(y_via))

# === EDGE CUTS LAYER ===
edge_aperture = edge_cuts.add_aperture("circle", 0.01)
edge_cuts.select_aperture(edge_aperture)
edge_cuts.draw_rectangle(0, 0, BOARD_W_IN, BOARD_H_IN)

# === DRILL FILE ===
# Connector holes
for i in range(6):
    drill.add_hole(mm_to_inch(CONN_X_START + i * 2.54), mm_to_inch(CONN_Y), 0.035)

# Via holes (plated)
for x_via in [20, 35, 50, 65]:
    for y_via in [15, 30, 45]:
        drill.add_hole(mm_to_inch(x_via), mm_to_inch(y_via), 0.012)

# === SOLDER MASK ===
mask_top = create_solder_mask(copper_top)
mask_bottom = create_solder_mask(copper_bottom)

# === PASTE LAYER (SMD pads only: 0603 components and IC) ===
paste_top = create_paste_layer(copper_top, [smd_pad_0603, ic_pad])

# === WRITE FILES ===
copper_top.write_file(os.path.join(OUTPUT_DIR, "copper_top.gbr"))
copper_bottom.write_file(os.path.join(OUTPUT_DIR, "copper_bottom.gbr"))
edge_cuts.write_file(os.path.join(OUTPUT_DIR, "edge_cuts.gbr"))
mask_top.write_file(os.path.join(OUTPUT_DIR, "soldermask_top.gbr"))
mask_bottom.write_file(os.path.join(OUTPUT_DIR, "soldermask_bottom.gbr"))
paste_top.write_file(os.path.join(OUTPUT_DIR, "paste_top.gbr"))
drill.write_file(os.path.join(OUTPUT_DIR, "drill.drl"))

print("✓ Generated Gerber files for Design 02 (LED Resistor Array)")
print(f"  Output directory: {OUTPUT_DIR}")
print(f"  Files created:")
print(f"    - copper_top.gbr")
print(f"    - copper_bottom.gbr (ground plane)")
print(f"    - soldermask_top.gbr / soldermask_bottom.gbr")
print(f"    - paste_top.gbr")
print(f"    - edge_cuts.gbr")
print(f"    - drill.drl")
