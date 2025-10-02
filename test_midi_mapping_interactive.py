#!/usr/bin/env python3
"""
🧪 Interactive MIDI Mapping Tester for Traktor Pro 3
Tests all MIDI commands defined in traktor_control.py with user confirmation
"""

import time
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False
    print("⚠️ python-rtmidi not available. Install with: pip install python-rtmidi")
    sys.exit(1)

# Import from traktor_control and config
from traktor_control import TraktorController, MIDIChannel
from config import DJConfig


class InteractiveMIDITester:
    """Interactive tester for all MIDI commands"""

    def __init__(self):
        # Initialize config
        self.config = DJConfig()
        self.traktor = TraktorController(self.config)
        self.results = {
            "test_date": datetime.now().isoformat(),
            "total_commands": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "failed_commands": [],
            "passed_commands": [],
            "notes": []
        }

        # Organize commands by category
        self.command_categories = self._organize_commands()

    def _organize_commands(self) -> Dict[str, List[Tuple[str, Tuple[int, int]]]]:
        """Organize commands from MIDI_MAP into categories"""
        categories = {
            "Transport": [],
            "Volume & Mixer": [],
            "EQ Controls": [],
            "Browser Basic": [],
            "Sync": [],
            "Pitch": [],
            "Browser Tree (NEW)": [],
            "Loops (NEW)": [],
            "Hotcues (NEW)": [],
            "Beatjump (NEW)": [],
            "Advanced (NEW)": [],
            "Effects": [],
            "Emergency": []
        }

        # Map each command to its category
        for cmd_name, (channel, cc) in self.traktor.MIDI_MAP.items():
            # Skip aliases
            if any(alias in cmd_name for alias in ['_load_selected', '_scroll_']):
                continue

            # Categorize
            if 'play' in cmd_name or 'cue' in cmd_name:
                categories["Transport"].append((cmd_name, (channel, cc)))
            elif 'volume' in cmd_name or 'crossfader' in cmd_name or 'master' in cmd_name:
                categories["Volume & Mixer"].append((cmd_name, (channel, cc)))
            elif 'eq' in cmd_name:
                categories["EQ Controls"].append((cmd_name, (channel, cc)))
            elif 'browser' in cmd_name and 'tree' not in cmd_name and cc < 50:
                categories["Browser Basic"].append((cmd_name, (channel, cc)))
            elif 'sync' in cmd_name:
                categories["Sync"].append((cmd_name, (channel, cc)))
            elif 'pitch' in cmd_name:
                categories["Pitch"].append((cmd_name, (channel, cc)))
            elif 'browser_tree' in cmd_name or 'browser_page' in cmd_name or 'browser_top' in cmd_name or 'browser_bottom' in cmd_name:
                categories["Browser Tree (NEW)"].append((cmd_name, (channel, cc)))
            elif 'loop' in cmd_name:
                categories["Loops (NEW)"].append((cmd_name, (channel, cc)))
            elif 'hotcue' in cmd_name:
                categories["Hotcues (NEW)"].append((cmd_name, (channel, cc)))
            elif 'beatjump' in cmd_name:
                categories["Beatjump (NEW)"].append((cmd_name, (channel, cc)))
            elif 'keylock' in cmd_name or 'quantize' in cmd_name or 'flux' in cmd_name:
                categories["Advanced (NEW)"].append((cmd_name, (channel, cc)))
            elif 'fx' in cmd_name:
                categories["Effects"].append((cmd_name, (channel, cc)))
            elif 'emergency' in cmd_name or 'ai_enable' in cmd_name:
                categories["Emergency"].append((cmd_name, (channel, cc)))

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def _format_command_name(self, cmd_name: str) -> str:
        """Format command name for display"""
        # Remove underscores, capitalize
        return cmd_name.replace('_', ' ').title()

    def _get_command_description(self, cmd_name: str, channel: int, cc: int) -> str:
        """Get human-readable description of command"""
        descriptions = {
            # Transport
            'deck_a_play': 'Play/Pause Deck A',
            'deck_b_play': 'Play/Pause Deck B',
            'deck_a_cue': 'Cue Point Deck A',
            'deck_b_cue': 'Cue Point Deck B',

            # Volume
            'deck_a_volume': 'Deck A Volume Fader',
            'deck_b_volume': 'Deck B Volume Fader',
            'crossfader': 'Crossfader Position',
            'master_volume': 'Master Output Volume',

            # EQ
            'deck_a_eq_high': 'Deck A High EQ',
            'deck_a_eq_mid': 'Deck A Mid EQ',
            'deck_a_eq_low': 'Deck A Low EQ',
            'deck_b_eq_high': 'Deck B High EQ',
            'deck_b_eq_mid': 'Deck B Mid EQ',
            'deck_b_eq_low': 'Deck B Low EQ',

            # Browser
            'browser_up': 'Scroll Browser Up',
            'browser_down': 'Scroll Browser Down',
            'browser_load_deck_a': 'Load Track to Deck A',
            'browser_load_deck_b': 'Load Track to Deck B',
            'browser_select_item': 'Select/Enter Item',

            # Sync
            'deck_a_sync': 'Sync Deck A to Master',
            'deck_b_sync': 'Sync Deck B to Master',

            # Pitch
            'deck_a_pitch': 'Deck A Pitch Adjust',
            'deck_b_pitch': 'Deck B Pitch Adjust',

            # Tree Navigation
            'browser_tree_up': 'Navigate Tree Up',
            'browser_tree_down': 'Navigate Tree Down',
            'browser_tree_enter': 'Enter Folder/Playlist',
            'browser_tree_exit': 'Exit to Parent Folder',
            'browser_tree_expand': 'Expand Folder',
            'browser_tree_collapse': 'Collapse Folder',
            'browser_page_up': 'Page Up in List',
            'browser_page_down': 'Page Down in List',

            # Loops
            'deck_a_loop_in': 'Set Loop In Point (Deck A)',
            'deck_a_loop_out': 'Set Loop Out Point (Deck A)',
            'deck_a_loop_active': 'Activate Loop (Deck A)',
            'deck_a_loop_size': 'Set Loop Size (Deck A)',
            'deck_b_loop_in': 'Set Loop In Point (Deck B)',
            'deck_b_loop_out': 'Set Loop Out Point (Deck B)',
            'deck_b_loop_active': 'Activate Loop (Deck B)',
            'deck_b_loop_size': 'Set Loop Size (Deck B)',
        }

        # Hotcues
        for deck in ['a', 'b']:
            for i in range(1, 9):
                descriptions[f'deck_{deck}_hotcue_{i}'] = f'Hotcue {i} (Deck {deck.upper()})'

        # Beatjump
        for deck in ['a', 'b']:
            for direction in ['fwd', 'back']:
                for beats in [1, 4]:
                    key = f'deck_{deck}_beatjump_{direction}_{beats}'
                    dir_name = "Forward" if direction == "fwd" else "Backward"
                    descriptions[key] = f'Beatjump {dir_name} {beats} beat(s) (Deck {deck.upper()})'

        # Advanced
        for deck in ['a', 'b']:
            descriptions[f'deck_{deck}_keylock'] = f'Keylock Toggle (Deck {deck.upper()})'
            descriptions[f'deck_{deck}_quantize'] = f'Quantize Toggle (Deck {deck.upper()})'
            descriptions[f'deck_{deck}_flux'] = f'Flux Mode Toggle (Deck {deck.upper()})'

        return descriptions.get(cmd_name, self._format_command_name(cmd_name))

    def _send_test_command(self, channel: int, cc: int, value: int = 127) -> bool:
        """Send a test MIDI command"""
        try:
            return self.traktor._send_midi_command(channel, cc, value, "Test")
        except Exception as e:
            print(f"❌ Error sending MIDI: {e}")
            return False

    def _show_debug_info(self, cmd_name: str, channel: int, cc: int):
        """Show debugging information for failed command"""
        print("\n" + "="*60)
        print("🔍 DEBUG INFORMATION")
        print("="*60)
        print(f"Command Name: {cmd_name}")
        print(f"MIDI Channel: {channel}")
        print(f"CC Number: {cc}")
        print(f"\n📋 Checklist:")
        print("  1. ☑️ Traktor Pro 3 is running?")
        print("  2. ☑️ IAC Driver Bus 1 is enabled in Audio MIDI Setup?")
        print("  3. ☑️ TSI file (AI_DJ_Perfect_Mapping.tsi) imported?")
        print("  4. ☑️ Correct view active in Traktor?")

        # Category-specific hints
        if 'tree' in cmd_name or 'browser' in cmd_name:
            print("\n💡 Browser commands require:")
            print("   - Press F3 to open Browser view")
            print("   - Tree panel must be visible")
        elif 'loop' in cmd_name:
            print("\n💡 Loop commands require:")
            print("   - Track must be loaded and playing")
            print("   - Deck must be in focus")
        elif 'hotcue' in cmd_name:
            print("\n💡 Hotcue commands:")
            print("   - First trigger stores the hotcue")
            print("   - Second trigger jumps to position")

        print("\n🛠️ Troubleshooting:")
        print(f"   - Try manually in Traktor MIDI learn mode")
        print(f"   - Check Controller Manager → Generic MIDI")
        print(f"   - Verify CC {cc} is mapped correctly")
        print("="*60 + "\n")

    def test_command(self, cmd_name: str, channel: int, cc: int) -> Dict:
        """Test a single command with user confirmation"""
        description = self._get_command_description(cmd_name, channel, cc)

        print(f"\n🧪 Testing: CC {cc} - {description}")
        print(f"📝 Command: {cmd_name}")
        print(f"📡 Sending MIDI: Channel {channel}, CC {cc}, Value 127")

        # Send command
        sent = self._send_test_command(channel, cc, 127)
        if not sent:
            print("❌ Failed to send MIDI command")
            return {"status": "error", "cc": cc, "name": cmd_name, "description": description}

        time.sleep(1.5)  # Give time to see the effect

        # Ask for confirmation
        while True:
            print("\n" + "-"*60)
            response = input("✅ Hai visto funzionare il comando? (s/n/q/skip): ").lower().strip()

            if response == 's':
                print("✅ PASSED")
                return {
                    "status": "passed",
                    "cc": cc,
                    "name": cmd_name,
                    "description": description
                }

            elif response == 'n':
                analyze = input("🔍 Vuoi analizzare l'errore ora? (s/n): ").lower().strip()
                if analyze == 's':
                    self._show_debug_info(cmd_name, channel, cc)
                    input("\nPremi INVIO per continuare...")

                print("❌ FAILED")
                return {
                    "status": "failed",
                    "cc": cc,
                    "name": cmd_name,
                    "description": description
                }

            elif response == 'skip':
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
                print("❌ Risposta non valida. Usa: s (sì), n (no), skip (salta), q (termina)")

    def test_category(self, category_name: str, commands: List[Tuple[str, Tuple[int, int]]]):
        """Test all commands in a category"""
        print("\n" + "="*70)
        print(f"📁 Categoria: {category_name}")
        print(f"   {len(commands)} comandi da testare")
        print("="*70)

        for cmd_name, (channel, cc) in commands:
            result = self.test_command(cmd_name, channel, cc)

            if result["status"] == "quit":
                return "quit"
            elif result["status"] == "passed":
                self.results["passed"] += 1
                self.results["passed_commands"].append(result)
            elif result["status"] == "failed":
                self.results["failed"] += 1
                self.results["failed_commands"].append(result)
            elif result["status"] == "skipped":
                self.results["skipped"] += 1

            self.results["total_commands"] += 1

        # Category summary
        print("\n" + "-"*70)
        print(f"✅ Categoria '{category_name}' completata!")
        print(f"   Testati: {len(commands)}")
        print("-"*70)

        return "continue"

    def run(self):
        """Run interactive test on all commands"""
        print("\n" + "="*70)
        print("🎛️  MIDI MAPPING INTERACTIVE TESTER")
        print("="*70)
        print(f"\nTrovati {sum(len(cmds) for cmds in self.command_categories.values())} comandi in {len(self.command_categories)} categorie\n")

        print("📋 Istruzioni:")
        print("   - Assicurati che Traktor Pro 3 sia aperto")
        print("   - Importa AI_DJ_Perfect_Mapping.tsi se non l'hai già fatto")
        print("   - Verifica che IAC Driver Bus 1 sia attivo")
        print("   - Per ogni comando:")
        print("     • 's' = funziona correttamente ✅")
        print("     • 'n' = non funziona ❌")
        print("     • 'skip' = salta questo comando ⏭️")
        print("     • 'q' = termina test e salva risultati")
        print("\n" + "="*70)

        input("\nPremi INVIO per iniziare...")

        # Test each category
        for idx, (category_name, commands) in enumerate(self.command_categories.items(), 1):
            print(f"\n\n📊 Progresso: Categoria {idx}/{len(self.command_categories)}")

            result = self.test_category(category_name, commands)

            if result == "quit":
                print("\n⚠️ Test interrotto dall'utente")
                break

            # Short pause between categories
            if idx < len(self.command_categories):
                cont = input("\n➡️ Continua con la prossima categoria? (INVIO=sì, q=termina): ").lower()
                if cont == 'q':
                    break

        # Save results
        self._save_results()
        self._print_summary()

    def _save_results(self):
        """Save test results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON report
        json_file = Path(f"test_results_{timestamp}.json")
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Report JSON salvato: {json_file}")

        # Human-readable TXT report
        txt_file = Path(f"test_results_{timestamp}.txt")
        with open(txt_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("MIDI MAPPING TEST RESULTS\n")
            f.write("="*70 + "\n\n")
            f.write(f"Test Date: {self.results['test_date']}\n")
            f.write(f"Total Commands: {self.results['total_commands']}\n")
            f.write(f"✅ Passed: {self.results['passed']}\n")
            f.write(f"❌ Failed: {self.results['failed']}\n")
            f.write(f"⏭️ Skipped: {self.results['skipped']}\n\n")

            if self.results['failed_commands']:
                f.write("="*70 + "\n")
                f.write("FAILED COMMANDS\n")
                f.write("="*70 + "\n\n")
                for cmd in self.results['failed_commands']:
                    f.write(f"❌ CC {cmd['cc']} - {cmd['description']}\n")
                    f.write(f"   Command: {cmd['name']}\n\n")

            if self.results['passed_commands']:
                f.write("="*70 + "\n")
                f.write("PASSED COMMANDS\n")
                f.write("="*70 + "\n\n")
                for cmd in self.results['passed_commands']:
                    f.write(f"✅ CC {cmd['cc']} - {cmd['description']}\n")

        print(f"📄 Report TXT salvato: {txt_file}")

    def _print_summary(self):
        """Print final summary"""
        print("\n\n" + "="*70)
        print("📊 RIEPILOGO FINALE")
        print("="*70)
        print(f"\nComandi totali testati: {self.results['total_commands']}")
        print(f"✅ Passati: {self.results['passed']} ({self.results['passed']/max(self.results['total_commands'],1)*100:.1f}%)")
        print(f"❌ Falliti: {self.results['failed']} ({self.results['failed']/max(self.results['total_commands'],1)*100:.1f}%)")
        print(f"⏭️ Saltati: {self.results['skipped']}")

        if self.results['failed_commands']:
            print(f"\n⚠️ Comandi falliti ({len(self.results['failed_commands'])}):")
            for cmd in self.results['failed_commands'][:10]:  # Show first 10
                print(f"   • CC {cmd['cc']}: {cmd['description']}")
            if len(self.results['failed_commands']) > 10:
                print(f"   ... e altri {len(self.results['failed_commands'])-10}")

        print("\n" + "="*70)
        print("✅ Test completato!")
        print("="*70 + "\n")


def main():
    """Main entry point"""
    try:
        tester = InteractiveMIDITester()
        tester.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrotto da tastiera (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore inaspettato: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
