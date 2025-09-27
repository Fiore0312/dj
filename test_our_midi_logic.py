#!/usr/bin/env python3
"""
🎧 Test Logica MIDI del nostro DJ AI System
Simula esattamente quello che fa il nostro controller
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID
from config import get_config

def main():
    print("🎧 TEST LOGICA MIDI DJ AI SYSTEM")
    print("=" * 45)
    print("🎯 Simula esattamente il test MIDI della GUI")
    print("=" * 45)

    try:
        # Usa la stessa logica del nostro sistema
        config = get_config()
        controller = TraktorController(config)

        print("🔌 Connessione controller...")
        success = controller.connect()

        if not success:
            print("❌ Connessione fallita")
            print("💡 Verifica IAC Driver in Audio MIDI Setup")
            return

        print("✅ Controller connesso")
        print(f"📤 MIDI Out: {controller.midi_out}")

        # Simula esattamente il test della GUI
        print("\n📡 Invio comandi come nel test GUI...")

        for i in range(5):
            print(f"\n🎛️ Test {i+1}/5: Volume Deck A = 0.5")

            # Questo è esattamente quello che fa la GUI
            result = controller.set_deck_volume(DeckID.A, 0.5)

            if result:
                print("   ✅ Comando inviato con successo")
            else:
                print("   ❌ Comando fallito")

            # Aggiungi anche alcuni altri comandi per test completo
            if i == 2:  # Test a metà
                print("   🔀 Test crossfader...")
                controller.set_crossfader(0.5)

        print("\n✅ Test completato")
        print("👀 Controlla se l'icona MIDI di Traktor ha lampeggiato")

        # Statistiche
        stats = controller.get_stats()
        print(f"\n📊 Statistiche:")
        print(f"   Comandi inviati: {stats['commands_sent']}")
        print(f"   Connesso da: {stats['uptime_seconds']:.1f}s")

        controller.disconnect()
        print("🔌 Disconnesso")

    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()