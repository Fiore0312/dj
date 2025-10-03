#!/usr/bin/env python3
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

    print("\nInvia comandi di test...")

    for name, channel, cc, expected in tests:
        print(f"\n🎛️ {name} (CC{cc}): {expected}")

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
    print("\n🎯 Test completato!")

if __name__ == "__main__":
    test_essential_controls()
