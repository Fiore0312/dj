#!/usr/bin/env python3
"""
Single MIDI Command Test
Send one specific CC command for testing
"""

import rtmidi
import sys

def send_single_cc(cc_number, value):
    """Send single MIDI CC command to Driver IAC Bus 1."""
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
            return False

        midi_out.open_port(target_port)

        # Send CC command (Channel 1)
        status = 176  # Control Change, Channel 1
        message = [status, cc_number, value]
        midi_out.send_message(message)

        print(f"✅ Sent: CC {cc_number} with value {value}")

        midi_out.close_port()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 single_command_test.py <CC_NUMBER> <VALUE>")
        sys.exit(1)

    cc_num = int(sys.argv[1])
    cc_val = int(sys.argv[2])

    send_single_cc(cc_num, cc_val)