#!/usr/bin/env python3
"""
Render Gerber files as PNG images using gerbv.
"""

import os
import subprocess
import sys

DESIGNS_DIR = os.path.join(os.path.dirname(__file__), 'designs')
DESIGNS = [
    '01_battery_bulb',
    '02_led_resistor',
    '03_christmas_lights',
]

def render_design(design_name):
    """Render a single design's Gerber files to PNG."""
    design_path = os.path.join(DESIGNS_DIR, design_name, 'output')

    if not os.path.exists(design_path):
        print(f"✗ Output directory not found: {design_path}")
        return False

    # Find all .gbr files in the design output directory
    gbr_files = sorted([f for f in os.listdir(design_path) if f.endswith('.gbr')])

    if not gbr_files:
        print(f"✗ No Gerber files found in {design_path}")
        return False

    # Also include drill file if present
    drl_file = os.path.join(design_path, 'drill.drl')
    render_files = [os.path.join(design_path, f) for f in gbr_files]
    if os.path.exists(drl_file):
        render_files.append(drl_file)

    output_png = os.path.join(design_path, f'{design_name}_render.png')

    try:
        print(f"  Rendering {design_name}...")
        # Use gerbv with explicit export options (non-interactive)
        cmd = ['gerbv', '-dNEWER', '-x', 'png', '-o', output_png] + render_files
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0 and os.path.exists(output_png):
            file_size = os.path.getsize(output_png) / 1024
            print(f"  ✓ Created: {output_png} ({file_size:.1f} KB)")
            return True
        else:
            print(f"  ✗ gerbv failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Gerber File Rendering (gerbv)")
    print("=" * 60)
    print()

    failed = []
    for design in DESIGNS:
        if not render_design(design):
            failed.append(design)

    print()
    print("=" * 60)
    if not failed:
        print("✓ All designs rendered successfully!")
    else:
        print(f"✗ {len(failed)} design(s) failed to render")
        sys.exit(1)

if __name__ == '__main__':
    main()
