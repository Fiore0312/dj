#!/usr/bin/env python3
"""
Test full workflow: browse -> load -> play sequence
"""

import asyncio
import logging
from autonomous_dj_hybrid import OpenRouterDJAgent
from config import DJConfig

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

async def test_workflow():
    """Test complete DJ workflow"""
    config = DJConfig()
    config.simulation_mode = True

    agent = OpenRouterDJAgent(config)
    agent.session_context.venue_type = "Club"
    agent.session_context.event_type = "House Night"
    agent.session_context.current_bpm = 128.0
    agent.session_context.energy_level = 5
    agent.active = True

    print("=" * 70)
    print("🧪 WORKFLOW TEST: Complete Track Loading and Play Sequence")
    print("=" * 70)

    test_commands = [
        "carica e fai partire una traccia house",
        "cerca tracce techno tra 125 e 135 bpm",
        "carica deck B e mixa con deck A"
    ]

    for i, cmd in enumerate(test_commands, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{ len(test_commands)}: '{cmd}'")
        print("-" * 70)

        result = await agent.execute_command(cmd)
        print(result)

    print("\n" + "=" * 70)
    print("✅ All tests complete!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_workflow())
