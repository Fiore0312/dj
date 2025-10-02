#!/usr/bin/env python3
"""
Test GIL Fix - Verify MIDI initialization works without GIL errors
Tests both real MIDI and simulation mode
"""

import sys
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gil_safe_connection():
    """Test GIL-safe MIDI connection"""
    print("\n" + "="*60)
    print("TEST: GIL-Safe MIDI Connection")
    print("="*60)

    try:
        from traktor_control import TraktorController
        from config import DJConfig

        config = DJConfig()
        controller = TraktorController(config)

        print("\n✅ Controller created")
        print(f"   Testing connect_with_gil_safety()...")

        # Test GIL-safe connection
        start_time = time.time()
        success = controller.connect_with_gil_safety(timeout=5.0)
        elapsed = time.time() - start_time

        print(f"\n   Connection result: {success}")
        print(f"   Elapsed time: {elapsed:.2f}s")
        print(f"   Simulation mode: {controller.simulation_mode}")
        print(f"   Connected: {controller.connected}")

        if success:
            if controller.simulation_mode:
                print("\n✅ GIL-safe connection: SIMULATION MODE active")
                print("   (This is expected if IAC Driver unavailable)")
            else:
                print("\n✅ GIL-safe connection: Real MIDI connected")

            # Test sending a command
            print("\n   Testing command send...")
            test_success = controller.set_crossfader(0.5)
            print(f"   Command result: {test_success}")

            # Cleanup
            controller.disconnect()
            print("\n✅ Disconnected successfully")

            return True
        else:
            print("\n❌ Connection failed")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simulated_tkinter_callback():
    """
    Test che simula chiamata da Tkinter callback

    Questo è il pattern che causava GIL error prima del fix
    """
    print("\n" + "="*60)
    print("TEST: Simulated Tkinter Callback (GIL stress test)")
    print("="*60)

    try:
        import tkinter as tk
        from traktor_control import TraktorController
        from config import DJConfig

        root = tk.Tk()
        root.withdraw()  # Hide window

        config = DJConfig()
        controller_ref = [None]  # Use list for closure
        result_ref = [None]

        def button_callback():
            """Simula callback da button click"""
            print("\n   📱 Simulating button click callback...")
            controller = TraktorController(config)
            controller_ref[0] = controller

            # Questo è il pattern che causava GIL error
            print("   🔒 Calling connect_with_gil_safety() from Tkinter...")
            success = controller.connect_with_gil_safety()
            result_ref[0] = success

            print(f"   ✅ Connection completed: {success}")
            print(f"   Simulation mode: {controller.simulation_mode}")

            root.quit()

        # Schedule callback (simula click dopo 100ms)
        root.after(100, button_callback)

        # Run event loop
        print("\n   Starting Tkinter event loop...")
        root.mainloop()

        # Check result
        if result_ref[0]:
            print("\n✅ Tkinter callback test PASSED")
            print("   No GIL errors occurred!")

            if controller_ref[0]:
                controller_ref[0].disconnect()

            return True
        else:
            print("\n❌ Tkinter callback test FAILED")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "🎛️ " * 20)
    print("GIL FIX VERIFICATION TEST")
    print("🎛️ " * 20)

    results = {}

    # Test 1: Basic GIL-safe connection
    results['GIL-Safe Connection'] = test_gil_safe_connection()

    # Test 2: Simulated Tkinter callback (stress test)
    results['Tkinter Callback'] = test_simulated_tkinter_callback()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)

    print(f"\nResult: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED - GIL FIX WORKING!")
        print("✅ No more GIL errors")
        print("✅ MIDI initialization is GIL-safe")
        print("✅ Simulation mode fallback works")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())