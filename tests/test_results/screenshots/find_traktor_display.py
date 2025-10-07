#!/usr/bin/env python3
"""
Find which display has Traktor - capture all displays to identify the correct one
"""

import subprocess
import os
import json
from pathlib import Path
from PIL import Image

def capture_display(display_num: int, output_dir: str) -> dict:
    """Capture a specific display"""
    result = {
        "display": display_num,
        "captured": False,
        "path": None,
        "size_kb": 0,
        "error": None
    }

    try:
        output_path = f"{output_dir}/display_{display_num}.jpg"
        temp_png = f"{output_dir}/display_{display_num}_temp.png"

        # Capture with screencapture
        cmd = ['screencapture', '-D', str(display_num), '-t', 'png', temp_png]
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)

        if not os.path.exists(temp_png):
            result["error"] = "File not created"
            return result

        # Compress to JPEG
        img = Image.open(temp_png)

        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img

        # Save with moderate compression
        img.save(output_path, 'JPEG', quality=75, optimize=True)

        result["captured"] = True
        result["path"] = output_path
        result["size_kb"] = round(os.path.getsize(output_path) / 1024, 1)

        # Clean up temp
        os.remove(temp_png)

    except subprocess.TimeoutExpired:
        result["error"] = "Timeout - display might not exist"
    except subprocess.CalledProcessError as e:
        result["error"] = f"screencapture failed: {e.stderr}"
    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    """Try to capture all displays"""
    output_dir = "/Users/Fiore/dj/tests/test_results/screenshots"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("SEARCHING FOR TRAKTOR DISPLAY")
    print("=" * 60)
    print()

    results = []

    # Try displays 1-4
    for display_num in range(1, 5):
        print(f"Trying Display {display_num}...", end=" ")
        result = capture_display(display_num, output_dir)
        results.append(result)

        if result["captured"]:
            print(f"✓ Captured ({result['size_kb']}KB)")
            print(f"   Saved to: {result['path']}")
        else:
            print(f"✗ {result['error']}")
        print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    captured_displays = [r for r in results if r["captured"]]
    print(f"Found {len(captured_displays)} display(s)")
    print()

    if captured_displays:
        print("NEXT STEPS:")
        print("1. Open each screenshot to find which has Traktor:")
        for r in captured_displays:
            print(f"   open {r['path']}")
        print()
        print("2. Once you identify the correct display, update the capture script")
        print("   to use that display number")

    # Save results
    json_path = f"{output_dir}/display_search_results.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {json_path}")


if __name__ == "__main__":
    main()
