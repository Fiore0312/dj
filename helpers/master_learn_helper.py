#!/usr/bin/env python3
"""
🎛️ MASTER Button Learn Helper - Traktor Pro 3
Script per mappare i button MASTER usando Traktor Controller Manager Learn Mode
"""

import time
import sys
from pathlib import Path

# Aggiungi il path per importare TraktorController
sys.path.append(str(Path(__file__).parent.parent))

from core.traktor_control import TraktorController, DeckID
from core.config import DJConfig

def master_learn_sequence():
    """Sequenza guidata per MIDI Learn dei button MASTER"""

    print("🎛️ MASTER BUTTON LEARN HELPER - Traktor Pro 3")
    print("=" * 60)
    print("")
    print("📋 PREPARAZIONE:")
    print("1. ✅ Apri Traktor Pro 3")
    print("2. ✅ Vai in Preferences → Controller Manager")
    print("3. ✅ Seleziona il tuo device MIDI (es: IAC Driver Bus 1)")
    print("4. ✅ Clicca 'Learn' in alto a destra")
    print("")
    print("🎯 FUNZIONE DA MAPPARE:")
    print("Nome: 'Set as Tempo Master'")
    print("Posizione: Master Clock → Set Tempo Master")
    print("Tipo: Button, Interaction Mode: Toggle")
    print("")

    input("Premi INVIO quando sei pronto per iniziare il Learn Mode...")

    try:
        config = DJConfig()
        controller = TraktorController(config)
        controller.connect()

        # Definisco le mappature MASTER da imparare
        master_mappings = [
            ("DECK A MASTER", "Set as Tempo Master", "Deck A", 33),
            ("DECK B MASTER", "Set as Tempo Master", "Deck B", 37),
            ("DECK C MASTER", "Set as Tempo Master", "Deck C", 38),
            ("DECK D MASTER", "Set as Tempo Master", "Deck D", 39)
        ]

        print("🚀 INIZIO SEQUENZA LEARN MODE")
        print("")

        for i, (deck_name, function_name, deck_assignment, cc_num) in enumerate(master_mappings):
            print(f"📡 STEP {i+1}/4: {deck_name}")
            print(f"   Funzione: {function_name}")
            print(f"   Assignment: {deck_assignment}")
            print(f"   CC: {cc_num}")
            print("")
            print("👆 AZIONI IN TRAKTOR:")
            print(f"1. Cerca '{function_name}' nella lista funzioni")
            print(f"2. Seleziona Assignment: '{deck_assignment}'")
            print("3. Clicca 'Learn' accanto alla funzione")
            print("4. Quando vedi 'Learning...' aspetta il comando MIDI")
            print("")

            input("Premi INVIO quando hai attivato Learn Mode in Traktor...")

            print("⏰ Invio comando MIDI tra 3 secondi...")
            for countdown in [3, 2, 1]:
                print(f"   {countdown}...")
                time.sleep(1)

            # Invio comando MIDI
            success = controller._send_midi_command(1, cc_num, 127, f"{deck_name} LEARN")

            if success:
                print(f"✅ CC {cc_num} inviato per {deck_name}")
                time.sleep(1)

                # Invio anche il comando OFF per completezza
                controller._send_midi_command(1, cc_num, 0, f"{deck_name} LEARN OFF")
                print(f"   (comando OFF inviato)")
            else:
                print(f"❌ Errore invio CC {cc_num}")

            print("")
            print("🔍 VERIFICA IN TRAKTOR:")
            print(f"   - Il Learn Mode ha catturato CC {cc_num}?")
            print("   - La mappatura è stata creata correttamente?")
            print("")

            if i < len(master_mappings) - 1:
                input("Premi INVIO per continuare con il prossimo MASTER button...")
                print("")

        controller.disconnect()

        print("🎉 SEQUENZA LEARN COMPLETATA!")
        print("")
        print("📋 MAPPATURE CREATE:")
        print("CC 33 → Set as Tempo Master (Deck A)")
        print("CC 37 → Set as Tempo Master (Deck B)")
        print("CC 38 → Set as Tempo Master (Deck C)")
        print("CC 39 → Set as Tempo Master (Deck D)")
        print("")
        print("🔧 FINALIZZI IN TRAKTOR:")
        print("1. Clicka 'OK' per salvare le mappature")
        print("2. Testa i button MASTER con lo script di test")
        print("")

    except Exception as e:
        print(f"❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

def test_master_buttons():
    """Test rapido dei button MASTER dopo il Learn"""

    print("🧪 TEST MASTER BUTTONS")
    print("=" * 30)

    try:
        config = DJConfig()
        controller = TraktorController(config)
        controller.connect()

        print("🎯 Test sequenziale di tutti i MASTER buttons...")
        print("")

        for deck_id, cc in [(DeckID.A, 33), (DeckID.B, 37), (DeckID.C, 38), (DeckID.D, 39)]:
            print(f"🔴 Test MASTER {deck_id.value} (CC {cc})...")

            # Attiva MASTER
            success = controller.set_deck_master(deck_id, True)
            print(f"   ON: {'✅' if success else '❌'}")
            time.sleep(2)

            # Disattiva MASTER
            success = controller.set_deck_master(deck_id, False)
            print(f"   OFF: {'✅' if success else '❌'}")
            time.sleep(1)

            print("")

        controller.disconnect()
        print("✅ Test completato!")

    except Exception as e:
        print(f"❌ ERRORE: {e}")

if __name__ == "__main__":
    print("🎛️ MASTER BUTTON LEARN HELPER")
    print("")
    print("Scegli modalità:")
    print("1. Learn Mode guidato (RACCOMANDATO)")
    print("2. Test MASTER buttons esistenti")
    print("")

    try:
        choice = input("Inserisci scelta (1 o 2): ").strip()

        if choice == "1":
            master_learn_sequence()
        elif choice == "2":
            test_master_buttons()
        else:
            print("❌ Scelta non valida")

    except KeyboardInterrupt:
        print("\n🛑 Interrotto dall'utente")
    except Exception as e:
        print(f"❌ ERRORE: {e}")