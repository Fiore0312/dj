#!/usr/bin/env python3
"""
🚨 URGENT MASTER CC TESTER
Quick tester for MASTER button CCs 33, 37, 38, 39

This script will systematically test the current MASTER button mappings
and verify which ones work vs which ones are broken.
"""

import time
import sys
import os

# Add parent directory to path to import traktor_control
sys.path.append('/Users/Fiore/dj')
sys.path.append('/Users/Fiore/dj/core')

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False
    print("⚠️ rtmidi not available - install with: pip install python-rtmidi")

class MasterCCTester:
    """Quick tester for MASTER button CCs"""

    def __init__(self):
        self.midi_out = None

        # Current problematic mappings from traktor_control.py
        self.test_mappings = {
            'MASTER A (Deck A)': 33,
            'MASTER B (Deck B)': 37,
            'MASTER C (Deck C)': 38,
            'MASTER D (Deck D)': 39
        }

    def connect_midi(self) -> bool:
        """Connect to IAC Driver"""
        if not RTMIDI_AVAILABLE:
            print("❌ rtmidi not available")
            return False

        try:
            self.midi_out = rtmidi.MidiOut()
            ports = self.midi_out.get_ports()

            # Find IAC Bus 1
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
            message = [0xB0, cc, value]  # Channel 1, CC, Value
            self.midi_out.send_message(message)
            print(f"📡 Sent: Channel 1, CC{cc}, Value {value}")

    def test_master_ccs(self):
        """Test all MASTER CCs systematically"""

        print("\n🚨 TESTING CURRENT MASTER BUTTON MAPPINGS")
        print("="*60)
        print("CRITICAL: We need to verify which MASTER CCs work correctly")
        print("Expected behavior: MASTER button should light up and become tempo reference")
        print("Known issue: CC 33 activates LIMITER instead of MASTER")
        print("="*60)

        results = {}

        for master_name, cc in self.test_mappings.items():
            print(f"\n🎛️  TESTING {master_name} (CC{cc})")
            print("-" * 40)

            # Test MASTER ON (CC = 127)
            print(f"📡 Sending CC{cc} = 127 (MASTER ON)...")
            self.send_cc(cc, 127)
            time.sleep(1.5)

            print(f"""
❓ PLEASE CHECK TRAKTOR NOW:

   1. Did the MASTER button for {master_name} light up?
   2. Did it become the tempo reference (other MASTERs turn off)?
   3. Or did something else happen (e.g., limiter, other effect)?

   Expected: MASTER button glows, controls global tempo
   Problem: CC33 activates LIMITER instead
""")

            response = input(f"What happened with CC{cc}? (working/limiter/other/nothing): ").lower().strip()

            if response == 'working':
                results[master_name] = f"✅ WORKING - CC{cc} correctly activates MASTER"
                print(f"✅ {master_name} MASTER button works correctly!")
            elif response == 'limiter':
                results[master_name] = f"❌ LIMITER - CC{cc} activates LIMITER (not MASTER)"
                print(f"❌ {master_name} activates LIMITER instead of MASTER!")
            elif response == 'other':
                what = input("   What did it activate instead?: ")
                results[master_name] = f"❌ OTHER - CC{cc} activates: {what}"
                print(f"❌ {master_name} activates {what} instead of MASTER!")
            else:
                results[master_name] = f"❌ NO RESPONSE - CC{cc} does nothing"
                print(f"❌ {master_name} shows no response!")

            # Test MASTER OFF (CC = 0)
            print(f"\n📡 Sending CC{cc} = 0 (MASTER OFF)...")
            self.send_cc(cc, 0)
            time.sleep(1)

            input("Press Enter to continue to next MASTER button...")

        return results

    def print_summary(self, results: dict):
        """Print test summary"""

        print(f"\n{'='*70}")
        print("📊 MASTER BUTTON TEST RESULTS SUMMARY")
        print(f"{'='*70}")

        working_count = 0
        broken_count = 0

        for master_name, result in results.items():
            print(f"{result}")
            if "WORKING" in result:
                working_count += 1
            else:
                broken_count += 1

        print(f"\n📈 STATISTICS:")
        print(f"   ✅ Working MASTER buttons: {working_count}/4")
        print(f"   ❌ Broken MASTER buttons: {broken_count}/4")

        if broken_count > 0:
            print(f"\n🚨 URGENT ACTION REQUIRED:")
            print(f"   {broken_count} MASTER button(s) need CC discovery!")
            print(f"   Run: python3 master_button_discovery.py")
            print(f"   Without working MASTER controls, professional mixing is impossible!")
        else:
            print(f"\n🎉 ALL MASTER BUTTONS WORKING!")

        print(f"\n💡 NEXT STEPS:")
        if broken_count > 0:
            print(f"   1. Run master_button_discovery.py for full Learn Mode discovery")
            print(f"   2. Use Traktor Controller Manager Learn Mode")
            print(f"   3. Update traktor_control.py with correct CCs")
        print(f"   4. Test MASTER button exclusivity (only one active at a time)")
        print(f"   5. Verify tempo reference functionality in mixing workflow")

def main():
    """Run MASTER CC test"""

    tester = MasterCCTester()

    print("🚨 URGENT MASTER BUTTON CC TESTER")
    print("="*40)
    print("Testing CC 33, 37, 38, 39 systematically")
    print("="*40)

    if not tester.connect_midi():
        print("❌ Cannot connect to MIDI - ensure IAC Driver is running")
        return

    print(f"""
🎛️ MASTER BUTTON FUNCTION:

   The MASTER button sets which deck controls the GLOBAL TEMPO REFERENCE.
   Only one deck can be MASTER at a time (mutually exclusive).
   Essential for professional DJ mixing and BPM synchronization.

   CRITICAL ISSUE: CC 33 activates LIMITER instead of MASTER button!

🎯 This test will verify which CCs work correctly.
""")

    input("Press Enter when Traktor Pro is open and ready for testing...")

    # Run systematic test
    results = tester.test_master_ccs()

    # Print summary
    tester.print_summary(results)

if __name__ == "__main__":
    main()