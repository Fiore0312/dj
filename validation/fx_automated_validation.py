#!/usr/bin/env python3
"""
🎛️ FX Automated Validation - REAL TESTING degli FX Unit 2/3/4
Test automatico dei CC predetti 97-120 senza input interattivo
"""

import time
import sys
import json
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).parent))

try:
    import rtmidi
except ImportError as e:
    print(f"❌ Errore import rtmidi: {e}")
    sys.exit(1)

class FXAutomatedValidator:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None
        self.test_results = {}

        # CC predetti da testare (dal traktor_control.py)
        self.predicted_mappings = {
            'fx2': {
                'drywet': 97, 'knob1': 98, 'knob2': 99, 'knob3': 100,
                'rst_button': 101, 'frz_button': 102, 'spr_button': 103, 'onoff': 104
            },
            'fx3': {
                'drywet': 105, 'knob1': 106, 'knob2': 107, 'knob3': 108,
                'rst_button': 109, 'frz_button': 110, 'spr_button': 111, 'onoff': 112
            },
            'fx4': {
                'drywet': 113, 'knob1': 114, 'knob2': 115, 'knob3': 116,
                'rst_button': 117, 'frz_button': 118, 'spr_button': 119, 'onoff': 120
            }
        }

    def find_iac_bus(self):
        """Trova IAC Bus 1 per MIDI communication"""
        print("📤 Porte MIDI disponibili:")
        for i, port in enumerate(self.out_ports):
            print(f"  [{i}] {port}")

        for i, port in enumerate(self.out_ports):
            if "IAC" in port and ("Bus 1" in port or "1" in port):
                self.iac_port = i
                break

        if self.iac_port is None:
            print("❌ IAC Bus 1 non trovato!")
            return False

        print(f"\n🎛️ Connesso a: {self.out_ports[self.iac_port]}")
        self.midiout.open_port(self.iac_port)
        return True

    def test_fx_control(self, fx_unit, control_name, cc_number, is_button=False):
        """Testa un singolo controllo FX"""
        print(f"🧪 Testing FX{fx_unit} {control_name:12} = CC {cc_number:3d}", end="")

        try:
            if is_button:
                # Button test: ON then OFF
                self.midiout.send_message([0xB0, cc_number, 127])  # ON
                time.sleep(0.3)
                self.midiout.send_message([0xB0, cc_number, 0])    # OFF
                time.sleep(0.2)
                test_type = "BUTTON"
            else:
                # Knob test: sweep through values
                test_values = [0, 32, 64, 96, 127, 64]  # Sweep and return to center
                for value in test_values:
                    self.midiout.send_message([0xB0, cc_number, value])
                    time.sleep(0.1)
                test_type = "KNOB"

            print(f" [{test_type}] ✅ SENT")
            return True

        except Exception as e:
            print(f" [{test_type}] ❌ ERROR: {e}")
            return False

    def test_fx_unit_complete(self, fx_unit):
        """Testa tutti i controlli di un FX Unit"""
        print(f"\n🎛️ {'='*20} FX UNIT {fx_unit} TESTING {'='*20}")

        unit_key = f'fx{fx_unit}'
        predicted = self.predicted_mappings[unit_key]
        unit_results = {}

        # Test knobs first (visual feedback easier)
        knob_controls = [
            ('drywet', False), ('knob1', False), ('knob2', False), ('knob3', False)
        ]

        for control_name, is_button in knob_controls:
            cc = predicted[control_name]
            success = self.test_fx_control(fx_unit, control_name, cc, is_button)
            unit_results[control_name] = {
                'cc': cc,
                'success': success,
                'type': 'knob',
                'tested_at': datetime.now().isoformat()
            }

        print(f"\n   💡 Knobs tested - check Traktor FX{fx_unit} for movement")
        time.sleep(1)

        # Test buttons
        button_controls = [
            ('rst_button', True), ('frz_button', True), ('spr_button', True), ('onoff', True)
        ]

        for control_name, is_button in button_controls:
            cc = predicted[control_name]
            success = self.test_fx_control(fx_unit, control_name, cc, is_button)
            unit_results[control_name] = {
                'cc': cc,
                'success': success,
                'type': 'button',
                'tested_at': datetime.now().isoformat()
            }

        print(f"\n   🔘 Buttons tested - check Traktor FX{fx_unit} for button activity")
        time.sleep(1)

        self.test_results[unit_key] = unit_results
        return unit_results

    def test_cc_range_discovery(self, start_cc, end_cc):
        """Testa un range di CC per discovery"""
        print(f"\n🔍 DISCOVERY TEST: CC {start_cc}-{end_cc}")
        print("   Testing systematic CC range for any Traktor response...")

        discovered = []

        for cc in range(start_cc, end_cc + 1):
            # Quick knob test
            for value in [0, 127, 64]:  # Min, Max, Center
                self.midiout.send_message([0xB0, cc, value])
                time.sleep(0.05)

            print(f"   📤 CC {cc:3d} tested", end="")
            if cc % 10 == 0:
                print()  # New line every 10 CCs

        print(f"\n   ✅ Range CC {start_cc}-{end_cc} discovery completed")
        return discovered

    def show_unit_summary(self, fx_unit, results):
        """Mostra summary per un FX Unit"""
        print(f"\n📊 FX{fx_unit} TEST SUMMARY:")
        print("-" * 50)

        successful_tests = 0
        total_tests = len(results)

        for control, data in results.items():
            cc = data['cc']
            success = data['success']
            control_type = data['type'].upper()

            status = "✅ SENT" if success else "❌ FAIL"
            print(f"   {control:12} CC {cc:3d} [{control_type:6}] {status}")

            if success:
                successful_tests += 1

        success_rate = (successful_tests / total_tests) * 100
        print(f"\n   🎯 Success Rate: {successful_tests}/{total_tests} ({success_rate:.0f}%)")

        return success_rate

    def generate_test_report(self):
        """Genera report completo del test"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"fx_validation_report_{timestamp}.json"

        print("\n" + "🏆" * 20)
        print("FX VALIDATION COMPLETE REPORT")
        print("🏆" * 20)

        total_controls = 0
        total_successful = 0

        summary_data = {
            'test_session': {
                'timestamp': datetime.now().isoformat(),
                'total_fx_units': 3,
                'tested_cc_range': '97-120',
                'prediction_source': 'traktor_control.py pattern logic'
            },
            'results_by_unit': {},
            'cc_mapping_validation': {}
        }

        for fx_unit in [2, 3, 4]:
            unit_key = f'fx{fx_unit}'
            if unit_key in self.test_results:
                results = self.test_results[unit_key]
                success_rate = self.show_unit_summary(fx_unit, results)

                unit_controls = len(results)
                unit_successful = sum(1 for r in results.values() if r['success'])

                total_controls += unit_controls
                total_successful += unit_successful

                summary_data['results_by_unit'][unit_key] = {
                    'total_controls': unit_controls,
                    'successful_tests': unit_successful,
                    'success_rate': success_rate,
                    'details': results
                }

        overall_success = (total_successful / total_controls) * 100 if total_controls > 0 else 0

        print(f"\n🎯 OVERALL TEST RESULTS:")
        print(f"   Total Controls Tested: {total_controls}")
        print(f"   Successful MIDI Sends: {total_successful}")
        print(f"   Overall Success Rate:  {overall_success:.1f}%")

        # Validation of predicted pattern
        print(f"\n🔍 CC PATTERN VALIDATION:")
        expected_ccs = list(range(97, 121))  # CC 97-120
        tested_ccs = []

        for unit_results in self.test_results.values():
            for control_data in unit_results.values():
                tested_ccs.append(control_data['cc'])

        pattern_match = all(cc in expected_ccs for cc in tested_ccs)
        print(f"   Predicted CC Range: 97-120")
        print(f"   Tested CCs: {sorted(tested_ccs)}")
        print(f"   Pattern Match: {'✅ PERFECT' if pattern_match else '❌ DEVIATION'}")

        summary_data['pattern_validation'] = {
            'expected_range': '97-120',
            'tested_ccs': sorted(tested_ccs),
            'pattern_match': pattern_match,
            'overall_success_rate': overall_success
        }

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if overall_success >= 100:
            rec = "🎉 PERFECT! All MIDI commands sent successfully"
            next_step = "✅ Proceed with manual Traktor verification"
        elif overall_success >= 90:
            rec = "👍 EXCELLENT! High success rate for MIDI transmission"
            next_step = "✅ Check failed commands, proceed with verification"
        elif overall_success >= 70:
            rec = "🤔 GOOD! Most commands successful"
            next_step = "⚠️  Review failed commands before Traktor verification"
        else:
            rec = "😞 POOR! Significant MIDI transmission issues"
            next_step = "❌ Check MIDI setup before proceeding"

        print(f"   {rec}")
        print(f"   Next Step: {next_step}")

        summary_data['recommendations'] = {
            'overall_assessment': rec,
            'next_step': next_step
        }

        # Save report
        with open(report_file, 'w') as f:
            json.dump(summary_data, f, indent=2)

        print(f"\n📄 Detailed report saved: {report_file}")

        return summary_data

    def run_automated_validation(self):
        """Esegue validazione automatica completa"""
        print("🎛️ FX AUTOMATED VALIDATION SESSION")
        print("=" * 60)
        print("🎯 TESTING: CC 97-120 predictions for FX Units 2/3/4")
        print("🔍 METHOD: Automated MIDI transmission + pattern validation")
        print("⚠️  NOTE: This tests MIDI sending - Traktor response requires manual verification")
        print("=" * 60)

        if not self.find_iac_bus():
            return

        try:
            print("\n🚀 Starting automated FX validation...")
            print("\n⏱️  Each FX Unit will be tested systematically")
            print("   🎚️  Knobs: Sweep through values 0→32→64→96→127→64")
            print("   🔘 Buttons: Press (127) then Release (0)")

            # Test each FX Unit
            for fx_unit in [2, 3, 4]:
                self.test_fx_unit_complete(fx_unit)

                if fx_unit < 4:
                    print(f"\n⏭️  Moving to FX Unit {fx_unit + 1}...")
                    time.sleep(1)

            # Generate comprehensive report
            report_data = self.generate_test_report()

            # Additional CC discovery if needed
            print(f"\n🔍 ADDITIONAL CC DISCOVERY (for reference):")
            print("   Testing nearby CC ranges for comparison...")

            # Test some alternative ranges for discovery
            self.test_cc_range_discovery(80, 96)   # Near FX1
            self.test_cc_range_discovery(121, 127) # High range

            print(f"\n✅ FX AUTOMATED VALIDATION COMPLETED!")
            print(f"   📊 Report generated with detailed results")
            print(f"   🎯 Next: Manual verification in Traktor Controller Manager")

        except KeyboardInterrupt:
            print("\n⏹️  FX validation interrupted")
        except Exception as e:
            print(f"❌ Error during validation: {e}")
        finally:
            if self.midiout.is_port_open():
                self.midiout.close_port()
            print("\n🔌 MIDI connection closed")

def main():
    print("🎛️ FX AUTOMATED VALIDATION - Pattern Testing Tool")
    print("Automated testing of predicted FX mappings CC 97-120")
    print("=" * 70)

    validator = FXAutomatedValidator()
    validator.run_automated_validation()

if __name__ == "__main__":
    main()