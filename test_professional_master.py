#!/usr/bin/env python3
"""
🎛️ Test Professional MASTER Workflow
Demonstrates the correct 3-step MASTER activation sequence and professional mixing
"""

import asyncio
import logging
from core.traktor_control import TraktorController, DeckID
from core.config import get_config

async def test_professional_master_workflow():
    """Test the professional MASTER activation and mixing workflow"""
    print("🎯 Professional MASTER Workflow Test")
    print("=" * 50)

    # Setup
    config = get_config()
    controller = TraktorController(config)

    # Connect
    print("🔌 Connecting to Traktor...")
    if not controller.connect_with_gil_safety(output_only=True, timeout=10.0):
        print("❌ Connection failed")
        return

    print("✅ Connected to Traktor")

    # Test 1: Professional MASTER activation on Deck A
    print("\n🎯 Test 1: Professional MASTER Activation (Deck A)")
    print("SEQUENCE: PLAY → VOLUME ADJUST → MASTER")

    success = controller.activate_deck_master(DeckID.A)
    print(f"Result: {'✅ SUCCESS' if success else '❌ FAILED'}")

    await asyncio.sleep(2.0)

    # Test 2: Load track to Deck B and activate MASTER
    print("\n🎯 Test 2: Load track and activate MASTER (Deck B)")

    # Load track to Deck B
    load_success = controller.load_next_track_smart(DeckID.B)
    print(f"Load Result: {'✅ SUCCESS' if load_success else '❌ FAILED'}")

    await asyncio.sleep(1.0)

    # Activate MASTER on Deck B
    success_b = controller.activate_deck_master(DeckID.B)
    print(f"MASTER Result: {'✅ SUCCESS' if success_b else '❌ FAILED'}")

    await asyncio.sleep(2.0)

    # Test 3: Professional A→B mix with MASTER handoff
    print("\n🎯 Test 3: Professional A→B Mix with MASTER Handoff")

    mix_success = controller.mix_to_deck_b()
    print(f"Mix Result: {'✅ SUCCESS' if mix_success else '❌ FAILED'}")

    # Show final status
    print("\n📊 Final Status:")
    print(f"Current MASTER deck: {controller.get_current_master_deck()}")
    print(f"Deck A playing: {controller.is_deck_playing(DeckID.A)}")
    print(f"Deck B playing: {controller.is_deck_playing(DeckID.B)}")

    # Cleanup
    controller.disconnect()
    print("\n✅ Professional MASTER workflow test completed")

if __name__ == "__main__":
    asyncio.run(test_professional_master_workflow())