#!/usr/bin/env python3
"""
🎧 Test MIDI Diretto per Traktor
Invia messaggi MIDI specifici per verificare se Traktor riceve
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

def main():
    print("🎧 TEST MIDI DIRETTO PER TRAKTOR")
    print("=" * 40)
    print("🎯 OBIETTIVO: Verificare se Traktor riceve MIDI")
    print("=" * 40)

    # Trova IAC Bus 1
    midiout = rtmidi.MidiOut()
    out_ports = midiout.get_ports()

    print("📤 Porte MIDI disponibili:")
    for i, port in enumerate(out_ports):
        print(f"  [{i}] {port}")

    iac_port = None
    for i, port in enumerate(out_ports):
        if "IAC" in port and ("Bus 1" in port or "1" in port):
            iac_port = i
            break

    if iac_port is None:
        print("❌ IAC Bus 1 non trovato!")
        return

    try:
        print(f"\n🎛️ Connessione a: {out_ports[iac_port]}")
        midiout.open_port(iac_port)

        print("\n🚨 IMPORTANTE:")
        print("  1. Apri Traktor Pro 3")
        print("  2. Vai in Help > Controller Manager")
        print("  3. Verifica che il mapping AI_DJ_Complete sia ATTIVO (spunta)")
        print("  4. Verifica che Device = 'Generic MIDI'")
        print("  5. Verifica che In/Out Port = 'Bus 1'")
        print("\n👀 GUARDA L'ICONA MIDI IN TRAKTOR (dovrebbe lampeggiare)!")

        # Messaggi di test per Traktor
        messages = [
            # Volume Deck A - Control Change Channel 1, CC 7
            ([0xB0, 0x07, 0x7F], "Volume Deck A = MAX"),
            ([0xB0, 0x07, 0x00], "Volume Deck A = MIN"),
            ([0xB0, 0x07, 0x40], "Volume Deck A = 50%"),

            # Volume Deck B - Control Change Channel 1, CC 8
            ([0xB0, 0x08, 0x7F], "Volume Deck B = MAX"),
            ([0xB0, 0x08, 0x00], "Volume Deck B = MIN"),

            # Crossfader - Control Change Channel 1, CC 11
            ([0xB0, 0x0B, 0x00], "Crossfader = Left"),
            ([0xB0, 0x0B, 0x7F], "Crossfader = Right"),
            ([0xB0, 0x0B, 0x40], "Crossfader = Center"),
        ]

        print(f"\n📡 Invio {len(messages)} messaggi MIDI...")

        for i, (msg, desc) in enumerate(messages):
            print(f"\n📤 {i+1}/{len(messages)}: {desc}")
            print(f"   MIDI: Channel={msg[0]:02X} CC={msg[1]} Value={msg[2]}")

            midiout.send_message(msg)
            time.sleep(2)  # Pausa per vedere il lampeggio

        midiout.close_port()

        print("\n" + "=" * 50)
        print("✅ TEST COMPLETATO")
        print("=" * 50)
        print("❓ RISULTATO: L'icona MIDI di Traktor ha lampeggiato?")
        print("")
        print("🟢 SE SÌ = MIDI funziona, problema nel DJ AI System")
        print("🔴 SE NO = problema configurazione Traktor:")
        print("   • Verifica mapping in Controller Manager")
        print("   • Re-importa traktor/AI_DJ_Complete.tsi")
        print("   • Verifica che Generic MIDI sia su Bus 1")
        print("   • Riavvia Traktor")

    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    main()