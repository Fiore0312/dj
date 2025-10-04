#!/usr/bin/env python3
"""
🎛️ FX3 Learn Helper - Automated CC Sender for Traktor Controller Manager
Sends the exact CC values needed for FX3 Learn mapping process
"""

import time
import rtmidi

class FX3LearnHelper:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None

        # FX3 CC mappings to configure
        self.fx3_mappings = {
            'drywet': 105,     # Dry/Wet mix knob
            'knob1': 106,      # Parameter 1 knob
            'knob2': 107,      # Parameter 2 knob
            'knob3': 108,      # Parameter 3 knob
            'rst_button': 109, # Reset button
            'frz_button': 110, # Freeze button
            'spr_button': 111, # Spread button
            'onoff': 112       # On/Off button
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
        """Interactive Learn session for FX3"""
        print("🎛️ FX3 LEARN HELPER - Interactive Session")
        print("=" * 50)
        print("📋 Instructions:")
        print("1. Open Traktor Pro 3 Controller Manager")
        print("2. Click 'Learn' for each control")
        print("3. Press ENTER when ready to send CC")
        print("4. Confirm mapping in Traktor")
        print("=" * 50)

        if not self.connect_midi():
            return

        for control_name, cc in self.fx3_mappings.items():
            print(f"\n🎚️ CONFIGURING: FX3 {control_name.upper()}")
            print(f"   Target CC: {cc}")
            print(f"   Traktor Path: FX Unit 3 > {self.get_traktor_path(control_name)}")

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

        print(f"\n🏆 FX3 LEARN SESSION COMPLETED!")
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
        """Quick test of all FX3 CCs"""
        print("🧪 QUICK TEST: All FX3 CCs")

        if not self.connect_midi():
            return

        for control_name, cc in self.fx3_mappings.items():
            value = 127 if 'button' in control_name else 64
            print(f"Testing {control_name} (CC {cc})...")
            self.send_cc(cc, value)
            time.sleep(0.5)

        print("✅ Quick test completed")

def main():
    print("🎛️ FX3 Learn Helper")
    print("Choose mode:")
    print("1. Interactive Learn Session")
    print("2. Quick Test All CCs")

    choice = input("Enter choice (1/2): ").strip()

    helper = FX3LearnHelper()

    if choice == "1":
        helper.interactive_learn_session()
    elif choice == "2":
        helper.quick_test_all()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()