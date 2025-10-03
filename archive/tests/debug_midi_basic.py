#!/usr/bin/env python3
"""
🔍 DECK B CUE DISCOVERY - CC 81 TEST
Test specifico per scoprire il comando corretto per Deck B Cue
"""

import time
import sys
import platform

def test_deck_b_cue_discovery():
    """Test CC 81 per Deck B Cue discovery"""

    print("🎯 DECK B CUE DISCOVERY - CC 81 TEST")
    print("=" * 60)
    print("CURRENT STATUS: Learn mode READY for Deck B Cue")
    print("STRATEGY: Testing CC 81 (logical sequence after CC 80 = Deck A Cue)")
    print("=" * 60)

    # Step 1: Import and setup
    print("\n🧪 STEP 1: Setup MIDI for CC 81 discovery")
    try:
        import rtmidi
        print("✅ rtmidi ready")
    except ImportError as e:
        print(f"❌ ERRORE import rtmidi: {e}")
        return False

    # Step 2: Trova IAC Driver Bus 1
    print("\n🧪 STEP 2: Cerca IAC Driver Bus 1 per discovery")
    try:
        midi_out = rtmidi.MidiOut()
        output_ports = midi_out.get_ports()

        # Cerca IAC Driver Bus 1
        iac_port = None
        for i, port in enumerate(output_ports):
            if 'iac driver bus 1' in port.lower():
                iac_port = i
                print(f"✅ IAC Driver Bus 1 trovato: {port}")
                break

        if iac_port is None:
            print("❌ IAC Driver Bus 1 non trovato!")
            print("💡 Verifica che IAC Driver sia abilitato in Audio MIDI Setup")
            return False

    except Exception as e:
        print(f"❌ ERRORE ricerca IAC: {e}")
        return False

    # Step 3: Connessione a IAC Driver
    print("\n🧪 STEP 3: Connessione a IAC Driver Bus 1")
    try:
        midi_connection = rtmidi.MidiOut()
        midi_connection.open_port(iac_port)
        print("✅ Connesso a IAC Driver Bus 1 per discovery")

    except Exception as e:
        print(f"❌ ERRORE connessione IAC: {e}")
        return False

    # Step 4: CC 81 DISCOVERY TEST
    print("\n🧪 STEP 4: CC 81 DISCOVERY TEST FOR DECK B CUE")
    print("\n🚨 ATTENTION: Make sure Traktor learn mode is ACTIVE for Deck B Cue!")
    print("👀 Ready to test CC 81...")

    input("\n▶️ Press ENTER when learn mode is ready and you're watching Traktor...")

    try:
        # Test CC 81 = 127 (Deck B Cue ON)
        cc_81_on = [0xB0, 81, 127]  # Channel 1, CC 81, Value 127

        print("\n🎯 TESTING CC 81 FOR DECK B CUE")
        print(f"   Sending: {cc_81_on}")
        print(f"   Command: CC 81 = 127 on Channel 1")

        midi_connection.send_message(cc_81_on)
        print("✅ CC 81 command sent!")

        print("\n⏰ Waiting 2 seconds for Traktor to register...")
        time.sleep(2)

        # Send OFF command
        cc_81_off = [0xB0, 81, 0]  # CC 81 = 0
        print("\n📴 Sending CC 81 OFF command...")
        midi_connection.send_message(cc_81_off)
        print("✅ CC 81 OFF sent")

    except Exception as e:
        print(f"❌ ERRORE sending CC 81: {e}")
        return False

    # Step 5: Verifica con utente
    print("\n🧪 STEP 5: USER VERIFICATION")
    print("=" * 50)
    print("❓ CRITICAL QUESTION:")
    print("   Did you see Traktor's learn mode register CC 81?")
    print("   Did the learn mode capture the command?")
    print("\n🔍 EXPECTED BEHAVIOR:")
    print("   - Learn mode should show 'CC 81' or similar")
    print("   - Dialog should close or show 'learned'")
    print("   - Deck B Cue should now be mapped to CC 81")

    response = input("\n✅ Did CC 81 work? (y/n/maybe): ").lower().strip()

    if response in ['y', 'yes']:
        print("\n🎉 SUCCESS! CC 81 = Deck B Cue DISCOVERED!")
        print("📝 ADDING TO MAPPING DATABASE:")
        print("   ✅ CC 81 = Deck B Cue (Channel 1)")
        print("\n🔄 UPDATED SEQUENCE:")
        print("   CC 60 = Volume Deck B")
        print("   CC 80 = Deck A Cue")
        print("   CC 81 = Deck B Cue ← NEW DISCOVERY!")
        return True

    elif response in ['n', 'no']:
        print("\n❌ CC 81 failed. Moving to CC 82...")
        print("💡 NEXT STRATEGY: Test CC 82")
        return test_cc_82(midi_connection)

    else:
        print("\n🤔 Uncertain response. Let's try CC 82 to be sure...")
        return test_cc_82(midi_connection)

def test_cc_82(midi_connection):
    """Test CC 82 as backup for Deck B Cue"""
    print("\n🎯 TESTING CC 82 FOR DECK B CUE (BACKUP)")
    print("🚨 Make sure learn mode is still active!")

    input("\n▶️ Press ENTER when ready for CC 82 test...")

    try:
        # Test CC 82 = 127
        cc_82_on = [0xB0, 82, 127]
        print(f"\n📤 Sending CC 82: {cc_82_on}")
        midi_connection.send_message(cc_82_on)
        print("✅ CC 82 sent!")

        time.sleep(2)

        # OFF command
        cc_82_off = [0xB0, 82, 0]
        midi_connection.send_message(cc_82_off)
        print("📴 CC 82 OFF sent")

        response = input("\n✅ Did CC 82 work? (y/n): ").lower().strip()

        if response in ['y', 'yes']:
            print("\n🎉 SUCCESS! CC 82 = Deck B Cue DISCOVERED!")
            return True
        else:
            print("\n❌ CC 82 also failed. Need to try CC 83-85 range...")
            return False

    except Exception as e:
        print(f"❌ Error testing CC 82: {e}")
        return False

    # Cleanup
    print("\n🧹 Cleanup...")
    try:
        midi_connection.close()
        print("✅ MIDI connection closed")
    except:
        pass

    print("\n" + "=" * 60)
    print("🏁 CC 81 DISCOVERY COMPLETE")
    print("=" * 60)

    return True

if __name__ == "__main__":
    print("🎯 DECK B CUE DISCOVERY - CC 81 TEST")
    print("Testing logical sequence: CC 80 (Deck A) → CC 81 (Deck B)")
    print("")

    try:
        success = test_deck_b_cue_discovery()
        if success:
            print("\n🎉 DISCOVERY SUCCESSFUL!")
        else:
            print("\n⚠️ Discovery needs continuation with higher CC numbers")
    except Exception as e:
        print(f"\n❌ ERRORE FATALE: {e}")
        import traceback
        traceback.print_exc()

    print("\n👋 Discovery test completed")