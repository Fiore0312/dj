#!/usr/bin/env python3
"""
🚨 CRITICAL BROWSER DIRECTION TEST
==================================
Tests CC56 with both value directions to determine correct UP/DOWN mapping.
This will definitively solve the direction inversion problem.
"""

import time
import rtmidi
from typing import Optional

class BrowserDirectionTester:
    """Test browser tree navigation directions"""

    def __init__(self):
        self.midi_out: Optional[rtmidi.MidiOut] = None

    def connect_midi(self) -> bool:
        """Connect to IAC Driver"""
        try:
            self.midi_out = rtmidi.MidiOut()
            ports = self.midi_out.get_ports()

            # Find IAC Bus 1
            for i, port in enumerate(ports):
                if "IAC" in port and "Bus 1" in port:
                    self.midi_out.open_port(i)
                    print(f"✅ Connected to: {port}")
                    return True

            print("❌ IAC Driver Bus 1 not found")
            return False

        except Exception as e:
            print(f"❌ MIDI connection error: {e}")
            return False

    def send_midi_cc(self, cc: int, value: int, description: str) -> bool:
        """Send MIDI CC command"""
        if not self.midi_out:
            return False

        try:
            message = [0xB0, cc, value]  # Channel 1, Control Change
            self.midi_out.send_message(message)
            print(f"📤 SENT: CC{cc}={value} ({description})")
            return True
        except Exception as e:
            print(f"❌ Error sending MIDI: {e}")
            return False

    def test_direction_mapping(self):
        """Test both directions on CC56 to determine correct mapping"""
        print("🚨 CRITICAL BROWSER DIRECTION TEST")
        print("=" * 50)
        print("📍 SETUP INSTRUCTIONS:")
        print("1. Open Traktor Pro 3")
        print("2. Make browser visible")
        print("3. Navigate to a folder with subfolders (like 'Chill')")
        print("4. Focus on browser tree (left side)")
        print("5. Watch CAREFULLY which direction each command moves")
        print("=" * 50)

        input("Press ENTER when Traktor is ready...")

        # Test current "UP" command (value=1)
        print("\n🧪 TEST 1: Current 'UP' logic (CC56, value=1)")
        print("📝 Current code expects: MOVES UP in tree")
        self.send_midi_cc(56, 1, "Current UP command")

        direction1 = input("Which direction did it move? (up/down/none): ").lower()

        time.sleep(1)

        # Test current "DOWN" command (value=127)
        print("\n🧪 TEST 2: Current 'DOWN' logic (CC56, value=127)")
        print("📝 Current code expects: MOVES DOWN in tree")
        self.send_midi_cc(56, 127, "Current DOWN command")

        direction2 = input("Which direction did it move? (up/down/none): ").lower()

        # Analysis
        print("\n📊 DIRECTION MAPPING ANALYSIS:")
        print(f"CC56, value=1   → Actual movement: {direction1.upper()}")
        print(f"CC56, value=127 → Actual movement: {direction2.upper()}")

        # Determine if mapping is correct or inverted
        if direction1 == "up" and direction2 == "down":
            print("\n✅ DIRECTION MAPPING IS CORRECT")
            print("   Problem is NOT in direction values")
            print("   Issue may be elsewhere (command parsing, browser focus, etc.)")
            return "CORRECT"

        elif direction1 == "down" and direction2 == "up":
            print("\n🚨 DIRECTION MAPPING IS INVERTED")
            print("   Current code has wrong direction values")
            print("   SOLUTION: Swap values in browser_tree_up/down functions")
            print("   UP should use value=127, DOWN should use value=1")
            return "INVERTED"

        elif direction1 == "none" and direction2 == "none":
            print("\n❌ CC56 DOES NOT CONTROL BROWSER TREE")
            print("   CC56 may be wrong, or browser doesn't have focus")
            print("   Need to discover correct CC for browser tree navigation")
            return "WRONG_CC"

        else:
            print(f"\n❓ UNCLEAR RESULT: {direction1}/{direction2}")
            print("   May need to repeat test or check browser setup")
            return "UNCLEAR"

    def run_comprehensive_test(self):
        """Run complete direction test"""
        if not self.connect_midi():
            return

        try:
            result = self.test_direction_mapping()

            print(f"\n🎯 TEST RESULT: {result}")

            if result == "INVERTED":
                print("\n🔧 REQUIRED FIX:")
                print("In traktor_control.py, change browser_tree_up and browser_tree_down:")
                print("   browser_tree_up: use value=127 (instead of 1)")
                print("   browser_tree_down: use value=1 (instead of 127)")

            elif result == "WRONG_CC":
                print("\n🔍 REQUIRED DISCOVERY:")
                print("Need to find correct CC for browser tree navigation")
                print("CC56 may control something else")

        finally:
            if self.midi_out:
                self.midi_out.close()

def main():
    tester = BrowserDirectionTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()