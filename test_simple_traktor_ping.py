#!/usr/bin/env python3
"""
🏓 Simple Traktor Ping Test - Based on User's Working Script
Replicates the user's successful 3-second ping pattern that made Traktor's MIDI icon blink
"""

import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import rtmidi
    print("✅ rtmidi available")
except ImportError:
    print("❌ rtmidi not available. Install with: pip install python-rtmidi")
    sys.exit(1)

def simple_traktor_ping_test():
    """
    Simple test that replicates the user's working script:
    - Send MIDI signal every 3 seconds
    - Make Traktor's MIDI icon blink
    - Use the exact pattern that worked before
    """
    print("🏓 SIMPLE TRAKTOR PING TEST")
    print("=" * 50)
    print("Based on user's working 3-second ping script")
    print("This should make Traktor's MIDI icon blink!")
    print("=" * 50)

    # Try multiple connection methods
    methods_to_try = [
        ("Direct Traktor Port", try_direct_traktor_connection),
        ("Virtual Port", try_virtual_port_connection),
        ("System Default Output", try_system_default_connection)
    ]

    for method_name, method_func in methods_to_try:
        print(f"\n🔧 Testing Method: {method_name}")
        print("-" * 30)

        success = method_func()
        if success:
            print(f"✅ SUCCESS with {method_name}!")
            break
        else:
            print(f"❌ FAILED with {method_name}")

    print("\n" + "=" * 50)
    print("🏁 TEST COMPLETED")
    print("=" * 50)

def try_direct_traktor_connection():
    """Try connecting directly to Traktor MIDI ports"""
    try:
        # Scan for Traktor ports
        midi_out = rtmidi.MidiOut()
        output_ports = midi_out.get_ports()

        print(f"📋 Available output ports ({len(output_ports)}):")
        for i, port in enumerate(output_ports):
            print(f"   {i}: {port}")

        # Look for Traktor-specific ports
        traktor_port_idx = None
        traktor_patterns = ['traktor', 'TRAKTOR', 'Traktor', 'Native', 'Controller']

        for i, port in enumerate(output_ports):
            for pattern in traktor_patterns:
                if pattern.lower() in port.lower():
                    traktor_port_idx = i
                    print(f"🎯 Found potential Traktor port: {port}")
                    break
            if traktor_port_idx is not None:
                break

        if traktor_port_idx is None:
            print("⚠️ No Traktor ports detected")
            return False

        # Connect to Traktor port
        midi_out.open_port(traktor_port_idx)
        print(f"🔗 Connected to port {traktor_port_idx}: {output_ports[traktor_port_idx]}")

        # Send the ping pattern (3-second intervals)
        return send_ping_pattern(midi_out, output_ports[traktor_port_idx])

    except Exception as e:
        print(f"❌ Direct connection error: {e}")
        return False

def try_virtual_port_connection():
    """Try creating a virtual port for Traktor communication"""
    try:
        # Create virtual output port
        midi_out = rtmidi.MidiOut()
        virtual_port_name = "TraktorPing_Virtual"
        midi_out.open_virtual_port(virtual_port_name)

        print(f"✅ Created virtual port: {virtual_port_name}")
        print("💡 You can now map this port in Traktor Controller Manager")

        # Send the ping pattern
        return send_ping_pattern(midi_out, virtual_port_name)

    except Exception as e:
        print(f"❌ Virtual port error: {e}")
        return False

def try_system_default_connection():
    """Try using the first available system output port"""
    try:
        midi_out = rtmidi.MidiOut()
        output_ports = midi_out.get_ports()

        if not output_ports:
            print("❌ No MIDI output ports available")
            return False

        # Use first available port
        first_port = output_ports[0]
        midi_out.open_port(0)
        print(f"🔗 Connected to first available port: {first_port}")

        # Send the ping pattern
        return send_ping_pattern(midi_out, first_port)

    except Exception as e:
        print(f"❌ System default connection error: {e}")
        return False

def send_ping_pattern(midi_out, port_name):
    """
    Send the actual ping pattern that worked for the user:
    - MIDI signal every 3 seconds
    - Should make Traktor's MIDI icon blink
    """
    try:
        print(f"\n🏓 Starting ping pattern on: {port_name}")
        print("💡 Watch Traktor's MIDI icon - it should blink!")
        print("⚠️ Press Ctrl+C to stop")

        ping_count = 0
        successful_pings = 0

        while True:
            try:
                ping_count += 1

                # Send a safe MIDI CC message (CC 127 is usually safe for testing)
                # This replicates the pattern that worked for the user
                midi_message = [0xB0, 127, 64]  # Control Change, CC 127, value 64
                midi_out.send_message(midi_message)

                print(f"🏓 Ping {ping_count} sent: CC 127 = 64")
                successful_pings += 1

                # Small delay, then send off message to create blink effect
                time.sleep(0.1)
                off_message = [0xB0, 127, 0]  # Turn off
                midi_out.send_message(off_message)

                # Wait 3 seconds (as per user's working script)
                print("   ⏰ Waiting 3 seconds...")
                time.sleep(3)

                # Every 5 pings, show status
                if ping_count % 5 == 0:
                    print(f"📊 Status: {successful_pings}/{ping_count} pings successful")

            except KeyboardInterrupt:
                print(f"\n\n🛑 Ping test stopped by user")
                break

            except Exception as e:
                print(f"❌ Ping {ping_count} failed: {e}")
                time.sleep(1)  # Brief pause before retrying

        # Final statistics
        success_rate = (successful_pings / ping_count * 100) if ping_count > 0 else 0
        print(f"\n📊 Final Results:")
        print(f"   Total pings: {ping_count}")
        print(f"   Successful: {successful_pings}")
        print(f"   Success rate: {success_rate:.1f}%")

        if success_rate > 80:
            print("🎉 EXCELLENT: Communication working well!")
            return True
        elif success_rate > 50:
            print("⚠️ PARTIAL: Some communication issues")
            return True
        else:
            print("❌ POOR: Major communication problems")
            return False

    except Exception as e:
        print(f"❌ Ping pattern error: {e}")
        return False

    finally:
        try:
            midi_out.close()
        except:
            pass

if __name__ == "__main__":
    print("🎧 Simple Traktor Ping Test")
    print("Replicating the user's working 3-second ping pattern")
    print()

    try:
        simple_traktor_ping_test()
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

    print("\n👋 Test completed")