#!/usr/bin/env python3
"""
🗂️ Browser Navigation Learn Helper - Traktor Pro 3
Script per trovare i comandi corretti per navigazione browser sequenziale
"""

import time
import sys
from pathlib import Path

# Aggiungi il path per importare TraktorController
sys.path.append(str(Path(__file__).parent.parent))

from core.traktor_control import TraktorController, DeckID
from core.config import DJConfig

def browser_learn_sequence():
    """Sequenza guidata per MIDI Learn della navigazione browser"""

    print("🗂️ BROWSER NAVIGATION LEARN HELPER - Traktor Pro 3")
    print("=" * 60)
    print("")
    print("🎯 FUNZIONI DA TROVARE:")
    print("• Tree Navigation UP (sequenziale, non jump)")
    print("• Tree Navigation DOWN (sequenziale, non jump)")
    print("• List Navigation UP (sequenziale, non jump)")
    print("• List Navigation DOWN (sequenziale, non jump)")
    print("• Folder Expand/Enter")
    print("• Folder Collapse/Back")
    print("")
    print("📋 PREPARAZIONE:")
    print("1. ✅ Apri Traktor Pro 3")
    print("2. ✅ Vai in Preferences → Controller Manager")
    print("3. ✅ Seleziona il tuo device MIDI")
    print("4. ✅ Browser deve essere visibile")
    print("")

    # Possibili nomi delle funzioni browser - CC LIBERI SENZA CONFLITTI
    browser_functions = [
        ("Browser Tree UP", "Browser → Tree → Select Up/Down", "CC 72"),
        ("Browser Tree DOWN", "Browser → Tree → Select Up/Down", "CC 73"),
        ("Browser List UP", "Browser → List → Select Up/Down", "CC 74"),
        ("Browser List DOWN", "Browser → List → Select Up/Down", "CC 92"),
        ("Browser Expand/Collapse", "Browser → Select Expand/Collapse", "CC 64"),
    ]

    input("Premi INVIO quando sei pronto per iniziare il Learn Mode...")

    try:
        config = DJConfig()
        controller = TraktorController(config)
        controller.connect()

        print("🚀 INIZIO SEQUENZA LEARN MODE")
        print("")

        for i, (function_name, suggested_path, suggested_cc) in enumerate(browser_functions):
            print(f"📡 STEP {i+1}/6: {function_name}")
            print(f"   Cerca in: {suggested_path}")
            print(f"   CC suggerito: {suggested_cc}")
            print("")
            print("👆 AZIONI IN TRAKTOR:")
            print("1. Cerca la funzione nel menu (prova Browser → ...")
            print("2. Potrebbe essere in 'Track Collection' o 'Browser'")
            print("3. Clicca 'Learn' accanto alla funzione")
            print("4. Quando vedi 'Learning...' aspetta il comando MIDI")
            print("")

            input("Premi INVIO quando hai attivato Learn Mode...")

            print("⏰ Invio comando MIDI tra 3 secondi...")
            for countdown in [3, 2, 1]:
                print(f"   {countdown}...")
                time.sleep(1)

            # Estraggo il numero CC dal suggested_cc
            cc_num = int(suggested_cc.split()[-1])

            # Invio comando MIDI
            success = controller._send_midi_command(1, cc_num, 127, f"{function_name} LEARN")

            if success:
                print(f"✅ {suggested_cc} inviato per {function_name}")
                time.sleep(1)

                # Invio anche comando OFF
                controller._send_midi_command(1, cc_num, 0, f"{function_name} LEARN OFF")
                print(f"   (comando OFF inviato)")
            else:
                print(f"❌ Errore invio {suggested_cc}")

            print("")
            print("🔍 VERIFICA IN TRAKTOR:")
            print(f"   - Learn Mode ha catturato {suggested_cc}?")
            print("   - La funzione è stata mappata?")
            print("")

            if i < len(browser_functions) - 1:
                input("Premi INVIO per continuare con la prossima funzione...")
                print("")

        controller.disconnect()

        print("🎉 LEARN SEQUENCE COMPLETATA!")
        print("")
        print("📋 FUNZIONI DA TESTARE:")
        for _, _, cc in browser_functions:
            print(f"   {cc}")
        print("")
        print("🧪 TESTA LE NUOVE MAPPATURE:")
        print("1. Salva le mappature in Traktor")
        print("2. Esegui il test delle nuove funzioni")
        print("")

    except Exception as e:
        print(f"❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

def test_new_browser_functions():
    """Test delle nuove funzioni browser dopo Learn Mode"""

    print("🧪 TEST NUOVE FUNZIONI BROWSER")
    print("=" * 40)

    try:
        config = DJConfig()
        controller = TraktorController(config)
        controller.connect()

        new_mappings = [
            ("Browser Tree UP", 72),
            ("Browser Tree DOWN", 73),
            ("Browser List UP", 74),
            ("Browser List DOWN", 92),
            ("Browser Expand/Collapse", 64),
        ]

        print("🎯 Test sequenziale delle nuove funzioni...")
        print("")

        for function_name, cc in new_mappings:
            print(f"🔴 Test {function_name} (CC {cc})...")

            success = controller._send_midi_command(1, cc, 127, f"{function_name} TEST")
            print(f"   Comando: {'✅' if success else '❌'}")
            time.sleep(2)

            print("")

        controller.disconnect()
        print("✅ Test completato!")
        print("")
        print("🎧 HAI VISTO NAVIGAZIONE SEQUENZIALE?")
        print("✓ Tree navigation si muove passo-passo?")
        print("✓ List navigation scorre traccia per traccia?")

    except Exception as e:
        print(f"❌ ERRORE: {e}")

if __name__ == "__main__":
    print("🗂️ BROWSER NAVIGATION LEARN HELPER")
    print("")
    print("Scegli modalità:")
    print("1. Learn Mode per trovare funzioni corrette")
    print("2. Test nuove funzioni browser")
    print("")

    try:
        choice = input("Inserisci scelta (1 o 2): ").strip()

        if choice == "1":
            browser_learn_sequence()
        elif choice == "2":
            test_new_browser_functions()
        else:
            print("❌ Scelta non valida")

    except KeyboardInterrupt:
        print("\n🛑 Interrotto dall'utente")
    except Exception as e:
        print(f"❌ ERRORE: {e}")