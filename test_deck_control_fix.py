#!/usr/bin/env python3
"""
🔧 URGENT DECK CONTROL TEST - Master Coordinator Request
Test corrected MIDI commands for track loading and volume control
"""

import sys
import time
import logging
from pathlib import Path

# Add core directory to path
sys.path.append(str(Path(__file__).parent / "core"))

from core.traktor_control import TraktorController, DeckID
from core.config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_corrected_commands():
    """Test the corrected MIDI commands that were failing"""

    print("🎛️ URGENT DECK CONTROL TEST - Master Coordinator Request")
    print("=" * 60)
    print("Testing corrected MIDI commands for:")
    print("✅ Track loading (corrected mapping)")
    print("✅ Volume fader control")
    print("✅ Browser navigation (corrected methods)")
    print()

    # Initialize controller
    config = get_config()
    controller = TraktorController(config)

    # Connect (with simulation fallback)
    print("🔌 Connecting to Traktor...")
    if not controller.connect_with_gil_safety(output_only=True, timeout=3.0):
        print("❌ Connection failed")
        return False

    if controller.simulation_mode:
        print("⚠️ Running in SIMULATION mode (MIDI not available)")
    else:
        print("✅ Connected to Traktor via MIDI")

    print()

    # Test 1: Volume fader control (this was working)
    print("🔊 TEST 1: Volume Fader Control")
    print("-" * 30)

    success_volume = True
    for deck in [DeckID.A, DeckID.B]:
        volume_level = 0.5  # 50%
        result = controller.set_deck_volume(deck, volume_level)
        print(f"   Deck {deck.value} volume → 50%: {'✅ SUCCESS' if result else '❌ FAILED'}")
        if not result:
            success_volume = False
        time.sleep(0.1)

    print(f"   Volume control overall: {'✅ SUCCESS' if success_volume else '❌ FAILED'}")
    print()

    # Test 2: Track loading (this was the main issue)
    print("🎵 TEST 2: Track Loading Commands")
    print("-" * 30)

    success_loading = True
    for deck in [DeckID.A, DeckID.B, DeckID.C, DeckID.D]:
        result = controller.load_track_to_deck(deck)
        print(f"   Load track to Deck {deck.value}: {'✅ SUCCESS' if result else '❌ FAILED'}")
        if not result:
            success_loading = False
        time.sleep(0.2)

    print(f"   Track loading overall: {'✅ SUCCESS' if success_loading else '❌ FAILED'}")
    print()

    # Test 3: Browser navigation (corrected methods)
    print("🧭 TEST 3: Browser Navigation")
    print("-" * 30)

    nav_tests = [
        ("Browser Down", controller.browse_track_down),
        ("Browser Up", controller.browse_track_up),
        ("Select Item", controller.select_browser_item),
        ("Browser Back", controller.browser_back),
    ]

    success_navigation = True
    for test_name, test_func in nav_tests:
        try:
            result = test_func()
            print(f"   {test_name}: {'✅ SUCCESS' if result else '❌ FAILED'}")
            if not result:
                success_navigation = False
        except Exception as e:
            print(f"   {test_name}: ❌ EXCEPTION - {e}")
            success_navigation = False
        time.sleep(0.1)

    print(f"   Browser navigation overall: {'✅ SUCCESS' if success_navigation else '❌ FAILED'}")
    print()

    # Test 4: Play control (this was working)
    print("▶️ TEST 4: Play Control (Force Play)")
    print("-" * 30)

    result_play = controller.force_play_deck(DeckID.A)
    print(f"   Force play Deck A: {'✅ SUCCESS' if result_play else '❌ FAILED'}")
    print()

    # Overall results
    print("📊 OVERALL TEST RESULTS")
    print("=" * 60)

    all_tests = [
        ("Volume Control", success_volume),
        ("Track Loading", success_loading),
        ("Browser Navigation", success_navigation),
        ("Play Control", result_play),
    ]

    total_success = sum(1 for _, success in all_tests if success)
    total_tests = len(all_tests)

    for test_name, success in all_tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name:20}: {status}")

    success_rate = total_success / total_tests * 100
    print(f"\n   Success Rate: {total_success}/{total_tests} ({success_rate:.0f}%)")

    # Specific feedback for Master Coordinator
    print("\n🎯 MASTER COORDINATOR FEEDBACK")
    print("=" * 60)

    if success_loading:
        print("✅ TRACK LOADING: FIXED - All decks now use correct browser_load_deck_* mappings")
    else:
        print("❌ TRACK LOADING: Still failing - Check MIDI mappings in Traktor")

    if success_volume:
        print("✅ VOLUME CONTROL: Working correctly - No changes needed")
    else:
        print("❌ VOLUME CONTROL: Failing - Check MIDI channel/CC mappings")

    if success_navigation:
        print("✅ BROWSER NAVIGATION: FIXED - Now uses correct CC mappings")
    else:
        print("❌ BROWSER NAVIGATION: Still failing - May need Traktor MIDI Learn")

    print()

    # MIDI mapping verification
    print("🔍 MIDI MAPPING VERIFICATION")
    print("=" * 60)
    print("The following MIDI commands are being sent:")
    print(f"   Track Load A: Channel 1, CC 43")
    print(f"   Track Load B: Channel 1, CC 44")
    print(f"   Track Load C: Channel 1, CC 45")
    print(f"   Track Load D: Channel 1, CC 46")
    print(f"   Volume A: Channel 1, CC 28")
    print(f"   Volume B: Channel 1, CC 60")
    print(f"   Browser Nav: Channel 1, CC 49 (up/down)")
    print(f"   Browser Select: Channel 1, CC 64 (expand/collapse)")
    print()

    if controller.simulation_mode:
        print("⚠️ Note: All commands were simulated. Connect MIDI to test real commands.")
    else:
        print("✅ Commands were sent via real MIDI to Traktor.")

    # Disconnect
    controller.disconnect()

    return success_loading and success_volume

if __name__ == "__main__":
    test_corrected_commands()