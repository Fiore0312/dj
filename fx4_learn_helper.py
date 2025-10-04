#!/usr/bin/env python3
"""
🎛️ FX4 Learn Helper - Automated CC Sender for Traktor Controller Manager
Sends the exact CC values needed for FX4 Learn mapping process
"""

import time
import rtmidi

class FX4LearnHelper:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None

        # FX4 CC mappings to configure
        self.fx4_mappings = {
            'drywet': 113,     # Dry/Wet mix knob
            'knob1': 114,      # Parameter 1 knob
            'knob2': 115,      # Parameter 2 knob
            'knob3': 116,      # Parameter 3 knob
            'rst_button': 117, # Reset button
            'frz_button': 118, # Freeze button
            'spr_button': 119, # Spread button
            'onoff': 120       # On/Off button
        }

    def connect_midi(self):
        """Connect to IAC Bus 1"""
        for i, port in enumerate(self.out_ports):
            if "IAC" in port and ("Bus 1" in port or " 1" in port):
                self.iac_port = i
                break

        if self.iac_port is None:
            print("❌ IAC Bus 1 not found!")
            return False

        try:
            self.midiout.open_port(self.iac_port)
            print(f"✅ Connected to: {self.out_ports[self.iac_port]}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def send_cc(self, cc, value=64):
        """Send MIDI CC on channel 1"""
        try:
            message = [0xB0, cc, value]  # Channel 1, CC, Value
            self.midiout.send_message(message)
            print(f"📤 Sent: CC {cc} = {value}")
            return True
        except Exception as e:
            print(f"❌ MIDI error: {e}")
            return False

    def interactive_learn_session(self):
        """Interactive Learn session for FX4"""
        print("🎛️ FX4 LEARN HELPER - Interactive Session")
        print("=" * 50)
        print("📋 Instructions:")
        print("1. Open Traktor Pro 3 Controller Manager")
        print("2. Click 'Learn' for each control")
        print("3. Press ENTER when ready to send CC")
        print("4. Confirm mapping in Traktor")
        print("=" * 50)

        if not self.connect_midi():
            return

        for control_name, cc in self.fx4_mappings.items():
            print(f"\n🎚️ CONFIGURING: FX4 {control_name.upper()}")
            print(f"   Target CC: {cc}")
            print(f"   Traktor Path: FX Unit 4 > {self.get_traktor_path(control_name)}")

            input(f"   ⏸️  Press ENTER to send CC {cc} for {control_name}...")

            # Send appropriate value based on control type
            if 'button' in control_name:
                value = 127  # Full value for buttons
            else:
                value = 64   # Mid value for knobs

            success = self.send_cc(cc, value)

            if success:
                print(f"   ✅ CC {cc} sent successfully")
                print(f"   📝 Check Traktor Controller Manager for mapping confirmation")
            else:
                print(f"   ❌ Failed to send CC {cc}")

            # Wait for user confirmation
            result = input(f"   ❓ Mapping successful in Traktor? (y/n): ").lower()
            if result == 'y':
                print(f"   🎉 {control_name} configured successfully!")
            else:
                print(f"   ⚠️  {control_name} needs manual attention")

        print(f"\n🏆 FX4 LEARN SESSION COMPLETED!")
        print(f"📝 Remember to save your TSI file in Controller Manager")

    def get_traktor_path(self, control_name):
        """Get Traktor Controller Manager path for control"""
        paths = {
            'drywet': 'Dry/Wet',
            'knob1': 'Knob 1',
            'knob2': 'Knob 2',
            'knob3': 'Knob 3',
            'rst_button': 'Reset',
            'frz_button': 'Freeze',
            'spr_button': 'Spread',
            'onoff': 'On'
        }
        return paths.get(control_name, control_name)

    def quick_test_all(self):
        """Quick test of all FX4 CCs"""
        print("🧪 QUICK TEST: All FX4 CCs")

        if not self.connect_midi():
            return

        for control_name, cc in self.fx4_mappings.items():
            value = 127 if 'button' in control_name else 64
            print(f"Testing {control_name} (CC {cc})...")
            self.send_cc(cc, value)
            time.sleep(0.5)

        print("✅ Quick test completed")

def main():
    print("🎛️ FX4 Learn Helper")
    print("Choose mode:")
    print("1. Interactive Learn Session")
    print("2. Quick Test All CCs")

    choice = input("Enter choice (1/2): ").strip()

    helper = FX4LearnHelper()

    if choice == "1":
        helper.interactive_learn_session()
    elif choice == "2":
        helper.quick_test_all()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()