#!/usr/bin/env python3
"""
🚀 Autonomous DJ Launcher
Simple launcher for Claude Agent SDK-powered autonomous DJ system
"""

import sys
import os
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import claude_agent_sdk
        return True
    except ImportError:
        return False

def install_requirements():
    """Install required packages"""
    print("📦 Installing Claude Agent SDK requirements...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements_simple.txt"],
            check=True
        )
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def check_traktor():
    """Check if Traktor MIDI is available"""
    try:
        import rtmidi
        midi_out = rtmidi.MidiOut()
        ports = midi_out.get_ports()

        # Check for IAC Driver or Traktor
        has_midi = any("IAC" in port or "Bus 1" in port or "Traktor" in port for port in ports)

        if has_midi:
            print("✅ Traktor MIDI connection available")
        else:
            print("⚠️ Traktor MIDI not detected - will use simulation mode")

        return True
    except Exception as e:
        print(f"⚠️ MIDI check warning: {e}")
        print("   System will use simulation mode")
        return True

def check_config():
    """Check if configuration is set up"""
    config_file = Path(".env")

    if not config_file.exists():
        print("⚠️ No .env file found")
        print("   Creating basic configuration...")

        # Check for Anthropic API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("\n📋 Anthropic API Key Setup:")
            print("   The autonomous DJ agent requires an Anthropic API key.")
            api_key = input("   Enter your Anthropic API key (or press Enter to skip): ").strip()

        if api_key:
            with open(".env", "w") as f:
                f.write(f"ANTHROPIC_API_KEY={api_key}\n")
            print("✅ Configuration saved to .env")
        else:
            print("⚠️ No API key provided - using OpenRouter fallback")

    return True

def print_welcome():
    """Print welcome message"""
    print("=" * 70)
    print("🎛️  AUTONOMOUS DJ AGENT - Claude Agent SDK Edition")
    print("=" * 70)
    print()
    print("This autonomous DJ system uses Claude's Agent SDK to control Traktor")
    print("via MIDI, with intelligent track selection and professional mixing.")
    print()

def print_instructions():
    """Print usage instructions"""
    print()
    print("📚 QUICK START GUIDE:")
    print("-" * 70)
    print()
    print("1. PREPARATION:")
    print("   • Ensure Traktor Pro is running")
    print("   • Enable IAC Driver in Audio MIDI Setup (macOS)")
    print("   • Import traktor/AI_DJ_Complete.tsi mapping")
    print("   • Have music files in /Users/Fiore/Music")
    print()
    print("2. RUNNING THE AGENT:")
    print("   • The agent will scan your music library")
    print("   • You'll be prompted for venue and event type")
    print("   • Give natural language commands like:")
    print("     - 'Play a house track to start the set'")
    print("     - 'Mix to an energetic tech-house track'")
    print("     - 'Find and play something with 128 BPM'")
    print()
    print("3. AUTONOMOUS MODE:")
    print("   • Type 'auto' to start fully autonomous mixing")
    print("   • The agent will select and mix tracks automatically")
    print("   • Maintains energy flow and harmonic mixing")
    print()
    print("4. COMMANDS:")
    print("   • Natural DJ commands (e.g., 'start with a warm-up track')")
    print("   • 'status' - Show current Traktor status")
    print("   • 'auto' - Start autonomous mode")
    print("   • 'quit' - Exit gracefully")
    print()
    print("-" * 70)
    print()

def main():
    """Main launcher function"""
    print_welcome()

    # Step 1: Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        print(f"   Current version: {sys.version}")
        return 1

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Step 2: Check requirements
    if not check_requirements():
        print("❌ Claude Agent SDK not installed")
        response = input("   Install now? (y/n): ").strip().lower()
        if response == 'y':
            if not install_requirements():
                return 1
        else:
            print("   Please run: pip install -r requirements_simple.txt")
            return 1

    print("✅ Claude Agent SDK available")

    # Step 3: Check Traktor MIDI
    check_traktor()

    # Step 4: Check configuration
    check_config()

    # Step 5: Print instructions
    print_instructions()

    # Step 6: Launch autonomous agent
    response = input("🚀 Ready to start? (y/n): ").strip().lower()
    if response != 'y':
        print("👋 Exiting launcher")
        return 0

    print("\n🎵 Launching Autonomous DJ Agent...")
    print("-" * 70)
    print()

    # Import and run the agent
    try:
        import asyncio
        from autonomous_dj_sdk_agent import main as agent_main

        asyncio.run(agent_main())

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n👋 Session ended successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
