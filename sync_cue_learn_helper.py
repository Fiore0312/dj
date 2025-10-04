#!/usr/bin/env python3
"""
🎛️ Sync & Cue Learn Helper - Automated CC Sender for Traktor Controller Manager
Interactive Learn session for Sync and Cue controls across all 4 decks
"""

import time
import rtmidi

class SyncCueLearnHelper:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None

        # Known Sync & Cue CC mappings (from discovery)
        self.known_mappings = {
            'deck_a_sync': 24,    # Confirmed working
            'deck_b_sync': 25,    # Confirmed working
            'deck_a_cue': 80,     # Confirmed working
            'deck_b_cue': 81,     # Confirmed working
        }

        # Suggested mappings for Deck C & D (following pattern)
        self.suggested_mappings = {
            'deck_c_sync': 26,    # Following +1 pattern from A/B
            'deck_d_sync': 27,    # Following +1 pattern from A/B
            'deck_c_cue': 82,     # Following +1 pattern from A/B
            'deck_d_cue': 83,     # Following +1 pattern from A/B
        }

        # Combine all mappings
        self.all_mappings = {**self.known_mappings, **self.suggested_mappings}

        # Control descriptions for user interface
        self.control_descriptions = {
            'deck_a_sync': 'Deck A Sync Button',
            'deck_b_sync': 'Deck B Sync Button',
            'deck_c_sync': 'Deck C Sync Button',
            'deck_d_sync': 'Deck D Sync Button',
            'deck_a_cue': 'Deck A Cue Button',
            'deck_b_cue': 'Deck B Cue Button',
            'deck_c_cue': 'Deck C Cue Button',
            'deck_d_cue': 'Deck D Cue Button'
        }

        # Traktor paths for Controller Manager
        self.traktor_paths = {
            'deck_a_sync': 'Deck A > Sync',
            'deck_b_sync': 'Deck B > Sync',
            'deck_c_sync': 'Deck C > Sync',
            'deck_d_sync': 'Deck D > Sync',
            'deck_a_cue': 'Deck A > Cue',
            'deck_b_cue': 'Deck B > Cue',
            'deck_c_cue': 'Deck C > Cue',
            'deck_d_cue': 'Deck D > Cue'
        }

        # Control status (known vs suggested)
        self.control_status = {
            'deck_a_sync': 'KNOWN ✅',
            'deck_b_sync': 'KNOWN ✅',
            'deck_a_cue': 'KNOWN ✅',
            'deck_b_cue': 'KNOWN ✅',
            'deck_c_sync': 'SUGGESTED 🔍',
            'deck_d_sync': 'SUGGESTED 🔍',
            'deck_c_cue': 'SUGGESTED 🔍',
            'deck_d_cue': 'SUGGESTED 🔍'
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

    def configure_sync_cue_controls(self):
        """Interactive Learn session for all Sync & Cue controls"""
        print("🎛️ SYNC & CUE LEARN HELPER")
        print("=" * 70)
        print("🎯 OBJECTIVE: Configure Sync and Cue buttons for all 4 decks")
        print("📊 TOTAL CONTROLS: 8 (4 Sync + 4 Cue)")
        print("🔢 CC RANGE: 24-27 (Sync) + 80-83 (Cue)")
        print("=" * 70)

        print(f"\n📋 CONTROL OVERVIEW:")
        print("   SYNC CONTROLS:")
        print("   • Deck A Sync: CC 24 ✅ (Known)")
        print("   • Deck B Sync: CC 25 ✅ (Known)")
        print("   • Deck C Sync: CC 26 🔍 (Suggested)")
        print("   • Deck D Sync: CC 27 🔍 (Suggested)")
        print("   CUE CONTROLS:")
        print("   • Deck A Cue: CC 80 ✅ (Known)")
        print("   • Deck B Cue: CC 81 ✅ (Known)")
        print("   • Deck C Cue: CC 82 🔍 (Suggested)")
        print("   • Deck D Cue: CC 83 🔍 (Suggested)")

        print(f"\n📋 PRE-CONFIGURATION CHECKLIST:")
        print("✅ 1. Traktor Pro 3 is open")
        print("✅ 2. Controller Manager is open (Preferences > Controller Manager)")
        print("✅ 3. Your controller device is selected")
        print("✅ 4. All 4 decks are visible in Traktor interface")
        print("✅ 5. IAC Bus 1 is configured and online")

        if not self.connect_midi():
            return

        input(f"\n⏸️  Press ENTER to begin Sync & Cue configuration...")

        success_count = 0
        total_controls = len(self.all_mappings)

        # Group controls by type for logical ordering
        sync_controls = {k: v for k, v in self.all_mappings.items() if 'sync' in k}
        cue_controls = {k: v for k, v in self.all_mappings.items() if 'cue' in k}

        # Configure Sync controls first
        print(f"\n{'='*60}")
        print("🔄 CONFIGURING SYNC CONTROLS")
        print(f"{'='*60}")

        for control_name, cc in sync_controls.items():
            success = self.configure_single_control(control_name, cc)
            if success:
                success_count += 1

        # Configure Cue controls second
        print(f"\n{'='*60}")
        print("🎵 CONFIGURING CUE CONTROLS")
        print(f"{'='*60}")

        for control_name, cc in cue_controls.items():
            success = self.configure_single_control(control_name, cc)
            if success:
                success_count += 1

        # Final summary
        print(f"\n🏆{'='*60}🏆")
        print("SYNC & CUE CONFIGURATION SESSION RESULTS")
        print(f"🏆{'='*60}🏆")

        success_rate = (success_count / total_controls) * 100
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Controls Configured: {success_count}/{total_controls}")
        print(f"   Success Rate: {success_rate:.1f}%")

        if success_rate >= 95:
            status = "🎉 EXCELLENT - All controls working!"
        elif success_rate >= 75:
            status = "✅ GOOD - Most controls working"
        elif success_rate >= 50:
            status = "⚠️ PARTIAL - Some controls working"
        else:
            status = "❌ POOR - Major issues detected"

        print(f"   Status: {status}")

        # Generate code for traktor_control.py
        self.generate_traktor_control_code(success_count)

        print(f"\n💾 SAVE REMINDER:")
        print("   Don't forget to EXPORT your TSI file in Controller Manager!")
        print("   Recommended filename: Sync_Cue_Mapping_24-27_80-83.tsi")

    def configure_single_control(self, control_name, cc):
        """Configure a single Sync or Cue control"""
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

        # Send button value (127 for all buttons)
        value = 127
        print(f"   📤 Sending: CC {cc} = {value} (BUTTON)")

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

    def generate_traktor_control_code(self, success_count):
        """Generate Python code for traktor_control.py integration"""
        print(f"\n💻 TRAKTOR_CONTROL.PY INTEGRATION CODE:")
        print("=" * 50)
        print("# Add these methods to your TraktorControl class:")
        print()

        # Generate sync methods
        print("# Sync Control Methods")
        for control_name, cc in self.all_mappings.items():
            if 'sync' in control_name:
                deck = control_name.split('_')[1].upper()
                method_name = f"sync_deck_{deck.lower()}"
                print(f"def {method_name}(self):")
                print(f'    """Toggle sync for Deck {deck}"""')
                print(f"    return self.send_cc({cc}, 127)  # CC {cc}")
                print()

        # Generate cue methods
        print("# Cue Control Methods")
        for control_name, cc in self.all_mappings.items():
            if 'cue' in control_name:
                deck = control_name.split('_')[1].upper()
                method_name = f"cue_deck_{deck.lower()}"
                print(f"def {method_name}(self):")
                print(f'    """Trigger cue for Deck {deck}"""')
                print(f"    return self.send_cc({cc}, 127)  # CC {cc}")
                print()

        print("# Combined method for all sync controls")
        print("def sync_all_decks(self):")
        print('    """Enable sync on all decks"""')
        print("    results = []")
        for control_name, cc in self.all_mappings.items():
            if 'sync' in control_name:
                deck = control_name.split('_')[1].lower()
                print(f"    results.append(self.sync_deck_{deck}())")
        print("    return all(results)")

    def quick_test_sync_cue(self):
        """Quick test all Sync & Cue controls"""
        print("🧪 QUICK TEST: All Sync & Cue Controls")
        print("=" * 50)

        if not self.connect_midi():
            return

        # Test sync controls
        print("\n🔄 Testing SYNC controls...")
        for control_name, cc in self.all_mappings.items():
            if 'sync' in control_name:
                print(f"   📤 {control_name}: CC {cc} = 127")
                self.send_cc(cc, 127)
                time.sleep(0.3)

        # Test cue controls
        print("\n🎵 Testing CUE controls...")
        for control_name, cc in self.all_mappings.items():
            if 'cue' in control_name:
                print(f"   📤 {control_name}: CC {cc} = 127")
                self.send_cc(cc, 127)
                time.sleep(0.3)

        print(f"\n✅ Quick test completed - check Traktor for responses")

def main():
    print("🎛️ Sync & Cue Learn Helper")
    print("Configure Sync and Cue controls for all 4 decks in Traktor Pro 3")
    print("=" * 65)
    print("Available modes:")
    print("1. Interactive Learn Configuration Session")
    print("2. Quick Test All Sync & Cue Controls")
    print("3. Exit")

    choice = input("\nEnter choice (1/2/3): ").strip()

    helper = SyncCueLearnHelper()

    if choice == "1":
        helper.configure_sync_cue_controls()
    elif choice == "2":
        helper.quick_test_sync_cue()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()