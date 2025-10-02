#!/usr/bin/env python3
"""
🔧 Debug Deck Mapping

Diagnostico specifico per verificare se i comandi ai deck
vengono inviati correttamente e perché il Deck A va al Deck B
"""

import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from traktor_control import TraktorController, DeckID

def test_deck_commands():
    """Test diretto dei comandi ai deck"""
    print("🔧 DEBUG: Deck Command Mapping")
    print("=" * 50)

    # Inizializza controller
    from config import get_config
    config = get_config()
    traktor = TraktorController(config)

    print(f"✅ Traktor connected: {traktor.connected}")

    # Test MIDI channels e note numbers
    print(f"\n📡 MIDI Configuration:")
    print(f"   Channel: {traktor.midi_channel}")
    print(f"   Device: {traktor.device_name}")

    # Test stato iniziale
    print(f"\n📊 Initial Status:")
    initial_status = traktor.get_status()
    if initial_status:
        for key, value in initial_status.items():
            print(f"   {key}: {value}")
    else:
        print("   ⚠️ No status received")

    # Test specifico comandi deck
    print(f"\n🎯 Testing Deck Commands:")

    # Test 1: Play Deck A
    print(f"\n1️⃣ Testing PLAY DECK A...")
    print(f"   Command: play_deck(DeckID.A)")
    print(f"   Expected: Deck A should start playing")

    result = traktor.play_deck(DeckID.A)
    print(f"   Result: {result}")

    time.sleep(2.0)  # Attendi esecuzione

    # Verifica stato
    status_after_a = traktor.get_status()
    if status_after_a:
        print(f"   Status after:")
        print(f"     Deck A playing: {status_after_a.get('deck_a_playing', 'unknown')}")
        print(f"     Deck B playing: {status_after_a.get('deck_b_playing', 'unknown')}")
        print(f"     Deck A BPM: {status_after_a.get('deck_a_bpm', 0)}")
        print(f"     Deck B BPM: {status_after_a.get('deck_b_bpm', 0)}")

    # Test 2: Play Deck B
    print(f"\n2️⃣ Testing PLAY DECK B...")
    print(f"   Command: play_deck(DeckID.B)")
    print(f"   Expected: Deck B should start playing")

    result = traktor.play_deck(DeckID.B)
    print(f"   Result: {result}")

    time.sleep(2.0)  # Attendi esecuzione

    # Verifica stato
    status_after_b = traktor.get_status()
    if status_after_b:
        print(f"   Status after:")
        print(f"     Deck A playing: {status_after_b.get('deck_a_playing', 'unknown')}")
        print(f"     Deck B playing: {status_after_b.get('deck_b_playing', 'unknown')}")
        print(f"     Deck A BPM: {status_after_b.get('deck_a_bpm', 0)}")
        print(f"     Deck B BPM: {status_after_b.get('deck_b_bpm', 0)}")

    # Test 3: Stop All
    print(f"\n3️⃣ Testing STOP ALL...")
    traktor.stop_deck(DeckID.A)
    traktor.stop_deck(DeckID.B)

    time.sleep(2.0)

    final_status = traktor.get_status()
    if final_status:
        print(f"   Final status:")
        print(f"     Deck A playing: {final_status.get('deck_a_playing', 'unknown')}")
        print(f"     Deck B playing: {final_status.get('deck_b_playing', 'unknown')}")

def debug_midi_mapping():
    """Debug specifico della mappatura MIDI"""
    print(f"\n🎹 DEBUG: MIDI Mapping Details")
    print("=" * 50)

    from config import get_config
    config = get_config()
    traktor = TraktorController(config)

    # Controlla mapping interno
    print(f"📋 Internal Mapping:")

    # Accedi alle note MIDI interne (se disponibili)
    if hasattr(traktor, 'DECK_A_PLAY_NOTE'):
        print(f"   Deck A Play Note: {traktor.DECK_A_PLAY_NOTE}")
    if hasattr(traktor, 'DECK_B_PLAY_NOTE'):
        print(f"   Deck B Play Note: {traktor.DECK_B_PLAY_NOTE}")

    # Test raw MIDI send
    print(f"\n🎵 Testing Raw MIDI Commands:")

    try:
        # Se ha accesso diretto al MIDI out
        if hasattr(traktor, 'midi_out') and traktor.midi_out:
            print(f"   MIDI Out available: {traktor.midi_out}")

            # Test note dirette
            print(f"   Sending raw MIDI note 0x90 (Note On) to channel 0...")
            # Note: questo dipende dall'implementazione interna

    except Exception as e:
        print(f"   ⚠️ Raw MIDI test failed: {e}")

def analyze_traktor_mapping_file():
    """Analizza il file di mapping di Traktor se disponibile"""
    print(f"\n📄 ANALYZE: Traktor Mapping File")
    print("=" * 50)

    # Percorsi comuni file mapping Traktor
    possible_paths = [
        Path.cwd() / "traktor" / "AI_DJ_Complete.tsi",
        Path.cwd() / "AI_DJ_Complete.tsi",
        Path.home() / "Documents" / "Native Instruments" / "Traktor Pro 3" / "Settings" / "AI_DJ_Complete.tsi"
    ]

    mapping_found = False

    for path in possible_paths:
        if path.exists():
            print(f"✅ Found mapping file: {path}")
            mapping_found = True

            # Analisi basic del file (è XML)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # primi 1000 caratteri
                    print(f"   File preview:")
                    print(f"   {content[:200]}...")

                    # Cerca pattern specifici
                    if "DECK_A" in content or "Deck A" in content:
                        print(f"   ✅ Contains Deck A references")
                    if "DECK_B" in content or "Deck B" in content:
                        print(f"   ✅ Contains Deck B references")

            except Exception as e:
                print(f"   ⚠️ Could not read mapping file: {e}")
            break

    if not mapping_found:
        print(f"❌ No Traktor mapping file found in common locations")
        print(f"   Expected locations:")
        for path in possible_paths:
            print(f"     - {path}")
        print(f"   📝 Action needed: Import AI_DJ_Complete.tsi in Traktor")

def test_deck_feedback():
    """Test feedback dai deck per vedere quale risponde"""
    print(f"\n📡 TEST: Deck Feedback Analysis")
    print("=" * 50)

    from config import get_config
    config = get_config()
    traktor = TraktorController(config)

    # Status prima di qualsiasi comando
    print(f"1️⃣ Status before any commands:")
    initial = traktor.get_status()
    print(f"   {initial}")

    # Comando a Deck A
    print(f"\n2️⃣ Sending command to Deck A...")
    traktor.play_deck(DeckID.A)
    time.sleep(1.5)

    after_a = traktor.get_status()
    print(f"   Status after Deck A command:")
    print(f"   {after_a}")

    # Confronta cambiamenti
    if initial and after_a:
        changes = []
        for key in after_a.keys():
            if key in initial and initial[key] != after_a[key]:
                changes.append(f"{key}: {initial[key]} → {after_a[key]}")

        if changes:
            print(f"   🔍 Changes detected:")
            for change in changes:
                print(f"     - {change}")
        else:
            print(f"   ⚠️ No changes detected - command may not be working")

    # Stop per reset
    traktor.stop_deck(DeckID.A)
    traktor.stop_deck(DeckID.B)
    time.sleep(1.0)

def run_complete_debug():
    """Esegue debug completo del mapping deck"""
    print("🔧 COMPLETE DECK MAPPING DEBUG")
    print("=" * 60)

    # Test 1: Comandi base
    test_deck_commands()

    # Test 2: Mapping MIDI
    debug_midi_mapping()

    # Test 3: File mapping
    analyze_traktor_mapping_file()

    # Test 4: Feedback analysis
    test_deck_feedback()

    print(f"\n" + "=" * 60)
    print("📊 DEBUG SUMMARY & RECOMMENDATIONS")
    print("=" * 60)

    print(f"🔍 POSSIBLE CAUSES:")
    print(f"   1. MIDI mapping file not loaded in Traktor")
    print(f"   2. Deck A and Deck B note numbers swapped in mapping")
    print(f"   3. MIDI channel configuration mismatch")
    print(f"   4. IAC Driver channel assignment incorrect")
    print(f"   5. Traktor deck assignment in Controller Manager wrong")

    print(f"\n🛠️ IMMEDIATE ACTIONS:")
    print(f"   1. Verify AI_DJ_Complete.tsi is imported in Traktor")
    print(f"   2. Check Controller Manager → Deck Assignment")
    print(f"   3. Verify IAC Driver Bus 1 is selected in Traktor")
    print(f"   4. Test manual MIDI commands in Traktor's MIDI Learn mode")
    print(f"   5. Check if deck assignment is swapped in mapping file")

    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Run this debug again after checking mapping")
    print(f"   2. Use visual_feedback_agent.py for real-time verification")
    print(f"   3. Test with single deck commands to isolate issue")

if __name__ == "__main__":
    run_complete_debug()