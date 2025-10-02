#!/usr/bin/env python3
"""
🔧 Claude SDK Tools - Fixed format for autonomous_dj_master.py
All tools with correct input_schema and return format
"""

from typing import Dict, Any, Optional
import asyncio
import logging

# These will be set by autonomous_dj_master.py
traktor_controller = None
music_scanner = None
session_state = None

logger = logging.getLogger(__name__)

# Import after globals are defined
from traktor_control import DeckID


def create_tools(tool_decorator):
    """Create all tools with the provided decorator"""

    @tool_decorator(
        name="load_track_to_deck",
        description="Load the currently selected track from Traktor browser into a specific deck (A or B)",
        input_schema={"deck": str}
    )
    async def load_track_to_deck(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        deck = args.get("deck", "A")
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.load_track_to_deck(deck_id)
        message = f"✅ Track loaded to Deck {deck}" if success else f"❌ Failed to load track to Deck {deck}"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="play_deck",
        description="Start playing a deck. Deck must have a track loaded first.",
        input_schema={"deck": str}
    )
    async def play_deck(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        deck = args.get("deck", "A")
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.force_play_deck(deck_id)
        message = f"▶️ Deck {deck} playing" if success else f"❌ Failed to play Deck {deck}"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="stop_deck",
        description="Stop/pause a deck that is currently playing",
        input_schema={"deck": str}
    )
    async def stop_deck(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        deck = args.get("deck", "A")
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.stop_deck(deck_id)
        message = f"⏸️ Deck {deck} stopped" if success else f"❌ Failed to stop Deck {deck}"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="set_crossfader",
        description="Set crossfader position. 0.0=full Deck A, 0.5=center, 1.0=full Deck B",
        input_schema={"position": float}
    )
    async def set_crossfader(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        position = args.get("position", 0.5)
        success = traktor_controller.set_crossfader(position)
        message = f"🎚️ Crossfader: {position:.0%}" if success else f"❌ Failed to set crossfader"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="set_deck_volume",
        description="Set volume for a specific deck (0.0 to 1.0)",
        input_schema={"deck": str, "volume": float}
    )
    async def set_deck_volume(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        deck = args.get("deck", "A")
        volume = args.get("volume", 0.75)
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.set_deck_volume(deck_id, volume)
        message = f"🔊 Deck {deck} volume: {volume:.0%}" if success else f"❌ Failed to set volume for Deck {deck}"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="set_eq",
        description="Set EQ band level for a deck. Band: high/mid/low, Level: 0.0 to 1.0",
        input_schema={"deck": str, "band": str, "level": float}
    )
    async def set_eq(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        deck = args.get("deck", "A")
        band = args.get("band", "mid")
        level = args.get("level", 0.5)
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.set_eq(deck_id, band, level)
        message = f"🎚️ Deck {deck} EQ {band}: {level:.0%}" if success else f"❌ Failed to set EQ for Deck {deck}"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="set_fx",
        description="Set FX unit dry/wet mix. Unit: 1-4, Mix: 0.0 to 1.0",
        input_schema={"unit": int, "mix": float}
    )
    async def set_fx(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        unit = args.get("unit", 1)
        mix = args.get("mix", 0.0)
        success = traktor_controller.set_fx(unit, mix)
        message = f"✨ FX{unit} mix: {mix:.0%}" if success else f"❌ Failed to set FX{unit}"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="sync_deck",
        description="Sync deck BPM and phase to master clock",
        input_schema={"deck": str}
    )
    async def sync_deck(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        deck = args.get("deck", "A")
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.sync_deck(deck_id)
        message = f"🔄 Deck {deck} synced" if success else f"❌ Failed to sync Deck {deck}"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="search_music_library",
        description="Search for tracks in music library by keywords (artist, title, genre, BPM)",
        input_schema={"query": str, "limit": int}
    )
    async def search_music_library(args: Dict[str, Any]) -> Dict[str, Any]:
        global music_scanner
        query = args.get("query", "")
        limit = args.get("limit", 10)

        results = await music_scanner.search_tracks(query, limit=limit)

        if not results:
            return {"content": [{"type": "text", "text": f"❌ No tracks found for '{query}'"}]}

        output = f"🔍 Found {len(results)} tracks:\n"
        for i, track in enumerate(results, 1):
            output += f"{i}. {track.artist} - {track.title} ({track.bpm} BPM, {track.genre})\n"

        return {"content": [{"type": "text", "text": output}]}

    @tool_decorator(
        name="get_session_state",
        description="Get current session state (mode, energy, venue, crowd response)",
        input_schema={}
    )
    async def get_session_state(args: Dict[str, Any]) -> Dict[str, Any]:
        global session_state
        message = f"""📊 Session State:
Mode: {session_state.mode.value.upper()}
Venue: {session_state.venue_type}
Event: {session_state.event_type}
Energy: {session_state.energy_level:.0%}
Crowd: {session_state.crowd_response}
Decisions: {session_state.total_decisions} ({session_state.approved_decisions} approved)
Deck A: {session_state.current_deck_a or 'Empty'}
Deck B: {session_state.current_deck_b or 'Empty'}"""
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="emergency_stop",
        description="EMERGENCY: Stop all decks immediately",
        input_schema={}
    )
    async def emergency_stop(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        traktor_controller.emergency_stop()
        return {"content": [{"type": "text", "text": "🚨 EMERGENCY STOP - All decks stopped"}]}

    @tool_decorator(
        name="set_pitch",
        description="Adjust pitch/tempo for a deck. Amount: -1.0 to 1.0 (percentage)",
        input_schema={"deck": str, "amount": float}
    )
    async def set_pitch(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        deck = args.get("deck", "A")
        amount = args.get("amount", 0.0)
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B

        midi_value = int(64 + (amount * 63))
        midi_value = max(0, min(127, midi_value))

        channel, cc = traktor_controller.MIDI_MAP.get(f'deck_{deck.lower()}_pitch', (1, 45))
        success = traktor_controller._send_midi_command(channel, cc, midi_value, f"Pitch {deck}")

        sign = "+" if amount >= 0 else ""
        message = f"🎵 Deck {deck} pitch: {sign}{amount*100:.1f}%" if success else f"❌ Failed to set pitch"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="trigger_cue",
        description="Trigger cue point on a deck. Point: 1-4",
        input_schema={"deck": str, "point": int}
    )
    async def trigger_cue(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        deck = args.get("deck", "A")
        point = args.get("point", 1)

        channel, cc = traktor_controller.MIDI_MAP.get(f'deck_{deck.lower()}_cue', (1, 24))
        success = traktor_controller._send_midi_command(channel, cc, 127, f"Cue {point} Deck {deck}")

        message = f"📍 Deck {deck} cue point {point} triggered" if success else f"❌ Failed to trigger cue"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="set_master_volume",
        description="Set master output volume. Level: 0.0 to 1.0",
        input_schema={"level": float}
    )
    async def set_master_volume(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        level = args.get("level", 0.75)

        channel, cc = traktor_controller.MIDI_MAP.get('master_volume', (1, 33))
        midi_value = int(level * 127)
        success = traktor_controller._send_midi_command(channel, cc, midi_value, "Master Volume")

        message = f"🔊 Master volume: {level:.0%}" if success else f"❌ Failed to set master volume"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="kill_eq_band",
        description="Kill (zero out) specific EQ band. Deck: A/B, Band: high/mid/low",
        input_schema={"deck": str, "band": str}
    )
    async def kill_eq_band(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        deck = args.get("deck", "A")
        band = args.get("band", "low")
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.set_eq(deck_id, band, 0.0)

        message = f"💀 Deck {deck} {band.upper()} KILLED" if success else f"❌ Failed to kill {band}"
        return {"content": [{"type": "text", "text": message}]}

    @tool_decorator(
        name="beatmatch_decks",
        description="Automatic beatmatching between two decks (sync, volume match, EQ reset)",
        input_schema={"deck1": str, "deck2": str}
    )
    async def beatmatch_decks(args: Dict[str, Any]) -> Dict[str, Any]:
        global traktor_controller
        deck1 = args.get("deck1", "A")
        deck2 = args.get("deck2", "B")

        result = f"🎯 Beatmatching Deck {deck1} ↔ Deck {deck2}\n"

        deck2_id = DeckID.A if deck2 == "A" else DeckID.B
        traktor_controller.sync_deck(deck2_id)
        await asyncio.sleep(0.5)
        result += f"✓ Deck {deck2} synced\n"

        for deck_name in [deck1, deck2]:
            deck_id = DeckID.A if deck_name == "A" else DeckID.B
            traktor_controller.set_deck_volume(deck_id, 0.75)
        result += f"✓ Volumes matched at 75%\n"

        for deck_name in [deck1, deck2]:
            deck_id = DeckID.A if deck_name == "A" else DeckID.B
            for band in ["high", "mid", "low"]:
                traktor_controller.set_eq(deck_id, band, 0.5)
        result += f"✓ EQs reset to neutral\n"

        result += "✅ Beatmatch complete!"
        return {"content": [{"type": "text", "text": result}]}

    return [
        load_track_to_deck, play_deck, stop_deck, set_crossfader,
        set_deck_volume, set_eq, set_fx, sync_deck,
        search_music_library, get_session_state, emergency_stop,
        set_pitch, trigger_cue, set_master_volume,
        kill_eq_band, beatmatch_decks
    ]
