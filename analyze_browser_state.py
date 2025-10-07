#!/usr/bin/env python3
"""
🔍 TRAKTOR BROWSER STATE ANALYZER
=================================
Quick analysis of current Traktor browser state to plan navigation to "Dub" folder.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def take_traktor_screenshot():
    """Take a screenshot of Traktor browser area"""
    try:
        from PIL import ImageGrab
        import cv2
        import numpy as np

        print("📸 Taking screenshot of Traktor browser...")

        # Take full screenshot first
        screenshot = ImageGrab.grab()
        screenshot_np = np.array(screenshot)

        # Save full screenshot for analysis
        cv2.imwrite("debug_screenshots/traktor_full_screenshot.png", cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR))
        print("✅ Full screenshot saved: debug_screenshots/traktor_full_screenshot.png")

        # Typical browser area for Traktor (left side panel)
        # These coordinates may need adjustment based on your screen setup
        browser_area = (50, 150, 300, 600)  # (x, y, width, height)

        # Crop to browser area
        x, y, w, h = browser_area
        browser_crop = screenshot.crop((x, y, x + w, y + h))
        browser_crop.save("debug_screenshots/traktor_browser_area.png")
        print("✅ Browser area crop saved: debug_screenshots/traktor_browser_area.png")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Screenshot error: {e}")
        return False

def analyze_screenshot_with_ocr():
    """Analyze screenshot using OCR to extract folder names"""
    try:
        import pytesseract
        from PIL import Image

        screenshot_path = "debug_screenshots/traktor_browser_area.png"
        if not os.path.exists(screenshot_path):
            print("❌ No browser screenshot found")
            return False

        print("🔍 Analyzing screenshot with OCR...")

        # Load and process image
        img = Image.open(screenshot_path)

        # OCR configuration for better text recognition
        ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 '

        # Extract text
        extracted_text = pytesseract.image_to_string(img, config=ocr_config)

        print("\n📋 EXTRACTED TEXT FROM BROWSER:")
        print("-" * 40)
        print(extracted_text)
        print("-" * 40)

        # Look for folder names
        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]

        print(f"\n📁 DETECTED FOLDER/FILE NAMES ({len(lines)} items):")
        for i, line in enumerate(lines):
            print(f"  {i+1}. {line}")

        # Check if we can see "Dub" or related folders
        music_related = ['Music', 'Electronic', 'Dub', 'House', 'Techno', 'Jazz']
        found_items = []

        for line in lines:
            for term in music_related:
                if term.lower() in line.lower():
                    found_items.append((line, term))

        if found_items:
            print(f"\n🎵 MUSIC-RELATED FOLDERS FOUND:")
            for found_line, matched_term in found_items:
                print(f"  ✅ '{found_line}' (matches: {matched_term})")
        else:
            print("\n⚠️ No music-related folders visible in current view")

        return True

    except ImportError as e:
        print(f"❌ OCR not available: {e}")
        return False
    except Exception as e:
        print(f"❌ OCR analysis error: {e}")
        return False

def create_navigation_plan():
    """Create navigation plan to reach Music -> Dub"""

    print("\n🗺️ NAVIGATION PLAN TO REACH MUSIC → DUB")
    print("=" * 50)

    plan = {
        "target_path": "Music → Dub",
        "strategy": "systematic_exploration",
        "steps": [
            {
                "step": 1,
                "action": "Analyze current position",
                "description": "Take screenshot and identify current folder/selection"
            },
            {
                "step": 2,
                "action": "Look for Music folder",
                "description": "Check if Music folder is visible in current view"
            },
            {
                "step": 3,
                "action": "Navigate to Music",
                "description": "Use UP/DOWN navigation to select Music folder, then EXPAND"
            },
            {
                "step": 4,
                "action": "Look for Dub subfolder",
                "description": "Navigate within Music folder to find Dub subfolder"
            },
            {
                "step": 5,
                "action": "Select Dub folder",
                "description": "Navigate to and select the Dub folder"
            }
        ],
        "midi_commands": {
            "navigate_up": "CC73",
            "navigate_down": "CC72",
            "expand_folder": "CC64",
            "collapse_folder": "CC64"
        }
    }

    for step_info in plan["steps"]:
        print(f"📋 Step {step_info['step']}: {step_info['action']}")
        print(f"    {step_info['description']}")

    print(f"\n🎛️ MIDI COMMANDS TO USE:")
    for action, cc in plan["midi_commands"].items():
        print(f"  {action.replace('_', ' ').title()}: {cc}")

    return plan

def main():
    """Main analysis execution"""
    print("🔍 TRAKTOR BROWSER STATE ANALYZER")
    print("=" * 40)

    # Ensure debug directory exists
    os.makedirs("debug_screenshots", exist_ok=True)

    # Step 1: Take screenshot
    print("\n📸 STEP 1: Taking screenshot...")
    screenshot_ok = take_traktor_screenshot()

    # Step 2: OCR Analysis
    if screenshot_ok:
        print("\n🔍 STEP 2: OCR Analysis...")
        ocr_ok = analyze_screenshot_with_ocr()

    # Step 3: Create navigation plan
    print("\n🗺️ STEP 3: Creating navigation plan...")
    plan = create_navigation_plan()

    print(f"\n✅ ANALYSIS COMPLETE")
    print("Next steps:")
    print("1. Review the screenshot: debug_screenshots/traktor_browser_area.png")
    print("2. Check OCR results above")
    print("3. Use the navigation plan to reach Music → Dub")
    print("4. Execute navigation with traktor_control.py MIDI commands")

if __name__ == "__main__":
    main()