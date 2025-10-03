#!/usr/bin/env python3
"""
🤖 Autonomous DJ Agent - Hybrid Implementation
Supports both Claude Agent SDK (Anthropic) and OpenRouter (Free models)
Automatically detects available API keys and uses best option
"""

import asyncio
import time
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# DJ System components
from config import get_config, DJConfig
from traktor_control import TraktorController, DeckID, get_traktor_controller
from music_library import MusicLibraryScanner, TrackInfo, get_music_scanner
from core.openrouter_client import DJContext, OpenRouterClient, get_openrouter_client

logger = logging.getLogger(__name__)

# ==========================================
# DETECT AVAILABLE API KEYS
# ==========================================

def detect_available_backend():
    """Detect which API backend is available"""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    # Check if Claude Agent SDK can be imported
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions, tool
        has_claude_sdk = True
    except ImportError:
        has_claude_sdk = False

    backends = {
        "claude_sdk": has_claude_sdk and bool(anthropic_key),
        "openrouter": bool(openrouter_key) or True,  # OpenRouter ha fallback hardcoded
        "anthropic_key": anthropic_key,
        "openrouter_key": openrouter_key
    }

    # Determine best backend
    if backends["claude_sdk"]:
        backends["selected"] = "claude_sdk"
    else:
        backends["selected"] = "openrouter"

    return backends


# ==========================================
# GLOBAL CONTROLLER REFERENCES
# ==========================================

traktor_controller: Optional[TraktorController] = None
music_scanner: Optional[MusicLibraryScanner] = None


# ==========================================
# TOOL FUNCTIONS (Work with both backends)
# ==========================================

async def tool_load_track_to_deck(deck: str) -> str:
    """Load track to specified deck"""
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


async def tool_play_deck(deck: str) -> str:
    """Start playing specified deck"""
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


async def tool_stop_deck(deck: str) -> str:
    """Stop playing specified deck"""
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


async def tool_set_crossfader(position: float) -> str:
    """Set crossfader position"""
    try:
        global traktor_controller
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


async def tool_sync_deck(deck: str) -> str:
    """Sync deck to master tempo"""
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


async def tool_search_music_library(
    genre: Optional[str] = None,
    min_bpm: Optional[float] = None,
    max_bpm: Optional[float] = None
) -> str:
    """Search for tracks in music library"""
    try:
        global music_scanner
        bpm_range = None
        if min_bpm and max_bpm:
            bpm_range = (min_bpm, max_bpm)

        tracks = music_scanner.search_tracks(
            genre=genre,
            bpm_range=bpm_range,
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


async def tool_professional_mix(from_deck: str, to_deck: str, duration: int = 30) -> str:
    """Execute professional mixing transition"""
    try:
        global traktor_controller

        from_deck_id = DeckID.A if from_deck.upper() == "A" else DeckID.B
        to_deck_id = DeckID.A if to_deck.upper() == "A" else DeckID.B

        result = f"🎚️ Starting professional mix: Deck {from_deck} → Deck {to_deck}\n"

        # Check target deck loaded
        if not traktor_controller.deck_states[to_deck_id]['loaded']:
            result += "⚠️ Target deck has no track loaded\n"
            return result

        # Sync target deck
        traktor_controller.sync_deck(to_deck_id)
        await asyncio.sleep(0.5)
        result += f"✓ Deck {to_deck} synced\n"

        # Start target deck
        traktor_controller.force_play_deck(to_deck_id)
        await asyncio.sleep(1)
        result += f"✓ Deck {to_deck} playing\n"

        # Gradual crossfade
        steps = 10
        step_duration = duration / steps

        for i in range(steps + 1):
            progress = i / steps
            if from_deck.upper() == "A":
                crossfader_pos = progress
            else:
                crossfader_pos = 1.0 - progress

            traktor_controller.set_crossfader(crossfader_pos)

            if i < steps:
                await asyncio.sleep(step_duration)

        result += f"✓ Crossfade completed over {duration}s\n"

        # Stop source deck
        traktor_controller.pause_deck(from_deck_id)
        result += f"✓ Deck {from_deck} stopped\n"
        result += "✅ Professional mix transition completed!"

        return result

    except Exception as e:
        logger.error(f"Error in mix transition: {e}")
        return f"❌ Error: {str(e)}"


# ==========================================
# OPENROUTER BACKEND
# ==========================================

class OpenRouterDJAgent:
    """DJ Agent using OpenRouter (free models)"""

    def __init__(self, config: DJConfig):
        """Initialize OpenRouter-based agent"""
        self.config = config

        global traktor_controller, music_scanner
        traktor_controller = get_traktor_controller(config)
        music_scanner = get_music_scanner(config)

        # OpenRouter client
        self.client = get_openrouter_client(
            config.openrouter_api_key if hasattr(config, 'openrouter_api_key') else None
        )

        self.active = False
        self.session_context = DJContext()

        logger.info("🤖 OpenRouter DJ Agent initialized (FREE models)")

    def _build_system_prompt(self) -> str:
        """Build system prompt for OpenRouter"""
        return """Sei un DJ AI PROFESSIONALE che controlla Traktor Pro tramite MIDI.

⚠️ REGOLA CRITICA: Puoi SOLO usare questi comandi JSON esatti. NON inventare nuovi comandi!

🎧 COMANDI DISPONIBILI (COPIA ESATTAMENTE):

📀 CARICARE E RIPRODURRE:
{"action": "load_track", "deck": "A"}     ← Carica traccia selezionata nel browser
{"action": "play_deck", "deck": "A"}      ← Avvia riproduzione
{"action": "stop_deck", "deck": "A"}      ← Ferma deck

🎛️ MIXING:
{"action": "set_crossfader", "position": 0.5}    ← Sposta crossfader (0.0=A, 1.0=B)
{"action": "sync_deck", "deck": "B"}             ← Sincronizza BPM
{"action": "professional_mix", "from_deck": "A", "to_deck": "B", "duration": 30}  ← Mix automatico

🎵 LIBRERIA:
{"action": "search_library", "genre": "house", "min_bpm": 120, "max_bpm": 130}  ← Cerca musica
{"action": "browse_tracks", "direction": "down", "steps": 1}  ← Naviga (up/down)

⚠️ FORMATO RISPOSTA:
1. Testo breve in italiano (1 riga)
2. Uno o più comandi JSON (ESATTAMENTE come sopra, senza ```json```)

✅ ESEMPIO VALIDO:
Carico e avvio la prima traccia house.
{"action": "browse_tracks", "direction": "down", "steps": 1}
{"action": "load_track", "deck": "A"}
{"action": "play_deck", "deck": "A"}

❌ ERRORI DA EVITARE:
- NON usare "azione" (usa "action")
- NON inventare campi come "traccia", "volumi", "BPM"
- NON usare ```json``` code blocks
- NON creare comandi custom

🎯 IMPORTANTE: DEVI usare SOLO i comandi elencati sopra, ESATTAMENTE come scritti!
"""

    async def execute_command(self, user_command: str) -> str:
        """Execute user command through OpenRouter"""
        try:
            logger.info(f"🎤 User command: {user_command}")

            # Build prompt with examples
            full_prompt = f"""SESSIONE DJ CORRENTE:
- Locale: {self.session_context.venue_type}
- Evento: {self.session_context.event_type}
- BPM Attuale: {self.session_context.current_bpm}
- Energia: {self.session_context.energy_level}/10

RICHIESTA UTENTE: {user_command}

IMPORTANTE: Rispondi SOLO con i comandi JSON validi dalla lista. NON inventare campi custom!

ESEMPI DI RISPOSTE CORRETTE:
User: "carica una traccia house"
AI: Cerco traccia house adatta.
{{"action": "search_library", "genre": "house", "min_bpm": 120, "max_bpm": 130}}

User: "fai partire deck A"
AI: Avvio Deck A.
{{"action": "play_deck", "deck": "A"}}

User: "carica deck B"
AI: Carico traccia nel Deck B.
{{"action": "load_track", "deck": "B"}}

User: "passa al deck B"
AI: Transizione verso Deck B.
{{"action": "professional_mix", "from_deck": "A", "to_deck": "B", "duration": 30}}

ORA RISPONDI ALLA RICHIESTA SOPRA NEL FORMATO CORRETTO:"""

            # Query OpenRouter
            response = self.client.get_dj_decision(
                self.session_context,
                full_prompt,
                autonomous_mode=True
            )

            if not response.success:
                return f"❌ AI Error: {response.error}"

            ai_text = response.response
            logger.info(f"🤖 AI Response: {ai_text}")

            # Extract JSON actions from response text
            actions = self._extract_json_actions(ai_text)

            if actions:
                results = []
                for action in actions:
                    result = await self._execute_action(action)
                    results.append(result)

                return f"🤖 {ai_text}\n\n" + "\n".join(results)
            else:
                # Fallback: try using response.decision
                if response.decision:
                    result = await self._execute_action(response.decision)
                    return f"🤖 {ai_text}\n\n{result}"
                else:
                    return f"🤖 {ai_text}\n\n⚠️ No executable JSON found in response"

        except Exception as e:
            logger.error(f"❌ Error executing command: {e}")
            return f"❌ Error: {str(e)}"

    def _extract_json_actions(self, text: str) -> List[Dict]:
        """Extract JSON action objects from AI response text"""
        import json
        import re

        actions = []

        # Remove code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)

        # Find all JSON-like objects in the text
        # Pattern matches: {"action": "...", ...}
        # More flexible pattern to catch nested objects
        json_pattern = r'\{[^{}]*?"action"\s*:\s*"[^"]+?"[^{}]*?\}'

        matches = re.findall(json_pattern, text, re.DOTALL)

        for match in matches:
            try:
                # Clean up the match (remove extra whitespace)
                clean_match = ' '.join(match.split())
                action = json.loads(clean_match)
                if "action" in action:
                    actions.append(action)
                    logger.info(f"✅ Extracted JSON action: {action}")
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Failed to parse JSON: {match[:100]}... Error: {e}")
                continue

        return actions

    async def _execute_action(self, action_dict: Dict) -> str:
        """Execute action from JSON"""
        try:
            action = action_dict.get("action")

            if action == "load_track":
                return await tool_load_track_to_deck(action_dict.get("deck", "A"))

            elif action == "play_deck":
                return await tool_play_deck(action_dict.get("deck", "A"))

            elif action == "stop_deck":
                return await tool_stop_deck(action_dict.get("deck", "A"))

            elif action == "set_crossfader":
                return await tool_set_crossfader(action_dict.get("position", 0.5))

            elif action == "sync_deck":
                return await tool_sync_deck(action_dict.get("deck", "A"))

            elif action == "professional_mix":
                return await tool_professional_mix(
                    action_dict.get("from_deck", "A"),
                    action_dict.get("to_deck", "B"),
                    action_dict.get("duration", 30)
                )

            elif action == "search_library":
                return await tool_search_music_library(
                    genre=action_dict.get("genre"),
                    min_bpm=action_dict.get("min_bpm"),
                    max_bpm=action_dict.get("max_bpm")
                )

            elif action == "browse_tracks":
                return await tool_browse_tracks(
                    direction=action_dict.get("direction", "down"),
                    steps=action_dict.get("steps", 1)
                )

            else:
                return f"⚠️ Unknown action: {action}"

        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return f"❌ Error: {str(e)}"

    async def start_session(self, venue_type: str, event_type: str):
        """Start DJ session"""
        logger.info(f"🎵 Starting session: {venue_type} - {event_type}")

        self.session_context.venue_type = venue_type
        self.session_context.event_type = event_type

        # Connect to Traktor
        if not traktor_controller.connect_with_gil_safety(output_only=True):
            raise Exception("Failed to connect to Traktor")

        # Scan music library
        await music_scanner.scan_library()

        self.active = True
        logger.info("✅ Session started with OpenRouter")

    def stop_session(self):
        """Stop session"""
        self.active = False
        if traktor_controller:
            traktor_controller.disconnect()


# ==========================================
# CLAUDE SDK BACKEND (if available)
# ==========================================

class ClaudeSDKDJAgent:
    """DJ Agent using Claude Agent SDK (Anthropic)"""

    def __init__(self, config: DJConfig):
        """Initialize Claude SDK agent"""
        from claude_agent_sdk import query, ClaudeAgentOptions, tool

        self.config = config

        global traktor_controller, music_scanner
        traktor_controller = get_traktor_controller(config)
        music_scanner = get_music_scanner(config)

        # Register tools dynamically
        self._register_tools()

        self.active = False
        self.session_context = DJContext()

        # Agent options
        self.agent_options = ClaudeAgentOptions(
            model="claude-sonnet-4-20250514",
            system_prompt=self._build_system_prompt(),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            setting_sources=[],
            max_tokens=2000
        )

        logger.info("🤖 Claude SDK DJ Agent initialized")

    def _register_tools(self):
        """Register tools with Claude SDK"""
        from claude_agent_sdk import tool

        # Register each tool function
        tool(name="load_track_to_deck", description="Load track to deck")(tool_load_track_to_deck)
        tool(name="play_deck", description="Start playing deck")(tool_play_deck)
        tool(name="stop_deck", description="Stop deck")(tool_stop_deck)
        tool(name="set_crossfader", description="Move crossfader")(tool_set_crossfader)
        tool(name="sync_deck", description="Sync deck to master")(tool_sync_deck)
        tool(name="search_music_library", description="Search library")(tool_search_music_library)
        tool(name="professional_mix", description="Execute mix transition")(tool_professional_mix)

    def _build_system_prompt(self) -> str:
        """Build system prompt for Claude SDK"""
        return """You are a PROFESSIONAL DJ AI with direct Traktor control.

Use your tools to execute DJ commands immediately.
Always explain your DJ technique reasoning."""

    async def execute_command(self, user_command: str) -> str:
        """Execute command through Claude SDK"""
        from claude_agent_sdk import query

        try:
            full_prompt = f"""Current Context:
- Venue: {self.session_context.venue_type}
- Event: {self.session_context.event_type}
- BPM: {self.session_context.current_bpm}

User Request: {user_command}"""

            response_text = ""
            async for message in query(prompt=full_prompt, options=self.agent_options):
                response_text += message.get("text", "")

            return response_text

        except Exception as e:
            logger.error(f"Error: {e}")
            return f"❌ Error: {str(e)}"

    async def start_session(self, venue_type: str, event_type: str):
        """Start session"""
        self.session_context.venue_type = venue_type
        self.session_context.event_type = event_type

        if not traktor_controller.connect_with_gil_safety(output_only=True):
            raise Exception("Failed to connect to Traktor")

        await music_scanner.scan_library()
        self.active = True
        logger.info("✅ Session started with Claude SDK")

    def stop_session(self):
        """Stop session"""
        self.active = False
        if traktor_controller:
            traktor_controller.disconnect()


# ==========================================
# MAIN UNIFIED INTERFACE
# ==========================================

async def main():
    """Main execution"""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("🎛️ Autonomous DJ Agent - Hybrid Edition")
    print("=" * 60)

    # Detect available backend
    backends = detect_available_backend()

    print(f"\n🔍 Backend Detection:")
    print(f"  Claude SDK: {'✅' if backends['claude_sdk'] else '❌'}")
    print(f"  OpenRouter: {'✅' if backends['openrouter'] else '❌'}")
    print(f"\n  Selected: {backends['selected'].upper()}")
    print()

    # Load config
    config = get_config()

    # Create appropriate agent
    if backends['selected'] == 'claude_sdk':
        print("🚀 Using Claude Agent SDK (Anthropic)")
        agent = ClaudeSDKDJAgent(config)
    else:
        print("🚀 Using OpenRouter (FREE models)")
        agent = OpenRouterDJAgent(config)

    # Start session
    venue = input("Venue type (club/bar/festival) [club]: ").strip() or "club"
    event = input("Event type (warm_up/prime_time/closing) [prime_time]: ").strip() or "prime_time"

    try:
        await agent.start_session(venue, event)
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        return

    print("\n🎤 DJ Agent ready! Commands:")
    print("  - Natural DJ commands")
    print("  - 'status' - Show status")
    print("  - 'quit' - Exit\n")

    try:
        while True:
            user_input = input("DJ Command> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                break

            if user_input.lower() == 'status':
                status = traktor_controller.get_comprehensive_status()
                print(f"\n🎛️ Status: Deck A: {status['traktor_status']['deck_a_bpm']:.1f} BPM")
                print(f"           Deck B: {status['traktor_status']['deck_b_bpm']:.1f} BPM\n")
                continue

            # Execute command
            response = await agent.execute_command(user_input)
            print(f"\n🤖 {response}\n")

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted")

    finally:
        agent.stop_session()
        print("👋 Session ended")


if __name__ == "__main__":
    asyncio.run(main())
