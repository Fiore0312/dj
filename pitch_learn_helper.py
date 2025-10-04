#!/usr/bin/env python3
"""
🎛️ Pitch Learn Helper - Automated CC Sender for Traktor Controller Manager
Interactive Learn session for Pitch controls across all 4 decks
"""

import time
import rtmidi

class PitchLearnHelper:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None

        # Known Pitch CC mappings (from discovery)
        self.known_mappings = {
            'deck_a_pitch': 41,    # Confirmed working
            'deck_b_pitch': 40,    # Confirmed working
        }

        # Suggested mappings for Deck C & D (following pattern analysis)
        # Note: Deck B is 40, Deck A is 41 - suggests reverse order pattern
        # Continuing this pattern: C=39, D=38 OR C=42, D=43
        # We'll try the ascending pattern first: C=42, D=43
        self.suggested_mappings = {
            'deck_c_pitch': 42,    # Following ascending pattern
            'deck_d_pitch': 43,    # Following ascending pattern
        }

        # Alternative suggestions in case first pattern fails
        self.alternative_mappings = {
            'deck_c_pitch_alt': 39,    # Reverse pattern option
            'deck_d_pitch_alt': 38,    # Reverse pattern option
        }

        # Combine primary mappings
        self.all_mappings = {**self.known_mappings, **self.suggested_mappings}

        # Control descriptions for user interface
        self.control_descriptions = {
            'deck_a_pitch': 'Deck A Pitch Fader/Knob',
            'deck_b_pitch': 'Deck B Pitch Fader/Knob',
            'deck_c_pitch': 'Deck C Pitch Fader/Knob',
            'deck_d_pitch': 'Deck D Pitch Fader/Knob'
        }

        # Traktor paths for Controller Manager
        self.traktor_paths = {
            'deck_a_pitch': 'Deck A > Pitch Fader',
            'deck_b_pitch': 'Deck B > Pitch Fader',
            'deck_c_pitch': 'Deck C > Pitch Fader',
            'deck_d_pitch': 'Deck D > Pitch Fader'
        }

        # Control status (known vs suggested)
        self.control_status = {
            'deck_a_pitch': 'KNOWN ✅',
            'deck_b_pitch': 'KNOWN ✅',
            'deck_c_pitch': 'SUGGESTED 🔍',
            'deck_d_pitch': 'SUGGESTED 🔍'
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

    def configure_pitch_controls(self):
        """Interactive Learn session for all Pitch controls"""
        print("🎛️ PITCH LEARN HELPER")
        print("=" * 70)
        print("🎯 OBJECTIVE: Configure Pitch faders for all 4 decks")
        print("📊 TOTAL CONTROLS: 4 (1 per deck)")
        print("🔢 CC RANGE: 40-43 (primary pattern)")
        print("=" * 70)

        print(f"\n📋 CONTROL OVERVIEW:")
        print("   PITCH FADER PATTERN ANALYSIS:")
        print("   • Deck A Pitch: CC 41 ✅ (Known)")
        print("   • Deck B Pitch: CC 40 ✅ (Known)")
        print("   • Deck C Pitch: CC 42 🔍 (Suggested - ascending pattern)")
        print("   • Deck D Pitch: CC 43 🔍 (Suggested - ascending pattern)")
        print()
        print("   💡 PATTERN NOTE: B=40, A=41 suggests unconventional order")
        print("   📊 Alternative CCs available if primary fails: 39, 38")

        print(f"\n📋 PRE-CONFIGURATION CHECKLIST:")
        print("✅ 1. Traktor Pro 3 is open")
        print("✅ 2. Controller Manager is open (Preferences > Controller Manager)")
        print("✅ 3. Your controller device is selected")
        print("✅ 4. All 4 decks are visible in Traktor interface")
        print("✅ 5. Pitch faders are visible and accessible")
        print("✅ 6. IAC Bus 1 is configured and online")

        if not self.connect_midi():
            return

        input(f"\n⏸️  Press ENTER to begin Pitch configuration...")

        success_count = 0
        total_controls = len(self.all_mappings)

        # Configure controls in logical deck order
        deck_order = ['deck_a_pitch', 'deck_b_pitch', 'deck_c_pitch', 'deck_d_pitch']

        for control_name in deck_order:
            cc = self.all_mappings[control_name]
            success = self.configure_single_pitch_control(control_name, cc)
            if success:
                success_count += 1
            elif control_name in ['deck_c_pitch', 'deck_d_pitch']:
                # Try alternative CC for suggested mappings
                success = self.try_alternative_cc(control_name)
                if success:
                    success_count += 1

        # Final summary
        print(f"\n🏆{'='*60}🏆")
        print("PITCH CONFIGURATION SESSION RESULTS")
        print(f"🏆{'='*60}🏆")

        success_rate = (success_count / total_controls) * 100
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Controls Configured: {success_count}/{total_controls}")
        print(f"   Success Rate: {success_rate:.1f}%")

        if success_rate >= 95:
            status = "🎉 EXCELLENT - All pitch controls working!"
        elif success_rate >= 75:
            status = "✅ GOOD - Most pitch controls working"
        elif success_rate >= 50:
            status = "⚠️ PARTIAL - Some pitch controls working"
        else:
            status = "❌ POOR - Major issues detected"

        print(f"   Status: {status}")

        # Generate code for traktor_control.py
        self.generate_traktor_control_code()

        print(f"\n🎵 PITCH CONTROL TESTING TIPS:")
        print("   • Test with small pitch adjustments (+/- 2-5%)")
        print("   • Verify smooth fader response across full range")
        print("   • Check pitch display updates in Traktor interface")
        print("   • Test pitch reset (center position)")

        print(f"\n💾 SAVE REMINDER:")
        print("   Don't forget to EXPORT your TSI file in Controller Manager!")
        print("   Recommended filename: Pitch_Mapping_40-43.tsi")

    def configure_single_pitch_control(self, control_name, cc):
        """Configure a single Pitch control"""
        print(f"\n🎚️ MAPPING: {self.control_descriptions[control_name]}")
        print(f"   🎯 Target: {self.traktor_paths[control_name]}")
        print(f"   📡 CC: {cc}")
        print(f"   📊 Status: {self.control_status[control_name]}")

        # Special note for suggested mappings
        if 'SUGGESTED' in self.control_status[control_name]:
            print(f"   💡 This is a pattern-based suggestion - may need adjustment")

        # Instructions for Traktor
        print(f"\n📋 TRAKTOR STEPS:")
        print(f"   1. Click 'Learn' in Controller Manager")
        print(f"   2. Navigate to: {self.traktor_paths[control_name]}")
        print(f"   3. Press ENTER below to send CC {cc}")

        input(f"   ⏸️  Ready to send CC {cc}? Press ENTER...")

        # Send fader value (64 = center position for pitch faders)
        value = 64
        print(f"   📤 Sending: CC {cc} = {value} (CENTER POSITION)")

        success = self.send_cc(cc, value)

        if success:
            print(f"   ✅ CC {cc} sent successfully")

            # User confirmation with retry option
            while True:
                result = input(f"   ❓ Mapping confirmed in Traktor? (y/n/r=retry): ").lower().strip()

                if result == 'y':
                    print(f"   🎉 {control_name} configured successfully!")
                    # Test pitch range
                    self.test_pitch_range(cc, control_name)
                    return True
                elif result == 'n':
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

    def try_alternative_cc(self, control_name):
        """Try alternative CC suggestions for failed mappings"""
        if control_name == 'deck_c_pitch':
            alt_cc = self.alternative_mappings['deck_c_pitch_alt']
        elif control_name == 'deck_d_pitch':
            alt_cc = self.alternative_mappings['deck_d_pitch_alt']
        else:
            return False

        print(f"\n🔄 TRYING ALTERNATIVE CC FOR {control_name.upper()}")
        print(f"   📡 Alternative CC: {alt_cc}")
        print(f"   💡 This follows the reverse pattern (B=40, A=41, C=39, D=38)")

        retry = input(f"   ❓ Try alternative CC {alt_cc}? (y/n): ").lower().strip()
        if retry != 'y':
            return False

        # Update mapping for this session
        self.all_mappings[control_name] = alt_cc

        # Try configuration with alternative CC
        return self.configure_single_pitch_control(control_name, alt_cc)

    def test_pitch_range(self, cc, control_name):
        """Test pitch fader range after successful mapping"""
        print(f"   🧪 Testing pitch range for {control_name}...")

        test_values = [
            (0, "Maximum Pitch Down"),
            (32, "Half Pitch Down"),
            (64, "Center Position"),
            (96, "Half Pitch Up"),
            (127, "Maximum Pitch Up")
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

        # Generate pitch methods
        print("# Pitch Control Methods")
        for control_name, cc in self.all_mappings.items():
            deck = control_name.split('_')[1].upper()
            method_name = f"set_pitch_deck_{deck.lower()}"
            print(f"def {method_name}(self, pitch_value):")
            print(f'    """Set pitch for Deck {deck} (0-127, 64=center)"""')
            print(f"    return self.send_cc({cc}, pitch_value)  # CC {cc}")
            print()

        # Generate convenience methods
        print("# Convenience Methods")
        print("def reset_all_pitch(self):")
        print('    """Reset all deck pitches to center position"""')
        print("    results = []")
        for control_name, cc in self.all_mappings.items():
            deck = control_name.split('_')[1].lower()
            print(f"    results.append(self.set_pitch_deck_{deck}(64))  # Center")
        print("    return all(results)")
        print()

        print("def fine_pitch_up(self, deck, amount=2):")
        print('    """Fine pitch adjustment up"""')
        print("    # Implementation depends on current pitch reading")
        print("    pass")
        print()

        print("def fine_pitch_down(self, deck, amount=2):")
        print('    """Fine pitch adjustment down"""')
        print("    # Implementation depends on current pitch reading")
        print("    pass")

    def quick_test_pitch(self):
        """Quick test all Pitch controls"""
        print("🧪 QUICK TEST: All Pitch Controls")
        print("=" * 50)

        if not self.connect_midi():
            return

        print("\n🎵 Testing PITCH faders...")
        for control_name, cc in self.all_mappings.items():
            print(f"   📤 {control_name}: CC {cc}")

            # Test sequence: center -> up -> down -> center
            test_sequence = [64, 96, 32, 64]
            descriptions = ["Center", "Pitch Up", "Pitch Down", "Center"]

            for value, desc in zip(test_sequence, descriptions):
                print(f"      {desc}: {value}")
                self.send_cc(cc, value)
                time.sleep(0.4)

        print(f"\n✅ Quick test completed - check Traktor pitch displays")

def main():
    print("🎛️ Pitch Learn Helper")
    print("Configure Pitch faders for all 4 decks in Traktor Pro 3")
    print("=" * 60)
    print("Available modes:")
    print("1. Interactive Learn Configuration Session")
    print("2. Quick Test All Pitch Controls")
    print("3. Exit")

    choice = input("\nEnter choice (1/2/3): ").strip()

    helper = PitchLearnHelper()

    if choice == "1":
        helper.configure_pitch_controls()
    elif choice == "2":
        helper.quick_test_pitch()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()