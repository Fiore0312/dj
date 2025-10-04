#!/usr/bin/env python3
"""
🎛️ Complete FX Learn Helper - All FX Units (2, 3, 4) Configuration Tool
Master script for configuring all remaining FX units in Traktor Controller Manager
"""

import time
import rtmidi

class CompleteFXLearnHelper:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None

        # Complete FX mappings for all units
        self.fx_mappings = {
            'FX2': {
                'drywet': 97, 'knob1': 98, 'knob2': 99, 'knob3': 100,
                'rst_button': 101, 'frz_button': 102, 'spr_button': 103, 'onoff': 104
            },
            'FX3': {
                'drywet': 105, 'knob1': 106, 'knob2': 107, 'knob3': 108,
                'rst_button': 109, 'frz_button': 110, 'spr_button': 111, 'onoff': 112
            },
            'FX4': {
                'drywet': 113, 'knob1': 114, 'knob2': 115, 'knob3': 116,
                'rst_button': 117, 'frz_button': 118, 'spr_button': 119, 'onoff': 120
            }
        }

        # Control descriptions for user interface
        self.control_descriptions = {
            'drywet': 'Dry/Wet Mix Knob',
            'knob1': 'Parameter Knob 1',
            'knob2': 'Parameter Knob 2',
            'knob3': 'Parameter Knob 3',
            'rst_button': 'Reset Button',
            'frz_button': 'Freeze Button',
            'spr_button': 'Spread Button',
            'onoff': 'On/Off Switch'
        }

        # Traktor paths for Controller Manager
        self.traktor_paths = {
            'drywet': 'Dry/Wet',
            'knob1': 'Knob 1',
            'knob2': 'Knob 2',
            'knob3': 'Knob 3',
            'rst_button': 'Reset',
            'frz_button': 'Freeze',
            'spr_button': 'Spread',
            'onoff': 'On'
        }

    def connect_midi(self):
        """Connect to IAC Bus 1"""
        print("🔍 Searching for MIDI ports...")

        for i, port in enumerate(self.out_ports):
            print(f"  [{i}] {port}")

        for i, port in enumerate(self.out_ports):
            if "IAC" in port and ("Bus 1" in port or " 1" in port):
                self.iac_port = i
                break

        if self.iac_port is None:
            print("❌ IAC Bus 1 not found!")
            print("💡 Setup Instructions:")
            print("   1. Open Audio MIDI Setup")
            print("   2. Window > Show MIDI Studio")
            print("   3. Double-click 'IAC Driver'")
            print("   4. Check 'Device is online'")
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
            return True
        except Exception as e:
            print(f"❌ MIDI error: {e}")
            return False

    def configure_fx_unit(self, fx_unit):
        """Configure a single FX unit interactively"""
        print(f"\n{'='*60}")
        print(f"🎛️ CONFIGURING FX UNIT {fx_unit[-1]}")
        print(f"{'='*60}")

        mappings = self.fx_mappings[fx_unit]
        cc_range = f"CC {min(mappings.values())}-{max(mappings.values())}"
        print(f"📍 CC Range: {cc_range}")
        print(f"📋 Controls to map: {len(mappings)}")

        # Wait for user readiness
        input(f"\n⏸️  Ensure FX Unit {fx_unit[-1]} is visible in Traktor. Press ENTER to continue...")

        success_count = 0

        for control_name, cc in mappings.items():
            print(f"\n🎚️ MAPPING: {self.control_descriptions[control_name]}")
            print(f"   🎯 Target: FX Unit {fx_unit[-1]} > {self.traktor_paths[control_name]}")
            print(f"   📡 CC: {cc}")

            # Instructions for Traktor
            print(f"\n📋 TRAKTOR STEPS:")
            print(f"   1. Click 'Learn' in Controller Manager")
            print(f"   2. Navigate to: FX Unit {fx_unit[-1]} > {self.traktor_paths[control_name]}")
            print(f"   3. Press ENTER below to send CC {cc}")

            input(f"   ⏸️  Ready to send CC {cc}? Press ENTER...")

            # Send appropriate value
            if 'button' in control_name:
                value = 127  # Full value for buttons
                print(f"   📤 Sending: CC {cc} = {value} (BUTTON)")
            else:
                value = 64   # Mid value for knobs
                print(f"   📤 Sending: CC {cc} = {value} (KNOB)")

            success = self.send_cc(cc, value)

            if success:
                print(f"   ✅ CC {cc} sent successfully")

                # User confirmation
                while True:
                    result = input(f"   ❓ Mapping confirmed in Traktor? (y/n/r=retry): ").lower().strip()

                    if result == 'y':
                        print(f"   🎉 {control_name} configured successfully!")
                        success_count += 1
                        break
                    elif result == 'n':
                        print(f"   ⚠️  {control_name} failed - may need manual configuration")
                        break
                    elif result == 'r':
                        print(f"   🔄 Retrying CC {cc}...")
                        self.send_cc(cc, value)
                    else:
                        print(f"   ⚠️  Please enter 'y', 'n', or 'r'")
            else:
                print(f"   ❌ Failed to send CC {cc}")

        # Unit summary
        print(f"\n📊 {fx_unit} CONFIGURATION SUMMARY:")
        print(f"   Successful mappings: {success_count}/{len(mappings)}")

        if success_count == len(mappings):
            print(f"   🎉 PERFECT! All {fx_unit} controls configured")
        elif success_count >= len(mappings) * 0.75:
            print(f"   ✅ EXCELLENT! Most {fx_unit} controls working")
        else:
            print(f"   ⚠️  PARTIAL: Some {fx_unit} controls need attention")

        return success_count

    def complete_configuration_session(self):
        """Complete configuration session for all FX units"""
        print("🎛️ COMPLETE FX LEARN HELPER")
        print("=" * 70)
        print("🎯 OBJECTIVE: Configure FX Units 2, 3, and 4")
        print("📊 TOTAL CONTROLS: 24 (8 per unit)")
        print("🔢 CC RANGE: 97-120")
        print("=" * 70)

        print(f"\n📋 PRE-CONFIGURATION CHECKLIST:")
        print("✅ 1. Traktor Pro 3 is open")
        print("✅ 2. Controller Manager is open (Preferences > Controller Manager)")
        print("✅ 3. Your controller device is selected")
        print("✅ 4. FX Units are visible in Traktor interface")
        print("✅ 5. IAC Bus 1 is configured and online")

        if not self.connect_midi():
            return

        input(f"\n⏸️  Press ENTER to begin complete FX configuration...")

        total_success = 0
        total_controls = 0

        # Configure each FX unit
        for fx_unit in ['FX2', 'FX3', 'FX4']:
            unit_success = self.configure_fx_unit(fx_unit)
            total_success += unit_success
            total_controls += len(self.fx_mappings[fx_unit])

            if fx_unit != 'FX4':  # Don't pause after last unit
                input(f"\n⏭️  Press ENTER to continue to {['FX3', 'FX4'][['FX2', 'FX3'].index(fx_unit)]}...")

        # Final summary
        print(f"\n🏆{'='*60}🏆")
        print("COMPLETE FX CONFIGURATION SESSION RESULTS")
        print(f"🏆{'='*60}🏆")

        success_rate = (total_success / total_controls) * 100
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Controls Configured: {total_success}/{total_controls}")
        print(f"   Success Rate: {success_rate:.1f}%")

        if success_rate >= 95:
            status = "🎉 EXCELLENT - Production Ready!"
        elif success_rate >= 80:
            status = "✅ GOOD - Minor issues only"
        elif success_rate >= 60:
            status = "⚠️ PARTIAL - Some controls need work"
        else:
            status = "❌ POOR - Major configuration needed"

        print(f"   Status: {status}")

        print(f"\n🚀 NEXT STEPS:")
        if success_rate >= 95:
            print("   ✅ Export TSI file from Controller Manager")
            print("   ✅ Test FX controls in live mixing")
            print("   ✅ All FX Units ready for autonomous DJ!")
        elif success_rate >= 80:
            print("   🔧 Review failed controls manually")
            print("   ✅ Export partial TSI configuration")
            print("   ⚠️ Test carefully before production use")
        else:
            print("   🔧 Manual MIDI Learn session recommended")
            print("   📚 Review Traktor Controller Manager documentation")
            print("   ❌ Additional configuration required")

        print(f"\n💾 SAVE REMINDER:")
        print("   Don't forget to EXPORT your TSI file in Controller Manager!")
        print("   Recommended filename: Complete_FX_Mapping_97-120.tsi")

    def quick_test_all_fx(self):
        """Quick test all FX units for verification"""
        print("🧪 QUICK TEST: All FX Units (2, 3, 4)")
        print("=" * 50)

        if not self.connect_midi():
            return

        for fx_unit, mappings in self.fx_mappings.items():
            print(f"\n🎛️ Testing {fx_unit}...")

            for control_name, cc in mappings.items():
                value = 127 if 'button' in control_name else 64
                print(f"   📤 {control_name}: CC {cc} = {value}")
                self.send_cc(cc, value)
                time.sleep(0.3)

        print(f"\n✅ Quick test completed - check Traktor for responses")

def main():
    print("🎛️ Complete FX Learn Helper")
    print("Configure FX Units 2, 3, and 4 for Traktor Pro 3")
    print("=" * 60)
    print("Available modes:")
    print("1. Complete Interactive Configuration Session")
    print("2. Quick Test All FX Units")
    print("3. Exit")

    choice = input("\nEnter choice (1/2/3): ").strip()

    helper = CompleteFXLearnHelper()

    if choice == "1":
        helper.complete_configuration_session()
    elif choice == "2":
        helper.quick_test_all_fx()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()