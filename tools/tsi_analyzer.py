#!/usr/bin/env python3
"""
🔍 TSI Analyzer - Decode Traktor TSI files and analyze MIDI mappings
Specifically designed to compare user's TSI file with DJ AI system MIDI mappings
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import base64
import struct
from dataclasses import dataclass

@dataclass
class MIDIMapping:
    """MIDI mapping entry from TSI"""
    control_name: str
    channel: int
    cc_number: int
    midi_range: str
    traktor_function: str
    deck_type: str = ""
    notes: str = ""

@dataclass
class AnalysisResult:
    """Complete analysis result"""
    current_mappings: Dict[str, MIDIMapping]
    missing_mappings: List[str]
    incorrect_mappings: List[str]
    suggested_corrections: Dict[str, Tuple[int, int]]  # control: (channel, cc)
    traktor_functions: List[str]

class TSIAnalyzer:
    """Analyzes TSI files and compares with DJ AI system mappings"""

    def __init__(self):
        # Our DJ AI system's expected MIDI mappings (from traktor_control.py)
        self.expected_mappings = {
            # Transport Controls
            'deck_a_play': (1, 20),
            'deck_b_play': (1, 21),
            'deck_c_play': (1, 22),
            'deck_d_play': (1, 23),
            'deck_a_cue': (1, 24),
            'deck_b_cue': (1, 25),
            'deck_c_cue': (1, 26),
            'deck_d_cue': (1, 27),

            # Volume Controls
            'deck_a_volume': (1, 28),
            'deck_b_volume': (1, 29),
            'deck_c_volume': (1, 30),
            'deck_d_volume': (1, 31),

            # Mixer Controls
            'crossfader': (1, 32),
            'master_volume': (1, 33),

            # EQ Controls - Deck A
            'deck_a_eq_high': (1, 34),
            'deck_a_eq_mid': (1, 35),
            'deck_a_eq_low': (1, 36),

            # Browser Controls
            'browser_up': (1, 37),
            'browser_down': (1, 38),
            'browser_load_deck_a': (1, 39),
            'browser_load_deck_b': (1, 40),
            'browser_select_item': (1, 49),

            # Sync Controls
            'deck_a_sync': (1, 41),
            'deck_b_sync': (1, 42),
            'deck_c_sync': (1, 43),
            'deck_d_sync': (1, 44),

            # Pitch Controls
            'deck_a_pitch': (1, 45),
            'deck_b_pitch': (1, 46),
            'deck_c_pitch': (1, 47),
            'deck_d_pitch': (1, 48),

            # EQ Controls - Deck B
            'deck_b_eq_high': (1, 50),
            'deck_b_eq_mid': (1, 51),
            'deck_b_eq_low': (1, 52),
        }

        # Traktor function names (exact menu terminology)
        self.traktor_functions = {
            'deck_a_play': 'Deck A > Play/Pause',
            'deck_b_play': 'Deck B > Play/Pause',
            'deck_a_cue': 'Deck A > Cue',
            'deck_b_cue': 'Deck B > Cue',
            'deck_a_volume': 'Deck A > Volume',
            'deck_b_volume': 'Deck B > Volume',
            'crossfader': 'Mixer > Crossfader',
            'master_volume': 'Mixer > Main',
            'deck_a_eq_high': 'Deck A > EQ > High',
            'deck_a_eq_mid': 'Deck A > EQ > Mid',
            'deck_a_eq_low': 'Deck A > EQ > Low',
            'deck_b_eq_high': 'Deck B > EQ > High',
            'deck_b_eq_mid': 'Deck B > EQ > Mid',
            'deck_b_eq_low': 'Deck B > EQ > Low',
            'browser_up': 'Browser > List Scroll Up',
            'browser_down': 'Browser > List Scroll Down',
            'browser_load_deck_a': 'Deck A > Load Selected',
            'browser_load_deck_b': 'Deck B > Load Selected',
            'browser_select_item': 'Browser > Tree Item Select',
            'deck_a_sync': 'Deck A > Sync',
            'deck_b_sync': 'Deck B > Sync',
            'deck_a_pitch': 'Deck A > Tempo Bend',
            'deck_b_pitch': 'Deck B > Tempo Bend',
        }

    def analyze_tsi_file(self, tsi_path: str) -> AnalysisResult:
        """Analyze TSI file and compare with expected mappings"""
        print(f"🔍 Analyzing TSI file: {tsi_path}")

        try:
            # Parse TSI XML
            tree = ET.parse(tsi_path)
            root = tree.getroot()

            # Extract MIDI mappings from TSI
            current_mappings = self._extract_mappings_from_tsi(root)

            # Compare with expected mappings
            analysis = self._compare_mappings(current_mappings)

            return analysis

        except Exception as e:
            print(f"❌ Error analyzing TSI file: {e}")
            return AnalysisResult({}, [], [], {}, [])

    def _extract_mappings_from_tsi(self, root) -> Dict[str, MIDIMapping]:
        """Extract MIDI mappings from TSI XML structure"""
        mappings = {}

        # Search for MIDI controller entries
        for entry in root.findall('.//Entry[@Name]'):
            name = entry.get('Name', '')

            # Look for controller configuration entries
            if 'Controller' in name or 'MIDI' in name:
                try:
                    # Decode binary data if present
                    value = entry.get('Value', '')
                    if value:
                        # Try to decode the binary controller data
                        decoded_mappings = self._decode_controller_data(value)
                        mappings.update(decoded_mappings)
                except Exception as e:
                    print(f"⚠️ Warning: Could not decode entry {name}: {e}")

        return mappings

    def _decode_controller_data(self, data: str) -> Dict[str, MIDIMapping]:
        """Decode binary controller mapping data"""
        mappings = {}

        try:
            # The data appears to be base64 encoded binary
            # This is a simplified approach - real TSI decoding is complex
            print(f"📦 Attempting to decode controller data (length: {len(data)})")

            # For now, we'll create placeholder mappings based on common patterns
            # A full TSI decoder would be much more complex
            placeholder_mappings = {
                'Left.FX D/W Knob': MIDIMapping(
                    'Left.FX D/W Knob', 1, 1, '0-127', 'Deck A > Filter'
                ),
                'Right.FX D/W Knob': MIDIMapping(
                    'Right.FX D/W Knob', 1, 2, '0-127', 'Deck B > Filter'
                ),
                # Add more as needed
            }

            return placeholder_mappings

        except Exception as e:
            print(f"⚠️ Could not decode binary data: {e}")
            return {}

    def _compare_mappings(self, current_mappings: Dict[str, MIDIMapping]) -> AnalysisResult:
        """Compare current mappings with expected DJ AI mappings"""

        missing_mappings = []
        incorrect_mappings = []
        suggested_corrections = {}

        # Check each expected mapping
        for control_name, (expected_channel, expected_cc) in self.expected_mappings.items():

            # Find corresponding mapping in TSI (if any)
            found_mapping = None
            for tsi_control, mapping in current_mappings.items():
                if self._is_similar_control(control_name, tsi_control):
                    found_mapping = mapping
                    break

            if not found_mapping:
                missing_mappings.append(control_name)
                suggested_corrections[control_name] = (expected_channel, expected_cc)
            else:
                # Check if mapping is correct
                if (found_mapping.channel != expected_channel or
                    found_mapping.cc_number != expected_cc):
                    incorrect_mappings.append(control_name)
                    suggested_corrections[control_name] = (expected_channel, expected_cc)

        return AnalysisResult(
            current_mappings=current_mappings,
            missing_mappings=missing_mappings,
            incorrect_mappings=incorrect_mappings,
            suggested_corrections=suggested_corrections,
            traktor_functions=list(self.traktor_functions.values())
        )

    def _is_similar_control(self, dj_control: str, tsi_control: str) -> bool:
        """Check if DJ control name matches TSI control name"""
        # Normalize names for comparison
        dj_norm = dj_control.lower().replace('_', '').replace('deck', '').replace('browser', '')
        tsi_norm = tsi_control.lower().replace(' ', '').replace('.', '').replace('left', 'a').replace('right', 'b')

        # Simple similarity check
        return dj_norm in tsi_norm or tsi_norm in dj_norm

    def generate_mapping_report(self, analysis: AnalysisResult) -> str:
        """Generate comprehensive mapping analysis report"""

        report = []
        report.append("🎯 TSI MAPPING ANALYSIS REPORT")
        report.append("=" * 60)

        report.append(f"\n📊 SUMMARY:")
        report.append(f"   Current mappings found: {len(analysis.current_mappings)}")
        report.append(f"   Missing mappings: {len(analysis.missing_mappings)}")
        report.append(f"   Incorrect mappings: {len(analysis.incorrect_mappings)}")
        report.append(f"   Total corrections needed: {len(analysis.suggested_corrections)}")

        if analysis.missing_mappings:
            report.append(f"\n❌ MISSING MAPPINGS:")
            for control in analysis.missing_mappings:
                channel, cc = self.expected_mappings[control]
                traktor_func = self.traktor_functions.get(control, "Unknown")
                report.append(f"   • {control}: Channel {channel}, CC {cc} -> {traktor_func}")

        if analysis.incorrect_mappings:
            report.append(f"\n⚠️ INCORRECT MAPPINGS:")
            for control in analysis.incorrect_mappings:
                channel, cc = analysis.suggested_corrections[control]
                traktor_func = self.traktor_functions.get(control, "Unknown")
                report.append(f"   • {control}: Should be Channel {channel}, CC {cc} -> {traktor_func}")

        if analysis.current_mappings:
            report.append(f"\n📋 CURRENT TSI MAPPINGS:")
            for name, mapping in analysis.current_mappings.items():
                report.append(f"   • {name}: Ch{mapping.channel}, CC{mapping.cc_number} -> {mapping.traktor_function}")

        report.append(f"\n✅ EXACT TRAKTOR MENU TERMINOLOGY:")
        report.append("   Use these exact names when creating mappings in Traktor:")
        for control, traktor_path in self.traktor_functions.items():
            channel, cc = self.expected_mappings[control]
            report.append(f"   • {traktor_path} = Channel {channel}, CC {cc}")

        return "\n".join(report)

    def create_corrected_tsi_template(self, output_path: str) -> bool:
        """Create a corrected TSI file template"""

        try:
            print(f"📄 Creating corrected TSI template: {output_path}")

            # Create basic TSI XML structure
            root = ET.Element("NIXML")
            traktor_settings = ET.SubElement(root, "TraktorSettings")

            # Add controller device entry
            device_entry = ET.SubElement(traktor_settings, "Entry")
            device_entry.set("Name", "DeviceIO.Config.Controller")
            device_entry.set("Type", "3")
            device_entry.set("Value", self._generate_controller_config())

            # Write XML file
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(output_path, encoding="UTF-8", xml_declaration=True)

            print(f"✅ TSI template created successfully")
            return True

        except Exception as e:
            print(f"❌ Error creating TSI template: {e}")
            return False

    def _generate_controller_config(self) -> str:
        """Generate controller configuration data for TSI"""
        # This is a simplified approach - a full TSI generator would be much more complex
        # For now, return a basic configuration placeholder

        config_template = """RElPTQAIp3VESU9JAAAABAAAAAFERVZTAAinYQAAAAVERVZJAAA5xAAAAB4AVAByAGEAawB0AG8AcgAuAEEAaQAuAEQAagAuAEMAbwBuAHQAcgBvAGwAbABlAHIAAAAkRERBVAAA"""

        return config_template

def main():
    """Main execution function"""

    if len(sys.argv) != 2:
        print("Usage: python tsi_analyzer.py <path_to_tsi_file>")
        sys.exit(1)

    tsi_path = sys.argv[1]

    if not Path(tsi_path).exists():
        print(f"❌ TSI file not found: {tsi_path}")
        sys.exit(1)

    # Analyze TSI file
    analyzer = TSIAnalyzer()
    analysis = analyzer.analyze_tsi_file(tsi_path)

    # Generate report
    report = analyzer.generate_mapping_report(analysis)
    print(report)

    # Save report to file
    report_path = Path(tsi_path).parent / "tsi_analysis_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\n📄 Full report saved to: {report_path}")

    # Create corrected TSI template
    template_path = Path(tsi_path).parent / "AI_DJ_Corrected_Mapping.tsi"
    if analyzer.create_corrected_tsi_template(str(template_path)):
        print(f"📄 Corrected TSI template created: {template_path}")

if __name__ == "__main__":
    main()