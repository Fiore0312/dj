#!/usr/bin/env python3
"""
🔍 Traktor MIDI Communication Diagnostic Tool
Comprehensive testing for Traktor Pro MIDI connectivity
Based on user's working 3-second ping script pattern
"""

import asyncio
import sys
import time
import signal
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from midi.traktor_specific_driver import get_traktor_driver, TraktorMIDIDriver

class TraktorDiagnostic:
    """Comprehensive Traktor MIDI diagnostic system"""

    def __init__(self):
        self.driver = get_traktor_driver()
        self.running = False
        self.test_results = {}

    async def run_full_diagnostic(self):
        """Run complete Traktor communication diagnostic"""
        print("🔍 TRAKTOR MIDI COMMUNICATION DIAGNOSTIC")
        print("=" * 60)
        print("Based on user's working 3-second ping pattern")
        print("=" * 60)

        # Test 1: System MIDI Detection
        await self.test_system_midi_detection()

        # Test 2: Traktor Device Scanning
        await self.test_traktor_device_scanning()

        # Test 3: Connection Methods
        await self.test_connection_methods()

        # Test 4: Communication Test (3-second ping pattern)
        await self.test_communication_pattern()

        # Test 5: Real-time Control
        await self.test_real_time_control()

        # Display results
        self.display_diagnostic_results()

    async def test_system_midi_detection(self):
        """Test 1: Basic MIDI system detection"""
        print("\n🧪 Test 1: System MIDI Detection")
        print("-" * 40)

        try:
            import rtmidi

            # Test input ports
            midi_in = rtmidi.MidiIn()
            input_ports = midi_in.get_ports()
            print(f"   📥 MIDI Input Ports: {len(input_ports)}")
            for i, port in enumerate(input_ports):
                print(f"      {i}: {port}")

            # Test output ports
            midi_out = rtmidi.MidiOut()
            output_ports = midi_out.get_ports()
            print(f"   📤 MIDI Output Ports: {len(output_ports)}")
            for i, port in enumerate(output_ports):
                print(f"      {i}: {port}")

            self.test_results['system_midi'] = {
                'status': 'success',
                'input_ports': len(input_ports),
                'output_ports': len(output_ports),
                'total_ports': len(input_ports) + len(output_ports)
            }

            if len(input_ports) == 0 and len(output_ports) == 0:
                print("   ⚠️  WARNING: No MIDI ports detected")
                print("   💡 TIP: Check MIDI drivers and system settings")
            else:
                print(f"   ✅ MIDI system operational ({len(input_ports) + len(output_ports)} total ports)")

        except Exception as e:
            print(f"   ❌ MIDI system error: {e}")
            self.test_results['system_midi'] = {
                'status': 'failed',
                'error': str(e)
            }

    async def test_traktor_device_scanning(self):
        """Test 2: Traktor-specific device detection"""
        print("\n🧪 Test 2: Traktor Device Scanning")
        print("-" * 40)

        try:
            devices = self.driver.scan_traktor_devices()

            if devices:
                print(f"   ✅ Found {len(devices)} Traktor devices:")
                for device in devices:
                    print(f"      • {device.name}")
                    if device.input_port:
                        print(f"        Input: {device.input_port}")
                    if device.output_port:
                        print(f"        Output: {device.output_port}")
            else:
                print("   ⚠️  No Traktor devices detected")
                print("   💡 TIP: Make sure Traktor Pro is running")
                print("   💡 TIP: Check Traktor MIDI settings")

            self.test_results['traktor_devices'] = {
                'status': 'success',
                'devices_found': len(devices),
                'devices': [d.name for d in devices]
            }

        except Exception as e:
            print(f"   ❌ Traktor device scan error: {e}")
            self.test_results['traktor_devices'] = {
                'status': 'failed',
                'error': str(e)
            }

    async def test_connection_methods(self):
        """Test 3: Different connection methods"""
        print("\n🧪 Test 3: Connection Methods")
        print("-" * 40)

        # Method 1: Direct connection
        print("   🔗 Testing direct connection...")
        try:
            direct_success = self.driver.connect_to_traktor_direct()
            if direct_success:
                print("   ✅ Direct connection successful")
            else:
                print("   ⚠️  Direct connection failed")
        except Exception as e:
            print(f"   ❌ Direct connection error: {e}")
            direct_success = False

        # Method 2: Virtual ports
        print("   📡 Testing virtual port creation...")
        try:
            virtual_success = self.driver.create_enhanced_virtual_ports()
            if virtual_success:
                print("   ✅ Virtual ports created successfully")
            else:
                print("   ⚠️  Virtual port creation failed")
        except Exception as e:
            print(f"   ❌ Virtual port error: {e}")
            virtual_success = False

        self.test_results['connection_methods'] = {
            'direct_connection': direct_success,
            'virtual_ports': virtual_success,
            'any_method_working': direct_success or virtual_success
        }

        if not (direct_success or virtual_success):
            print("   ❌ All connection methods failed")
            print("   💡 TIP: Check MIDI drivers and Traktor settings")
        else:
            print("   ✅ At least one connection method working")

    async def test_communication_pattern(self):
        """Test 4: Communication pattern (user's 3-second ping)"""
        print("\n🧪 Test 4: Communication Pattern (3-second ping)")
        print("-" * 40)

        if not self.test_results['connection_methods']['any_method_working']:
            print("   ⏭️  Skipping - no connection available")
            return

        try:
            print("   🚀 Starting Traktor communication...")
            comm_success = self.driver.start_traktor_communication()

            if not comm_success:
                print("   ❌ Failed to start communication")
                return

            print("   📡 Testing 3-second ping pattern (like user's working script)...")
            print("   💡 Watch Traktor's MIDI icon - it should blink!")

            pings_sent = 0
            pings_successful = 0

            for i in range(5):  # Test 5 pings
                print(f"   🏓 Ping {i+1}/5...")

                # Send ping using the same pattern as user's working script
                ping_success = self.driver.ping_traktor()

                if ping_success:
                    pings_successful += 1
                    print(f"      ✅ Ping {i+1} sent successfully")
                else:
                    print(f"      ❌ Ping {i+1} failed")

                pings_sent += 1

                # Wait 3 seconds (as per user's working script)
                if i < 4:  # Don't wait after last ping
                    print("      ⏰ Waiting 3 seconds...")
                    await asyncio.sleep(3)

            success_rate = (pings_successful / pings_sent) * 100 if pings_sent > 0 else 0

            print(f"   📊 Ping Results: {pings_successful}/{pings_sent} successful ({success_rate:.1f}%)")

            self.test_results['communication_pattern'] = {
                'status': 'success' if success_rate > 50 else 'failed',
                'pings_sent': pings_sent,
                'pings_successful': pings_successful,
                'success_rate': success_rate
            }

            if success_rate == 100:
                print("   🎉 EXCELLENT: All pings successful!")
                print("   💡 Traktor MIDI communication is working perfectly")
            elif success_rate > 50:
                print("   ⚠️  PARTIAL: Some pings failed")
                print("   💡 Check Traktor MIDI settings or port conflicts")
            else:
                print("   ❌ POOR: Most pings failed")
                print("   💡 Traktor may not be receiving MIDI properly")

        except Exception as e:
            print(f"   ❌ Communication test error: {e}")
            self.test_results['communication_pattern'] = {
                'status': 'failed',
                'error': str(e)
            }

    async def test_real_time_control(self):
        """Test 5: Real-time control messages"""
        print("\n🧪 Test 5: Real-time Control Messages")
        print("-" * 40)

        if not self.test_results.get('communication_pattern', {}).get('status') == 'success':
            print("   ⏭️  Skipping - communication pattern test failed")
            return

        try:
            print("   🎛️ Testing Traktor control messages...")

            # Test common Traktor controls
            test_controls = [
                (1, 127, "Deck A Play"),
                (1, 0, "Deck A Stop"),
                (2, 127, "Deck A Cue"),
                (20, 127, "Deck B Play"),
                (20, 0, "Deck B Stop"),
                (80, 64, "Crossfader Center"),
                (13, 100, "Deck A EQ High"),
                (14, 100, "Deck A EQ Mid"),
                (15, 100, "Deck A EQ Low")
            ]

            controls_sent = 0
            controls_successful = 0

            for cc, value, description in test_controls:
                success = self.driver.send_traktor_control(cc, value)
                controls_sent += 1

                if success:
                    controls_successful += 1
                    print(f"      ✅ {description} (CC {cc}={value})")
                else:
                    print(f"      ❌ {description} (CC {cc}={value}) FAILED")

                await asyncio.sleep(0.2)  # Small delay between controls

            success_rate = (controls_successful / controls_sent) * 100 if controls_sent > 0 else 0

            self.test_results['real_time_control'] = {
                'status': 'success' if success_rate > 80 else 'failed',
                'controls_sent': controls_sent,
                'controls_successful': controls_successful,
                'success_rate': success_rate
            }

            print(f"   📊 Control Results: {controls_successful}/{controls_sent} successful ({success_rate:.1f}%)")

            if success_rate > 80:
                print("   🎉 Real-time control is working well!")
            else:
                print("   ⚠️  Some control messages failed")

        except Exception as e:
            print(f"   ❌ Real-time control test error: {e}")
            self.test_results['real_time_control'] = {
                'status': 'failed',
                'error': str(e)
            }

    def display_diagnostic_results(self):
        """Display comprehensive diagnostic results"""
        print("\n" + "=" * 60)
        print("🏁 TRAKTOR MIDI DIAGNOSTIC RESULTS")
        print("=" * 60)

        overall_status = "✅ WORKING"
        critical_issues = []

        # Check each test
        for test_name, result in self.test_results.items():
            status = result.get('status', 'unknown')

            if test_name == 'system_midi':
                print(f"🔧 System MIDI: {status.upper()}")
                if status != 'success':
                    critical_issues.append("MIDI system not working")

            elif test_name == 'traktor_devices':
                devices_found = result.get('devices_found', 0)
                print(f"🎛️ Traktor Devices: {devices_found} found")
                if devices_found == 0:
                    print("   ⚠️  Consider: Make sure Traktor is running")

            elif test_name == 'connection_methods':
                direct = "✅" if result.get('direct_connection') else "❌"
                virtual = "✅" if result.get('virtual_ports') else "❌"
                print(f"🔗 Connections: Direct {direct} | Virtual {virtual}")
                if not result.get('any_method_working'):
                    critical_issues.append("No connection method working")

            elif test_name == 'communication_pattern':
                if status == 'success':
                    rate = result.get('success_rate', 0)
                    print(f"📡 Communication: ✅ {rate:.1f}% success rate")
                else:
                    print(f"📡 Communication: ❌ FAILED")
                    critical_issues.append("Communication pattern failed")

            elif test_name == 'real_time_control':
                if status == 'success':
                    rate = result.get('success_rate', 0)
                    print(f"🎮 Control: ✅ {rate:.1f}% success rate")
                else:
                    print(f"🎮 Control: ❌ FAILED")

        # Overall status
        if critical_issues:
            overall_status = "❌ ISSUES FOUND"

        print(f"\n🏆 Overall Status: {overall_status}")

        if critical_issues:
            print("\n🚨 Critical Issues:")
            for issue in critical_issues:
                print(f"   • {issue}")

        # Recommendations
        print("\n💡 Recommendations:")

        if 'system_midi' in self.test_results and self.test_results['system_midi']['status'] != 'success':
            print("   1. Check MIDI drivers installation")
            print("   2. Restart audio/MIDI services")

        if self.test_results.get('traktor_devices', {}).get('devices_found', 0) == 0:
            print("   3. Start Traktor Pro application")
            print("   4. Enable MIDI in Traktor Preferences > Controller Manager")

        if not self.test_results.get('connection_methods', {}).get('any_method_working', False):
            print("   5. Check MIDI port conflicts")
            print("   6. Try running as administrator/root")

        if self.test_results.get('communication_pattern', {}).get('status') != 'success':
            print("   7. Create manual MIDI mapping in Traktor")
            print("   8. Use IAC Driver (macOS) or loopMIDI (Windows)")

        # Status summary
        status = self.driver.get_traktor_status()
        print(f"\n📊 Driver Status:")
        print(f"   Traktor Detected: {status['traktor_detected']}")
        print(f"   Communication Active: {status['communication_active']}")
        print(f"   Direct Connection: {status['direct_connection']}")
        print(f"   Virtual Ports: {status['virtual_ports_active']}")

        stats = status['stats']
        print(f"   Messages Sent: {stats['messages_sent']}")
        print(f"   Traktor Pings: {stats['traktor_pings']}")
        print(f"   Errors: {stats['communication_errors']}")

        print("\n" + "=" * 60)

        # Stop the driver
        self.driver.stop()

async def main():
    """Main diagnostic function"""
    print("🎧 Traktor MIDI Communication Diagnostic")
    print("Starting comprehensive test suite...")

    # Handle interrupts gracefully
    diagnostic = TraktorDiagnostic()

    def signal_handler(signum, frame):
        print("\n\n🛑 Diagnostic interrupted")
        diagnostic.driver.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        await diagnostic.run_full_diagnostic()
        return 0

    except Exception as e:
        print(f"\n❌ Diagnostic error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)