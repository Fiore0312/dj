#!/usr/bin/env python3
"""
🐌 SLOW METHODICAL TRAKTOR MIDI TESTER
Tests critical commands one at a time with extended pauses for careful observation
Human verification required for every single command
"""

import time
import sys
from datetime import datetime
from pathlib import Path

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False
    print("⚠️ python-rtmidi not available. Install with: pip install python-rtmidi")
    sys.exit(1)

from traktor_control import TraktorController, MIDIChannel
from config import DJConfig

class SlowMethodicalTester:
    """Ultra-slow methodical tester for critical commands only"""

    def __init__(self):
        # Initialize config and controller
        self.config = DJConfig()
        self.traktor = TraktorController(self.config)

        # Connect to Traktor
        print("\n🔌 Connecting to Traktor via IAC Driver...")
        if not self.traktor.connect_with_gil_safety(output_only=True):
            print("❌ Failed to connect to Traktor MIDI")
            print("   Please check:")
            print("   1. IAC Driver Bus 1 is enabled in Audio MIDI Setup")
            print("   2. Traktor Pro 3 is running")
            sys.exit(1)
        print("✅ Connected to Traktor MIDI successfully!\n")

        # Critical commands for slow testing
        self.critical_commands = [
            # PHASE 1: TRANSPORT (4 commands)
            ('deck_a_play', 20, 'Play/Pause Deck A (should start/stop track A)'),
            ('deck_b_play', 21, 'Play/Pause Deck B (should start/stop track B)'),
            ('deck_a_cue', 39, 'Cue Point Deck A (should jump to cue point)'),
            ('deck_b_cue', 26, 'Cue Point Deck B (should jump to cue point)'),

            # PHASE 2: VOLUME (4 commands)
            ('deck_a_volume', 28, 'Deck A Volume Fader (should change deck A volume)'),
            ('deck_b_volume', 29, 'Deck B Volume Fader (should change deck B volume) ⚠️ KNOWN CONFLICT'),
            ('crossfader', 32, 'Crossfader Position (should move crossfader)'),
            ('master_volume', 33, 'Master Output Volume (should change master level)'),

            # PHASE 3: BROWSER LOADING (2 commands)
            ('browser_load_deck_a', 43, 'Load Selected Track to Deck A (should load highlighted track to A)'),
            ('browser_load_deck_b', 44, 'Load Selected Track to Deck B (should load highlighted track to B)')
        ]

        self.test_results = []

    def announce_command(self, phase: str, cmd_num: int, total_in_phase: int, cmd_name: str, cc: int, description: str):
        """Clearly announce what command we're about to test"""
        print(f"\n{'='*80}")
        print(f"🎯 {phase}")
        print(f"{'='*80}")
        print(f"📍 Command {cmd_num}/{total_in_phase} in this phase")
        print(f"🎛️ Testing: {cmd_name}")
        print(f"📡 MIDI: CC {cc}")
        print(f"📝 Expected: {description}")
        print(f"{'─'*80}")
        print(f"⏰ Preparing to send MIDI command in 3 seconds...")
        print(f"👁️ Watch Traktor carefully for the expected behavior!")

        # Countdown
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        print("   🚀 SENDING NOW!")

    def send_command_slowly(self, cmd_name: str, cc: int, description: str):
        """Send command with appropriate test sequence"""
        channel = 1  # AI_CONTROL channel

        try:
            if 'play' in cmd_name or 'cue' in cmd_name or 'load' in cmd_name:
                # Trigger commands: send 127 (on)
                self.traktor.midi_out.send_message([0xB0 + (channel - 1), cc, 127])
                print(f"📡 Sent: CC {cc} = 127 (trigger)")
                time.sleep(1.5)

            elif 'volume' in cmd_name or 'crossfader' in cmd_name:
                # Volume/fader commands: slow sequence with pauses
                print(f"📡 Testing {cmd_name} with slow sequence:")

                # 0 → 127 → 64 with extended pauses
                values = [0, 127, 64]
                descriptions = ['MINIMUM (0)', 'MAXIMUM (127)', 'MIDDLE (64)']

                for value, desc in zip(values, descriptions):
                    print(f"   Sending: CC {cc} = {value} ({desc})")
                    self.traktor.midi_out.send_message([0xB0 + (channel - 1), cc, value])
                    time.sleep(2.0)  # 2 second pause between each value

            else:
                # Default: trigger
                self.traktor.midi_out.send_message([0xB0 + (channel - 1), cc, 127])
                print(f"📡 Sent: CC {cc} = 127 (default trigger)")
                time.sleep(1.5)

            return True

        except Exception as e:
            print(f"❌ Error sending MIDI: {e}")
            return False

    def get_human_verification(self, cmd_name: str, description: str) -> str:
        """Get human verification with clear options"""
        print(f"\n{'─'*80}")
        print(f"👁️ HUMAN VERIFICATION REQUIRED")
        print(f"{'─'*80}")
        print(f"❓ Did you observe the expected behavior in Traktor?")
        print(f"   Expected: {description}")
        print(f"   Command: {cmd_name}")
        print(f"{'─'*80}")

        while True:
            response = input("\n🎯 Your response (y=WORKING/n=FAILED/r=REPEAT/s=SKIP/q=QUIT): ").lower().strip()

            if response in ['y', 'n', 'r', 's', 'q']:
                return response
            else:
                print("❌ Invalid response. Please use:")
                print("   y = WORKING ✅ (command worked as expected)")
                print("   n = FAILED ❌ (command didn't work)")
                print("   r = REPEAT 🔁 (test again)")
                print("   s = SKIP ⏭️ (skip this command)")
                print("   q = QUIT 🚪 (stop testing)")

    def test_single_command(self, phase: str, cmd_num: int, total_in_phase: int, cmd_name: str, cc: int, description: str):
        """Test a single command with full slow methodology"""

        # Announce what we're testing
        self.announce_command(phase, cmd_num, total_in_phase, cmd_name, cc, description)

        while True:  # Repeat until we get a definitive answer
            # Send the command
            sent = self.send_command_slowly(cmd_name, cc, description)

            if not sent:
                print(f"❌ Failed to send MIDI for {cmd_name}")
                self.test_results.append({
                    'command': cmd_name,
                    'cc': cc,
                    'status': 'error',
                    'description': description
                })
                return

            # 4-5 second observation pause
            print(f"\n⏳ Observation pause - watch Traktor for 4 seconds...")
            time.sleep(4)

            # Get human verification
            response = self.get_human_verification(cmd_name, description)

            if response == 'y':
                print("✅ VERIFIED WORKING")
                self.test_results.append({
                    'command': cmd_name,
                    'cc': cc,
                    'status': 'working',
                    'description': description
                })
                break

            elif response == 'n':
                print("❌ VERIFIED FAILED")
                self.test_results.append({
                    'command': cmd_name,
                    'cc': cc,
                    'status': 'failed',
                    'description': description
                })
                break

            elif response == 'r':
                print("🔁 REPEATING test...")
                continue  # Repeat the test

            elif response == 's':
                print("⏭️ SKIPPED")
                self.test_results.append({
                    'command': cmd_name,
                    'cc': cc,
                    'status': 'skipped',
                    'description': description
                })
                break

            elif response == 'q':
                print("🚪 QUITTING test session")
                return "quit"

        # Pause before next command
        print(f"\n⏸️ 4-second pause before next command...")
        time.sleep(4)

    def run_slow_test(self):
        """Run the complete slow methodical test"""
        print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                     SLOW METHODICAL MIDI TESTER                          ║
║                         TRAKTOR CRITICAL COMMANDS                         ║
╚════════════════════════════════════════════════════════════════════════════╝

🐌 SLOW TESTING METHODOLOGY:
   • ONE command at a time with 4-5 second pauses
   • Clear announcements before each test
   • Visual verification required from human
   • Multiple test sequences for volume/faders
   • Total commands: {len(self.critical_commands)}

📋 SETUP VERIFICATION:
   ✅ Traktor Pro 3 is running and visible
   ✅ At least one track loaded in Deck A and Deck B
   ✅ Browser view is open (press F3 in Traktor)
   ✅ Tracks are selected in browser for loading tests
   ✅ You're ready to observe each command carefully

⚠️ CRITICAL: You MUST watch Traktor and verify each command!
   This test requires your full attention and confirmation.
        """)

        input("\n🚀 Press ENTER when you're ready to start the slow methodical test...")

        # Group commands by phase
        phases = [
            ("PHASE 1: TRANSPORT CONTROLS", self.critical_commands[0:4]),
            ("PHASE 2: VOLUME CONTROLS", self.critical_commands[4:8]),
            ("PHASE 3: BROWSER LOADING", self.critical_commands[8:10])
        ]

        for phase_name, phase_commands in phases:
            print(f"\n{'='*80}")
            print(f"🚀 STARTING {phase_name}")
            print(f"{'='*80}")
            print(f"📊 {len(phase_commands)} commands in this phase")

            for idx, (cmd_name, cc, description) in enumerate(phase_commands, 1):
                result = self.test_single_command(
                    phase_name, idx, len(phase_commands),
                    cmd_name, cc, description
                )

                if result == "quit":
                    print("\n⚠️ Test session terminated by user")
                    self.print_summary()
                    return

            # Phase completion
            print(f"\n✅ {phase_name} COMPLETED")

            # Ask to continue to next phase (except for last phase)
            if phase_name != phases[-1][0]:
                cont = input(f"\n➡️ Continue to next phase? (ENTER=yes, q=quit): ").lower()
                if cont == 'q':
                    break

        print("\n🎉 ALL PHASES COMPLETED!")
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print(f"\n{'='*80}")
        print(f"📊 SLOW METHODICAL TEST SUMMARY")
        print(f"{'='*80}")

        working = [r for r in self.test_results if r['status'] == 'working']
        failed = [r for r in self.test_results if r['status'] == 'failed']
        skipped = [r for r in self.test_results if r['status'] == 'skipped']
        errors = [r for r in self.test_results if r['status'] == 'error']

        total = len(self.test_results)

        print(f"\n📈 RESULTS:")
        print(f"   Total Commands Tested: {total}")
        print(f"   ✅ Working: {len(working)} ({len(working)/max(total,1)*100:.1f}%)")
        print(f"   ❌ Failed: {len(failed)} ({len(failed)/max(total,1)*100:.1f}%)")
        print(f"   ⏭️ Skipped: {len(skipped)} ({len(skipped)/max(total,1)*100:.1f}%)")
        print(f"   ⚠️ Errors: {len(errors)} ({len(errors)/max(total,1)*100:.1f}%)")

        if working:
            print(f"\n✅ WORKING COMMANDS:")
            for cmd in working:
                print(f"   CC {cmd['cc']}: {cmd['command']} - {cmd['description']}")

        if failed:
            print(f"\n❌ FAILED COMMANDS:")
            for cmd in failed:
                print(f"   CC {cmd['cc']}: {cmd['command']} - {cmd['description']}")

        if skipped:
            print(f"\n⏭️ SKIPPED COMMANDS:")
            for cmd in skipped:
                print(f"   CC {cmd['cc']}: {cmd['command']} - {cmd['description']}")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"slow_test_results_{timestamp}.txt"

        with open(results_file, 'w') as f:
            f.write("SLOW METHODICAL TEST RESULTS\n")
            f.write("="*50 + "\n\n")
            f.write(f"Test Date: {datetime.now().isoformat()}\n")
            f.write(f"Total: {total}, Working: {len(working)}, Failed: {len(failed)}\n\n")

            for result in self.test_results:
                f.write(f"{result['status'].upper()}: CC {result['cc']} - {result['command']}\n")
                f.write(f"  Description: {result['description']}\n\n")

        print(f"\n💾 Results saved to: {results_file}")
        print(f"{'='*80}")


def main():
    """Main entry point for slow methodical testing"""
    try:
        tester = SlowMethodicalTester()
        tester.run_slow_test()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()