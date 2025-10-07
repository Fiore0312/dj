#!/usr/bin/env python3
"""
🎯 VISUAL BROWSER NAVIGATION - Jazz Folder Challenge Solver
=========================================================

Advanced visual browser navigation solution for Traktor Pro 3 using:
1. Computer Vision + OCR for reading folder names from screenshots
2. Intelligent pathfinding to locate target folders (like "Jazz")
3. Integration with existing traktor_control.py MIDI CC commands
4. Real-time visual feedback and debugging capabilities

KEY FEATURES:
- Solves the "Jazz folder navigation challenge" autonomously
- Uses PIL/OpenCV for screenshot capture of browser area
- OCR text extraction with pytesseract for folder name recognition
- MIDI commands: CC72 (tree down), CC73 (tree up), CC64 (expand/collapse)
- Systematic exploration algorithm with state tracking
- Visual debugging with annotated screenshots

TECHNICAL APPROACH:
- Screenshot browser area → OCR text extraction → Locate target → Navigate
- Handle both visible and hidden folders through systematic exploration
- State management for navigation history and position tracking
- Error handling and recovery from navigation failures

MIDI MAPPINGS USED:
- CC72: Browser Tree Down (browser_tree_down)
- CC73: Browser Tree Up (browser_tree_up)
- CC64: Browser Expand/Collapse (browser_expand_collapse)

Author: Enhanced Visual Navigation Agent
Date: 2025-10-06
"""

import time
import logging
import json
import os
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Computer Vision imports
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageGrab, ImageDraw, ImageFont
    import pytesseract
    VISION_AVAILABLE = True
    print("✅ Computer vision libraries loaded successfully")
except ImportError as e:
    VISION_AVAILABLE = False
    print(f"⚠️ Vision libraries unavailable: {e}")
    print("   Install with: pip install opencv-python pillow pytesseract")

# Local imports
try:
    from core.traktor_control import TraktorController, DeckID
    from core.config import DJConfig
    TRAKTOR_AVAILABLE = True
except ImportError as e:
    TRAKTOR_AVAILABLE = False
    print(f"⚠️ TraktorController unavailable: {e}")

logger = logging.getLogger(__name__)

@dataclass
class BrowserItem:
    """Browser item with enhanced position tracking and metadata"""
    name: str
    position: int
    is_folder: bool
    is_expanded: bool = False
    is_selected: bool = False
    confidence: float = 0.0
    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)  # (x, y, width, height)
    depth_level: int = 0  # Tree depth for hierarchy tracking
    parent_folder: Optional[str] = None
    visual_features: Dict = field(default_factory=dict)

@dataclass
class NavigationState:
    """Comprehensive navigation state tracking"""
    current_position: int = 0
    selected_item: Optional[BrowserItem] = None
    visible_items: List[BrowserItem] = field(default_factory=list)
    navigation_history: List[str] = field(default_factory=list)
    visited_folders: Set[str] = field(default_factory=set)
    search_path: List[str] = field(default_factory=list)
    target_found: bool = False
    last_screenshot_time: float = 0.0
    exploration_depth: int = 0
    max_depth_reached: int = 0
    folders_expanded: Set[str] = field(default_factory=set)

class NavigationCommand(Enum):
    """Navigation commands for browser control"""
    TREE_UP = "tree_up"      # CC73
    TREE_DOWN = "tree_down"  # CC72
    EXPAND = "expand"        # CC64 (high value)
    COLLAPSE = "collapse"    # CC64 (low value)

class VisualBrowserNavigator:
    """Advanced visual browser navigator with Jazz folder solving capabilities"""

    def __init__(self, traktor_controller: Optional[TraktorController] = None):
        """Initialize the visual browser navigator"""

        # Traktor integration
        self.traktor = traktor_controller
        if not self.traktor and TRAKTOR_AVAILABLE:
            print("🎛️ Initializing TraktorController...")
            config = DJConfig()  # Use default config
            self.traktor = TraktorController(config)

        # Navigation state
        self.nav_state = NavigationState()

        # Computer vision configuration
        self.browser_area = (50, 100, 400, 600)  # Default browser area (x, y, w, h)
        self.ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\(\)\[\]_-. '

        # Search parameters
        self.max_exploration_attempts = 100  # Max navigation attempts
        self.screenshot_delay = 0.3  # Delay between screenshots
        self.navigation_delay = 0.6  # Delay between navigation commands
        self.ocr_confidence_threshold = 40  # OCR confidence threshold

        # Debug settings
        self.debug_mode = True
        self.save_debug_screenshots = True
        self.debug_folder = "debug_screenshots"

        if self.save_debug_screenshots:
            os.makedirs(self.debug_folder, exist_ok=True)

        # Verify dependencies
        if not VISION_AVAILABLE:
            raise ImportError("❌ Computer vision libraries not available! Install opencv-python, pillow, pytesseract")

        if not TRAKTOR_AVAILABLE:
            raise ImportError("❌ TraktorController not available! Check core.traktor_control import")

        logger.info("🎯 Visual Browser Navigator initialized")

    def take_browser_screenshot(self) -> Optional[np.ndarray]:
        """Capture screenshot of browser area with enhanced error handling"""
        try:
            x, y, w, h = self.browser_area

            # Take screenshot
            screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h))

            # Convert to OpenCV format
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

            self.nav_state.last_screenshot_time = time.time()

            if self.debug_mode:
                logger.debug(f"📸 Screenshot captured: {w}x{h} pixels")

            return screenshot_cv

        except Exception as e:
            logger.error(f"❌ Screenshot capture failed: {e}")
            return None

    def extract_folder_names_with_ocr(self, image: np.ndarray) -> List[BrowserItem]:
        """Extract folder names using enhanced OCR with preprocessing"""
        try:
            # Preprocessing pipeline for better OCR accuracy
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Enhance contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)

            # Apply adaptive threshold for better text extraction
            binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 11, 2)

            # OCR extraction with detailed output
            ocr_data = pytesseract.image_to_data(
                binary,
                config=self.ocr_config,
                output_type=pytesseract.Output.DICT
            )

            items = []
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()

                if text and len(text) > 1:  # Filter out single characters and empty strings
                    confidence = int(ocr_data['conf'][i])

                    if confidence > self.ocr_confidence_threshold:
                        x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i],
                                     ocr_data['width'][i], ocr_data['height'][i])

                        # Enhanced detection algorithms
                        is_folder = self._detect_folder_type(image, (x, y, w, h))
                        is_selected = self._detect_selection_highlight(image, (x, y, w, h))
                        depth_level = self._estimate_tree_depth(image, x)

                        # Create browser item
                        item = BrowserItem(
                            name=text,
                            position=len(items),
                            is_folder=is_folder,
                            is_selected=is_selected,
                            confidence=confidence / 100.0,
                            bbox=(x, y, w, h),
                            depth_level=depth_level,
                            visual_features={
                                'text_color': self._analyze_text_color(image, (x, y, w, h)),
                                'background_color': self._analyze_background_color(image, (x, y, w, h))
                            }
                        )
                        items.append(item)

            # Update navigation state
            self.nav_state.visible_items = items
            selected_items = [item for item in items if item.is_selected]
            self.nav_state.selected_item = selected_items[0] if selected_items else None

            logger.info(f"🔍 OCR extracted {len(items)} items, {len(selected_items)} selected")

            return items

        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {e}")
            return []

    def _detect_folder_type(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> bool:
        """Enhanced folder detection using visual cues"""
        x, y, w, h = bbox

        # Check area to the left of text for folder icons
        icon_search_area = image[max(0, y-5):y+h+5, max(0, x-30):x]

        if icon_search_area.size == 0:
            return False

        # Convert to HSV for better color-based detection
        hsv = cv2.cvtColor(icon_search_area, cv2.COLOR_BGR2HSV)

        # Look for typical folder colors (yellow/orange range for folder icons)
        folder_color_lower = np.array([15, 80, 80])   # Yellow-orange lower bound
        folder_color_upper = np.array([35, 255, 255]) # Yellow-orange upper bound

        color_mask = cv2.inRange(hsv, folder_color_lower, folder_color_upper)
        folder_color_pixels = cv2.countNonZero(color_mask)

        # Also check for expansion arrows (small triangular shapes)
        # Look for edge patterns that might indicate expand/collapse arrows
        edges = cv2.Canny(icon_search_area, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Small triangular or arrow-like shapes
        arrow_like_shapes = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 5 < area < 50:  # Small shapes that could be arrows
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0:
                    solidity = area / hull_area
                    if 0.5 < solidity < 0.9:  # Moderate solidity typical of arrows
                        arrow_like_shapes += 1

        # Combine evidence: folder color OR arrow-like shapes
        has_folder_indicators = folder_color_pixels > 10 or arrow_like_shapes > 0

        return has_folder_indicators

    def _detect_selection_highlight(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> bool:
        """Enhanced selection detection using background color analysis"""
        x, y, w, h = bbox

        # Analyze background area around the text
        bg_margin = 5
        bg_area = image[max(0, y-bg_margin):min(image.shape[0], y+h+bg_margin),
                       max(0, x-bg_margin):min(image.shape[1], x+w+bg_margin)]

        if bg_area.size == 0:
            return False

        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(bg_area, cv2.COLOR_BGR2HSV)

        # Look for typical selection highlight colors
        # Blue range (common for selection highlights)
        blue_lower = np.array([100, 50, 50])
        blue_upper = np.array([130, 255, 255])

        # Cyan range (alternative selection color)
        cyan_lower = np.array([85, 50, 50])
        cyan_upper = np.array([100, 255, 255])

        # Create masks for both color ranges
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        cyan_mask = cv2.inRange(hsv, cyan_lower, cyan_upper)

        # Combine masks
        selection_mask = cv2.bitwise_or(blue_mask, cyan_mask)
        selection_pixels = cv2.countNonZero(selection_mask)

        # Calculate selection ratio
        total_pixels = bg_area.shape[0] * bg_area.shape[1]
        selection_ratio = selection_pixels / total_pixels if total_pixels > 0 else 0

        # Consider selected if significant portion is highlighted
        return selection_ratio > 0.15  # 15% threshold for selection detection

    def _estimate_tree_depth(self, image: np.ndarray, x_position: int) -> int:
        """Estimate tree hierarchy depth based on indentation and visual cues"""
        # Simple depth estimation based on horizontal position
        base_indent = 25        # Base left margin
        indent_per_level = 18   # Pixels per hierarchy level

        if x_position < base_indent:
            return 0

        estimated_depth = (x_position - base_indent) // indent_per_level
        return max(0, min(estimated_depth, 8))  # Cap at reasonable depth

    def _analyze_text_color(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int]:
        """Analyze the dominant text color in the bounding box"""
        x, y, w, h = bbox
        text_area = image[y:y+h, x:x+w]

        if text_area.size == 0:
            return (0, 0, 0)

        # Find the most common color (mode)
        pixels = text_area.reshape(-1, 3)
        unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
        dominant_color = unique_colors[np.argmax(counts)]

        return tuple(dominant_color)

    def _analyze_background_color(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int]:
        """Analyze the background color around the text"""
        x, y, w, h = bbox

        # Sample background areas around the text
        margin = 3
        bg_areas = []

        # Top area
        if y - margin > 0:
            bg_areas.append(image[y-margin:y, x:x+w])

        # Bottom area
        if y + h + margin < image.shape[0]:
            bg_areas.append(image[y+h:y+h+margin, x:x+w])

        # Combine all background areas
        if bg_areas:
            combined_bg = np.vstack(bg_areas)
            pixels = combined_bg.reshape(-1, 3)
            unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
            dominant_bg_color = unique_colors[np.argmax(counts)]
            return tuple(dominant_bg_color)

        return (128, 128, 128)  # Default gray

    def find_item_by_name(self, target_name: str, case_sensitive: bool = False, partial_match: bool = True) -> Optional[BrowserItem]:
        """Find item by name with flexible matching options"""
        search_name = target_name if case_sensitive else target_name.lower()

        best_match = None
        best_score = 0

        for item in self.nav_state.visible_items:
            item_name = item.name if case_sensitive else item.name.lower()

            if partial_match:
                # Partial match with scoring
                if search_name in item_name:
                    # Score based on match quality
                    score = len(search_name) / len(item_name) * item.confidence
                    if score > best_score:
                        best_score = score
                        best_match = item
            else:
                # Exact match
                if search_name == item_name:
                    return item

        return best_match

    def navigate_to_target_folder(self, target_name: str, max_attempts: Optional[int] = None) -> bool:
        """
        Main method to navigate to target folder (Jazz folder challenge solver)

        Advanced Algorithm:
        1. Take screenshot and scan current browser state
        2. Search for target in visible items
        3. If found, navigate directly to it
        4. If not found, systematically explore folders using breadth-first approach
        5. Track visited folders to avoid infinite loops
        6. Use smart expansion strategy for optimal search
        """
        logger.info(f"🎯 Starting Jazz folder challenge: Navigate to '{target_name}'")

        # Initialize search state
        self.nav_state.target_found = False
        self.nav_state.exploration_depth = 0
        self.nav_state.max_depth_reached = 0
        self.nav_state.visited_folders.clear()
        self.nav_state.folders_expanded.clear()

        attempts = max_attempts or self.max_exploration_attempts

        for attempt in range(attempts):
            logger.info(f"🔍 Search attempt {attempt + 1}/{attempts}")

            # Step 1: Capture and analyze current browser state
            if not self._scan_current_browser_state():
                logger.warning("⚠️ Failed to capture browser state, retrying...")
                time.sleep(self.screenshot_delay)
                continue

            # Step 2: Check if target is visible in current view
            target_item = self.find_item_by_name(target_name, case_sensitive=False, partial_match=True)

            if target_item:
                logger.info(f"✅ FOUND TARGET '{target_name}' at position {target_item.position}!")
                logger.info(f"   Full name: '{target_item.name}' (confidence: {target_item.confidence:.2f})")

                # Navigate to the target
                if self._navigate_to_item(target_item):
                    self.nav_state.target_found = True
                    logger.info(f"🏆 SUCCESS! Navigated to '{target_name}'!")
                    return True
                else:
                    logger.warning(f"⚠️ Found target but navigation failed, continuing search...")

            # Step 3: Target not visible, explore next area systematically
            exploration_success = self._explore_next_area_intelligent()

            if not exploration_success:
                logger.warning("🚫 No more areas to explore")
                break

            # Brief pause between attempts
            time.sleep(self.navigation_delay)

        logger.error(f"❌ Failed to find '{target_name}' after {attempts} attempts")
        return False

    def _scan_current_browser_state(self) -> bool:
        """Scan current browser state and extract all visible items"""
        screenshot = self.take_browser_screenshot()

        if screenshot is None:
            logger.error("❌ Failed to capture screenshot")
            return False

        items = self.extract_folder_names_with_ocr(screenshot)

        if self.save_debug_screenshots:
            self._save_debug_screenshot(screenshot, items)

        if self.debug_mode and items:
            self._log_current_browser_state(items)

        return len(items) > 0

    def _navigate_to_item(self, target_item: BrowserItem) -> bool:
        """Navigate to a specific item that's currently visible"""
        if not self.nav_state.selected_item:
            logger.warning("⚠️ No currently selected item detected, attempting first item selection")
            # Try to select the first item if none is selected
            if self.nav_state.visible_items:
                target_item = self.nav_state.visible_items[0]
            else:
                logger.error("❌ No items visible for navigation")
                return False

        current_pos = self.nav_state.selected_item.position if self.nav_state.selected_item else 0
        target_pos = target_item.position

        steps_needed = target_pos - current_pos
        logger.info(f"📍 Navigating from position {current_pos} to {target_pos} (steps: {steps_needed})")

        if steps_needed == 0:
            logger.info("✅ Already at target position")
            return True

        # Navigate step by step
        command = NavigationCommand.TREE_DOWN if steps_needed > 0 else NavigationCommand.TREE_UP
        steps = abs(steps_needed)

        success_count = 0
        for step in range(steps):
            if self._send_navigation_command(command):
                success_count += 1
                logger.debug(f"🔄 Navigation step {step + 1}/{steps} completed")
            else:
                logger.warning(f"⚠️ Navigation failed at step {step + 1}/{steps}")

            time.sleep(self.navigation_delay * 0.7)  # Slightly faster between steps

        # Consider successful if most steps worked
        return success_count >= (steps * 0.7)

    def _explore_next_area_intelligent(self) -> bool:
        """
        Intelligent exploration strategy for systematic folder search
        Returns True if exploration can continue, False if exhausted
        """
        # Strategy priorities:
        # 1. Expand unexplored folders at current level
        # 2. Navigate down to see more items
        # 3. Navigate up to explore different branches
        # 4. Backtrack if we've gone too deep

        # Priority 1: Expand unexplored folders
        if self._try_expand_unexplored_folders():
            logger.debug("📂 Expanded folder for exploration")
            return True

        # Priority 2: Navigate down to see more items
        if self._send_navigation_command(NavigationCommand.TREE_DOWN):
            logger.debug("🔽 Navigated down to explore more items")
            return True

        # Priority 3: Navigate up to explore different branches
        if self._send_navigation_command(NavigationCommand.TREE_UP):
            logger.debug("🔼 Navigated up to explore different branch")
            return True

        # Priority 4: Try collapsing current folder and moving to siblings
        if self._try_backtrack_and_explore_siblings():
            logger.debug("↩️ Backtracked to explore sibling folders")
            return True

        logger.debug("🚫 No more exploration options available")
        return False

    def _try_expand_unexplored_folders(self) -> bool:
        """Try to expand folders that haven't been explored yet"""
        for item in self.nav_state.visible_items:
            if (item.is_folder and
                item.name not in self.nav_state.visited_folders and
                item.name not in self.nav_state.folders_expanded):

                logger.info(f"📂 Attempting to expand folder: '{item.name}'")

                # Navigate to the folder first
                if self._navigate_to_item(item):
                    # Then expand it
                    if self._send_navigation_command(NavigationCommand.EXPAND):
                        self.nav_state.visited_folders.add(item.name)
                        self.nav_state.folders_expanded.add(item.name)
                        self.nav_state.exploration_depth += 1
                        self.nav_state.max_depth_reached = max(
                            self.nav_state.max_depth_reached,
                            self.nav_state.exploration_depth
                        )
                        return True
                    else:
                        logger.warning(f"⚠️ Failed to expand folder: '{item.name}'")
                else:
                    logger.warning(f"⚠️ Failed to navigate to folder: '{item.name}'")

        return False

    def _try_backtrack_and_explore_siblings(self) -> bool:
        """Try to collapse current folder and explore siblings"""
        if self.nav_state.exploration_depth > 0:
            logger.debug("↩️ Attempting backtrack by collapsing current level")

            if self._send_navigation_command(NavigationCommand.COLLAPSE):
                self.nav_state.exploration_depth = max(0, self.nav_state.exploration_depth - 1)
                return True

        return False

    def _send_navigation_command(self, command: NavigationCommand) -> bool:
        """Send navigation command using proper MIDI CC mappings from traktor_control.py"""
        if not self.traktor:
            logger.error("❌ No Traktor controller available")
            return False

        try:
            success = False

            if command == NavigationCommand.TREE_UP:
                # Use browser_tree_up from traktor_control.py (CC73)
                success = self.traktor.browser_tree_up()
                self.nav_state.navigation_history.append("TREE_UP")

            elif command == NavigationCommand.TREE_DOWN:
                # Use browser_tree_down from traktor_control.py (CC72)
                success = self.traktor.browser_tree_down()
                self.nav_state.navigation_history.append("TREE_DOWN")

            elif command == NavigationCommand.EXPAND:
                # Use browser expand/collapse (CC64) with high value for expand
                success = self.traktor._send_midi_command(1, 64, 127, "Expand folder")
                self.nav_state.navigation_history.append("EXPAND")

            elif command == NavigationCommand.COLLAPSE:
                # Use browser expand/collapse (CC64) with low value for collapse
                success = self.traktor._send_midi_command(1, 64, 1, "Collapse folder")
                self.nav_state.navigation_history.append("COLLAPSE")

            if success:
                logger.debug(f"✅ Navigation command sent: {command.value}")
                # Allow UI time to update
                time.sleep(self.navigation_delay)
            else:
                logger.warning(f"⚠️ Navigation command failed: {command.value}")

            return success

        except Exception as e:
            logger.error(f"❌ Navigation command error: {e}")
            return False

    def _save_debug_screenshot(self, screenshot: np.ndarray, items: List[BrowserItem]):
        """Save annotated debug screenshot with detected items"""
        try:
            debug_img = screenshot.copy()

            # Draw detection results
            for i, item in enumerate(items):
                x, y, w, h = item.bbox

                # Color coding
                if item.is_selected:
                    color = (0, 255, 0)      # Green for selected
                    thickness = 3
                elif item.is_folder:
                    color = (0, 165, 255)    # Orange for folders
                    thickness = 2
                else:
                    color = (255, 255, 255)  # White for files
                    thickness = 1

                # Draw bounding box
                cv2.rectangle(debug_img, (x, y), (x + w, y + h), color, thickness)

                # Draw label with item info
                label = f"{item.name}"
                confidence_text = f"({item.confidence:.2f})"

                # Label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                cv2.rectangle(debug_img,
                            (x, y - 25),
                            (x + label_size[0] + 50, y - 5),
                            color, -1)

                # Label text
                cv2.putText(debug_img, label, (x + 2, y - 12),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                cv2.putText(debug_img, confidence_text, (x + 2, y - 2),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)

            # Add navigation info overlay
            info_text = [
                f"Items: {len(items)}",
                f"Selected: {self.nav_state.selected_item.name if self.nav_state.selected_item else 'None'}",
                f"Depth: {self.nav_state.exploration_depth}",
                f"Commands: {len(self.nav_state.navigation_history)}"
            ]

            for i, text in enumerate(info_text):
                cv2.putText(debug_img, text, (10, 25 + i*20),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # Save with timestamp
            timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]  # Include milliseconds
            filename = f"{self.debug_folder}/browser_nav_{timestamp}.png"
            cv2.imwrite(filename, debug_img)

            logger.debug(f"📸 Debug screenshot saved: {filename}")

        except Exception as e:
            logger.error(f"❌ Failed to save debug screenshot: {e}")

    def _log_current_browser_state(self, items: List[BrowserItem]):
        """Log detailed browser state for debugging"""
        logger.debug("=" * 70)
        logger.debug(f"📊 BROWSER STATE ANALYSIS - {len(items)} items detected:")
        logger.debug(f"🎯 Target search depth: {self.nav_state.exploration_depth}")
        logger.debug(f"📁 Folders expanded: {len(self.nav_state.folders_expanded)}")
        logger.debug("-" * 70)

        for i, item in enumerate(items):
            icon = "📁" if item.is_folder else "📄"
            selected = "⭐" if item.is_selected else "  "
            depth_indicator = "  " * item.depth_level + "├─"
            confidence_bar = "●" * int(item.confidence * 10)

            logger.debug(f"{selected} {depth_indicator}{icon} {item.name}")
            logger.debug(f"     └─ conf:{item.confidence:.2f} {confidence_bar} pos:{item.position}")

        logger.debug("=" * 70)

    def get_navigation_status(self) -> Dict:
        """Get comprehensive navigation status for monitoring"""
        return {
            'target_found': self.nav_state.target_found,
            'visible_items_count': len(self.nav_state.visible_items),
            'selected_item': self.nav_state.selected_item.name if self.nav_state.selected_item else None,
            'current_depth': self.nav_state.exploration_depth,
            'max_depth_reached': self.nav_state.max_depth_reached,
            'folders_visited': len(self.nav_state.visited_folders),
            'folders_expanded': len(self.nav_state.folders_expanded),
            'navigation_commands_sent': len(self.nav_state.navigation_history),
            'last_screenshot_time': self.nav_state.last_screenshot_time,
            'browser_area': self.browser_area,
            'recent_commands': self.nav_state.navigation_history[-5:] if self.nav_state.navigation_history else []
        }

    def calibrate_browser_area(self, bbox: Optional[Tuple[int, int, int, int]] = None):
        """Calibrate browser screenshot area"""
        if bbox:
            x, y, w, h = bbox
            self.browser_area = (x, y, w, h)
            logger.info(f"🎯 Browser area calibrated to: {bbox}")

            # Test screenshot in new area
            test_screenshot = self.take_browser_screenshot()
            if test_screenshot is not None:
                logger.info("✅ Browser area calibration successful")
                return True
            else:
                logger.error("❌ Browser area calibration failed - screenshot test failed")
                return False
        else:
            logger.info("🎯 Current browser area: {}".format(self.browser_area))
            logger.info("   Use calibrate_browser_area((x, y, width, height)) to set new area")
            return True

    def reset_navigation_state(self):
        """Reset navigation state for fresh search"""
        self.nav_state = NavigationState()
        logger.info("🔄 Navigation state reset - ready for new search")

    def test_browser_connection(self) -> bool:
        """Test browser connection and basic functionality"""
        logger.info("🧪 Testing browser connection and functionality...")

        try:
            # Test 1: Screenshot capture
            logger.info("📸 Test 1: Screenshot capture...")
            screenshot = self.take_browser_screenshot()
            if screenshot is None:
                logger.error("❌ Screenshot capture failed")
                return False
            logger.info("✅ Screenshot capture working")

            # Test 2: OCR extraction
            logger.info("🔤 Test 2: OCR text extraction...")
            items = self.extract_folder_names_with_ocr(screenshot)
            if not items:
                logger.error("❌ OCR extraction failed - no items detected")
                return False
            logger.info(f"✅ OCR working - detected {len(items)} items")

            # Test 3: MIDI navigation commands
            logger.info("🎛️ Test 3: MIDI navigation commands...")
            if self.traktor:
                # Test tree navigation
                test_commands = [NavigationCommand.TREE_DOWN, NavigationCommand.TREE_UP]
                for cmd in test_commands:
                    if not self._send_navigation_command(cmd):
                        logger.error(f"❌ MIDI command failed: {cmd.value}")
                        return False
                logger.info("✅ MIDI navigation commands working")
            else:
                logger.warning("⚠️ No Traktor controller available for MIDI testing")

            logger.info("🎉 All browser connection tests passed!")
            return True

        except Exception as e:
            logger.error(f"❌ Browser connection test failed: {e}")
            return False

def main():
    """Main function for Jazz folder challenge"""

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('visual_browser_navigation.log'),
            logging.StreamHandler()
        ]
    )

    print("🎯 VISUAL BROWSER NAVIGATION - JAZZ FOLDER CHALLENGE")
    print("=" * 60)

    try:
        # Initialize components
        print("🎛️ Initializing Traktor controller...")
        config = DJConfig()  # Use default config
        traktor = TraktorController(config)
        if not traktor.connect():
            print("❌ Failed to connect to Traktor - check MIDI setup")
            return

        print("👁️ Initializing Visual Browser Navigator...")
        navigator = VisualBrowserNavigator(traktor)

        # Test system
        print("\n🧪 Testing system components...")
        if not navigator.test_browser_connection():
            print("❌ System test failed - check setup and try again")
            return

        # Configuration
        print(f"\n📐 Current browser area: {navigator.browser_area}")
        calibrate_input = input("🎯 Enter new browser area as 'x,y,w,h' or press Enter to use default: ").strip()

        if calibrate_input:
            try:
                x, y, w, h = map(int, calibrate_input.split(','))
                navigator.calibrate_browser_area((x, y, w, h))
            except ValueError:
                print("⚠️ Invalid format, using default area")

        # Jazz folder challenge
        target_folder = input("\n🎯 Enter target folder name [default: Jazz]: ").strip()
        if not target_folder:
            target_folder = "Jazz"

        max_attempts = input(f"🔄 Max search attempts [default: {navigator.max_exploration_attempts}]: ").strip()
        if max_attempts.isdigit():
            max_attempts = int(max_attempts)
        else:
            max_attempts = navigator.max_exploration_attempts

        print(f"\n🚀 STARTING JAZZ FOLDER CHALLENGE!")
        print(f"🎯 Target: '{target_folder}'")
        print(f"🔄 Max attempts: {max_attempts}")
        print(f"📸 Debug screenshots: {navigator.debug_folder}/")
        print("📝 The navigator will systematically explore the browser...")
        print()

        start_time = time.time()

        # Run the challenge
        success = navigator.navigate_to_target_folder(target_folder, max_attempts)

        elapsed_time = time.time() - start_time

        # Results
        print(f"\n{'🏆' if success else '❌'} JAZZ FOLDER CHALLENGE COMPLETE")
        print("=" * 60)

        if success:
            print(f"🏆 SUCCESS! Found '{target_folder}' in {elapsed_time:.1f} seconds")
        else:
            print(f"❌ Challenge failed after {elapsed_time:.1f} seconds")

        # Detailed statistics
        status = navigator.get_navigation_status()
        print(f"\n📊 CHALLENGE STATISTICS:")
        print(f"   ⏱️  Total time: {elapsed_time:.1f} seconds")
        print(f"   🧭  Navigation commands: {status['navigation_commands_sent']}")
        print(f"   📁  Folders visited: {status['folders_visited']}")
        print(f"   📂  Folders expanded: {status['folders_expanded']}")
        print(f"   🔍  Max depth reached: {status['max_depth_reached']}")
        print(f"   👁️  Final visible items: {status['visible_items_count']}")
        if status['selected_item']:
            print(f"   📍  Final selection: {status['selected_item']}")
        if status['recent_commands']:
            print(f"   🔄  Recent commands: {' → '.join(status['recent_commands'][-5:])}")

        print(f"\n📸 Debug screenshots saved to: {navigator.debug_folder}/")
        print(f"📋 Log file: visual_browser_navigation.log")

        if success:
            print("\n🎉 Computer vision + MIDI navigation working perfectly!")
            print("🤖 The system successfully demonstrated autonomous browser navigation!")
        else:
            print("\n💡 Tips for better results:")
            print("   • Ensure Traktor browser window is fully visible")
            print("   • Check browser area coordinates are correct")
            print("   • Verify folder names are readable in screenshots")
            print("   • Make sure MIDI connection is stable")

    except KeyboardInterrupt:
        print("\n⏹️ Challenge interrupted by user")

    except Exception as e:
        print(f"❌ Challenge failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()