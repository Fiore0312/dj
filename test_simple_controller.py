#!/usr/bin/env python3
"""
Test Simple DJ Controller - Rule-based system
"""

import asyncio
import logging
from simple_dj_controller import SimpleDJController
from config import DJConfig

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

async def test_simple_controller():
    """Test rule-based controller"""
    print("=" * 70)
    print("🧪 TESTING SIMPLE DJ CONTROLLER (Rule-Based, NO AI)")
    print("=" * 70)

    # Config
    config = DJConfig()
    config.simulation_mode = True

    # Create controller
    controller = SimpleDJController(config)
    await controller.start()

    # Test commands
    test_commands = [
        ("help", "Show help"),
        ("search house 120-130", "Search house tracks"),
        ("load a", "Load track to deck A"),
        ("play a", "Play deck A"),
        ("volume a 80%", "Set volume A to 80%"),
        ("sync b", "Sync deck B"),
        ("load b", "Load track to deck B"),
        ("mix a to b 20", "Mix from A to B in 20 seconds"),
        ("crossfade 50%", "Crossfader to center"),
        ("status", "Show status"),
    ]

    for i, (cmd, description) in enumerate(test_commands, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(test_commands)}: {description}")
        print(f"Command: '{cmd}'")
        print("-" * 70)

        result = await controller.execute_command(cmd)
        print(result)

        # Small delay between commands
        if "mix" in cmd:
            await asyncio.sleep(2)  # Wait a bit for mix to complete
        else:
            await asyncio.sleep(0.5)

    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)

    controller.stop()

if __name__ == "__main__":
    asyncio.run(test_simple_controller())
