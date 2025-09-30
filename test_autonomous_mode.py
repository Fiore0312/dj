#!/usr/bin/env python3
"""
🧪 Test Autonomous Mode Complete
Verifica che modalità autonoma funzioni end-to-end
"""

import subprocess
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def test_autonomous_mode():
    """Test complete autonomous mode"""
    print("\n" + "="*80)
    print("🧪 TEST AUTONOMOUS MODE")
    print("="*80)

    tests = []

    # Test 1: Autonomous mode avvio
    print("\n1️⃣ Testing autonomous mode startup...")
    try:
        proc = subprocess.Popen(
            ['python3', 'dj_ai_launcher.py', '--autonomous', '--duration', '1'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for startup and first transition
        time.sleep(30)

        # Send interrupt
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

        # Check output
        success = (
            "AUTONOMOUS DJ MODE" in stdout and
            "✅ Connected to Traktor MIDI" in stdout and
            "Loading first track" in stdout
        )

        if success:
            print("   ✅ Autonomous mode startup: SUCCESS")
            tests.append(("Autonomous startup", True))
        else:
            print("   ❌ Autonomous mode startup: FAILED")
            print(f"   Output: {stdout[:500]}")
            tests.append(("Autonomous startup", False))

    except Exception as e:
        print(f"   ❌ Autonomous mode startup error: {e}")
        tests.append(("Autonomous startup", False))

    # Test 2: Force play integration
    print("\n2️⃣ Testing force play in autonomous...")
    try:
        # Check that force_play is used
        with open('dj_ai_launcher.py', 'r') as f:
            content = f.read()
            uses_force_play = 'force_play_deck' in content

        if uses_force_play:
            print("   ✅ Uses force_play_deck: SUCCESS")
            tests.append(("Force play integration", True))
        else:
            print("   ❌ Does not use force_play_deck")
            tests.append(("Force play integration", False))

    except Exception as e:
        print(f"   ❌ Force play check error: {e}")
        tests.append(("Force play integration", False))

    # Test 3: Blinking fix integrated
    print("\n3️⃣ Testing blinking fix integrated...")
    try:
        with open('dj_ai_launcher.py', 'r') as f:
            content = f.read()
            has_intelligent_delay = 'wait_if_recent_load' in content
            has_smart_load = 'load_next_track_smart' in content

        if has_intelligent_delay and has_smart_load:
            print("   ✅ Blinking fix integrated: SUCCESS")
            tests.append(("Blinking fix", True))
        else:
            print("   ❌ Blinking fix missing components")
            tests.append(("Blinking fix", False))

    except Exception as e:
        print(f"   ❌ Blinking fix check error: {e}")
        tests.append(("Blinking fix", False))

    # Test 4: CLI autonomous command
    print("\n4️⃣ Testing CLI autonomous command availability...")
    try:
        with open('dj_ai_launcher.py', 'r') as f:
            content = f.read()
            has_cli_command = 'elif command == "autonomous"' in content

        if has_cli_command:
            print("   ✅ CLI autonomous command: SUCCESS")
            tests.append(("CLI command", True))
        else:
            print("   ❌ CLI autonomous command missing")
            tests.append(("CLI command", False))

    except Exception as e:
        print(f"   ❌ CLI command check error: {e}")
        tests.append(("CLI command", False))

    # Test 5: Documentation exists
    print("\n5️⃣ Testing documentation...")
    try:
        import os
        has_docs = os.path.exists('AUTONOMOUS_QUICK_START.md')

        if has_docs:
            print("   ✅ Documentation exists: SUCCESS")
            tests.append(("Documentation", True))
        else:
            print("   ❌ Documentation missing")
            tests.append(("Documentation", False))

    except Exception as e:
        print(f"   ❌ Documentation check error: {e}")
        tests.append(("Documentation", False))

    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, success in tests if success)
    total = len(tests)

    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print()
    print(f"Total: {passed}/{total} tests passed")
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"Success rate: {success_rate:.0f}%")

    print("="*80)

    if passed == total:
        print("✅ ALL TESTS PASSED - AUTONOMOUS MODE READY!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Review issues above")
        return False

if __name__ == "__main__":
    try:
        success = test_autonomous_mode()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
