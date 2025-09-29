#!/usr/bin/env python3
"""
🔧 TSI Import Troubleshooter
Analizza i problemi di import TSI e crea versione corretta
"""

import xml.etree.ElementTree as ET
from pathlib import Path

def analyze_tsi_files():
    """Analizza i due file TSI per capire il problema"""

    print("🔍 ANALISI PROBLEMI IMPORT TSI")
    print("=" * 50)

    # File 1: AI_DJ_Corrected_Mapping.tsi (298 bytes)
    print("\n📁 File 1: AI_DJ_Corrected_Mapping.tsi (298 bytes)")
    print("   Risultato: Controller mapping acceso, rotellina infinita, crash")
    print("   Problema: Template minimo, dati binari non decodificabili")

    # File 2: AI_DJ_Perfect_Mapping.tsi (11,588 bytes)
    print("\n📁 File 2: AI_DJ_Perfect_Mapping.tsi (11,588 bytes)")
    print("   Risultato: Nessuna opzione accesa, import silenzioso")
    print("   Problema: Formato XML non compatibile con formato TSI binario")

    print("\n🎯 ROOT CAUSE:")
    print("   I file TSI di Traktor NON sono semplici XML!")
    print("   Sono file binari compressi con metadati specifici")
    print("   Il nostro generatore XML non è compatibile")

def create_working_solution():
    """Crea soluzione funzionante per l'import"""

    print("\n🔧 SOLUZIONE CORRETTA:")
    print("=" * 50)

    solution_steps = [
        "METODO 1: Setup Manuale (RACCOMANDATO)",
        "1. Traktor > Preferences > Controller Manager",
        "2. Add > Generic MIDI",
        "3. Device Name: 'AI DJ Controller'",
        "4. Device Setup:",
        "   - Input: IAC Driver Bus 1",
        "   - Output: IAC Driver Bus 1",
        "5. Add In... per ogni controllo uno per uno",
        "",
        "METODO 2: Modifica TSI esistente",
        "1. Esporta il tuo TSI attuale da Traktor",
        "2. Aggiungi manualmente i controlli mancanti",
        "3. Re-importa il TSI modificato",
        "",
        "METODO 3: Copia da controller esistente",
        "1. Cerca online TSI per controller MIDI generico",
        "2. Modifica i CC numbers per matchare i nostri",
        "3. Importa il TSI modificato"
    ]

    for step in solution_steps:
        print(f"   {step}")

def generate_manual_commands():
    """Genera comandi specifici per setup manuale"""

    print("\n🎛️ COMANDI ESSENZIALI DA AGGIUNGERE SUBITO:")
    print("=" * 50)

    essential_mappings = [
        ("Deck A Play", 1, 20, "Deck A > Play/Pause", "Button", "Toggle"),
        ("Deck B Play", 1, 21, "Deck B > Play/Pause", "Button", "Toggle"),
        ("Deck A Volume", 1, 28, "Deck A > Volume", "Fader", "Direct"),
        ("Deck B Volume", 1, 29, "Deck B > Volume", "Fader", "Direct"),
        ("Crossfader", 1, 32, "Mixer > Crossfader", "Fader", "Direct"),
        ("Browser Up", 1, 37, "Browser > List Scroll Up", "Button", "Inc"),
        ("Browser Down", 1, 38, "Browser > List Scroll Down", "Button", "Inc"),
        ("Load Deck A", 1, 39, "Deck A > Load Selected", "Button", "Trigger"),
        ("Load Deck B", 1, 40, "Deck B > Load Selected", "Button", "Trigger"),
    ]

    print("Per ogni controllo, in Traktor Controller Manager:")
    print("Add In... e configura:")
    print()

    for i, (name, channel, cc, function, ctrl_type, mode) in enumerate(essential_mappings, 1):
        print(f"{i}. {name}:")
        print(f"   Device: Generic MIDI")
        print(f"   Channel: {channel}")
        print(f"   Control: CC")
        print(f"   No.: {cc}")
        print(f"   Assignment: {function}")
        print(f"   Type of Controller: {ctrl_type}")
        print(f"   Interaction Mode: {mode}")
        print()

def create_test_script():
    """Crea script di test immediato"""

    test_code = '''#!/usr/bin/env python3
"""
🧪 Test Immediato Import TSI
Testa se i controlli base funzionano dopo setup manuale
"""

import mido
import time

def test_essential_controls():
    """Testa solo i controlli essenziali"""

    print("🎯 Test Controlli Essenziali Post-Setup")
    print("=" * 40)

    try:
        output = mido.open_output('Bus 1')
        print("✅ Connesso a IAC Driver Bus 1")
    except:
        print("❌ IAC Driver non disponibile")
        return False

    # Test controlli uno per uno
    tests = [
        ("Play Deck A", 1, 20, "Deve far partire/fermare Deck A"),
        ("Play Deck B", 1, 21, "Deve far partire/fermare Deck B"),
        ("Browser Up", 1, 37, "Deve scrollare browser su"),
        ("Load Deck A", 1, 39, "Deve caricare traccia selezionata in Deck A"),
    ]

    print("\\nInvia comandi di test...")

    for name, channel, cc, expected in tests:
        print(f"\\n🎛️ {name} (CC{cc}): {expected}")

        msg = mido.Message('control_change',
                          channel=channel-1,
                          control=cc,
                          value=127)
        output.send(msg)

        result = input("   Funziona? (y/n): ").lower()

        if result == 'y':
            print("   ✅ OK")
        else:
            print("   ❌ NON funziona - controlla mapping in Traktor")

        time.sleep(0.5)

    output.close()
    print("\\n🎯 Test completato!")

if __name__ == "__main__":
    test_essential_controls()
'''

    with open("test_manual_setup.py", "w") as f:
        f.write(test_code)

    print(f"\n🧪 Script di test creato: test_manual_setup.py")
    print("   Usa questo dopo il setup manuale per verificare")

def main():
    """Main function"""

    analyze_tsi_files()
    create_working_solution()
    generate_manual_commands()
    create_test_script()

    print("\n" + "=" * 60)
    print("🎯 RACCOMANDAZIONE FINALE:")
    print("=" * 60)
    print("1. ❌ NON usare i file TSI generati (non funzionano)")
    print("2. ✅ Fai setup MANUALE in Traktor Controller Manager")
    print("3. ✅ Usa la lista comandi sopra uno per uno")
    print("4. ✅ Testa con: python test_manual_setup.py")
    print("5. ✅ Una volta funzionante, esporta TSI da Traktor per backup")
    print()
    print("💡 Il setup manuale è più affidabile dell'import automatico!")

if __name__ == "__main__":
    main()