#!/usr/bin/env python3
"""
Agent Navigation Execution Test
--------------------------------
Navigate from "Ableton" to "Dub" folder using browser tree navigation.

Current position: "Ableton" (index 0)
Target position: "Dub" (index 12)
Steps needed: 12 DOWN movements
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.traktor_control import get_traktor_controller
from core.config import get_config


def navigate_to_dub():
    """Navigate from Ableton to Dub folder."""
    print("=" * 60)
    print("AGENT NAVIGATION EXECUTION")
    print("=" * 60)

    # Initialize configuration
    print("\n[1/4] Loading configuration...")
    config = get_config()
    print(f"   - MIDI device: {config.midi_device_name}")
    print(f"   - IAC bus: {config.iac_bus_name}")

    # Get Traktor controller instance
    print("\n[2/4] Initializing Traktor controller...")
    try:
        controller = get_traktor_controller(config)
        print("   - Controller initialized successfully")

        # Connect to Traktor
        print("\n[2.5/4] Connecting to Traktor via MIDI...")
        connection_success = controller.connect(output_only=True)

        if not connection_success:
            print("   - ERROR: Failed to connect to Traktor")
            print("   - Please ensure:")
            print("     1. Traktor Pro is running")
            print("     2. IAC Driver is enabled in Audio MIDI Setup")
            print("     3. Traktor MIDI mappings are loaded")
            return False

        if controller.simulation_mode:
            print("   - WARNING: Running in SIMULATION MODE")
            print("   - Commands will be logged but not sent to Traktor")
            print("   - To connect properly:")
            print("     1. Open Audio MIDI Setup")
            print("     2. Enable 'IAC Driver' > 'Device is online'")
            print("     3. Ensure 'Bus 1' exists")
            print("     4. Restart Traktor Pro")
        else:
            print("   - MIDI connection established successfully")
            print(f"   - Connected: {controller.connected}")

    except Exception as e:
        print(f"   - ERROR: Failed to initialize controller: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Calculate navigation path
    current_folder = "Ableton"
    target_folder = "Dub"
    steps_down = 12

    print(f"\n[3/4] Navigation plan:")
    print(f"   - Current folder: {current_folder}")
    print(f"   - Target folder: {target_folder}")
    print(f"   - Steps DOWN needed: {steps_down}")
    print(f"   - Delay between steps: 0.5 seconds")

    # Execute navigation
    print(f"\n[4/4] Executing navigation...")
    try:
        for step in range(1, steps_down + 1):
            print(f"   - Step {step}/{steps_down}: Sending browser_tree_down()")
            controller.browser_tree_down()

            # Add delay between steps (except after last step)
            if step < steps_down:
                time.sleep(0.5)

        print(f"\n{'=' * 60}")
        print("NAVIGATION COMPLETE")
        print(f"{'=' * 60}")
        print(f"\nExecuted {steps_down} DOWN movements")
        print(f"Expected result: Browser should now be on '{target_folder}' folder")
        print(f"\nNext step: Run music-vision-navigator to verify the current folder")

        return True

    except Exception as e:
        print(f"\n   - ERROR during navigation: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = navigate_to_dub()
    sys.exit(0 if success else 1)
