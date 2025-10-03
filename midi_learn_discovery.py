#!/usr/bin/env python3
"""
🎛️ MIDI Learn Discovery Tool - Traktor Command Mapping Discovery
Systematic discovery and verification of Traktor MIDI commands using learn mode
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

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

class DiscoveryStatus(Enum):
    PENDING = "pending"
    TESTING = "testing"
    LEARNING = "learning"
    DISCOVERED = "discovered"
    VERIFIED = "verified"
    FAILED = "failed"

@dataclass
class CommandDiscovery:
    """Tracking discovery progress for a command"""
    command_name: str
    current_cc: int
    expected_behavior: str
    status: DiscoveryStatus
    discovered_cc: Optional[int] = None
    test_results: List[str] = None
    verification_confirmed: bool = False

    def __post_init__(self):
        if self.test_results is None:
            self.test_results = []

class MIDILearnDiscovery:
    """Interactive MIDI Learn Discovery Tool"""

    # Problematic commands identified from batch testing
    PROBLEMATIC_COMMANDS = {
        'deck_c_play': {
            'current_cc': 22,
            'expected_behavior': 'Deck C PLAY button (start/stop playback)',
            'issue': 'Controls CUE instead of PLAY',
            'pattern_suggestions': [22, 24, 26, 28]  # Logical patterns to try
        },
        'deck_d_play': {
            'current_cc': 23,
            'expected_behavior': 'Deck D PLAY button (start/stop playback)',
            'issue': 'No clear response observed',
            'pattern_suggestions': [23, 25, 27, 29]
        },
        'deck_c_cue': {
            'current_cc': 27,
            'expected_behavior': 'Deck C CUE button (set cue point/return to cue)',
            'issue': 'No clear response observed',
            'pattern_suggestions': [82, 83, 84, 85]  # Following 80, 81 pattern
        },
        'deck_d_cue': {
            'current_cc': 88,
            'expected_behavior': 'Deck D CUE button (set cue point/return to cue)',
            'issue': 'No clear response observed',
            'pattern_suggestions': [83, 84, 85, 86]
        },
        'deck_b_sync_grid': {
            'current_cc': 25,
            'expected_behavior': 'Deck B SYNC to grid (align to beatgrid)',
            'issue': 'Controls PLAY flash + CUE instead of sync',
            'pattern_suggestions': [26, 57, 58, 64, 65]
        }
    }

    def __init__(self, config: DJConfig):
        self.config = config
        self.midi_out: Optional[rtmidi.MidiOut] = None
        self.connected = False

        # Discovery tracking
        self.discoveries: Dict[str, CommandDiscovery] = {}
        self.session_results: List[str] = []

        # Initialize discovery tracking
        for cmd_name, cmd_info in self.PROBLEMATIC_COMMANDS.items():
            self.discoveries[cmd_name] = CommandDiscovery(
                command_name=cmd_name,
                current_cc=cmd_info['current_cc'],
                expected_behavior=cmd_info['expected_behavior'],
                status=DiscoveryStatus.PENDING
            )

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

    def test_current_command(self, command_name: str) -> bool:
        """Test current mapping for a command"""
        if command_name not in self.discoveries:
            logger.error(f"❌ Unknown command: {command_name}")
            return False

        discovery = self.discoveries[command_name]
        discovery.status = DiscoveryStatus.TESTING

        print(f"\n🧪 TESTING CURRENT MAPPING: {command_name}")
        print(f"Expected: {discovery.expected_behavior}")
        print(f"Current CC: {discovery.current_cc}")
        print(f"Known issue: {self.PROBLEMATIC_COMMANDS[command_name]['issue']}")

        # Send current command
        success = self.send_midi_command(1, discovery.current_cc, 127, f"Test {command_name}")

        if success:
            print(f"✅ MIDI command sent successfully")
            print(f"👀 PLEASE OBSERVE TRAKTOR and confirm what happened:")

            # Get user feedback
            response = input(f"Did you observe the expected behavior ({discovery.expected_behavior})? (y/n/describe): ").strip().lower()

            if response == 'y':
                discovery.status = DiscoveryStatus.VERIFIED
                discovery.verification_confirmed = True
                discovery.test_results.append("✅ Current mapping works correctly")
                print(f"✅ Current mapping for {command_name} is WORKING!")
                return True
            elif response == 'n':
                description = input("What behavior did you observe instead? (or 'none' if no response): ").strip()
                discovery.test_results.append(f"❌ Wrong behavior: {description}")
                print(f"❌ Current mapping confirmed as problematic")
                return False
            else:
                discovery.test_results.append(f"⚠️ User described: {response}")
                print(f"📝 Behavior logged: {response}")
                return False
        else:
            discovery.test_results.append("❌ MIDI command failed to send")
            return False

    def guide_midi_learn(self, command_name: str) -> Optional[int]:
        """Guide user through Traktor MIDI learn process"""
        if command_name not in self.discoveries:
            return None

        discovery = self.discoveries[command_name]
        discovery.status = DiscoveryStatus.LEARNING

        print(f"\n🎓 MIDI LEARN MODE for {command_name}")
        print("=" * 60)
        print(f"Target: {discovery.expected_behavior}")
        print("\nSTEPS TO FOLLOW:")
        print("1. In Traktor, go to Preferences > Controller Manager")
        print("2. Select your mapping (AI_DJ_Complete or similar)")
        print("3. Click 'Learn' button (or press Ctrl+L)")
        print("4. Find and click the control you want to map:")

        # Specific instructions per command
        if 'play' in command_name:
            deck = command_name.split('_')[1].upper()
            print(f"   → Click the PLAY button for Deck {deck}")
        elif 'cue' in command_name:
            deck = command_name.split('_')[1].upper()
            print(f"   → Click the CUE button for Deck {deck}")
        elif 'sync' in command_name:
            deck = command_name.split('_')[1].upper()
            print(f"   → Click the SYNC button for Deck {deck}")

        print("5. Traktor will show 'Learning...' - wait for it")
        print("6. I will now send MIDI commands for you to assign")
        print("\nPress ENTER when you're ready to start MIDI Learn...")
        input()

        # Try pattern suggestions first
        suggestions = self.PROBLEMATIC_COMMANDS[command_name]['pattern_suggestions']

        for suggested_cc in suggestions:
            print(f"\n🎯 Trying CC {suggested_cc} for {command_name}")
            print("Sending MIDI command...")

            success = self.send_midi_command(1, suggested_cc, 127, f"Learn {command_name}")

            if success:
                time.sleep(0.5)
                response = input(f"Did Traktor accept CC {suggested_cc} for {command_name}? (y/n): ").strip().lower()

                if response == 'y':
                    discovery.discovered_cc = suggested_cc
                    discovery.status = DiscoveryStatus.DISCOVERED
                    print(f"🎉 DISCOVERED: {command_name} = CC {suggested_cc}")

                    # Test the new mapping immediately
                    self.verify_discovered_command(command_name, suggested_cc)
                    return suggested_cc
                else:
                    print(f"❌ CC {suggested_cc} not accepted, trying next...")

        print(f"⚠️ Pattern suggestions didn't work. Manual CC input needed.")
        while True:
            try:
                manual_cc = input("Enter CC number to try (or 'quit' to stop): ").strip()
                if manual_cc.lower() == 'quit':
                    return None

                cc_num = int(manual_cc)
                if 0 <= cc_num <= 127:
                    success = self.send_midi_command(1, cc_num, 127, f"Learn {command_name}")
                    if success:
                        time.sleep(0.5)
                        response = input(f"Did Traktor accept CC {cc_num} for {command_name}? (y/n): ").strip().lower()
                        if response == 'y':
                            discovery.discovered_cc = cc_num
                            discovery.status = DiscoveryStatus.DISCOVERED
                            self.verify_discovered_command(command_name, cc_num)
                            return cc_num
                else:
                    print("Please enter a CC number between 0 and 127")
            except ValueError:
                print("Please enter a valid number")

    def verify_discovered_command(self, command_name: str, discovered_cc: int) -> bool:
        """Verify that discovered command works correctly"""
        print(f"\n✅ VERIFYING DISCOVERED COMMAND: {command_name} = CC {discovered_cc}")

        discovery = self.discoveries[command_name]

        print(f"Expected behavior: {discovery.expected_behavior}")
        print("Testing the discovered command...")

        # Send the discovered command
        success = self.send_midi_command(1, discovered_cc, 127, f"Verify {command_name}")

        if success:
            print(f"📤 Sent CC {discovered_cc}")
            time.sleep(0.5)

            response = input(f"👀 Did you observe the correct behavior ({discovery.expected_behavior})? (y/n): ").strip().lower()

            if response == 'y':
                discovery.status = DiscoveryStatus.VERIFIED
                discovery.verification_confirmed = True
                discovery.test_results.append(f"✅ Verified: CC {discovered_cc} works correctly")
                print(f"🎉 VERIFICATION SUCCESS: {command_name} = CC {discovered_cc}")
                return True
            else:
                actual_behavior = input("What behavior did you observe? ").strip()
                discovery.test_results.append(f"❌ Verification failed: {actual_behavior}")
                discovery.status = DiscoveryStatus.FAILED
                print(f"❌ Verification failed for CC {discovered_cc}")
                return False
        else:
            discovery.test_results.append("❌ Verification MIDI send failed")
            discovery.status = DiscoveryStatus.FAILED
            return False

    def run_full_discovery_session(self):
        """Run complete discovery session for all problematic commands"""
        print("🎛️ TRAKTOR MIDI COMMAND DISCOVERY SESSION")
        print("=" * 60)
        print("This tool will systematically discover and verify MIDI commands for Traktor.")
        print("Please ensure:")
        print("✅ Traktor Pro is running")
        print("✅ IAC Driver Bus 1 is enabled")
        print("✅ You can access Traktor's Preferences > Controller Manager")
        print("\nPress ENTER to continue...")
        input()

        if not self.connect():
            print("❌ Failed to connect to MIDI. Please check IAC Driver setup.")
            return

        completed_commands = []

        for command_name in self.PROBLEMATIC_COMMANDS.keys():
            print(f"\n{'='*60}")
            print(f"🎯 PROCESSING: {command_name}")
            print(f"{'='*60}")

            # Step 1: Test current mapping
            print(f"\n📝 Step 1: Testing current mapping...")
            current_works = self.test_current_command(command_name)

            if current_works:
                print(f"✅ Current mapping for {command_name} works! Moving to next command...")
                completed_commands.append(command_name)
                continue

            # Step 2: MIDI Learn discovery
            print(f"\n🎓 Step 2: MIDI Learn discovery...")
            discovered_cc = self.guide_midi_learn(command_name)

            if discovered_cc:
                completed_commands.append(command_name)
                print(f"✅ {command_name} discovered and verified!")
            else:
                print(f"❌ Failed to discover {command_name}")

            # Continue prompt
            if command_name != list(self.PROBLEMATIC_COMMANDS.keys())[-1]:
                cont = input(f"\nContinue to next command? (y/n): ").strip().lower()
                if cont != 'y':
                    break

        # Final report
        self.generate_session_report()

    def generate_session_report(self):
        """Generate comprehensive session report"""
        print(f"\n{'='*60}")
        print("📊 DISCOVERY SESSION REPORT")
        print(f"{'='*60}")

        verified_count = 0
        failed_count = 0
        mapping_updates = []

        for command_name, discovery in self.discoveries.items():
            print(f"\n🎯 {command_name}:")
            print(f"   Status: {discovery.status.value}")
            print(f"   Current CC: {discovery.current_cc}")

            if discovery.discovered_cc:
                print(f"   Discovered CC: {discovery.discovered_cc}")
                if discovery.verification_confirmed:
                    verified_count += 1
                    mapping_updates.append(f"'{command_name}': (MIDIChannel.AI_CONTROL.value, {discovery.discovered_cc}),")
                    print(f"   ✅ VERIFIED and ready for mapping update")
                else:
                    failed_count += 1
                    print(f"   ❌ Discovered but verification failed")
            else:
                failed_count += 1
                print(f"   ❌ No discovery made")

            if discovery.test_results:
                print(f"   Test Results:")
                for result in discovery.test_results:
                    print(f"     • {result}")

        print(f"\n📈 SUMMARY:")
        print(f"   ✅ Verified commands: {verified_count}")
        print(f"   ❌ Failed commands: {failed_count}")
        print(f"   📊 Success rate: {verified_count/(verified_count+failed_count)*100:.1f}%")

        if mapping_updates:
            print(f"\n🔧 MAPPING UPDATES NEEDED:")
            print("Add these lines to traktor_control.py MIDI_MAP:")
            for update in mapping_updates:
                print(f"   {update}")

            update_now = input(f"\nUpdate traktor_control.py mapping file now? (y/n): ").strip().lower()
            if update_now == 'y':
                self.update_mapping_file(mapping_updates)

    def update_mapping_file(self, mapping_updates: List[str]):
        """Update the traktor_control.py mapping file with discovered commands"""
        print(f"\n🔧 Updating traktor_control.py mapping...")

        try:
            # This would be implemented to actually update the file
            # For now, just provide the manual update instructions
            print(f"✅ Manual update required:")
            print(f"1. Open /Users/Fiore/dj/traktor_control.py")
            print(f"2. Find the MIDI_MAP dictionary")
            print(f"3. Update these commands:")
            for update in mapping_updates:
                print(f"   {update}")
            print(f"4. Save the file")
            print(f"5. Test the updated mappings")

        except Exception as e:
            logger.error(f"❌ Auto-update failed: {e}")
            print(f"Please manually update the mapping file")

def main():
    """Main discovery session"""
    config = get_config()
    discovery_tool = MIDILearnDiscovery(config)
    discovery_tool.run_full_discovery_session()

if __name__ == "__main__":
    main()