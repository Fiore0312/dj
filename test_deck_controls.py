#!/usr/bin/env python3
"""
🎛️ Test Controlli Deck - Play/Pause/Cue
Verifica che i controlli deck funzionino correttamente con Traktor
"""

import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID
from config import get_config

def test_deck_controls():
    print("🎛️ TEST CONTROLLI DECK")
    print("=" * 40)
    print("🎯 Test Play/Pause/Cue con stato interno")
    print("=" * 40)

    try:
        config = get_config()
        controller = TraktorController(config)

        print("🔌 Connessione (output-only per test)...")
        success = controller.connect(output_only=True)

        if not success:
            print("❌ Connessione fallita!")
            return

        print("✅ Controller connesso")
        print("\n👀 CONTROLLA TRAKTOR PRO PER VERIFICARE LE AZIONI!")

        # Test sequence per Deck A
        deck = DeckID.A
        print(f"\n🎵 === TEST DECK {deck.value} ===")

        # Test 1: Play (da stato iniziale pause)
        print(f"\n1️⃣ Play Deck {deck.value}")
        print(f"   Stato prima: Playing={controller.is_deck_playing(deck)}")
        result = controller.play_deck(deck)
        print(f"   Comando: {'✅' if result else '❌'}")
        print(f"   Stato dopo: Playing={controller.is_deck_playing(deck)}")
        time.sleep(3)

        # Test 2: Play again (dovrebbe essere no-op)
        print(f"\n2️⃣ Play Deck {deck.value} (di nuovo)")
        print(f"   Stato prima: Playing={controller.is_deck_playing(deck)}")
        result = controller.play_deck(deck)
        print(f"   Comando: {'✅' if result else '❌'}")
        print(f"   Stato dopo: Playing={controller.is_deck_playing(deck)}")
        time.sleep(2)

        # Test 3: Pause
        print(f"\n3️⃣ Pause Deck {deck.value}")
        print(f"   Stato prima: Playing={controller.is_deck_playing(deck)}")
        result = controller.pause_deck(deck)
        print(f"   Comando: {'✅' if result else '❌'}")
        print(f"   Stato dopo: Playing={controller.is_deck_playing(deck)}")
        time.sleep(3)

        # Test 4: Cue
        print(f"\n4️⃣ Cue Deck {deck.value}")
        print(f"   Stato prima: Playing={controller.is_deck_playing(deck)}, Cued={controller.is_deck_cued(deck)}")
        result = controller.cue_deck(deck)
        print(f"   Comando: {'✅' if result else '❌'}")
        print(f"   Stato dopo: Playing={controller.is_deck_playing(deck)}, Cued={controller.is_deck_cued(deck)}")
        time.sleep(3)

        # Test 5: Toggle Play/Pause diretto
        print(f"\n5️⃣ Toggle Play/Pause Deck {deck.value}")
        print(f"   Stato prima: Playing={controller.is_deck_playing(deck)}")
        result = controller.toggle_play_pause(deck)
        print(f"   Comando: {'✅' if result else '❌'}")
        print(f"   Stato dopo: Playing={controller.is_deck_playing(deck)}")
        time.sleep(3)

        # Test rapido Deck B
        print(f"\n🎵 === TEST RAPIDO DECK B ===")
        deck_b = DeckID.B
        print(f"Play → Pause → Play")
        controller.play_deck(deck_b)
        time.sleep(2)
        controller.pause_deck(deck_b)
        time.sleep(2)
        controller.play_deck(deck_b)
        time.sleep(2)

        # Statistiche finali
        stats = controller.get_stats()
        print(f"\n📊 Statistiche:")
        print(f"   Comandi inviati: {stats['commands_sent']}")
        print(f"   Errori: {stats['errors']}")

        # Stato finale di tutti i deck
        print(f"\n📋 Stato finale deck:")
        for deck in [DeckID.A, DeckID.B]:
            state = controller.get_deck_state(deck)
            print(f"   Deck {deck.value}: Playing={state['playing']}, Cued={state['cued']}")

        controller.disconnect()
        print(f"\n✅ Test completato!")
        print(f"❓ I controlli in Traktor hanno risposto correttamente?")

    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_deck_controls()