#!/usr/bin/env python3
"""
Test Extended Commands - Simple DJ Controller
Tests all new advanced features
"""

import asyncio
import logging
from simple_dj_controller import SimpleDJController
from config import DJConfig

logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')

async def test_extended_commands():
    """Test all new extended commands"""
    print("=" * 70)
    print("🧪 TESTING EXTENDED COMMANDS - Simple DJ Controller")
    print("=" * 70)

    # Config
    config = DJConfig()
    config.simulation_mode = True

    # Create controller
    controller = SimpleDJController(config)
    await controller.start()

    # Test commands grouped by category
    test_groups = [
        ("🎛️ EQ CONTROLS", [
            ("eq a high 75%", "Set deck A high EQ to 75%"),
            ("eq b bass 50%", "Set deck B bass to 50%"),
            ("kill a bass", "Kill bass on deck A"),
            ("kill b high", "Kill highs on deck B"),
        ]),

        ("✨ EFFECTS", [
            ("fx 1 50%", "FX1 at 50%"),
            ("fx 2 off", "Turn off FX2"),
            ("fx 3 on", "Turn on FX3"),
        ]),

        ("🎵 PITCH CONTROL", [
            ("pitch a +2", "Increase deck A pitch +2%"),
            ("pitch b -1.5", "Decrease deck B pitch -1.5%"),
            ("pitch a 0", "Reset deck A pitch"),
        ]),

        ("📍 CUE POINTS", [
            ("cue a", "Jump to cue on deck A"),
            ("cue b", "Jump to cue on deck B"),
        ]),

        ("🔊 MASTER CONTROLS", [
            ("master 80%", "Set master volume to 80%"),
            ("master full", "Set master to max"),
        ]),

        ("🎯 MACRO COMMANDS", [
            ("beatmatch a b", "Auto beatmatch decks A and B"),
        ]),

        ("🚨 EMERGENCY", [
            ("emergency stop", "Emergency stop all"),
            ("panic", "Panic button (alias)"),
        ]),
    ]

    for group_name, commands in test_groups:
        print(f"\n{'='*70}")
        print(f"{group_name}")
        print("=" * 70)

        for cmd, description in commands:
            print(f"\n📝 Test: {description}")
            print(f"   Command: '{cmd}'")
            print("-" * 70)

            result = await controller.execute_command(cmd)
            print(result)

            # Small delay
            await asyncio.sleep(0.3)

    print("\n" + "=" * 70)
    print("✅ All extended command tests completed!")
    print("=" * 70)

    controller.stop()

if __name__ == "__main__":
    asyncio.run(test_extended_commands())
