#!/usr/bin/env python3
"""
Generate PNG previews of Gerber designs using PIL/Pillow.
Creates simple visual representations without requiring gerbv.
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
    },
    '02_led_resistor': {
        'name': 'LED Resistor Array',
        'width_mm': 75,
        'height_mm': 50,
        'bg_color': (187, 222, 251),  # Light blue
        'board_outline': (13, 71, 161),  # Dark blue
        'pad_color': (76, 175, 80),  # Green
        'pad_outline': (27, 94, 32),  # Dark green
    },
    '03_christmas_lights': {
        'name': 'Christmas Light Controller',
        'width_mm': 100,
        'height_mm': 75,
        'bg_color': (200, 230, 201),  # Light green
        'board_outline': (56, 142, 60),  # Dark green
        'pad_color': (244, 67, 54),  # Red
        'pad_outline': (183, 28, 28),  # Dark red
    }
}

def parse_gerber_positions(gbr_file):
    """Extract aperture positions from Gerber file."""
    positions = []
    try:
        with open(gbr_file, 'r') as f:
            content = f.read()
        pattern = r'X(\d+)Y(\d+)D03'
        matches = re.findall(pattern, content)
        for x_str, y_str in matches:
            x_inch = int(x_str) / 1e5
            y_inch = int(y_str) / 1e5
            positions.append((x_inch, y_inch))
    except:
        pass
    return positions

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
    except:
        pass
    return positions

def generate_png(design_name, design_info):
    """Generate a PNG rendering of the design."""
    design_path = os.path.join(DESIGNS_DIR, design_name, 'output')

    # PNG settings
    scale = 4  # pixels per mm
    width_px = design_info['width_mm'] * scale
    height_px = design_info['height_mm'] * scale
    pad_radius = 5  # pixels

    # Create image
    img = Image.new('RGB', (width_px, height_px), design_info['bg_color'])
    draw = ImageDraw.Draw(img)

    # Draw board outline
    draw.rectangle(
        [0, 0, width_px - 1, height_px - 1],
        outline=design_info['board_outline'],
        width=3
    )

    # Parse copper pads
    copper_file = os.path.join(design_path, 'copper_top.gbr')
    if os.path.exists(copper_file):
        positions = parse_gerber_positions(copper_file)
        for x_inch, y_inch in positions[:40]:  # Limit visualization
            x_mm = x_inch * 25.4
            y_mm = y_inch * 25.4

            if 0 <= x_mm <= design_info['width_mm'] and 0 <= y_mm <= design_info['height_mm']:
                x_px = int(x_mm * scale)
                y_px = int(y_mm * scale)
                draw.ellipse(
                    [x_px - pad_radius, y_px - pad_radius, x_px + pad_radius, y_px + pad_radius],
                    fill=design_info['pad_color'],
                    outline=design_info['pad_outline'],
                    width=2
                )

    # Parse drill holes
    drill_file = os.path.join(design_path, 'drill.drl')
    if os.path.exists(drill_file):
        positions = parse_drill_positions(drill_file)
        for x_coord, y_coord in positions[:40]:
            x_mm = x_coord * 25.4
            y_mm = y_coord * 25.4

            if 0 <= x_mm <= design_info['width_mm'] and 0 <= y_mm <= design_info['height_mm']:
                x_px = int(x_mm * scale)
                y_px = int(y_mm * scale)
                draw.ellipse(
                    [x_px - pad_radius + 1, y_px - pad_radius + 1, x_px + pad_radius - 1, y_px + pad_radius - 1],
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
        print(f"✗ Failed: {e}")
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
