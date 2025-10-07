#!/usr/bin/env python3
"""
Primary Display Screenshot Capture for Traktor Browser Navigation

This script captures screenshots from the PRIMARY display (where Traktor runs)
instead of secondary displays, then uses OCR to locate folder structures.

Key Features:
- Multi-display detection and primary display targeting
- OCR text extraction for folder navigation
- Visual debugging with annotated screenshots
- Step counting for navigation instructions
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import subprocess
import json
import os
from typing import List, Dict, Tuple, Optional
import time
from dataclasses import dataclass

@dataclass
class DisplayInfo:
    """Information about a display"""
    index: int
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    is_primary: bool
    name: str

@dataclass
class FolderItem:
    """Detected folder item with position"""
    name: str
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    y_center: int

class PrimaryDisplayCapture:
    """Handles primary display detection and screenshot capture"""

    def __init__(self):
        self.displays = self._detect_displays()
        self.primary_display = self._find_primary_display()
        print(f"Detected {len(self.displays)} displays")
        print(f"Primary display: {self.primary_display.name if self.primary_display else 'Not found'}")

    def _detect_displays(self) -> List[DisplayInfo]:
        """Detect all available displays on macOS"""
        try:
            # Use system_profiler to get display information
            cmd = ['system_profiler', 'SPDisplaysDataType', '-json']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            display_data = json.loads(result.stdout)

            displays = []

            # Also get screen resolution info using screencapture
            cmd_screens = ['screencapture', '-l']
            screens_result = subprocess.run(cmd_screens, capture_output=True, text=True)

            # For macOS, we'll use a simpler approach with screencapture
            # Get main screen dimensions
            cmd_main = ['system_profiler', 'SPDisplaysDataType', '-json']
            result = subprocess.run(cmd_main, capture_output=True, text=True, check=True)

            # For now, create a primary display entry
            # We'll use screencapture which captures the main display by default
            primary = DisplayInfo(
                index=0,
                bounds=(0, 0, 1920, 1080),  # Will be adjusted after capture
                is_primary=True,
                name="Primary Display"
            )
            displays.append(primary)

            return displays

        except Exception as e:
            print(f"Error detecting displays: {e}")
            # Fallback to single primary display
            return [DisplayInfo(0, (0, 0, 1920, 1080), True, "Primary Display")]

    def _find_primary_display(self) -> Optional[DisplayInfo]:
        """Find the primary display"""
        for display in self.displays:
            if display.is_primary:
                return display
        return self.displays[0] if self.displays else None

    def capture_primary_display(self, output_path: str = None) -> str:
        """Capture screenshot of primary display only"""
        if not output_path:
            timestamp = int(time.time())
            output_path = f"/Users/Fiore/dj/screenshots/primary_display_{timestamp}.png"

        # Create screenshots directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            # Use screencapture with -m flag to capture main display only
            cmd = ['screencapture', '-m', '-t', 'png', output_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if os.path.exists(output_path):
                print(f"✅ Primary display captured: {output_path}")

                # Get actual image dimensions
                with Image.open(output_path) as img:
                    width, height = img.size
                    if self.primary_display:
                        self.primary_display.bounds = (0, 0, width, height)

                return output_path
            else:
                raise Exception("Screenshot file was not created")

        except subprocess.CalledProcessError as e:
            print(f"❌ Screenshot capture failed: {e}")
            print(f"Error output: {e.stderr}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

class TraktorBrowserOCR:
    """OCR analysis for Traktor browser interface"""

    def __init__(self):
        # Configure Tesseract for better text recognition
        self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_ '

    def extract_folder_structure(self, image_path: str) -> List[FolderItem]:
        """Extract folder names and positions from Traktor browser"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")

            # Convert to RGB for PIL
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)

            # Get detailed OCR data with bounding boxes
            ocr_data = pytesseract.image_to_data(
                pil_image,
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )

            folders = []

            # Process OCR results
            n_boxes = len(ocr_data['text'])
            for i in range(n_boxes):
                text = ocr_data['text'][i].strip()
                confidence = float(ocr_data['conf'][i])

                # Filter for potential folder names
                if (confidence > 30 and
                    len(text) > 2 and
                    text.replace(' ', '').replace('-', '').replace('_', '').isalnum()):

                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]

                    folder = FolderItem(
                        name=text,
                        bbox=(x, y, w, h),
                        confidence=confidence,
                        y_center=y + h // 2
                    )
                    folders.append(folder)

            # Sort by vertical position (y_center)
            folders.sort(key=lambda f: f.y_center)

            print(f"✅ Extracted {len(folders)} potential folder names")
            for folder in folders:
                print(f"  - {folder.name} (confidence: {folder.confidence:.1f})")

            return folders

        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")
            return []

    def find_target_folder(self, folders: List[FolderItem], target: str) -> Optional[FolderItem]:
        """Find target folder in the list"""
        target_lower = target.lower()

        # Try exact match first
        for folder in folders:
            if folder.name.lower() == target_lower:
                return folder

        # Try partial match
        for folder in folders:
            if target_lower in folder.name.lower() or folder.name.lower() in target_lower:
                return folder

        return None

    def calculate_navigation_steps(self, folders: List[FolderItem], current_pos: str, target: str) -> Dict:
        """Calculate navigation steps from current position to target"""
        current_folder = self.find_target_folder(folders, current_pos)
        target_folder = self.find_target_folder(folders, target)

        result = {
            'current_found': current_folder is not None,
            'target_found': target_folder is not None,
            'current_folder': current_folder,
            'target_folder': target_folder,
            'steps': 0,
            'direction': None,
            'instructions': []
        }

        if current_folder and target_folder:
            current_index = folders.index(current_folder)
            target_index = folders.index(target_folder)

            steps = target_index - current_index
            result['steps'] = abs(steps)

            if steps > 0:
                result['direction'] = 'down'
                result['instructions'] = [f"Press DOWN arrow {abs(steps)} times to reach '{target}'"]
            elif steps < 0:
                result['direction'] = 'up'
                result['instructions'] = [f"Press UP arrow {abs(steps)} times to reach '{target}'"]
            else:
                result['instructions'] = [f"Already on '{target}' folder"]

        return result

    def create_annotated_screenshot(self, image_path: str, folders: List[FolderItem],
                                  target_folder: Optional[FolderItem] = None) -> str:
        """Create annotated screenshot showing detected folders"""
        try:
            # Load image
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)

            # Create drawing context
            draw = ImageDraw.Draw(pil_image)

            # Try to use a better font
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            except:
                font = ImageFont.load_default()

            # Draw bounding boxes and labels for all folders
            for i, folder in enumerate(folders):
                x, y, w, h = folder.bbox

                # Color coding
                if target_folder and folder.name.lower() == target_folder.name.lower():
                    color = (255, 0, 0)  # Red for target
                    thickness = 3
                else:
                    color = (0, 255, 0)  # Green for others
                    thickness = 2

                # Draw rectangle
                draw.rectangle([x, y, x + w, y + h], outline=color, width=thickness)

                # Draw label with index and name
                label = f"{i+1}: {folder.name}"
                draw.text((x, y - 20), label, fill=color, font=font)

            # Save annotated image
            annotated_path = image_path.replace('.png', '_annotated.png')
            pil_image.save(annotated_path)

            print(f"✅ Annotated screenshot saved: {annotated_path}")
            return annotated_path

        except Exception as e:
            print(f"❌ Failed to create annotated screenshot: {e}")
            return image_path

def main():
    """Main execution function"""
    print("🎯 PRIMARY DISPLAY TRAKTOR BROWSER NAVIGATION")
    print("=" * 50)

    # Initialize capture system
    capture = PrimaryDisplayCapture()
    ocr = TraktorBrowserOCR()

    # Capture primary display
    print("\n📸 Capturing primary display...")
    try:
        screenshot_path = capture.capture_primary_display()
        print(f"Screenshot saved: {screenshot_path}")
    except Exception as e:
        print(f"❌ Failed to capture screenshot: {e}")
        return

    # Extract folder structure
    print("\n🔍 Analyzing folder structure with OCR...")
    folders = ocr.extract_folder_structure(screenshot_path)

    if not folders:
        print("❌ No folders detected. Check if Traktor browser is visible.")
        return

    # Look for target folder
    target = "Dub"
    current = "Music"  # Assumed current position

    print(f"\n🎯 Searching for '{target}' folder...")
    target_folder = ocr.find_target_folder(folders, target)

    if target_folder:
        print(f"✅ Found '{target}' folder!")
        print(f"   Position: {folders.index(target_folder) + 1} in list")
        print(f"   Confidence: {target_folder.confidence:.1f}%")
    else:
        print(f"❌ '{target}' folder not found in visible list")
        print("Available folders:")
        for i, folder in enumerate(folders):
            print(f"  {i+1}. {folder.name}")

    # Calculate navigation steps
    print(f"\n🧭 Calculating navigation from '{current}' to '{target}'...")
    navigation = ocr.calculate_navigation_steps(folders, current, target)

    print(f"Current folder found: {navigation['current_found']}")
    print(f"Target folder found: {navigation['target_found']}")

    if navigation['instructions']:
        print("\n📋 NAVIGATION INSTRUCTIONS:")
        for instruction in navigation['instructions']:
            print(f"   🔸 {instruction}")

    # Create annotated screenshot
    print("\n🖼️  Creating annotated screenshot...")
    annotated_path = ocr.create_annotated_screenshot(screenshot_path, folders, target_folder)

    print(f"\n✅ Analysis complete!")
    print(f"   Original screenshot: {screenshot_path}")
    print(f"   Annotated screenshot: {annotated_path}")

    return screenshot_path, folders, navigation

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()