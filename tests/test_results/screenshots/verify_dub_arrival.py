#!/usr/bin/env python3
"""
Verify arrival at Dub folder - Capture Display 2 screenshot with compression
"""

import Quartz
import LaunchServices
from PIL import Image
import io
import json
from pathlib import Path

def capture_display_2_compressed(output_path: str, max_size_kb: int = 200) -> dict:
    """
    Capture screenshot from Display 2 (HP monitor) with automatic compression.

    Args:
        output_path: Path to save the compressed screenshot
        max_size_kb: Maximum file size in KB (default: 200KB)

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
        # Get all online displays
        (err, active_displays, num_displays) = Quartz.CGGetActiveDisplayList(10, None, None)

        if err != 0 or num_displays < 2:
            result["error"] = f"Error getting displays. Code: {err}, Displays found: {num_displays}"
            print(f"ERROR: {result['error']}")
            return result

        print(f"Found {num_displays} displays")
        print(f"Display IDs: {active_displays[:num_displays]}")

        # Display 2 is usually index 1 (second display)
        display_id = active_displays[1]
        print(f"Capturing from Display ID: {display_id}")

        # Capture the display
        image_ref = Quartz.CGDisplayCreateImage(display_id)
        if image_ref is None:
            result["error"] = "Failed to capture display image"
            print(f"ERROR: {result['error']}")
            return result

        # Get dimensions
        width = Quartz.CGImageGetWidth(image_ref)
        height = Quartz.CGImageGetHeight(image_ref)
        print(f"Captured image: {width}x{height}")

        # Convert CGImage to PIL Image
        bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)
        data_provider = Quartz.CGImageGetDataProvider(image_ref)
        pixel_data = Quartz.CGDataProviderCopyData(data_provider)

        # Create PIL Image from raw data
        pil_image = Image.frombytes(
            "RGBA",
            (width, height),
            pixel_data,
            "raw",
            "BGRA",
            bytes_per_row
        )

        # Convert RGBA to RGB (remove alpha channel)
        if pil_image.mode == 'RGBA':
            rgb_image = Image.new('RGB', pil_image.size, (255, 255, 255))
            rgb_image.paste(pil_image, mask=pil_image.split()[3])
            pil_image = rgb_image

        # Compress iteratively to meet size requirement
        quality = 85
        min_quality = 40

        print(f"Compressing to meet {max_size_kb}KB target...")

        while quality >= min_quality:
            # Save to bytes buffer
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=quality, optimize=True)
            size_bytes = buffer.tell()
            size_kb = size_bytes / 1024

            print(f"Quality {quality}: {size_kb:.1f}KB")

            if size_kb <= max_size_kb:
                # Success - save to file
                with open(output_path, 'wb') as f:
                    f.write(buffer.getvalue())

                result["screenshot_captured"] = True
                result["screenshot_size_kb"] = round(size_kb, 1)
                result["verification"] = "screenshot captured, awaiting analysis"

                print(f"✓ Screenshot saved: {output_path}")
                print(f"✓ Final size: {size_kb:.1f}KB")
                break

            # Reduce quality for next iteration
            quality -= 5

        if not result["screenshot_captured"]:
            result["error"] = f"Could not compress below {max_size_kb}KB (minimum quality {min_quality} reached)"
            print(f"ERROR: {result['error']}")

    except Exception as e:
        result["error"] = f"Exception during capture: {str(e)}"
        print(f"ERROR: {result['error']}")
        import traceback
        traceback.print_exc()

    return result


def main():
    """Main execution"""
    output_path = "/Users/Fiore/dj/tests/test_results/screenshots/verify_dub_arrival.jpg"

    # Ensure directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("VERIFYING ARRIVAL AT DUB FOLDER")
    print("=" * 60)
    print(f"Output: {output_path}")
    print(f"Max size: 200KB")
    print()

    # Capture screenshot
    result = capture_display_2_compressed(output_path, max_size_kb=200)

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
