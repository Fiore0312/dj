#!/usr/bin/env python3
"""
🎛️ Loop Learn Helper - Interactive Learn Session for Traktor Controller Manager
Configure Loop controls using Learn mode for all 4 decks
"""

import time
import rtmidi

class LoopLearnHelper:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None

        # Suggested CC mappings for Loop controls (based on existing patterns)
        self.suggested_mappings = {
            # Deck A Loop Controls
            'deck_a_loop_in': 121,
            'deck_a_loop_out': 122,
            'deck_a_loop_active': 123,

            # Deck B Loop Controls
            'deck_b_loop_in': 124,
            'deck_b_loop_out': 125,
            'deck_b_loop_active': 126,

            # Deck C Loop Controls (new suggestions)
            'deck_c_loop_in': 53,
            'deck_c_loop_out': 54,
            'deck_c_loop_active': 55,

            # Deck D Loop Controls (new suggestions)
            'deck_d_loop_in': 56,
            'deck_d_loop_out': 57,
            'deck_d_loop_active': 58
        }

        # Control descriptions for user interface
        self.control_descriptions = {
            'deck_a_loop_in': 'Deck A Loop In Point',
            'deck_a_loop_out': 'Deck A Loop Out Point',
            'deck_a_loop_active': 'Deck A Loop Active Toggle',
            'deck_b_loop_in': 'Deck B Loop In Point',
            'deck_b_loop_out': 'Deck B Loop Out Point',
            'deck_b_loop_active': 'Deck B Loop Active Toggle',
            'deck_c_loop_in': 'Deck C Loop In Point',
            'deck_c_loop_out': 'Deck C Loop Out Point',
            'deck_c_loop_active': 'Deck C Loop Active Toggle',
            'deck_d_loop_in': 'Deck D Loop In Point',
            'deck_d_loop_out': 'Deck D Loop Out Point',
            'deck_d_loop_active': 'Deck D Loop Active Toggle'
        }

        # Traktor paths for Controller Manager
        self.traktor_paths = {
            'deck_a_loop_in': 'Deck A > Loop In',
            'deck_a_loop_out': 'Deck A > Loop Out',
            'deck_a_loop_active': 'Deck A > Loop Active',
            'deck_b_loop_in': 'Deck B > Loop In',
            'deck_b_loop_out': 'Deck B > Loop Out',
            'deck_b_loop_active': 'Deck B > Loop Active',
            'deck_c_loop_in': 'Deck C > Loop In',
            'deck_c_loop_out': 'Deck C > Loop Out',
            'deck_c_loop_active': 'Deck C > Loop Active',
            'deck_d_loop_in': 'Deck D > Loop In',
            'deck_d_loop_out': 'Deck D > Loop Out',
            'deck_d_loop_active': 'Deck D > Loop Active'
        }

        # Control status and grouping
        self.control_status = {
            'deck_a_loop_in': 'SUGGESTED ✅',
            'deck_a_loop_out': 'SUGGESTED ✅',
            'deck_a_loop_active': 'SUGGESTED ✅',
            'deck_b_loop_in': 'SUGGESTED ✅',
            'deck_b_loop_out': 'SUGGESTED ✅',
            'deck_b_loop_active': 'SUGGESTED ✅',
            'deck_c_loop_in': 'NEW 🔍',
            'deck_c_loop_out': 'NEW 🔍',
            'deck_c_loop_active': 'NEW 🔍',
            'deck_d_loop_in': 'NEW 🔍',
            'deck_d_loop_out': 'NEW 🔍',
            'deck_d_loop_active': 'NEW 🔍'
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

    def send_cc(self, cc, value=127):
        """Send MIDI CC on channel 1"""
        try:
            message = [0xB0, cc, value]  # Channel 1, CC, Value
            self.midiout.send_message(message)
            return True
        except Exception as e:
            print(f"❌ MIDI error: {e}")
            return False

    def configure_deck_loop_controls(self, deck):
        """Configure all loop controls for a specific deck"""
        deck_controls = {k: v for k, v in self.suggested_mappings.items() if k.startswith(f'deck_{deck}_')}

        print(f"\n{'='*60}")
        print(f"🎛️ CONFIGURING DECK {deck.upper()} LOOP CONTROLS")
        print(f"{'='*60}")

        cc_range = f"CC {min(deck_controls.values())}-{max(deck_controls.values())}"
        print(f"📍 CC Range: {cc_range}")
        print(f"📋 Controls to map: {len(deck_controls)}")

        # Wait for user readiness
        input(f"\n⏸️  Ensure Deck {deck.upper()} is visible with loop controls. Press ENTER to continue...")

        success_count = 0

        # Configure in logical order: In -> Out -> Active
        control_order = ['loop_in', 'loop_out', 'loop_active']

        for control_type in control_order:
            control_name = f"deck_{deck}_{control_type}"
            if control_name in deck_controls:
                cc = deck_controls[control_name]
                success = self.configure_single_loop_control(control_name, cc)
                if success:
                    success_count += 1

        # Deck summary
        print(f"\n📊 DECK {deck.upper()} LOOP CONFIGURATION SUMMARY:")
        print(f"   Successful mappings: {success_count}/{len(deck_controls)}")

        if success_count == len(deck_controls):
            print(f"   🎉 PERFECT! All Deck {deck.upper()} loop controls configured")
        elif success_count >= len(deck_controls) * 0.66:
            print(f"   ✅ GOOD! Most Deck {deck.upper()} loop controls working")
        else:
            print(f"   ⚠️  PARTIAL: Some Deck {deck.upper()} loop controls need attention")

        return success_count

    def configure_single_loop_control(self, control_name, cc):
        """Configure a single Loop control"""
        print(f"\n🎚️ MAPPING: {self.control_descriptions[control_name]}")
        print(f"   🎯 Target: {self.traktor_paths[control_name]}")
        print(f"   📡 CC: {cc}")
        print(f"   📊 Status: {self.control_status[control_name]}")

        # Control type specific instructions
        control_type = control_name.split('_')[-1]
        if control_type == 'in':
            print(f"   💡 Loop In: Sets the start point of the loop")
        elif control_type == 'out':
            print(f"   💡 Loop Out: Sets end point and activates loop")
        elif control_type == 'active':
            print(f"   💡 Loop Active: Toggles loop on/off")

        # Instructions for Traktor
        print(f"\n📋 TRAKTOR STEPS:")
        print(f"   1. Click 'Learn' in Controller Manager")
        print(f"   2. Navigate to: {self.traktor_paths[control_name]}")
        print(f"   3. Press ENTER below to send CC {cc}")

        input(f"   ⏸️  Ready to send CC {cc}? Press ENTER...")

        # Send button value (127 for all loop buttons)
        value = 127
        print(f"   📤 Sending: CC {cc} = {value} (LOOP BUTTON)")

        success = self.send_cc(cc, value)

        if success:
            print(f"   ✅ CC {cc} sent successfully")

            # User confirmation with retry option
            while True:
                result = input(f"   ❓ Mapping confirmed in Traktor? (y/n/r=retry): ").lower().strip()

                if result == 'y':
                    print(f"   🎉 {control_name} configured successfully!")
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

    def complete_configuration_session(self):
        """Complete configuration session for all Loop controls"""
        print("🎛️ LOOP LEARN HELPER")
        print("=" * 70)
        print("🎯 OBJECTIVE: Configure Loop controls for all 4 decks")
        print("📊 TOTAL CONTROLS: 12 (3 per deck: In, Out, Active)")
        print("🔢 CC RANGE: 121-126 (A&B), 53-58 (C&D)")
        print("=" * 70)

        print(f"\n📋 CONTROL OVERVIEW:")
        print("   LOOP CONTROL GROUPS:")
        print("   DECK A: Loop In (121), Loop Out (122), Loop Active (123)")
        print("   DECK B: Loop In (124), Loop Out (125), Loop Active (126)")
        print("   DECK C: Loop In (53), Loop Out (54), Loop Active (55)")
        print("   DECK D: Loop In (56), Loop Out (57), Loop Active (58)")
        print()
        print("   💡 LOOP WORKFLOW: Set In Point → Set Out Point → Toggle Active")
        print("   🎵 Use loops for creative transitions and performance effects")

        print(f"\n📋 PRE-CONFIGURATION CHECKLIST:")
        print("✅ 1. Traktor Pro 3 is open")
        print("✅ 2. Controller Manager is open (Preferences > Controller Manager)")
        print("✅ 3. Your controller device is selected")
        print("✅ 4. All 4 decks are visible in Traktor interface")
        print("✅ 5. Loop sections are visible and accessible")
        print("✅ 6. IAC Bus 1 is configured and online")

        if not self.connect_midi():
            return

        input(f"\n⏸️  Press ENTER to begin Loop configuration...")

        total_success = 0
        total_controls = len(self.suggested_mappings)

        # Configure each deck's loop controls
        for deck in ['a', 'b', 'c', 'd']:
            deck_success = self.configure_deck_loop_controls(deck)
            total_success += deck_success

            if deck != 'd':  # Don't pause after last deck
                next_deck = chr(ord(deck) + 1).upper()
                input(f"\n⏭️  Press ENTER to continue to Deck {next_deck}...")

        # Final summary
        print(f"\n🏆{'='*60}🏆")
        print("LOOP CONFIGURATION SESSION RESULTS")
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
            print("   ✅ Test loop workflow in live mixing")
            print("   ✅ Practice creative loop combinations")
            print("   ✅ All loop controls ready for autonomous DJ!")
        elif success_rate >= 80:
            print("   🔧 Review failed controls manually")
            print("   ✅ Export partial TSI configuration")
            print("   ⚠️ Test carefully before production use")
        else:
            print("   🔧 Manual MIDI Learn session recommended")
            print("   📚 Review Traktor Loop documentation")
            print("   ❌ Additional configuration required")

        # Generate code for traktor_control.py
        self.generate_traktor_control_code()

        print(f"\n💾 SAVE REMINDER:")
        print("   Don't forget to EXPORT your TSI file in Controller Manager!")
        print("   Recommended filename: Loop_Controls_53-58_121-126.tsi")

    def generate_traktor_control_code(self):
        """Generate Python code for traktor_control.py integration"""
        print(f"\n💻 TRAKTOR_CONTROL.PY INTEGRATION CODE:")
        print("=" * 50)
        print("# Add these methods to your TraktorControl class:")
        print()

        # Generate individual loop methods
        print("# Individual Loop Control Methods")
        for control_name, cc in self.suggested_mappings.items():
            parts = control_name.split('_')
            deck = parts[1].upper()
            loop_type = '_'.join(parts[2:])
            method_name = f"{loop_type}_deck_{deck.lower()}"

            print(f"def {method_name}(self):")
            print(f'    """Trigger {loop_type.replace("_", " ")} for Deck {deck}"""')
            print(f"    return self.send_cc({cc}, 127)  # CC {cc}")
            print()

        # Generate deck-specific loop workflows
        print("# Deck Loop Workflow Methods")
        for deck in ['a', 'b', 'c', 'd']:
            deck_upper = deck.upper()
            print(f"def setup_loop_deck_{deck}(self, in_point=True, out_point=True, activate=True):")
            print(f'    """Complete loop setup workflow for Deck {deck_upper}"""')
            print("    results = []")
            print("    if in_point:")
            print(f"        results.append(self.loop_in_deck_{deck}())")
            print("    if out_point:")
            print(f"        results.append(self.loop_out_deck_{deck}())")
            print("    if activate:")
            print(f"        results.append(self.loop_active_deck_{deck}())")
            print("    return all(results)")
            print()

        # Generate utility methods
        print("# Loop Utility Methods")
        print("def activate_all_loops(self):")
        print('    """Activate loops on all decks"""')
        print("    results = []")
        for deck in ['a', 'b', 'c', 'd']:
            print(f"    results.append(self.loop_active_deck_{deck}())")
        print("    return all(results)")
        print()

        print("def deactivate_all_loops(self):")
        print('    """Deactivate loops on all decks (send again to toggle off)"""')
        print("    return self.activate_all_loops()  # Toggle same CCs")

    def quick_test_loop_controls(self):
        """Quick test all Loop controls for verification"""
        print("🧪 QUICK TEST: All Loop Controls")
        print("=" * 50)

        if not self.connect_midi():
            return

        # Test by deck for logical grouping
        for deck in ['A', 'B', 'C', 'D']:
            print(f"\n🎛️ Testing Deck {deck} loop controls...")

            deck_controls = {k: v for k, v in self.suggested_mappings.items()
                           if k.startswith(f'deck_{deck.lower()}_')}

            for control_name, cc in deck_controls.items():
                control_type = control_name.split('_')[-1]
                print(f"   📤 {control_type.upper()}: CC {cc} = 127")
                self.send_cc(cc, 127)
                time.sleep(0.3)

        print(f"\n✅ Quick test completed - check Traktor for loop responses")

def main():
    print("🎛️ Loop Learn Helper")
    print("Configure Loop controls for all 4 decks in Traktor Pro 3")
    print("=" * 60)
    print("Available modes:")
    print("1. Complete Interactive Configuration Session")
    print("2. Quick Test All Loop Controls")
    print("3. Exit")

    choice = input("\nEnter choice (1/2/3): ").strip()

    helper = LoopLearnHelper()

    if choice == "1":
        helper.complete_configuration_session()
    elif choice == "2":
        helper.quick_test_loop_controls()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()