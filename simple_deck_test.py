#!/usr/bin/env python3
"""
🎯 Simple Deck Test

Test semplificato per identificare il problema Deck A → Deck B
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import time
from config import get_config
from traktor_control import TraktorController, DeckID

def simple_deck_test():
    """Test semplice per vedere quale deck risponde ai comandi"""
    print("🎯 SIMPLE DECK COMMAND TEST")
    print("=" * 40)

    # Inizializza
    config = get_config()
    traktor = TraktorController(config)

    print(f"Connection: {traktor.connected}")

    # Test 1: Comando a Deck A
    print(f"\n1️⃣ Sending PLAY command to DECK A...")
    print(f"   Using: traktor.play_deck(DeckID.A)")

    # Status prima
    status_before = traktor.get_status()
    print(f"   Before: {status_before}")

    # Comando
    result_a = traktor.play_deck(DeckID.A)
    print(f"   Command result: {result_a}")

    time.sleep(2.0)  # Attendi

    # Status dopo
    status_after_a = traktor.get_status()
    print(f"   After:  {status_after_a}")

    # Ferma tutto
    traktor.stop_deck(DeckID.A)
    traktor.stop_deck(DeckID.B)
    time.sleep(1.0)

    # Test 2: Comando a Deck B
    print(f"\n2️⃣ Sending PLAY command to DECK B...")
    print(f"   Using: traktor.play_deck(DeckID.B)")

    # Status prima
    status_before_b = traktor.get_status()
    print(f"   Before: {status_before_b}")

    # Comando
    result_b = traktor.play_deck(DeckID.B)
    print(f"   Command result: {result_b}")

    time.sleep(2.0)  # Attendi

    # Status dopo
    status_after_b = traktor.get_status()
    print(f"   After:  {status_after_b}")

    # Analisi
    print(f"\n🔍 ANALYSIS:")

    if status_after_a and status_before:
        deck_a_changed = False
        deck_b_changed = False

        # Controlla cosa è cambiato dopo comando Deck A
        for key in status_after_a.keys():
            if 'deck_a' in key.lower() and status_after_a.get(key) != status_before.get(key):
                deck_a_changed = True
                print(f"   Deck A command → Deck A responded: {key} changed")

            if 'deck_b' in key.lower() and status_after_a.get(key) != status_before.get(key):
                deck_b_changed = True
                print(f"   🔴 Deck A command → Deck B responded: {key} changed")

        if not deck_a_changed and not deck_b_changed:
            print(f"   ⚠️ Deck A command → No response from either deck")

    # Stop tutto
    traktor.stop_deck(DeckID.A)
    traktor.stop_deck(DeckID.B)

    print(f"\n📋 CONCLUSION:")
    print(f"   - Check which deck actually responds to each command")
    print(f"   - Look for swapped mappings in Traktor Controller Manager")
    print(f"   - Verify AI_DJ_Complete.tsi mapping file is correctly loaded")

if __name__ == "__main__":
    simple_deck_test()