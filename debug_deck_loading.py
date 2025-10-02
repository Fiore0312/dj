#!/usr/bin/env python3
"""
Debug Deck Loading Issue
Diagnose perché le tracce lampeggiano ma non partono
"""

import asyncio
import logging
import time
from config import DJConfig
from traktor_control import TraktorController, DeckID
from traktor_collection_parser import TraktorCollectionParser
from smart_traktor_navigator import SmartTraktorNavigator

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_load_and_play():
    """Debug complete load and play sequence"""
    print("\n🔍 DEBUG: Deck Loading Issue")
    print("="*60)

    # Setup
    config = DJConfig()
    traktor = TraktorController(config)

    print("\n1. Connecting to Traktor...")
    if not traktor.connect_with_gil_safety():
        print("❌ Failed to connect")
        return

    print(f"✅ Connected (Simulation: {traktor.simulation_mode})")

    # Parse collection
    parser = TraktorCollectionParser()
    print("\n2. Parsing collection...")
    if not parser.parse_collection():
        print("❌ Failed to parse")
        return

    print(f"✅ Parsed {len(parser.tracks)} tracks")

    # Get a simple track (near beginning)
    all_tracks = parser.get_all_tracks()
    if not all_tracks:
        print("❌ No tracks found")
        return

    # Use a track with low position for faster test
    test_track = None
    for track in all_tracks:
        if track.browser_position and track.browser_position < 100 and track.bpm:
            test_track = track
            break

    if not test_track:
        test_track = all_tracks[0]

    print(f"\n3. Test Track:")
    print(f"   Artist: {test_track.artist}")
    print(f"   Title: {test_track.title}")
    print(f"   Position: {test_track.browser_position}")
    print(f"   BPM: {test_track.bpm}")
    print(f"   File: {test_track.filepath}")

    # Create navigator
    navigator = SmartTraktorNavigator(traktor, parser)

    # STEP BY STEP DEBUG
    print("\n4. Navigating to track...")

    # Manual navigation with detailed logging
    target_pos = test_track.browser_position

    print(f"   Current position: {navigator.current_position}")
    print(f"   Target position: {target_pos}")

    # Reset to top first
    print("\n   Resetting to top...")
    for i in range(50):  # Navigate up many times
        traktor.browse_track_up()
        await asyncio.sleep(0.01)

    navigator.current_position = 0
    print("   ✅ At top")

    # Navigate down to target
    print(f"\n   Navigating down {target_pos} steps...")
    for i in range(target_pos):
        traktor.browse_track_down()
        await asyncio.sleep(0.08)

        if (i + 1) % 10 == 0:
            print(f"   ... step {i+1}/{target_pos}")

    print(f"   ✅ Navigated to position {target_pos}")

    # Select item
    print("\n5. Selecting item...")
    await asyncio.sleep(0.2)

    if not traktor.select_browser_item():
        print("   ⚠️  No select_browser_item command available")
    else:
        print("   ✅ Item selected")

    await asyncio.sleep(0.2)

    # Load to Deck A
    print("\n6. Loading to Deck A...")
    deck_state_before = traktor.deck_states.get(DeckID.A, {}).copy()
    print(f"   Deck state before: {deck_state_before}")

    load_success = traktor.load_track_to_deck(DeckID.A)
    print(f"   Load command result: {load_success}")

    # Wait for load
    await asyncio.sleep(1.0)

    deck_state_after = traktor.deck_states.get(DeckID.A, {})
    print(f"   Deck state after: {deck_state_after}")

    if deck_state_after.get('loaded'):
        print("   ✅ Track appears loaded in internal state")
    else:
        print("   ⚠️  Track NOT marked as loaded")

    # Check if track file exists
    import os
    if os.path.exists(test_track.filepath):
        print(f"   ✅ File exists: {test_track.filepath}")
    else:
        print(f"   ❌ File NOT found: {test_track.filepath}")
        print("   → This could be the problem!")

    # Try to PLAY
    print("\n7. Attempting to PLAY Deck A...")

    # Check deck state
    print(f"   Deck A loaded: {deck_state_after.get('loaded', False)}")
    print(f"   Deck A playing: {deck_state_after.get('playing', False)}")

    # Send play command
    play_success = traktor.play_deck(DeckID.A)
    print(f"   Play command result: {play_success}")

    await asyncio.sleep(0.5)

    # Check state after play
    deck_state_final = traktor.deck_states.get(DeckID.A, {})
    print(f"   Deck state after play: {deck_state_final}")

    if deck_state_final.get('playing'):
        print("\n✅ SUCCESS: Deck A is playing!")
    else:
        print("\n❌ PROBLEM: Deck A is NOT playing")
        print("\nPossible causes:")
        print("1. Track file doesn't exist at filepath")
        print("2. MIDI play command not reaching Traktor")
        print("3. Traktor deck is in wrong mode (not in Internal mode)")
        print("4. Track is corrupted or unsupported format")

    # Additional diagnostics
    print("\n8. Diagnostics:")
    print(f"   MIDI connected: {traktor.connected}")
    print(f"   Simulation mode: {traktor.simulation_mode}")
    print(f"   Total commands sent: {traktor.stats.get('commands_sent', 0)}")

    # Disconnect
    traktor.disconnect()
    print("\n✅ Debug complete")

if __name__ == "__main__":
    asyncio.run(debug_load_and_play())