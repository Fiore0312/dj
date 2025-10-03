#!/usr/bin/env python3
"""
🧪 MIDI Mapping Verification Tool
Diagnostica completa per verificare che tutti i comandi MIDI corrispondano
effettivamente ai controlli di Traktor Pro
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID
from config import get_config
import logging

# Setup logging dettagliato
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_midi_mapping_verification():
    """Test sistematico di tutti i comandi MIDI per verificare corrispondenza con Traktor"""
    print("🧪 MIDI Mapping Verification Tool")
    print("=" * 80)
    print("Questo test verifica che ogni comando MIDI corrisponda al controllo corretto in Traktor")
    print("📋 IMPORTANTE: Controlla visivamente Traktor per ogni test!")
    print("=" * 80)

    try:
        # Setup
        config = get_config()
        controller = TraktorController(config)

        # Test connessione
        print("\n🔌 Testando connessione MIDI...")
        if not controller.connect():
            print("❌ ERRORE: Connessione MIDI fallita")
            print("   Checklist:")
            print("   1. Traktor Pro 3 è avviato?")
            print("   2. IAC Driver abilitato in Audio MIDI Setup?")
            print("   3. Mapping AI DJ importato in Controller Manager?")
            print("   4. Mapping attivo (non in conflitto)?")
            return False

        print("✅ Connessione MIDI OK")

        # Mappings da testare (basati su TraktorController.MIDI_MAP)
        test_mappings = {
            # TRANSPORT CONTROLS
            "deck_a_play": (1, 20, "Play/Pause Deck A"),
            "deck_b_play": (1, 21, "Play/Pause Deck B"),
            "deck_c_play": (1, 22, "Play/Pause Deck C"),
            "deck_d_play": (1, 23, "Play/Pause Deck D"),

            "deck_a_cue": (1, 24, "Cue Deck A"),
            "deck_b_cue": (1, 25, "Cue Deck B"),
            "deck_c_cue": (1, 26, "Cue Deck C"),
            "deck_d_cue": (1, 27, "Cue Deck D"),

            # VOLUME CONTROLS
            "deck_a_volume": (1, 28, "Volume Fader Deck A"),
            "deck_b_volume": (1, 29, "Volume Fader Deck B"),
            "deck_c_volume": (1, 30, "Volume Fader Deck C"),
            "deck_d_volume": (1, 31, "Volume Fader Deck D"),

            # CROSSFADER
            "crossfader": (1, 32, "Crossfader"),

            # MASTER VOLUME
            "master_volume": (1, 33, "Master Volume"),

            # EQ CONTROLS (Deck A)
            "deck_a_eq_high": (1, 34, "EQ High Deck A"),
            "deck_a_eq_mid": (1, 35, "EQ Mid Deck A"),
            "deck_a_eq_low": (1, 36, "EQ Low Deck A"),

            # BROWSER CONTROLS
            "browser_up": (1, 37, "Browser Navigate Up"),
            "browser_down": (1, 38, "Browser Navigate Down"),
            "browser_load_deck_a": (1, 39, "Browser Load to Deck A"),
            "browser_load_deck_b": (1, 40, "Browser Load to Deck B"),

            # SYNC CONTROLS
            "deck_a_sync": (1, 41, "Sync Deck A"),
            "deck_b_sync": (1, 42, "Sync Deck B"),

            # PITCH CONTROLS
            "deck_a_pitch": (1, 43, "Pitch Fader Deck A"),
            "deck_b_pitch": (1, 44, "Pitch Fader Deck B"),
        }

        print(f"\n📋 Testando {len(test_mappings)} mappings...")
        print("\nPer ogni test:")
        print("1. Osserva cosa succede in Traktor")
        print("2. Conferma se il controllo è corretto")
        print("3. Annota eventuali discrepanze")
        print("\nPremi Enter per iniziare...")
        input()

        # Test sistematico
        results = {}
        failed_mappings = []

        for i, (command_name, (channel, cc, description)) in enumerate(test_mappings.items(), 1):
            print(f"\n{'='*60}")
            print(f"TEST {i}/{len(test_mappings)}: {command_name}")
            print(f"{'='*60}")
            print(f"📤 Invio: Channel {channel}, CC {cc}")
            print(f"🎯 Atteso: {description}")
            print(f"📋 Controlla in Traktor: {description}")

            # Test con valore medio per controlli continui
            test_value = 64 if "volume" in command_name or "eq" in command_name or "pitch" in command_name or "crossfader" in command_name else 127

            # Invio comando
            print(f"   → Invio valore {test_value}...")
            success = controller._send_midi_command(channel, cc, test_value, command_name)

            if success:
                print(f"   ✅ Comando inviato con successo")
            else:
                print(f"   ❌ Errore nell'invio del comando")
                failed_mappings.append((command_name, "Send failed"))
                continue

            # Pausa per osservazione
            time.sleep(0.5)

            # Chiedi feedback utente
            print(f"\n❓ VERIFICA TRAKTOR:")
            print(f"   Il controllo '{description}' ha risposto correttamente?")
            print(f"   [y] Sì, funziona correttamente")
            print(f"   [n] No, controllo sbagliato o nessuna risposta")
            print(f"   [w] Controllo sbagliato (specificare quale)")

            while True:
                response = input("   Risposta [y/n/w]: ").lower().strip()
                if response in ['y', 'yes', 's', 'si']:
                    results[command_name] = "✅ CORRETTO"
                    print(f"   ✅ {command_name} verificato come corretto")
                    break
                elif response in ['n', 'no']:
                    results[command_name] = "❌ SBAGLIATO/NON RISPONDE"
                    failed_mappings.append((command_name, "Wrong control or no response"))
                    print(f"   ❌ {command_name} non funziona correttamente")
                    break
                elif response in ['w', 'wrong']:
                    actual_control = input("   Quale controllo ha risposto? ").strip()
                    results[command_name] = f"❌ CONTROLLO SBAGLIATO: {actual_control}"
                    failed_mappings.append((command_name, f"Wrong control: {actual_control}"))
                    print(f"   ❌ {command_name} attiva il controllo sbagliato: {actual_control}")
                    break
                else:
                    print("   ⚠️ Risposta non valida. Usa [y/n/w]")

            # Reset valore per controlli continui
            if test_value != 127:
                controller._send_midi_command(channel, cc, 0, f"{command_name}_reset")
                time.sleep(0.2)

        # REPORT FINALE
        print(f"\n{'='*80}")
        print("📊 REPORT VERIFICA MIDI MAPPING")
        print(f"{'='*80}")

        correct_count = sum(1 for result in results.values() if "✅" in result)
        total_count = len(results)

        print(f"\n📈 STATISTICHE:")
        print(f"   Mappings corretti: {correct_count}/{total_count} ({correct_count/total_count*100:.1f}%)")
        print(f"   Mappings da correggere: {len(failed_mappings)}")

        print(f"\n✅ MAPPINGS CORRETTI:")
        for command, result in results.items():
            if "✅" in result:
                channel, cc, desc = test_mappings[command]
                print(f"   {command}: CH{channel} CC{cc} → {desc}")

        if failed_mappings:
            print(f"\n❌ MAPPINGS DA CORREGGERE:")
            for command, issue in failed_mappings:
                channel, cc, desc = test_mappings[command]
                print(f"   {command}: CH{channel} CC{cc} → {desc}")
                print(f"      Problema: {issue}")

        print(f"\n📋 AZIONI NECESSARIE:")
        if failed_mappings:
            print("   1. Aprire Traktor Pro 3")
            print("   2. Preferences → Controller Manager")
            print("   3. Selezionare 'DJ AI Controller' (Generic MIDI)")
            print("   4. Correggere i mapping sopra elencati")
            print("   5. Assicurarsi che Type sia corretto (Button/Fader)")
            print("   6. Verificare Mode (Toggle per Button, Direct per Fader)")
            print("   7. Salvare e rieseguire questo test")
        else:
            print("   🎉 Tutti i mapping sono corretti!")
            print("   Il sistema dovrebbe funzionare perfettamente.")

        # Salva report su file
        report_file = "midi_mapping_verification_report.txt"
        with open(report_file, 'w') as f:
            f.write("MIDI Mapping Verification Report\n")
            f.write("="*50 + "\n\n")
            f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mappings testati: {total_count}\n")
            f.write(f"Mappings corretti: {correct_count}\n")
            f.write(f"Successo: {correct_count/total_count*100:.1f}%\n\n")

            f.write("MAPPINGS CORRETTI:\n")
            for command, result in results.items():
                if "✅" in result:
                    channel, cc, desc = test_mappings[command]
                    f.write(f"  {command}: CH{channel} CC{cc} → {desc}\n")

            f.write("\nMAPPINGS DA CORREGGERE:\n")
            for command, issue in failed_mappings:
                channel, cc, desc = test_mappings[command]
                f.write(f"  {command}: CH{channel} CC{cc} → {desc}\n")
                f.write(f"    Problema: {issue}\n")

        print(f"\n💾 Report salvato in: {report_file}")

        # Disconnect
        controller.disconnect()
        print(f"\n✅ Verifica completata!")

        return len(failed_mappings) == 0

    except Exception as e:
        print(f"❌ Errore durante verifica mapping: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_traktor_mapping_guide():
    """Genera guida dettagliata per correggere mapping in Traktor"""
    print("\n🗺️ Guida Correzione Mapping Traktor")
    print("="*60)

    guide_content = """
# GUIDA CORREZIONE MAPPING TRAKTOR

## Setup Iniziale
1. Aprire Traktor Pro 3
2. Andare in Preferences (Ctrl+, oppure Traktor → Preferences)
3. Cliccare su "Controller Manager" nella sidebar sinistra
4. Cercare "DJ AI Controller" nella lista (Generic MIDI device)

## Se DJ AI Controller non esiste:
1. Cliccare "Add..." in basso a sinistra
2. Selezionare "Generic MIDI"
3. Impostare Nome: "DJ AI Controller"
4. In Port: Selezionare "IAC Driver Bus 1"
5. Out Port: Selezionare "IAC Driver Bus 1"

## Aggiungere/Correggere Mapping:

### TRANSPORT CONTROLS
- CH1 CC20 → Deck A → Play (Type: Button, Mode: Toggle)
- CH1 CC21 → Deck B → Play (Type: Button, Mode: Toggle)
- CH1 CC22 → Deck C → Play (Type: Button, Mode: Toggle)
- CH1 CC23 → Deck D → Play (Type: Button, Mode: Toggle)

- CH1 CC24 → Deck A → Cue (Type: Button, Mode: Hold)
- CH1 CC25 → Deck B → Cue (Type: Button, Mode: Hold)
- CH1 CC26 → Deck C → Cue (Type: Button, Mode: Hold)
- CH1 CC27 → Deck D → Cue (Type: Button, Mode: Hold)

### VOLUME CONTROLS
- CH1 CC28 → Deck A → Volume (Type: Fader, Mode: Direct)
- CH1 CC29 → Deck B → Volume (Type: Fader, Mode: Direct)
- CH1 CC30 → Deck C → Volume (Type: Fader, Mode: Direct)
- CH1 CC31 → Deck D → Volume (Type: Fader, Mode: Direct)

### CROSSFADER E MASTER
- CH1 CC32 → Mixer → Crossfader (Type: Fader, Mode: Direct)
- CH1 CC33 → Mixer → Main Volume (Type: Fader, Mode: Direct)

### EQ CONTROLS (Deck A)
- CH1 CC34 → Deck A → EQ High (Type: Fader, Mode: Direct)
- CH1 CC35 → Deck A → EQ Mid (Type: Fader, Mode: Direct)
- CH1 CC36 → Deck A → EQ Low (Type: Fader, Mode: Direct)

### BROWSER CONTROLS
- CH1 CC37 → Browser → List Up (Type: Button, Mode: Trigger)
- CH1 CC38 → Browser → List Down (Type: Button, Mode: Trigger)
- CH1 CC39 → Browser → Load → Deck A (Type: Button, Mode: Trigger)
- CH1 CC40 → Browser → Load → Deck B (Type: Button, Mode: Trigger)

### SYNC E PITCH
- CH1 CC41 → Deck A → Sync (Type: Button, Mode: Toggle)
- CH1 CC42 → Deck B → Sync (Type: Button, Mode: Toggle)
- CH1 CC43 → Deck A → Tempo (Type: Fader, Mode: Direct)
- CH1 CC44 → Deck B → Tempo (Type: Fader, Mode: Direct)

## IMPORTANTE:
- Type: Button per comandi on/off, Fader per controlli continui
- Mode: Toggle per play/sync, Hold per cue, Trigger per browser, Direct per fader
- Controllare che non ci siano conflitti con altri controller
- Salvare dopo ogni modifica
"""

    with open("traktor_mapping_guide.txt", 'w') as f:
        f.write(guide_content)

    print("💾 Guida salvata in: traktor_mapping_guide.txt")
    print("📖 Leggere questo file per istruzioni dettagliate!")

if __name__ == "__main__":
    print("🤖 DJ AI - MIDI Mapping Verification Tool")
    print("="*80)

    try:
        print("📋 CHECKLIST PRE-TEST:")
        print("1. Traktor Pro 3 è avviato?")
        print("2. IAC Driver Bus 1 è abilitato?")
        print("3. Hai accesso visivo a Traktor per monitorare i controlli?")
        print("4. Sei pronto a testare ogni comando uno per uno?")
        print()

        generate_traktor_mapping_guide()
        print()

        print("Premi Enter per iniziare la verifica mapping...")
        input()

        success = test_midi_mapping_verification()

        if success:
            print("\n🎉 TUTTI I MAPPING SONO CORRETTI!")
            print("Il sistema dovrebbe funzionare perfettamente.")
        else:
            print("\n⚠️ ALCUNI MAPPING NECESSITANO CORREZIONE")
            print("Consulta il report e la guida per correggere.")

    except KeyboardInterrupt:
        print("\n⚠️ Test interrotto dall'utente")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()