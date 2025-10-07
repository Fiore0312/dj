#!/usr/bin/env python3
"""
🎯 Test Complete 6-Step Professional MASTER Sequence

This script tests the complete professional DJ workflow:
1. BROWSER TREE NAVIGATION → Select Up/Down (browser.tree)
2. BROWSER LIST NAVIGATION → Select Up/Down (browser.list)
3. LOAD TRACK → Load selected track to deck
4. PLAY → Start track playback
5. VOLUME ADJUST → Set gain to maximum
6. MASTER → Activate MASTER button

This is the standard professional DJ workflow from track selection to MASTER activation.
"""

import sys
import os
import time
import asyncio

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_config
from core.traktor_control import TraktorController, DeckID

def main():
    """Test complete 6-step MASTER sequence"""

    print("🎯 Testing Complete 6-Step Professional MASTER Sequence")
    print("=" * 60)
    print("Professional DJ Workflow:")
    print("1. BROWSER TREE NAVIGATION → Select Up/Down (browser.tree)")
    print("2. BROWSER LIST NAVIGATION → Select Up/Down (browser.list)")
    print("3. LOAD TRACK → Load selected track to deck")
    print("4. PLAY → Start track playback")
    print("5. VOLUME ADJUST → Set gain to maximum")
    print("6. MASTER → Activate MASTER button")
    print("=" * 60)

    # Initialize controller
    config = get_config()
    controller = TraktorController(config)

    # Connect to Traktor
    print("\n🔌 Connecting to Traktor...")
    if not controller.connect_with_gil_safety(output_only=False):
        print("❌ Failed to connect to Traktor")
        return False

    print("✅ Connected to Traktor")

    try:
        # Show current browser mappings
        print("\n📋 Current Browser Navigation Mappings:")
        mappings = controller.get_browser_navigation_mappings()

        print(f"   Browser Tree Navigation: CC {mappings['browser_tree_navigation']['cc_number']}")
        print(f"   Browser List Navigation: CC {mappings['browser_list_navigation']['cc_number']}")
        print(f"   Load to Deck A: CC {mappings['browser_load_commands']['deck_a']['cc_number']}")
        print(f"   Load to Deck B: CC {mappings['browser_load_commands']['deck_b']['cc_number']}")

        # Test individual browser navigation functions
        print("\n🗂️ Testing Individual Browser Functions:")

        print("   Testing browser tree navigation...")
        tree_up = controller.browser_tree_up()
        time.sleep(0.2)
        tree_down = controller.browser_tree_down()
        print(f"   ├── Tree UP: {'✅' if tree_up else '❌'}")
        print(f"   └── Tree DOWN: {'✅' if tree_down else '❌'}")

        time.sleep(0.5)

        print("   Testing browser list navigation...")
        list_up = controller.browser_select_up()
        time.sleep(0.2)
        list_down = controller.browser_select_down()
        print(f"   ├── List UP: {'✅' if list_up else '❌'}")
        print(f"   └── List DOWN: {'✅' if list_down else '❌'}")

        time.sleep(1.0)

        # Test complete track selection and loading
        print("\n💾 Testing Track Selection and Loading:")
        selection_result = controller.select_track_and_load(DeckID.A, navigation_steps=2, direction="down")
        print(f"   Track Selection & Load to Deck A: {'✅' if selection_result else '❌'}")

        time.sleep(2.0)

        # Test complete 6-step MASTER sequence
        print("\n👑 Testing Complete 6-Step MASTER Sequence on Deck A:")
        print("   This will execute all 6 steps in sequence...")

        master_result = controller.activate_deck_master(DeckID.A)

        if master_result:
            print("🎉 COMPLETE 6-STEP MASTER SEQUENCE SUCCESSFUL!")
            print("✅ All steps executed: BROWSE → SELECT → LOAD → PLAY → GAIN → MASTER")
        else:
            print("❌ 6-step MASTER sequence failed")

        time.sleep(2.0)

        # Test on additional deck for validation
        print("\n🔄 Testing on Deck B for validation...")
        deck_b_result = controller.activate_deck_master(DeckID.B)
        print(f"   Deck B 6-step sequence: {'✅' if deck_b_result else '❌'}")

        # Show final status
        print("\n📊 Final Status:")
        deck_a_state = controller.get_deck_state(DeckID.A)
        deck_b_state = controller.get_deck_state(DeckID.B)

        print(f"   Deck A - Loaded: {deck_a_state['loaded']}, Playing: {deck_a_state['playing']}")
        print(f"   Deck B - Loaded: {deck_b_state['loaded']}, Playing: {deck_b_state['playing']}")
        print(f"   Current Master Deck: {controller.get_current_master_deck()}")

        # Show comprehensive test results
        print("\n🧪 Running Comprehensive Test Suite...")
        comprehensive_test = controller.test_6step_master_sequence_all_decks()

        print(f"\n📈 Comprehensive Test Results:")
        print(f"   Successful Decks: {comprehensive_test['successful_decks']}/4")
        print(f"   Success Rate: {comprehensive_test['success_rate']:.1%}")
        print(f"   Professional Workflow Validated: {'🏆 YES' if comprehensive_test['professional_workflow_validated'] else '⚠️ NO'}")

        # Show individual deck results
        for deck_name, result in comprehensive_test['deck_results'].items():
            status_icon = '✅' if result['success'] else '❌'
            exec_time = result['execution_time']
            print(f"   ├── Deck {deck_name}: {status_icon} ({exec_time}s)")
            if result.get('error'):
                print(f"   │   Error: {result['error']}")

        return comprehensive_test['professional_workflow_validated']

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

    finally:
        # Cleanup
        controller.disconnect()
        print("\n👋 Test completed, disconnected from Traktor")

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🏆 PROFESSIONAL WORKFLOW FULLY VALIDATED!")
        print("🎯 All 6 steps of the professional DJ sequence are working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️ PROFESSIONAL WORKFLOW ISSUES DETECTED")
        print("🔧 Some steps in the 6-step sequence may need attention.")
        sys.exit(1)