#!/usr/bin/env python3
"""
Complete System Test - MIDI Monitor Integration
Tests both with and without Traktor connection
"""

import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_traktor_controller():
    """Test TraktorController with crash protection"""
    print("\n" + "="*60)
    print("TEST 1: TraktorController Initialization")
    print("="*60)

    try:
        from traktor_control import TraktorController
        from config import DJConfig

        config = DJConfig()
        controller = TraktorController(config)
        print(f"✅ Controller created")

        success = controller.connect()
        print(f"✅ Connect returned: {success}")
        print(f"   Simulation mode: {controller.simulation_mode}")
        print(f"   Connected: {controller.connected}")

        if controller.simulation_mode:
            print("⚠️  SIMULATION MODE active (Traktor not available)")
        else:
            print("✅ Real MIDI connection established")

        return controller

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_midi_monitor(controller):
    """Test MIDICommunicationMonitor"""
    print("\n" + "="*60)
    print("TEST 2: MIDI Communication Monitor")
    print("="*60)

    if not controller:
        print("❌ No controller, skipping")
        return None

    try:
        from midi_communication_monitor import MIDICommunicationMonitor

        monitor = MIDICommunicationMonitor(controller)
        print("✅ Monitor created")

        # Setup callbacks
        events = []

        def on_sent(ct):
            msg = f"SENT: {ct.command_name}"
            events.append(msg)
            print(f"   📤 {msg}")

        def on_verified(ct):
            msg = f"VERIFIED: {ct.command_name}"
            events.append(msg)
            print(f"   ✅ {msg}")

        def on_timeout(ct):
            msg = f"TIMEOUT: {ct.command_name}"
            events.append(msg)
            print(f"   ⏱️  {msg}")

        monitor.on_command_sent = on_sent
        monitor.on_command_verified = on_verified
        monitor.on_command_timeout = on_timeout

        print("✅ Callbacks configured")
        return monitor, events

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, []

def test_load_track(controller, monitor, events):
    """Test load track with monitoring"""
    print("\n" + "="*60)
    print("TEST 3: Load Track with Monitoring")
    print("="*60)

    if not controller or not monitor:
        print("❌ Prerequisites missing, skipping")
        return False

    try:
        from traktor_control import DeckID

        # Track command
        monitor.track_command(
            command_name="Load Track A",
            deck_id="A",
            expected_state="loaded=True",
            timeout=2.0
        )

        # Execute load with DeckID enum
        print("   Executing load_next_track_smart(DeckID.A, 'down')...")
        success = controller.load_next_track_smart(DeckID.A, 'down')
        print(f"   Controller returned: {success}")

        # Wait for processing
        time.sleep(0.5)

        # Check state using DeckID enum
        deck_state = controller.deck_states.get(DeckID.A, {})
        loaded = deck_state.get('loaded', False)
        print(f"   Deck state loaded: {loaded}")

        if loaded:
            monitor.mark_verified()
            print("   ✅ Track loaded and verified")
        else:
            print("   ⚠️  Track not confirmed in state")

        # Check for timeout
        time.sleep(2.1)
        is_timeout = monitor.check_timeout()
        if is_timeout:
            print("   ⏱️  Timeout detected")

        return success

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_play_deck(controller, monitor, events):
    """Test play deck with monitoring"""
    print("\n" + "="*60)
    print("TEST 4: Play Deck with Monitoring")
    print("="*60)

    if not controller or not monitor:
        print("❌ Prerequisites missing, skipping")
        return False

    try:
        from traktor_control import DeckID

        # Track command
        monitor.track_command(
            command_name="Play Deck A",
            deck_id="A",
            expected_state="playing=True",
            timeout=1.5
        )

        # Execute play with DeckID enum
        print("   Executing play_deck(DeckID.A)...")
        success = controller.play_deck(DeckID.A)
        print(f"   Controller returned: {success}")

        # Wait for processing
        time.sleep(0.3)

        # Check state using DeckID enum
        deck_state = controller.deck_states.get(DeckID.A, {})
        playing = deck_state.get('playing', False)
        print(f"   Deck state playing: {playing}")

        if playing:
            monitor.mark_verified()
            print("   ✅ Deck playing and verified")
        else:
            print("   ⚠️  Play not confirmed in state")

        # Check for timeout
        time.sleep(1.6)
        is_timeout = monitor.check_timeout()
        if is_timeout:
            print("   ⏱️  Timeout detected")

        return success

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics(monitor):
    """Test statistics tracking"""
    print("\n" + "="*60)
    print("TEST 5: Statistics Tracking")
    print("="*60)

    if not monitor:
        print("❌ No monitor, skipping")
        return False

    try:
        stats = monitor.get_stats_summary()

        print(f"   Total sent: {stats['sent']}")
        print(f"   Total verified: {stats['verified']}")
        print(f"   Total timeout: {stats['timeout']}")
        print(f"   Total failed: {stats['failed']}")
        print(f"   Success rate: {stats['success_rate']:.1f}%")

        print("✅ Statistics retrieved successfully")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "🎛️ " * 20)
    print("COMPLETE SYSTEM TEST - MIDI MONITOR INTEGRATION")
    print("🎛️ " * 20)

    results = {}

    # Test 1: Controller
    controller = test_traktor_controller()
    results['Controller Init'] = controller is not None

    # Test 2: Monitor
    monitor, events = test_midi_monitor(controller) if controller else (None, [])
    results['MIDI Monitor'] = monitor is not None

    # Test 3: Load Track
    if controller and monitor:
        results['Load Track'] = test_load_track(controller, monitor, events)
    else:
        results['Load Track'] = False

    # Test 4: Play Deck
    if controller and monitor:
        results['Play Deck'] = test_play_deck(controller, monitor, events)
    else:
        results['Play Deck'] = False

    # Test 5: Statistics
    if monitor:
        results['Statistics'] = test_statistics(monitor)
    else:
        results['Statistics'] = False

    # Print event log
    if events:
        print("\n" + "="*60)
        print("EVENT LOG")
        print("="*60)
        for event in events:
            print(f"   {event}")

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)

    print(f"\nResult: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return 1

    # Cleanup
    if controller:
        try:
            controller.disconnect()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())