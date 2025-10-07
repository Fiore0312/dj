#!/usr/bin/env python3
"""
🚨 MASTER CC BATCH TESTER - For Human Observation
Sends all MASTER CC commands in sequence for human verification
"""

import time
import sys
import os

sys.path.append('/Users/Fiore/dj')
sys.path.append('/Users/Fiore/dj/core')

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False

class MasterCCBatchTester:
    """Batch tester for MASTER CCs - sends all commands for observation"""

    def __init__(self):
        self.midi_out = None

        # Current mappings to test
        self.test_mappings = [
            ('MASTER A (Deck A)', 33),
            ('MASTER B (Deck B)', 37),
            ('MASTER C (Deck C)', 38),
            ('MASTER D (Deck D)', 39)
        ]

    def connect_midi(self) -> bool:
        """Connect to IAC Driver"""
        if not RTMIDI_AVAILABLE:
            print("❌ rtmidi not available")
            return False

        try:
            self.midi_out = rtmidi.MidiOut()
            ports = self.midi_out.get_ports()

            iac_port_idx = None
            for i, port in enumerate(ports):
                if "bus 1" in port.lower() or "iac" in port.lower():
                    iac_port_idx = i
                    break

            if iac_port_idx is not None:
                self.midi_out.open_port(iac_port_idx)
                print(f"✅ Connected to: {ports[iac_port_idx]}")
                return True
            else:
                print("❌ IAC Driver not found")
                return False

        except Exception as e:
            print(f"❌ MIDI connection error: {e}")
            return False

    def send_cc(self, cc: int, value: int):
        """Send CC on Channel 1"""
        if self.midi_out:
            message = [0xB0, cc, value]
            self.midi_out.send_message(message)

    def run_batch_test(self):
        """Send all MASTER CC tests in sequence"""

        print("\n🚨 MASTER BUTTON CC BATCH TEST")
        print("="*60)
        print("TESTING: CC 33, 37, 38, 39 (Current MASTER button mappings)")
        print("KNOWN ISSUE: CC 33 activates LIMITER instead of MASTER button")
        print("="*60)

        print("\n📡 SENDING ALL MASTER BUTTON TEST COMMANDS...")
        print("👀 PLEASE OBSERVE TRAKTOR CAREFULLY!")

        for master_name, cc in self.test_mappings:
            print(f"\n🎛️  Testing {master_name} (CC{cc})...")

            # Send MASTER ON
            print(f"📡 Sending CC{cc} = 127 (MASTER ON)")
            self.send_cc(cc, 127)
            time.sleep(2)  # Allow observation time

            # Send MASTER OFF
            print(f"📡 Sending CC{cc} = 0 (MASTER OFF)")
            self.send_cc(cc, 0)
            time.sleep(1)

        print(f"\n✅ BATCH TEST COMPLETE")
        print(f"\n❓ PLEASE REPORT OBSERVATIONS:")
        print(f"   • Did CC 33 activate the LIMITER instead of MASTER A?")
        print(f"   • Which CCs (37, 38, 39) successfully activated MASTER buttons?")
        print(f"   • Were any MASTER buttons mutually exclusive (only one active)?")
        print(f"   • Did any CCs activate other functions instead of MASTER?")

        return True

def main():
    """Run batch test"""

    print("🚨 URGENT: MASTER BUTTON CC BATCH TEST")
    print("Testing all current MASTER mappings: CC 33, 37, 38, 39")

    tester = MasterCCBatchTester()

    if not tester.connect_midi():
        print("❌ Cannot connect to MIDI")
        return

    print(f"""
🎯 BATCH TEST PROCEDURE:

1. This script will send ALL 4 MASTER CC commands in sequence
2. Each CC will be sent as ON (127) then OFF (0)
3. OBSERVE Traktor carefully for each CC test
4. Report which CCs work vs which are broken

CRITICAL: CC 33 should activate LIMITER (not MASTER) - this is the known bug!
""")

    # Run the batch test
    success = tester.run_batch_test()

    if success:
        print(f"\n🎯 NEXT STEP: Run master_button_discovery.py for Learn Mode")

if __name__ == "__main__":
    main()