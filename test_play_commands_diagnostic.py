#!/usr/bin/env python3
"""
🧪 Test Diagnostico Play Commands
Diagnosi approfondita dei comandi MIDI play per identificare perché le tracce non partono
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID
from config import get_config
import logging

# Setup logging dettagliato
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_play_command_variations():
    """Test diverse variazioni dei comandi play per diagnosticare il problema"""
    print("🧪 Test Diagnostico Play Commands...")
    print("="*60)

    try:
        # Setup
        config = get_config()
        controller = TraktorController(config)

        # Test connessione
        print("🔌 Testando connessione MIDI...")
        if not controller.connect():
            print("❌ ERRORE: Connessione MIDI fallita")
            print("   Verifica:")
            print("   1. Traktor Pro è avviato?")
            print("   2. IAC Driver abilitato?")
            print("   3. Mapping AI DJ importato?")
            return False

        print("✅ Connessione MIDI OK")
        print()

        # Test 1: Play Direct MIDI Commands
        print("="*60)
        print("🎯 TEST 1: COMANDI MIDI DIRETTI")
        print("="*60)

        test_cases = [
            {"name": "Play Deck A - Standard", "channel": 1, "cc": 20, "value": 127},
            {"name": "Play Deck A - Mid Value", "channel": 1, "cc": 20, "value": 64},
            {"name": "Play Deck A - Low Value", "channel": 1, "cc": 20, "value": 32},
            {"name": "Play Deck A - Toggle Off", "channel": 1, "cc": 20, "value": 0},
            {"name": "Play Deck B - Standard", "channel": 1, "cc": 21, "value": 127},
            {"name": "Play Deck B - Mid Value", "channel": 1, "cc": 21, "value": 64},
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n{i}. {test['name']}")
            print(f"   → Invio: CH{test['channel']} CC{test['cc']} Value={test['value']}")

            success = controller._send_midi_command(
                test['channel'],
                test['cc'],
                test['value'],
                test['name']
            )

            status = "✅ INVIATO" if success else "❌ FALLITO"
            print(f"   → Risultato: {status}")

            # Attendi e chiedi feedback
            print(f"   → CONTROLLA TRAKTOR: La traccia nel Deck {'A' if test['cc'] == 20 else 'B'} è partita?")
            print("     (Premi Enter per continuare)")
            input()

        # Test 2: High-Level Play Commands
        print("="*60)
        print("🎯 TEST 2: COMANDI HIGH-LEVEL")
        print("="*60)

        high_level_tests = [
            {"name": "play_deck(DeckID.A)", "action": lambda: controller.play_deck(DeckID.A)},
            {"name": "play_deck(DeckID.B)", "action": lambda: controller.play_deck(DeckID.B)},
            {"name": "toggle_play_pause(DeckID.A)", "action": lambda: controller.toggle_play_pause(DeckID.A)},
            {"name": "toggle_play_pause(DeckID.B)", "action": lambda: controller.toggle_play_pause(DeckID.B)},
        ]

        for i, test in enumerate(high_level_tests, 1):
            print(f"\n{i}. {test['name']}")
            print(f"   → Stato prima: Deck A={controller.is_deck_playing(DeckID.A)}, Deck B={controller.is_deck_playing(DeckID.B)}")

            try:
                result = test['action']()
                status = "✅ SUCCESS" if result else "❌ FAILED"
                print(f"   → Risultato Python: {status}")

                print(f"   → Stato dopo: Deck A={controller.is_deck_playing(DeckID.A)}, Deck B={controller.is_deck_playing(DeckID.B)}")

                print(f"   → CONTROLLA TRAKTOR: La traccia sta effettivamente suonando?")
                print("     (Premi Enter per continuare)")
                input()

            except Exception as e:
                print(f"   → ERRORE: {e}")

        # Test 3: Timing Analysis
        print("="*60)
        print("🎯 TEST 3: ANALISI TIMING")
        print("="*60)

        print("\n1. Test Load + Play Immediato")
        print("   → Carico traccia nel Deck A...")
        success_load = controller.load_track_to_deck(DeckID.A)
        print(f"   → Load result: {'✅' if success_load else '❌'}")

        print("   → Play immediato...")
        success_play = controller.play_deck(DeckID.A)
        print(f"   → Play result: {'✅' if success_play else '❌'}")
        print("   → CONTROLLA: La traccia suona?")
        input()

        print("\n2. Test Load + Delay + Play")
        print("   → Carico traccia nel Deck B...")
        success_load = controller.load_track_to_deck(DeckID.B)
        print(f"   → Load result: {'✅' if success_load else '❌'}")

        print("   → Attendo 2 secondi...")
        time.sleep(2)

        print("   → Play dopo delay...")
        success_play = controller.play_deck(DeckID.B)
        print(f"   → Play result: {'✅' if success_play else '❌'}")
        print("   → CONTROLLA: La traccia suona ora?")
        input()

        # Test 4: Status Verification
        print("="*60)
        print("🎯 TEST 4: VERIFICA STATI")
        print("="*60)

        print("\nStato Controller Interno:")
        print(f"   Deck A playing: {controller.is_deck_playing(DeckID.A)}")
        print(f"   Deck B playing: {controller.is_deck_playing(DeckID.B)}")
        print(f"   Deck A cued: {controller.is_deck_cued(DeckID.A)}")
        print(f"   Deck B cued: {controller.is_deck_cued(DeckID.B)}")

        print("\nStatus Traktor (dal controller):")
        status = controller.get_status()
        print(f"   Deck A BPM: {status.deck_a_bpm}")
        print(f"   Deck B BPM: {status.deck_b_bpm}")
        print(f"   Deck A Position: {status.deck_a_position}")
        print(f"   Deck B Position: {status.deck_b_position}")

        print("\nStati VS Realtà:")
        print("   CONTROLLA TRAKTOR e confronta con gli stati sopra")
        print("   - Le tracce che il controller pensa stiano suonando stanno effettivamente suonando?")
        print("   - I BPM sono corretti?")
        print("   - Le posizioni si stanno aggiornando?")

        # Statistiche finali
        print("="*60)
        print("📊 STATISTICHE DIAGNOSTICA")
        print("="*60)
        stats = controller.get_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")

        # Disconnect
        controller.disconnect()
        print("\n✅ Test diagnostico completato!")

        return True

    except Exception as e:
        print(f"❌ Errore durante test diagnostico: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_midi_mapping_verification():
    """Verifica che la mappatura MIDI sia corretta"""
    print("\n🗺️  Verifica Mappatura MIDI Play Commands...")

    from traktor_control import TraktorController

    expected_play_commands = [
        'deck_a_play',
        'deck_b_play',
        'deck_c_play',
        'deck_d_play'
    ]

    print("✅ Mappatura Play Commands:")
    for cmd in expected_play_commands:
        if cmd in TraktorController.MIDI_MAP:
            channel, cc = TraktorController.MIDI_MAP[cmd]
            print(f"   {cmd}: Channel {channel}, CC {cc}")
        else:
            print(f"   ❌ {cmd}: NON MAPPATO")

    print("\n📋 Checklist Traktor:")
    print("   1. Apri Traktor Pro 3")
    print("   2. Vai in Preferences → Controller Manager")
    print("   3. Trova 'DJ AI Controller' (Generic MIDI)")
    print("   4. Verifica mappings:")
    print("      - CH1 CC20 → Deck A → Play (Type: Button, Mode: Toggle)")
    print("      - CH1 CC21 → Deck B → Play (Type: Button, Mode: Toggle)")
    print("   5. Salva e chiudi preferences")
    print("\n⚠️  IMPORTANTE: Se questi mapping non esistono, creali manualmente!")

if __name__ == "__main__":
    print("🤖 DJ AI - Diagnostica Play Commands")
    print("="*60)

    try:
        # Verifica mappatura prima del test
        test_midi_mapping_verification()

        print("\n" + "="*60)
        print("🚀 INIZIANDO TEST DIAGNOSTICO")
        print("="*60)
        print("IMPORTANTE: Assicurati che:")
        print("1. Traktor Pro sia avviato")
        print("2. Una traccia sia già caricata nel Browser")
        print("3. IAC Driver sia abilitato")
        print("4. Mapping AI DJ sia importato")
        print()
        print("Premi Enter per iniziare il test...")
        input()

        success = test_play_command_variations()

        if success:
            print("\n🎉 DIAGNOSTICA COMPLETATA!")
            print("Analizza i risultati per identificare dove il workflow si interrompe.")
        else:
            print("\n❌ DIAGNOSTICA FALLITA!")

    except KeyboardInterrupt:
        print("\n⚠️  Test interrotto dall'utente")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()