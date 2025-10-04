#!/usr/bin/env python3
"""
🎛️ Autonomous DJ Traktor Agent
Professional autonomous DJ system for Traktor software with real-time decision making
and musical coherence maintenance.

Use this agent when you need:
- An autonomous DJ that can mix tracks using Traktor software
- Real-time decisions based on feedback
- Musical coherence maintenance
- Professional DJ techniques

Examples:
- When user wants DJ agent to start an evening set for a house party
- When user provides real-time feedback during a DJ set
- When user wants the DJ to operate completely autonomously for an event
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """
    Main entry point for the Autonomous DJ Traktor Agent.

    This agent is an expert autonomous DJ with deep knowledge of:
    - Music mixing and beatmatching
    - Crowd reading and energy management
    - Professional DJ techniques
    - Traktor software operation with precision
    - Intelligent, real-time decision making about track selection and mixing
    """

    print("🎛️ AUTONOMOUS DJ TRAKTOR AGENT")
    print("=" * 50)
    print()
    print("Professional autonomous DJ system for Traktor Pro")
    print("with intelligent mixing and real-time decision making.")
    print()
    print("Features:")
    print("• Autonomous track selection and mixing")
    print("• Real-time crowd feedback integration")
    print("• Professional beatmatching and harmonic mixing")
    print("• Traktor Pro MIDI control")
    print("• Musical coherence maintenance")
    print("• Natural language command interface")
    print()

    # Check if the autonomous DJ system exists
    autonomous_dj_path = project_root / "archive" / "experiments" / "autonomous_dj_sdk_agent.py"

    if autonomous_dj_path.exists():
        print("🚀 Launching autonomous DJ system...")
        print()

        # Import and run the existing autonomous DJ system
        try:
            sys.path.insert(0, str(autonomous_dj_path.parent))
            from autonomous_dj_sdk_agent import main as dj_main

            # Run the autonomous DJ
            asyncio.run(dj_main())

        except Exception as e:
            print(f"❌ Error launching autonomous DJ: {e}")
            print()
            print("Fallback: Launching basic DJ interface...")

            # Fallback to basic DJ system
            try:
                from dj_ai import main as basic_dj_main
                basic_dj_main()
            except Exception as fallback_error:
                print(f"❌ Error with fallback system: {fallback_error}")
                print("Please check system requirements and Traktor setup.")
                return 1
    else:
        print("ℹ️ Full autonomous system not found. Using basic DJ interface...")

        # Use the basic DJ system
        try:
            from dj_ai import main as basic_dj_main
            basic_dj_main()
        except Exception as e:
            print(f"❌ Error launching DJ system: {e}")
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())