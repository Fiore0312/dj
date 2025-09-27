#!/usr/bin/env python3
"""
🎧 Autonomous DJ System - Main Launcher
Professional AI-powered DJ system with Claude integration and robust MIDI handling
"""

import asyncio
import sys
import os
import time
import signal
import logging
from typing import Optional, Dict, Any
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import core components
from core import (
    get_sdk_master, validate_api_key,
    ClaudeConfig, DJTaskType
)
from midi.professional_midi_manager import get_midi_manager
from agents.autonomous_dj_agent import AutonomousDJAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutonomousDJSystem:
    """Main controller for the Autonomous DJ System"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Autonomous DJ System"""
        self.config = config or {}
        self.running = False
        self.start_time = None

        # Core components
        self.sdk_master = None
        self.midi_manager = None
        self.dj_agent = None

        # System state
        self.system_stats = {
            'start_time': None,
            'tracks_played': 0,
            'ai_decisions': 0,
            'midi_messages': 0,
            'errors': 0
        }

        logger.info("🎧 Autonomous DJ System initialized")

    async def start(self) -> bool:
        """Start the complete Autonomous DJ System"""
        try:
            logger.info("🚀 Starting Autonomous DJ System with Claude AI...")
            self.start_time = time.time()
            self.system_stats['start_time'] = self.start_time

            # Step 1: Validate Claude API
            if not validate_api_key():
                logger.error("❌ Claude API key validation failed")
                logger.info("💡 Set ANTHROPIC_API_KEY environment variable")
                logger.info("💡 Get your API key from: https://console.anthropic.com/")
                return False

            # Step 2: Initialize SDK Master Agent
            logger.info("🤖 Initializing Claude SDK Master Agent...")
            self.sdk_master = get_sdk_master()

            # Test AI connectivity
            test_response = await self.sdk_master.make_dj_decision(
                DJTaskType.REAL_TIME_FEEDBACK,
                "System startup test - respond with 'AI system ready'"
            )

            if test_response.success:
                logger.info(f"✅ Claude AI connected: {test_response.response[:50]}...")
            else:
                logger.warning("⚠️ Claude AI connection test failed, continuing with limited functionality")

            # Step 3: Initialize Professional MIDI Manager with Traktor Support
            logger.info("🎛️ Starting Professional MIDI Manager with Traktor integration...")
            self.midi_manager = get_midi_manager()

            # Enable Traktor-specific communication
            if not self.midi_manager.start(enable_traktor=True):
                logger.error("❌ Failed to start MIDI Manager")
                return False

            # Test MIDI functionality
            logger.info("🧪 Testing MIDI functionality...")
            latency_results = self.midi_manager.test_latency(3)
            if latency_results:
                logger.info(f"✅ MIDI latency: {latency_results['average_ms']:.2f}ms average")

            # Check Traktor integration status
            stats = self.midi_manager.get_performance_stats()
            if stats.get('traktor_mode', False):
                logger.info("🎛️ Traktor MIDI integration active")
            else:
                logger.info("📡 Using standard MIDI communication")

            # Step 4: Initialize Autonomous DJ Agent
            logger.info("🎵 Initializing Autonomous DJ Agent...")
            music_library = self.config.get('music_library_path')
            self.dj_agent = AutonomousDJAgent(music_library_path=music_library)

            # Step 5: Start DJ session if configured
            if self.config.get('auto_start_session', False):
                session_config = {
                    'venue': self.config.get('venue_type', 'club'),
                    'duration': self.config.get('session_duration', 120),
                    'genre': self.config.get('preferred_genre', 'house')
                }

                logger.info(f"🎤 Starting automatic DJ session: {session_config}")
                session_success = await self.dj_agent.start_dj_session(session_config)

                if session_success:
                    logger.info("✅ DJ session started successfully")
                else:
                    logger.warning("⚠️ DJ session start failed, continuing in manual mode")

            self.running = True
            logger.info("🎉 Autonomous DJ System started successfully!")
            self._print_startup_summary()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to start Autonomous DJ System: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _print_startup_summary(self):
        """Print startup summary with system status"""
        elapsed = time.time() - self.start_time

        print("\n" + "="*60)
        print("🎧 AUTONOMOUS DJ SYSTEM - READY")
        print("="*60)
        print(f"⏱️  Startup time: {elapsed:.2f} seconds")
        print(f"🤖 Claude AI: {'✅ Connected' if self.sdk_master else '❌ Failed'}")
        print(f"🎛️  MIDI System: {'✅ Active' if self.midi_manager else '❌ Failed'}")
        print(f"🎵 DJ Agent: {'✅ Ready' if self.dj_agent else '❌ Failed'}")

        if self.midi_manager:
            ports = self.midi_manager.get_available_ports()
            print(f"📤 Virtual Ports: {len(ports['virtual_outputs'])} output, {len(ports['virtual_inputs'])} input")

        if self.sdk_master:
            stats = self.sdk_master.get_performance_stats()
            print(f"🧠 AI Stats: {stats['total_requests']} requests, {stats['success_rate']:.1f}% success")

        print("\n💡 Available Commands:")
        print("   • start_mix() - Begin intelligent mixing")
        print("   • get_stats() - Show system statistics")
        print("   • get_advice(situation) - Get real-time DJ advice")
        print("   • stop() - Stop the system")
        print("="*60 + "\n")

    async def start_intelligent_mixing(self) -> bool:
        """Start AI-powered intelligent mixing"""
        if not self.dj_agent:
            logger.error("❌ DJ Agent not initialized")
            return False

        try:
            logger.info("🎵 Starting intelligent mixing...")
            result = await self.dj_agent.perform_intelligent_mix()

            if result:
                self.system_stats['tracks_played'] += 1
                logger.info("✅ Intelligent mix completed successfully")
            else:
                logger.warning("⚠️ Intelligent mix failed or incomplete")

            return result

        except Exception as e:
            logger.error(f"❌ Intelligent mixing error: {e}")
            self.system_stats['errors'] += 1
            return False

    async def get_real_time_advice(self, situation: str) -> str:
        """Get real-time DJ advice from Claude AI"""
        if not self.sdk_master:
            return "AI system not available"

        try:
            logger.info(f"🤖 Getting AI advice for: {situation}")
            response = await self.sdk_master.get_mixing_advice(situation)

            self.system_stats['ai_decisions'] += 1

            if response.success:
                logger.info(f"✅ AI advice received ({response.processing_time_ms}ms)")
                return response.response
            else:
                logger.warning("⚠️ AI advice request failed")
                return "Unable to get AI advice at this time"

        except Exception as e:
            logger.error(f"❌ AI advice error: {e}")
            self.system_stats['errors'] += 1
            return f"Error getting advice: {str(e)}"

    def send_midi_command(self, cc_number: int, value: int, channel: int = 0) -> bool:
        """Send a MIDI control change command"""
        if not self.midi_manager:
            logger.error("❌ MIDI Manager not available")
            return False

        try:
            success = self.midi_manager.send_control_change(cc_number, value, channel)
            if success:
                self.system_stats['midi_messages'] += 1
                logger.debug(f"📤 Sent MIDI CC {cc_number}={value}")
            return success

        except Exception as e:
            logger.error(f"❌ MIDI command error: {e}")
            self.system_stats['errors'] += 1
            return False

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0

        stats = {
            'system': {
                'uptime_seconds': round(uptime, 1),
                'uptime_minutes': round(uptime / 60, 1),
                'running': self.running,
                **self.system_stats
            }
        }

        # Add component stats
        if self.sdk_master:
            stats['claude_ai'] = self.sdk_master.get_performance_stats()

        if self.midi_manager:
            stats['midi'] = self.midi_manager.get_performance_stats()

        if self.dj_agent:
            stats['dj_agent'] = self.dj_agent.get_session_stats()

        return stats

    async def run_demo_sequence(self):
        """Run a demonstration sequence"""
        logger.info("🎬 Starting demo sequence...")

        try:
            # Demo 1: AI advice
            advice = await self.get_real_time_advice("Starting a house music set for 200 people at 10pm")
            print(f"\n🤖 AI Advice: {advice}")

            await asyncio.sleep(2)

            # Demo 2: MIDI commands
            print("\n🎛️ Testing MIDI controls...")
            for cc in [1, 2, 3]:  # Play, Cue, Sync
                success = self.send_midi_command(cc, 127)
                print(f"   CC {cc}: {'✅' if success else '❌'}")
                await asyncio.sleep(0.5)

            # Demo 3: Intelligent mixing (if session active)
            if self.dj_agent and self.dj_agent.mix_session:
                print("\n🎵 Demonstrating intelligent mixing...")
                mix_result = await self.start_intelligent_mixing()
                print(f"   Intelligent mix: {'✅' if mix_result else '❌'}")

            # Demo 4: System stats
            print("\n📊 System Statistics:")
            stats = self.get_system_stats()
            for category, data in stats.items():
                print(f"   {category.upper()}:")
                for key, value in data.items():
                    print(f"     {key}: {value}")

            logger.info("✅ Demo sequence completed")

        except Exception as e:
            logger.error(f"❌ Demo sequence error: {e}")

    async def stop(self):
        """Stop the Autonomous DJ System"""
        logger.info("🛑 Stopping Autonomous DJ System...")

        self.running = False

        try:
            # Stop DJ session
            if self.dj_agent:
                await self.dj_agent.stop_session()
                logger.info("🎵 DJ Agent stopped")

            # Stop MIDI manager
            if self.midi_manager:
                self.midi_manager.stop()
                logger.info("🎛️ MIDI Manager stopped")

            # Final stats
            uptime = time.time() - self.start_time if self.start_time else 0
            logger.info(f"📊 Session summary:")
            logger.info(f"   Uptime: {uptime/60:.1f} minutes")
            logger.info(f"   Tracks played: {self.system_stats['tracks_played']}")
            logger.info(f"   AI decisions: {self.system_stats['ai_decisions']}")
            logger.info(f"   MIDI messages: {self.system_stats['midi_messages']}")
            logger.info(f"   Errors: {self.system_stats['errors']}")

            logger.info("✅ Autonomous DJ System stopped successfully")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

# Global system instance
_dj_system = None

def get_dj_system() -> AutonomousDJSystem:
    """Get the global DJ system instance"""
    global _dj_system
    if _dj_system is None:
        _dj_system = AutonomousDJSystem()
    return _dj_system

# CLI Interface
async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Autonomous DJ System - Claude AI Powered")
    parser.add_argument('--demo', action='store_true',
                       help='Run demonstration sequence')
    parser.add_argument('--auto-start', action='store_true',
                       help='Automatically start DJ session')
    parser.add_argument('--venue', default='club',
                       choices=['club', 'festival', 'wedding', 'party'],
                       help='Venue type for DJ session')
    parser.add_argument('--duration', type=int, default=120,
                       help='Session duration in minutes')
    parser.add_argument('--music-library', type=str,
                       help='Path to music library')
    parser.add_argument('--config', type=str,
                       help='Path to configuration file')

    args = parser.parse_args()

    # Build configuration
    config = {
        'auto_start_session': args.auto_start,
        'venue_type': args.venue,
        'session_duration': args.duration,
        'music_library_path': args.music_library,
    }

    # Initialize system
    dj_system = AutonomousDJSystem(config)

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(dj_system.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start the system
        success = await dj_system.start()

        if not success:
            logger.error("❌ Failed to start Autonomous DJ System")
            return 1

        # Run demo if requested
        if args.demo:
            await dj_system.run_demo_sequence()

        # Keep running until stopped
        if not args.demo:
            logger.info("🎧 System running... Press Ctrl+C to stop")
            try:
                while dj_system.running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")

        # Shutdown
        await dj_system.stop()
        return 0

    except Exception as e:
        logger.error(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Set event loop policy for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    exit_code = asyncio.run(main())
    sys.exit(exit_code)