#!/usr/bin/env python3
"""
🎵 JAZZ FOLDER CHALLENGE - Autonomous Navigation Test
====================================================

This script demonstrates the Enhanced Visual Browser Agent solving the
"Jazz folder navigation challenge" by:

1. Taking screenshots of Traktor's browser interface
2. Using OCR to read folder names
3. Systematically navigating to find the "Jazz" folder
4. Providing visual debugging and real-time feedback

CHALLENGE SCENARIO:
- User is somewhere in Traktor's browser tree
- Target: Find and navigate to "Jazz" folder
- Method: Computer vision + intelligent navigation

REQUIREMENTS:
- Traktor Pro 3 running with browser visible
- PIL, OpenCV, and pytesseract installed
- IAC Driver configured for MIDI communication

Author: Enhanced Library Management Agent
Date: 2025-10-06
"""

import sys
import os
import time
import logging
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.traktor_control import TraktorController
    from agents.enhanced_visual_browser_agent import EnhancedVisualBrowserAgent
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"❌ Required modules not available: {e}")

def setup_logging():
    """Setup logging for detailed challenge tracking"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('jazz_challenge.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def print_challenge_header():
    """Print challenge introduction"""
    print("🎵" * 50)
    print("🎵 JAZZ FOLDER NAVIGATION CHALLENGE")
    print("🎵 Enhanced Visual Browser Agent Test")
    print("🎵" * 50)
    print()
    print("OBJECTIVE: Autonomously find and navigate to 'Jazz' folder")
    print("METHOD: Computer Vision + OCR + Intelligent Navigation")
    print("TECHNOLOGY: PIL + OpenCV + pytesseract + MIDI CC commands")
    print()

def verify_prerequisites():
    """Verify all prerequisites are met"""
    print("🔍 VERIFYING PREREQUISITES:")
    print("=" * 40)

    # Check module availability
    if not MODULES_AVAILABLE:
        print("❌ Required modules not available")
        return False

    # Check computer vision libraries
    try:
        import cv2
        import numpy as np
        from PIL import Image, ImageGrab
        import pytesseract
        print("✅ Computer vision libraries: OK")
    except ImportError as e:
        print(f"❌ Computer vision libraries: {e}")
        return False

    # Check if tesseract is available
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR: v{version}")
    except Exception as e:
        print(f"⚠️ Tesseract OCR: {e} (may still work)")

    print("✅ Prerequisites check passed")
    return True

def get_user_configuration():
    """Get user configuration for the challenge"""
    print("\n🎯 CHALLENGE CONFIGURATION:")
    print("=" * 30)

    # Browser area configuration
    print("📐 Browser area configuration:")
    print("   Current default: (50, 100, 400, 600) = (x, y, width, height)")
    print("   This should cover Traktor's browser tree area")

    custom_area = input("   Enter custom area as 'x,y,w,h' or press Enter for default: ").strip()
    browser_area = None

    if custom_area:
        try:
            x, y, w, h = map(int, custom_area.split(','))
            browser_area = (x, y, w, h)
            print(f"   ✅ Using custom area: {browser_area}")
        except ValueError:
            print("   ⚠️ Invalid format, using default")

    # Target folder configuration
    target_folder = input("\n🎯 Enter target folder name [default: Jazz]: ").strip()
    if not target_folder:
        target_folder = "Jazz"

    # Challenge parameters
    print(f"\n📋 CHALLENGE PARAMETERS:")
    print(f"   🎯 Target folder: '{target_folder}'")
    print(f"   📐 Browser area: {browser_area or 'default (50, 100, 400, 600)'}")
    print(f"   🔍 Max exploration attempts: 50")
    print(f"   ⏱️ Navigation delay: 0.5s")
    print(f"   📸 Debug screenshots: enabled")

    return target_folder, browser_area

def run_jazz_folder_challenge(target_folder: str, browser_area: Optional[tuple] = None):
    """Run the main jazz folder challenge"""
    logger = logging.getLogger(__name__)

    try:
        print(f"\n🚀 STARTING CHALLENGE: Find '{target_folder}' folder")
        print("=" * 50)

        # Initialize Traktor controller
        print("🎛️ Step 1: Connecting to Traktor...")
        traktor = TraktorController()
        connected = traktor.connect()

        if not connected:
            print("❌ Failed to connect to Traktor")
            return False

        print("✅ Traktor connection established")

        # Initialize Enhanced Visual Browser Agent
        print("👁️ Step 2: Initializing Visual Browser Agent...")
        agent = EnhancedVisualBrowserAgent(traktor)

        # Configure browser area if specified
        if browser_area:
            agent.calibrate_browser_area(browser_area)

        print("✅ Visual Browser Agent ready")

        # Test initial screenshot and OCR
        print("📸 Step 3: Testing screenshot and OCR...")
        if not agent._scan_current_browser_state():
            print("❌ Screenshot/OCR test failed - check browser visibility")
            return False

        initial_status = agent.get_navigation_status()
        print(f"✅ OCR working - detected {initial_status['visible_items_count']} items")

        if initial_status['selected_item']:
            print(f"📍 Currently selected: {initial_status['selected_item']}")

        # Start the main challenge
        print(f"\n🎯 Step 4: BEGINNING NAVIGATION TO '{target_folder}'")
        print("📝 The agent will now systematically explore the browser...")
        print("   - Taking screenshots of browser area")
        print("   - Using OCR to read folder names")
        print("   - Navigating with CC72 (down) / CC73 (up) / CC64 (expand)")
        print("   - Tracking exploration state")
        print()

        start_time = time.time()

        # The main challenge execution
        success = agent.navigate_to_target_folder(target_folder)

        elapsed_time = time.time() - start_time

        # Results analysis
        print(f"\n{'🏆' if success else '❌'} CHALLENGE RESULTS")
        print("=" * 50)

        final_status = agent.get_navigation_status()

        if success:
            print(f"🏆 SUCCESS! Found '{target_folder}' in {elapsed_time:.1f} seconds")
            print(f"✅ Target located and navigation completed")
        else:
            print(f"❌ CHALLENGE FAILED after {elapsed_time:.1f} seconds")
            print(f"💡 Target '{target_folder}' not found in visible areas")

        # Detailed statistics
        print(f"\n📊 DETAILED STATISTICS:")
        print(f"   ⏱️  Total time: {elapsed_time:.1f} seconds")
        print(f"   🧭  Navigation commands: {final_status['navigation_commands_sent']}")
        print(f"   📁  Folders explored: {final_status['visited_folders_count']}")
        print(f"   🔍  Max depth reached: {final_status['exploration_depth']}")
        print(f"   👁️  Items detected in final view: {final_status['visible_items_count']}")

        if final_status['selected_item']:
            print(f"   📍  Final selection: {final_status['selected_item']}")

        print(f"   📸  Debug screenshots saved to: debug_screenshots/")

        return success

    except KeyboardInterrupt:
        print("\n⏹️ Challenge interrupted by user")
        return False

    except Exception as e:
        logger.error(f"Challenge error: {e}")
        print(f"❌ Challenge failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main challenge execution"""
    # Setup
    logger = setup_logging()
    print_challenge_header()

    # Verify prerequisites
    if not verify_prerequisites():
        print("\n❌ Prerequisites not met. Please install required dependencies.")
        return

    # Get configuration
    target_folder, browser_area = get_user_configuration()

    # Confirmation
    print(f"\n🔥 READY TO START CHALLENGE!")
    print("   Make sure:")
    print("   ✓ Traktor Pro 3 is running")
    print("   ✓ Browser window is visible")
    print("   ✓ You can see folder names in the browser tree")
    print("   ✓ IAC Driver is configured for MIDI")

    start_challenge = input("\n🚀 Press Enter to start challenge or 'q' to quit: ").strip()

    if start_challenge.lower() == 'q':
        print("👋 Challenge cancelled")
        return

    # Run the challenge
    success = run_jazz_folder_challenge(target_folder, browser_area)

    # Final message
    print(f"\n{'🎉' if success else '💔'} JAZZ FOLDER CHALLENGE COMPLETE")
    if success:
        print("🎵 The agent successfully demonstrated autonomous browser navigation!")
        print("🤖 Computer vision + OCR + MIDI navigation working perfectly!")
    else:
        print("📝 Challenge incomplete - check logs and debug screenshots for details")
        print("💡 Tips: Verify browser visibility, folder names, and MIDI connection")

    print(f"\n📋 Challenge log saved to: jazz_challenge.log")

if __name__ == "__main__":
    main()