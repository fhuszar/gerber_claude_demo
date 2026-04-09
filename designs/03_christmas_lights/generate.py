#!/usr/bin/env python3
"""
Generate Gerber and drill files for the Christmas Light Controller.

This design includes:
- ATtiny85 microcontroller (SOIC-8)
- 2× 74HC595 shift registers (SOIC-16 daisy-chained)
- 16 addressable 0603 LEDs (dual-color: red and green)
- 16 current-limiting resistors (0603)
- 3 decoupling capacitors (0603)
- 8MHz ceramic resonator (SMD)
- Momentary button (through-hole)
- USB Type-C connector or 5V barrel jack
- ISP 6-pin header for programming
- Extensive via array for ground distribution
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from gerber_utils import GerberFile, DrillFile, mm_to_inch

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create Gerber layers
copper_top = GerberFile("copper_top")
copper_bottom = GerberFile("copper_bottom")
edge_cuts = GerberFile("edge_cuts")
drill = DrillFile()

# Board dimensions (mm)
BOARD_WIDTH = 100
BOARD_HEIGHT = 75
BOARD_W_IN = mm_to_inch(BOARD_WIDTH)
BOARD_H_IN = mm_to_inch(BOARD_HEIGHT)

def mm_xy(x_mm, y_mm):
    return (mm_to_inch(x_mm), mm_to_inch(y_mm))

# === COMPONENT PLACEMENT ===

# Microcontroller (ATtiny85, SOIC-8) - center-left
MCU_X, MCU_Y = 25, 37.5

# Shift registers (2× 74HC595, SOIC-16) - right of MCU
IC1_X, IC1_Y = 55, 42  # First shift register
IC2_X, IC2_Y = 55, 18  # Second shift register (daisy-chained)

# LED arrays (8 red on top, 8 green on bottom)
LED_RED_START_X = 10
LED_RED_START_Y = 60
LED_GREEN_START_X = 10
LED_GREEN_START_Y = 5
LED_SPACING = 8

# Current-limiting resistor arrays (parallel to LEDs)
RES_RED_START_X = 10
RES_RED_START_Y = 50
RES_GREEN_START_X = 10
RES_GREEN_START_Y = 15

# Decoupling capacitors (near VCC)
CAP_MCU_X, CAP_MCU_Y = 20, 45
CAP_IC1_X, CAP_IC1_Y = 60, 50
CAP_IC2_X, CAP_IC2_Y = 60, 10

# Ceramic resonator (near MCU)
RES_X, RES_Y = 30, 25

# Input button (push-button, through-hole)
BUTTON_X, BUTTON_Y = 5, 30

# Power connector (USB/barrel jack, 3 pins)
PWR_X, PWR_Y = 95, 75

# ISP programming header (6-pin, 2.54mm pitch)
ISP_X, ISP_Y = 95, 25

# === COPPER TOP LAYER ===

# 0603 pad-to-pad center distance: ~1.5mm (0.059")
PAD_0603_HALF = mm_to_inch(0.75)

# Define apertures
smd_pad = copper_top.add_aperture("rect", 0.04, 0.03)  # 0603 SMD pad
ic_pad = copper_top.add_aperture("rect", 0.024, 0.06)   # SOIC IC pad
via = copper_top.add_aperture("circle", 0.012)
connector_hole = copper_top.add_aperture("circle", 0.045)
button_hole = copper_top.add_aperture("circle", 0.035)
trace_small = copper_top.add_aperture("circle", 0.006)  # 6-mil trace
trace_power = copper_top.add_aperture("circle", 0.012)  # 12-mil power trace

# Place ATtiny85 (SOIC-8: pins 1-4 left top-to-bottom, pins 5-8 right bottom-to-top)
copper_top.select_aperture(ic_pad)
mcu_x, mcu_y = mm_xy(MCU_X, MCU_Y)
# SOIC-8 pin pitch: 0.05" (1.27mm), body width ~0.2" between pad centers
for pin in range(1, 9):
    if pin <= 4:
        offset_y = (pin - 1) * 0.05 - 0.075  # pins 1-4 down left side
        copper_top.flash(mcu_x - 0.1, mcu_y + offset_y)
    else:
        offset_y = (8 - pin) * 0.05 - 0.075  # pins 5-8 up right side
        copper_top.flash(mcu_x + 0.1, mcu_y + offset_y)

# Place 74HC595 ICs (SOIC-16: pins 1-8 left top-to-bottom, 9-16 right bottom-to-top)
for ic_placement in [(IC1_X, IC1_Y), (IC2_X, IC2_Y)]:
    copper_top.select_aperture(ic_pad)
    ic_x, ic_y = mm_xy(ic_placement[0], ic_placement[1])
    for pin in range(1, 17):
        if pin <= 8:
            offset_y = (pin - 1) * 0.05 - 0.175
            copper_top.flash(ic_x - 0.15, ic_y + offset_y)
        else:
            offset_y = (16 - pin) * 0.05 - 0.175
            copper_top.flash(ic_x + 0.15, ic_y + offset_y)

# Place red LEDs (8 total, 0603, 2 pads each)
copper_top.select_aperture(smd_pad)
for i in range(8):
    led_x = mm_to_inch(LED_RED_START_X + i * LED_SPACING)
    led_y = mm_to_inch(LED_RED_START_Y)
    copper_top.flash(led_x - PAD_0603_HALF, led_y)  # anode
    copper_top.flash(led_x + PAD_0603_HALF, led_y)  # cathode

# Place green LEDs (8 total, 0603, 2 pads each)
for i in range(8):
    led_x = mm_to_inch(LED_GREEN_START_X + i * LED_SPACING)
    led_y = mm_to_inch(LED_GREEN_START_Y)
    copper_top.flash(led_x - PAD_0603_HALF, led_y)  # anode
    copper_top.flash(led_x + PAD_0603_HALF, led_y)  # cathode

# Place resistors (16 total, 0603, 2 pads each)
for i in range(8):
    # Red resistors
    res_x = mm_to_inch(RES_RED_START_X + i * LED_SPACING)
    res_y = mm_to_inch(RES_RED_START_Y)
    copper_top.flash(res_x - PAD_0603_HALF, res_y)
    copper_top.flash(res_x + PAD_0603_HALF, res_y)

    # Green resistors
    res_x = mm_to_inch(RES_GREEN_START_X + i * LED_SPACING)
    res_y = mm_to_inch(RES_GREEN_START_Y)
    copper_top.flash(res_x - PAD_0603_HALF, res_y)
    copper_top.flash(res_x + PAD_0603_HALF, res_y)

# Place decoupling capacitors (2 pads each)
for cap_x, cap_y in [(CAP_MCU_X, CAP_MCU_Y), (CAP_IC1_X, CAP_IC1_Y), (CAP_IC2_X, CAP_IC2_Y)]:
    cx, cy = mm_xy(cap_x, cap_y)
    copper_top.flash(cx - PAD_0603_HALF, cy)
    copper_top.flash(cx + PAD_0603_HALF, cy)

# Place ceramic resonator (2-pad SMD)
rx, ry = mm_xy(RES_X, RES_Y)
copper_top.flash(rx - PAD_0603_HALF, ry)
copper_top.flash(rx + PAD_0603_HALF, ry)

# Place button (through-hole)
copper_top.select_aperture(button_hole)
copper_top.flash(*mm_xy(BUTTON_X, BUTTON_Y))

# Place power connector
copper_top.select_aperture(connector_hole)
copper_top.flash(*mm_xy(PWR_X, PWR_Y))

# Place ISP header (6 pins, 2.54mm pitch)
for i in range(6):
    isp_x = mm_to_inch(ISP_X - i * 2.54)
    isp_y = mm_to_inch(ISP_Y)
    copper_top.flash(isp_x, isp_y)

# Draw key signal traces (simplified SPI bus)
copper_top.select_aperture(trace_small)
mcu_x_in, mcu_y_in = mm_xy(MCU_X, MCU_Y)
ic1_x_in, ic1_y_in = mm_xy(IC1_X, IC1_Y)
ic2_x_in, ic2_y_in = mm_xy(IC2_X, IC2_Y)

# MCU to first shift register (SPI signals)
copper_top.move_to(mcu_x_in, mcu_y_in)
copper_top.line_to(ic1_x_in - 0.5, ic1_y_in)

# First to second shift register (daisy-chain)
copper_top.move_to(ic1_x_in + 0.3, ic1_y_in - 1.2)
copper_top.line_to(ic2_x_in, ic2_y_in)

# === COPPER BOTTOM LAYER (Ground Plane) ===
# Fill the bottom layer with a solid ground plane using region fill
copper_bottom.fill_rectangle(0, 0, BOARD_W_IN, BOARD_H_IN)

# Add extensive via array for ground distribution
copper_bottom.select_aperture(via)
for x_via in [15, 25, 35, 45, 55, 65, 75, 85]:
    for y_via in [10, 25, 40, 55, 70]:
        copper_bottom.flash(mm_to_inch(x_via), mm_to_inch(y_via))

# === EDGE CUTS LAYER ===
edge = edge_cuts.add_aperture("circle", 0.01)
edge_cuts.select_aperture(edge)
edge_cuts.draw_rectangle(0, 0, BOARD_W_IN, BOARD_H_IN)

# === DRILL FILE ===

# Button hole
drill.add_hole(*mm_xy(BUTTON_X, BUTTON_Y), 0.035)

# Power connector holes (3-pin)
drill.add_hole(*mm_xy(PWR_X, PWR_Y), 0.045)
drill.add_hole(*mm_xy(PWR_X + 2.54, PWR_Y), 0.045)
drill.add_hole(*mm_xy(PWR_X + 5.08, PWR_Y), 0.045)

# ISP header holes (6-pin)
for i in range(6):
    isp_x = ISP_X - i * 2.54
    isp_y = ISP_Y
    drill.add_hole(mm_to_inch(isp_x), mm_to_inch(isp_y), 0.035)

# Via holes (distributed)
for x_via in [15, 25, 35, 45, 55, 65, 75, 85]:
    for y_via in [10, 25, 40, 55, 70]:
        drill.add_hole(mm_to_inch(x_via), mm_to_inch(y_via), 0.012)

# === WRITE FILES ===
copper_top.write_file(os.path.join(OUTPUT_DIR, "copper_top.gbr"))
copper_bottom.write_file(os.path.join(OUTPUT_DIR, "copper_bottom.gbr"))
edge_cuts.write_file(os.path.join(OUTPUT_DIR, "edge_cuts.gbr"))
drill.write_file(os.path.join(OUTPUT_DIR, "drill.drl"))

print("✓ Generated Gerber files for Design 03 (Christmas Light Controller)")
print(f"  Output directory: {OUTPUT_DIR}")
print(f"  Files created:")
print(f"    - copper_top.gbr (signals and components)")
print(f"    - copper_bottom.gbr (ground plane with vias)")
print(f"    - edge_cuts.gbr (board outline)")
print(f"    - drill.drl (plated and unplated holes)")
