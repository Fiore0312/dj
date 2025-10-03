#!/usr/bin/env python3
"""
🎯 DECK B CUE DISCOVERY - CC 81 TEST
Targeted test for discovering Deck B Cue command
"""

import time
import sys
from traktor_control import TraktorController, MIDIChannel
from config import DJConfig

def test_cc_81_deck_b_cue():
    """Test CC 81 specifically for Deck B Cue discovery"""

    print("🎯 DECK B CUE DISCOVERY - CC 81 TEST")
    print("=" * 60)
    print("STATUS: Testing logical sequence CC 80 (Deck A) → CC 81 (Deck B)")
    print("OBJECTIVE: Discover if CC 81 controls Deck B Cue")
    print("=" * 60)

    # Initialize controller
    config = DJConfig()
    traktor = TraktorController(config)

    # Connect to Traktor
    print("\n🔌 Connecting to Traktor via IAC Driver...")
    if not traktor.connect_with_gil_safety(output_only=True):
        print("❌ Failed to connect to Traktor MIDI")
        print("💡 Make sure:")
        print("   - Traktor Pro 3 is running")
        print("   - IAC Driver Bus 1 is enabled")
        print("   - MIDI is configured in Traktor")
        return False

    print("✅ Connected to Traktor!")
    print("\n🚨 IMPORTANT: Make sure Traktor learn mode is ACTIVE for Deck B Cue!")
    print("👀 Watch Traktor carefully during this test...")

    print("\n⏰ Starting CC 81 test in 3 seconds...")
    time.sleep(1)
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")

    try:
        print("\n🎯 TESTING CC 81 FOR DECK B CUE")
        print("=" * 40)

        # Test sequence 1: CC 81 = 127 (ON)
        print("📡 Sending CC 81 = 127 (ON command)")
        traktor.midi_out.send_message([0xB0, 81, 127])  # Channel 1, CC 81, Value 127
        print("✅ CC 81 ON sent")

        time.sleep(2)  # Wait for Traktor to register

        # Test sequence 2: CC 81 = 0 (OFF)
        print("📡 Sending CC 81 = 0 (OFF command)")
        traktor.midi_out.send_message([0xB0, 81, 0])    # Channel 1, CC 81, Value 0
        print("✅ CC 81 OFF sent")

        time.sleep(1)

        # Test sequence 3: CC 81 = 127 again (to confirm)
        print("📡 Sending CC 81 = 127 (confirmation)")
        traktor.midi_out.send_message([0xB0, 81, 127])
        print("✅ CC 81 confirmation sent")

        print("\n" + "=" * 60)
        print("🔍 CC 81 TEST COMPLETED")
        print("=" * 60)

        print("\n❓ CRITICAL QUESTIONS:")
        print("   1. Did you see Traktor's learn mode activate?")
        print("   2. Did learn mode show 'CC 81' or similar?")
        print("   3. Did the learn dialog close/complete?")
        print("   4. Is Deck B Cue now mapped to CC 81?")

        print("\n📋 EXPECTED RESULTS:")
        print("   ✅ Learn mode captures CC 81")
        print("   ✅ Dialog shows successful mapping")
        print("   ✅ Deck B Cue responds to CC 81")

        print("\n📊 DISCOVERY STATUS:")
        print("   🔍 CC 80 = Deck A Cue (confirmed)")
        print("   🔍 CC 81 = Deck B Cue (testing now)")

        return True

    except Exception as e:
        print(f"\n❌ ERROR during CC 81 test: {e}")
        return False

    finally:
        # Cleanup
        traktor.disconnect()
        print("\n🧹 MIDI connection closed")

def test_cc_82_backup():
    """Backup test for CC 82 if CC 81 fails"""

    print("\n🔄 BACKUP TEST: CC 82 FOR DECK B CUE")
    print("=" * 50)
    print("Running backup test in case CC 81 didn't work...")

    config = DJConfig()
    traktor = TraktorController(config)

    if not traktor.connect_with_gil_safety(output_only=True):
        print("❌ Connection failed for backup test")
        return False

    try:
        print("\n📡 Testing CC 82...")

        # Test CC 82 = 127
        traktor.midi_out.send_message([0xB0, 82, 127])
        print("✅ CC 82 = 127 sent")
        time.sleep(2)

        # Test CC 82 = 0
        traktor.midi_out.send_message([0xB0, 82, 0])
        print("✅ CC 82 = 0 sent")

        print("\n❓ Did CC 82 work for Deck B Cue?")

        return True

    except Exception as e:
        print(f"❌ CC 82 test failed: {e}")
        return False

    finally:
        traktor.disconnect()

if __name__ == "__main__":
    print("🎯 DECK B CUE DISCOVERY TOOL")
    print("Testing CC 81 first, then CC 82 as backup")
    print("")

    try:
        # Test CC 81 first
        success = test_cc_81_deck_b_cue()

        if success:
            print("\n✅ CC 81 test completed successfully!")
            print("📋 Please verify in Traktor if CC 81 was learned.")

            # Ask if we should also test CC 82
            print("\n💡 Would you like to also test CC 82 as confirmation?")
            print("   This can help verify the sequence pattern.")

        else:
            print("\n⚠️ CC 81 test had issues. Consider manual verification.")

    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n👋 Discovery test completed")
    print("🔍 Next steps: Verify the mapping in Traktor and test functionality")