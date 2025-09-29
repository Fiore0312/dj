#!/usr/bin/env python3
"""
🚀 Simple Autonomous DJ Launcher
Simplified version without heavy audio dependencies
Uses basic DJ AI agent for autonomous mixing
"""

import sys
import time
import argparse
from pathlib import Path

# Core imports
from config import get_config, check_system_requirements
from core.openrouter_client import get_openrouter_client, DJContext
from music_library import get_music_scanner
from traktor_control import get_traktor_controller

# Simple DJ agent (not the heavy autonomous system)
from ai_dj_agent import SimpleDJAgent

def check_dependencies():
    """Check minimal dependencies for simple autonomous mode"""
    print("🔧 Checking simple autonomous dependencies...")

    # Check basic system requirements
    status = check_system_requirements()

    errors = []
    if not status['api_key']:
        errors.append("❌ OpenRouter API key missing")
    if not status['music_library']:
        errors.append("❌ Music library not accessible")
    if not status['midi_system']:
        errors.append("❌ MIDI system not available")

    if errors:
        print("\n".join(errors))
        return False

    print("✅ All simple autonomous dependencies satisfied!")
    return True

async def run_simple_autonomous_session(venue: str, event: str, duration: int):
    """Run a simple autonomous DJ session"""
    print(f"""
🎧 ═══════════════════════════════════════════════════════════════ 🎧

    🤖 SIMPLE AUTONOMOUS DJ SYSTEM
    AI-Powered DJ with Basic Mixing Logic

    ✨ Features:
    • AI decision making with OpenRouter
    • Basic beatmatching and transitions
    • Traktor Pro MIDI integration
    • Simple music selection logic

🎧 ═══════════════════════════════════════════════════════════════ 🎧
    """)

    if not check_dependencies():
        print("❌ Dependency check failed")
        return False

    print("🚀 Launching Simple Autonomous DJ Session...")

    try:
        # Initialize components
        config = get_config()

        print("🤖 Initializing AI client...")
        ai_client = get_openrouter_client(config.openrouter_api_key)

        print("🎛️ Connecting to Traktor...")
        traktor = get_traktor_controller()

        print("🎵 Scanning music library...")
        music_scanner = get_music_scanner()

        print("🤖 Initializing DJ Agent...")
        dj_agent = SimpleDJAgent(ai_client, traktor, music_scanner)

        print(f"""
🎵 Starting simple autonomous session:
   Venue: {venue}
   Event: {event}
   Duration: {duration} minutes

⚠️  SIMPLE MODE: Basic AI mixing without advanced audio analysis
   Press Ctrl+C to stop the session at any time
        """)

        # Start session
        success = await dj_agent.start_session(venue, event, duration)

        if success:
            print("✅ Session started successfully!")

            # Simple session loop
            start_time = time.time()
            try:
                while time.time() - start_time < duration * 60:
                    await dj_agent.process_autonomous_decisions()
                    time.sleep(5)  # Check every 5 seconds

            except KeyboardInterrupt:
                print("\n🛑 Session stopped by user")

            # End session
            await dj_agent.stop_session()
            print("✅ Session completed successfully!")
            return True
        else:
            print("❌ Failed to start session")
            return False

    except Exception as e:
        print(f"❌ Error during session: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Simple Autonomous DJ System')
    parser.add_argument('--venue', type=str, default='club',
                       choices=['club', 'festival', 'bar', 'wedding', 'radio'],
                       help='Venue type for DJ session')
    parser.add_argument('--event', type=str, default='prime_time',
                       choices=['opening', 'prime_time', 'closing', 'after_hours', 'warm_up', 'cool_down'],
                       help='Event type for DJ strategy')
    parser.add_argument('--duration', type=int, default=60,
                       help='Session duration in minutes')

    args = parser.parse_args()

    print("🎧 Simple Autonomous DJ System")
    print("=" * 50)

    # Run async session
    import asyncio
    try:
        success = asyncio.run(run_simple_autonomous_session(args.venue, args.event, args.duration))
        if not success:
            print("\n❌ Simple autonomous DJ session failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Session interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()