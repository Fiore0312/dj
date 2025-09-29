#!/usr/bin/env python3
"""
🎯 Create Perfect TSI - Generate a complete TSI file for DJ AI system
Creates TSI with all required MIDI mappings using exact Traktor menu terminology
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import base64
import datetime

class TraktorTSIGenerator:
    """Generate complete TSI file with all DJ AI mappings"""

    def __init__(self):
        # Complete mapping with exact Traktor function names
        self.mappings = [
            # TRANSPORT CONTROLS
            {
                'name': 'Deck A Play',
                'traktor_function': 'Deck A > Play/Pause',
                'channel': 1,
                'cc': 20,
                'midi_range': '0-127',
                'interaction_mode': 'Toggle',
                'control_type': 'Button'
            },
            {
                'name': 'Deck B Play',
                'traktor_function': 'Deck B > Play/Pause',
                'channel': 1,
                'cc': 21,
                'midi_range': '0-127',
                'interaction_mode': 'Toggle',
                'control_type': 'Button'
            },
            {
                'name': 'Deck A Cue',
                'traktor_function': 'Deck A > Cue',
                'channel': 1,
                'cc': 24,
                'midi_range': '0-127',
                'interaction_mode': 'Hold',
                'control_type': 'Button'
            },
            {
                'name': 'Deck B Cue',
                'traktor_function': 'Deck B > Cue',
                'channel': 1,
                'cc': 25,
                'midi_range': '0-127',
                'interaction_mode': 'Hold',
                'control_type': 'Button'
            },

            # VOLUME CONTROLS
            {
                'name': 'Deck A Volume',
                'traktor_function': 'Deck A > Volume',
                'channel': 1,
                'cc': 28,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Fader'
            },
            {
                'name': 'Deck B Volume',
                'traktor_function': 'Deck B > Volume',
                'channel': 1,
                'cc': 29,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Fader'
            },

            # MIXER CONTROLS
            {
                'name': 'Crossfader',
                'traktor_function': 'Mixer > Crossfader',
                'channel': 1,
                'cc': 32,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Fader'
            },
            {
                'name': 'Master Volume',
                'traktor_function': 'Mixer > Main',
                'channel': 1,
                'cc': 33,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Fader'
            },

            # EQ CONTROLS - DECK A
            {
                'name': 'Deck A EQ High',
                'traktor_function': 'Deck A > EQ > High',
                'channel': 1,
                'cc': 34,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Knob'
            },
            {
                'name': 'Deck A EQ Mid',
                'traktor_function': 'Deck A > EQ > Mid',
                'channel': 1,
                'cc': 35,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Knob'
            },
            {
                'name': 'Deck A EQ Low',
                'traktor_function': 'Deck A > EQ > Low',
                'channel': 1,
                'cc': 36,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Knob'
            },

            # BROWSER CONTROLS
            {
                'name': 'Browser Up',
                'traktor_function': 'Browser > List Scroll Up',
                'channel': 1,
                'cc': 37,
                'midi_range': '127-127',
                'interaction_mode': 'Inc',
                'control_type': 'Button'
            },
            {
                'name': 'Browser Down',
                'traktor_function': 'Browser > List Scroll Down',
                'channel': 1,
                'cc': 38,
                'midi_range': '127-127',
                'interaction_mode': 'Inc',
                'control_type': 'Button'
            },
            {
                'name': 'Load Deck A',
                'traktor_function': 'Deck A > Load Selected',
                'channel': 1,
                'cc': 39,
                'midi_range': '127-127',
                'interaction_mode': 'Trigger',
                'control_type': 'Button'
            },
            {
                'name': 'Load Deck B',
                'traktor_function': 'Deck B > Load Selected',
                'channel': 1,
                'cc': 40,
                'midi_range': '127-127',
                'interaction_mode': 'Trigger',
                'control_type': 'Button'
            },
            {
                'name': 'Browser Select',
                'traktor_function': 'Browser > Tree Item Select',
                'channel': 1,
                'cc': 49,
                'midi_range': '127-127',
                'interaction_mode': 'Trigger',
                'control_type': 'Button'
            },

            # SYNC CONTROLS
            {
                'name': 'Deck A Sync',
                'traktor_function': 'Deck A > Sync',
                'channel': 1,
                'cc': 41,
                'midi_range': '127-127',
                'interaction_mode': 'Toggle',
                'control_type': 'Button'
            },
            {
                'name': 'Deck B Sync',
                'traktor_function': 'Deck B > Sync',
                'channel': 1,
                'cc': 42,
                'midi_range': '127-127',
                'interaction_mode': 'Toggle',
                'control_type': 'Button'
            },

            # PITCH CONTROLS
            {
                'name': 'Deck A Tempo Bend',
                'traktor_function': 'Deck A > Tempo Bend',
                'channel': 1,
                'cc': 45,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Fader'
            },
            {
                'name': 'Deck B Tempo Bend',
                'traktor_function': 'Deck B > Tempo Bend',
                'channel': 1,
                'cc': 46,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Fader'
            },

            # EQ CONTROLS - DECK B
            {
                'name': 'Deck B EQ High',
                'traktor_function': 'Deck B > EQ > High',
                'channel': 1,
                'cc': 50,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Knob'
            },
            {
                'name': 'Deck B EQ Mid',
                'traktor_function': 'Deck B > EQ > Mid',
                'channel': 1,
                'cc': 51,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Knob'
            },
            {
                'name': 'Deck B EQ Low',
                'traktor_function': 'Deck B > EQ > Low',
                'channel': 1,
                'cc': 52,
                'midi_range': '0-127',
                'interaction_mode': 'Direct',
                'control_type': 'Knob'
            },
        ]

    def create_tsi_file(self, output_path: str, device_name: str = "AI DJ Controller") -> bool:
        """Create complete TSI file with all mappings"""

        print(f"🎯 Creating complete TSI file: {output_path}")
        print(f"📱 Device name: {device_name}")
        print(f"🎛️ Total mappings: {len(self.mappings)}")

        try:
            # Create root XML structure
            root = ET.Element("NIXML")

            # Create Traktor Settings container
            traktor_settings = ET.SubElement(root, "TraktorSettings")

            # Add device info
            self._add_device_info(traktor_settings, device_name)

            # Add all MIDI mappings
            self._add_midi_mappings(traktor_settings)

            # Write TSI file
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)

            with open(output_path, 'wb') as f:
                f.write(b'<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
                tree.write(f, encoding="UTF-8")

            print(f"✅ TSI file created successfully!")
            return True

        except Exception as e:
            print(f"❌ Error creating TSI file: {e}")
            return False

    def _add_device_info(self, parent, device_name):
        """Add MIDI device configuration"""

        device_entry = ET.SubElement(parent, "Entry")
        device_entry.set("Name", "DeviceIO.Config.Device")
        device_entry.set("Type", "1")
        device_entry.set("Value", device_name)

        # Add MIDI input configuration
        midi_in_entry = ET.SubElement(parent, "Entry")
        midi_in_entry.set("Name", "DeviceIO.Config.MidiIn.Device")
        midi_in_entry.set("Type", "1")
        midi_in_entry.set("Value", "IAC Driver Bus 1")  # macOS IAC Driver

        # Add MIDI output configuration
        midi_out_entry = ET.SubElement(parent, "Entry")
        midi_out_entry.set("Name", "DeviceIO.Config.MidiOut.Device")
        midi_out_entry.set("Type", "1")
        midi_out_entry.set("Value", "IAC Driver Bus 1")

    def _add_midi_mappings(self, parent):
        """Add all MIDI control mappings"""

        for i, mapping in enumerate(self.mappings):
            self._add_single_mapping(parent, mapping, i)

    def _add_single_mapping(self, parent, mapping, index):
        """Add a single MIDI mapping entry"""

        # Create mapping entry
        mapping_entry = ET.SubElement(parent, "Entry")
        mapping_entry.set("Name", f"ControllerManager.Mapping.{index}")
        mapping_entry.set("Type", "4")

        # Create mapping sub-entries
        name_entry = ET.SubElement(mapping_entry, "Entry")
        name_entry.set("Name", "Name")
        name_entry.set("Type", "1")
        name_entry.set("Value", mapping['name'])

        # MIDI channel
        channel_entry = ET.SubElement(mapping_entry, "Entry")
        channel_entry.set("Name", "MidiChannel")
        channel_entry.set("Type", "2")
        channel_entry.set("Value", str(mapping['channel']))

        # MIDI CC number
        cc_entry = ET.SubElement(mapping_entry, "Entry")
        cc_entry.set("Name", "MidiCC")
        cc_entry.set("Type", "2")
        cc_entry.set("Value", str(mapping['cc']))

        # Traktor function
        function_entry = ET.SubElement(mapping_entry, "Entry")
        function_entry.set("Name", "TraktorFunction")
        function_entry.set("Type", "1")
        function_entry.set("Value", mapping['traktor_function'])

        # Control type
        type_entry = ET.SubElement(mapping_entry, "Entry")
        type_entry.set("Name", "ControlType")
        type_entry.set("Type", "1")
        type_entry.set("Value", mapping['control_type'])

        # Interaction mode
        mode_entry = ET.SubElement(mapping_entry, "Entry")
        mode_entry.set("Name", "InteractionMode")
        mode_entry.set("Type", "1")
        mode_entry.set("Value", mapping['interaction_mode'])

        # MIDI range
        range_entry = ET.SubElement(mapping_entry, "Entry")
        range_entry.set("Name", "MidiRange")
        range_entry.set("Type", "1")
        range_entry.set("Value", mapping['midi_range'])

    def generate_manual_setup_guide(self) -> str:
        """Generate step-by-step manual setup guide"""

        guide = []
        guide.append("🎯 MANUAL TSI SETUP GUIDE - DJ AI CONTROLLER")
        guide.append("=" * 60)
        guide.append(f"📅 Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        guide.append("")

        guide.append("📋 SETUP INSTRUCTIONS:")
        guide.append("1. Open Traktor Pro 3")
        guide.append("2. Go to Preferences > Controller Manager")
        guide.append("3. Add > Generic MIDI")
        guide.append("4. Name: 'AI DJ Controller'")
        guide.append("5. In Device Setup:")
        guide.append("   - MIDI Input: IAC Driver Bus 1")
        guide.append("   - MIDI Output: IAC Driver Bus 1")
        guide.append("6. Click 'Add Out...' for each mapping below")
        guide.append("")

        guide.append("🎛️ EXACT MIDI MAPPINGS (Copy these exactly):")
        guide.append("-" * 60)

        for i, mapping in enumerate(self.mappings, 1):
            guide.append(f"\n{i}. {mapping['name']}:")
            guide.append(f"   Device: Generic MIDI")
            guide.append(f"   Channel: {mapping['channel']}")
            guide.append(f"   Control: CC")
            guide.append(f"   No.: {mapping['cc']}")
            guide.append(f"   Assignment: {mapping['traktor_function']}")
            guide.append(f"   Type of Controller: {mapping['control_type']}")
            guide.append(f"   Interaction Mode: {mapping['interaction_mode']}")
            guide.append(f"   MIDI Range: {mapping['midi_range']}")

        guide.append("\n" + "=" * 60)
        guide.append("✅ VERIFICATION:")
        guide.append("After setup, test each control:")
        guide.append("- Play/Pause buttons should toggle playback")
        guide.append("- Volume faders should control deck volume")
        guide.append("- Browser controls should navigate music library")
        guide.append("- EQ knobs should adjust frequency bands")
        guide.append("- Load buttons should load selected tracks")

        guide.append("\n🆘 TROUBLESHOOTING:")
        guide.append("- If MIDI light flashes but no action: Check function assignment")
        guide.append("- If no MIDI light: Check IAC Driver Bus 1 is enabled")
        guide.append("- If wrong action: Verify CC numbers match exactly")

        return "\n".join(guide)

    def create_verification_test(self, output_path: str) -> bool:
        """Create a verification test script"""

        test_code = '''#!/usr/bin/env python3
"""
🧪 TSI Mapping Verification Test
Tests all MIDI mappings are working correctly with Traktor
"""

import mido
import time
from typing import Dict, List

class TSIVerificationTest:
    """Test all TSI MIDI mappings"""

    def __init__(self):
        self.test_mappings = {
            # Transport Tests
            'deck_a_play': (1, 20, 'Play/Pause Deck A'),
            'deck_b_play': (1, 21, 'Play/Pause Deck B'),
            'deck_a_cue': (1, 24, 'Cue Deck A'),
            'deck_b_cue': (1, 25, 'Cue Deck B'),

            # Volume Tests
            'deck_a_volume': (1, 28, 'Volume Deck A'),
            'deck_b_volume': (1, 29, 'Volume Deck B'),
            'crossfader': (1, 32, 'Crossfader'),
            'master_volume': (1, 33, 'Master Volume'),

            # Browser Tests
            'browser_up': (1, 37, 'Browser Up'),
            'browser_down': (1, 38, 'Browser Down'),
            'load_deck_a': (1, 39, 'Load Deck A'),
            'load_deck_b': (1, 40, 'Load Deck B'),

            # EQ Tests
            'deck_a_eq_high': (1, 34, 'Deck A EQ High'),
            'deck_a_eq_mid': (1, 35, 'Deck A EQ Mid'),
            'deck_a_eq_low': (1, 36, 'Deck A EQ Low'),
            'deck_b_eq_high': (1, 50, 'Deck B EQ High'),
            'deck_b_eq_mid': (1, 51, 'Deck B EQ Mid'),
            'deck_b_eq_low': (1, 52, 'Deck B EQ Low'),
        }

    def run_verification_test(self) -> Dict[str, bool]:
        """Run complete verification test"""
        print("🧪 Starting TSI Mapping Verification...")
        print("🎯 This will test all MIDI mappings with Traktor")
        print("📋 Watch Traktor for responses to each test\\n")

        results = {}

        try:
            # Connect to MIDI
            output = mido.open_output('Bus 1')  # macOS IAC Driver
            print("✅ Connected to IAC Driver Bus 1")

        except Exception as e:
            print(f"❌ Could not connect to MIDI: {e}")
            return results

        # Test each mapping
        for control_name, (channel, cc, description) in self.test_mappings.items():
            print(f"🎛️ Testing: {description} (Ch{channel}, CC{cc})")

            try:
                # Send test MIDI message
                msg = mido.Message('control_change',
                                 channel=channel-1,  # mido uses 0-based channels
                                 control=cc,
                                 value=127)
                output.send(msg)

                # Wait for user verification
                response = input("   Did Traktor respond correctly? (y/n/skip): ").lower()

                if response == 'y':
                    results[control_name] = True
                    print("   ✅ PASSED\\n")
                elif response == 'skip':
                    results[control_name] = None
                    print("   ⏭️ SKIPPED\\n")
                else:
                    results[control_name] = False
                    print("   ❌ FAILED\\n")

                time.sleep(0.5)  # Brief pause between tests

            except Exception as e:
                print(f"   ❌ ERROR: {e}\\n")
                results[control_name] = False

        output.close()

        # Show results
        self.show_test_results(results)
        return results

    def show_test_results(self, results: Dict[str, bool]):
        """Show final test results"""

        print("\\n🎯 TEST RESULTS SUMMARY")
        print("=" * 50)

        passed = sum(1 for v in results.values() if v is True)
        failed = sum(1 for v in results.values() if v is False)
        skipped = sum(1 for v in results.values() if v is None)

        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️ Skipped: {skipped}")

        if failed > 0:
            print(f"\\n❌ FAILED TESTS:")
            for control, result in results.items():
                if result is False:
                    channel, cc, desc = self.test_mappings[control]
                    print(f"   • {desc}: Channel {channel}, CC {cc}")

        if passed == len([v for v in results.values() if v is not None]):
            print("\\n🎉 ALL TESTS PASSED! TSI mappings are working correctly!")
        else:
            print(f"\\n⚠️ Some tests failed. Check Traktor Controller Manager mappings.")

if __name__ == "__main__":
    tester = TSIVerificationTest()
    tester.run_verification_test()
'''

        try:
            with open(output_path, 'w') as f:
                f.write(test_code)
            print(f"✅ Verification test created: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating test: {e}")
            return False

def main():
    """Main execution function"""

    print("🎯 DJ AI - Perfect TSI Generator")
    print("Creating complete TSI file with all required MIDI mappings")
    print("=" * 60)

    generator = TraktorTSIGenerator()

    # Create TSI file
    tsi_path = "AI_DJ_Perfect_Mapping.tsi"
    if generator.create_tsi_file(tsi_path):
        print(f"✅ Perfect TSI file created: {tsi_path}")

    # Create manual setup guide
    guide = generator.generate_manual_setup_guide()
    guide_path = "AI_DJ_Manual_Setup_Guide.txt"

    with open(guide_path, 'w') as f:
        f.write(guide)
    print(f"📄 Manual setup guide created: {guide_path}")

    # Create verification test
    test_path = "test_tsi_verification.py"
    if generator.create_verification_test(test_path):
        print(f"🧪 Verification test created: {test_path}")

    print("\n🎉 COMPLETE SOLUTION CREATED!")
    print("📋 Next steps:")
    print("1. Import AI_DJ_Perfect_Mapping.tsi in Traktor Controller Manager")
    print("2. OR follow AI_DJ_Manual_Setup_Guide.txt for manual setup")
    print("3. Run python test_tsi_verification.py to verify everything works")
    print("4. Test with DJ AI system")

if __name__ == "__main__":
    main()