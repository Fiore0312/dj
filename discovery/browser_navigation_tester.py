#!/usr/bin/env python3
"""
BROWSER NAVIGATION VALIDATION TOOL
=====================================

Test e validazione sistematica dei controlli di navigazione browser Traktor Pro 3.
Basato sul metodo di successo utilizzato per FX Units 1-4.

Sezioni da testare:
- Browser Tree Navigation (up/down, enter/exit, expand/collapse)
- Browser Page Controls (page up/down, top/bottom)

Author: DJ AI System
Date: 2025-10-04
"""

import time
import json
import rtmidi
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class BrowserTestResult:
    """Risultato di un test browser."""
    command: str
    midi_details: Dict
    expected_behavior: str
    midi_sent_successfully: bool
    human_verified: Optional[bool] = None
    user_feedback: str = "PENDING - Awaiting human verification"
    timestamp: float = 0.0
    verification_status: str = "PENDING_USER_CONFIRMATION"

class BrowserNavigationTester:
    """Tester per controlli di navigazione browser Traktor."""

    def __init__(self):
        self.midi_out: Optional[rtmidi.MidiOut] = None
        self.results: List[BrowserTestResult] = []

        # Browser controls da testare
        self.browser_controls = {
            # TREE NAVIGATION CONTROLS (già alcuni testati)
            'browser_tree_up': {
                'cc': 55,
                'test_value': 127,
                'description': 'Tree navigation up - should move up in browser tree (Explorer/Music Folders)'
            },
            'browser_tree_down': {
                'cc': 56,
                'test_value': 127,
                'description': 'Tree navigation down - should move down in browser tree'
            },
            'browser_tree_enter': {
                'cc': 66,
                'test_value': 127,
                'description': 'Tree enter - should enter/expand selected folder'
            },
            'browser_tree_exit': {
                'cc': 67,
                'test_value': 127,
                'description': 'Tree exit - should exit/go back to parent folder'
            },
            'browser_tree_expand': {
                'cc': 59,
                'test_value': 127,
                'description': 'Tree expand - should expand selected tree node (Artists/Songs)'
            },
            'browser_tree_collapse': {
                'cc': 68,
                'test_value': 127,
                'description': 'Tree collapse - should collapse selected tree node'
            },

            # PAGE NAVIGATION CONTROLS (teorici)
            'browser_page_up': {
                'cc': 69,
                'test_value': 127,
                'description': 'Page up - should scroll up one page in browser list'
            },
            'browser_page_down': {
                'cc': 70,
                'test_value': 127,
                'description': 'Page down - should scroll down one page in browser list'
            },
            'browser_top': {
                'cc': 71,
                'test_value': 127,
                'description': 'Go to top - should jump to top of browser list'
            },
            'browser_bottom': {
                'cc': 72,
                'test_value': 127,
                'description': 'Go to bottom - should jump to bottom of browser list'
            }
        }

    def connect_midi(self) -> bool:
        """Connetti MIDI output."""
        try:
            self.midi_out = rtmidi.MidiOut()

            # Trova porta AI DJ Virtual Controller
            ports = self.midi_out.get_ports()
            target_port = None

            for i, port in enumerate(ports):
                if "AI DJ Virtual Controller" in port:
                    target_port = i
                    break

            if target_port is None:
                print("❌ AI DJ Virtual Controller non trovato!")
                print("🔍 Porte disponibili:")
                for i, port in enumerate(ports):
                    print(f"  {i}: {port}")
                return False

            self.midi_out.open_port(target_port)
            print(f"✅ Connesso a: {ports[target_port]}")
            return True

        except Exception as e:
            print(f"❌ Errore connessione MIDI: {e}")
            return False

    def send_midi_cc(self, channel: int, cc: int, value: int) -> bool:
        """Invia comando MIDI CC."""
        if not self.midi_out:
            return False

        try:
            # Status byte: 176 + channel (176 = Control Change per channel 1)
            status = 176 + (channel - 1)
            message = [status, cc, value]
            self.midi_out.send_message(message)
            return True
        except Exception as e:
            print(f"❌ Errore invio MIDI: {e}")
            return False

    def test_browser_command(self, command_name: str, command_info: Dict) -> BrowserTestResult:
        """Testa un singolo comando browser."""
        print(f"\n🧪 Testing: {command_name}")
        print(f"📝 Expected: {command_info['description']}")
        print(f"🎛️ MIDI: Channel 1, CC {command_info['cc']}, Value {command_info['test_value']}")

        # Invia comando MIDI
        midi_sent = self.send_midi_cc(1, command_info['cc'], command_info['test_value'])

        result = BrowserTestResult(
            command=command_name,
            midi_details={
                'channel': 1,
                'cc': command_info['cc'],
                'test_value': command_info['test_value']
            },
            expected_behavior=command_info['description'],
            midi_sent_successfully=midi_sent,
            timestamp=time.time()
        )

        if midi_sent:
            print("✅ MIDI command sent successfully")
            print("👀 Watch Traktor browser - did the expected action occur?")
        else:
            print("❌ Failed to send MIDI command")
            result.verification_status = "MIDI_SEND_FAILED"

        return result

    def run_automated_test(self) -> None:
        """Esegui test automatico per identificare controlli funzionanti."""
        print("🎛️ BROWSER NAVIGATION AUTOMATED VALIDATION")
        print("=" * 50)
        print("📍 AUTO-TEST MODE:")
        print("1. Connecting to MIDI...")
        print("2. Sending all browser commands...")
        print("3. Generating report for manual verification...")
        print("=" * 50)

        if not self.connect_midi():
            return

        try:
            # Test ogni comando browser automaticamente
            print(f"\n🧪 Testing {len(self.browser_controls)} browser commands...")

            for i, (command_name, command_info) in enumerate(self.browser_controls.items(), 1):
                print(f"\n[{i}/{len(self.browser_controls)}] Testing: {command_name}")
                result = self.test_browser_command(command_name, command_info)

                if result.midi_sent_successfully:
                    result.user_feedback = "📤 MIDI SENT - Awaiting manual verification in Traktor"
                    result.verification_status = "MIDI_SENT_SUCCESS"
                    print("✅ MIDI command sent - Check Traktor for response")
                else:
                    result.user_feedback = "❌ MIDI SEND FAILED"
                    result.verification_status = "MIDI_SEND_FAILED"
                    print("❌ Failed to send MIDI")

                self.results.append(result)

                # Breve pausa tra i comandi
                if i < len(self.browser_controls):
                    time.sleep(1)

            # Genera report finale
            self.generate_report()

        finally:
            if self.midi_out:
                self.midi_out.close_port()
                print("\n🔌 MIDI connection closed")

    def generate_report(self) -> None:
        """Genera report di validazione."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Statistiche
        total_tests = len(self.results)
        working_tests = len([r for r in self.results if r.human_verified is True])
        failed_tests = len([r for r in self.results if r.human_verified is False])
        skipped_tests = len([r for r in self.results if r.verification_status == "SKIPPED"])

        # Report JSON
        report_data = {
            "metadata": {
                "test_type": "BROWSER_NAVIGATION_VALIDATION",
                "agent": "browser-navigation-tester",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": time.time() - (self.results[0].timestamp if self.results else time.time()),
                "midi_available": True,
                "midi_connected": True
            },
            "test_configuration": {
                "controls_tested": list(self.browser_controls.keys()),
                "cc_range": "55-72",
                "total_commands": total_tests
            },
            "statistics": {
                "total_tests": total_tests,
                "working_commands": working_tests,
                "failed_commands": failed_tests,
                "skipped_commands": skipped_tests,
                "success_rate": f"{(working_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            "results": [
                {
                    "command": r.command,
                    "midi_details": r.midi_details,
                    "expected_behavior": r.expected_behavior,
                    "midi_sent_successfully": r.midi_sent_successfully,
                    "human_verified": r.human_verified,
                    "user_feedback": r.user_feedback,
                    "timestamp": r.timestamp,
                    "verification_status": r.verification_status
                }
                for r in self.results
            ]
        }

        # Salva report JSON
        json_filename = f"browser_validation_report_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(report_data, f, indent=2)

        # Report console
        print("\n" + "=" * 60)
        print("📊 BROWSER NAVIGATION VALIDATION REPORT")
        print("=" * 60)
        print(f"📈 Statistics:")
        print(f"   Total Commands Tested: {total_tests}")
        print(f"   ✅ Working Commands: {working_tests}")
        print(f"   ❌ Failed Commands: {failed_tests}")
        print(f"   ⏭️ Skipped Commands: {skipped_tests}")
        print(f"   📊 Success Rate: {(working_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")

        print(f"\n🎯 DETAILED RESULTS:")
        for result in self.results:
            status_icon = {
                "CONFIRMED_WORKING": "✅",
                "CONFIRMED_NOT_WORKING": "❌",
                "SKIPPED": "⏭️",
                "PENDING_USER_CONFIRMATION": "⏸️",
                "MIDI_SEND_FAILED": "🚫"
            }.get(result.verification_status, "❓")

            print(f"   {status_icon} {result.command} (CC {result.midi_details['cc']}): {result.user_feedback}")

        print(f"\n💾 Report saved: {json_filename}")
        print("=" * 60)

def main():
    """Funzione principale."""
    print("🎛️ BROWSER NAVIGATION TESTER - Traktor Pro 3")
    print("Based on successful FX validation methodology")
    print("\nThis tool will test browser navigation controls:")
    print("- Tree navigation (up/down, enter/exit, expand/collapse)")
    print("- Page controls (page up/down, top/bottom)")

    tester = BrowserNavigationTester()
    tester.run_automated_test()

if __name__ == "__main__":
    main()