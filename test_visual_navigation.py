#!/usr/bin/env python3
"""
🧪 TEST VISUAL NAVIGATION - Quick Jazz Folder Challenge Test
==========================================================

Simple test runner for the visual browser navigation system.
This script provides a quick way to test the Jazz folder finding capabilities
without going through the full interactive setup.

Usage:
    python3 test_visual_navigation.py
    python3 test_visual_navigation.py --target "Ambient"
    python3 test_visual_navigation.py --area "100,200,500,600"
"""

import sys
import argparse
import logging
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from visual_browser_navigation import VisualBrowserNavigator
    from core.traktor_control import TraktorController
    from core.config import DJConfig
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"❌ Required modules not available: {e}")

def setup_test_logging():
    """Setup logging for test output"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_visual_navigation.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Test Visual Browser Navigation - Jazz Folder Challenge'
    )

    parser.add_argument(
        '--target',
        default='Jazz',
        help='Target folder name to find (default: Jazz)'
    )

    parser.add_argument(
        '--area',
        help='Browser area as "x,y,width,height" (e.g., "50,100,400,600")'
    )

    parser.add_argument(
        '--max-attempts',
        type=int,
        default=50,
        help='Maximum search attempts (default: 50)'
    )

    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable debug screenshots'
    )

    parser.add_argument(
        '--simulation',
        action='store_true',
        help='Run in simulation mode (no actual MIDI commands)'
    )

    return parser.parse_args()

def test_visual_navigation(args):
    """Main test function"""
    logger = setup_test_logging()

    print("🧪 VISUAL BROWSER NAVIGATION TEST")
    print("=" * 50)
    print(f"🎯 Target folder: '{args.target}'")
    print(f"🔄 Max attempts: {args.max_attempts}")
    print(f"📸 Debug mode: {'disabled' if args.no_debug else 'enabled'}")
    print(f"🎛️ MIDI mode: {'simulation' if args.simulation else 'real'}")
    print()

    try:
        # Initialize Traktor controller
        if not args.simulation:
            print("🎛️ Initializing Traktor controller...")
            config = DJConfig()
            traktor = TraktorController(config)

            if not traktor.connect():
                print("⚠️ Failed to connect to Traktor - running in simulation mode")
                traktor = None
        else:
            print("🎮 Running in simulation mode")
            traktor = None

        # Initialize visual navigator
        print("👁️ Initializing Visual Browser Navigator...")
        navigator = VisualBrowserNavigator(traktor)

        # Configure debug mode
        if args.no_debug:
            navigator.save_debug_screenshots = False
            navigator.debug_mode = False

        # Configure browser area if specified
        if args.area:
            try:
                x, y, w, h = map(int, args.area.split(','))
                navigator.calibrate_browser_area((x, y, w, h))
                print(f"📐 Browser area set to: ({x}, {y}, {w}, {h})")
            except ValueError:
                print("⚠️ Invalid area format, using default")

        print(f"📍 Current browser area: {navigator.browser_area}")

        # Test system components
        print("\n🔧 Testing system components...")

        # Test screenshot capture
        print("📸 Testing screenshot capture...")
        screenshot = navigator.take_browser_screenshot()
        if screenshot is not None:
            print(f"✅ Screenshot working - captured {screenshot.shape[1]}x{screenshot.shape[0]} image")
        else:
            print("❌ Screenshot capture failed")
            return False

        # Test OCR
        print("🔤 Testing OCR extraction...")
        items = navigator.extract_folder_names_with_ocr(screenshot)
        print(f"✅ OCR working - detected {len(items)} items")

        if items:
            print("📋 Detected items:")
            for i, item in enumerate(items[:5]):  # Show first 5 items
                icon = "📁" if item.is_folder else "📄"
                selected = "⭐" if item.is_selected else "  "
                print(f"   {selected} {icon} {item.name} (conf: {item.confidence:.2f})")
            if len(items) > 5:
                print(f"   ... and {len(items) - 5} more items")

        # Run the Jazz folder challenge
        print(f"\n🚀 STARTING SEARCH FOR '{args.target}'")
        print("-" * 40)

        import time
        start_time = time.time()

        success = navigator.navigate_to_target_folder(args.target, args.max_attempts)

        elapsed_time = time.time() - start_time

        # Results
        print(f"\n{'🏆' if success else '❌'} TEST RESULTS")
        print("=" * 50)

        if success:
            print(f"🏆 SUCCESS! Found '{args.target}' in {elapsed_time:.1f} seconds")
        else:
            print(f"❌ FAILED to find '{args.target}' after {elapsed_time:.1f} seconds")

        # Show detailed statistics
        status = navigator.get_navigation_status()
        print(f"\n📊 DETAILED STATISTICS:")
        print(f"   ⏱️  Total time: {elapsed_time:.1f} seconds")
        print(f"   🧭  Navigation commands: {status['navigation_commands_sent']}")
        print(f"   📁  Folders visited: {status['folders_visited']}")
        print(f"   📂  Folders expanded: {status['folders_expanded']}")
        print(f"   🔍  Max depth reached: {status['max_depth_reached']}")
        print(f"   👁️  Final visible items: {status['visible_items_count']}")
        if status['selected_item']:
            print(f"   📍  Final selection: {status['selected_item']}")
        if status['recent_commands']:
            print(f"   🔄  Recent commands: {' → '.join(status['recent_commands'])}")

        if not args.no_debug:
            print(f"\n📸 Debug screenshots saved to: {navigator.debug_folder}/")
        print(f"📋 Test log saved to: test_visual_navigation.log")

        return success

    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    if not MODULES_AVAILABLE:
        print("❌ Required modules not available")
        print("   Make sure you have installed:")
        print("   - pip install opencv-python pillow pytesseract")
        print("   - Traktor control modules are available")
        return

    args = parse_arguments()

    print("🎯 Visual Browser Navigation Test Runner")
    print("   Target:", args.target)
    if args.area:
        print("   Browser area:", args.area)
    print("   Max attempts:", args.max_attempts)
    print()

    success = test_visual_navigation(args)

    if success:
        print("\n🎉 TEST PASSED - Visual navigation working correctly!")
    else:
        print("\n💔 TEST FAILED - Check logs and debug screenshots")
        print("💡 Tips:")
        print("   • Make sure Traktor browser window is visible")
        print("   • Check browser area coordinates are correct")
        print("   • Verify target folder exists and is readable")
        print("   • Ensure MIDI connection is working")

if __name__ == "__main__":
    main()