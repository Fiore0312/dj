#!/usr/bin/env python3
"""
Quick test script for autonomous DJ hybrid system
Tests a single command to verify JSON extraction and execution
"""

import asyncio
import logging
from autonomous_dj_hybrid import OpenRouterDJAgent, detect_available_backend
from config import DJConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_command():
    """Test a single DJ command"""
    print("=" * 60)
    print("🧪 QUICK TEST - Autonomous DJ Hybrid System")
    print("=" * 60)

    # Check backend
    backends = detect_available_backend()
    print(f"\n🔍 Backend selected: {backends['selected']}")
    print(f"   - Claude SDK available: {backends['claude_sdk']}")
    print(f"   - OpenRouter available: {backends['openrouter']}")

    # Initialize config
    config = DJConfig()
    config.music_path = "/Users/Fiore/Music"
    config.simulation_mode = True  # Use simulation mode for testing

    # Create agent
    print("\n🤖 Initializing OpenRouter DJ Agent...")
    agent = OpenRouterDJAgent(config)

    # Start minimal session
    print("\n🎵 Starting test session...")
    agent.session_context.venue_type = "Club"
    agent.session_context.event_type = "House Night"
    agent.session_context.current_bpm = 128.0
    agent.session_context.energy_level = 5
    agent.active = True

    # Test command
    test_command = "fai partire la prima traccia"
    print(f"\n📝 Test command: '{test_command}'")
    print("-" * 60)

    result = await agent.execute_command(test_command)

    print("\n📤 Result:")
    print(result)
    print("=" * 60)

    # Show what would have been executed
    print("\n✅ Test complete!")
    print("\nℹ️ Note: This was a simulation test.")
    print("   For real Traktor control, start with: ./quick_start.sh")

if __name__ == "__main__":
    asyncio.run(test_command())
