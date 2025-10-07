#!/usr/bin/env python3
"""
Simple Primary Display Capture

Captures PRIMARY display (where Traktor runs) for manual inspection.
No OCR required - just visual verification of correct display capture.
"""

import subprocess
import os
import time

def capture_primary_display():
    """Capture PRIMARY display using macOS screencapture"""
    timestamp = int(time.time())
    output_path = f"/Users/Fiore/dj/screenshots/primary_display_{timestamp}.png"

    # Create directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        print("🎯 Capturing PRIMARY display (where Traktor should be visible)...")

        # Use screencapture with -m flag to capture main display only
        # This avoids capturing secondary terminal displays
        cmd = ['screencapture', '-m', '-t', 'png', output_path]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        if os.path.exists(output_path):
            print(f"✅ SUCCESS: Primary display captured")
            print(f"📸 Screenshot saved to: {output_path}")

            # Get image dimensions for verification
            stat = os.stat(output_path)
            file_size = stat.st_size

            print(f"📊 File info:")
            print(f"   - Size: {file_size:,} bytes")
            print(f"   - Time: {time.ctime(stat.st_mtime)}")

            print(f"\n🔍 NEXT STEPS:")
            print(f"   1. Open screenshot to verify it shows Traktor browser")
            print(f"   2. Look for 'Music' folder and genre subfolders")
            print(f"   3. Count how many folders down 'Dub' appears")
            print(f"   4. Use that count for DOWN arrow key presses")

            print(f"\n💡 To open screenshot:")
            print(f"   open \"{output_path}\"")

            return output_path

        else:
            print("❌ ERROR: Screenshot file was not created")
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Screenshot command failed")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Error: {e.stderr}")
        return None

    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {e}")
        return None

def show_display_info():
    """Show information about display setup"""
    print("🖥️  DISPLAY CAPTURE INFO:")
    print("=" * 40)
    print("This script uses 'screencapture -m' which captures:")
    print("✅ The MAIN/PRIMARY display only")
    print("❌ NOT secondary displays (like terminal screens)")
    print()
    print("If Traktor Pro 3 is running on your primary display,")
    print("the screenshot should show the Traktor interface.")
    print()

def main():
    """Main execution"""
    print("🎯 PRIMARY DISPLAY SCREENSHOT TOOL")
    print("=" * 40)

    show_display_info()

    # Capture the screenshot
    screenshot_path = capture_primary_display()

    if screenshot_path:
        print(f"\n🎉 CAPTURE COMPLETE!")
        print(f"Screenshot: {screenshot_path}")

        # Ask if user wants to open it immediately
        print(f"\n❓ Open screenshot now? (y/n): ", end="")
        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                subprocess.run(['open', screenshot_path])
                print("📖 Screenshot opened in default image viewer")
        except KeyboardInterrupt:
            print("\nSkipped opening screenshot")

    else:
        print(f"\n❌ CAPTURE FAILED")
        print("Possible issues:")
        print("- Screen recording permissions not granted")
        print("- screencapture command not available")
        print("- File system permissions issue")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()