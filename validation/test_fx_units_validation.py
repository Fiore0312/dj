#!/usr/bin/env python3
"""
🎛️ Interactive FX Units 2/3/4 Validation Tool
Test CC mappings from traktor_control.py with user confirmation

This tool systematically tests each FX unit (2, 3, 4) by:
- Testing all 8 controls per unit
- Using predicted CC mappings (97-104, 105-112, 113-120)
- Asking for user confirmation that controls work in Traktor
- Generating a comprehensive validation report
"""

import time
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.append(str(Path(__file__).parent))

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importing rtmidi: {e}")
    print("Install with: pip install python-rtmidi")
    RTMIDI_AVAILABLE = False
    sys.exit(1)

class InteractiveFXValidator:
    """Interactive validator for FX Units 2, 3, and 4"""

    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None
        self.validation_results = {}

        # FX mappings from traktor_control.py
        self.fx_mappings = {
            2: {  # FX Unit 2 - CC 97-104
                'drywet': 97,
                'knob1': 98,
                'knob2': 99,
                'knob3': 100,
                'rst_button': 101,
                'frz_button': 102,
                'spr_button': 103,
                'onoff': 104
            },
            3: {  # FX Unit 3 - CC 105-112
                'drywet': 105,
                'knob1': 106,
                'knob2': 107,
                'knob3': 108,
                'rst_button': 109,
                'frz_button': 110,
                'spr_button': 111,
                'onoff': 112
            },
            4: {  # FX Unit 4 - CC 113-120
                'drywet': 113,
                'knob1': 114,
                'knob2': 115,
                'knob3': 116,
                'rst_button': 117,
                'frz_button': 118,
                'spr_button': 119,
                'onoff': 120
            }
        }

        # Control descriptions for user interface
        self.control_descriptions = {
            'drywet': 'Dry/Wet Mix Knob',
            'knob1': 'Parameter Knob 1',
            'knob2': 'Parameter Knob 2',
            'knob3': 'Parameter Knob 3',
            'rst_button': 'Reset (RST) Button',
            'frz_button': 'Freeze (FRZ) Button',
            'spr_button': 'Spread (SPR) Button',
            'onoff': 'On/Off Main Switch'
        }

        # Test patterns for different control types
        self.knob_test_values = [0, 32, 64, 96, 127, 64]  # Sweep and return to center
        self.button_test_pattern = [(127, 0.2), (0, 0.3)]  # Press then release

    def find_and_connect_iac(self) -> bool:
        """Find and connect to IAC Bus 1"""
        print("🔍 Searching for MIDI ports...")
        print("\n📤 Available MIDI output ports:")

        for i, port in enumerate(self.out_ports):
            print(f"  [{i}] {port}")

        # Look for IAC Bus 1
        for i, port in enumerate(self.out_ports):
            if "IAC" in port and ("Bus 1" in port or " 1" in port):
                self.iac_port = i
                break

        if self.iac_port is None:
            print("\n❌ IAC Bus 1 not found!")
            print("💡 Setup Instructions:")
            print("   1. Open Audio MIDI Setup (Applications > Utilities)")
            print("   2. Window > Show MIDI Studio")
            print("   3. Double-click 'IAC Driver'")
            print("   4. Check 'Device is online'")
            print("   5. Ensure 'Bus 1' is listed")
            return False

        try:
            self.midiout.open_port(self.iac_port)
            print(f"\n✅ Connected to: {self.out_ports[self.iac_port]}")
            return True
        except Exception as e:
            print(f"\n❌ Failed to connect to IAC port: {e}")
            return False

    def send_midi_cc(self, cc: int, value: int) -> bool:
        """Send MIDI Control Change message"""
        try:
            message = [0xB0, cc, value]  # Channel 1, CC, Value
            self.midiout.send_message(message)
            return True
        except Exception as e:
            print(f"❌ MIDI send error: {e}")
            return False

    def test_knob_control(self, fx_unit: int, control_name: str, cc: int) -> bool:
        """Test a knob control with visual sweep"""
        print(f"\n🎚️  Testing {self.control_descriptions[control_name]}")
        print(f"    CC {cc} - Watch FX{fx_unit} in Traktor for knob movement")
        print("    Test pattern: 0% → 25% → 50% → 75% → 100% → 50%")

        input("\n⏸️  Press ENTER when ready to test this knob...")

        # Send test pattern
        for i, value in enumerate(self.knob_test_values):
            percentage = int((value / 127) * 100)
            print(f"    📤 Sending: {percentage:3d}% (CC{cc}={value})")

            if not self.send_midi_cc(cc, value):
                print(f"    ❌ Failed to send MIDI CC{cc}={value}")
                return False

            time.sleep(0.3)  # Visible delay between changes

        # User confirmation
        while True:
            response = input(f"\n❓ Did you see the {control_name} knob moving in FX{fx_unit}? (y/n/r=retry): ").lower().strip()

            if response == 'y':
                print(f"    ✅ CONFIRMED: {control_name} works (CC {cc})")
                return True
            elif response == 'n':
                print(f"    ❌ NOT WORKING: {control_name} failed (CC {cc})")
                return False
            elif response == 'r':
                print(f"    🔄 Retrying {control_name} test...")
                # Retry the test
                for value in self.knob_test_values:
                    percentage = int((value / 127) * 100)
                    print(f"    📤 Retry: {percentage:3d}% (CC{cc}={value})")
                    self.send_midi_cc(cc, value)
                    time.sleep(0.3)
            else:
                print("    ⚠️  Please enter 'y' (yes), 'n' (no), or 'r' (retry)")

    def test_button_control(self, fx_unit: int, control_name: str, cc: int) -> bool:
        """Test a button control with press/release"""
        print(f"\n🔘 Testing {self.control_descriptions[control_name]}")
        print(f"    CC {cc} - Watch FX{fx_unit} in Traktor for button activation")
        print("    Test pattern: Press (ON) → Release (OFF)")

        input("\n⏸️  Press ENTER when ready to test this button...")

        # Send button test pattern
        for value, duration in self.button_test_pattern:
            action = "PRESS (ON)" if value > 0 else "RELEASE (OFF)"
            print(f"    📤 {action} (CC{cc}={value})")

            if not self.send_midi_cc(cc, value):
                print(f"    ❌ Failed to send MIDI CC{cc}={value}")
                return False

            time.sleep(duration)

        # User confirmation
        while True:
            response = input(f"\n❓ Did you see the {control_name} activate in FX{fx_unit}? (y/n/r=retry): ").lower().strip()

            if response == 'y':
                print(f"    ✅ CONFIRMED: {control_name} works (CC {cc})")
                return True
            elif response == 'n':
                print(f"    ❌ NOT WORKING: {control_name} failed (CC {cc})")
                return False
            elif response == 'r':
                print(f"    🔄 Retrying {control_name} test...")
                # Retry the test
                for value, duration in self.button_test_pattern:
                    action = "PRESS (ON)" if value > 0 else "RELEASE (OFF)"
                    print(f"    📤 Retry: {action} (CC{cc}={value})")
                    self.send_midi_cc(cc, value)
                    time.sleep(duration)
            else:
                print("    ⚠️  Please enter 'y' (yes), 'n' (no), or 'r' (retry)")

    def test_fx_unit(self, fx_unit: int) -> Dict[str, Dict]:
        """Test all controls for a specific FX unit"""
        print(f"\n{'='*60}")
        print(f"🎛️  FX UNIT {fx_unit} VALIDATION")
        print(f"{'='*60}")
        print(f"Testing CC range: {min(self.fx_mappings[fx_unit].values())}-{max(self.fx_mappings[fx_unit].values())}")

        unit_results = {}

        # Test knobs first (easier to see)
        knob_controls = ['drywet', 'knob1', 'knob2', 'knob3']
        print(f"\n🎚️  KNOB CONTROLS TESTING")
        print(f"-" * 30)

        for control in knob_controls:
            cc = self.fx_mappings[fx_unit][control]
            success = self.test_knob_control(fx_unit, control, cc)

            unit_results[control] = {
                'cc': cc,
                'type': 'knob',
                'working': success,
                'tested_at': datetime.now().isoformat(),
                'description': self.control_descriptions[control]
            }

        # Test buttons
        button_controls = ['rst_button', 'frz_button', 'spr_button', 'onoff']
        print(f"\n🔘 BUTTON CONTROLS TESTING")
        print(f"-" * 30)

        for control in button_controls:
            cc = self.fx_mappings[fx_unit][control]
            success = self.test_button_control(fx_unit, control, cc)

            unit_results[control] = {
                'cc': cc,
                'type': 'button',
                'working': success,
                'tested_at': datetime.now().isoformat(),
                'description': self.control_descriptions[control]
            }

        # Unit summary
        total_controls = len(unit_results)
        working_controls = sum(1 for result in unit_results.values() if result['working'])
        success_rate = (working_controls / total_controls) * 100

        print(f"\n📊 FX{fx_unit} TEST SUMMARY:")
        print(f"    Working controls: {working_controls}/{total_controls} ({success_rate:.0f}%)")

        if success_rate == 100:
            print(f"    🎉 PERFECT! All FX{fx_unit} controls validated")
        elif success_rate >= 75:
            print(f"    ✅ EXCELLENT! FX{fx_unit} mostly working")
        elif success_rate >= 50:
            print(f"    ⚠️  PARTIAL: FX{fx_unit} has some issues")
        else:
            print(f"    ❌ POOR: FX{fx_unit} has major problems")

        # Show failed controls if any
        failed_controls = [name for name, data in unit_results.items() if not data['working']]
        if failed_controls:
            print(f"    Failed controls: {', '.join(failed_controls)}")

        return unit_results

    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"fx_units_validation_report_{timestamp}.json"

        print(f"\n{'🏆'*20}")
        print("FX UNITS VALIDATION REPORT")
        print(f"{'🏆'*20}")

        # Calculate overall statistics
        total_units = len(self.validation_results)
        total_controls = sum(len(unit_data) for unit_data in self.validation_results.values())
        total_working = sum(
            sum(1 for control_data in unit_data.values() if control_data['working'])
            for unit_data in self.validation_results.values()
        )
        overall_success_rate = (total_working / total_controls) * 100 if total_controls > 0 else 0

        # Detailed analysis per unit
        print(f"\n📊 DETAILED RESULTS BY FX UNIT:")
        print(f"-" * 50)

        units_summary = {}
        for fx_unit in [2, 3, 4]:
            if fx_unit in self.validation_results:
                unit_data = self.validation_results[fx_unit]
                unit_controls = len(unit_data)
                unit_working = sum(1 for data in unit_data.values() if data['working'])
                unit_success_rate = (unit_working / unit_controls) * 100

                status_emoji = "✅" if unit_success_rate == 100 else "⚠️" if unit_success_rate >= 75 else "❌"
                print(f"FX{fx_unit}: {status_emoji} {unit_working}/{unit_controls} controls ({unit_success_rate:.0f}%)")

                # Show CC range
                ccs = [data['cc'] for data in unit_data.values()]
                cc_range = f"CC {min(ccs)}-{max(ccs)}"
                print(f"      Range: {cc_range}")

                # Show failed controls
                failed = [name for name, data in unit_data.items() if not data['working']]
                if failed:
                    print(f"      Failed: {', '.join(failed)}")

                units_summary[fx_unit] = {
                    'total_controls': unit_controls,
                    'working_controls': unit_working,
                    'success_rate': unit_success_rate,
                    'cc_range': cc_range,
                    'failed_controls': failed
                }

        # Overall assessment
        print(f"\n🎯 OVERALL VALIDATION RESULTS:")
        print(f"   Total FX Units Tested: {total_units}")
        print(f"   Total Controls Tested: {total_controls}")
        print(f"   Working Controls: {total_working}")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}%")

        # Validation status
        if overall_success_rate >= 95:
            validation_status = "🎉 EXCELLENT - Ready for production"
            confidence = "HIGH"
        elif overall_success_rate >= 80:
            validation_status = "✅ GOOD - Minor issues only"
            confidence = "MEDIUM-HIGH"
        elif overall_success_rate >= 60:
            validation_status = "⚠️ PARTIAL - Some controls need investigation"
            confidence = "MEDIUM"
        else:
            validation_status = "❌ POOR - Significant mapping issues"
            confidence = "LOW"

        print(f"\n💡 VALIDATION ASSESSMENT:")
        print(f"   Status: {validation_status}")
        print(f"   Confidence Level: {confidence}")

        # Recommendations
        print(f"\n🚀 RECOMMENDATIONS:")
        if overall_success_rate >= 95:
            print("   ✅ All FX mappings validated successfully!")
            print("   ✅ Update traktor_control.py: Change PREDICTED → CONFIRMED")
            print("   ✅ FX Units 2/3/4 ready for autonomous DJ use")
        elif overall_success_rate >= 80:
            print("   ⚠️ Most mappings work well")
            print("   ⚠️ Investigate failed controls with MIDI Learn")
            print("   ✅ Can use working controls in production")
        elif overall_success_rate >= 60:
            print("   🔍 Moderate mapping issues detected")
            print("   🔧 Use MIDI Learn for failed controls")
            print("   ⚠️ Test carefully before production use")
        else:
            print("   ❌ Significant mapping problems")
            print("   🔧 Manual MIDI Learn session recommended")
            print("   ❌ Do not use in production until fixed")

        # Generate JSON report
        report_data = {
            'test_session': {
                'timestamp': datetime.now().isoformat(),
                'tool_version': 'Interactive FX Units Validator v1.0',
                'tested_fx_units': list(self.validation_results.keys()),
                'cc_ranges_tested': {
                    f'fx{unit}': f"CC {min(data['cc'] for data in unit_data.values())}-{max(data['cc'] for data in unit_data.values())}"
                    for unit, unit_data in self.validation_results.items()
                }
            },
            'overall_results': {
                'total_units': total_units,
                'total_controls': total_controls,
                'working_controls': total_working,
                'overall_success_rate': overall_success_rate,
                'validation_status': validation_status,
                'confidence_level': confidence
            },
            'units_summary': units_summary,
            'detailed_results': self.validation_results,
            'recommendations': {
                'production_ready': overall_success_rate >= 95,
                'needs_investigation': [
                    f"FX{unit}: {', '.join(summary['failed_controls'])}"
                    for unit, summary in units_summary.items()
                    if summary['failed_controls']
                ],
                'next_steps': [
                    "Update traktor_control.py comments" if overall_success_rate >= 95 else "Use MIDI Learn for failed controls",
                    "Test in autonomous DJ mode" if overall_success_rate >= 80 else "Manual testing required"
                ]
            }
        }

        # Save report
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Detailed validation report saved: {report_file}")
        except Exception as e:
            print(f"\n❌ Failed to save report: {e}")

        return report_file

    def run_interactive_validation(self):
        """Run the complete interactive validation process"""
        print("🎛️ INTERACTIVE FX UNITS VALIDATION TOOL")
        print("=" * 60)
        print("🎯 Purpose: Validate FX Units 2, 3, and 4 CC mappings")
        print("📋 Method: Interactive testing with user confirmation")
        print("🔢 Testing: CC 97-104 (FX2), 105-112 (FX3), 113-120 (FX4)")
        print("=" * 60)

        if not RTMIDI_AVAILABLE:
            print("❌ MIDI not available - install python-rtmidi")
            return

        if not self.find_and_connect_iac():
            return

        print(f"\n📋 SETUP INSTRUCTIONS:")
        print("1. ✅ Open Traktor Pro")
        print("2. ✅ Load tracks into decks (for FX to be visible)")
        print("3. ✅ Make sure FX panels are visible in Traktor")
        print("4. ✅ Watch FX Units 2, 3, and 4 during testing")
        print("5. ✅ Confirm when you see controls moving")

        # Wait for user to be ready
        input(f"\n⏸️  Press ENTER when Traktor is ready and you can see FX Units...")

        try:
            # Test each FX unit
            for fx_unit in [2, 3, 4]:
                unit_results = self.test_fx_unit(fx_unit)
                self.validation_results[fx_unit] = unit_results

                if fx_unit < 4:  # Don't pause after the last unit
                    input(f"\n⏭️  Press ENTER to continue to FX Unit {fx_unit + 1}...")

            # Generate final report
            report_file = self.generate_validation_report()

            print(f"\n✅ INTERACTIVE VALIDATION COMPLETED!")
            print(f"📊 Results saved to: {report_file}")
            print(f"🎛️ Thank you for testing the FX Units!")

        except KeyboardInterrupt:
            print(f"\n⏹️  Validation interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during validation: {e}")
        finally:
            if self.midiout.is_port_open():
                self.midiout.close_port()
            print(f"\n🔌 MIDI connection closed")

def main():
    """Main entry point"""
    print("🎛️ Interactive FX Units Validator")
    print("Systematic validation of FX2/3/4 CC mappings with user confirmation")
    print("=" * 70)

    validator = InteractiveFXValidator()
    validator.run_interactive_validation()

if __name__ == "__main__":
    main()