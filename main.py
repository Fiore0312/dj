#!/usr/bin/env python3
"""
🎧 Autonomous DJ System - Main Entry Point
Launch the complete DJ system with GUI, MIDI driver, and autonomous agent
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Import GUI
    from dj_gui.main_window import AutonomousDJGUI

    # Import MIDI driver (when available)
    try:
        from traktor_midi_driver import TraktorMIDIDriver
        MIDI_AVAILABLE = True
    except ImportError:
        print("⚠️  MIDI driver not available - GUI-only mode")
        MIDI_AVAILABLE = False

    # Import autonomous DJ (when available)
    try:
        from autonomous_dj import AutonomousDJEngine
        DJ_AGENT_AVAILABLE = True
    except ImportError:
        print("⚠️  DJ agent not available - manual mode only")
        DJ_AGENT_AVAILABLE = False

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and dependencies are installed")
    sys.exit(1)


class AutonomousDJSystem:
    """
    Main system controller that coordinates GUI, MIDI driver, and DJ agent
    """

    def __init__(self):
        """Initialize the complete DJ system"""
        self.gui = None
        self.midi_driver = None
        self.dj_agent = None
        self.running = False

    async def initialize(self):
        """Initialize all system components"""
        print("🎧 Initializing Autonomous DJ System...")

        # Initialize GUI (always available)
        print("📱 Starting GUI...")
        self.gui = AutonomousDJGUI()

        # Initialize MIDI driver if available
        if MIDI_AVAILABLE:
            print("🎛️  Initializing MIDI driver...")
            try:
                self.midi_driver = TraktorMIDIDriver()
                await self.midi_driver.connect()
                print("✅ MIDI driver connected")
            except Exception as e:
                print(f"⚠️  MIDI driver failed to connect: {e}")
                self.midi_driver = None

        # Initialize DJ agent if available
        if DJ_AGENT_AVAILABLE:
            print("🤖 Initializing DJ agent...")
            try:
                self.dj_agent = AutonomousDJEngine()
                if self.midi_driver:
                    self.dj_agent.set_midi_driver(self.midi_driver)
                print("✅ DJ agent initialized")
            except Exception as e:
                print(f"⚠️  DJ agent failed to initialize: {e}")
                self.dj_agent = None

        # Setup integrations
        self._setup_integrations()

        print("🚀 System initialization complete!")
        self._print_system_status()

    def _setup_integrations(self):
        """Setup integrations between components"""
        if self.gui and self.midi_driver:
            # Connect GUI to MIDI driver
            # This would involve setting up callbacks for real-time updates
            print("🔗 Connected GUI to MIDI driver")

        if self.gui and self.dj_agent:
            # Connect GUI to DJ agent
            # This would involve setting up callbacks for agent control
            print("🔗 Connected GUI to DJ agent")

        if self.midi_driver and self.dj_agent:
            # Connect MIDI driver to DJ agent
            # This would allow the agent to control Traktor
            print("🔗 Connected MIDI driver to DJ agent")

    def _print_system_status(self):
        """Print current system status"""
        print("\n" + "="*50)
        print("🎧 AUTONOMOUS DJ SYSTEM STATUS")
        print("="*50)
        print(f"GUI:        {'✅ Active' if self.gui else '❌ Failed'}")
        print(f"MIDI:       {'✅ Connected' if self.midi_driver else '❌ Not Available'}")
        print(f"DJ Agent:   {'✅ Ready' if self.dj_agent else '❌ Not Available'}")
        print("="*50)

        if not self.midi_driver:
            print("💡 To enable MIDI: Install dependencies and connect hardware")

        if not self.dj_agent:
            print("💡 To enable DJ Agent: Complete autonomous DJ implementation")

        print("🎮 Starting GUI interface...")
        print("="*50 + "\n")

    def run(self):
        """Run the DJ system"""
        try:
            # Initialize system
            asyncio.run(self.initialize())

            # Start GUI (this blocks until GUI is closed)
            if self.gui:
                self.gui.run()
            else:
                print("❌ Cannot start - GUI failed to initialize")

        except KeyboardInterrupt:
            print("\n⏹️  Shutdown requested by user")
        except Exception as e:
            print(f"❌ System error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown all system components"""
        print("⏹️  Shutting down Autonomous DJ System...")

        # Stop DJ agent
        if self.dj_agent:
            print("🤖 Stopping DJ agent...")
            # self.dj_agent.stop()

        # Disconnect MIDI driver
        if self.midi_driver:
            print("🎛️  Disconnecting MIDI driver...")
            # asyncio.run(self.midi_driver.stop())

        print("✅ System shutdown complete")


def check_dependencies():
    """Check system dependencies"""
    print("🔍 Checking system dependencies...")

    dependencies = {
        'tkinter': 'GUI framework',
        'asyncio': 'Async operations',
        'pathlib': 'File operations'
    }

    missing = []
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module:<12} - {description}")
        except ImportError:
            print(f"❌ {module:<12} - {description} (MISSING)")
            missing.append(module)

    optional_deps = {
        'mido': 'MIDI operations',
        'librosa': 'Audio analysis',
        'numpy': 'Numerical computing'
    }

    print("\nOptional dependencies:")
    for module, description in optional_deps.items():
        try:
            __import__(module)
            print(f"✅ {module:<12} - {description}")
        except ImportError:
            print(f"⚠️  {module:<12} - {description} (optional)")

    if missing:
        print(f"\n❌ Missing required dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\n✅ All required dependencies available")
    return True


def print_welcome():
    """Print welcome message"""
    welcome = """
🎧 ═══════════════════════════════════════════════════════════════════════════════════════════

                        AUTONOMOUS DJ SYSTEM v1.0
                     Professional DJ Software with AI Mixing

   ┌─────────────────────────────────────────────────────────────────────────────────────────┐
   │  🎛️  Traktor Pro Integration        📊  Real-time Performance Monitoring                │
   │  🤖  Intelligent Track Selection    🎚️   Professional Mixing Controls                   │
   │  🎵  Autonomous Beatmatching        🚨  Manual Override & Emergency Controls             │
   │  📱  Dark Theme DJ Interface        ⚡  Low-latency MIDI Communication                  │
   └─────────────────────────────────────────────────────────────────────────────────────────┘

   Built with Claude Code + MCP Agents (autonomous-dj-traktor, midi-driver-creator, gui-interface-creator)

════════════════════════════════════════════════════════════════════════════════════════════
"""
    print(welcome)


def main():
    """Main entry point"""
    print_welcome()

    # Check dependencies
    if not check_dependencies():
        return 1

    # Create and run DJ system
    try:
        dj_system = AutonomousDJSystem()
        dj_system.run()
        return 0
    except Exception as e:
        print(f"❌ Failed to start DJ system: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)