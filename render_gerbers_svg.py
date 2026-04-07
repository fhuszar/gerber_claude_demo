#!/usr/bin/env python3
"""
Generate SVG visual renderings of Gerber designs.
Creates a simple visual representation showing board outline and key features.
"""

import os
import re

DESIGNS_DIR = os.path.join(os.path.dirname(__file__), 'designs')
DESIGNS = {
    '01_battery_bulb': {
        'name': 'Simple Battery & Bulb',
        'width_mm': 100,
        'height_mm': 50,
        'color': '#FFE0B2'
    },
    '02_led_resistor': {
        'name': 'LED Resistor Array',
        'width_mm': 75,
        'height_mm': 50,
        'color': '#BBDEFB'
    },
    '03_christmas_lights': {
        'name': 'Christmas Light Controller',
        'width_mm': 100,
        'height_mm': 75,
        'color': '#C8E6C9'
    }
}

def parse_gerber_positions(gbr_file):
    """Extract aperture positions from Gerber file for visualization."""
    positions = []

    try:
        with open(gbr_file, 'r') as f:
            content = f.read()

        # Find all flash commands (D03)
        pattern = r'X(\d+)Y(\d+)D03'
        matches = re.findall(pattern, content)

        for x_str, y_str in matches:
            # Gerber format is 2.5 (X and Y as integers, divide by 1e5 to get inches)
            x_inch = int(x_str) / 1e5
            y_inch = int(y_str) / 1e5
            positions.append((x_inch, y_inch))
    except:
        pass

    return positions

def generate_svg(design_name, design_info):
    """Generate an SVG rendering of the design."""
    design_path = os.path.join(DESIGNS_DIR, design_name, 'output')

    # Convert mm to SVG units (pixels at 96 DPI)
    scale = 3  # pixels per mm
    width_px = design_info['width_mm'] * scale
    height_px = design_info['height_mm'] * scale

    # Start SVG
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width_px}" height="{height_px}" viewBox="0 0 {design_info['width_mm']} {design_info['height_mm']}"
     xmlns="http://www.w3.org/2000/svg">
  <style>
    .board {{ fill: {design_info['color']}; stroke: #333; stroke-width: 0.5; }}
    .pad {{ fill: #FFD700; stroke: #FF8C00; stroke-width: 0.2; }}
    .text {{ font-family: monospace; font-size: 2; fill: #333; }}
  </style>

  <!-- Board outline -->
  <rect class="board" x="0" y="0" width="{design_info['width_mm']}" height="{design_info['height_mm']}" />

  <!-- Title -->
  <text class="text" x="5" y="15">{design_info['name']}</text>

  <!-- Component pads visualization -->
'''

    # Parse and visualize pads from copper layer
    copper_file = os.path.join(design_path, 'copper_top.gbr')
    if os.path.exists(copper_file):
        positions = parse_gerber_positions(copper_file)

        # Convert inches to mm and add pads
        for x_inch, y_inch in positions[:30]:  # Limit to first 30 for visualization
            x_mm = x_inch * 25.4
            y_mm = y_inch * 25.4

            if 0 <= x_mm <= design_info['width_mm'] and 0 <= y_mm <= design_info['height_mm']:
                svg += f'  <circle class="pad" cx="{x_mm}" cy="{y_mm}" r="0.8" />\n'

    # Parse drill positions
    drill_file = os.path.join(design_path, 'drill.drl')
    if os.path.exists(drill_file):
        try:
            with open(drill_file, 'r') as f:
                lines = f.readlines()

            # Simple drill parsing - extract X/Y coordinates
            for line in lines:
                match = re.match(r'X(\d+)Y(\d+)', line.strip())
                if match:
                    x_coord = int(match.group(1)) / 10000  # 2.4 format to inches
                    y_coord = int(match.group(2)) / 10000
                    x_mm = x_coord * 25.4
                    y_mm = y_coord * 25.4

                    if 0 <= x_mm <= design_info['width_mm'] and 0 <= y_mm <= design_info['height_mm']:
                        svg += f'  <circle class="pad" cx="{x_mm}" cy="{y_mm}" r="0.6" />\n'
        except:
            pass

    # Close SVG
    svg += '</svg>\n'

    # Write SVG file
    output_svg = os.path.join(design_path, f'{design_name}_schematic.svg')
    try:
        with open(output_svg, 'w') as f:
            f.write(svg)

        file_size = os.path.getsize(output_svg) / 1024
        print(f"✓ Created: {output_svg} ({file_size:.1f} KB)")
        return True
    except Exception as e:
        print(f"✗ Failed to write SVG: {e}")
        return False

def main():
    print("=" * 60)
    print("Gerber SVG Rendering")
    print("=" * 60)
    print()

    failed = []
    for design_name, design_info in DESIGNS.items():
        print(f"Rendering {design_name}...")
        if not generate_svg(design_name, design_info):
            failed.append(design_name)

    print()
    print("=" * 60)
    if not failed:
        print("✓ All designs rendered as SVG!")
    else:
        print(f"✗ {len(failed)} design(s) failed")

if __name__ == '__main__':
    main()
