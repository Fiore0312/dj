#!/usr/bin/env python3
"""
Quick Dub Folder Finder

Captures PRIMARY display, finds "Dub" folder in Traktor browser,
provides immediate navigation instructions.
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import subprocess
import os
import time

def capture_primary_display():
    """Capture PRIMARY display using macOS screencapture"""
    timestamp = int(time.time())
    output_path = f"/Users/Fiore/dj/screenshots/primary_{timestamp}.png"

    # Create directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        # -m flag captures main display only
        cmd = ['screencapture', '-m', '-t', 'png', output_path]
        subprocess.run(cmd, check=True)

        print(f"✅ PRIMARY display captured: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
        return None

def find_folders_in_screenshot(image_path):
    """Extract text and find folders using OCR"""
    try:
        # Load image
        image = cv2.imread(image_path)

        # Convert to RGB for OCR
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)

        # OCR with bounding boxes
        ocr_data = pytesseract.image_to_data(
            pil_image,
            config='--oem 3 --psm 6',
            output_type=pytesseract.Output.DICT
        )

        folders = []
        n_boxes = len(ocr_data['text'])

        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            confidence = float(ocr_data['conf'][i])

            # Filter for folder-like text
            if confidence > 30 and len(text) > 2:
                y = ocr_data['top'][i]
                h = ocr_data['height'][i]
                y_center = y + h // 2

                folders.append({
                    'name': text,
                    'confidence': confidence,
                    'y_center': y_center,
                    'bbox': (ocr_data['left'][i], y, ocr_data['width'][i], h)
                })

        # Sort by vertical position
        folders.sort(key=lambda f: f['y_center'])

        return folders

    except Exception as e:
        print(f"❌ OCR failed: {e}")
        return []

def find_dub_navigation(folders):
    """Find Dub folder and calculate navigation steps"""
    print(f"\n🔍 Found {len(folders)} text items:")

    dub_folder = None
    dub_index = -1

    # Display all detected text
    for i, folder in enumerate(folders):
        name = folder['name']
        conf = folder['confidence']
        print(f"  {i+1:2d}. {name:<20} (confidence: {conf:.1f})")

        # Check for Dub folder
        if 'dub' in name.lower() or name.lower() == 'dub':
            dub_folder = folder
            dub_index = i
            print(f"      ⭐ DUB FOLDER FOUND!")

    if dub_folder:
        print(f"\n✅ DUB FOLDER LOCATED:")
        print(f"   Position: #{dub_index + 1} in list")
        print(f"   Confidence: {dub_folder['confidence']:.1f}%")
        print(f"\n📋 NAVIGATION INSTRUCTION:")
        print(f"   🔸 Press DOWN arrow {dub_index} times to reach 'Dub' folder")
        print(f"   🔸 Then press ENTER to select")

        return dub_index, dub_folder
    else:
        print(f"\n❌ 'Dub' folder not found in visible text")
        print("   Try scrolling or checking if browser pane is visible")
        return -1, None

def main():
    """Quick execution to find Dub folder"""
    print("🎯 FINDING DUB FOLDER IN TRAKTOR BROWSER")
    print("=" * 45)

    # Step 1: Capture primary display
    print("\n📸 Capturing PRIMARY display...")
    screenshot = capture_primary_display()

    if not screenshot:
        return

    # Step 2: Find folders with OCR
    print("\n🔍 Analyzing screenshot for folder names...")
    folders = find_folders_in_screenshot(screenshot)

    if not folders:
        print("❌ No text detected. Ensure Traktor browser is visible.")
        return

    # Step 3: Find Dub folder and get navigation
    steps, dub_folder = find_dub_navigation(folders)

    print(f"\n📊 SUMMARY:")
    print(f"   Screenshot: {screenshot}")
    print(f"   Text items found: {len(folders)}")
    print(f"   Dub folder: {'Found' if dub_folder else 'Not found'}")

    if dub_folder:
        print(f"   🎯 ACTION: Press DOWN {steps} times, then ENTER")

if __name__ == "__main__":
    main()