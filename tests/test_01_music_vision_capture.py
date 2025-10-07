#!/usr/bin/env python3
"""
TEST 01: Music Vision Navigator - Screenshot Capture with Compression
Tests screenshot capture on both displays with strict 200KB size validation.
"""

import subprocess
from PIL import Image
import os
from pathlib import Path
from datetime import datetime

# Test configuration
TEST_ID = "01"
TEST_NAME = "music_vision_capture"
MAX_SIZE_KB = 200
RESULTS_DIR = Path(__file__).parent / "test_results"
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"

def setup_test():
    """Create test directories"""
    RESULTS_DIR.mkdir(exist_ok=True)
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    print(f"✅ Test directories: {RESULTS_DIR}")

def capture_display_compressed(display_num=1, max_size_kb=200, output_path=None):
    """
    Capture a display with automatic compression to stay under size limit.

    Args:
        display_num: Display number (1=primary, 2=secondary on macOS)
        max_size_kb: Maximum file size in KB (default 200KB)
        output_path: Optional output path

    Returns:
        Path to compressed screenshot or None if failed
    """
    timestamp = int(datetime.now().timestamp())

    if output_path is None:
        output_path = SCREENSHOTS_DIR / f"display_{display_num}_{timestamp}.jpg"
    else:
        output_path = Path(output_path)

    raw_path = SCREENSHOTS_DIR / f"display_{display_num}_{timestamp}_raw.jpg"

    # Capture using macOS screencapture
    print(f"\n📸 Capturing display {display_num}...")
    result = subprocess.run(
        ['screencapture', '-D', str(display_num), '-t', 'jpg', str(raw_path)],
        capture_output=True,
        timeout=10
    )

    if result.returncode != 0:
        print(f"❌ Screenshot failed: {result.stderr.decode()}")
        return None

    # Compress aggressively
    try:
        with Image.open(raw_path) as img:
            original_size_kb = os.path.getsize(raw_path) / 1024
            print(f"📊 Original: {original_size_kb:.1f} KB ({img.width}x{img.height})")

            # Start with aggressive settings
            max_width = 1280
            quality = 40

            iteration = 0
            while iteration < 10:  # Safety limit
                iteration += 1

                # Resize if needed
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_size = (max_width, int(img.height * ratio))
                    resized = img.resize(new_size, Image.Resampling.LANCZOS)
                else:
                    resized = img

                # Save with compression
                resized.save(output_path, 'JPEG', quality=quality, optimize=True)

                size_kb = os.path.getsize(output_path) / 1024
                print(f"🔧 Iter {iteration}: {size_kb:.1f} KB (quality={quality}, {resized.width}x{resized.height})")

                if size_kb <= max_size_kb:
                    print(f"✅ Compression successful: {size_kb:.1f} KB")
                    break

                # More aggressive compression
                if quality > 25:
                    quality -= 5
                elif max_width > 640:
                    max_width = int(max_width * 0.8)
                    quality = 40  # Reset quality when resizing
                else:
                    print(f"⚠️ Cannot compress below {size_kb:.1f} KB")
                    break

    except Exception as e:
        print(f"❌ Compression error: {e}")
        raw_path.unlink(missing_ok=True)
        return None

    # Clean up raw
    raw_path.unlink(missing_ok=True)

    final_size_kb = os.path.getsize(output_path) / 1024

    if final_size_kb > max_size_kb:
        print(f"❌ FAILED: Screenshot {final_size_kb:.1f} KB exceeds {max_size_kb}KB limit")
        print(f"❌ DO NOT ANALYZE THIS FILE")
        output_path.unlink()  # Delete oversized file
        return None

    print(f"✅ Final screenshot: {final_size_kb:.1f} KB")
    return output_path

def test_both_displays():
    """Test screenshot capture on both displays"""
    results = {
        'display_1': None,
        'display_2': None
    }

    print("\n" + "="*70)
    print("TESTING DISPLAY 1 (Primary - Retina)")
    print("="*70)
    results['display_1'] = capture_display_compressed(display_num=1, max_size_kb=MAX_SIZE_KB)

    print("\n" + "="*70)
    print("TESTING DISPLAY 2 (Secondary - HP)")
    print("="*70)
    results['display_2'] = capture_display_compressed(display_num=2, max_size_kb=MAX_SIZE_KB)

    return results

def save_test_report(results):
    """Save test results to markdown"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = RESULTS_DIR / f"test_{TEST_ID}_{TEST_NAME}_report.md"

    display1_status = "✅ PASSED" if results['display_1'] else "❌ FAILED"
    display2_status = "✅ PASSED" if results['display_2'] else "❌ FAILED"

    display1_size = ""
    display2_size = ""

    if results['display_1']:
        size_kb = os.path.getsize(results['display_1']) / 1024
        with Image.open(results['display_1']) as img:
            display1_size = f"{size_kb:.1f} KB ({img.width}x{img.height})"

    if results['display_2']:
        size_kb = os.path.getsize(results['display_2']) / 1024
        with Image.open(results['display_2']) as img:
            display2_size = f"{size_kb:.1f} KB ({img.width}x{img.height})"

    content = f"""# Test {TEST_ID}: {TEST_NAME.replace('_', ' ').title()}

**Date**: {timestamp}
**Overall Status**: {'✅ PASSED' if results['display_1'] and results['display_2'] else '⚠️ PARTIAL' if results['display_1'] or results['display_2'] else '❌ FAILED'}

## Test Objective
Verify music-vision-navigator agent can capture screenshots from both displays with automatic compression under 200KB limit.

## Results

### Display 1 (Primary - Retina): {display1_status}
- File: `{results['display_1'].name if results['display_1'] else 'N/A'}`
- Size: {display1_size if display1_size else 'Failed to capture'}
- Max allowed: {MAX_SIZE_KB} KB

### Display 2 (Secondary - HP Traktor): {display2_status}
- File: `{results['display_2'].name if results['display_2'] else 'N/A'}`
- Size: {display2_size if display2_size else 'Failed to capture'}
- Max allowed: {MAX_SIZE_KB} KB

## Key Findings

### Compression Strategy
1. Start with 1280px width max, quality=40
2. Iteratively reduce quality (down to 25) or resize further
3. Abort if cannot compress below limit
4. Delete oversized files automatically

### Size Validation
✅ All screenshots validated before analysis
✅ Oversized files rejected and deleted
✅ music-vision-navigator agent updated with compression logic

## Next Steps
1. {'✅ Display 2 screenshot ready for Traktor analysis' if results['display_2'] else '❌ Need to fix Display 2 capture'}
2. Test music-vision-navigator agent with compressed screenshots
3. Verify agent respects 200KB size limit

## Agent Modifications
- Added `capture_display_compressed()` function to music-vision-navigator.md
- Added CRITICAL size validation rule (200KB max)
- Agent now rejects oversized files automatically

## Test Results Storage
- Screenshots: `{SCREENSHOTS_DIR}`
- Report: `{report_path.name}`
"""

    with open(report_path, 'w') as f:
        f.write(content)

    print(f"\n✅ Test report saved: {report_path}")
    return report_path

def main():
    """Run the test"""
    print(f"\n{'='*70}")
    print(f"TEST {TEST_ID}: {TEST_NAME.upper()}")
    print(f"MAX SIZE LIMIT: {MAX_SIZE_KB} KB")
    print(f"{'='*70}\n")

    # Setup
    setup_test()

    # Test both displays
    results = test_both_displays()

    # Save report
    report_path = save_test_report(results)

    # Summary
    print(f"\n{'='*70}")
    print(f"TEST {TEST_ID} COMPLETED")
    print(f"{'='*70}")

    if results['display_1']:
        print(f"✅ Display 1: {os.path.getsize(results['display_1']) / 1024:.1f} KB")
    else:
        print(f"❌ Display 1: FAILED")

    if results['display_2']:
        print(f"✅ Display 2: {os.path.getsize(results['display_2']) / 1024:.1f} KB")
    else:
        print(f"❌ Display 2: FAILED")

    print(f"\n📄 Report: {report_path}")

    success = results['display_1'] is not None and results['display_2'] is not None
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
