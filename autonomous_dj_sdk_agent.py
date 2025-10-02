#!/usr/bin/env python3
"""
🤖 Autonomous DJ Agent - Claude Agent SDK Implementation
Professional autonomous DJ system using Claude Agent SDK with custom tools
Combines AI decision-making with real-time Traktor control
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Claude Agent SDK imports
from claude_agent_sdk import query, ClaudeAgentOptions, tool

# DJ System components
from config import get_config, DJConfig
from traktor_control import TraktorController, DeckID, get_traktor_controller
from music_library import MusicLibraryScanner, TrackInfo, get_music_scanner
from core.openrouter_client import DJContext

logger = logging.getLogger(__name__)

# ==========================================
# CUSTOM TOOLS FOR DJ CONTROL
# ==========================================

@tool(
    name="load_track_to_deck",
    description="Load the currently selected track from Traktor browser into a specific deck (A or B)"
)
async def load_track_to_deck(deck: str) -> str:
    """
    Load track to specified deck.

    Args:
        deck: Deck identifier ("A" or "B")

    Returns:
        Success message or error
    """
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B

        success = traktor_controller.load_track_to_deck(deck_id)

        if success:
            return f"✅ Track loaded successfully to Deck {deck}"
        else:
            return f"❌ Failed to load track to Deck {deck}"

    except Exception as e:
        logger.error(f"Error loading track: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="play_deck",
    description="Start playing a deck. Deck must have a track loaded first."
)
async def play_deck(deck: str) -> str:
    """
    Start playing specified deck.

    Args:
        deck: Deck identifier ("A" or "B")

    Returns:
        Success message or error
    """
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B

        success = traktor_controller.force_play_deck(deck_id)

        if success:
            return f"▶️ Deck {deck} is now playing"
        else:
            return f"❌ Failed to play Deck {deck}"

    except Exception as e:
        logger.error(f"Error playing deck: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="stop_deck",
    description="Stop/pause a deck that is currently playing"
)
async def stop_deck(deck: str) -> str:
    """
    Stop playing specified deck.

    Args:
        deck: Deck identifier ("A" or "B")

    Returns:
        Success message or error
    """
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B

        success = traktor_controller.pause_deck(deck_id)

        if success:
            return f"⏸️ Deck {deck} stopped"
        else:
            return f"❌ Failed to stop Deck {deck}"

    except Exception as e:
        logger.error(f"Error stopping deck: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="set_crossfader",
    description="Move crossfader to mix between decks. 0.0 = full Deck A, 0.5 = center, 1.0 = full Deck B"
)
async def set_crossfader(position: float) -> str:
    """
    Set crossfader position for mixing.

    Args:
        position: Crossfader position (0.0 to 1.0)

    Returns:
        Success message or error
    """
    try:
        global traktor_controller

        # Clamp position between 0 and 1
        position = max(0.0, min(1.0, position))

        success = traktor_controller.set_crossfader(position)

        if success:
            if position < 0.3:
                desc = "mostly Deck A"
            elif position > 0.7:
                desc = "mostly Deck B"
            else:
                desc = "center (both decks)"
            return f"🎛️ Crossfader set to {position:.2f} ({desc})"
        else:
            return f"❌ Failed to set crossfader"

    except Exception as e:
        logger.error(f"Error setting crossfader: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="set_deck_volume",
    description="Set volume for a specific deck (0.0 = silent, 1.0 = maximum)"
)
async def set_deck_volume(deck: str, volume: float) -> str:
    """
    Set deck volume.

    Args:
        deck: Deck identifier ("A" or "B")
        volume: Volume level (0.0 to 1.0)

    Returns:
        Success message or error
    """
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B

        # Clamp volume between 0 and 1
        volume = max(0.0, min(1.0, volume))

        success = traktor_controller.set_deck_volume(deck_id, volume)

        if success:
            return f"🔊 Deck {deck} volume set to {volume:.2f}"
        else:
            return f"❌ Failed to set volume for Deck {deck}"

    except Exception as e:
        logger.error(f"Error setting volume: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="sync_deck",
    description="Sync deck BPM to master tempo for beatmatching"
)
async def sync_deck(deck: str) -> str:
    """
    Sync deck to master tempo.

    Args:
        deck: Deck identifier ("A" or "B")

    Returns:
        Success message or error
    """
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B

        success = traktor_controller.sync_deck(deck_id)

        if success:
            return f"🎯 Deck {deck} synced to master tempo"
        else:
            return f"❌ Failed to sync Deck {deck}"

    except Exception as e:
        logger.error(f"Error syncing deck: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="browse_tracks",
    description="Navigate through Traktor's track browser (up or down)"
)
async def browse_tracks(direction: str, steps: int = 1) -> str:
    """
    Browse through track list.

    Args:
        direction: Direction to browse ("up" or "down")
        steps: Number of tracks to move (default 1)

    Returns:
        Success message or error
    """
    try:
        global traktor_controller

        success_count = 0
        for _ in range(steps):
            if direction.lower() == "up":
                success = traktor_controller.browse_track_up()
            else:
                success = traktor_controller.browse_track_down()

            if success:
                success_count += 1
            time.sleep(0.1)  # Small delay between steps

        if success_count == steps:
            return f"📜 Browsed {steps} track(s) {direction}"
        else:
            return f"⚠️ Browsed {success_count}/{steps} tracks {direction}"

    except Exception as e:
        logger.error(f"Error browsing tracks: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="search_music_library",
    description="Search music library for compatible tracks by genre, BPM range, or artist"
)
async def search_music_library(
    genre: Optional[str] = None,
    min_bpm: Optional[float] = None,
    max_bpm: Optional[float] = None,
    artist: Optional[str] = None
) -> str:
    """
    Search for tracks in music library.

    Args:
        genre: Genre to filter by (optional)
        min_bpm: Minimum BPM (optional)
        max_bpm: Maximum BPM (optional)
        artist: Artist name to filter by (optional)

    Returns:
        List of matching tracks
    """
    try:
        global music_scanner

        bpm_range = None
        if min_bpm and max_bpm:
            bpm_range = (min_bpm, max_bpm)

        tracks = music_scanner.search_tracks(
            genre=genre,
            bpm_range=bpm_range,
            artist=artist,
            limit=10
        )

        if not tracks:
            return "📭 No tracks found matching criteria"

        result = f"🎵 Found {len(tracks)} track(s):\n"
        for i, track in enumerate(tracks[:5], 1):
            result += f"{i}. '{track.title}' - {track.artist} "
            result += f"({track.genre}, {track.bpm or 'unknown'} BPM)\n"

        if len(tracks) > 5:
            result += f"... and {len(tracks) - 5} more"

        return result

    except Exception as e:
        logger.error(f"Error searching library: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="get_compatible_tracks",
    description="Get tracks compatible with current BPM and genre for mixing"
)
async def get_compatible_tracks(current_bpm: float, genre: Optional[str] = None) -> str:
    """
    Find tracks compatible for mixing.

    Args:
        current_bpm: Current track BPM
        genre: Current genre (optional)

    Returns:
        List of compatible tracks
    """
    try:
        global music_scanner

        tracks = music_scanner.get_compatible_tracks(
            current_bpm=current_bpm,
            current_genre=genre,
            limit=5
        )

        if not tracks:
            return f"📭 No compatible tracks found for {current_bpm} BPM"

        result = f"🎯 Found {len(tracks)} compatible track(s) for {current_bpm} BPM:\n"
        for i, track in enumerate(tracks, 1):
            compat = track.compatible_bpm_range[0] if track.compatible_bpm_range else 0
            result += f"{i}. '{track.title}' - {track.artist} "
            result += f"({track.bpm:.0f} BPM, compatibility: {compat:.2f})\n"

        return result

    except Exception as e:
        logger.error(f"Error finding compatible tracks: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="get_traktor_status",
    description="Get current Traktor status (BPM, deck states, crossfader position)"
)
async def get_traktor_status() -> str:
    """
    Get current Traktor system status.

    Returns:
        Current system status
    """
    try:
        global traktor_controller

        status = traktor_controller.get_comprehensive_status()

        result = "🎛️ Traktor Status:\n"
        result += f"Deck A: {status['traktor_status']['deck_a_bpm']:.1f} BPM\n"
        result += f"Deck B: {status['traktor_status']['deck_b_bpm']:.1f} BPM\n"
        result += f"Crossfader: {status['traktor_status']['crossfader_position']}\n"

        # Deck states
        for deck_name, deck_state in status['browser_status']['decks_state'].items():
            result += f"Deck {deck_name}: "
            result += f"{'Playing' if deck_state['playing'] else 'Stopped'}, "
            result += f"{'Loaded' if deck_state['loaded'] else 'Empty'}\n"

        return result

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="professional_mix_transition",
    description="Execute a professional mixing transition from one deck to another with gradual crossfade"
)
async def professional_mix_transition(from_deck: str, to_deck: str, duration_seconds: int = 30) -> str:
    """
    Execute professional mixing transition.

    Args:
        from_deck: Source deck ("A" or "B")
        to_deck: Target deck ("A" or "B")
        duration_seconds: Transition duration in seconds (default 30)

    Returns:
        Success message or error
    """
    try:
        global traktor_controller

        from_deck_id = DeckID.A if from_deck.upper() == "A" else DeckID.B
        to_deck_id = DeckID.A if to_deck.upper() == "A" else DeckID.B

        result = f"🎚️ Starting professional mix: Deck {from_deck} → Deck {to_deck}\n"

        # Step 1: Ensure target deck is loaded
        if not traktor_controller.deck_states[to_deck_id]['loaded']:
            result += "⚠️ Target deck has no track loaded. Load a track first.\n"
            return result

        # Step 2: Sync target deck
        traktor_controller.sync_deck(to_deck_id)
        await asyncio.sleep(0.5)
        result += f"✓ Deck {to_deck} synced\n"

        # Step 3: Start target deck playing
        traktor_controller.force_play_deck(to_deck_id)
        await asyncio.sleep(1)
        result += f"✓ Deck {to_deck} playing\n"

        # Step 4: Gradual crossfade
        steps = 10
        step_duration = duration_seconds / steps

        for i in range(steps + 1):
            progress = i / steps

            # Calculate crossfader position based on direction
            if from_deck.upper() == "A":
                crossfader_pos = progress  # Move from A (0.0) to B (1.0)
            else:
                crossfader_pos = 1.0 - progress  # Move from B (1.0) to A (0.0)

            traktor_controller.set_crossfader(crossfader_pos)

            if i < steps:
                await asyncio.sleep(step_duration)

        result += f"✓ Crossfade completed over {duration_seconds}s\n"

        # Step 5: Stop source deck
        traktor_controller.pause_deck(from_deck_id)
        result += f"✓ Deck {from_deck} stopped\n"

        result += "✅ Professional mix transition completed!"
        return result

    except Exception as e:
        logger.error(f"Error in mix transition: {e}")
        return f"❌ Error: {str(e)}"


# ==========================================
# AUTONOMOUS DJ AGENT
# ==========================================

class AutonomousDJAgent:
    """Autonomous DJ Agent powered by Claude Agent SDK"""

    def __init__(self, config: DJConfig):
        """Initialize autonomous DJ agent"""
        self.config = config

        # Initialize components
        global traktor_controller, music_scanner
        traktor_controller = get_traktor_controller(config)
        music_scanner = get_music_scanner(config)

        # Session state
        self.active = False
        self.session_context = DJContext()

        # Agent options
        self.agent_options = ClaudeAgentOptions(
            model="claude-sonnet-4-20250514",  # Latest Sonnet
            system_prompt=self._build_system_prompt(),
            api_key=config.anthropic_api_key if hasattr(config, 'anthropic_api_key') else None,
            setting_sources=[],  # No filesystem settings
            max_tokens=2000
        )

        logger.info("🤖 Autonomous DJ Agent initialized with Claude Agent SDK")

    def _build_system_prompt(self) -> str:
        """Build optimized system prompt for autonomous DJ"""
        return """You are a PROFESSIONAL AUTONOMOUS DJ AI controlling Traktor Pro via MIDI.

🎧 YOUR ROLE:
You are a skilled DJ who can:
- SELECT and LOAD tracks from the music library
- CONTROL Traktor decks (play, stop, sync)
- EXECUTE professional mixing transitions
- MAKE real-time decisions about track selection and mixing
- MAINTAIN energy flow and crowd engagement

🎛️ AVAILABLE TOOLS:
You have direct control over Traktor through these tools:
- load_track_to_deck: Load selected track to a deck
- play_deck / stop_deck: Control deck playback
- set_crossfader: Mix between decks (0.0=A, 1.0=B)
- set_deck_volume: Control individual deck volumes
- sync_deck: Sync deck to master tempo
- browse_tracks: Navigate track browser
- search_music_library: Find tracks by genre/BPM/artist
- get_compatible_tracks: Find mixable tracks
- get_traktor_status: Check system status
- professional_mix_transition: Execute complete mix

🎯 DJ PRINCIPLES:
1. Always check deck status before loading/playing
2. Sync decks before mixing for beatmatching
3. Use gradual crossfade transitions (not instant cuts)
4. Maintain energy progression throughout the set
5. Select harmonically compatible tracks
6. Monitor BPM compatibility (±8-10% range)

⚡ WORKFLOW EXAMPLE:
User: "Start the set with a house track"
You:
1. Search for house tracks: search_music_library(genre="house")
2. Load to Deck A: load_track_to_deck(deck="A")
3. Start playing: play_deck(deck="A")

User: "Mix to the next track"
You:
1. Find compatible track: get_compatible_tracks(current_bpm=128)
2. Browse to it: browse_tracks(direction="down", steps=2)
3. Load to Deck B: load_track_to_deck(deck="B")
4. Execute professional mix: professional_mix_transition(from_deck="A", to_deck="B")

🚀 BE AUTONOMOUS: When asked to perform DJ actions, execute them immediately using your tools.
Always explain what you're doing and why (DJ technique reasoning).
"""

    async def start_session(self, venue_type: str, event_type: str, duration_minutes: int = 120):
        """Start autonomous DJ session"""
        try:
            logger.info(f"🎵 Starting autonomous session: {venue_type} - {event_type}")

            # Update context
            self.session_context.venue_type = venue_type
            self.session_context.event_type = event_type
            self.session_context.time_in_set = 0

            # Connect to Traktor
            logger.info("🔌 Connecting to Traktor...")
            if not traktor_controller.connect_with_gil_safety(output_only=True):
                raise Exception("Failed to connect to Traktor")

            # Scan music library
            logger.info("📚 Scanning music library...")
            await music_scanner.scan_library()

            self.active = True
            logger.info("✅ Autonomous DJ session started")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to start session: {e}")
            return False

    async def execute_command(self, user_command: str) -> str:
        """Execute user command through Claude Agent SDK"""
        try:
            logger.info(f"🎤 User command: {user_command}")

            # Build context-aware prompt
            full_prompt = f"""Current Context:
- Venue: {self.session_context.venue_type}
- Event: {self.session_context.event_type}
- Current BPM: {self.session_context.current_bpm}
- Energy Level: {self.session_context.energy_level}/10
- Time in set: {self.session_context.time_in_set} minutes

User Request: {user_command}

Execute this DJ command using your available tools."""

            # Query Claude Agent SDK
            response_text = ""
            async for message in query(
                prompt=full_prompt,
                options=self.agent_options
            ):
                response_text += message.get("text", "")

                # Log tool usage
                if "tool_use" in message:
                    tool_info = message["tool_use"]
                    logger.info(f"🔧 Tool used: {tool_info.get('name')}")

            return response_text

        except Exception as e:
            logger.error(f"❌ Error executing command: {e}")
            return f"❌ Error: {str(e)}"

    async def autonomous_loop(self, duration_minutes: int = 60):
        """Run fully autonomous DJ loop"""
        logger.info(f"🤖 Starting {duration_minutes}min autonomous set")

        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        # Initial track
        await self.execute_command("Start the set with an energetic track suitable for the venue")

        while time.time() < end_time and self.active:
            # Update time
            self.session_context.time_in_set = int((time.time() - start_time) / 60)

            # Every 3-4 minutes, prepare next track
            await asyncio.sleep(180)  # 3 minutes

            if self.active:
                await self.execute_command(
                    f"We're {self.session_context.time_in_set} minutes into the set. "
                    "Find and mix to an appropriate next track to maintain energy."
                )

        logger.info("🎉 Autonomous set completed")

    def stop_session(self):
        """Stop autonomous session"""
        logger.info("🛑 Stopping autonomous session...")
        self.active = False

        if traktor_controller:
            traktor_controller.disconnect()

        logger.info("✅ Session stopped")


# ==========================================
# MAIN EXECUTION
# ==========================================

async def main():
    """Main execution function"""
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("🎛️ Autonomous DJ Agent - Claude Agent SDK")
    print("=" * 60)

    # Load config
    config = get_config()

    # Create agent
    agent = AutonomousDJAgent(config)

    # Start session
    venue = input("Venue type (club/bar/festival) [club]: ").strip() or "club"
    event = input("Event type (warm_up/prime_time/closing) [prime_time]: ").strip() or "prime_time"

    success = await agent.start_session(venue, event)

    if not success:
        print("❌ Failed to start session")
        return

    print("\n🎤 Autonomous DJ Agent ready!")
    print("Commands:")
    print("  - Natural language DJ commands (e.g., 'play a house track')")
    print("  - 'auto' - Start fully autonomous mode")
    print("  - 'status' - Show system status")
    print("  - 'quit' - Exit\n")

    try:
        while True:
            user_input = input("DJ Command> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                break

            if user_input.lower() == 'auto':
                duration = int(input("Autonomous set duration (minutes) [60]: ") or 60)
                await agent.autonomous_loop(duration)
                continue

            if user_input.lower() == 'status':
                status_result = await get_traktor_status()
                print(status_result)
                continue

            # Execute command
            response = await agent.execute_command(user_input)
            print(f"\n🤖 Agent: {response}\n")

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")

    finally:
        agent.stop_session()
        print("👋 Session ended")


if __name__ == "__main__":
    asyncio.run(main())
