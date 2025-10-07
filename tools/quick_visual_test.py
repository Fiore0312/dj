#!/usr/bin/env python3
"""
🔧 QUICK VISUAL BROWSER TEST - Debug Helper
===========================================

Quick test script for debugging the visual browser agent:
- Test screenshot capture
- Test OCR text extraction
- Test MIDI navigation commands
- View current browser state

Use this for rapid iteration and debugging before running full Jazz challenge.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.traktor_control import TraktorController
    from agents.enhanced_visual_browser_agent import EnhancedVisualBrowserAgent
    import cv2
    import numpy as np
    MODULES_OK = True
except ImportError as e:
    MODULES_OK = False
    print(f"❌ Import error: {e}")

def quick_screenshot_test(agent):
    """Test screenshot capture and display"""
    print("\n📸 SCREENSHOT TEST")
    print("-" * 30)

    screenshot = agent.take_browser_screenshot()

    if screenshot is not None:
        h, w = screenshot.shape[:2]
        print(f"✅ Screenshot captured: {w}x{h} pixels")

        # Save test screenshot
        cv2.imwrite("quick_test_screenshot.png", screenshot)
        print("💾 Saved as: quick_test_screenshot.png")

        return True
    else:
        print("❌ Screenshot failed")
        return False

def quick_ocr_test(agent):
    """Test OCR text extraction"""
    print("\n🔍 OCR TEST")
    print("-" * 20)

    success = agent._scan_current_browser_state()

    if success:
        items = agent.nav_state.visible_items
        print(f"✅ OCR detected {len(items)} items:")

        for item in items:
            icon = "📁" if item.is_folder else "📄"
            star = "⭐" if item.is_selected else "  "
            conf = f"({item.confidence:.2f})"
            print(f"   {star}{icon} {item.name} {conf}")

        return True
    else:
        print("❌ OCR failed")
        return False

def quick_navigation_test(agent):
    """Test basic navigation commands"""
    print("\n🧭 NAVIGATION TEST")
    print("-" * 25)

    commands = [
        ("DOWN", lambda: agent._send_navigation_command(agent.NavigationDirection.DOWN)),
        ("UP", lambda: agent._send_navigation_command(agent.NavigationDirection.UP)),
    ]

    results = []
    for name, cmd_func in commands:
        print(f"Testing {name}...", end=" ")
        success = cmd_func()
        results.append(success)
        print("✅" if success else "❌")
        time.sleep(0.5)

    return all(results)

def interactive_browser_viewer(agent):
    """Interactive browser viewer"""
    print("\n👁️ INTERACTIVE BROWSER VIEWER")
    print("=" * 40)
    print("Commands:")
    print("  's' - take screenshot and scan")
    print("  'd' - navigate DOWN")
    print("  'u' - navigate UP")
    print("  'e' - expand folder")
    print("  'c' - collapse folder")
    print("  'f <name>' - find folder by name")
    print("  'q' - quit viewer")
    print()

    while True:
        try:
            cmd = input("🎛️ Command: ").strip().lower()

            if cmd == 'q':
                break
            elif cmd == 's':
                if agent._scan_current_browser_state():
                    print("📊 Current browser state:")
                    for item in agent.nav_state.visible_items:
                        icon = "📁" if item.is_folder else "📄"
                        star = "⭐" if item.is_selected else "  "
                        print(f"   {star}{icon} {item.name}")
            elif cmd == 'd':
                if agent._send_navigation_command(agent.NavigationDirection.DOWN):
                    print("✅ Moved DOWN")
                else:
                    print("❌ DOWN failed")
            elif cmd == 'u':
                if agent._send_navigation_command(agent.NavigationDirection.UP):
                    print("✅ Moved UP")
                else:
                    print("❌ UP failed")
            elif cmd == 'e':
                if agent._send_navigation_command(agent.NavigationDirection.EXPAND):
                    print("✅ Expanded")
                else:
                    print("❌ Expand failed")
            elif cmd == 'c':
                if agent._send_navigation_command(agent.NavigationDirection.COLLAPSE):
                    print("✅ Collapsed")
                else:
                    print("❌ Collapse failed")
            elif cmd.startswith('f '):
                target = cmd[2:].strip()
                if target:
                    print(f"🎯 Searching for '{target}'...")
                    success = agent.navigate_to_target_folder(target)
                    if success:
                        print(f"✅ Found '{target}'!")
                    else:
                        print(f"❌ Could not find '{target}'")
            else:
                print("❓ Unknown command")

        except KeyboardInterrupt:
            print("\n👋 Interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main test execution"""
    print("🔧 QUICK VISUAL BROWSER TEST")
    print("=" * 35)

    if not MODULES_OK:
        print("❌ Required modules not available")
        return

    try:
        # Initialize
        print("🎛️ Connecting to Traktor...")
        traktor = TraktorController()
        traktor.connect()

        print("👁️ Initializing Visual Browser Agent...")
        agent = EnhancedVisualBrowserAgent(traktor)

        # Calibrate browser area
        area_input = input("📐 Browser area (x,y,w,h) or Enter for default: ").strip()
        if area_input:
            try:
                x, y, w, h = map(int, area_input.split(','))
                agent.calibrate_browser_area((x, y, w, h))
                print(f"✅ Browser area set to: {(x, y, w, h)}")
            except ValueError:
                print("⚠️ Invalid format, using default")

        # Run tests
        tests = [
            ("Screenshot Test", lambda: quick_screenshot_test(agent)),
            ("OCR Test", lambda: quick_ocr_test(agent)),
            ("Navigation Test", lambda: quick_navigation_test(agent)),
        ]

        results = []
        for name, test_func in tests:
            print(f"\n🧪 Running {name}...")
            success = test_func()
            results.append(success)

        print(f"\n📊 TEST SUMMARY")
        print("-" * 20)
        for i, (name, _) in enumerate(tests):
            status = "✅ PASS" if results[i] else "❌ FAIL"
            print(f"{name}: {status}")

        # Interactive mode
        if any(results):
            use_interactive = input("\n🎮 Enter interactive mode? (y/n): ").strip().lower()
            if use_interactive == 'y':
                interactive_browser_viewer(agent)

        print("\n✅ Quick test complete")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()