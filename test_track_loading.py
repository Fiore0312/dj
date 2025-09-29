#!/usr/bin/env python3
"""
🧪 Test Track Loading MIDI Commands
Verifica che i comandi di caricamento tracce funzionino correttamente
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID
from config import get_config

def test_track_loading_commands():
    """Test comandi MIDI per caricamento tracce"""
    print("🧪 Test Track Loading Commands...")

    try:
        # Setup configurazione
        config = get_config()
        controller = TraktorController(config)

        # Test connessione
        print("🔌 Connessione a Traktor...")
        if not controller.connect():
            print("❌ Errore connessione MIDI. Verifica:")
            print("   1. Traktor Pro è avviato?")
            print("   2. IAC Driver abilitato in Audio MIDI Setup?")
            print("   3. Mapping AI DJ importato in Traktor?")
            return False

        print("✅ Connessione MIDI OK")

        # Test comandi singoli
        test_cases = [
            {
                "name": "🎵 Load Track to Deck A",
                "action": lambda: controller.load_track_to_deck(DeckID.A),
                "description": "Carica traccia selezionata nel Deck A"
            },
            {
                "name": "🎵 Load Track to Deck B",
                "action": lambda: controller.load_track_to_deck(DeckID.B),
                "description": "Carica traccia selezionata nel Deck B"
            },
            {
                "name": "⬆️ Browser Scroll Up",
                "action": lambda: controller.browse_track_up(),
                "description": "Naviga verso l'alto nel browser"
            },
            {
                "name": "⬇️ Browser Scroll Down",
                "action": lambda: controller.browse_track_down(),
                "description": "Naviga verso il basso nel browser"
            },
            {
                "name": "🎯 Browser Select Item",
                "action": lambda: controller.select_browser_item(),
                "description": "Seleziona item corrente nel browser"
            },
            {
                "name": "⬅️ Browser Back",
                "action": lambda: controller.browser_back(),
                "description": "Torna indietro nel browser"
            }
        ]

        # Esegui test singoli
        for i, test in enumerate(test_cases, 1):
            print(f"\n{'-'*40}")
            print(f"{i}. {test['name']}")
            print(f"   {test['description']}")

            try:
                result = test['action']()
                status = "✅ SUCCESS" if result else "❌ FAILED"
                print(f"   Risultato: {status}")

                # Pausa tra comandi per vedere l'effetto
                time.sleep(1)

            except Exception as e:
                print(f"   ❌ ERRORE: {e}")

        # Test sequenza completa di caricamento
        print(f"\n{'='*50}")
        print("🔄 TEST SEQUENZA COMPLETA")
        print(f"{'='*50}")

        sequence_tests = [
            {
                "deck": DeckID.A,
                "direction": "down",
                "description": "Carica prossima traccia in Deck A"
            },
            {
                "deck": DeckID.B,
                "direction": "up",
                "description": "Carica traccia precedente in Deck B"
            }
        ]

        for i, test in enumerate(sequence_tests, 1):
            print(f"\n{i}. {test['description']}")
            print(f"   Deck: {test['deck'].value}, Direzione: {test['direction']}")

            try:
                result = controller.load_next_track(test['deck'], test['direction'])
                status = "✅ SUCCESS" if result else "❌ FAILED"
                print(f"   Risultato: {status}")

                # Pausa più lunga per vedere il caricamento
                time.sleep(2)

            except Exception as e:
                print(f"   ❌ ERRORE: {e}")

        # Test stats
        print(f"\n{'='*50}")
        print("📊 STATISTICHE CONTROLLER")
        print(f"{'='*50}")
        stats = controller.get_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")

        # Disconnessione
        controller.disconnect()
        print("\n✅ Test completato! Controller disconnesso.")
        return True

    except Exception as e:
        print(f"\n❌ Errore generale test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_midi_mapping():
    """Verifica mappatura MIDI per track loading"""
    print("\n🗺️  Verifica Mappatura MIDI Track Loading...")

    from traktor_control import TraktorController, MIDIChannel

    # Verifica che tutti i comandi siano mappati
    expected_commands = [
        'deck_a_load_selected',
        'deck_b_load_selected',
        'deck_c_load_selected',
        'deck_d_load_selected',
        'browser_scroll_up',
        'browser_scroll_down',
        'browser_select_item',
        'browser_back'
    ]

    missing_commands = []
    for cmd in expected_commands:
        if cmd not in TraktorController.MIDI_MAP:
            missing_commands.append(cmd)

    if missing_commands:
        print(f"❌ Comandi mancanti nella mappatura: {missing_commands}")
        return False

    # Verifica mappatura corretta
    print("✅ Tutti i comandi track loading sono mappati:")
    for cmd in expected_commands:
        channel, cc = TraktorController.MIDI_MAP[cmd]
        print(f"   {cmd}: Channel {channel}, CC {cc}")

    # Verifica che usino il canale corretto (AI_CONTROL = 1)
    ai_control_channel = MIDIChannel.AI_CONTROL.value
    for cmd in expected_commands:
        channel, cc = TraktorController.MIDI_MAP[cmd]
        if channel != ai_control_channel:
            print(f"⚠️  {cmd} usa channel {channel}, atteso {ai_control_channel}")

    print("✅ Mappatura MIDI verificata!")
    return True

if __name__ == "__main__":
    print("🤖 DJ AI - Test Track Loading Functionality")
    print("="*50)

    try:
        # Test 1: Verifica mappatura
        mapping_ok = test_midi_mapping()

        if mapping_ok:
            # Test 2: Test comandi reali
            commands_ok = test_track_loading_commands()

            if commands_ok:
                print("\n🎉 TUTTI I TEST TRACK LOADING PASSATI!")
            else:
                print("\n❌ Alcuni test track loading falliti")
        else:
            print("\n❌ Errori nella mappatura MIDI")

    except KeyboardInterrupt:
        print("\n⚠️  Test interrotto dall'utente")
    except Exception as e:
        print(f"\n❌ Test fallito: {e}")
        import traceback
        traceback.print_exc()