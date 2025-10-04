#!/usr/bin/env python3
"""
🎛️ Tempo Adjust Learn Helper - TSI Confirmed CC Mappings
Interactive Learn session for Tempo Adjust controls across all 4 decks
Updated with TSI confirmed mappings (2025-10-04)
"""

import time
import rtmidi

class TempoAdjustLearnHelper:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None

        # TSI CONFIRMED MAPPINGS (2025-10-04)
        self.confirmed_mappings = {
            'deck_a_tempo_adjust': 41,  # Legacy confirmed (pitch fader)
            'deck_b_tempo_adjust': 40,  # Legacy confirmed (pitch fader)
            'deck_c_tempo_adjust': 2,   # TSI CONFIRMED
            'deck_d_tempo_adjust': 3,   # TSI CONFIRMED
        }

        # Control descriptions for user interface
        self.control_descriptions = {
            'deck_a_tempo_adjust': 'Deck A Tempo Adjust/Pitch Fader',
            'deck_b_tempo_adjust': 'Deck B Tempo Adjust/Pitch Fader',
            'deck_c_tempo_adjust': 'Deck C Tempo Adjust/Pitch Fader',
            'deck_d_tempo_adjust': 'Deck D Tempo Adjust/Pitch Fader'
        }

        # Traktor paths for Controller Manager
        self.traktor_paths = {
            'deck_a_tempo_adjust': 'Deck A > Tempo Adjust',
            'deck_b_tempo_adjust': 'Deck B > Tempo Adjust',
            'deck_c_tempo_adjust': 'Deck C > Tempo Adjust',
            'deck_d_tempo_adjust': 'Deck D > Tempo Adjust'
        }

        # Control status (known vs TSI confirmed)
        self.control_status = {
            'deck_a_tempo_adjust': 'LEGACY CONFIRMED ✅',
            'deck_b_tempo_adjust': 'LEGACY CONFIRMED ✅',
            'deck_c_tempo_adjust': 'TSI CONFIRMED ✅',
            'deck_d_tempo_adjust': 'TSI CONFIRMED ✅'
        }

        # Special notes for TSI confirmed mappings
        self.tsi_notes = {
            'deck_c_tempo_adjust': 'Confirmed via TSI analysis - deck isolation prevents hotcue conflicts',
            'deck_d_tempo_adjust': 'Confirmed via TSI analysis - deck isolation prevents hotcue conflicts'
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

    def configure_tempo_adjust_controls(self):
        """Interactive Learn session for all Tempo Adjust controls"""
        print("🎛️ TEMPO ADJUST LEARN HELPER")
        print("=" * 70)
        print("🎯 OBJECTIVE: Configure Tempo Adjust faders for all 4 decks")
        print("📊 TOTAL CONTROLS: 4 (1 per deck)")
        print("🔢 CC RANGE: Mixed (Legacy: 40-41, TSI: 2-3)")
        print("📄 TSI ANALYSIS: Updated 2025-10-04")
        print("=" * 70)

        print(f"\n📋 CONTROL OVERVIEW:")
        print("   TEMPO ADJUST PATTERN ANALYSIS:")
        print("   • Deck A Tempo: CC 41 ✅ (Legacy Confirmed)")
        print("   • Deck B Tempo: CC 40 ✅ (Legacy Confirmed)")
        print("   • Deck C Tempo: CC 2  ✅ (TSI CONFIRMED)")
        print("   • Deck D Tempo: CC 3  ✅ (TSI CONFIRMED)")
        print()
        print("   💡 PATTERN NOTE: Mixed pattern due to incremental discovery")
        print("   📊 TSI CONFIRMED: Decks C & D validated via TSI file analysis")
        print("   🛡️ CONFLICT STATUS: Deck isolation prevents hotcue conflicts")

        print(f"\n📋 PRE-CONFIGURATION CHECKLIST:")
        print("✅ 1. Traktor Pro 3 is open")
        print("✅ 2. Controller Manager is open (Preferences > Controller Manager)")
        print("✅ 3. Your controller device is selected")
        print("✅ 4. All 4 decks are visible in Traktor interface")
        print("✅ 5. Tempo faders are visible and accessible")
        print("✅ 6. IAC Bus 1 is configured and online")
        print("✅ 7. TSI analysis completed (2025-10-04)")

        if not self.connect_midi():
            return

        input(f"\n⏸️  Press ENTER to begin Tempo Adjust configuration...")

        success_count = 0
        total_controls = len(self.confirmed_mappings)

        # Configure controls in logical deck order
        deck_order = ['deck_a_tempo_adjust', 'deck_b_tempo_adjust', 'deck_c_tempo_adjust', 'deck_d_tempo_adjust']

        for control_name in deck_order:
            cc = self.confirmed_mappings[control_name]
            success = self.configure_single_tempo_control(control_name, cc)
            if success:
                success_count += 1

        # Final summary
        print(f"\n🏆{'='*60}🏆")
        print("TEMPO ADJUST CONFIGURATION SESSION RESULTS")
        print(f"🏆{'='*60}🏆")

        success_rate = (success_count / total_controls) * 100
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Controls Configured: {success_count}/{total_controls}")
        print(f"   Success Rate: {success_rate:.1f}%")

        if success_rate >= 95:
            status = "🎉 EXCELLENT - All tempo controls working!"
        elif success_rate >= 75:
            status = "✅ GOOD - Most tempo controls working"
        elif success_rate >= 50:
            status = "⚠️ PARTIAL - Some tempo controls working"
        else:
            status = "❌ POOR - Major issues detected"

        print(f"   Status: {status}")

        # Generate code for traktor_control.py
        self.generate_traktor_control_code()

        print(f"\n🎵 TEMPO CONTROL TESTING TIPS:")
        print("   • Test with small tempo adjustments (+/- 2-5%)")
        print("   • Verify smooth fader response across full range")
        print("   • Check tempo display updates in Traktor interface")
        print("   • Test tempo reset (center position)")

        print(f"\n💾 SAVE REMINDER:")
        print("   TSI mappings already confirmed via file analysis!")
        print("   Current TSI file contains validated mappings.")

    def configure_single_tempo_control(self, control_name, cc):
        """Configure a single Tempo Adjust control"""
        print(f"\n🎚️ MAPPING: {self.control_descriptions[control_name]}")
        print(f"   🎯 Target: {self.traktor_paths[control_name]}")
        print(f"   📡 CC: {cc}")
        print(f"   📊 Status: {self.control_status[control_name]}")

        # Special note for TSI confirmed mappings
        if 'TSI CONFIRMED' in self.control_status[control_name]:
            print(f"   🔍 TSI Note: {self.tsi_notes[control_name]}")
            print(f"   ✅ This mapping is already validated and functional")

        # Instructions for Traktor
        print(f"\n📋 TRAKTOR STEPS:")
        if 'TSI CONFIRMED' in self.control_status[control_name]:
            print(f"   💡 OPTIONAL: This mapping is already in your TSI file")
            print(f"   1. Test current functionality OR")
            print(f"   2. Re-learn if you want to verify: Click 'Learn' in Controller Manager")
            print(f"   3. Navigate to: {self.traktor_paths[control_name]}")
        else:
            print(f"   1. Click 'Learn' in Controller Manager")
            print(f"   2. Navigate to: {self.traktor_paths[control_name]}")

        print(f"   3. Press ENTER below to send CC {cc}")

        input(f"   ⏸️  Ready to send CC {cc}? Press ENTER...")

        # Send fader value (64 = center position for tempo faders)
        value = 64
        print(f"   📤 Sending: CC {cc} = {value} (CENTER POSITION)")

        success = self.send_cc(cc, value)

        if success:
            print(f"   ✅ CC {cc} sent successfully")

            # User confirmation with retry option
            while True:
                if 'TSI CONFIRMED' in self.control_status[control_name]:
                    result = input(f"   ❓ Control response confirmed? (y/n/r=retry): ").lower().strip()
                else:
                    result = input(f"   ❓ Mapping confirmed in Traktor? (y/n/r=retry): ").lower().strip()

                if result == 'y':
                    print(f"   🎉 {control_name} validated successfully!")
                    # Test tempo range
                    self.test_tempo_range(cc, control_name)
                    return True
                elif result == 'n':
                    if 'TSI CONFIRMED' in self.control_status[control_name]:
                        print(f"   ⚠️  {control_name} TSI mapping needs verification")
                    else:
                        print(f"   ⚠️  {control_name} failed - may need manual configuration")
                    return False
                elif result == 'r':
                    print(f"   🔄 Retrying CC {cc}...")
                    self.send_cc(cc, value)
                else:
                    print(f"   ⚠️  Please enter 'y', 'n', or 'r'")
        else:
            print(f"   ❌ Failed to send CC {cc}")
            return False

    def test_tempo_range(self, cc, control_name):
        """Test tempo fader range after successful mapping"""
        print(f"   🧪 Testing tempo range for {control_name}...")

        test_values = [
            (0, "Maximum Tempo Down"),
            (32, "Half Tempo Down"),
            (64, "Center Position"),
            (96, "Half Tempo Up"),
            (127, "Maximum Tempo Up")
        ]

        for value, description in test_values:
            print(f"   📤 {description}: CC {cc} = {value}")
            self.send_cc(cc, value)
            time.sleep(0.4)

        # Return to center
        self.send_cc(cc, 64)
        print(f"   🎯 Returned to center position")

    def generate_traktor_control_code(self):
        """Generate Python code for traktor_control.py integration"""
        print(f"\n💻 TRAKTOR_CONTROL.PY INTEGRATION CODE:")
        print("=" * 50)
        print("# Add these methods to your TraktorControl class:")
        print()

        # Generate tempo methods
        print("# Tempo Adjust Control Methods")
        for control_name, cc in self.confirmed_mappings.items():
            deck = control_name.split('_')[1].upper()
            method_name = f"set_tempo_deck_{deck.lower()}"
            status = "TSI CONFIRMED" if 'TSI CONFIRMED' in self.control_status[control_name] else "LEGACY"
            print(f"def {method_name}(self, tempo_value):")
            print(f'    """Set tempo for Deck {deck} (0-127, 64=center) - {status}"""')
            print(f"    return self.send_cc({cc}, tempo_value)  # CC {cc}")
            print()

        # Generate convenience methods
        print("# Convenience Methods")
        print("def reset_all_tempo(self):")
        print('    """Reset all deck tempos to center position"""')
        print("    results = []")
        for control_name, cc in self.confirmed_mappings.items():
            deck = control_name.split('_')[1].lower()
            print(f"    results.append(self.set_tempo_deck_{deck}(64))  # Center")
        print("    return all(results)")
        print()

        print("def fine_tempo_up(self, deck, amount=2):")
        print('    """Fine tempo adjustment up"""')
        print("    # Implementation depends on current tempo reading")
        print("    pass")
        print()

        print("def fine_tempo_down(self, deck, amount=2):")
        print('    """Fine tempo adjustment down"""')
        print("    # Implementation depends on current tempo reading")
        print("    pass")

    def quick_test_tempo_adjust(self):
        """Quick test all Tempo Adjust controls"""
        print("🧪 QUICK TEST: All Tempo Adjust Controls")
        print("=" * 50)

        if not self.connect_midi():
            return

        print("\n🎵 Testing TEMPO ADJUST faders...")
        for control_name, cc in self.confirmed_mappings.items():
            status = self.control_status[control_name]
            print(f"   📤 {control_name}: CC {cc} ({status})")

            # Test sequence: center -> up -> down -> center
            test_sequence = [64, 96, 32, 64]
            descriptions = ["Center", "Tempo Up", "Tempo Down", "Center"]

            for value, desc in zip(test_sequence, descriptions):
                print(f"      {desc}: {value}")
                self.send_cc(cc, value)
                time.sleep(0.4)

        print(f"\n✅ Quick test completed - check Traktor tempo displays")

    def validate_tsi_mappings(self):
        """Validate TSI confirmed mappings specifically"""
        print("🔍 TSI MAPPING VALIDATION")
        print("=" * 50)

        tsi_mappings = {k: v for k, v in self.confirmed_mappings.items()
                       if 'TSI CONFIRMED' in self.control_status[k]}

        if not tsi_mappings:
            print("ℹ️ No TSI confirmed mappings to validate")
            return

        if not self.connect_midi():
            return

        print(f"\n📊 Validating {len(tsi_mappings)} TSI confirmed mappings...")

        for control_name, cc in tsi_mappings.items():
            print(f"\n🔍 {control_name}: CC {cc}")
            print(f"   Note: {self.tsi_notes[control_name]}")

            # Quick test
            self.send_cc(cc, 64)
            time.sleep(0.2)
            self.send_cc(cc, 96)
            time.sleep(0.2)
            self.send_cc(cc, 64)

        print(f"\n✅ TSI validation test completed")

def main():
    print("🎛️ Tempo Adjust Learn Helper")
    print("Configure Tempo Adjust faders for all 4 decks in Traktor Pro 3")
    print("Updated with TSI confirmed mappings (2025-10-04)")
    print("=" * 60)
    print("Available modes:")
    print("1. Interactive Learn Configuration Session")
    print("2. Quick Test All Tempo Adjust Controls")
    print("3. Validate TSI Confirmed Mappings Only")
    print("4. Exit")

    choice = input("\nEnter choice (1/2/3/4): ").strip()

    helper = TempoAdjustLearnHelper()

    if choice == "1":
        helper.configure_tempo_adjust_controls()
    elif choice == "2":
        helper.quick_test_tempo_adjust()
    elif choice == "3":
        helper.validate_tsi_mappings()
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()