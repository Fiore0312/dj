#!/usr/bin/env python3
"""
🔍 Debug MIDI Dettagliato per DJ AI System
Analizza punto per punto dove si rompe la comunicazione MIDI
"""

import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    import rtmidi
    print("✅ rtmidi importato correttamente")
except ImportError as e:
    print(f"❌ Errore import rtmidi: {e}")
    sys.exit(1)

def list_midi_ports():
    """Lista tutte le porte MIDI disponibili"""
    print("\n🔍 ANALISI PORTE MIDI DISPONIBILI")
    print("=" * 50)

    # Output ports
    midiout = rtmidi.MidiOut()
    out_ports = midiout.get_ports()
    print(f"📤 PORTE OUTPUT ({len(out_ports)}):")
    for i, port in enumerate(out_ports):
        print(f"  [{i}] {port}")

    # Input ports
    midiin = rtmidi.MidiIn()
    in_ports = midiin.get_ports()
    print(f"\n📥 PORTE INPUT ({len(in_ports)}):")
    for i, port in enumerate(in_ports):
        print(f"  [{i}] {port}")

    return out_ports, in_ports

def test_iac_bus():
    """Test specifico IAC Bus 1"""
    print("\n🎛️ TEST IAC BUS 1")
    print("=" * 30)

    midiout = rtmidi.MidiOut()
    out_ports = midiout.get_ports()

    # Cerca IAC Driver Bus 1
    iac_port = None
    for i, port in enumerate(out_ports):
        if "IAC" in port and ("Bus 1" in port or "1" in port):
            iac_port = i
            print(f"✅ IAC Bus 1 trovato: [{i}] {port}")
            break

    if iac_port is None:
        print("❌ IAC Bus 1 NON trovato!")
        print("💡 Verifica che IAC Driver sia online in Audio MIDI Setup")
        return False

    return iac_port

def test_midi_messages(port_index):
    """Test invio messaggi MIDI specifici"""
    print(f"\n📡 TEST INVIO MESSAGGI MIDI su porta {port_index}")
    print("=" * 50)

    try:
        midiout = rtmidi.MidiOut()
        midiout.open_port(port_index)
        print(f"✅ Porta MIDI aperta")

        # Test diversi tipi di messaggi MIDI
        test_messages = [
            ([0xB0, 0x07, 0x40], "Control Change Ch1 CC7 (Volume) = 64"),
            ([0xB0, 0x07, 0x7F], "Control Change Ch1 CC7 (Volume) = 127 (MAX)"),
            ([0xB0, 0x07, 0x00], "Control Change Ch1 CC7 (Volume) = 0 (MIN)"),
            ([0x90, 0x40, 0x7F], "Note On Ch1 Note=64 Velocity=127"),
            ([0x80, 0x40, 0x00], "Note Off Ch1 Note=64"),
        ]

        for i, (message, description) in enumerate(test_messages):
            print(f"\n📤 Messaggio {i+1}/5: {description}")
            print(f"   Raw: {message}")

            midiout.send_message(message)
            print(f"   ✅ Inviato")

            time.sleep(2)  # Pausa tra messaggi

        midiout.close_port()
        print(f"\n✅ Test completato - porta chiusa")
        return True

    except Exception as e:
        print(f"❌ Errore durante test: {e}")
        return False

def test_traktor_specific():
    """Test specifico per Traktor Pro"""
    print("\n🎧 TEST SPECIFICO TRAKTOR PRO")
    print("=" * 40)

    iac_port = test_iac_bus()
    if iac_port is False:
        return False

    try:
        midiout = rtmidi.MidiOut()
        out_ports = midiout.get_ports()
        print(f"🎛️ Usando porta: {out_ports[iac_port]}")

        midiout.open_port(iac_port)

        # Messaggi specifici per Traktor (basati sul nostro mapping)
        traktor_messages = [
            # Volume Deck A (Channel 1, CC 7)
            ([0xB0, 0x07, 0x40], "Volume Deck A = 50%"),
            ([0xB0, 0x07, 0x7F], "Volume Deck A = 100%"),
            ([0xB0, 0x07, 0x20], "Volume Deck A = 25%"),

            # Volume Deck B (Channel 1, CC 8)
            ([0xB0, 0x08, 0x40], "Volume Deck B = 50%"),
            ([0xB0, 0x08, 0x7F], "Volume Deck B = 100%"),

            # Crossfader (Channel 1, CC 11)
            ([0xB0, 0x0B, 0x00], "Crossfader = Left"),
            ([0xB0, 0x0B, 0x40], "Crossfader = Center"),
            ([0xB0, 0x0B, 0x7F], "Crossfader = Right"),
        ]

        print("🎵 Invio sequenza messaggi Traktor...")
        print("👀 CONTROLLA SE L'ICONA MIDI DI TRAKTOR LAMPEGGIA!")

        for i, (message, description) in enumerate(traktor_messages):
            print(f"\n📤 {i+1}/8: {description}")
            midiout.send_message(message)
            time.sleep(1.5)  # Pausa più breve per vedere meglio

        midiout.close_port()
        print(f"\n✅ Test Traktor completato!")
        print("❓ L'icona MIDI di Traktor ha lampeggiato?")

        return True

    except Exception as e:
        print(f"❌ Errore test Traktor: {e}")
        return False

def main():
    """Test completo MIDI debug"""
    print("🎧 DJ AI SYSTEM - DEBUG MIDI DETTAGLIATO")
    print("=" * 60)
    print("🎯 Obiettivo: Trovare perché Traktor non riceve MIDI")
    print("=" * 60)

    # 1. Lista porte disponibili
    out_ports, in_ports = list_midi_ports()

    if not out_ports:
        print("\n❌ NESSUNA PORTA OUTPUT MIDI TROVATA!")
        print("💡 Verifica che IAC Driver sia configurato")
        return

    # 2. Test IAC Bus
    iac_port = test_iac_bus()
    if iac_port is False:
        print("\n❌ IAC Bus 1 non disponibile")
        print("💡 Configura IAC Driver in Audio MIDI Setup:")
        print("   - Apri Audio MIDI Setup")
        print("   - Finestra > Mostra MIDI Studio")
        print("   - Doppio click su IAC Driver")
        print("   - Spunta 'Il dispositivo è online'")
        return

    # 3. Test messaggi MIDI generici
    print("\n🔄 Avvio test messaggi MIDI...")
    success = test_midi_messages(iac_port)

    if not success:
        print("❌ Test messaggi MIDI fallito")
        return

    # 4. Test specifico Traktor
    print("\n🎧 IMPORTANTE: APRI TRAKTOR PRO 3 PRIMA DI CONTINUARE!")
    input("\n⏯️  Premi ENTER quando Traktor è aperto...")

    test_traktor_specific()

    print("\n" + "=" * 60)
    print("🎯 DEBUG COMPLETATO")
    print("=" * 60)
    print("✅ Se l'icona MIDI di Traktor ha lampeggiato = MIDI funziona")
    print("❌ Se NON ha lampeggiato = problema mapping/configurazione Traktor")
    print("\n💡 PROSSIMI PASSI se NON lampeggia:")
    print("   1. Verifica mapping in Controller Manager")
    print("   2. Reimporta traktor/AI_DJ_Complete.tsi")
    print("   3. Verifica che Device = 'Generic MIDI' con Bus 1")

if __name__ == "__main__":
    main()