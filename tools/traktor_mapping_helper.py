#!/usr/bin/env python3
"""
🎛️ Traktor Mapping Helper - Assistente per Learn Mode
Genera segnali MIDI specifici per facilitare il Learn mode in Traktor
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID
from config import get_config

def traktor_mapping_helper():
    print("🎛️ TRAKTOR MAPPING HELPER")
    print("=" * 50)
    print("🎯 Assistente per configurazione Learn Mode in Traktor")
    print("=" * 50)

    print("\n📋 ISTRUZIONI:")
    print("1. Apri Traktor → Preferences → Controller Manager")
    print("2. Add Generic → Generic MIDI")
    print("3. In-Port: Bus 1, Out-Port: Bus 1")
    print("4. Per ogni controllo: clicca 'Add In...', poi 'Learn'")
    print("5. Quando richiesto qui, premi INVIO per inviare il segnale MIDI")

    try:
        config = get_config()
        controller = TraktorController(config)

        print("\n🔌 Connessione controller...")
        success = controller.connect(output_only=True)

        if not success:
            print("❌ Connessione fallita!")
            return

        print("✅ Controller connesso")

        # Lista dei controlli da mappare in ordine di priorità
        mapping_controls = [
            {
                'name': 'Volume Deck A',
                'action': lambda: controller.set_deck_volume(DeckID.A, 0.5),
                'assignment': 'Deck A → Volume',
                'type': 'Fader',
                'mode': 'Direct'
            },
            {
                'name': 'Volume Deck B',
                'action': lambda: controller.set_deck_volume(DeckID.B, 0.5),
                'assignment': 'Deck B → Volume',
                'type': 'Fader',
                'mode': 'Direct'
            },
            {
                'name': 'Play Deck A',
                'action': lambda: controller.play_deck(DeckID.A),
                'assignment': 'Deck A → Play',
                'type': 'Button',
                'mode': 'Toggle'
            },
            {
                'name': 'Play Deck B',
                'action': lambda: controller.play_deck(DeckID.B),
                'assignment': 'Deck B → Play',
                'type': 'Button',
                'mode': 'Toggle'
            },
            {
                'name': 'Crossfader',
                'action': lambda: controller.set_crossfader(0.5),
                'assignment': 'Mixer → Crossfader',
                'type': 'Fader',
                'mode': 'Direct'
            },
            {
                'name': 'Cue Deck A',
                'action': lambda: controller.cue_deck(DeckID.A),
                'assignment': 'Deck A → Cue',
                'type': 'Button',
                'mode': 'Hold'
            },
            {
                'name': 'Cue Deck B',
                'action': lambda: controller.cue_deck(DeckID.B),
                'assignment': 'Deck B → Cue',
                'type': 'Button',
                'mode': 'Hold'
            }
        ]

        print(f"\n🚀 INIZIO PROCEDURA MAPPING - {len(mapping_controls)} CONTROLLI")
        print("=" * 50)

        for i, control in enumerate(mapping_controls, 1):
            print(f"\n📍 CONTROLLO {i}/{len(mapping_controls)}: {control['name']}")
            print("-" * 30)
            print(f"🎯 Assignment: {control['assignment']}")
            print(f"📝 Type: {control['type']}")
            print(f"⚙️ Mode: {control['mode']}")

            print(f"\n🔧 PASSI IN TRAKTOR:")
            print(f"1. Clicca 'Add In...'")
            print(f"2. Clicca 'Learn'")
            print(f"3. Assignment: {control['assignment']}")
            print(f"4. Type: {control['type']}")
            print(f"5. Interaction Mode: {control['mode']}")

            # Aspetta conferma utente
            input(f"\n⏳ Premi INVIO quando hai impostato Learn per '{control['name']}'...")

            # Invia segnale MIDI
            print(f"📡 Invio segnale MIDI per {control['name']}...")
            try:
                success = control['action']()
                if success:
                    print(f"✅ Segnale inviato!")
                else:
                    print(f"❌ Errore invio segnale")
            except Exception as e:
                print(f"❌ Errore: {e}")

            # Pausa per conferma mapping
            print(f"🔍 Traktor dovrebbe aver rilevato il segnale MIDI")
            input(f"⏳ Premi INVIO quando hai completato il mapping...")

        print(f"\n🎉 MAPPING COMPLETATO!")
        print("=" * 50)
        print(f"✅ Tutti i {len(mapping_controls)} controlli dovrebbero essere mappati")

        # Test finale
        print(f"\n🧪 TEST FINALE - Verifica che tutto funzioni:")
        input(f"⏳ Carica una traccia nel Deck A e premi INVIO...")

        print(f"📡 Test Play Deck A...")
        controller.play_deck(DeckID.A)
        print(f"🎵 La traccia dovrebbe essere partita!")

        time.sleep(2)

        print(f"📡 Test Pause Deck A...")
        controller.pause_deck(DeckID.A)
        print(f"⏸️ La traccia dovrebbe essere in pausa!")

        print(f"📡 Test Volume Deck A...")
        controller.set_deck_volume(DeckID.A, 0.8)
        print(f"🔊 Il volume dovrebbe essere aumentato!")

        controller.disconnect()

        print(f"\n🎊 CONFIGURAZIONE COMPLETATA!")
        print(f"🚀 Il DJ AI System è ora completamente funzionale!")

    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    traktor_mapping_helper()