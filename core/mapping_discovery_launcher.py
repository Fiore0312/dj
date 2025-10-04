#!/usr/bin/env python3
"""
🎛️ Mapping Discovery Launcher - Complete MIDI Control Discovery Suite
Centralized launcher for all Traktor control mapping discovery tools
"""

import subprocess
import sys
import os
from pathlib import Path

class MappingDiscoveryLauncher:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent  # Go up one level from core/
        self.helpers_dir = self.base_dir / 'helpers'

        # Available discovery tools
        self.tools = {
            'fx': {
                'name': 'FX Units (2/3/4) Helper',
                'scripts': [
                    'helpers/fx2_learn_helper.py',
                    'helpers/fx3_learn_helper.py',
                    'helpers/fx4_learn_helper.py',
                    'helpers/complete_fx_learn_helper.py'
                ],
                'description': 'Configure FX Units 2, 3, 4 using Learn mode',
                'status': '✅ COMPLETED',
                'priority': 'DONE'
            },
            'sync_cue': {
                'name': 'Sync & Cue Learn Helper',
                'scripts': ['helpers/sync_cue_learn_helper.py'],
                'description': 'Configure sync/cue controls using Traktor Learn mode',
                'status': '✅ READY',
                'priority': 'HIGH'
            },
            'pitch': {
                'name': 'Pitch Learn Helper',
                'scripts': ['helpers/pitch_learn_helper.py'],
                'description': 'Configure pitch/tempo controls using Traktor Learn mode',
                'status': '✅ READY',
                'priority': 'HIGH'
            },
            'loop': {
                'name': 'Loop Learn Helper',
                'scripts': ['helpers/loop_learn_helper.py'],
                'description': 'Configure loop controls using Traktor Learn mode',
                'status': '✅ READY',
                'priority': 'MEDIUM'
            },
            'validation': {
                'name': 'FX Validation Tools',
                'scripts': [
                    'validation/fx_automated_validation.py',
                    'validation/test_fx_units_validation.py',
                    'validation/fx_command_tester.py'
                ],
                'description': 'Validate and test existing FX mappings',
                'status': '✅ AVAILABLE',
                'priority': 'LOW'
            }
        }

        # Quick access scripts
        self.quick_scripts = {
            'essential': [
                'helpers/sync_cue_learn_helper.py',
                'helpers/pitch_learn_helper.py'
            ],
            'complete': [
                'helpers/sync_cue_learn_helper.py',
                'helpers/pitch_learn_helper.py',
                'helpers/loop_learn_helper.py'
            ],
            'fx_complete': [
                'helpers/complete_fx_learn_helper.py'
            ],
            'validation': [
                'validation/fx_automated_validation.py'
            ]
        }

    def check_script_exists(self, script_name):
        """Check if a script exists in the directory"""
        script_path = self.base_dir / script_name
        return script_path.exists()

    def run_script(self, script_name):
        """Run a Python script"""
        script_path = self.base_dir / script_name

        if not script_path.exists():
            print(f"❌ Script not found: {script_name}")
            return False

        try:
            print(f"\n🚀 Launching: {script_name}")
            print("=" * 60)

            # Run the script
            result = subprocess.run([sys.executable, str(script_path)],
                                  cwd=str(self.base_dir))

            print("=" * 60)
            print(f"✅ Script completed: {script_name}")
            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error running {script_name}: {e}")
            return False

    def run_script_sequence(self, script_list, sequence_name):
        """Run a sequence of scripts"""
        print(f"\n🎯 RUNNING SEQUENCE: {sequence_name.upper()}")
        print("=" * 60)

        for i, script in enumerate(script_list, 1):
            print(f"\n📍 Step {i}/{len(script_list)}: {script}")

            if not self.check_script_exists(script):
                print(f"⚠️  Script not found: {script} - Skipping")
                continue

            user_input = input(f"🎯 Run {script}? (y/n/q=quit): ").lower().strip()

            if user_input == 'q':
                print("🛑 Sequence interrupted by user")
                break
            elif user_input == 'n':
                print(f"⏭️  Skipping {script}")
                continue

            success = self.run_script(script)

            if not success:
                retry = input(f"❌ {script} failed. Retry? (y/n): ").lower().strip()
                if retry == 'y':
                    self.run_script(script)

            if i < len(script_list):
                input(f"\n⏸️  Press ENTER to continue to next script...")

    def show_main_menu(self):
        """Display main menu"""
        print("\n🎛️ TRAKTOR MAPPING DISCOVERY LAUNCHER")
        print("=" * 60)
        print("🎯 OBJECTIVE: Complete Traktor Pro 3 MIDI mapping discovery")
        print("📊 STATUS: Centralized tool for all discovery scripts")
        print("=" * 60)

        print(f"\n📋 AVAILABLE DISCOVERY TOOLS:")
        for key, tool in self.tools.items():
            status_icon = "✅" if "COMPLETED" in tool['status'] else "🔍" if "READY" in tool['status'] else "⚠️"
            priority_color = "🔥" if tool['priority'] == 'HIGH' else "⚡" if tool['priority'] == 'MEDIUM' else "💡"

            print(f"   {status_icon} {tool['name']}: {tool['description']}")
            print(f"      Priority: {priority_color} {tool['priority']} | Status: {tool['status']}")

            # Show available scripts
            available_scripts = [s for s in tool['scripts'] if self.check_script_exists(s)]
            missing_scripts = [s for s in tool['scripts'] if not self.check_script_exists(s)]

            if available_scripts:
                print(f"      Available: {', '.join(available_scripts)}")
            if missing_scripts:
                print(f"      Missing: {', '.join(missing_scripts)}")

    def show_quick_menu(self):
        """Display quick access menu"""
        print(f"\n🚀 QUICK ACCESS MENU:")
        print("1. 🔥 Essential Learn Session (Sync/Cue + Pitch) - 30 min")
        print("2. ⚡ Complete Learn Session (Essential + Loops) - 60 min")
        print("3. ✅ FX Complete Setup (All FX Units) - 20 min")
        print("4. 🧪 Validation Suite (Test existing) - 15 min")
        print("")
        print("📋 INDIVIDUAL TOOLS:")

        tool_number = 5
        self.menu_map = {}

        for key, tool in self.tools.items():
            available_scripts = [s for s in tool['scripts'] if self.check_script_exists(s)]
            if available_scripts:
                print(f"{tool_number}. 🎛️ {tool['name']}")
                self.menu_map[str(tool_number)] = (key, tool)
                tool_number += 1

        print(f"{tool_number}. 📊 System Status & Analysis")
        print(f"{tool_number + 1}. ❓ Help & Documentation")
        print("q. Quit")

    def show_individual_tool_menu(self, tool_key, tool_info):
        """Show menu for individual tool"""
        print(f"\n🎛️ {tool_info['name'].upper()}")
        print("=" * 50)
        print(f"📝 Description: {tool_info['description']}")
        print(f"🎯 Priority: {tool_info['priority']}")
        print(f"📊 Status: {tool_info['status']}")

        available_scripts = [s for s in tool_info['scripts'] if self.check_script_exists(s)]

        if not available_scripts:
            print("❌ No available scripts for this tool")
            return

        print(f"\n📋 AVAILABLE SCRIPTS:")
        for i, script in enumerate(available_scripts, 1):
            print(f"{i}. {script}")

        print(f"{len(available_scripts) + 1}. Run all scripts in sequence")
        print("b. Back to main menu")

        choice = input(f"\n🎯 Choose script (1-{len(available_scripts) + 1}/b): ").strip()

        if choice == 'b':
            return
        elif choice == str(len(available_scripts) + 1):
            self.run_script_sequence(available_scripts, tool_info['name'])
        elif choice.isdigit() and 1 <= int(choice) <= len(available_scripts):
            script = available_scripts[int(choice) - 1]
            self.run_script(script)
        else:
            print("❌ Invalid choice")

    def show_system_status(self):
        """Show system status and analysis"""
        print(f"\n📊 SYSTEM STATUS & ANALYSIS")
        print("=" * 60)

        # Check script availability
        total_scripts = sum(len(tool['scripts']) for tool in self.tools.values())
        available_scripts = sum(len([s for s in tool['scripts'] if self.check_script_exists(s)])
                              for tool in self.tools.values())

        print(f"📋 SCRIPT AVAILABILITY:")
        print(f"   Total scripts: {total_scripts}")
        print(f"   Available: {available_scripts}")
        print(f"   Missing: {total_scripts - available_scripts}")
        print(f"   Completion: {available_scripts/total_scripts*100:.1f}%")

        # Check by priority
        print(f"\n🎯 PRIORITY ANALYSIS:")
        for priority in ['HIGH', 'MEDIUM', 'LOW', 'DONE']:
            priority_tools = [tool for tool in self.tools.values() if tool['priority'] == priority]
            priority_scripts = sum(len([s for s in tool['scripts'] if self.check_script_exists(s)])
                                 for tool in priority_tools)
            priority_total = sum(len(tool['scripts']) for tool in priority_tools)

            if priority_total > 0:
                emoji = "🔥" if priority == 'HIGH' else "⚡" if priority == 'MEDIUM' else "💡" if priority == 'LOW' else "✅"
                print(f"   {emoji} {priority}: {priority_scripts}/{priority_total} scripts available")

        # Check key files
        print(f"\n📁 KEY FILES STATUS:")
        key_files = [
            'traktor_control.py',
            'config.py',
            'fx_validation_report_20251004_092916.json'
        ]

        for file_name in key_files:
            file_path = self.base_dir / file_name
            status = "✅ EXISTS" if file_path.exists() else "❌ MISSING"
            print(f"   {status}: {file_name}")

    def show_help(self):
        """Show help and documentation"""
        print(f"\n❓ HELP & DOCUMENTATION")
        print("=" * 60)

        print(f"🎯 PURPOSE:")
        print("   This launcher centralizes all Traktor MIDI mapping discovery tools.")
        print("   Use it to systematically test existing mappings and discover new ones.")

        print(f"\n📋 WORKFLOW RECOMMENDATIONS:")
        print("   1. Start with 'Essential Learn Session' (Sync/Cue + Pitch)")
        print("   2. Continue with 'Complete Learn Session' to add Loop controls")
        print("   3. Use 'Validation Suite' to test completed mappings")
        print("   4. Update traktor_control.py with discovered mappings")

        print(f"\n🔧 SETUP REQUIREMENTS:")
        print("   ✅ Traktor Pro 3 running")
        print("   ✅ IAC Bus 1 configured and online")
        print("   ✅ Tracks loaded in all 4 decks")
        print("   ✅ MIDI mappings visible in Traktor interface")

        print(f"\n💡 TIPS:")
        print("   • Run scripts in a quiet environment to hear audio changes")
        print("   • Keep Traktor Controller Manager open during Learn sessions")
        print("   • Save TSI files after completing mappings")
        print("   • Test discovered mappings in real mixing scenarios")

        print(f"\n📚 DOCUMENTATION:")
        print("   • Each script generates JSON reports with results")
        print("   • Code snippets are provided for traktor_control.py updates")
        print("   • Failed mappings are logged for troubleshooting")

    def run(self):
        """Main application loop"""
        while True:
            self.show_main_menu()
            self.show_quick_menu()

            choice = input(f"\n🎯 Enter your choice: ").strip()

            if choice == 'q':
                print("👋 Goodbye! Happy DJing!")
                break
            elif choice == '1':
                # Essential Learn Session
                self.run_script_sequence(self.quick_scripts['essential'],
                                       "Essential Learn Session (Sync/Cue + Pitch)")
            elif choice == '2':
                # Complete Learn Session
                self.run_script_sequence(self.quick_scripts['complete'],
                                       "Complete Learn Session (Essential + Loops)")
            elif choice == '3':
                # FX Complete Setup
                self.run_script_sequence(self.quick_scripts['fx_complete'],
                                       "FX Complete Setup")
            elif choice == '4':
                # Validation Suite
                self.run_script_sequence(self.quick_scripts['validation'],
                                       "Validation Suite")
            elif choice in self.menu_map:
                # Individual tool
                tool_key, tool_info = self.menu_map[choice]
                self.show_individual_tool_menu(tool_key, tool_info)
            elif choice == str(len(self.menu_map) + 5):
                # System Status
                self.show_system_status()
                input("\n⏸️  Press ENTER to continue...")
            elif choice == str(len(self.menu_map) + 6):
                # Help
                self.show_help()
                input("\n⏸️  Press ENTER to continue...")
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Entry point"""
    print("🎛️ Traktor Mapping Discovery Launcher")
    print("Centralized access to all MIDI mapping discovery tools")
    print("=" * 60)

    launcher = MappingDiscoveryLauncher()
    launcher.run()

if __name__ == "__main__":
    main()