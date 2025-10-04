#!/usr/bin/env python3
"""
🎯 Pattern-Based MIDI Command Discovery
Quick discovery using logical CC patterns for problematic commands
"""

import time
import logging
from typing import Dict, List, Optional, Tuple

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False
    print("⚠️ rtmidi not available. Install with: pip install python-rtmidi")

from config import DJConfig, get_config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PatternDiscoveryTester:
    """Test logical CC patterns for problematic commands"""

    # Pattern-based discovery suggestions
    PATTERN_TESTS = {
        'deck_c_play': {
            'current_cc': 22,
            'issue': 'Controls CUE instead of PLAY',
            'pattern_ccs': [26, 28, 30, 32, 34, 36, 38],  # Even numbers after 24
            'description': 'Deck C PLAY button'
        },
        'deck_d_play': {
            'current_cc': 23,
            'issue': 'No clear response',
            'pattern_ccs': [27, 29, 31, 33, 35, 37, 39],  # Odd numbers after 25
            'description': 'Deck D PLAY button'
        },
        'deck_c_cue': {
            'current_cc': 27,
            'issue': 'No clear response',
            'pattern_ccs': [82, 84, 86, 22],  # Following 80,81 pattern + current deck_c_play CC
            'description': 'Deck C CUE button'
        },
        'deck_d_cue': {
            'current_cc': 88,
            'issue': 'No clear response',
            'pattern_ccs': [83, 85, 87, 23],  # Following pattern + current deck_d_play CC
            'description': 'Deck D CUE button'
        },
        'deck_b_sync_grid': {
            'current_cc': 25,
            'issue': 'Controls PLAY flash + CUE instead of sync',
            'pattern_ccs': [26, 56, 57, 58, 64, 65, 66],  # Around other sync commands
            'description': 'Deck B SYNC to grid'
        }
    }

    def __init__(self, config: DJConfig):
        self.config = config
        self.midi_out: Optional[rtmidi.MidiOut] = None
        self.connected = False
        self.test_results: Dict[str, List[Tuple[int, str]]] = {}

    def connect(self) -> bool:
        """Connect to IAC Driver for MIDI output"""
        if not RTMIDI_AVAILABLE:
            logger.error("❌ rtmidi not available")
            return False

        try:
            self.midi_out = rtmidi.MidiOut()
            output_ports = self.midi_out.get_ports()

            logger.info(f"📋 Available MIDI ports: {output_ports}")

            # Find IAC Driver Bus 1
            iac_port_idx = None
            for i, port in enumerate(output_ports):
                if "iac" in port.lower() and "bus 1" in port.lower():
                    iac_port_idx = i
                    break

            if iac_port_idx is not None:
                self.midi_out.open_port(iac_port_idx)
                self.connected = True
                logger.info(f"✅ Connected to: {output_ports[iac_port_idx]}")
                return True
            else:
                logger.error("❌ IAC Driver Bus 1 not found")
                return False

        except Exception as e:
            logger.error(f"❌ MIDI connection error: {e}")
            return False

    def send_midi_command(self, channel: int, cc: int, value: int, description: str = "") -> bool:
        """Send MIDI command to Traktor"""
        if not self.connected or not self.midi_out:
            logger.warning("⚠️ Not connected to MIDI")
            return False

        try:
            message = [0xB0 + (channel - 1), cc, value]
            self.midi_out.send_message(message)
            logger.info(f"📤 Sent: CH{channel} CC{cc}={value} ({description})")
            return True
        except Exception as e:
            logger.error(f"❌ MIDI send error: {e}")
            return False

    def test_pattern_for_command(self, command_name: str) -> List[Tuple[int, str]]:
        """Test all pattern CCs for a specific command"""
        if command_name not in self.PATTERN_TESTS:
            return []

        pattern_info = self.PATTERN_TESTS[command_name]
        results = []

        print(f"\n🎯 TESTING PATTERNS for {command_name}")
        print(f"Description: {pattern_info['description']}")
        print(f"Current issue: {pattern_info['issue']}")
        print(f"Current CC: {pattern_info['current_cc']} (problematic)")

        for cc in pattern_info['pattern_ccs']:
            print(f"\n🧪 Testing CC {cc} for {command_name}...")

            success = self.send_midi_command(1, cc, 127, f"Pattern test {command_name}")

            if success:
                time.sleep(0.3)  # Brief pause to observe

                # Since we can't get user input in this environment,
                # we'll test a few different values to see the response
                print(f"📤 Sent CC {cc} = 127")

                # Test value 0 (off) after brief pause
                time.sleep(0.2)
                self.send_midi_command(1, cc, 0, f"Pattern test {command_name} OFF")
                print(f"📤 Sent CC {cc} = 0")

                results.append((cc, "Sent - Human verification needed"))
            else:
                results.append((cc, "MIDI send failed"))

        self.test_results[command_name] = results
        return results

    def test_all_patterns(self):
        """Test patterns for all problematic commands"""
        print("🎯 PATTERN-BASED DISCOVERY TEST")
        print("=" * 60)
        print("Testing logical CC patterns for problematic transport commands")
        print("⚠️ HUMAN VERIFICATION REQUIRED: Please observe Traktor for each test")
        print("=" * 60)

        if not self.connect():
            print("❌ Failed to connect to MIDI")
            return

        for command_name in self.PATTERN_TESTS.keys():
            results = self.test_pattern_for_command(command_name)

            print(f"\n📊 Results for {command_name}:")
            for cc, result in results:
                print(f"   CC {cc}: {result}")

        self.generate_pattern_report()

    def generate_pattern_report(self):
        """Generate pattern test report"""
        print(f"\n{'='*60}")
        print("📊 PATTERN DISCOVERY REPORT")
        print(f"{'='*60}")

        print("\n🔍 TESTED CC PATTERNS:")
        for command_name, results in self.test_results.items():
            print(f"\n{command_name}:")
            print(f"  Issue: {self.PATTERN_TESTS[command_name]['issue']}")
            print(f"  Tested CCs: {[cc for cc, _ in results]}")
            print(f"  Total patterns tested: {len(results)}")

        print(f"\n👀 HUMAN VERIFICATION NEEDED:")
        print(f"For each command above, please note which CC (if any) produced the correct behavior:")

        for command_name in self.PATTERN_TESTS.keys():
            pattern_info = self.PATTERN_TESTS[command_name]
            print(f"\n✅ {command_name} - Expected: {pattern_info['description']}")
            ccs_tested = [cc for cc, _ in self.test_results.get(command_name, [])]
            print(f"   Tested CCs: {ccs_tested}")
            print(f"   Which CC worked? (Note for later update)")

        print(f"\n🔧 NEXT STEPS:")
        print(f"1. Note which CCs produced correct behaviors")
        print(f"2. Update traktor_control.py with working CCs")
        print(f"3. Test updated mappings")
        print(f"4. If no patterns worked, use MIDI Learn mode in Traktor")

    def test_single_command(self, command_name: str, cc: int):
        """Test a single CC for a specific command - useful for targeted testing"""
        if command_name not in self.PATTERN_TESTS:
            print(f"❌ Unknown command: {command_name}")
            return

        pattern_info = self.PATTERN_TESTS[command_name]
        print(f"\n🎯 SINGLE COMMAND TEST: {command_name}")
        print(f"Expected: {pattern_info['description']}")
        print(f"Testing CC: {cc}")

        if not self.connected:
            if not self.connect():
                print("❌ Failed to connect to MIDI")
                return

        # Test ON
        print(f"📤 Sending CC {cc} = 127 (ON)")
        success = self.send_midi_command(1, cc, 127, f"Test {command_name}")

        if success:
            time.sleep(0.5)

            # Test OFF
            print(f"📤 Sending CC {cc} = 0 (OFF)")
            self.send_midi_command(1, cc, 0, f"Test {command_name} OFF")

            print(f"✅ Test completed for {command_name} CC {cc}")
            print(f"👀 Did you observe the correct behavior: {pattern_info['description']}?")
        else:
            print(f"❌ MIDI send failed")

def main():
    """Main pattern discovery test"""
    print("Select test mode:")
    print("1. Test all problematic commands with pattern discovery")
    print("2. Test specific command with specific CC")

    config = get_config()
    tester = PatternDiscoveryTester(config)

    # For automated testing, run all patterns
    print("Running all pattern tests...")
    tester.test_all_patterns()

if __name__ == "__main__":
    main()