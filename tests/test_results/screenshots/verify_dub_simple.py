#!/usr/bin/env python3
"""
Verify arrival at Dub folder - Simple Display 2 screenshot capture
Uses screencapture command for Display 2 (HP monitor with Traktor)
"""

import subprocess
import os
import json
from pathlib import Path
from PIL import Image

def capture_display_2(output_path: str, max_size_kb: int = 200) -> dict:
    """
    Capture screenshot from Display 2 using screencapture command

    Args:
        output_path: Path to save the screenshot
        max_size_kb: Maximum file size in KB

    Returns:
        dict with capture results
    """
    result = {
        "screenshot_captured": False,
        "screenshot_size_kb": 0,
        "current_folder": "unknown",
        "navigation_successful": False,
        "verification": "error",
        "error": None
    }

    try:
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # First capture to temp PNG (Display 2 is -D 2)
        temp_png = output_path.replace('.jpg', '_temp.png')

        print(f"Capturing Display 2 to temp file: {temp_png}")

        # Use screencapture with -D 2 for second display
        cmd = ['screencapture', '-D', '2', '-t', 'png', temp_png]

        subprocess.run(cmd, capture_output=True, text=True, check=True)

        if not os.path.exists(temp_png):
            result["error"] = "screencapture failed to create file"
            print(f"ERROR: {result['error']}")
            return result

        print(f"✓ Screenshot captured: {temp_png}")

        # Get original size
        original_size_kb = os.path.getsize(temp_png) / 1024
        print(f"Original PNG size: {original_size_kb:.1f}KB")

        # Open with PIL and compress to JPEG
        print(f"Compressing to meet {max_size_kb}KB target...")

        img = Image.open(temp_png)

        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img

        # Iteratively compress
        quality = 85
        min_quality = 40

        while quality >= min_quality:
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            size_kb = os.path.getsize(output_path) / 1024

            print(f"Quality {quality}: {size_kb:.1f}KB")

            if size_kb <= max_size_kb:
                result["screenshot_captured"] = True
                result["screenshot_size_kb"] = round(size_kb, 1)
                result["verification"] = "screenshot captured, awaiting analysis"

                print(f"✓ Compressed screenshot saved: {output_path}")
                print(f"✓ Final size: {size_kb:.1f}KB")

                # Clean up temp file
                os.remove(temp_png)
                print(f"✓ Temp file removed")
                break

            quality -= 5

        if not result["screenshot_captured"]:
            result["error"] = f"Could not compress below {max_size_kb}KB"
            print(f"ERROR: {result['error']}")

    except subprocess.CalledProcessError as e:
        result["error"] = f"screencapture failed: {e.stderr}"
        print(f"ERROR: {result['error']}")

    except Exception as e:
        result["error"] = f"Exception: {str(e)}"
        print(f"ERROR: {result['error']}")
        import traceback
        traceback.print_exc()

    return result


def main():
    """Main execution"""
    output_path = "/Users/Fiore/dj/tests/test_results/screenshots/verify_dub_arrival.jpg"

    print("=" * 60)
    print("VERIFYING ARRIVAL AT DUB FOLDER")
    print("=" * 60)
    print(f"Output: {output_path}")
    print(f"Max size: 200KB")
    print()

    # Capture screenshot
    result = capture_display_2(output_path, max_size_kb=200)

    print()
    print("=" * 60)
    print("CAPTURE RESULTS")
    print("=" * 60)
    print(json.dumps(result, indent=2))

    # Save result to JSON
    json_path = "/Users/Fiore/dj/tests/test_results/screenshots/verify_dub_arrival.json"
    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nResults saved to: {json_path}")

    return result


if __name__ == "__main__":
    main()
