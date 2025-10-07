#!/usr/bin/env python3
"""
CONTINUE BROWSER NAVIGATION TEST
================================
Continue testing from Labels position to find Broken Beat folder.
Using confirmed working settings:
- Tree navigation: CC 72 (value 63=down, value 65=up)
- List navigation: CC 74/92
- Folder expand: CC 64
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
        return True
    except Exception as e:
        print(f"❌ MIDI send error: {e}")
        return False

def test_navigation_step():
    """Test next navigation step from Labels position."""

    print("🎛️ CONTINUING BROWSER NAVIGATION TEST")
    print("=" * 50)
    print("📍 Current Status: Just navigated down from Labels position")
    print("🎯 Goal: Find 'Broken Beat' folder and test expansion/track loading")
    print("=" * 50)

    midi_out = connect_midi()
    if not midi_out:
        return

    try:
        while True:
            print("\n📍 NAVIGATION OPTIONS:")
            print("1. Test current position (where are we now?)")
            print("2. Navigate DOWN (CC 72, value 63)")
            print("3. Navigate UP (CC 72, value 65)")
            print("4. Expand folder (CC 64, value 127)")
            print("5. List navigation DOWN (CC 74, value 127)")
            print("6. List navigation UP (CC 92, value 127)")
            print("7. Load track to Deck A (when track selected)")
            print("0. Exit")

            choice = input("\nSelect option: ").strip()

            if choice == "1":
                print("👀 Please check Traktor browser and report current position")
                input("Press Enter when you've noted the current position...")

            elif choice == "2":
                print("📤 Sending: Tree Navigation DOWN (CC 72, value 63)")
                success = send_midi_cc(midi_out, 1, 72, 63)
                if success:
                    print("✅ Command sent successfully")
                    print("👀 Did the selection move down in the tree? What's now selected?")
                else:
                    print("❌ Failed to send command")
                input("Press Enter after checking Traktor...")

            elif choice == "3":
                print("📤 Sending: Tree Navigation UP (CC 72, value 65)")
                success = send_midi_cc(midi_out, 1, 72, 65)
                if success:
                    print("✅ Command sent successfully")
                    print("👀 Did the selection move up in the tree? What's now selected?")
                else:
                    print("❌ Failed to send command")
                input("Press Enter after checking Traktor...")

            elif choice == "4":
                print("📤 Sending: Folder Expand (CC 64, value 127)")
                success = send_midi_cc(midi_out, 1, 64, 127)
                if success:
                    print("✅ Command sent successfully")
                    print("👀 Did the selected folder expand? Do you see its contents?")
                else:
                    print("❌ Failed to send command")
                input("Press Enter after checking Traktor...")

            elif choice == "5":
                print("📤 Sending: List Navigation DOWN (CC 74, value 127)")
                success = send_midi_cc(midi_out, 1, 74, 127)
                if success:
                    print("✅ Command sent successfully")
                    print("👀 Did the selection move down in the list? What's now selected?")
                else:
                    print("❌ Failed to send command")
                input("Press Enter after checking Traktor...")

            elif choice == "6":
                print("📤 Sending: List Navigation UP (CC 92, value 127)")
                success = send_midi_cc(midi_out, 1, 92, 127)
                if success:
                    print("✅ Command sent successfully")
                    print("👀 Did the selection move up in the list? What's now selected?")
                else:
                    print("❌ Failed to send command")
                input("Press Enter after checking Traktor...")

            elif choice == "7":
                print("📤 Sending: Load track to Deck A (CC 21, value 127)")
                success = send_midi_cc(midi_out, 1, 21, 127)
                if success:
                    print("✅ Command sent successfully")
                    print("👀 Did the selected track load to Deck A? (Should NOT start playing)")
                else:
                    print("❌ Failed to send command")
                input("Press Enter after checking Traktor...")

            elif choice == "0":
                break

            else:
                print("❌ Invalid option")

    finally:
        if midi_out:
            midi_out.close_port()
            print("\n🔌 MIDI connection closed")

def main():
    """Main function."""
    test_navigation_step()

if __name__ == "__main__":
    main()