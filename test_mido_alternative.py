#!/usr/bin/env python3
"""
🎵 Test MIDI Alternativo con mido
Test usando la libreria mido invece di rtmidi diretto
"""

import time
import sys

def test_mido_midi():
    """Test usando mido library"""

    print("🎵 TEST MIDI CON MIDO")
    print("=" * 40)

    # Test import mido
    try:
        import mido
        print("✅ mido importato correttamente")
        print(f"   Backend MIDI: {mido.backend}")
    except ImportError:
        print("❌ mido non disponibile. Installa con: pip install mido")
        return False

    # Scansiona porte
    print("\n🔍 Scansione porte con mido...")

    try:
        input_names = mido.get_input_names()
        output_names = mido.get_output_names()

        print(f"📥 Input ports ({len(input_names)}):")
        for i, name in enumerate(input_names):
            print(f"   {i}: {name}")

        print(f"📤 Output ports ({len(output_names)}):")
        for i, name in enumerate(output_names):
            print(f"   {i}: {name}")

    except Exception as e:
        print(f"❌ Errore scansione porte: {e}")
        return False

    # Test creazione porta virtuale
    print("\n🧪 Test creazione porta virtuale con mido...")

    try:
        # Crea porta output virtuale
        virtual_port = mido.open_output('TestMido_Virtual', virtual=True)
        print("✅ Porta virtuale mido creata: TestMido_Virtual")

        # Test invio messaggi
        print("\n🎛️ Test invio messaggi con mido...")

        # Crea messaggio Control Change
        msg = mido.Message('control_change', channel=0, control=127, value=64)
        print(f"📤 Invio messaggio: {msg}")

        virtual_port.send(msg)
        print("✅ Messaggio inviato con mido!")

        # Pausa
        time.sleep(0.1)

        # Messaggio off
        msg_off = mido.Message('control_change', channel=0, control=127, value=0)
        print(f"📤 Invio messaggio OFF: {msg_off}")
        virtual_port.send(msg_off)

        # Test loop continuo
        print("\n🔄 Test loop continuo (3 secondi)...")
        print("🛑 Premi Ctrl+C per fermare")

        ping_count = 0
        try:
            while True:
                ping_count += 1

                # Messaggio ON
                msg_on = mido.Message('control_change', channel=0, control=127, value=127)
                virtual_port.send(msg_on)
                print(f"🏓 Ping {ping_count}: {msg_on}")

                time.sleep(0.1)

                # Messaggio OFF
                msg_off = mido.Message('control_change', channel=0, control=127, value=0)
                virtual_port.send(msg_off)
                print(f"🔄 Ping {ping_count}: OFF")

                print("⏰ Aspetto 3 secondi...")
                time.sleep(3)

        except KeyboardInterrupt:
            print("\n🛑 Loop interrotto")

        # Chiudi porta
        virtual_port.close()
        print("✅ Porta virtuale chiusa")

    except Exception as e:
        print(f"❌ Errore test mido: {e}")
        return False

    # Test con porte esistenti
    if output_names:
        print(f"\n🧪 Test con prima porta esistente: {output_names[0]}")

        try:
            # Apri prima porta disponibile
            with mido.open_output(output_names[0]) as port:
                print(f"✅ Connesso a: {output_names[0]}")

                # Invia alcuni messaggi
                for i in range(3):
                    msg = mido.Message('control_change', channel=0, control=127, value=100)
                    port.send(msg)
                    print(f"📤 Messaggio {i+1} inviato a {output_names[0]}")

                    time.sleep(0.1)

                    msg_off = mido.Message('control_change', channel=0, control=127, value=0)
                    port.send(msg_off)

                    time.sleep(1)

                print("✅ Test porta esistente completato")

        except Exception as e:
            print(f"❌ Errore test porta esistente: {e}")

    return True

def compare_backends():
    """Confronta i backend MIDI disponibili"""

    print("\n" + "=" * 50)
    print("🔧 CONFRONTO BACKEND MIDI")
    print("=" * 50)

    # Test mido backend
    try:
        import mido
        print(f"✅ mido backend: {mido.backend}")

        # Prova diversi backend se disponibili
        backends = ['mido.backends.rtmidi', 'mido.backends.pygame']
        for backend_name in backends:
            try:
                mido.set_backend(backend_name)
                print(f"✅ Backend disponibile: {backend_name}")
            except:
                print(f"❌ Backend non disponibile: {backend_name}")

    except Exception as e:
        print(f"❌ Errore test backend: {e}")

    # Test rtmidi diretto
    print("\n🧪 Test rtmidi diretto...")
    try:
        import rtmidi
        midi_out = rtmidi.MidiOut()
        ports = midi_out.get_ports()
        print(f"✅ rtmidi diretto: {len(ports)} porte trovate")
    except Exception as e:
        print(f"❌ rtmidi diretto fallito: {e}")

if __name__ == "__main__":
    print("🎵 Test MIDI Alternativo con mido")
    print("Test usando mido invece di rtmidi diretto")
    print("")

    try:
        # Test principale
        success = test_mido_midi()

        # Confronta backend
        compare_backends()

        if success:
            print("\n🎉 Test mido completato con successo!")

            print("\n💡 SE QUESTO FUNZIONA MA rtmidi NO:")
            print("   - Usa mido nel tuo codice principale")
            print("   - Il problema è specifico di rtmidi")
            print("   - mido è un wrapper più stabile")

        else:
            print("\n⚠️ Test mido fallito")
            print("💡 Possibili cause:")
            print("   - Driver MIDI di sistema")
            print("   - Permessi di accesso")
            print("   - Configurazione audio macOS")

    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

    print("\n👋 Test completato")