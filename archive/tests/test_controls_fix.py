#!/usr/bin/env python3
"""
🎛️ Test Controlli Fix - Diagnosi Play/Pause
Verifica perché i controlli non funzionano più
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID
from config import get_config

def test_controls_fix():
    print("🎛️ DIAGNOSI CONTROLLI PLAY/PAUSE")
    print("=" * 50)
    print("🎯 Verifica perché i controlli non funzionano più")
    print("=" * 50)

    try:
        config = get_config()
        print(f"✅ Config caricato")

        # Test 1: Controller creation
        print(f"\n1️⃣ Creazione controller...")
        controller = TraktorController(config)
        print(f"✅ Controller creato")

        # Test 2: Connection
        print(f"\n2️⃣ Connessione (modalità normale)...")
        success = controller.connect()

        if not success:
            print("❌ Connessione fallita! Questo è il problema principale.")
            print("Possibili cause:")
            print("- IAC Driver non attivo")
            print("- Porta già occupata da altro processo")
            print("- Traktor non aperto")
            return

        print("✅ Connesso!")

        # Test 3: Initial state
        print(f"\n3️⃣ Stato iniziale deck...")
        for deck in [DeckID.A, DeckID.B]:
            state = controller.get_deck_state(deck)
            print(f"   Deck {deck.value}: Playing={state['playing']}, Cued={state['cued']}")

        # Test 4: Play controls
        print(f"\n4️⃣ Test controlli Play...")
        print("   Play Deck A...")
        result = controller.play_deck(DeckID.A)
        print(f"   Risultato: {'✅' if result else '❌'}")

        if result:
            state = controller.get_deck_state(DeckID.A)
            print(f"   Nuovo stato: Playing={state['playing']}")

        time.sleep(2)

        print("   Pause Deck A...")
        result = controller.pause_deck(DeckID.A)
        print(f"   Risultato: {'✅' if result else '❌'}")

        if result:
            state = controller.get_deck_state(DeckID.A)
            print(f"   Nuovo stato: Playing={state['playing']}")

        # Test 5: MIDI stats
        print(f"\n5️⃣ Statistiche MIDI...")
        stats = controller.get_stats()
        print(f"   Comandi inviati: {stats['commands_sent']}")
        print(f"   Errori: {stats['errors']}")
        print(f"   Connesso: {stats['connected']}")

        # Test 6: Raw MIDI test
        print(f"\n6️⃣ Test MIDI raw...")
        print("   Invio comando raw volume...")
        raw_result = controller.set_deck_volume(DeckID.A, 0.7)
        print(f"   Risultato: {'✅' if raw_result else '❌'}")

        controller.disconnect()

        print(f"\n📋 DIAGNOSI:")
        if stats['commands_sent'] > 0:
            print("✅ MIDI communication funziona")
            if stats['errors'] == 0:
                print("✅ Nessun errore MIDI")
                print("🎯 I controlli dovrebbero funzionare!")
                print("   Possibili cause GUI:")
                print("   - Mapping Traktor non configurato")
                print("   - Tracce non caricate nei deck")
                print("   - Volume Traktor a zero")
            else:
                print("⚠️ Ci sono errori MIDI")
        else:
            print("❌ Nessun comando MIDI inviato - problema di connessione")

    except Exception as e:
        print(f"❌ Errore diagnosi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_controls_fix()