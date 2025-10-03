#!/usr/bin/env python3
"""
🎛️ Autonomous DJ Master - Hybrid Control System
Sistema DJ ibrido con 3 modalità operative:
- MANUAL: Controllo completamente manuale (default)
- AUTONOMOUS: AI decide e agisce autonomamente
- ASSISTED: AI suggerisce, umano approva

Combina Claude Agent SDK per AI + Pattern matching per controlli manuali
"""

import asyncio
import time
import logging
import os
import sys
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Claude Agent SDK imports
try:
    from claude_agent_sdk import query, ClaudeAgentOptions, tool as sdk_tool
    CLAUDE_SDK_AVAILABLE = True
except ImportError:
    CLAUDE_SDK_AVAILABLE = False
    print("⚠️ Claude Agent SDK not available. AI modes disabled.")
    # Create dummy placeholders
    sdk_tool = None
    query = None
    ClaudeAgentOptions = None

# Create universal tool decorator (works with or without SDK)
def tool(*args, **kwargs):
    """Universal tool decorator - works even without Claude SDK"""
    def decorator(func):
        if CLAUDE_SDK_AVAILABLE and sdk_tool:
            # Use real SDK decorator
            return sdk_tool(*args, **kwargs)(func)
        else:
            # Just return function as-is
            return func
    return decorator

# DJ System components
from config import get_config, DJConfig
from traktor_control import TraktorController, DeckID, get_traktor_controller
from music_library import MusicLibraryScanner, TrackInfo, get_music_scanner
from core.openrouter_client import DJContext

# Import manual controller for pattern matching
from simple_dj_controller import SimpleDJController, CommandType

logger = logging.getLogger(__name__)


class OperationMode(Enum):
    """Modalità operative del sistema"""
    MANUAL = "manual"          # Solo comandi manuali
    AUTONOMOUS = "autonomous"  # AI completamente autonoma
    ASSISTED = "assisted"      # AI suggerisce, umano approva


@dataclass
class AIDecision:
    """Decisione presa dall'AI"""
    action: str
    confidence: float
    reasoning: str
    parameters: Dict[str, Any]
    requires_approval: bool = False


@dataclass
class SessionState:
    """Stato della sessione DJ"""
    mode: OperationMode = OperationMode.MANUAL
    ai_monitoring: bool = False
    monitoring_interval: int = 5  # secondi
    auto_approve_threshold: float = 0.85  # Confidence per auto-approve

    # Session context
    venue_type: str = "club"
    event_type: str = "party"
    energy_level: float = 0.5
    crowd_response: str = "neutral"

    # Track state
    current_deck_a: Optional[str] = None
    current_deck_b: Optional[str] = None
    deck_a_position: float = 0.0
    deck_b_position: float = 0.0

    # Performance metrics
    total_decisions: int = 0
    approved_decisions: int = 0
    rejected_decisions: int = 0


# ==========================================
# CLAUDE SDK TOOLS (Extended)
# ==========================================

# Global references
traktor_controller: Optional[TraktorController] = None
music_scanner: Optional[MusicLibraryScanner] = None
session_state: Optional[SessionState] = None


@tool(
    name="load_track_to_deck",
    description="Load the currently selected track from Traktor browser into a specific deck (A or B)",
    input_schema={"deck": str}
)
async def load_track_to_deck(args: Dict[str, Any]) -> Dict[str, Any]:
    """Load track to specified deck"""
    try:
        global traktor_controller
        deck = args.get("deck", "A")
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.load_track_to_deck(deck_id)

        message = f"✅ Track loaded to Deck {deck}" if success else f"❌ Failed to load track to Deck {deck}"
        return {"content": [{"type": "text", "text": message}]}
    except Exception as e:
        logger.error(f"Error loading track: {e}")
        return {"content": [{"type": "text", "text": f"❌ Error: {str(e)}"}]}


@tool(
    name="play_deck",
    description="Start playing a deck. Deck must have a track loaded first."
)
async def play_deck(deck: str) -> str:
    """Start playing specified deck"""
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.force_play_deck(deck_id)
        if success:
            return f"▶️ Deck {deck} playing"
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
    """Stop playing specified deck"""
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.stop_deck(deck_id)
        if success:
            return f"⏸️ Deck {deck} stopped"
        else:
            return f"❌ Failed to stop Deck {deck}"
    except Exception as e:
        logger.error(f"Error stopping deck: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="set_crossfader",
    description="Set crossfader position. 0.0=full Deck A, 0.5=center, 1.0=full Deck B"
)
async def set_crossfader(position: float) -> str:
    """Set crossfader position"""
    try:
        global traktor_controller
        success = traktor_controller.set_crossfader(position)
        if success:
            return f"🎚️ Crossfader: {position:.0%}"
        else:
            return f"❌ Failed to set crossfader"
    except Exception as e:
        logger.error(f"Error setting crossfader: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="set_deck_volume",
    description="Set volume for a specific deck (0.0 to 1.0)"
)
async def set_deck_volume(deck: str, volume: float) -> str:
    """Set deck volume"""
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.set_deck_volume(deck_id, volume)
        if success:
            return f"🔊 Deck {deck} volume: {volume:.0%}"
        else:
            return f"❌ Failed to set volume for Deck {deck}"
    except Exception as e:
        logger.error(f"Error setting volume: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="set_eq",
    description="Set EQ band level for a deck. Band: high/mid/low, Level: 0.0 to 1.0"
)
async def set_eq(deck: str, band: str, level: float) -> str:
    """Set EQ band level"""
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.set_eq(deck_id, band, level)
        if success:
            return f"🎚️ Deck {deck} EQ {band}: {level:.0%}"
        else:
            return f"❌ Failed to set EQ for Deck {deck}"
    except Exception as e:
        logger.error(f"Error setting EQ: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="set_fx",
    description="Set FX unit dry/wet mix. Unit: 1-4, Mix: 0.0 to 1.0"
)
async def set_fx(unit: int, mix: float) -> str:
    """Set FX dry/wet mix"""
    try:
        global traktor_controller
        success = traktor_controller.set_fx(unit, mix)
        if success:
            return f"✨ FX{unit} mix: {mix:.0%}"
        else:
            return f"❌ Failed to set FX{unit}"
    except Exception as e:
        logger.error(f"Error setting FX: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="sync_deck",
    description="Sync deck BPM and phase to master clock"
)
async def sync_deck(deck: str) -> str:
    """Sync deck to master"""
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.sync_deck(deck_id)
        if success:
            return f"🔄 Deck {deck} synced"
        else:
            return f"❌ Failed to sync Deck {deck}"
    except Exception as e:
        logger.error(f"Error syncing deck: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="search_music_library",
    description="Search for tracks in music library by keywords (artist, title, genre, BPM)"
)
async def search_music_library(query: str, limit: int = 10) -> str:
    """Search music library"""
    try:
        global music_scanner
        results = await music_scanner.search_tracks(query, limit=limit)

        if not results:
            return f"❌ No tracks found for '{query}'"

        output = f"🔍 Found {len(results)} tracks:\n"
        for i, track in enumerate(results, 1):
            output += f"{i}. {track.artist} - {track.title} ({track.bpm} BPM, {track.genre})\n"

        return output
    except Exception as e:
        logger.error(f"Error searching library: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="get_session_state",
    description="Get current session state (mode, energy, venue, crowd response)"
)
async def get_session_state() -> str:
    """Get session state"""
    try:
        global session_state
        return f"""📊 Session State:
Mode: {session_state.mode.value.upper()}
Venue: {session_state.venue_type}
Event: {session_state.event_type}
Energy: {session_state.energy_level:.0%}
Crowd: {session_state.crowd_response}
Decisions: {session_state.total_decisions} ({session_state.approved_decisions} approved)
Deck A: {session_state.current_deck_a or 'Empty'}
Deck B: {session_state.current_deck_b or 'Empty'}"""
    except Exception as e:
        logger.error(f"Error getting session state: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="emergency_stop",
    description="EMERGENCY: Stop all decks immediately"
)
async def emergency_stop() -> str:
    """Emergency stop all decks"""
    try:
        global traktor_controller
        traktor_controller.emergency_stop()
        return "🚨 EMERGENCY STOP - All decks stopped"
    except Exception as e:
        logger.error(f"Error in emergency stop: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="set_pitch",
    description="Adjust pitch/tempo for a deck. Amount: -1.0 to 1.0 (percentage)"
)
async def set_pitch(deck: str, amount: float) -> str:
    """Set pitch adjustment"""
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B

        # Convert to MIDI value (0-127, 64 = center/no change)
        midi_value = int(64 + (amount * 63))
        midi_value = max(0, min(127, midi_value))

        # Get MIDI mapping
        channel, cc = traktor_controller.MIDI_MAP.get(f'deck_{deck.lower()}_pitch', (1, 45))
        success = traktor_controller._send_midi_command(channel, cc, midi_value, f"Pitch {deck}")

        if success:
            sign = "+" if amount >= 0 else ""
            return f"🎵 Deck {deck} pitch: {sign}{amount*100:.1f}%"
        else:
            return f"❌ Failed to set pitch for Deck {deck}"
    except Exception as e:
        logger.error(f"Error setting pitch: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="trigger_cue",
    description="Trigger cue point on a deck. Point: 1-4"
)
async def trigger_cue(deck: str, point: int) -> str:
    """Trigger cue point"""
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B

        # Get MIDI mapping for cue point
        channel, cc = traktor_controller.MIDI_MAP.get(f'deck_{deck.lower()}_cue', (1, 24))
        success = traktor_controller._send_midi_command(channel, cc, 127, f"Cue {point} Deck {deck}")

        if success:
            return f"📍 Deck {deck} cue point {point} triggered"
        else:
            return f"❌ Failed to trigger cue on Deck {deck}"
    except Exception as e:
        logger.error(f"Error triggering cue: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="set_master_volume",
    description="Set master output volume. Level: 0.0 to 1.0"
)
async def set_master_volume(level: float) -> str:
    """Set master volume"""
    try:
        global traktor_controller

        # Get MIDI mapping
        channel, cc = traktor_controller.MIDI_MAP.get('master_volume', (1, 33))
        midi_value = int(level * 127)
        success = traktor_controller._send_midi_command(channel, cc, midi_value, "Master Volume")

        if success:
            return f"🔊 Master volume: {level:.0%}"
        else:
            return f"❌ Failed to set master volume"
    except Exception as e:
        logger.error(f"Error setting master volume: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="kill_eq_band",
    description="Kill (zero out) specific EQ band. Deck: A/B, Band: high/mid/low"
)
async def kill_eq_band(deck: str, band: str) -> str:
    """Kill EQ band"""
    try:
        global traktor_controller
        deck_id = DeckID.A if deck.upper() == "A" else DeckID.B
        success = traktor_controller.set_eq(deck_id, band, 0.0)

        if success:
            return f"💀 Deck {deck} {band.upper()} KILLED"
        else:
            return f"❌ Failed to kill {band} on Deck {deck}"
    except Exception as e:
        logger.error(f"Error killing EQ: {e}")
        return f"❌ Error: {str(e)}"


@tool(
    name="beatmatch_decks",
    description="Automatic beatmatching between two decks (sync, volume match, EQ reset)"
)
async def beatmatch_decks(deck1: str, deck2: str) -> str:
    """Beatmatch two decks"""
    try:
        global traktor_controller

        result = f"🎯 Beatmatching Deck {deck1} ↔ Deck {deck2}\n"

        # Sync deck2 to deck1
        deck2_id = DeckID.A if deck2 == "A" else DeckID.B
        traktor_controller.sync_deck(deck2_id)
        await asyncio.sleep(0.5)
        result += f"✓ Deck {deck2} synced\n"

        # Match volumes
        for deck_name in [deck1, deck2]:
            deck_id = DeckID.A if deck_name == "A" else DeckID.B
            traktor_controller.set_deck_volume(deck_id, 0.75)
        result += f"✓ Volumes matched at 75%\n"

        # EQ reset
        for deck_name in [deck1, deck2]:
            deck_id = DeckID.A if deck_name == "A" else DeckID.B
            for band in ["high", "mid", "low"]:
                traktor_controller.set_eq(deck_id, band, 0.5)
        result += f"✓ EQs reset to neutral\n"

        result += "✅ Beatmatch complete!"
        return result

    except Exception as e:
        logger.error(f"Error beatmatching: {e}")
        return f"❌ Error: {str(e)}"


# ==========================================
# HYBRID DJ MASTER CONTROLLER
# ==========================================

class AutonomousDJMaster:
    """Master DJ controller with hybrid manual/AI control"""

    def __init__(self, config: DJConfig):
        """Initialize hybrid controller"""
        global traktor_controller, music_scanner, session_state

        self.config = config
        self.session = SessionState()
        session_state = self.session

        # Initialize components
        self.traktor = get_traktor_controller(config)
        traktor_controller = self.traktor

        self.music_scanner = get_music_scanner(config)
        music_scanner = self.music_scanner

        # Manual controller for pattern matching
        self.manual_controller = SimpleDJController(config)

        # AI monitoring task
        self.monitoring_task: Optional[asyncio.Task] = None

        # Anthropic API key check
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.ai_available = CLAUDE_SDK_AVAILABLE and bool(self.anthropic_key)

        if not self.ai_available:
            logger.warning("⚠️ AI modes disabled (missing ANTHROPIC_API_KEY or SDK)")
            print("\n⚠️  AI MODES DISABLED")
            print("To enable AI: export ANTHROPIC_API_KEY=your-key")
            print("Only MANUAL mode available\n")

        logger.info(f"🎛️ Autonomous DJ Master initialized (AI: {self.ai_available})")


    async def start(self):
        """Start the hybrid system"""
        logger.info("🎵 Starting Autonomous DJ Master...")

        # Connect to Traktor
        if not self.traktor.connect_with_gil_safety(output_only=True):
            raise Exception("Failed to connect to Traktor")

        # Scan music library
        await self.music_scanner.scan_library()

        # Start manual controller
        await self.manual_controller.start()

        logger.info("✅ Autonomous DJ Master ready!")
        self.print_welcome()


    def print_welcome(self):
        """Print welcome message with mode info"""
        print("\n" + "="*60)
        print("🎛️  AUTONOMOUS DJ MASTER - Hybrid Control System")
        print("="*60)
        print(f"\nCurrent Mode: {self.session.mode.value.upper()}")
        print(f"AI Available: {'✅ YES' if self.ai_available else '❌ NO (install ANTHROPIC_API_KEY)'}")
        print("\n📋 MODE COMMANDS:")
        print("  /manual     - Switch to MANUAL mode (default)")
        print("  /auto       - Switch to AUTONOMOUS mode (AI decides)")
        print("  /assist     - Switch to ASSISTED mode (AI suggests)")
        print("  /status     - Show current session state")
        print("  /help       - Show all available commands")
        print("  /quit       - Exit system")
        print("\n💡 In MANUAL mode, use natural language commands:")
        print("  'play deck A', 'mix to B', 'search techno', etc.")
        print("\n" + "="*60 + "\n")


    async def process_command(self, command: str) -> str:
        """Process command based on current mode"""
        cmd = command.strip().lower()

        # System commands (available in all modes)
        if cmd.startswith('/'):
            return await self._process_system_command(cmd)

        # Route to appropriate handler based on mode
        if self.session.mode == OperationMode.MANUAL:
            return await self._process_manual_command(command)

        elif self.session.mode == OperationMode.AUTONOMOUS:
            # In autonomous mode, user commands are treated as context updates
            return await self._process_autonomous_context(command)

        elif self.session.mode == OperationMode.ASSISTED:
            return await self._process_assisted_command(command)

        return "❌ Unknown mode"


    async def _process_system_command(self, cmd: str) -> str:
        """Process system commands (/manual, /auto, etc.)"""

        if cmd == '/manual':
            return await self._switch_mode(OperationMode.MANUAL)

        elif cmd == '/auto' or cmd == '/autonomous':
            if not self.ai_available:
                return "❌ AI not available (missing ANTHROPIC_API_KEY)"
            return await self._switch_mode(OperationMode.AUTONOMOUS)

        elif cmd == '/assist' or cmd == '/assisted':
            if not self.ai_available:
                return "❌ AI not available (missing ANTHROPIC_API_KEY)"
            return await self._switch_mode(OperationMode.ASSISTED)

        elif cmd == '/status':
            return await self._get_status()

        elif cmd == '/help':
            return self.manual_controller.get_help()

        elif cmd == '/quit' or cmd == '/exit':
            return "QUIT"

        else:
            return f"❌ Unknown system command: {cmd}"


    async def _switch_mode(self, new_mode: OperationMode) -> str:
        """Switch operation mode"""
        old_mode = self.session.mode
        self.session.mode = new_mode

        # Stop AI monitoring if switching from autonomous
        if old_mode == OperationMode.AUTONOMOUS and self.monitoring_task:
            self.monitoring_task.cancel()
            self.monitoring_task = None
            self.session.ai_monitoring = False

        # Start AI monitoring if switching to autonomous
        if new_mode == OperationMode.AUTONOMOUS:
            self.session.ai_monitoring = True
            self.monitoring_task = asyncio.create_task(self._autonomous_monitoring_loop())

        result = f"✅ Mode switched: {old_mode.value.upper()} → {new_mode.value.upper()}"

        if new_mode == OperationMode.AUTONOMOUS:
            result += "\n🤖 AI monitoring started (watching session every 5s)"
        elif new_mode == OperationMode.ASSISTED:
            result += "\n💡 AI will suggest actions, you approve/reject"
        elif new_mode == OperationMode.MANUAL:
            result += "\n👤 Manual control active"

        return result


    async def _process_manual_command(self, command: str) -> str:
        """Process manual command using pattern matching"""
        try:
            result = await self.manual_controller.process_command(command)
            return result
        except Exception as e:
            logger.error(f"Error in manual command: {e}")
            return f"❌ Error: {str(e)}"


    async def _process_autonomous_context(self, context: str) -> str:
        """Process user input as context update in autonomous mode"""
        # Update session context based on user feedback
        ctx = context.lower()

        if "energy" in ctx or "energia" in ctx:
            if "high" in ctx or "alta" in ctx:
                self.session.energy_level = 0.8
            elif "low" in ctx or "bassa" in ctx:
                self.session.energy_level = 0.3
            else:
                self.session.energy_level = 0.5
            return f"✅ Energy level updated: {self.session.energy_level:.0%}"

        elif "crowd" in ctx or "folla" in ctx:
            if "good" in ctx or "dancing" in ctx or "buona" in ctx:
                self.session.crowd_response = "positive"
            elif "bad" in ctx or "boring" in ctx or "negativa" in ctx:
                self.session.crowd_response = "negative"
            else:
                self.session.crowd_response = "neutral"
            return f"✅ Crowd response updated: {self.session.crowd_response}"

        else:
            return "ℹ️ In AUTONOMOUS mode, AI is controlling the session. Use /manual to take control."


    async def _process_assisted_command(self, command: str) -> str:
        """Process command in assisted mode (AI suggests, user approves)"""
        if not self.ai_available:
            return "❌ AI not available"

        try:
            # Ask AI for suggestion
            prompt = f"""You are a professional DJ assistant in ASSISTED mode.
The user said: "{command}"

Current session state:
- Venue: {self.session.venue_type}
- Event: {self.session.event_type}
- Energy: {self.session.energy_level:.0%}
- Crowd: {self.session.crowd_response}

Suggest ONE specific action to fulfill their request.
Use available tools if needed, but explain your reasoning."""

            # Query Claude Agent SDK
            result = await query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    api_key=self.anthropic_key,
                    max_tokens=500
                )
            )

            suggestion = result.get("content", "No suggestion")

            return f"💡 AI Suggestion:\n{suggestion}\n\n[Execute this? Type 'yes' to approve]"

        except Exception as e:
            logger.error(f"Error in assisted mode: {e}")
            return f"❌ AI Error: {str(e)}"


    async def _autonomous_monitoring_loop(self):
        """AI monitoring loop for autonomous mode"""
        logger.info("🤖 Starting autonomous AI monitoring...")

        while self.session.ai_monitoring:
            try:
                await asyncio.sleep(self.session.monitoring_interval)

                # AI analyzes current state and decides next action
                await self._ai_autonomous_decision()

            except asyncio.CancelledError:
                logger.info("🤖 AI monitoring stopped")
                break
            except Exception as e:
                logger.error(f"Error in AI monitoring: {e}")
                await asyncio.sleep(5)


    async def _ai_autonomous_decision(self):
        """AI makes autonomous decision based on current state"""
        if not self.ai_available:
            return

        try:
            # Build context for AI
            prompt = f"""You are an autonomous DJ AI controlling a live session.

Current State:
- Venue: {self.session.venue_type}
- Event: {self.session.event_type}
- Energy Level: {self.session.energy_level:.0%}
- Crowd Response: {self.session.crowd_response}
- Deck A: {self.session.current_deck_a or 'Empty'}
- Deck B: {self.session.current_deck_b or 'Empty'}
- Deck A Position: {self.session.deck_a_position:.1%}
- Deck B Position: {self.session.deck_b_position:.1%}

Analyze the situation and decide if you should take ANY action right now.
Use available tools (load_track, play_deck, set_crossfader, set_eq, etc.) if needed.

If no action needed, just say "Monitoring session, no action required."
"""

            # Query AI
            result = await query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    api_key=self.anthropic_key,
                    max_tokens=1000
                )
            )

            decision = result.get("content", "")

            # Log AI decision
            logger.info(f"🤖 AI Decision: {decision}")
            print(f"\n🤖 AI: {decision}\n")

            self.session.total_decisions += 1
            self.session.approved_decisions += 1  # Auto-approved in autonomous mode

        except Exception as e:
            logger.error(f"Error in AI decision: {e}")


    async def _get_status(self) -> str:
        """Get comprehensive system status"""
        status = f"""
📊 AUTONOMOUS DJ MASTER - System Status
{"="*60}

🎛️ Operation Mode: {self.session.mode.value.upper()}
🤖 AI Monitoring: {'✅ Active' if self.session.ai_monitoring else '❌ Inactive'}
⏱️  Monitoring Interval: {self.session.monitoring_interval}s

📍 Session Context:
  Venue: {self.session.venue_type}
  Event: {self.session.event_type}
  Energy Level: {self.session.energy_level:.0%}
  Crowd Response: {self.session.crowd_response}

🎵 Decks:
  Deck A: {self.session.current_deck_a or 'Empty'} ({self.session.deck_a_position:.1%})
  Deck B: {self.session.current_deck_b or 'Empty'} ({self.session.deck_b_position:.1%})

📈 Performance:
  Total Decisions: {self.session.total_decisions}
  Approved: {self.session.approved_decisions}
  Rejected: {self.session.rejected_decisions}

{"="*60}
"""
        return status


    def stop(self):
        """Stop the system"""
        if self.monitoring_task:
            self.monitoring_task.cancel()

        self.manual_controller.stop()
        self.traktor.disconnect()
        logger.info("👋 Autonomous DJ Master stopped")


# ==========================================
# MAIN CLI INTERFACE
# ==========================================

async def main():
    """Main entry point"""

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load config
    config = get_config()

    # Create controller
    controller = AutonomousDJMaster(config)

    try:
        # Start system
        await controller.start()

        # Main command loop
        while True:
            try:
                command = input("\nDJ Command> ").strip()

                if not command:
                    continue

                result = await controller.process_command(command)

                if result == "QUIT":
                    print("\n👋 Shutting down...")
                    break

                print(result)

            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user")
                break
            except EOFError:
                print("\n\n⚠️ EOF received")
                break

    finally:
        controller.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
