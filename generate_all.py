#!/usr/bin/env python3
"""
Master script to generate Gerber files for all PCB designs.
"""

import os
import subprocess
import sys

# Directory containing all designs
DESIGNS_DIR = os.path.join(os.path.dirname(__file__), 'designs')

# List of design directories
DESIGNS = [
    '01_battery_bulb',
    '02_led_resistor',
    '03_christmas_lights',
]

def main():
    print("=" * 60)
    print("PCB Gerber File Generator - All Designs")
    print("=" * 60)
    print()

    failed = []
    for design in DESIGNS:
        design_path = os.path.join(DESIGNS_DIR, design)
        generate_script = os.path.join(design_path, 'generate.py')

        if not os.path.exists(generate_script):
            print(f"✗ Design {design}: generate.py not found")
            failed.append(design)
            continue

        print(f"Generating {design}...")
        try:
            result = subprocess.run(
                [sys.executable, generate_script],
                cwd=design_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"✗ Error generating {design}:")
                print(result.stderr)
                failed.append(design)
        except Exception as e:
            print(f"✗ Exception in {design}: {e}")
            failed.append(design)

        print()

    print("=" * 60)
    if not failed:
        print("✓ All designs generated successfully!")
    else:
        print(f"✗ {len(failed)} design(s) failed:")
        for design in failed:
            print(f"  - {design}")
        sys.exit(1)

if __name__ == '__main__':
    main()
