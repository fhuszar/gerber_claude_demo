#!/usr/bin/env python3
"""
Generate PNG previews of Gerber designs using PIL/Pillow.
Creates visual representations showing pads, traces, and drill holes.
"""

import os
import re
from PIL import Image, ImageDraw

DESIGNS_DIR = os.path.join(os.path.dirname(__file__), 'designs')
DESIGNS = {
    '01_battery_bulb': {
        'name': 'Simple Battery & Bulb',
        'width_mm': 100,
        'height_mm': 50,
        'bg_color': (255, 224, 178),  # Light orange
        'board_outline': (51, 51, 51),  # Dark gray
        'pad_color': (255, 215, 0),  # Gold
        'pad_outline': (255, 140, 0),  # Dark orange
        'trace_color': (200, 160, 0),  # Darker gold
    },
    '02_led_resistor': {
        'name': 'LED Resistor Array',
        'width_mm': 75,
        'height_mm': 50,
        'bg_color': (187, 222, 251),  # Light blue
        'board_outline': (13, 71, 161),  # Dark blue
        'pad_color': (76, 175, 80),  # Green
        'pad_outline': (27, 94, 32),  # Dark green
        'trace_color': (56, 142, 60),  # Darker green
    },
    '03_christmas_lights': {
        'name': 'Christmas Light Controller',
        'width_mm': 100,
        'height_mm': 75,
        'bg_color': (200, 230, 201),  # Light green
        'board_outline': (56, 142, 60),  # Dark green
        'pad_color': (244, 67, 54),  # Red
        'pad_outline': (183, 28, 28),  # Dark red
        'trace_color': (211, 47, 47),  # Darker red
    }
}

# Rendering settings
SCALE = 8  # pixels per mm (doubled from 4)
PAD_RADIUS = 4  # pixels


def parse_gerber(gbr_file):
    """Extract pad positions (D03) and trace segments (D01/D02) from a Gerber file."""
    pads = []
    traces = []  # list of ((x1,y1), (x2,y2)) in inches
    current_pos = None

    try:
        with open(gbr_file, 'r') as f:
            content = f.read()

        # Match all X/Y coordinate commands
        for match in re.finditer(r'X(-?\d+)Y(-?\d+)D0([123])\*', content):
            x_inch = int(match.group(1)) / 1e5
            y_inch = int(match.group(2)) / 1e5
            d_code = int(match.group(3))

            if d_code == 3:  # Flash
                pads.append((x_inch, y_inch))
            elif d_code == 2:  # Move
                current_pos = (x_inch, y_inch)
            elif d_code == 1:  # Draw line
                if current_pos is not None:
                    traces.append((current_pos, (x_inch, y_inch)))
                current_pos = (x_inch, y_inch)
    except FileNotFoundError:
        pass

    return pads, traces


def parse_drill_positions(drl_file):
    """Extract drill positions from Excellon file."""
    positions = []
    try:
        with open(drl_file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            match = re.match(r'X(\d+)Y(\d+)', line.strip())
            if match:
                x_coord = int(match.group(1)) / 10000
                y_coord = int(match.group(2)) / 10000
                positions.append((x_coord, y_coord))
    except FileNotFoundError:
        pass
    return positions


def inch_to_px(x_inch, y_inch):
    """Convert inch coordinates to pixel coordinates."""
    x_mm = x_inch * 25.4
    y_mm = y_inch * 25.4
    return int(x_mm * SCALE), int(y_mm * SCALE)


def generate_png(design_name, design_info):
    """Generate a PNG rendering of the design."""
    design_path = os.path.join(DESIGNS_DIR, design_name, 'output')
    w_mm = design_info['width_mm']
    h_mm = design_info['height_mm']

    width_px = w_mm * SCALE
    height_px = h_mm * SCALE

    img = Image.new('RGB', (width_px, height_px), design_info['bg_color'])
    draw = ImageDraw.Draw(img)

    # Draw board outline
    draw.rectangle(
        [0, 0, width_px - 1, height_px - 1],
        outline=design_info['board_outline'],
        width=3
    )

    # Parse copper layer
    copper_file = os.path.join(design_path, 'copper_top.gbr')
    pads, traces = parse_gerber(copper_file)

    # Draw traces first (under pads)
    trace_color = design_info.get('trace_color', design_info['pad_outline'])
    for (x1, y1), (x2, y2) in traces:
        px1, py1 = inch_to_px(x1, y1)
        px2, py2 = inch_to_px(x2, y2)
        if all(0 <= v <= dim for v, dim in [(px1, width_px), (py1, height_px),
                                             (px2, width_px), (py2, height_px)]):
            draw.line([(px1, py1), (px2, py2)], fill=trace_color, width=2)

    # Draw pads (no cap — render all of them)
    for x_inch, y_inch in pads:
        x_mm = x_inch * 25.4
        y_mm = y_inch * 25.4
        if 0 <= x_mm <= w_mm and 0 <= y_mm <= h_mm:
            x_px = int(x_mm * SCALE)
            y_px = int(y_mm * SCALE)
            draw.ellipse(
                [x_px - PAD_RADIUS, y_px - PAD_RADIUS,
                 x_px + PAD_RADIUS, y_px + PAD_RADIUS],
                fill=design_info['pad_color'],
                outline=design_info['pad_outline'],
                width=1
            )

    # Parse and draw drill holes
    drill_file = os.path.join(design_path, 'drill.drl')
    for x_coord, y_coord in parse_drill_positions(drill_file):
        x_mm = x_coord * 25.4
        y_mm = y_coord * 25.4
        if 0 <= x_mm <= w_mm and 0 <= y_mm <= h_mm:
            x_px = int(x_mm * SCALE)
            y_px = int(y_mm * SCALE)
            r = PAD_RADIUS - 1
            draw.ellipse(
                [x_px - r, y_px - r, x_px + r, y_px + r],
                outline=(100, 100, 100),
                width=1
            )

    # Add title
    draw.text((20, 15), design_info['name'], fill=(0, 0, 0))

    # Save PNG
    output_png = os.path.join(design_path, f'{design_name}_preview.png')
    try:
        img.save(output_png, 'PNG')
        file_size = os.path.getsize(output_png) / 1024
        print(f"✓ Created: {output_png} ({file_size:.1f} KB)")
        return True
    except Exception as e:
        print(f"✗ Failed to save {output_png}: {e}")
        return False


def main():
    print("=" * 60)
    print("Generate PNG Previews")
    print("=" * 60)
    print()

    failed = []
    for design_name, design_info in DESIGNS.items():
        print(f"Rendering {design_name}...")
        if not generate_png(design_name, design_info):
            failed.append(design_name)

    print()
    print("=" * 60)
    if not failed:
        print("✓ All PNG previews generated!")
    else:
        print(f"✗ {len(failed)} design(s) failed")

if __name__ == '__main__':
    main()
