#!/usr/bin/env python3
"""
SYSTEMATIC BROWSER NAVIGATION TEST
==================================
Continue testing from Labels position to find Broken Beat folder.
Using confirmed working settings with automated step-by-step testing.
"""

import time
import rtmidi

def connect_midi():
    """Connect to Driver IAC Bus 1."""
    try:
        midi_out = rtmidi.MidiOut()
        ports = midi_out.get_ports()

        target_port = None
        for i, port in enumerate(ports):
            if "Driver IAC Bus 1" in port:
                target_port = i
                break

        if target_port is None:
            print("❌ Driver IAC Bus 1 not found!")
            print("🔍 Available ports:")
            for i, port in enumerate(ports):
                print(f"  {i}: {port}")
            return None

        midi_out.open_port(target_port)
        print(f"✅ Connected to: {ports[target_port]}")
        return midi_out

    except Exception as e:
        print(f"❌ MIDI connection error: {e}")
        return None

def send_midi_cc(midi_out, channel, cc, value):
    """Send MIDI CC command."""
    try:
        status = 176 + (channel - 1)  # Control Change
        message = [status, cc, value]
        midi_out.send_message(message)
        print(f"📤 MIDI sent: Channel {channel}, CC {cc}, Value {value}")
        return True
    except Exception as e:
        print(f"❌ MIDI send error: {e}")
        return False

def main():
    """Execute systematic browser navigation test."""

    print("🎛️ SYSTEMATIC BROWSER NAVIGATION TEST")
    print("=" * 50)
    print("📍 Status: Continuing from Labels position")
    print("🎯 Goal: Find 'Broken Beat' folder systematically")
    print("⚙️ Using confirmed working settings:")
    print("   - Tree navigation: CC 72 (63=down, 65=up)")
    print("   - Folder expand: CC 64 (value 127)")
    print("   - List navigation: CC 74/92")
    print("   - Track load: CC 21")
    print("=" * 50)

    midi_out = connect_midi()
    if not midi_out:
        return

    try:
        # Test sequence to find Broken Beat folder
        test_steps = [
            {
                'step': 1,
                'action': 'Check current position after Labels navigation',
                'description': 'User should verify current browser position',
                'midi_command': None
            },
            {
                'step': 2,
                'action': 'Navigate DOWN to next tree item',
                'description': 'Move down from current position to find Broken Beat',
                'midi_command': {'channel': 1, 'cc': 72, 'value': 63}
            },
            {
                'step': 3,
                'action': 'Continue DOWN navigation if needed',
                'description': 'Keep moving down until Broken Beat is found',
                'midi_command': {'channel': 1, 'cc': 72, 'value': 63}
            },
            {
                'step': 4,
                'action': 'Expand Broken Beat folder',
                'description': 'Once Broken Beat is selected, expand it',
                'midi_command': {'channel': 1, 'cc': 64, 'value': 127}
            },
            {
                'step': 5,
                'action': 'Navigate down in track list',
                'description': 'Move down in the track list within Broken Beat',
                'midi_command': {'channel': 1, 'cc': 74, 'value': 127}
            },
            {
                'step': 6,
                'action': 'Navigate up in track list',
                'description': 'Move up in the track list to test bidirectional movement',
                'midi_command': {'channel': 1, 'cc': 92, 'value': 127}
            },
            {
                'step': 7,
                'action': 'Load selected track to Deck A',
                'description': 'Load the currently selected track without playing',
                'midi_command': {'channel': 1, 'cc': 21, 'value': 127}
            }
        ]

        for step_info in test_steps:
            print(f"\n🧪 STEP {step_info['step']}: {step_info['action']}")
            print(f"📝 Expected: {step_info['description']}")

            if step_info['midi_command'] is None:
                print("👀 MANUAL CHECK REQUIRED")
                print("Please check Traktor browser and report current position.")
                print("Are you positioned at a folder that might contain 'Broken Beat'?")
            else:
                cmd = step_info['midi_command']
                success = send_midi_cc(midi_out, cmd['channel'], cmd['cc'], cmd['value'])

                if success:
                    print("✅ MIDI command sent successfully")

                    # Specific verification messages for each step
                    if step_info['step'] == 2:
                        print("👀 VERIFICATION NEEDED: Did the selection move down? What folder/item is now selected?")
                        print("   Looking for: 'Broken Beat' folder in the tree")
                    elif step_info['step'] == 3:
                        print("👀 VERIFICATION NEEDED: Continue until 'Broken Beat' folder is found and selected")
                    elif step_info['step'] == 4:
                        print("👀 VERIFICATION NEEDED: Did 'Broken Beat' folder expand? Do you see track list inside?")
                    elif step_info['step'] == 5:
                        print("👀 VERIFICATION NEEDED: Did selection move down in the track list?")
                    elif step_info['step'] == 6:
                        print("👀 VERIFICATION NEEDED: Did selection move up in the track list?")
                    elif step_info['step'] == 7:
                        print("👀 VERIFICATION NEEDED: Did the track load to Deck A? (Should NOT start playing)")
                        print("   Check: Deck A should show the loaded track but remain paused")
                else:
                    print("❌ Failed to send MIDI command")

            # Brief pause between steps
            time.sleep(2)
            print("─" * 40)

        print("\n📊 TEST SEQUENCE COMPLETED")
        print("=" * 50)
        print("🎯 MANUAL VERIFICATION REQUIRED:")
        print("1. Are you now positioned in the 'Broken Beat' folder?")
        print("2. Can you navigate up/down in the track list?")
        print("3. Did track loading to Deck A work correctly?")
        print("4. Does the track remain paused after loading?")
        print("=" * 50)

    finally:
        if midi_out:
            midi_out.close_port()
            print("\n🔌 MIDI connection closed")

if __name__ == "__main__":
    main()