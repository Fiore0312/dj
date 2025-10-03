#!/usr/bin/env python3
"""
🎛️ Systematic MIDI Command Tester and Repair Tool
Tests all 107 commands from traktor_control.py with human verification
Discovers correct CCs for failed commands using MIDI learn mode
"""

import time
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False
    print("⚠️ python-rtmidi not available. Install with: pip install python-rtmidi")
    sys.exit(1)

from traktor_control import TraktorController, MIDIChannel
from config import DJConfig

class SystematicMIDITester:
    """Systematic tester for all 107 MIDI commands with repair capabilities"""

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

        # Test results tracking
        self.test_results = {
            "test_date": datetime.now().isoformat(),
            "total_commands": 0,
            "working": 0,
            "failed": 0,
            "conflicts": 0,
            "skipped": 0,
            "working_commands": [],
            "failed_commands": [],
            "conflict_commands": [],
            "discovered_mappings": [],
            "notes": []
        }

        # Organize commands by priority
        self.command_priorities = self._organize_by_priority()

    def _organize_by_priority(self) -> Dict[str, List[Tuple[str, Tuple[int, int]]]]:
        """Organize commands into priority categories based on user requirements"""
        priorities = {
            "CRITICAL": [],
            "IMPORTANT": [],
            "ADVANCED": []
        }

        # Define critical commands (core DJ functionality)
        critical_commands = [
            'deck_a_play', 'deck_b_play', 'deck_a_cue', 'deck_b_cue',
            'deck_a_volume', 'deck_b_volume', 'crossfader', 'master_volume',
            'browser_load_deck_a', 'browser_load_deck_b'
        ]

        # Define important commands (mixing and navigation)
        important_commands = [
            'deck_a_eq_high', 'deck_a_eq_mid', 'deck_a_eq_low',
            'deck_b_eq_high', 'deck_b_eq_mid', 'deck_b_eq_low',
            'deck_a_sync', 'deck_b_sync', 'deck_a_sync_grid', 'deck_b_sync_grid',
            'deck_a_pitch', 'deck_b_pitch',
            'browser_up', 'browser_down', 'browser_scroll_tracks', 'browser_scroll_tree',
            'browser_select_item'
        ]

        # Categorize all commands
        for cmd_name, (channel, cc) in self.traktor.MIDI_MAP.items():
            # Skip aliases
            if any(alias in cmd_name for alias in ['_load_selected', '_scroll_']):
                continue

            if cmd_name in critical_commands:
                priorities["CRITICAL"].append((cmd_name, (channel, cc)))
            elif cmd_name in important_commands:
                priorities["IMPORTANT"].append((cmd_name, (channel, cc)))
            else:
                priorities["ADVANCED"].append((cmd_name, (channel, cc)))

        return priorities

    def _get_command_description(self, cmd_name: str) -> str:
        """Get human-readable description of command"""
        descriptions = {
            # Critical Transport
            'deck_a_play': 'Play/Pause Deck A (trigger)',
            'deck_b_play': 'Play/Pause Deck B (trigger)',
            'deck_a_cue': 'Cue Point Deck A (flash/blink)',
            'deck_b_cue': 'Cue Point Deck B (flash/blink)',

            # Critical Volume
            'deck_a_volume': 'Deck A Volume Fader (0-127)',
            'deck_b_volume': 'Deck B Volume Fader (0-127)',
            'crossfader': 'Crossfader Position (0=A, 64=center, 127=B)',
            'master_volume': 'Master Output Volume (0-127)',

            # Critical Browser Loading
            'browser_load_deck_a': 'Load Selected Track to Deck A',
            'browser_load_deck_b': 'Load Selected Track to Deck B',

            # Important EQ
            'deck_a_eq_high': 'Deck A High EQ (0-127, 64=neutral)',
            'deck_a_eq_mid': 'Deck A Mid EQ (0-127, 64=neutral)',
            'deck_a_eq_low': 'Deck A Low EQ (0-127, 64=neutral)',
            'deck_b_eq_high': 'Deck B High EQ (0-127, 64=neutral)',
            'deck_b_eq_mid': 'Deck B Mid EQ (0-127, 64=neutral)',
            'deck_b_eq_low': 'Deck B Low EQ (0-127, 64=neutral)',

            # Important Sync
            'deck_a_sync': 'Sync Deck A to Master BPM',
            'deck_b_sync': 'Sync Deck B to Master BPM',
            'deck_a_sync_grid': 'Sync Deck A to Grid',
            'deck_b_sync_grid': 'Sync Deck B to Grid',

            # Important Pitch
            'deck_a_pitch': 'Deck A Pitch Adjust (0-127, 64=0%)',
            'deck_b_pitch': 'Deck B Pitch Adjust (0-127, 64=0%)',

            # Important Browser
            'browser_up': 'Browser Scroll Up/Previous Track',
            'browser_down': 'Browser Scroll Down/Next Track',
            'browser_scroll_tracks': 'Scroll Track List',
            'browser_scroll_tree': 'Scroll Tree/Folder List',
            'browser_select_item': 'Select/Enter Current Item'
        }

        return descriptions.get(cmd_name, cmd_name.replace('_', ' ').title())

    def _send_test_sequence(self, channel: int, cc: int, cmd_name: str) -> bool:
        """Send a test sequence for the command"""
        try:
            # Different test sequences based on command type
            if 'play' in cmd_name or 'cue' in cmd_name or 'sync' in cmd_name or 'load' in cmd_name:
                # Trigger commands: send 127 (on)
                self.traktor.midi_out.send_message([0xB0 + (channel - 1), cc, 127])
                print(f"📡 Sent: CC {cc} = 127 (trigger)")
                time.sleep(1.0)

            elif 'volume' in cmd_name or 'crossfader' in cmd_name or 'eq' in cmd_name or 'pitch' in cmd_name:
                # Continuous controls: test sequence
                values = [0, 64, 127, 64]  # min, mid, max, back to mid
                for i, value in enumerate(values):
                    self.traktor.midi_out.send_message([0xB0 + (channel - 1), cc, value])
                    print(f"📡 Sent: CC {cc} = {value} ({['min', 'mid', 'max', 'mid'][i]})")
                    time.sleep(0.8)

            elif 'browser' in cmd_name:
                # Browser commands: trigger
                self.traktor.midi_out.send_message([0xB0 + (channel - 1), cc, 127])
                print(f"📡 Sent: CC {cc} = 127 (browser action)")
                time.sleep(1.0)

            else:
                # Default: trigger command
                self.traktor.midi_out.send_message([0xB0 + (channel - 1), cc, 127])
                print(f"📡 Sent: CC {cc} = 127 (default trigger)")
                time.sleep(1.0)

            return True

        except Exception as e:
            print(f"❌ Error sending MIDI: {e}")
            return False

    def test_command(self, cmd_name: str, channel: int, cc: int, priority: str) -> Dict[str, Any]:
        """Test a single command with human verification"""
        description = self._get_command_description(cmd_name)

        print(f"\n{'='*70}")
        print(f"🧪 TESTING: {cmd_name}")
        print(f"{'='*70}")
        print(f"📝 Description: {description}")
        print(f"📡 MIDI: Channel {channel}, CC {cc}")
        print(f"🎯 Priority: {priority}")
        print(f"{'─'*70}")

        # Check if command is already marked as working in traktor_control.py
        is_marked_working = "✅" in str(self.traktor.MIDI_MAP.get(cmd_name, ""))
        if is_marked_working:
            print("✅ This command is marked as TESTED/WORKING in traktor_control.py")
        else:
            print("⚠️ This command is marked as NOT TESTED in traktor_control.py")

        # Send test sequence
        print(f"\n🎛️ Sending test sequence...")
        sent = self._send_test_sequence(channel, cc, cmd_name)

        if not sent:
            return {
                "status": "error",
                "cc": cc,
                "name": cmd_name,
                "description": description,
                "error": "Failed to send MIDI"
            }

        # Human verification
        while True:
            print(f"\n{'─'*70}")
            print(f"👁️ HUMAN VERIFICATION REQUIRED")
            print(f"{'─'*70}")
            print(f"❓ Did you observe the expected behavior in Traktor?")
            print(f"   Expected: {description}")

            response = input("\n🎯 Response (y=WORKING/n=FAILED/r=REPEAT/c=CONFLICT/s=SKIP/q=QUIT): ").lower().strip()

            if response == 'y':
                print("✅ WORKING - Command verified by user")
                return {
                    "status": "working",
                    "cc": cc,
                    "name": cmd_name,
                    "description": description,
                    "verified_by_human": True
                }

            elif response == 'n':
                print("❌ FAILED - Command not working")
                # Offer MIDI learn mode
                learn = input("🎓 Start MIDI learn mode to discover correct CC? (y/n): ").lower().strip()
                if learn == 'y':
                    discovered_cc = self._midi_learn_mode(cmd_name, description)
                    return {
                        "status": "failed",
                        "cc": cc,
                        "name": cmd_name,
                        "description": description,
                        "discovered_cc": discovered_cc,
                        "needs_learn_mode": True
                    }
                else:
                    return {
                        "status": "failed",
                        "cc": cc,
                        "name": cmd_name,
                        "description": description,
                        "needs_learn_mode": True
                    }

            elif response == 'r':
                print("🔁 REPEATING test sequence...")
                self._send_test_sequence(channel, cc, cmd_name)
                # Loop continues to ask again

            elif response == 'c':
                conflict_desc = input("🔄 Describe the conflict (what else moved?): ").strip()
                print(f"⚠️ CONFLICT - {conflict_desc}")
                return {
                    "status": "conflict",
                    "cc": cc,
                    "name": cmd_name,
                    "description": description,
                    "conflict_description": conflict_desc
                }

            elif response == 's':
                print("⏭️ SKIPPED")
                return {
                    "status": "skipped",
                    "cc": cc,
                    "name": cmd_name,
                    "description": description
                }

            elif response == 'q':
                return {"status": "quit"}

            else:
                print("❌ Invalid response. Use:")
                print("   y = WORKING ✅")
                print("   n = FAILED ❌")
                print("   r = REPEAT test 🔁")
                print("   c = CONFLICT ⚠️")
                print("   s = SKIP ⏭️")
                print("   q = QUIT and save")

    def _midi_learn_mode(self, cmd_name: str, description: str) -> Optional[int]:
        """Guide user through MIDI learn mode to discover correct CC"""
        print(f"\n{'='*70}")
        print(f"🎓 MIDI LEARN MODE for {cmd_name}")
        print(f"{'='*70}")
        print(f"📝 Function: {description}")
        print()
        print("📋 INSTRUCTIONS:")
        print("1. In Traktor, go to Preferences > Controller Manager")
        print("2. Select 'Generic MIDI' or your controller")
        print("3. Click 'Learn' button")
        print("4. Click on the control in Traktor that should respond to this command")
        print("5. Traktor will show the CC number it expects")
        print("6. Note down the CC number")
        print("7. Exit learn mode")
        print()

        input("Press ENTER when you've completed the learn mode process...")

        while True:
            cc_input = input("🔢 What CC number did Traktor show? (or 'none' if not found): ").strip()

            if cc_input.lower() == 'none':
                print("❌ No CC discovered via learn mode")
                return None

            try:
                discovered_cc = int(cc_input)
                print(f"✅ Discovered CC: {discovered_cc}")

                # Test the discovered CC
                test_discovered = input(f"🧪 Test the discovered CC {discovered_cc} now? (y/n): ").lower().strip()
                if test_discovered == 'y':
                    print(f"📡 Testing discovered CC {discovered_cc}...")
                    self._send_test_sequence(1, discovered_cc, cmd_name)  # Use channel 1

                    works = input("✅ Does the discovered CC work? (y/n): ").lower().strip()
                    if works == 'y':
                        print(f"🎉 SUCCESS! CC {discovered_cc} works for {cmd_name}")
                        return discovered_cc
                    else:
                        print(f"❌ CC {discovered_cc} doesn't work either")
                        retry = input("🔄 Try learn mode again? (y/n): ").lower().strip()
                        if retry != 'y':
                            return None
                        # Loop continues for retry
                else:
                    return discovered_cc

            except ValueError:
                print("❌ Please enter a valid CC number (0-127) or 'none'")

    def test_priority_group(self, priority: str, commands: List[Tuple[str, Tuple[int, int]]]) -> str:
        """Test all commands in a priority group"""
        print(f"\n{'='*80}")
        print(f"🎯 TESTING {priority} PRIORITY COMMANDS")
        print(f"{'='*80}")
        print(f"📊 {len(commands)} commands to test")
        print()

        # Show priority-specific instructions
        if priority == "CRITICAL":
            print("🔥 CRITICAL COMMANDS - Core DJ functionality")
            print("   These MUST work for basic DJ operations")
            print("   ▶️ Play/Pause, Cue, Volume, Crossfader, Track Loading")

        elif priority == "IMPORTANT":
            print("⚡ IMPORTANT COMMANDS - Mixing and navigation")
            print("   These should work for professional mixing")
            print("   🎛️ EQ, Sync, Pitch, Browser Navigation")

        elif priority == "ADVANCED":
            print("🎪 ADVANCED COMMANDS - Professional features")
            print("   🔄 Loops, Hotcues, Beatjump, Effects, etc.")

        print(f"\n{'─'*80}")

        for idx, (cmd_name, (channel, cc)) in enumerate(commands, 1):
            print(f"\n📍 Progress: {idx}/{len(commands)} in {priority} priority")

            result = self.test_command(cmd_name, channel, cc, priority)

            if result["status"] == "quit":
                return "quit"
            elif result["status"] == "working":
                self.test_results["working"] += 1
                self.test_results["working_commands"].append(result)
            elif result["status"] == "failed":
                self.test_results["failed"] += 1
                self.test_results["failed_commands"].append(result)
                if result.get("discovered_cc"):
                    self.test_results["discovered_mappings"].append({
                        "command": cmd_name,
                        "original_cc": cc,
                        "discovered_cc": result["discovered_cc"],
                        "description": result["description"]
                    })
            elif result["status"] == "conflict":
                self.test_results["conflicts"] += 1
                self.test_results["conflict_commands"].append(result)
            elif result["status"] == "skipped":
                self.test_results["skipped"] += 1

            self.test_results["total_commands"] += 1

        # Priority group summary
        print(f"\n{'='*80}")
        print(f"✅ {priority} PRIORITY GROUP COMPLETED")
        print(f"{'='*80}")
        print(f"📊 Commands tested: {len(commands)}")
        print(f"✅ Working: {len([r for r in [self.test_results['working_commands'][-len(commands):] if self.test_results['working_commands'] else []] if r.get('status') == 'working'])}")
        print(f"❌ Failed: {len([r for r in [self.test_results['failed_commands'][-len(commands):] if self.test_results['failed_commands'] else []] if r.get('status') == 'failed'])}")
        print(f"⚠️ Conflicts: {len([r for r in [self.test_results['conflict_commands'][-len(commands):] if self.test_results['conflict_commands'] else []] if r.get('status') == 'conflict'])}")
        print(f"{'='*80}")

        return "continue"

    def run_systematic_test(self):
        """Run systematic test of all commands by priority"""
        print(f"\n{'='*80}")
        print(f"🎛️ SYSTEMATIC MIDI COMMAND TESTER")
        print(f"{'='*80}")
        print(f"📊 Total commands to test: {sum(len(cmds) for cmds in self.command_priorities.values())}")
        print(f"🎯 Priority groups: {len(self.command_priorities)}")
        print()

        print("📋 SETUP CHECKLIST:")
        print("✅ Traktor Pro 3 is running")
        print("✅ IAC Driver Bus 1 is enabled")
        print("✅ At least one track loaded in Deck A")
        print("✅ Browser view is visible (F3)")
        print("✅ You're ready to observe Traktor and verify commands")
        print()

        input("🚀 Press ENTER when ready to start testing...")

        # Test each priority group
        for priority, commands in self.command_priorities.items():
            if not commands:
                continue

            result = self.test_priority_group(priority, commands)

            if result == "quit":
                print("\n⚠️ Test interrupted by user")
                break

            # Ask to continue to next priority
            if priority != list(self.command_priorities.keys())[-1]:  # Not the last group
                cont = input(f"\n➡️ Continue to next priority group? (ENTER=yes, q=quit): ").lower()
                if cont == 'q':
                    break

        # Save results and show summary
        self._save_comprehensive_results()
        self._print_final_summary()

    def _save_comprehensive_results(self):
        """Save comprehensive test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON report with all data
        json_file = Path(f"systematic_test_results_{timestamp}.json")
        with open(json_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Comprehensive JSON report: {json_file}")

        # Human-readable summary report
        txt_file = Path(f"systematic_test_summary_{timestamp}.txt")
        with open(txt_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("SYSTEMATIC MIDI COMMAND TEST RESULTS\n")
            f.write("="*80 + "\n\n")
            f.write(f"Test Date: {self.test_results['test_date']}\n")
            f.write(f"Total Commands: {self.test_results['total_commands']}\n")
            f.write(f"✅ Working: {self.test_results['working']}\n")
            f.write(f"❌ Failed: {self.test_results['failed']}\n")
            f.write(f"⚠️ Conflicts: {self.test_results['conflicts']}\n")
            f.write(f"⏭️ Skipped: {self.test_results['skipped']}\n\n")

            # Working commands
            if self.test_results['working_commands']:
                f.write("="*80 + "\n")
                f.write("WORKING COMMANDS\n")
                f.write("="*80 + "\n\n")
                for cmd in self.test_results['working_commands']:
                    f.write(f"✅ CC {cmd['cc']} - {cmd['description']}\n")
                    f.write(f"   Command: {cmd['name']}\n\n")

            # Failed commands
            if self.test_results['failed_commands']:
                f.write("="*80 + "\n")
                f.write("FAILED COMMANDS\n")
                f.write("="*80 + "\n\n")
                for cmd in self.test_results['failed_commands']:
                    f.write(f"❌ CC {cmd['cc']} - {cmd['description']}\n")
                    f.write(f"   Command: {cmd['name']}\n")
                    if cmd.get('discovered_cc'):
                        f.write(f"   🎓 Discovered CC: {cmd['discovered_cc']}\n")
                    f.write("\n")

            # Conflict commands
            if self.test_results['conflict_commands']:
                f.write("="*80 + "\n")
                f.write("CONFLICT COMMANDS\n")
                f.write("="*80 + "\n\n")
                for cmd in self.test_results['conflict_commands']:
                    f.write(f"⚠️ CC {cmd['cc']} - {cmd['description']}\n")
                    f.write(f"   Command: {cmd['name']}\n")
                    f.write(f"   Conflict: {cmd.get('conflict_description', 'Unknown')}\n\n")

            # Discovered mappings summary
            if self.test_results['discovered_mappings']:
                f.write("="*80 + "\n")
                f.write("DISCOVERED CORRECT MAPPINGS\n")
                f.write("="*80 + "\n\n")
                for mapping in self.test_results['discovered_mappings']:
                    f.write(f"🎓 {mapping['command']}: CC {mapping['original_cc']} → CC {mapping['discovered_cc']}\n")
                    f.write(f"   Description: {mapping['description']}\n\n")

        print(f"📄 Human-readable summary: {txt_file}")

        # Create repair recommendations
        repair_file = Path(f"traktor_control_repair_recommendations_{timestamp}.py")
        with open(repair_file, 'w') as f:
            f.write("# TRAKTOR CONTROL REPAIR RECOMMENDATIONS\n")
            f.write(f"# Generated: {self.test_results['test_date']}\n\n")
            f.write("# SUGGESTED UPDATES FOR traktor_control.py MIDI_MAP:\n\n")

            for mapping in self.test_results['discovered_mappings']:
                f.write(f"# {mapping['command']}: CHANGE CC {mapping['original_cc']} → CC {mapping['discovered_cc']}\n")
                f.write(f"'{mapping['command']}': (MIDIChannel.AI_CONTROL.value, {mapping['discovered_cc']}),  # 🎓 Discovered via learn mode\n\n")

        print(f"🔧 Repair recommendations: {repair_file}")

    def _print_final_summary(self):
        """Print comprehensive final summary"""
        print(f"\n{'='*80}")
        print(f"📊 SYSTEMATIC TEST FINAL SUMMARY")
        print(f"{'='*80}")

        total = self.test_results['total_commands']
        working = self.test_results['working']
        failed = self.test_results['failed']
        conflicts = self.test_results['conflicts']
        skipped = self.test_results['skipped']

        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Commands Tested: {total}")
        print(f"   ✅ Working: {working} ({working/max(total,1)*100:.1f}%)")
        print(f"   ❌ Failed: {failed} ({failed/max(total,1)*100:.1f}%)")
        print(f"   ⚠️ Conflicts: {conflicts} ({conflicts/max(total,1)*100:.1f}%)")
        print(f"   ⏭️ Skipped: {skipped} ({skipped/max(total,1)*100:.1f}%)")

        # Health assessment
        health_score = (working / max(total, 1)) * 100
        if health_score >= 80:
            health_status = "🟢 EXCELLENT"
        elif health_score >= 60:
            health_status = "🟡 GOOD"
        elif health_score >= 40:
            health_status = "🟠 NEEDS WORK"
        else:
            health_status = "🔴 CRITICAL"

        print(f"\n🏥 SYSTEM HEALTH: {health_status} ({health_score:.1f}%)")

        # Priority breakdown
        print(f"\n🎯 BY PRIORITY:")
        for priority in ["CRITICAL", "IMPORTANT", "ADVANCED"]:
            priority_commands = [cmd for cmd in self.test_results['working_commands']
                               if cmd.get('name') in [c[0] for c in self.command_priorities.get(priority, [])]]
            priority_total = len(self.command_priorities.get(priority, []))
            priority_working = len(priority_commands)

            if priority_total > 0:
                print(f"   {priority}: {priority_working}/{priority_total} working ({priority_working/priority_total*100:.0f}%)")

        # Critical issues
        if failed > 0:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            print(f"   {failed} commands are not working correctly")
            if self.test_results['discovered_mappings']:
                print(f"   🎓 {len(self.test_results['discovered_mappings'])} correct CCs discovered via learn mode")
                print("   📝 See repair recommendations file for updates")

        if conflicts > 0:
            print(f"\n⚠️ CONFLICTS DETECTED:")
            print(f"   {conflicts} commands have conflicting CC assignments")
            print("   🔧 These need alternative CC numbers")

        # Next steps
        print(f"\n🎯 RECOMMENDED NEXT STEPS:")
        if failed > 0:
            print("   1. 🔧 Update traktor_control.py with discovered CC mappings")
            print("   2. 🎓 Use MIDI learn mode for remaining failed commands")
        if conflicts > 0:
            print("   3. ⚠️ Resolve CC conflicts by finding alternative numbers")
        if working < total:
            print("   4. 🧪 Re-test updated mappings")
        if health_score >= 80:
            print("   🎉 System is in excellent shape! Consider testing advanced features.")

        print(f"\n{'='*80}")
        print(f"✅ SYSTEMATIC TESTING COMPLETED")
        print(f"{'='*80}\n")


def main():
    """Main entry point"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                     SYSTEMATIC MIDI COMMAND TESTER                        ║
║                         FOR TRAKTOR PRO 3                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

🎯 This tool will systematically test ALL 107 commands from traktor_control.py

📋 WHAT IT DOES:
✅ Tests commands in priority order (CRITICAL → IMPORTANT → ADVANCED)
✅ Requires human verification for each command
✅ Uses MIDI learn mode to discover correct CCs for failed commands
✅ Identifies CC conflicts where multiple commands control same function
✅ Generates comprehensive reports and repair recommendations

🔧 WHAT YOU NEED:
✅ Traktor Pro 3 running with at least one track loaded
✅ IAC Driver Bus 1 enabled in Audio MIDI Setup
✅ Browser view visible (press F3)
✅ Your attention to observe and verify each command

⚠️ IMPORTANT: This requires human verification for each command!
   You MUST watch Traktor and confirm whether each command works.

🚀 Ready to systematically test and repair your MIDI mapping?
""")

    try:
        tester = SystematicMIDITester()
        tester.run_systematic_test()
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