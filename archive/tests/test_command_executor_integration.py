#!/usr/bin/env python3
"""
🧪 Test Command Executor Integration with MIDI Monitor
Verifica che CommandExecutor sia correttamente integrato con MIDICommunicationMonitor
"""

import time
import logging
from config import DJConfig
from traktor_control import TraktorController, DeckID
from gui.command_executor import CommandExecutor

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def test_command_executor_integration():
    """Test integration between CommandExecutor and MIDICommunicationMonitor"""
    print("\n" + "="*70)
    print("🧪 COMMAND EXECUTOR + MIDI MONITOR INTEGRATION TEST")
    print("="*70)

    # Setup
    config = DJConfig()
    traktor = TraktorController(config)

    print("\n1️⃣ Connecting to Traktor...")
    if not traktor.connect_with_gil_safety():
        print("❌ Failed to connect to Traktor")
        return False

    if traktor.simulation_mode:
        print("⚠️  Running in SIMULATION mode")
    else:
        print("✅ Connected to real Traktor MIDI")

    # Create CommandExecutor with MIDI monitor
    print("\n2️⃣ Creating CommandExecutor with MIDI Monitor...")
    executor = CommandExecutor(traktor, use_midi_monitor=True)

    if executor.midi_monitor:
        print("✅ MIDI Communication Monitor is active")
    else:
        print("⚠️  MIDI Monitor not available (optional feature)")

    # Test callbacks
    print("\n3️⃣ Setting up test callbacks...")

    def on_start(cmd_name):
        print(f"   📤 Command started: {cmd_name}")

    def on_success(result):
        print(f"   ✅ Command succeeded: {result.command_name}")
        print(f"      - Verified: {result.verified}")
        print(f"      - Execution time: {result.execution_time_ms:.0f}ms")
        print(f"      - Retry count: {result.retry_count}")

    def on_failed(result):
        print(f"   ❌ Command failed: {result.command_name}")
        print(f"      - Error: {result.error}")
        print(f"      - Retry count: {result.retry_count}")

    def on_verification(message):
        print(f"   🔍 Verification: {message}")

    executor.on_command_start = on_start
    executor.on_command_success = on_success
    executor.on_command_failed = on_failed
    executor.on_verification_status = on_verification

    # Test commands
    print("\n4️⃣ Testing command execution with verification...")

    # Test 1: Load track to Deck A
    print("\n   Test 1: Load Track to Deck A")
    result1 = executor.execute_load_track(DeckID.A, "down")
    print(f"   Result: {result1.status.value} (verified: {result1.verified})")
    time.sleep(1)

    # Test 2: Play Deck A
    print("\n   Test 2: Play Deck A")
    result2 = executor.execute_play_deck(DeckID.A)
    print(f"   Result: {result2.status.value} (verified: {result2.verified})")
    time.sleep(1)

    # Test 3: Load track to Deck B
    print("\n   Test 3: Load Track to Deck B")
    result3 = executor.execute_load_track(DeckID.B, "down")
    print(f"   Result: {result3.status.value} (verified: {result3.verified})")
    time.sleep(1)

    # Test 4: Crossfader
    print("\n   Test 4: Crossfader to 0.5")
    result4 = executor.execute_crossfader(0.5)
    print(f"   Result: {result4.status.value}")

    # Display statistics
    print("\n5️⃣ Command Executor Statistics:")
    print(f"   Success rate: {executor.get_success_rate() * 100:.0f}%")
    print(f"   Command history length: {len(executor.command_history)}")

    # Display MIDI Monitor statistics if available
    if executor.midi_monitor:
        print("\n6️⃣ MIDI Monitor Statistics:")
        midi_stats = executor.get_midi_monitor_stats()
        if midi_stats:
            print(f"   Total sent: {midi_stats['sent']}")
            print(f"   Verified: {midi_stats['verified']}")
            print(f"   Timeout: {midi_stats['timeout']}")
            print(f"   Failed: {midi_stats['failed']}")
            print(f"   Success rate: {midi_stats['success_rate']:.1f}%")
            print(f"   Currently tracking: {midi_stats['current_tracking']}")

        print("\n   Recent MIDI history:")
        history = executor.get_midi_monitor_history(5)
        for i, cmd in enumerate(history, 1):
            print(f"   {i}. {cmd.command_name} - {cmd.status.value}")
    else:
        print("\n6️⃣ MIDI Monitor not available")

    # Test timeout detection
    if executor.midi_monitor:
        print("\n7️⃣ Testing timeout detection...")
        print("   Starting a command and checking for timeout...")
        executor.midi_monitor.track_command(
            "Test Timeout Command",
            deck_id="A",
            expected_state="test",
            timeout=2.0
        )

        time.sleep(2.5)

        is_timeout = executor.midi_monitor.check_timeout()
        if is_timeout:
            print("   ✅ Timeout correctly detected")
        else:
            print("   ❌ Timeout not detected")

    # Cleanup
    print("\n8️⃣ Cleanup...")
    traktor.disconnect()
    print("✅ Disconnected from Traktor")

    print("\n" + "="*70)
    print("✅ INTEGRATION TEST COMPLETE")
    print("="*70)

    return True

if __name__ == "__main__":
    try:
        test_command_executor_integration()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
