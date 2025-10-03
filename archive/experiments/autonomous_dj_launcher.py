#!/usr/bin/env python3
"""
🚀 Autonomous DJ System Launcher
Easy launcher for the complete autonomous DJ system
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Import the autonomous system
from autonomous_dj_system import AutonomousDJSystem, AutonomousMode
from config import get_config, check_system_requirements

def print_banner():
    """Print system banner"""
    banner = """
🎧 ═══════════════════════════════════════════════════════════════ 🎧

    🤖 AUTONOMOUS DJ SYSTEM v2.0
    Complete AI-Powered DJ with Real-Time Mixing

    ✨ Features:
    • Real-time audio analysis with librosa + essentia
    • AI decision making with OpenRouter + Sequential Thinking MCP
    • Autonomous beatmatching and crossfading
    • Memory system for continuous learning
    • Harmonic mixing intelligence
    • Professional Traktor Pro MIDI integration

🎧 ═══════════════════════════════════════════════════════════════ 🎧
    """
    print(banner)

def check_dependencies():
    """Check system dependencies"""
    print("🔧 Checking system requirements...")

    status = check_system_requirements()

    print(f"✅ Python version: {'OK' if status['python_version'] else 'ERROR'}")
    print(f"✅ Music library: {'OK' if status['music_library'] else 'ERROR'}")
    print(f"✅ API key: {'OK' if status['api_key'] else 'ERROR'}")
    print(f"✅ MIDI system: {'OK' if status['midi_system'] else 'ERROR'}")

    if status['errors']:
        print("\n❌ Errors found:")
        for error in status['errors']:
            print(f"   - {error}")
        return False

    print("✅ All requirements satisfied!")
    return True

async def run_autonomous_session(venue: str, event: str, duration: int):
    """Run a complete autonomous DJ session"""

    # Initialize system
    print("🤖 Initializing Autonomous DJ System...")
    system = AutonomousDJSystem()

    # Setup monitoring callbacks
    def status_callback(status):
        if status.get('mixing_state') == 'mixing':
            print(f"🔄 Mixing: Deck {status.get('active_deck', '?')} -> Crossfader: {status.get('crossfader_position', 0):.2f}")

    def event_callback(event):
        event_type = event['type']
        data = event['data']

        if event_type == 'session_started':
            print(f"🎵 Session started: {data['session_id']}")
        elif event_type == 'session_stopped':
            print(f"⏹️ Session stopped: {data['session_id']}")
        elif event_type == 'track_transition':
            print(f"🔄 Track transition: {data.get('track', 'Unknown')}")
        elif event_type == 'mixer_error':
            print(f"⚠️ Mixer error: {data['error']}")

    system.add_status_callback(status_callback)
    system.add_event_callback(event_callback)

    try:
        # Initialize
        if not await system.initialize_system():
            print("❌ System initialization failed")
            return False

        print(f"🎵 Starting autonomous session:")
        print(f"   Venue: {venue}")
        print(f"   Event: {event}")
        print(f"   Duration: {duration} minutes")
        print(f"   Mode: FULLY AUTONOMOUS")
        print("\n🚨 WARNING: The AI will now take complete control of mixing!")
        print("   Press Ctrl+C to stop the session at any time")

        # Start session
        session_id = system.start_autonomous_session(venue, event, duration)

        print(f"\n🤖 AI DJ is now live! Session: {session_id}")
        print("=" * 60)

        # Monitor session
        start_time = asyncio.get_event_loop().time()
        session_duration_seconds = duration * 60

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            progress = min(1.0, elapsed / session_duration_seconds)

            # Get system status
            status = system.get_system_status()

            # Print periodic updates
            if int(elapsed) % 30 == 0:  # Every 30 seconds
                print(f"\n📊 Session Progress: {progress:.1%}")
                if status['session']:
                    print(f"   Phase: {status['session']['current_phase']}")
                    print(f"   Tracks played: {len(status['session']['played_tracks'])}")

                print(f"   Decision stats: {status['decision_stats']['total_decisions']} decisions")
                print(f"   Mix stats: {status['mixing_stats']['total_mixes']} transitions")

            # Check if session should end
            if elapsed >= session_duration_seconds:
                print(f"\n⏰ Session duration reached ({duration} minutes)")
                break

            await asyncio.sleep(1)

        # Stop session
        system.stop_session()

        # Show final stats
        final_status = system.get_system_status()
        print(f"\n📈 Final Session Statistics:")
        print(f"   Tracks mixed: {final_status['performance_metrics']['tracks_mixed']}")
        print(f"   Successful transitions: {final_status['performance_metrics']['successful_transitions']}")
        print(f"   Decision accuracy: {final_status['performance_metrics']['decision_accuracy']:.1%}")

        return True

    except KeyboardInterrupt:
        print(f"\n\n⏹️ Session interrupted by user")
        system.stop_session()
        return True

    except Exception as e:
        print(f"\n❌ Session failed: {e}")
        return False

    finally:
        system.shutdown()

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description='Autonomous DJ System Launcher')
    parser.add_argument('--venue', choices=['club', 'festival', 'bar', 'wedding', 'radio'],
                       default='club', help='Venue type')
    parser.add_argument('--event', choices=['opening', 'prime_time', 'closing', 'after_hours', 'warm_up'],
                       default='prime_time', help='Event type')
    parser.add_argument('--duration', type=int, default=60, help='Session duration in minutes')
    parser.add_argument('--check-only', action='store_true', help='Only check system requirements')

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please fix the errors above before starting the autonomous DJ")
        sys.exit(1)

    if args.check_only:
        print("\n✅ System check complete - ready for autonomous DJ operation!")
        sys.exit(0)

    print(f"\n🚀 Launching Autonomous DJ Session...")

    # Run autonomous session
    try:
        success = asyncio.run(run_autonomous_session(args.venue, args.event, args.duration))
        if success:
            print("\n🎉 Autonomous DJ session completed successfully!")
        else:
            print("\n❌ Autonomous DJ session failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()