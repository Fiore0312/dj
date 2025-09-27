#!/usr/bin/env python3
"""
🍎 Test MIDI macOS con IAC Driver
Test specifico per macOS che usa l'IAC Driver integrato
"""

import time
import sys
import subprocess
import platform

def check_macos_iac_driver():
    """Verifica e configura l'IAC Driver su macOS"""

    print("🍎 TEST MIDI macOS - IAC Driver")
    print("=" * 50)

    if platform.system() != "Darwin":
        print("❌ Questo test è specifico per macOS")
        return False

    print("🔍 Verifico configurazione IAC Driver...")

    # Verifica che l'IAC Driver sia abilitato
    print("\n💡 ISTRUZIONI PER ABILITARE IAC DRIVER:")
    print("1. Apri 'Audio MIDI Setup' (cerca in Spotlight)")
    print("2. Vai al menu Window > Show MIDI Studio")
    print("3. Fai doppio click su 'IAC Driver'")
    print("4. Spunta 'Device is online'")
    print("5. Assicurati che ci sia almeno una porta (Bus 1)")
    print("6. Premi 'Apply'")

    input("\n⏸️ Premi INVIO quando hai completato la configurazione IAC...")

    return True

def test_macos_midi():
    """Test MIDI specifico per macOS"""

    try:
        import rtmidi
        print("✅ rtmidi disponibile")
    except ImportError:
        print("❌ rtmidi non disponibile. Installa con: pip install python-rtmidi")
        return False

    # Scansiona porte MIDI
    print("\n🔍 Scansione porte MIDI macOS...")

    midi_out = rtmidi.MidiOut()
    output_ports = midi_out.get_ports()

    print(f"📤 Porte OUTPUT disponibili ({len(output_ports)}):")
    for i, port in enumerate(output_ports):
        print(f"   {i}: {port}")

    # Cerca IAC Driver
    iac_ports = [i for i, port in enumerate(output_ports) if 'IAC' in port or 'Bus' in port]

    if iac_ports:
        print(f"\n✅ IAC Driver trovato! Porte: {[output_ports[i] for i in iac_ports]}")

        # Usa la prima porta IAC
        iac_port_idx = iac_ports[0]
        iac_port_name = output_ports[iac_port_idx]

        print(f"\n🔗 Connessione a: {iac_port_name}")

        try:
            midi_out.open_port(iac_port_idx)
            print("✅ Connesso con successo!")

            # Test invio messaggi
            print("\n🧪 Test invio messaggi MIDI...")

            ping_count = 0
            print("🏓 Avvio ping test (ogni 3 secondi)")
            print("🎛️ Configura Traktor per ricevere da questa porta IAC!")
            print("🛑 Premi Ctrl+C per fermare")

            try:
                while True:
                    ping_count += 1

                    # Messaggio Control Change
                    msg = [0xB0, 127, 127]  # CC 127 = 127
                    midi_out.send_message(msg)
                    print(f"🏓 Ping {ping_count}: CC 127 = 127 inviato via {iac_port_name}")

                    time.sleep(0.1)

                    # Messaggio OFF
                    msg_off = [0xB0, 127, 0]
                    midi_out.send_message(msg_off)
                    print(f"🔄 Ping {ping_count}: CC 127 = 0 (off)")

                    print("⏰ Aspetto 3 secondi...")
                    time.sleep(3)

            except KeyboardInterrupt:
                print("\n🛑 Test interrotto")

        except Exception as e:
            print(f"❌ Errore connessione IAC: {e}")
            return False

    else:
        print("\n❌ IAC Driver non trovato!")
        print("\n🔧 CONFIGURAZIONE RICHIESTA:")
        print("1. Apri 'Audio MIDI Setup'")
        print("2. Window > Show MIDI Studio")
        print("3. Doppio click su 'IAC Driver'")
        print("4. Spunta 'Device is online'")
        print("5. Aggiungi almeno un Bus se non presente")

        # Prova a aprire Audio MIDI Setup automaticamente
        try:
            subprocess.run(['open', '/Applications/Utilities/Audio MIDI Setup.app'], check=True)
            print("\n✅ Audio MIDI Setup aperto automaticamente")
        except:
            print("\n💡 Apri manualmente Audio MIDI Setup dalle Applicazioni > Utility")

        return False

    # Cleanup
    try:
        midi_out.close()
    except:
        pass

    return True

def traktor_macos_setup():
    """Istruzioni per configurare Traktor su macOS"""

    print("\n" + "=" * 60)
    print("🎛️ CONFIGURAZIONE TRAKTOR PER macOS")
    print("=" * 60)

    print("\n📋 PASSO 1: Configura IAC Driver")
    print("   1. Apri 'Audio MIDI Setup'")
    print("   2. Menu Window > Show MIDI Studio")
    print("   3. Doppio click su 'IAC Driver'")
    print("   4. Spunta 'Device is online'")
    print("   5. Assicurati che 'Bus 1' sia presente")

    print("\n📋 PASSO 2: Configura Traktor")
    print("   1. Apri Traktor Pro")
    print("   2. Preferences > Controller Manager")
    print("   3. Add > Generic MIDI")
    print("   4. Input Device: seleziona 'Bus 1' (IAC Driver)")
    print("   5. Output Device: seleziona 'Bus 1' (IAC Driver)")
    print("   6. Aggiungi alcune mappature per test:")
    print("      - CC 127 -> qualsiasi controllo Traktor")

    print("\n📋 PASSO 3: Test")
    print("   1. Esegui questo script")
    print("   2. Osserva l'icona MIDI in Traktor")
    print("   3. Dovrebbe lampeggiare ogni 3 secondi")

    print("\n💡 TROUBLESHOOTING:")
    print("   - Se l'icona non lampeggia: verifica le mappature in Traktor")
    print("   - Se IAC non appare: riavvia Audio MIDI Setup")
    print("   - Se continua a non funzionare: riavvia il Mac")

if __name__ == "__main__":
    print("🍎 Test MIDI macOS con IAC Driver")
    print("Configurazione specifica per macOS")
    print("")

    try:
        # Step 1: Verifica/configura IAC
        if check_macos_iac_driver():
            # Step 2: Test MIDI
            if test_macos_midi():
                print("\n🎉 Test MIDI macOS completato con successo!")
            else:
                print("\n⚠️ Test MIDI fallito")
                traktor_macos_setup()

    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

    print("\n👋 Test completato")