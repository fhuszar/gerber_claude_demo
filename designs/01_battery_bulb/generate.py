#!/usr/bin/env python3
"""
Generate Gerber and drill files for the Simple Battery & Bulb circuit.

This design includes:
- 9V battery connector (2 pads)
- Momentary push-button switch (4 pads in rectangle)
- Light bulb socket (2 pads)
- Simple traces connecting components in series
"""

import os
import sys

# Add parent directory to path for gerber_utils import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from gerber_utils import GerberFile, DrillFile, mm_to_inch

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create output files
copper_top = GerberFile("copper_top")
edge_cuts = GerberFile("edge_cuts")
silkscreen = GerberFile("silkscreen_top")
drill = DrillFile()

# Design dimensions (in mm)
BOARD_WIDTH = 100
BOARD_HEIGHT = 50

# Convert to inches
BOARD_W_IN = mm_to_inch(BOARD_WIDTH)
BOARD_H_IN = mm_to_inch(BOARD_HEIGHT)

# Component pad positions (in mm)
# Battery connector: top-left, 2 pads with 0.1" spacing
BATT_X1_MM, BATT_Y1_MM = 10, 40
BATT_X2_MM, BATT_Y2_MM = 12.7, 40  # 0.1" spacing

# Push-button: center area, 4 pads in rectangle
BTN_X1_MM, BTN_Y1_MM = 35, 30
BTN_X2_MM, BTN_Y2_MM = 40, 30
BTN_X3_MM, BTN_Y3_MM = 40, 35
BTN_X4_MM, BTN_Y4_MM = 35, 35

# Light bulb socket: right side, GU10 spacing
BULB_X1_MM, BULB_Y1_MM = 85, 40
BULB_X2_MM, BULB_Y2_MM = 85, 25

# Convert positions to inches
def mm_xy(x_mm, y_mm):
    return (mm_to_inch(x_mm), mm_to_inch(y_mm))

BATT_X1, BATT_Y1 = mm_xy(BATT_X1_MM, BATT_Y1_MM)
BATT_X2, BATT_Y2 = mm_xy(BATT_X2_MM, BATT_Y2_MM)
BTN_X1, BTN_Y1 = mm_xy(BTN_X1_MM, BTN_Y1_MM)
BTN_X2, BTN_Y2 = mm_xy(BTN_X2_MM, BTN_Y2_MM)
BTN_X3, BTN_Y3 = mm_xy(BTN_X3_MM, BTN_Y3_MM)
BTN_X4, BTN_Y4 = mm_xy(BTN_X4_MM, BTN_Y4_MM)
BULB_X1, BULB_Y1 = mm_xy(BULB_X1_MM, BULB_Y1_MM)
BULB_X2, BULB_Y2 = mm_xy(BULB_X2_MM, BULB_Y2_MM)

# === COPPER LAYER ===

# Define apertures
pad_circle_100mil = copper_top.add_aperture("circle", 0.1)      # 0.1" diameter
pad_circle_63mil = copper_top.add_aperture("circle", 0.063)     # 0.063" for switch
pad_circle_125mil = copper_top.add_aperture("circle", 0.125)    # 0.125" for bulb
trace_aperture = copper_top.add_aperture("circle", 0.01)        # 10-mil trace width

# Add pads for battery connector (0.1" holes)
copper_top.select_aperture(pad_circle_100mil)
copper_top.flash(BATT_X1, BATT_Y1)
copper_top.flash(BATT_X2, BATT_Y2)

# Add pads for push-button (0.063" holes)
copper_top.select_aperture(pad_circle_63mil)
copper_top.flash(BTN_X1, BTN_Y1)
copper_top.flash(BTN_X2, BTN_Y2)
copper_top.flash(BTN_X3, BTN_Y3)
copper_top.flash(BTN_X4, BTN_Y4)

# Add pads for bulb socket (0.125" holes)
copper_top.select_aperture(pad_circle_125mil)
copper_top.flash(BULB_X1, BULB_Y1)
copper_top.flash(BULB_X2, BULB_Y2)

# Draw traces connecting components (simplified: single lines)
copper_top.select_aperture(trace_aperture)
# Trace: Battery+ → Button pin1 → Bulb+ → Button pin2 → Battery-
copper_top.move_to(BATT_X1, BATT_Y1)
copper_top.line_to(BTN_X1, BTN_Y1)  # Battery to button
copper_top.move_to(BTN_X2, BTN_Y2)
copper_top.line_to(BULB_X1, BULB_Y1)  # Button to bulb
copper_top.move_to(BULB_X2, BULB_Y2)
copper_top.line_to(BATT_X2, BATT_Y2)  # Bulb to ground

# === EDGE CUTS LAYER ===
edge_cuts.select_aperture(edge_cuts.add_aperture("circle", 0.01))
# Draw board outline rectangle
edge_cuts.draw_rectangle(0, 0, BOARD_W_IN, BOARD_H_IN)

# === SILKSCREEN LAYER ===
silk_pad = silkscreen.add_aperture("circle", 0.02)
silkscreen.select_aperture(silk_pad)
# Label pads (note: actual text rendering would require a text aperture,
# simplified here with markers)
# This is a placeholder; real silkscreen would use special text commands

# === DRILL FILE ===
# Battery connector holes
drill.add_hole(BATT_X1, BATT_Y1, 0.1)
drill.add_hole(BATT_X2, BATT_Y2, 0.1)

# Push-button holes
drill.add_hole(BTN_X1, BTN_Y1, 0.063)
drill.add_hole(BTN_X2, BTN_Y2, 0.063)
drill.add_hole(BTN_X3, BTN_Y3, 0.063)
drill.add_hole(BTN_X4, BTN_Y4, 0.063)

# Bulb socket holes
drill.add_hole(BULB_X1, BULB_Y1, 0.125)
drill.add_hole(BULB_X2, BULB_Y2, 0.125)

# === WRITE FILES ===
copper_top.write_file(os.path.join(OUTPUT_DIR, "copper_top.gbr"))
edge_cuts.write_file(os.path.join(OUTPUT_DIR, "edge_cuts.gbr"))
silkscreen.write_file(os.path.join(OUTPUT_DIR, "silkscreen_top.gbr"))
drill.write_file(os.path.join(OUTPUT_DIR, "drill.drl"))

print("✓ Generated Gerber files for Design 01 (Battery & Bulb)")
print(f"  Output directory: {OUTPUT_DIR}")
print(f"  Files created:")
print(f"    - copper_top.gbr")
print(f"    - edge_cuts.gbr")
print(f"    - silkscreen_top.gbr")
print(f"    - drill.drl")
