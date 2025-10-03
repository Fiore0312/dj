#!/usr/bin/env python3
"""
🧪 Batch Transport Command Tester - Traktor MIDI Testing Agent

Systematically tests remaining transport commands:
- deck_c_play (CC 22)
- deck_d_play (CC 23)
- deck_c_cue (CC 27)
- deck_d_cue (CC 88)

CRITICAL RULE: Never confirms functionality without human verification
"""

import time
import sys
import logging
from typing import List, Tuple
from dataclasses import dataclass

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    print("❌ rtmidi not available. Install: pip install python-rtmidi")
    RTMIDI_AVAILABLE = False
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestCommand:
    name: str
    channel: int
    cc: int
    description: str
    expected_behavior: str

class TransportTester:
    """Systematic transport command testing"""

    def __init__(self):
        self.midi_out = None
        self.connected = False

        # Transport commands to test (from traktor_control.py MIDI_MAP)
        self.test_commands = [
            TestCommand(
                name="deck_c_play",
                channel=1,
                cc=22,
                description="Deck C Play/Pause",
                expected_behavior="Deck C starts playing or toggles play/pause"
            ),
            TestCommand(
                name="deck_d_play",
                channel=1,
                cc=23,
                description="Deck D Play/Pause",
                expected_behavior="Deck D starts playing or toggles play/pause"
            ),
            TestCommand(
                name="deck_c_cue",
                channel=1,
                cc=27,
                description="Deck C Cue",
                expected_behavior="Deck C jumps to cue point and pauses"
            ),
            TestCommand(
                name="deck_d_cue",
                channel=1,
                cc=88,
                description="Deck D Cue",
                expected_behavior="Deck D jumps to cue point and pauses"
            )
        ]

        self.test_results = {}

    def connect_to_traktor(self) -> bool:
        """Connect to Traktor via IAC Driver Bus 1"""
        try:
            self.midi_out = rtmidi.MidiOut()
            output_ports = self.midi_out.get_ports()

            print(f"📋 Available MIDI ports: {output_ports}")

            # Find IAC Bus 1
            iac_port_idx = None
            for i, port in enumerate(output_ports):
                if "Bus 1" in port or "IAC" in port.lower():
                    iac_port_idx = i
                    break

            if iac_port_idx is None:
                logger.error("❌ IAC Driver Bus 1 not found")
                return False

            self.midi_out.open_port(iac_port_idx)
            self.connected = True
            logger.info(f"✅ Connected to: {output_ports[iac_port_idx]}")
            return True

        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False

    def send_midi_command(self, channel: int, cc: int, value: int, description: str) -> bool:
        """Send MIDI CC command"""
        if not self.connected or not self.midi_out:
            logger.error("❌ Not connected to MIDI")
            return False

        try:
            # Control Change message: [0xB0 + channel-1, CC, value]
            message = [0xB0 + (channel - 1), cc, value]
            self.midi_out.send_message(message)
            logger.info(f"📤 Sent: CH{channel} CC{cc}={value} ({description})")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send MIDI: {e}")
            return False

    def test_single_command(self, cmd: TestCommand) -> str:
        """Test a single command and get human verification"""
        print("\n" + "="*60)
        print(f"🧪 TESTING: {cmd.name}")
        print(f"📍 Command: Channel {cmd.channel}, CC {cmd.cc}")
        print(f"🎯 Expected: {cmd.expected_behavior}")
        print("="*60)

        # Send the command
        success = self.send_midi_command(cmd.channel, cmd.cc, 127, cmd.description)

        if not success:
            return "FAILED_SEND"

        print(f"\n✅ MIDI command sent successfully!")
        print(f"👁️ Please observe Traktor and check if: {cmd.expected_behavior}")

        # CRITICAL: Human verification required
        while True:
            response = input(f"\n❓ Did you observe the expected behavior for {cmd.name}? (y/n/retry): ").lower().strip()

            if response in ['y', 'yes']:
                print(f"✅ VERIFIED: {cmd.name} is working correctly")
                return "VERIFIED_WORKING"
            elif response in ['n', 'no']:
                print(f"❌ NOT WORKING: {cmd.name} did not produce expected behavior")
                return "NOT_WORKING"
            elif response in ['r', 'retry']:
                print(f"🔄 Retrying {cmd.name}...")
                return self.test_single_command(cmd)  # Recursive retry
            else:
                print("⚠️ Please enter 'y' (yes), 'n' (no), or 'retry'")

    def test_all_commands(self):
        """Test all transport commands systematically"""
        print("🎛️ TRAKTOR TRANSPORT COMMAND BATCH TESTER")
        print("🤖 AI Agent: Systematic Testing with Human Verification")
        print("=" * 70)

        if not self.connect_to_traktor():
            print("❌ Cannot proceed without MIDI connection")
            return

        print(f"\n🎯 Testing {len(self.test_commands)} transport commands...")
        print("⚠️ IMPORTANT: I will ask you to verify each command manually")

        # Test each command
        for i, cmd in enumerate(self.test_commands, 1):
            print(f"\n📊 Progress: {i}/{len(self.test_commands)}")
            result = self.test_single_command(cmd)
            self.test_results[cmd.name] = result

            # Brief pause between tests
            if i < len(self.test_commands):
                print("\n⏱️ Waiting 2 seconds before next test...")
                time.sleep(2)

        # Show final results
        self.show_results()

    def show_results(self):
        """Display comprehensive test results"""
        print("\n" + "="*70)
        print("📊 BATCH TESTING RESULTS")
        print("="*70)

        working_commands = []
        failed_commands = []

        for cmd_name, result in self.test_results.items():
            status_icon = "✅" if result == "VERIFIED_WORKING" else "❌"
            print(f"{status_icon} {cmd_name}: {result}")

            if result == "VERIFIED_WORKING":
                working_commands.append(cmd_name)
            else:
                failed_commands.append(cmd_name)

        print(f"\n📈 SUMMARY:")
        print(f"   ✅ Verified working: {len(working_commands)}")
        print(f"   ❌ Not working/failed: {len(failed_commands)}")
        print(f"   📊 Success rate: {len(working_commands)}/{len(self.test_commands)} ({len(working_commands)/len(self.test_commands)*100:.0f}%)")

        if failed_commands:
            print(f"\n🔍 FAILED COMMANDS NEED MIDI LEARN:")
            for cmd in failed_commands:
                print(f"   • {cmd}")
            print("\n💡 Next step: Use Traktor's MIDI Learn mode to discover correct CC values")

        if working_commands:
            print(f"\n✅ VERIFIED COMMANDS (ready for production):")
            for cmd in working_commands:
                test_cmd = next(tc for tc in self.test_commands if tc.name == cmd)
                print(f"   • {cmd}: Channel {test_cmd.channel}, CC {test_cmd.cc}")

    def disconnect(self):
        """Clean disconnection"""
        if self.midi_out:
            try:
                self.midi_out.close()
                logger.info("✅ MIDI connection closed")
            except:
                pass

def main():
    """Main testing function"""
    tester = TransportTester()

    try:
        tester.test_all_commands()
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        tester.disconnect()
        print("\n👋 Transport batch testing completed")

if __name__ == "__main__":
    main()