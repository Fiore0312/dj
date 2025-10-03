#!/usr/bin/env python3
"""
🎛️ FASE 2: VOLUME CONTROLS TESTER
Tests the 4 critical volume commands with graduated sequences and human verification
"""

import time
import sys
from datetime import datetime

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False
    print("⚠️ python-rtmidi not available. Install with: pip install python-rtmidi")
    sys.exit(1)

from traktor_control import TraktorController, MIDIChannel
from config import DJConfig

class Phase2VolumeTester:
    """Tester for Phase 2: Volume Controls with graduated sequences"""

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

        # Phase 2 commands to test
        self.phase2_commands = {
            'deck_a_volume': (1, 28, 'Deck A Volume Fader (should move channel fader up/down)'),
            'deck_b_volume': (1, 29, 'Deck B Volume Fader (⚠️ KNOWN CONFLICT: may move pitch instead)'),
            'crossfader': (1, 32, 'Crossfader Position (left=0, center=64, right=127)'),
            'master_volume': (1, 33, 'Master Output Volume (may not be visible in GUI)')
        }

        # Test results
        self.results = {
            'test_date': datetime.now().isoformat(),
            'phase': 'PHASE 2: VOLUME CONTROLS',
            'working': [],
            'failed': [],
            'conflicts': [],
            'notes': []
        }

    def test_volume_command(self, cmd_name: str, channel: int, cc: int, description: str):
        """Test a volume command with graduated sequence"""
        print(f"\n{'='*80}")
        print(f"🎛️ TESTING: {cmd_name}")
        print(f"{'='*80}")
        print(f"📝 Description: {description}")
        print(f"📡 MIDI: Channel {channel}, CC {cc}")
        print(f"⚠️ SPECIAL NOTE for CC 29: Known conflict - may move pitch instead of volume!")
        print(f"{'─'*80}")

        # Send graduated sequence: 0 → 127 → 64 (low → high → medium)
        sequence = [
            (0, "MINIMUM (silent/left)"),
            (64, "MIDDLE (50%/center)"),
            (127, "MAXIMUM (full/right)"),
            (64, "BACK TO MIDDLE")
        ]

        print(f"\n🎛️ Sending graduated sequence for {cmd_name}...")
        print("   Watch for smooth fader movement in Traktor!")

        for i, (value, description_val) in enumerate(sequence):
            try:
                # Send MIDI CC message
                midi_msg = [0xB0 + (channel - 1), cc, value]
                self.traktor.midi_out.send_message(midi_msg)

                print(f"📡 Step {i+1}/4: CC {cc} = {value:3d} ({description_val})")

                # Longer pause for volume changes to be observed
                time.sleep(2.0)

            except Exception as e:
                print(f"❌ Error sending MIDI: {e}")
                return False

        print(f"\n✅ Sequence completed for {cmd_name}")
        return True

    def run_phase2_test(self):
        """Run Phase 2 volume controls test"""
        print(f"\n{'='*80}")
        print(f"🎯 FASE 2: VOLUME CONTROLS TESTING")
        print(f"{'='*80}")
        print(f"📊 Commands to test: {len(self.phase2_commands)}")
        print()
        print("🎯 FOCUS: Test each volume control with graduated sequences")
        print("⚠️ SPECIAL ATTENTION: CC 29 should show the known conflict!")
        print()
        print("📋 WHAT TO WATCH FOR:")
        print("✅ Deck A Volume (CC 28): Channel fader should move smoothly")
        print("⚠️ Deck B Volume (CC 29): May move PITCH instead of volume!")
        print("✅ Crossfader (CC 32): Crossfader should move left/center/right")
        print("✅ Master Volume (CC 33): Master output level (may not be visible)")
        print()

        # Test each command
        for i, (cmd_name, (channel, cc, description)) in enumerate(self.phase2_commands.items(), 1):
            print(f"\n📍 Progress: {i}/{len(self.phase2_commands)} - Testing {cmd_name}")

            success = self.test_volume_command(cmd_name, channel, cc, description)

            if not success:
                print(f"❌ Failed to send MIDI for {cmd_name}")
                self.results['failed'].append({
                    'name': cmd_name,
                    'cc': cc,
                    'error': 'MIDI send failed'
                })
                continue

            # Give time to observe
            print(f"\n⏰ Observe Traktor for 3 seconds...")
            time.sleep(3.0)

        # Show summary and next steps
        self._show_phase2_summary()

    def _show_phase2_summary(self):
        """Show Phase 2 summary and next steps"""
        print(f"\n{'='*80}")
        print(f"✅ FASE 2: VOLUME CONTROLS COMPLETED")
        print(f"{'='*80}")
        print()
        print("🎯 NEXT STEPS:")
        print()
        print("1. **HUMAN VERIFICATION REQUIRED**:")
        print("   ✅ Did CC 28 (deck_a_volume) move the Deck A channel fader?")
        print("   ⚠️ Did CC 29 (deck_b_volume) move PITCH instead of volume? (conflict)")
        print("   ✅ Did CC 32 (crossfader) move the crossfader left/center/right?")
        print("   ✅ Did CC 33 (master_volume) affect master output level?")
        print()
        print("2. **EXPECTED CONFLICT**:")
        print("   ⚠️ CC 29 should move PITCH slider instead of volume fader")
        print("   This confirms the known conflict in the mapping")
        print()
        print("3. **AFTER PHASE 2 - MIDI LEARN FOR CUE COMMANDS**:")
        print("   📝 CC 39 (deck_a_cue) - FAILED in Phase 1")
        print("   📝 CC 26 (deck_b_cue) - FAILED in Phase 1")
        print("   🎓 Use MIDI Learn mode to discover correct CCs")
        print()
        print("4. **PREPARATION FOR PHASE 3**:")
        print("   🎛️ Next phase will test EQ controls (6 commands)")
        print("   📊 Then browser navigation (5 commands)")
        print()
        print(f"{'='*80}")
        print("📝 **PLEASE CONFIRM EACH COMMAND RESULT MANUALLY**")
        print("📝 **Note any conflicts or unexpected behavior**")
        print(f"{'='*80}")

def main():
    """Main entry point"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    FASE 2: VOLUME CONTROLS TESTER                        ║
║                         FOR TRAKTOR PRO 3                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

🎯 This tool tests the 4 critical volume commands with graduated sequences

📋 COMMANDS TO TEST:
✅ CC 28 (deck_a_volume) - Deck A Channel Fader
⚠️ CC 29 (deck_b_volume) - Deck B Channel Fader (CONFLICT EXPECTED)
✅ CC 32 (crossfader) - Crossfader Position
✅ CC 33 (master_volume) - Master Output Level

🔧 WHAT YOU NEED:
✅ Traktor Pro 3 running with tracks loaded
✅ IAC Driver Bus 1 enabled
✅ Clear view of all faders and controls
✅ Your attention to observe each fader movement

⚠️ SPECIAL: CC 29 should demonstrate the known pitch/volume conflict!
""")

    try:
        tester = Phase2VolumeTester()
        tester.run_phase2_test()
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