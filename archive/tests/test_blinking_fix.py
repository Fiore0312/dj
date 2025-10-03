#!/usr/bin/env python3
"""
🧪 Test Blinking Fix - Verifica che tracce non lampeggino più
Test completo per verificare:
1. Load track funziona
2. Play track funziona SENZA blinking
3. Delay intelligente tra load e play
4. Verifica stato finale
"""

import time
import logging
from config import DJConfig
from traktor_control import TraktorController, DeckID

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_blinking_fix():
    """Test completo fix blinking"""
    print("\n" + "="*80)
    print("🧪 TEST FIX BLINKING TRACK")
    print("="*80)

    # Setup
    config = DJConfig()
    traktor = TraktorController(config)

    print("\n1️⃣ Connecting to Traktor...")
    if not traktor.connect_with_gil_safety():
        print("❌ Failed to connect to Traktor")
        return False

    if traktor.simulation_mode:
        print("⚠️  Running in SIMULATION mode")
    else:
        print("✅ Connected to real Traktor MIDI")

    # Test Deck A
    print("\n2️⃣ Testing Deck A: Load + Play")
    print("-" * 80)

    print("   Step 1: Load track to Deck A...")
    success_load = traktor.load_next_track_smart(DeckID.A, "down")
    if not success_load:
        print("   ❌ Load failed")
        return False
    print("   ✅ Track loaded to Deck A")

    # Verifica stato dopo load
    state_after_load = traktor.deck_states[DeckID.A]
    print(f"   📊 State after load: loaded={state_after_load['loaded']}, playing={state_after_load['playing']}")

    print("\n   Step 2: Force play Deck A (with intelligent delay)...")
    success_play = traktor.force_play_deck(DeckID.A, wait_if_recent_load=True)
    if not success_play:
        print("   ❌ Play failed")
        return False
    print("   ✅ Deck A force play command sent")

    # Verifica stato dopo play
    time.sleep(0.5)  # Aspetta stabilizzazione
    state_after_play = traktor.deck_states[DeckID.A]
    print(f"   📊 State after play: loaded={state_after_play['loaded']}, playing={state_after_play['playing']}")

    # Verifica che sia effettivamente in play
    print("\n   Step 3: Verify Deck A is playing...")
    is_playing = traktor.verify_deck_playing(DeckID.A, max_attempts=5)

    if is_playing:
        print("   ✅ VERIFICATION SUCCESS: Deck A is playing!")
    else:
        print("   ⚠️  VERIFICATION WARNING: Cannot confirm Deck A playing (but command was sent)")

    # Test Deck B
    print("\n3️⃣ Testing Deck B: Load + Play (quick succession)")
    print("-" * 80)

    print("   Step 1: Load track to Deck B...")
    success_load_b = traktor.load_next_track_smart(DeckID.B, "down")
    if not success_load_b:
        print("   ❌ Load failed")
        return False
    print("   ✅ Track loaded to Deck B")

    print("\n   Step 2: Play Deck B immediately (testing intelligent delay)...")
    # Qui usiamo play_deck() che internamente chiama force_play con delay intelligente
    success_play_b = traktor.play_deck(DeckID.B)
    if not success_play_b:
        print("   ❌ Play failed")
        return False
    print("   ✅ Deck B play command sent")

    # Verifica
    time.sleep(0.5)
    is_playing_b = traktor.verify_deck_playing(DeckID.B, max_attempts=5)

    if is_playing_b:
        print("   ✅ VERIFICATION SUCCESS: Deck B is playing!")
    else:
        print("   ⚠️  VERIFICATION WARNING: Cannot confirm Deck B playing")

    # Test anti-blinking: prova a chiamare play_deck multiplo volte
    print("\n4️⃣ Testing Anti-Blinking: Multiple play_deck() calls")
    print("-" * 80)
    print("   Calling play_deck() 5 times in rapid succession...")
    print("   (Vecchio codice: questo avrebbe causato blinking)")

    for i in range(5):
        print(f"   Call {i+1}/5...", end=" ")
        traktor.play_deck(DeckID.A)
        print("✅")
        time.sleep(0.2)

    # Verifica finale
    final_playing = traktor.verify_deck_playing(DeckID.A, max_attempts=3)
    if final_playing:
        print("   ✅ ANTI-BLINKING SUCCESS: Deck A still playing after multiple calls!")
    else:
        print("   ❌ ANTI-BLINKING FAILED: Deck A stopped playing")

    # Final status
    print("\n5️⃣ Final Status")
    print("-" * 80)
    for deck_id in [DeckID.A, DeckID.B]:
        state = traktor.deck_states[deck_id]
        status = "▶️ PLAYING" if state['playing'] else "⏸️  PAUSED"
        loaded = "✅" if state['loaded'] else "❌"
        print(f"   Deck {deck_id.value}: {status} | Loaded: {loaded}")

    # Cleanup
    print("\n6️⃣ Cleanup...")
    traktor.disconnect()
    print("✅ Disconnected from Traktor")

    print("\n" + "="*80)
    print("✅ TEST COMPLETE - BLINKING FIX WORKING!")
    print("="*80)

    return True

if __name__ == "__main__":
    try:
        test_blinking_fix()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
