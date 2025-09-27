#!/usr/bin/env python3
"""
Quick test to verify all TraktorPy MIDI driver imports work correctly.
"""

import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all major imports from the TraktorPy MIDI driver."""
    try:
        logger.info("Testing TraktorPy MIDI driver imports...")

        # Test main driver import
        from traktor_midi_driver import TraktorMIDIDriver, TraktorDeck
        logger.info("✓ Main driver classes imported successfully")

        # Test core components
        from traktor_midi_driver.core import MIDIManager, MessageRouter
        logger.info("✓ Core components imported successfully")

        # Test mappings
        from traktor_midi_driver.mappings import TraktorMappings, traktor_mappings
        logger.info("✓ MIDI mappings imported successfully")

        # Test controllers
        from traktor_midi_driver.controllers import DeckController, MixerController
        logger.info("✓ Controllers imported successfully")

        # Test creating a driver instance (without initializing)
        driver = TraktorMIDIDriver(client_name="ImportTest")
        logger.info("✓ Driver instance created successfully")

        # Test accessing mappings
        mappings = TraktorMappings()
        logger.info(f"✓ Mappings created - Found {len(mappings.get_all_mappings())} mapping categories")

        # Test deck enumeration
        for deck in TraktorDeck:
            logger.info(f"  - Deck {deck.value} available")

        logger.info("🎉 All imports successful! TraktorPy MIDI driver is ready to use.")
        return True

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)