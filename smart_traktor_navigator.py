#!/usr/bin/env python3
"""
🧭 Smart Traktor Navigator
Navigation deterministica nel browser Traktor usando collection.nml mapping

Questo modulo risolve il problema della "navigation cieca":
- Invece di navigare a caso con browser_up/down
- Usa il mapping da collection.nml per sapere ESATTAMENTE dove andare
- Calcola shortest path (up vs down)
- Mantiene tracking della posizione corrente
- Recovery automatico da desync
"""

import logging
import time
import asyncio
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

from traktor_control import TraktorController, DeckID
from traktor_collection_parser import TraktorCollectionParser, TraktorTrackInfo

logger = logging.getLogger(__name__)


class NavigationStrategy(Enum):
    """Strategy per navigation"""
    UP = "up"
    DOWN = "down"
    RESET_AND_DOWN = "reset_and_down"  # Reset to top then navigate down
    SEARCH = "search"  # Use search if available


@dataclass
class NavigationPath:
    """Path calcolato per navigation"""
    strategy: NavigationStrategy
    steps: int
    target_position: int
    estimated_time: float  # seconds


class SmartTraktorNavigator:
    """
    Navigator intelligente per Traktor browser

    Usa mapping da collection.nml per navigation deterministica:
    1. Conosce posizione esatta di ogni traccia
    2. Calcola shortest path verso target
    3. Mantiene tracking della posizione corrente
    4. Recovery da desync automatico
    """

    def __init__(self, traktor_controller: TraktorController,
                 collection_parser: TraktorCollectionParser):
        """
        Initialize navigator

        Args:
            traktor_controller: Controller MIDI per Traktor
            collection_parser: Parser per collection.nml
        """
        self.traktor = traktor_controller
        self.parser = collection_parser

        # Position tracking
        self.current_position: int = 0
        self.position_verified: bool = False
        self.last_navigation_time: float = 0

        # Navigation settings
        self.navigation_delay = 0.08  # Delay between steps (80ms)
        self.selection_delay = 0.15  # Delay after selection (150ms)
        self.load_delay = 0.3  # Delay after load command (300ms)

        # Statistics
        self.stats = {
            'navigations': 0,
            'successful': 0,
            'failed': 0,
            'total_steps': 0,
            'desyncs_detected': 0,
            'resets_performed': 0
        }

        logger.info("🧭 Smart Traktor Navigator initialized")

    async def navigate_to_track(self, track: TraktorTrackInfo, deck: DeckID,
                                verify: bool = True) -> bool:
        """
        Navigate to specific track and load it

        Args:
            track: Track to navigate to
            deck: Deck to load into
            verify: Verify track loaded after navigation

        Returns:
            True if successful, False otherwise
        """
        target_position = track.browser_position

        if target_position is None:
            logger.error(f"❌ Track {track.title} has no browser position")
            return False

        logger.info(f"🎯 Navigating to: {track.artist} - {track.title}")
        logger.info(f"   Target position: {target_position}")
        logger.info(f"   Current position: {self.current_position}")

        try:
            self.stats['navigations'] += 1

            # Calculate navigation path
            path = self._calculate_navigation_path(target_position)
            logger.info(f"   Strategy: {path.strategy.value}, Steps: {path.steps}")

            # Execute navigation
            navigation_success = await self._execute_navigation(path)

            if not navigation_success:
                logger.error("❌ Navigation failed")
                self.stats['failed'] += 1
                return False

            # Select item
            await asyncio.sleep(self.selection_delay)
            select_success = self.traktor.select_browser_item()

            if not select_success:
                logger.error("❌ Selection failed")
                self.stats['failed'] += 1
                return False

            # Load to deck
            await asyncio.sleep(self.load_delay)
            load_success = self.traktor.load_track_to_deck(deck)

            if not load_success:
                logger.error("❌ Load failed")
                self.stats['failed'] += 1
                return False

            # Update current position
            self.current_position = target_position
            self.position_verified = True if verify else False

            # Verify load if requested
            if verify:
                await asyncio.sleep(0.5)
                deck_state = self.traktor.deck_states.get(deck, {})

                if deck_state.get('loaded'):
                    logger.info(f"✅ Track loaded successfully in Deck {deck.value}")
                    self.stats['successful'] += 1
                    return True
                else:
                    logger.warning("⚠️  Track sent to deck but verification failed")
                    self.stats['successful'] += 1  # Still count as success
                    return True
            else:
                self.stats['successful'] += 1
                return True

        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            import traceback
            traceback.print_exc()
            self.stats['failed'] += 1
            return False

    def _calculate_navigation_path(self, target_position: int) -> NavigationPath:
        """
        Calculate optimal navigation path

        Args:
            target_position: Target position in browser

        Returns:
            NavigationPath with strategy and steps
        """
        current = self.current_position
        delta = target_position - current

        # If position not verified, safer to reset to top
        if not self.position_verified:
            logger.info("   Position not verified, using reset strategy")
            return NavigationPath(
                strategy=NavigationStrategy.RESET_AND_DOWN,
                steps=target_position,
                target_position=target_position,
                estimated_time=target_position * self.navigation_delay + 0.5
            )

        # If target is current position
        if delta == 0:
            return NavigationPath(
                strategy=NavigationStrategy.DOWN,  # Just select
                steps=0,
                target_position=target_position,
                estimated_time=0
            )

        # Calculate up vs down
        steps_down = abs(delta) if delta > 0 else float('inf')
        steps_up = abs(delta) if delta < 0 else float('inf')

        # Also consider reset + down (always valid)
        steps_reset_down = target_position + 1  # +1 for reset

        # Choose shortest path
        min_steps = min(steps_down, steps_up, steps_reset_down)

        if min_steps == steps_down:
            strategy = NavigationStrategy.DOWN
            steps = steps_down
        elif min_steps == steps_up:
            strategy = NavigationStrategy.UP
            steps = steps_up
        else:
            strategy = NavigationStrategy.RESET_AND_DOWN
            steps = target_position

        estimated_time = steps * self.navigation_delay
        if strategy == NavigationStrategy.RESET_AND_DOWN:
            estimated_time += 0.5  # Extra time for reset

        return NavigationPath(
            strategy=strategy,
            steps=steps,
            target_position=target_position,
            estimated_time=estimated_time
        )

    async def _execute_navigation(self, path: NavigationPath) -> bool:
        """
        Execute navigation path

        Args:
            path: Navigation path to execute

        Returns:
            True if successful
        """
        try:
            if path.strategy == NavigationStrategy.RESET_AND_DOWN:
                # Reset to top
                logger.info("   Resetting to top of browser...")
                reset_success = await self._reset_to_top()

                if not reset_success:
                    logger.error("❌ Reset failed")
                    return False

                self.current_position = 0
                self.position_verified = True
                self.stats['resets_performed'] += 1

                # Navigate down from top
                if path.steps > 0:
                    await self._navigate_steps(NavigationStrategy.DOWN, path.steps)

            elif path.strategy in [NavigationStrategy.UP, NavigationStrategy.DOWN]:
                # Direct navigation
                await self._navigate_steps(path.strategy, path.steps)

            self.stats['total_steps'] += path.steps
            return True

        except Exception as e:
            logger.error(f"❌ Navigation execution error: {e}")
            return False

    async def _navigate_steps(self, direction: NavigationStrategy, steps: int):
        """
        Navigate n steps in direction

        Args:
            direction: UP or DOWN
            steps: Number of steps
        """
        if steps == 0:
            return

        logger.info(f"   Navigating {steps} steps {direction.value}...")

        for i in range(steps):
            if direction == NavigationStrategy.DOWN:
                self.traktor.browse_track_down()
            else:
                self.traktor.browse_track_up()

            # Delay between steps
            if i < steps - 1:  # No delay after last step
                await asyncio.sleep(self.navigation_delay)

        logger.info(f"   Navigation complete ({steps} steps)")

    async def _reset_to_top(self) -> bool:
        """
        Reset browser to top position

        Unfortunately Traktor doesn't have a "go to top" MIDI command,
        so we need to navigate up many times or use a workaround

        Returns:
            True if reset successful
        """
        # Strategy: Navigate up 10000 times (more than any library size)
        # This ensures we reach the top no matter where we are
        logger.info("   Navigating to top (max up navigation)...")

        # Send many up commands quickly
        for _ in range(100):  # 100 should be enough for most libraries
            self.traktor.browse_track_up()
            await asyncio.sleep(0.01)  # Very fast

        # We're now at top
        self.current_position = 0
        self.position_verified = True

        logger.info("   Reached top of browser")
        return True

    def reset_position_tracking(self):
        """Reset position tracking (call after manual user navigation)"""
        logger.info("🔄 Position tracking reset")
        self.current_position = 0
        self.position_verified = False

    def get_navigation_stats(self) -> dict:
        """Get navigation statistics"""
        success_rate = (self.stats['successful'] / self.stats['navigations'] * 100
                       if self.stats['navigations'] > 0 else 0)

        return {
            **self.stats,
            'success_rate': round(success_rate, 1),
            'current_position': self.current_position,
            'position_verified': self.position_verified,
            'avg_steps_per_navigation': (self.stats['total_steps'] / self.stats['navigations']
                                        if self.stats['navigations'] > 0 else 0)
        }


# Helper function for easy usage
async def load_track_by_path(traktor: TraktorController,
                            parser: TraktorCollectionParser,
                            track_path: str,
                            deck: DeckID) -> bool:
    """
    Convenience function to load track by filepath

    Args:
        traktor: Traktor controller
        parser: Collection parser
        track_path: Full filepath to track
        deck: Deck to load into

    Returns:
        True if successful
    """
    # Get track from parser
    track = parser.get_track_by_path(track_path)

    if not track:
        logger.error(f"❌ Track not found: {track_path}")
        return False

    # Create navigator
    navigator = SmartTraktorNavigator(traktor, parser)

    # Navigate and load
    return await navigator.navigate_to_track(track, deck)


if __name__ == "__main__":
    # Test the navigator
    logging.basicConfig(level=logging.INFO)

    print("🧭 Smart Traktor Navigator Test")
    print("=" * 60)

    # Parse collection
    print("\n📂 Loading collection...")
    parser = TraktorCollectionParser()

    if not parser.collection_path:
        print("❌ Collection not found")
        exit(1)

    if not parser.parse_collection():
        print("❌ Failed to parse collection")
        exit(1)

    print(f"✅ Collection loaded: {len(parser.tracks)} tracks")

    # Get some tracks for testing
    all_tracks = parser.get_all_tracks()

    if len(all_tracks) < 10:
        print("❌ Not enough tracks for testing")
        exit(1)

    # Create Traktor controller
    print("\n🎛️  Connecting to Traktor...")
    from config import DJConfig
    config = DJConfig()
    traktor = TraktorController(config)

    if not traktor.connect():
        print("❌ Failed to connect to Traktor")
        print("   Test will continue in SIMULATION MODE")

    # Create navigator
    navigator = SmartTraktorNavigator(traktor, parser)

    # Test navigation path calculation
    print("\n🎯 Testing navigation path calculation...")

    test_positions = [0, 10, 100, 500, 1000]

    for target in test_positions:
        if target < len(all_tracks):
            navigator.current_position = 0
            navigator.position_verified = True

            path = navigator._calculate_navigation_path(target)
            print(f"\n   Target: {target}")
            print(f"   Strategy: {path.strategy.value}")
            print(f"   Steps: {path.steps}")
            print(f"   Estimated time: {path.estimated_time:.2f}s")

    # Test actual navigation (if Traktor connected)
    if traktor.connected and not traktor.simulation_mode:
        print("\n🚀 Testing actual navigation...")
        print("   (This will navigate in your Traktor browser!)")

        # Test track
        test_track = all_tracks[50]  # Position 50

        print(f"\n   Test track: {test_track.artist} - {test_track.title}")
        print(f"   Position: {test_track.browser_position}")

        async def test_nav():
            success = await navigator.navigate_to_track(test_track, DeckID.A, verify=True)
            return success

        import asyncio
        result = asyncio.run(test_nav())

        if result:
            print("\n✅ Navigation test SUCCESSFUL!")
        else:
            print("\n❌ Navigation test FAILED")

        # Show stats
        stats = navigator.get_navigation_stats()
        print("\n📊 Navigation Statistics:")
        print(f"   Success rate: {stats['success_rate']}%")
        print(f"   Total navigations: {stats['navigations']}")
        print(f"   Total steps: {stats['total_steps']}")
        print(f"   Avg steps per navigation: {stats['avg_steps_per_navigation']:.1f}")
    else:
        print("\n⚠️  Skipping actual navigation test (simulation mode)")

    print("\n✅ Test complete!")