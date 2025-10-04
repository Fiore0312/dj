#!/usr/bin/env python3
"""
🎛️ Interactive FX Verifier - Real-time Human Verification
Companion to fx_command_tester.py for live verification during testing

This script allows real-time human verification of FX commands following
the traktor-command-tester agent's mandatory verification protocol.
"""

import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False

class InteractiveFXVerifier:
    """Interactive FX command verification with real-time human input"""

    def __init__(self):
        self.midi_out: Optional[rtmidi.MidiOut] = None
        self.connected = False
        self.verification_results = {}

        # Same mappings as fx_command_tester.py
        self.fx_mappings = {
            # FX UNIT 2 - CC 97-104
            'fx2_drywet': (1, 97, "Dry/Wet mix knob should move smoothly"),
            'fx2_knob1': (1, 98, "Parameter knob 1 should move"),
            'fx2_knob2': (1, 99, "Parameter knob 2 should move"),
            'fx2_knob3': (1, 100, "Parameter knob 3 should move"),
            'fx2_rst_button': (1, 101, "Reset button should trigger/flash"),
            'fx2_frz_button': (1, 102, "Freeze button should trigger/flash"),
            'fx2_spr_button': (1, 103, "Spread button should trigger/flash"),
            'fx2_onoff': (1, 104, "On/Off button should toggle state"),

            # FX UNIT 3 - CC 105-112
            'fx3_drywet': (1, 105, "Dry/Wet mix knob should move smoothly"),
            'fx3_knob1': (1, 106, "Parameter knob 1 should move"),
            'fx3_knob2': (1, 107, "Parameter knob 2 should move"),
            'fx3_knob3': (1, 108, "Parameter knob 3 should move"),
            'fx3_rst_button': (1, 109, "Reset button should trigger/flash"),
            'fx3_frz_button': (1, 110, "Freeze button should trigger/flash"),
            'fx3_spr_button': (1, 111, "Spread button should trigger/flash"),
            'fx3_onoff': (1, 112, "On/Off button should toggle state"),

            # FX UNIT 4 - CC 113-120
            'fx4_drywet': (1, 113, "Dry/Wet mix knob should move smoothly"),
            'fx4_knob1': (1, 114, "Parameter knob 1 should move"),
            'fx4_knob2': (1, 115, "Parameter knob 2 should move"),
            'fx4_knob3': (1, 116, "Parameter knob 3 should move"),
            'fx4_rst_button': (1, 117, "Reset button should trigger/flash"),
            'fx4_frz_button': (1, 118, "Freeze button should trigger/flash"),
            'fx4_spr_button': (1, 119, "Spread button should trigger/flash"),
            'fx4_onoff': (1, 120, "On/Off button should toggle state"),
        }

    def connect_midi(self) -> bool:
        """Connect to IAC Driver"""
        if not RTMIDI_AVAILABLE:
            print("ℹ️  rtmidi not available - simulation mode")
            return True

        try:
            self.midi_out = rtmidi.MidiOut()
            ports = self.midi_out.get_ports()

            # Find IAC Bus 1
            iac_port_idx = None
            for i, port in enumerate(ports):
                if "bus 1" in port.lower() or "iac" in port.lower():
                    iac_port_idx = i
                    break

            if iac_port_idx is not None:
                self.midi_out.open_port(iac_port_idx)
                self.connected = True
                print(f"✅ Connected to: {ports[iac_port_idx]}")
                return True
            else:
                print("⚠️  IAC Driver not found - simulation mode")
                return True

        except Exception as e:
            print(f"⚠️  MIDI error: {e} - simulation mode")
            return True

    def send_midi_command(self, channel: int, cc: int, value: int) -> bool:
        """Send MIDI command"""
        if self.connected and self.midi_out:
            try:
                message = [0xB0 + (channel - 1), cc, value]
                self.midi_out.send_message(message)
                return True
            except:
                return False
        return True  # Simulation mode

    def get_user_verification(self, command_name: str, expected_behavior: str) -> Tuple[bool, str]:
        """Get user verification with clear options"""
        print(f"\n❓ VERIFICATION for {command_name}:")
        print(f"   Expected: {expected_behavior}")
        print("   Did this work as expected?")
        print("   Options:")
        print("     (y) Yes - worked perfectly")
        print("     (n) No - did not work")
        print("     (p) Partial - worked but with issues")
        print("     (s) Skip this test")
        print("     (r) Repeat the test")
        print("     (q) Quit verification session")

        while True:
            try:
                response = input("   Your response: ").lower().strip()

                if response == 'y':
                    return True, "VERIFIED_WORKING"
                elif response == 'n':
                    feedback = input("   Describe what happened (or press Enter): ").strip()
                    return False, f"VERIFIED_NOT_WORKING: {feedback}" if feedback else "VERIFIED_NOT_WORKING"
                elif response == 'p':
                    feedback = input("   Describe the issue: ").strip()
                    return True, f"PARTIAL_WORKING: {feedback}"
                elif response == 's':
                    return None, "SKIPPED_BY_USER"
                elif response == 'r':
                    return "repeat", "REPEAT_REQUESTED"
                elif response == 'q':
                    print("🛑 Verification session terminated by user")
                    return "quit", "SESSION_TERMINATED"
                else:
                    print("   Invalid response. Please use y/n/p/s/r/q")

            except KeyboardInterrupt:
                print("\n🛑 Verification interrupted by user")
                return "quit", "SESSION_INTERRUPTED"

    def test_and_verify_command(self, command_name: str) -> Dict[str, any]:
        """Test command with real-time human verification"""
        if command_name not in self.fx_mappings:
            return {"error": f"Command {command_name} not found"}

        channel, cc, expected_behavior = self.fx_mappings[command_name]

        print(f"\n🧪 TESTING: {command_name}")
        print("="*50)
        print(f"📡 MIDI: Channel {channel}, CC {cc}")
        print(f"🎯 Expected: {expected_behavior}")

        # Determine test pattern based on control type
        if 'button' in command_name or 'onoff' in command_name:
            test_values = [127]  # Button press
            pattern_desc = "button trigger"
        elif 'drywet' in command_name:
            test_values = [0, 64, 127]  # Dry/wet sweep
            pattern_desc = "dry/wet sweep (0→50%→100%)"
        else:  # knob controls
            test_values = [0, 32, 64, 96, 127]  # Full sweep
            pattern_desc = "knob sweep (0→25%→50%→75%→100%)"

        print(f"🔢 Test pattern: {pattern_desc}")
        print("⏰ Sending commands in 2 seconds... Watch Traktor!")
        time.sleep(2)

        # Send test pattern
        for i, value in enumerate(test_values):
            print(f"📤 Sending: CC{cc} = {value}")
            self.send_midi_command(channel, cc, value)
            time.sleep(0.8)

        # Reset to neutral position for knobs
        if 'button' not in command_name and 'onoff' not in command_name:
            print("🔄 Resetting to neutral (64)")
            self.send_midi_command(channel, cc, 64)
            time.sleep(0.5)

        # Get human verification
        while True:
            verified, feedback = self.get_user_verification(command_name, expected_behavior)

            if verified == "repeat":
                print("🔄 Repeating test...")
                time.sleep(1)
                # Repeat the test pattern
                for value in test_values:
                    self.send_midi_command(channel, cc, value)
                    time.sleep(0.8)
                if 'button' not in command_name and 'onoff' not in command_name:
                    self.send_midi_command(channel, cc, 64)
                continue
            elif verified == "quit":
                return {"quit": True, "feedback": feedback}
            else:
                break

        result = {
            "command": command_name,
            "channel": channel,
            "cc": cc,
            "expected_behavior": expected_behavior,
            "test_pattern": test_values,
            "verified": verified,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }

        return result

    def run_interactive_verification(self, fx_units: List[int] = [2, 3, 4]) -> Dict[str, any]:
        """Run interactive verification session"""
        print("\n🎛️ INTERACTIVE FX VERIFICATION SESSION")
        print("="*60)
        print("🤖 Traktor-Command-Tester Agent - Interactive Mode")
        print("⚠️  Human verification required for each command")
        print("="*60)

        # Connect MIDI
        if not self.connect_midi():
            print("❌ Could not establish MIDI connection")
            return {"error": "MIDI connection failed"}

        # Pre-test setup
        print(f"\n📋 VERIFICATION SETUP:")
        print("   ✅ Ensure Traktor Pro is running")
        print("   ✅ Load at least one effect in each FX unit")
        print("   ✅ Make FX units visible on screen")
        print("   ✅ Set volume to comfortable level")

        input("\n📍 Press Enter when ready to start verification...")

        session_results = {
            "session_info": {
                "timestamp": datetime.now().isoformat(),
                "fx_units_tested": fx_units,
                "methodology": "traktor-command-tester-interactive"
            },
            "results": {},
            "summary": {}
        }

        total_tests = 0
        verified_working = 0
        verified_not_working = 0
        skipped = 0

        # Test each FX unit
        for fx_unit in fx_units:
            print(f"\n{'='*20} FX UNIT {fx_unit} {'='*20}")

            fx_controls = ['drywet', 'knob1', 'knob2', 'knob3', 'rst_button', 'frz_button', 'spr_button', 'onoff']
            unit_results = {}

            for control in fx_controls:
                command_name = f'fx{fx_unit}_{control}'
                total_tests += 1

                result = self.test_and_verify_command(command_name)

                if "quit" in result:
                    print(f"\n🛑 Session terminated during {command_name}")
                    break

                unit_results[command_name] = result

                # Update counters
                if result.get("verified") is True:
                    verified_working += 1
                elif result.get("verified") is False:
                    verified_not_working += 1
                elif result.get("verified") is None:
                    skipped += 1

                # Brief pause between tests
                if control != fx_controls[-1]:  # Not the last control
                    print("⏸️  Brief pause before next test...")
                    time.sleep(1.5)

            session_results["results"][f"fx_unit_{fx_unit}"] = unit_results

            # Check if session was terminated
            if any("quit" in r for r in unit_results.values() if isinstance(r, dict)):
                break

            # Pause between FX units
            if fx_unit != fx_units[-1]:
                input(f"\n✅ FX Unit {fx_unit} complete. Press Enter for next unit...")

        # Generate summary
        session_results["summary"] = {
            "total_commands_tested": total_tests,
            "verified_working": verified_working,
            "verified_not_working": verified_not_working,
            "skipped": skipped,
            "success_rate": f"{(verified_working/total_tests)*100:.1f}%" if total_tests > 0 else "0%"
        }

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/Users/Fiore/dj/fx_interactive_verification_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(session_results, f, indent=2)

        print(f"\n📁 Results saved: {filename}")
        return session_results

    def print_session_summary(self, results: Dict[str, any]):
        """Print comprehensive session summary"""
        if "summary" not in results:
            return

        summary = results["summary"]
        print(f"\n📊 VERIFICATION SESSION SUMMARY")
        print("="*40)
        print(f"Total commands tested: {summary['total_commands_tested']}")
        print(f"✅ Verified working: {summary['verified_working']}")
        print(f"❌ Verified not working: {summary['verified_not_working']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        print(f"📈 Success rate: {summary['success_rate']}")

        # Show detailed results by FX unit
        for fx_unit in [2, 3, 4]:
            unit_key = f"fx_unit_{fx_unit}"
            if unit_key in results["results"]:
                unit_results = results["results"][unit_key]
                working = sum(1 for r in unit_results.values() if isinstance(r, dict) and r.get("verified") is True)
                total = len([r for r in unit_results.values() if isinstance(r, dict)])
                print(f"   FX Unit {fx_unit}: {working}/{total} working")

def main():
    """Main interactive verification"""
    verifier = InteractiveFXVerifier()

    print("🚀 Starting Interactive FX Verification")
    print("🤖 Real-time human verification protocol")

    # Run verification
    results = verifier.run_interactive_verification()

    if "error" not in results:
        verifier.print_session_summary(results)

        print(f"\n🎯 VERIFICATION COMPLETE")
        print("   Use these results to update traktor_control.py")
        print("   Report any issues for further investigation")

if __name__ == "__main__":
    main()