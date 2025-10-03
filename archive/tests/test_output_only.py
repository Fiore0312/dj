#!/usr/bin/env python3
"""
🧪 Test MIDI con solo OUTPUT port
Verifica se il problema è l'apertura dell'input port o test_connection()
"""

import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    import rtmidi
except ImportError as e:
    print(f"❌ Errore import rtmidi: {e}")
    sys.exit(1)

def test_output_only():
    print("🧪 TEST MIDI - SOLO OUTPUT PORT")
    print("=" * 45)
    print("🎯 Come il test che funziona, solo output")
    print("=" * 45)

    try:
        # Esattamente come test_traktor_midi.py che funziona
        midiout = rtmidi.MidiOut()
        out_ports = midiout.get_ports()

        print("📤 Porte MIDI disponibili:")
        for i, port in enumerate(out_ports):
            print(f"  [{i}] {port}")

        # Trova IAC Bus 1
        iac_port = None
        for i, port in enumerate(out_ports):
            if "IAC" in port and ("Bus 1" in port or "1" in port):
                iac_port = i
                print(f"✅ IAC Bus 1 trovato: {port}")
                break

        if iac_port is None:
            print("❌ IAC Bus 1 non trovato!")
            return

        # SOLO apertura output port (come test che funziona)
        print(f"\n🔌 Apro SOLO porta output...")
        midiout.open_port(iac_port)
        print("✅ Porta output aperta")

        print("\n👀 CONTROLLA SE TRAKTOR LAMPEGGIA!")

        # Stessi messaggi del test funzionante
        messages = [
            ([0xB0, 0x07, 0x7F], "Volume Deck A = MAX"),
            ([0xB0, 0x07, 0x00], "Volume Deck A = MIN"),
            ([0xB0, 0x07, 0x40], "Volume Deck A = 50%"),
            ([0xB0, 0x0B, 0x40], "Crossfader = Center"),
        ]

        for i, (msg, desc) in enumerate(messages):
            print(f"\n📤 {i+1}/4: {desc}")
            print(f"   MIDI: {msg}")
            midiout.send_message(msg)
            time.sleep(2)

        midiout.close_port()
        print(f"\n✅ Test completato - porta chiusa")
        print(f"❓ L'icona MIDI di Traktor ha lampeggiato?")

    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    test_output_only()