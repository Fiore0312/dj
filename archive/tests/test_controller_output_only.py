#!/usr/bin/env python3
"""
🧪 Test TraktorController in modalità output-only
Verifica se il nostro controller funziona senza input port e test_connection
"""

import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID
from config import get_config

def test_controller_output_only():
    print("🧪 TEST TRAKTOR CONTROLLER - OUTPUT ONLY")
    print("=" * 50)
    print("🎯 Usa il nostro controller ma solo output")
    print("=" * 50)

    try:
        config = get_config()
        controller = TraktorController(config)

        print("🔌 Connessione in modalità output-only...")
        success = controller.connect(output_only=True)  # 🔑 MODALITÀ OUTPUT-ONLY

        if not success:
            print("❌ Connessione fallita!")
            return

        print("✅ Controller connesso (solo output)")
        print("👀 CONTROLLA SE TRAKTOR LAMPEGGIA!")

        # Test usando i metodi del controller
        print("\n📡 Test usando metodi TraktorController...")

        test_sequence = [
            ("Volume Deck A = 100%", lambda: controller.set_deck_volume(DeckID.A, 1.0)),
            ("Volume Deck A = 0%", lambda: controller.set_deck_volume(DeckID.A, 0.0)),
            ("Volume Deck A = 50%", lambda: controller.set_deck_volume(DeckID.A, 0.5)),
            ("Crossfader = Center", lambda: controller.set_crossfader(0.5)),
        ]

        for i, (desc, action) in enumerate(test_sequence):
            print(f"\n📤 {i+1}/4: {desc}")
            result = action()
            if result:
                print("   ✅ Comando inviato")
            else:
                print("   ❌ Comando fallito")
            time.sleep(2)

        # Statistiche
        stats = controller.get_stats()
        print(f"\n📊 Statistiche:")
        print(f"   Comandi inviati: {stats['commands_sent']}")
        print(f"   Errori: {stats['errors']}")

        controller.disconnect()
        print("\n✅ Test completato")
        print("❓ L'icona MIDI di Traktor ha lampeggiato?")
        print("🟢 SE SÌ = Il problema era l'input port o test_connection!")
        print("🔴 SE NO = Il problema è altrove")

    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_controller_output_only()