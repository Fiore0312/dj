#!/usr/bin/env python3
"""
🔍 Debug del nostro TraktorController
Verifica esattamente cosa fa il nostro controller vs test diretto
"""

import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID
from config import get_config

def debug_our_controller():
    print("🔍 DEBUG NOSTRO TRAKTOR CONTROLLER")
    print("=" * 50)

    try:
        config = get_config()
        controller = TraktorController(config)

        print(f"📋 Config IAC Bus: {config.iac_bus_name}")
        print(f"📋 Device Name: {config.midi_device_name}")

        # Prima verifica porte disponibili
        import rtmidi
        midiout = rtmidi.MidiOut()
        ports = midiout.get_ports()

        print(f"\n📤 Porte MIDI disponibili:")
        for i, port in enumerate(ports):
            print(f"  [{i}] {port}")
            if "IAC" in port and "Bus 1" in port:
                print(f"      ⭐ Questa è la porta che useremo!")

        print(f"\n🔌 Connessione controller...")
        success = controller.connect()

        if not success:
            print("❌ Connessione fallita!")
            return

        print("✅ Controller connesso")

        # Test con debug dettagliato
        print(f"\n🧪 TEST MIDI CON DEBUG DETTAGLIATO")
        print("👀 CONTROLLA SE TRAKTOR LAMPEGGIA!")

        # Stesso test del working script
        test_commands = [
            ("Volume Deck A = MAX", 1, 7, 127),
            ("Volume Deck A = MIN", 1, 7, 0),
            ("Volume Deck A = 50%", 1, 7, 64),
            ("Crossfader = Center", 1, 11, 64),
        ]

        for i, (desc, channel, cc, value) in enumerate(test_commands):
            print(f"\n📤 Test {i+1}/4: {desc}")
            print(f"   MIDI: [0x{0xB0 + (channel-1):02X}, 0x{cc:02X}, 0x{value:02X}]")
            print(f"        = [{0xB0 + (channel-1)}, {cc}, {value}]")

            # Usa il metodo interno per vedere esattamente cosa fa
            result = controller._send_midi_command(channel, cc, value, desc)

            if result:
                print(f"   ✅ Inviato con successo")
            else:
                print(f"   ❌ Invio fallito")

            time.sleep(2)  # Pausa per vedere lampeggio

        print(f"\n📊 Statistiche finali:")
        stats = controller.get_stats()
        print(f"   Comandi inviati: {stats['commands_sent']}")
        print(f"   Errori: {stats['errors']}")

        controller.disconnect()

        print(f"\n❓ RISULTATO: L'icona MIDI di Traktor ha lampeggiato?")
        print(f"🟢 SE SÌ = Il nostro controller funziona!")
        print(f"🔴 SE NO = C'è un bug nella nostra implementazione")

    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_our_controller()