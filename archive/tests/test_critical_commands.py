#!/usr/bin/env python3
"""
🔥 Critical MIDI Command Tester
Tests the most important commands that MUST work for basic DJ operation
"""

import time
import sys
from traktor_control import TraktorController
from config import DJConfig

def test_critical_commands():
    """Test critical commands and report results"""

    # Connect to Traktor
    config = DJConfig()
    traktor = TraktorController(config)

    print("🔌 Connecting to Traktor...")
    if not traktor.connect_with_gil_safety(output_only=True):
        print("❌ Connection failed!")
        return False

    print("✅ Connected to Traktor MIDI\n")

    # Critical commands to test
    critical_commands = [
        ('deck_a_play', 'Play/Pause Deck A - Should toggle play state'),
        ('deck_b_play', 'Play/Pause Deck B - Should toggle play state'),
        ('deck_a_cue', 'Cue Deck A - Should flash/blink cue button'),
        ('deck_b_cue', 'Cue Deck B - Should flash/blink cue button'),
        ('deck_a_volume', 'Deck A Volume - Should move volume fader'),
        ('deck_b_volume', 'Deck B Volume - Should move volume fader'),
        ('crossfader', 'Crossfader - Should move crossfader left/center/right'),
        ('master_volume', 'Master Volume - Should change master output level'),
        ('browser_load_deck_a', 'Load Track to Deck A - Should load selected track'),
        ('browser_load_deck_b', 'Load Track to Deck B - Should load selected track')
    ]

    print("🔥 TESTING CRITICAL COMMANDS")
    print("=" * 60)
    print("⚠️ IMPORTANT: Watch Traktor and observe what happens!")
    print("=" * 60)

    results = []

    for cmd_name, description in critical_commands:
        if cmd_name not in traktor.MIDI_MAP:
            print(f"❌ {cmd_name} not found in MIDI_MAP")
            continue

        channel, cc = traktor.MIDI_MAP[cmd_name]

        print(f"\n🧪 TESTING: {cmd_name}")
        print(f"📝 Expected: {description}")
        print(f"📡 MIDI: Channel {channel}, CC {cc}")
        print("─" * 60)

        # Send test command
        try:
            if 'volume' in cmd_name or 'crossfader' in cmd_name:
                # Test volume/fader commands with sequence
                print("📡 Sending volume test sequence...")
                values = [0, 64, 127, 64]  # min, mid, max, back to mid
                for i, value in enumerate(values):
                    traktor.midi_out.send_message([0xB0 + (channel - 1), cc, value])
                    print(f"   CC {cc} = {value} ({'min' if value == 0 else 'mid' if value == 64 else 'max'})")
                    time.sleep(0.8)
            else:
                # Test trigger commands
                print(f"📡 Sending trigger command...")
                traktor.midi_out.send_message([0xB0 + (channel - 1), cc, 127])
                print(f"   CC {cc} = 127 (trigger)")
                time.sleep(1.5)

            print(f"✅ MIDI command sent successfully")
            results.append((cmd_name, cc, "SENT", description))

        except Exception as e:
            print(f"❌ Error sending MIDI: {e}")
            results.append((cmd_name, cc, "ERROR", str(e)))

    # Summary
    print("\n" + "=" * 60)
    print("📊 CRITICAL COMMAND TEST SUMMARY")
    print("=" * 60)
    print(f"Total tested: {len(results)}")

    for cmd_name, cc, status, info in results:
        status_icon = "✅" if status == "SENT" else "❌"
        print(f"{status_icon} CC {cc:3d}: {cmd_name}")

    print("\n" + "=" * 60)
    print("❓ HUMAN VERIFICATION REQUIRED")
    print("=" * 60)
    print("Please observe Traktor and verify which commands worked:")
    print()

    for cmd_name, cc, status, description in results:
        if status == "SENT":
            print(f"CC {cc}: {cmd_name}")
            print(f"   Expected: {description}")
            print()

    print("💡 Next steps:")
    print("   1. Note which CCs worked correctly")
    print("   2. For failed commands, use Traktor's MIDI learn mode")
    print("   3. Run test_important_commands.py for the next priority group")

    traktor.disconnect()
    return True

if __name__ == "__main__":
    test_critical_commands()