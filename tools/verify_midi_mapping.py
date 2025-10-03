#!/usr/bin/env python3
"""
🎛️ Verifica Mapping MIDI - Analisi comandi esatti
Mostra esattamente quali messaggi MIDI vengono inviati per ogni controllo
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID
from config import get_config

def verify_midi_mapping():
    print("🎛️ VERIFICA MAPPING MIDI DJ AI SYSTEM")
    print("=" * 60)
    print("🎯 Analizziamo esattamente quali comandi MIDI vengono inviati")
    print("=" * 60)

    try:
        config = get_config()
        controller = TraktorController(config)

        # Connessione output-only per test
        print("\n🔌 Connessione controller (test mode)...")
        success = controller.connect(output_only=True)

        if not success:
            print("❌ Connessione fallita!")
            return

        print("✅ Controller connesso")

        # Stampiamo la mappa MIDI del controller
        print("\n📋 MAPPA MIDI CONTROLLER:")
        print("-" * 40)

        midi_map = controller.MIDI_MAP
        for control, (channel, cc) in midi_map.items():
            print(f"{control:<20} → Channel {channel:2d}, CC {cc:3d}")

        print("\n🧪 TEST CONTROLLI CON VALORI ESATTI:")
        print("👀 OSSERVA TRAKTOR E CONTROLLA SE I VALORI CAMBIANO!")
        print("-" * 60)

        # Test controlli principali con valori specifici
        test_controls = [
            # (descrizione, funzione, valore_atteso)
            ("🎵 Volume Deck A = 50%", lambda: controller.set_deck_volume(DeckID.A, 0.5), "CH1 CC7 = 64"),
            ("🎵 Volume Deck A = 100%", lambda: controller.set_deck_volume(DeckID.A, 1.0), "CH1 CC7 = 127"),
            ("🎵 Volume Deck A = 0%", lambda: controller.set_deck_volume(DeckID.A, 0.0), "CH1 CC7 = 0"),

            ("🎵 Volume Deck B = 75%", lambda: controller.set_deck_volume(DeckID.B, 0.75), "CH1 CC8 = 95"),

            ("🔀 Crossfader = Center", lambda: controller.set_crossfader(0.5), "CH1 CC11 = 64"),
            ("🔀 Crossfader = Full A", lambda: controller.set_crossfader(0.0), "CH1 CC11 = 0"),
            ("🔀 Crossfader = Full B", lambda: controller.set_crossfader(1.0), "CH1 CC11 = 127"),

            ("🎚️ EQ High A = 50%", lambda: controller.set_eq(DeckID.A, 'high', 0.5), "CH1 CC12 = 64"),
            ("🎚️ EQ Mid A = 75%", lambda: controller.set_eq(DeckID.A, 'mid', 0.75), "CH1 CC13 = 95"),
            ("🎚️ EQ Low A = 25%", lambda: controller.set_eq(DeckID.A, 'low', 0.25), "CH1 CC14 = 32"),

            ("▶️ Play Deck A", lambda: controller.play_deck(DeckID.A), "CH1 CC20 = 127 (TRIGGER)"),
            ("⏸️ Pause Deck A", lambda: controller.pause_deck(DeckID.A), "CH1 CC20 = 127 (TRIGGER)"),

            ("▶️ Play Deck B", lambda: controller.play_deck(DeckID.B), "CH1 CC21 = 127 (TRIGGER)"),

            ("🎯 Cue Deck A", lambda: controller.cue_deck(DeckID.A), "CH1 CC24 = 127 (TRIGGER)"),
            ("🔄 Sync Deck A", lambda: controller.sync_deck(DeckID.A), "CH1 CC28 = 127 (TRIGGER)"),
        ]

        for i, (description, action, expected) in enumerate(test_controls, 1):
            print(f"\n{i:2d}. {description}")
            print(f"    Atteso: {expected}")

            try:
                # Esegui azione
                result = action()
                status = "✅ Inviato" if result else "❌ Fallito"
                print(f"    Risultato: {status}")

                # Pausa per osservare in Traktor
                time.sleep(2)

            except Exception as e:
                print(f"    ❌ Errore: {e}")

        # Statistiche finali
        stats = controller.get_stats()
        print(f"\n📊 STATISTICHE FINALI:")
        print(f"   Comandi MIDI inviati: {stats['commands_sent']}")
        print(f"   Errori: {stats['errors']}")

        controller.disconnect()

        print(f"\n🎯 CONFIGURAZIONE TRAKTOR MANUALE:")
        print(f"=" * 60)
        print(f"Se Traktor non risponde ai comandi, configura manualmente:")
        print(f"")
        print(f"1. Traktor Pro → Preferences → Controller Manager")
        print(f"2. Add Generic → Generic MIDI")
        print(f"3. In Port: Bus 1 (IAC Driver)")
        print(f"4. Out Port: Bus 1 (IAC Driver)")
        print(f"5. Crea mappings per ogni controllo:")
        print(f"")

        # Tabella mappings più importanti
        important_mappings = [
            ("Volume Deck A", "CH 1, CC 7", "Deck A Volume"),
            ("Volume Deck B", "CH 1, CC 8", "Deck B Volume"),
            ("Crossfader", "CH 1, CC 11", "Crossfader"),
            ("Play Deck A", "CH 1, CC 20", "Deck A Play (Button)"),
            ("Play Deck B", "CH 1, CC 21", "Deck B Play (Button)"),
            ("Cue Deck A", "CH 1, CC 24", "Deck A Cue (Button)"),
            ("Cue Deck B", "CH 1, CC 25", "Deck B Cue (Button)"),
        ]

        print(f"   MAPPINGS PRIORITARI:")
        for control, midi, traktor in important_mappings:
            print(f"   {control:<15} {midi:<12} → {traktor}")

        print(f"\n💡 SUGGERIMENTI:")
        print(f"   - Per Play/Cue usa 'Button' type (trigger)")
        print(f"   - Per Volume/EQ/Crossfader usa 'Fader' type")
        print(f"   - Range MIDI: 0-127")
        print(f"   - Assicurati che 'Learn' sia attivo quando mappi")

    except Exception as e:
        print(f"❌ Errore verifica: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_midi_mapping()