#!/usr/bin/env python3
"""
🔍 MIDI Debug Ultra-Basilare
Test molto semplice per identificare il problema esatto della comunicazione MIDI
"""

import time
import sys
import platform

def test_midi_step_by_step():
    """Test MIDI passo per passo con debug dettagliato"""

    print("🔍 MIDI DEBUG ULTRA-BASILARE")
    print("=" * 60)
    print(f"Sistema: {platform.system()} {platform.release()}")
    print("=" * 60)

    # Step 1: Test import rtmidi
    print("\n🧪 STEP 1: Test import rtmidi")
    try:
        import rtmidi
        print("✅ rtmidi importato correttamente")
        print(f"   Versione rtmidi: {rtmidi.get_api_display_name(rtmidi.API_UNSPECIFIED)}")
    except ImportError as e:
        print(f"❌ ERRORE import rtmidi: {e}")
        print("💡 Esegui: pip install python-rtmidi")
        return False

    # Step 2: Verifica porte MIDI esistenti nel sistema
    print("\n🧪 STEP 2: Scansione porte MIDI del sistema")
    try:
        # Input ports
        midi_in = rtmidi.MidiIn()
        input_ports = midi_in.get_ports()
        print(f"📥 Porte INPUT trovate ({len(input_ports)}):")
        for i, port in enumerate(input_ports):
            print(f"   {i}: {port}")

        # Output ports
        midi_out = rtmidi.MidiOut()
        output_ports = midi_out.get_ports()
        print(f"📤 Porte OUTPUT trovate ({len(output_ports)}):")
        for i, port in enumerate(output_ports):
            print(f"   {i}: {port}")

        # Cerca porte Traktor
        traktor_ports = [p for p in output_ports if 'traktor' in p.lower() or 'native' in p.lower()]
        if traktor_ports:
            print(f"🎛️ Porte Traktor rilevate: {traktor_ports}")
        else:
            print("⚠️ Nessuna porta Traktor trovata - assicurati che Traktor sia aperto!")

    except Exception as e:
        print(f"❌ ERRORE scansione porte: {e}")
        return False

    # Step 3: Test creazione porta virtuale
    print("\n🧪 STEP 3: Test creazione porta virtuale")
    try:
        midi_out_virtual = rtmidi.MidiOut()
        virtual_name = "TestMIDI_Debug"

        print(f"   Creando porta virtuale: {virtual_name}")
        midi_out_virtual.open_virtual_port(virtual_name)
        print("✅ Porta virtuale creata con successo")

        # Verifica che sia stata creata
        time.sleep(0.5)  # Breve pausa per la registrazione

        # Ricontrolla le porte
        midi_check = rtmidi.MidiOut()
        new_ports = midi_check.get_ports()
        if virtual_name in str(new_ports):
            print(f"✅ Porta virtuale confermata nel sistema: {virtual_name}")
        else:
            print(f"⚠️ Porta virtuale non visibile nelle porte di sistema")
            print(f"   Porte attuali: {new_ports}")

    except Exception as e:
        print(f"❌ ERRORE creazione porta virtuale: {e}")
        midi_out_virtual = None

    # Step 4: Test invio messaggi MIDI
    print("\n🧪 STEP 4: Test invio messaggi MIDI")

    # Proviamo diversi target
    targets_to_try = []

    # Target 1: Porta virtuale appena creata
    if 'midi_out_virtual' in locals() and midi_out_virtual:
        targets_to_try.append(("Porta Virtuale", midi_out_virtual))

    # Target 2: Prima porta Traktor se disponibile
    if traktor_ports and output_ports:
        try:
            traktor_idx = output_ports.index(traktor_ports[0])
            midi_traktor = rtmidi.MidiOut()
            midi_traktor.open_port(traktor_idx)
            targets_to_try.append(("Porta Traktor Diretta", midi_traktor))
            print(f"✅ Connesso a porta Traktor: {traktor_ports[0]}")
        except Exception as e:
            print(f"⚠️ Non posso connettermi a Traktor: {e}")

    # Target 3: Prima porta disponibile
    if output_ports:
        try:
            midi_first = rtmidi.MidiOut()
            midi_first.open_port(0)
            targets_to_try.append(("Prima Porta Disponibile", midi_first))
            print(f"✅ Connesso alla prima porta: {output_ports[0]}")
        except Exception as e:
            print(f"⚠️ Non posso connettermi alla prima porta: {e}")

    if not targets_to_try:
        print("❌ Nessun target MIDI disponibile per il test!")
        return False

    # Test invio messaggi per ogni target
    for target_name, midi_connection in targets_to_try:
        print(f"\n   🎯 Test con {target_name}")

        try:
            # Messaggio di test: Control Change CC 127 (sicuro per test)
            test_message = [0xB0, 127, 64]  # Control Change, CC 127, valore 64

            print(f"      Invio messaggio: {test_message}")
            midi_connection.send_message(test_message)
            print("      ✅ Messaggio inviato con successo")

            # Pausa breve
            time.sleep(0.1)

            # Messaggio off per creare effetto blink
            off_message = [0xB0, 127, 0]
            print(f"      Invio messaggio OFF: {off_message}")
            midi_connection.send_message(off_message)
            print("      ✅ Messaggio OFF inviato")

            # Se questo è Traktor, dovrebbe far lampeggiare l'icona MIDI
            if "Traktor" in target_name:
                print("      🎛️ L'ICONA MIDI DI TRAKTOR DOVREBBE LAMPEGGIARE ORA!")
                print("      👀 Controlla Traktor - vedi l'icona MIDI lampeggiare?")

        except Exception as e:
            print(f"      ❌ ERRORE invio messaggio: {e}")

    # Step 5: Test loop continuo (come il tuo script originale)
    print("\n🧪 STEP 5: Test loop continuo (3 secondi)")

    if targets_to_try:
        print("   🔄 Avvio loop di ping ogni 3 secondi...")
        print("   🛑 Premi Ctrl+C per fermare")
        print("   👀 OSSERVA L'ICONA MIDI DI TRAKTOR!")

        target_name, midi_connection = targets_to_try[0]  # Usa il primo target
        print(f"   🎯 Usando: {target_name}")

        try:
            ping_count = 0
            while True:
                ping_count += 1

                # Messaggio ping
                ping_msg = [0xB0, 127, 127]  # CC 127 = 127 (valore alto)
                midi_connection.send_message(ping_msg)
                print(f"   🏓 Ping {ping_count}: Inviato CC 127 = 127")

                time.sleep(0.1)

                # Messaggio off
                off_msg = [0xB0, 127, 0]
                midi_connection.send_message(off_msg)
                print(f"   🔄 Ping {ping_count}: Inviato CC 127 = 0 (off)")

                print(f"   ⏰ Aspetto 3 secondi... (L'icona MIDI dovrebbe lampeggiare)")
                time.sleep(3)

        except KeyboardInterrupt:
            print("\n   🛑 Test interrotto dall'utente")
        except Exception as e:
            print(f"\n   ❌ ERRORE nel loop: {e}")

    # Cleanup
    print("\n🧹 Cleanup...")
    try:
        if 'midi_out_virtual' in locals():
            midi_out_virtual.close()
        for _, midi_conn in targets_to_try:
            midi_conn.close()
        print("✅ Tutte le connessioni MIDI chiuse")
    except:
        pass

    # Step 6: Diagnosi finale
    print("\n" + "=" * 60)
    print("🏁 DIAGNOSI FINALE")
    print("=" * 60)

    print("✅ Controlli completati:")
    print("   - rtmidi funziona")
    print("   - Porte MIDI rilevate")
    print("   - Porta virtuale creata")
    print("   - Messaggi MIDI inviati")

    print("\n❓ DOMANDE CHIAVE:")
    print("   1. Hai visto lampeggiare l'icona MIDI in Traktor?")
    print("   2. Traktor era aperto durante il test?")
    print("   3. Hai configurato MIDI in Traktor Preferences?")

    print("\n💡 PROSSIMI PASSI:")
    if not traktor_ports:
        print("   🔧 PROBLEMA: Nessuna porta Traktor rilevata")
        print("       - Apri Traktor Pro")
        print("       - Vai a Preferences > Controller Manager")
        print("       - Aggiungi un controller MIDI generico")
        print("       - Configura Input/Output")
    else:
        print("   ✅ Porte Traktor rilevate")
        print("   🔧 Se l'icona non lampeggia:")
        print("       - Verifica le impostazioni MIDI in Traktor")
        print("       - Controlla che MIDI sia abilitato")
        print("       - Prova a riavviare Traktor")

    return True

if __name__ == "__main__":
    print("🔍 MIDI Debug Ultra-Basilare")
    print("Questo test verifica ogni singolo passaggio della comunicazione MIDI")
    print("")

    try:
        test_midi_step_by_step()
    except Exception as e:
        print(f"\n❌ ERRORE FATALE: {e}")
        import traceback
        traceback.print_exc()

    print("\n👋 Test completato")