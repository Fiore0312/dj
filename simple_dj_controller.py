#!/usr/bin/env python3
"""
🎛️ Simple DJ Controller - Rule-based system (NO AI required)
Sistema di controllo DJ semplice basato su pattern matching diretto
"""

import re
import asyncio
import logging
from typing import Optional, Dict, List, Tuple
from enum import Enum

from config import DJConfig
from traktor_control import get_traktor_controller, DeckID
from music_library import get_music_scanner

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Tipi di comandi disponibili"""
    # Playback
    PLAY = "play"
    STOP = "stop"
    PAUSE = "pause"

    # Loading
    LOAD = "load"
    BROWSE = "browse"

    # Mixing
    MIX = "mix"
    CROSSFADE = "crossfade"
    SYNC = "sync"

    # Volume
    VOLUME = "volume"

    # EQ Controls
    EQ = "eq"
    KILL = "kill"

    # Effects
    FX = "fx"

    # Pitch/Tempo
    PITCH = "pitch"

    # Cue Points
    CUE = "cue"

    # Emergency & Master
    EMERGENCY = "emergency"
    MASTER = "master"

    # Library
    SEARCH = "search"

    # Macros
    BEATMATCH = "beatmatch"

    # Help
    HELP = "help"
    STATUS = "status"


class SimpleDJController:
    """Controller DJ semplice senza AI - basato su regole"""

    def __init__(self, config: DJConfig):
        """Initialize simple controller"""
        self.config = config
        self.traktor = get_traktor_controller(config)
        self.music_scanner = get_music_scanner(config)

        # State
        self.current_deck = "A"  # Default deck
        self.last_search_results = []
        self.selected_track_index = 0

        logger.info("🎛️ Simple DJ Controller initialized (Rule-based, NO AI)")

    async def start(self):
        """Start controller"""
        logger.info("🎵 Starting Simple DJ Controller...")

        # Connect to Traktor
        if not self.traktor.connect_with_gil_safety(output_only=True):
            raise Exception("Failed to connect to Traktor")

        # Scan music library
        await self.music_scanner.scan_library()

        logger.info("✅ Simple DJ Controller ready!")
        self.print_help()

    def stop(self):
        """Stop controller"""
        self.traktor.disconnect()
        logger.info("👋 Simple DJ Controller stopped")

    async def execute_command(self, command: str) -> str:
        """Execute user command"""
        command = command.strip().lower()

        if not command:
            return "⚠️ Empty command"

        try:
            # Parse command
            cmd_type, params = self._parse_command(command)

            if not cmd_type:
                return f"❌ Unknown command: '{command}'\nType 'help' for available commands"

            # Execute based on type
            if cmd_type == CommandType.HELP:
                return self._cmd_help()

            elif cmd_type == CommandType.STATUS:
                return await self._cmd_status()

            elif cmd_type == CommandType.PLAY:
                return await self._cmd_play(params)

            elif cmd_type == CommandType.STOP:
                return await self._cmd_stop(params)

            elif cmd_type == CommandType.PAUSE:
                return await self._cmd_pause(params)

            elif cmd_type == CommandType.LOAD:
                return await self._cmd_load(params)

            elif cmd_type == CommandType.BROWSE:
                return await self._cmd_browse(params)

            elif cmd_type == CommandType.MIX:
                return await self._cmd_mix(params)

            elif cmd_type == CommandType.CROSSFADE:
                return await self._cmd_crossfade(params)

            elif cmd_type == CommandType.SYNC:
                return await self._cmd_sync(params)

            elif cmd_type == CommandType.VOLUME:
                return await self._cmd_volume(params)

            elif cmd_type == CommandType.SEARCH:
                return await self._cmd_search(params)

            elif cmd_type == CommandType.EQ:
                return await self._cmd_eq(params)

            elif cmd_type == CommandType.KILL:
                return await self._cmd_kill(params)

            elif cmd_type == CommandType.FX:
                return await self._cmd_fx(params)

            elif cmd_type == CommandType.PITCH:
                return await self._cmd_pitch(params)

            elif cmd_type == CommandType.CUE:
                return await self._cmd_cue(params)

            elif cmd_type == CommandType.EMERGENCY:
                return await self._cmd_emergency(params)

            elif cmd_type == CommandType.MASTER:
                return await self._cmd_master(params)

            elif cmd_type == CommandType.BEATMATCH:
                return await self._cmd_beatmatch(params)

            else:
                return f"❌ Command not implemented: {cmd_type}"

        except Exception as e:
            logger.error(f"Error executing command: {e}", exc_info=True)
            return f"❌ Error: {str(e)}"

    def _parse_command(self, cmd: str) -> Tuple[Optional[CommandType], Dict]:
        """Parse command into type and parameters"""
        params = {}

        # HELP
        if cmd in ["help", "h", "?", "aiuto"]:
            return CommandType.HELP, {}

        # STATUS
        if cmd in ["status", "stato", "info"]:
            return CommandType.STATUS, {}

        # PLAY
        if re.match(r"(play|parti|avvia|start|go|fai partire|fa partire)", cmd):
            deck = self._extract_deck(cmd)
            return CommandType.PLAY, {"deck": deck}

        # STOP
        if re.match(r"(stop|ferma|halt)", cmd):
            deck = self._extract_deck(cmd)
            return CommandType.STOP, {"deck": deck}

        # PAUSE
        if re.match(r"(pause|pausa)", cmd):
            deck = self._extract_deck(cmd)
            return CommandType.PAUSE, {"deck": deck}

        # LOAD
        if re.match(r"(load|carica)", cmd):
            deck = self._extract_deck(cmd)
            return CommandType.LOAD, {"deck": deck}

        # BROWSE
        if re.match(r"(browse|naviga|scorri|next|prev)", cmd):
            direction = "down" if any(w in cmd for w in ["down", "next", "pross", "avanti", "giù"]) else "up"
            steps = self._extract_number(cmd, default=1)
            return CommandType.BROWSE, {"direction": direction, "steps": steps}

        # MIX (transition between decks)
        if re.match(r"(mix|mixa|transiz|passa|switch|cambia)", cmd):
            from_deck, to_deck = self._extract_deck_transition(cmd)
            duration = self._extract_number(cmd, default=30)
            return CommandType.MIX, {"from_deck": from_deck, "to_deck": to_deck, "duration": duration}

        # CROSSFADE
        if re.match(r"(crossfade|crossfader|xfade)", cmd):
            position = self._extract_crossfade_position(cmd)
            return CommandType.CROSSFADE, {"position": position}

        # SYNC
        if re.match(r"(sync|sincro)", cmd):
            deck = self._extract_deck(cmd)
            return CommandType.SYNC, {"deck": deck}

        # VOLUME
        if re.match(r"(volume|vol|alza|abbassa)", cmd):
            deck = self._extract_deck(cmd)
            level = self._extract_volume(cmd)
            return CommandType.VOLUME, {"deck": deck, "level": level}

        # SEARCH
        if re.match(r"(search|cerca|trova|find)", cmd):
            genre, bpm_min, bpm_max = self._extract_search_params(cmd)
            return CommandType.SEARCH, {"genre": genre, "bpm_min": bpm_min, "bpm_max": bpm_max}

        # EQ
        if re.match(r"(eq|equaliz)", cmd):
            deck = self._extract_deck(cmd)
            band, level = self._extract_eq_params(cmd)
            return CommandType.EQ, {"deck": deck, "band": band, "level": level}

        # KILL (EQ kill - immediate bass/mid/high to zero)
        if re.match(r"(kill)", cmd):
            deck = self._extract_deck(cmd)
            band = self._extract_eq_band(cmd)
            return CommandType.KILL, {"deck": deck, "band": band}

        # FX (Effects)
        if re.match(r"(fx|effect|effetto)", cmd):
            unit = self._extract_fx_unit(cmd)
            level = self._extract_fx_level(cmd)
            return CommandType.FX, {"unit": unit, "level": level}

        # PITCH
        if re.match(r"(pitch|tempo)", cmd):
            deck = self._extract_deck(cmd)
            amount = self._extract_pitch_amount(cmd)
            return CommandType.PITCH, {"deck": deck, "amount": amount}

        # CUE
        if re.match(r"(cue)", cmd):
            deck = self._extract_deck(cmd)
            return CommandType.CUE, {"deck": deck}

        # EMERGENCY
        if re.match(r"(emergency|panic|stop all)", cmd):
            return CommandType.EMERGENCY, {}

        # MASTER VOLUME
        if re.match(r"(master)", cmd):
            level = self._extract_volume(cmd)
            return CommandType.MASTER, {"level": level}

        # BEATMATCH (macro)
        if re.match(r"(beatmatch|beat match)", cmd):
            deck1, deck2 = self._extract_deck_transition(cmd)
            return CommandType.BEATMATCH, {"deck1": deck1, "deck2": deck2}

        return None, {}

    def _extract_deck(self, cmd: str) -> str:
        """Extract deck letter from command"""
        if re.search(r"\ba\b", cmd) or "deck a" in cmd:
            return "A"
        elif re.search(r"\bb\b", cmd) or "deck b" in cmd:
            return "B"
        else:
            return self.current_deck  # Use current deck

    def _extract_deck_transition(self, cmd: str) -> Tuple[str, str]:
        """Extract from_deck and to_deck for transitions"""
        # Look for patterns like "A to B", "da A a B", "from A to B"
        match = re.search(r"(?:da|from)?\s*([ab])\s*(?:a|to|->)\s*([ab])", cmd, re.IGNORECASE)
        if match:
            return match.group(1).upper(), match.group(2).upper()

        # Default: from current deck to the other
        if self.current_deck == "A":
            return "A", "B"
        else:
            return "B", "A"

    def _extract_number(self, cmd: str, default: int = 1) -> int:
        """Extract number from command"""
        match = re.search(r"\b(\d+)\b", cmd)
        return int(match.group(1)) if match else default

    def _extract_crossfade_position(self, cmd: str) -> float:
        """Extract crossfade position (0.0 = A, 1.0 = B)"""
        if "a" in cmd or "left" in cmd or "sinistra" in cmd:
            return 0.0
        elif "b" in cmd or "right" in cmd or "destra" in cmd:
            return 1.0
        elif "center" in cmd or "centro" in cmd or "middle" in cmd:
            return 0.5
        else:
            # Try to extract percentage
            match = re.search(r"(\d+)\s*%", cmd)
            if match:
                return int(match.group(1)) / 100.0
            return 0.5

    def _extract_volume(self, cmd: str) -> float:
        """Extract volume level"""
        # Look for percentage
        match = re.search(r"(\d+)\s*%", cmd)
        if match:
            return int(match.group(1)) / 100.0

        # Look for keywords
        if "max" in cmd or "alto" in cmd or "full" in cmd:
            return 1.0
        elif "min" in cmd or "basso" in cmd or "zero" in cmd:
            return 0.0
        elif "medio" in cmd or "metà" in cmd or "half" in cmd:
            return 0.5

        return 0.75  # Default

    def _extract_search_params(self, cmd: str) -> Tuple[Optional[str], Optional[float], Optional[float]]:
        """Extract search parameters (genre, bpm_min, bpm_max)"""
        genre = None
        bpm_min = None
        bpm_max = None

        # Genre keywords
        genres = ["house", "techno", "trance", "dubstep", "drum and bass", "dnb",
                  "electro", "disco", "funk", "hip hop", "rap"]
        for g in genres:
            if g in cmd:
                genre = g
                break

        # BPM range
        # Pattern: "120-130", "tra 120 e 130", "from 120 to 130"
        match = re.search(r"(\d+)\s*[-–a]\s*(\d+)", cmd)
        if match:
            bpm_min = float(match.group(1))
            bpm_max = float(match.group(2))
        else:
            # Single BPM
            match = re.search(r"(\d+)\s*bpm", cmd)
            if match:
                bpm = float(match.group(1))
                bpm_min = bpm - 5
                bpm_max = bpm + 5

        return genre, bpm_min, bpm_max

    def _extract_eq_params(self, cmd: str) -> Tuple[str, float]:
        """Extract EQ band and level"""
        # Detect band
        band = "mid"  # Default
        if "high" in cmd or "treble" in cmd or "acuti" in cmd:
            band = "high"
        elif "mid" in cmd or "medi" in cmd:
            band = "mid"
        elif "low" in cmd or "bass" in cmd or "bassi" in cmd:
            band = "low"

        # Detect level
        level = self._extract_volume(cmd)
        return band, level

    def _extract_eq_band(self, cmd: str) -> str:
        """Extract EQ band for kill command"""
        if "high" in cmd or "treble" in cmd or "acuti" in cmd:
            return "high"
        elif "mid" in cmd or "medi" in cmd:
            return "mid"
        elif "low" in cmd or "bass" in cmd or "bassi" in cmd:
            return "low"
        return "low"  # Default kill bass

    def _extract_fx_unit(self, cmd: str) -> int:
        """Extract FX unit number (1-4)"""
        match = re.search(r"(fx|effect)\s*([1-4])", cmd)
        if match:
            return int(match.group(2))
        return 1  # Default FX1

    def _extract_fx_level(self, cmd: str) -> Optional[float]:
        """Extract FX dry/wet level"""
        if "off" in cmd or "zero" in cmd:
            return 0.0
        elif "on" in cmd or "full" in cmd:
            return 1.0
        else:
            # Try to extract percentage
            match = re.search(r"(\d+)\s*%", cmd)
            if match:
                return int(match.group(1)) / 100.0
        return 0.5  # Default 50%

    def _extract_pitch_amount(self, cmd: str) -> float:
        """Extract pitch adjustment amount"""
        # Look for +/- percentage
        match = re.search(r"([+-]?\d+\.?\d*)\s*%?", cmd)
        if match:
            return float(match.group(1)) / 100.0  # Convert to decimal
        return 0.0

    # Command implementations

    def _cmd_help(self) -> str:
        """Show help"""
        return """🎛️ SIMPLE DJ CONTROLLER - Comandi Disponibili

📀 PLAYBACK:
  play [a|b]           - Avvia deck (es: "play a", "play")
  stop [a|b]           - Ferma deck
  pause [a|b]          - Pausa deck
  cue [a|b]            - Jump to cue point

📂 CARICAMENTO:
  load [a|b]           - Carica traccia selezionata nel deck
  browse up/down [N]   - Naviga browser (es: "browse down 5")

🎚️ MIXING:
  mix [a to b] [30s]   - Mix automatico tra deck (es: "mix a to b 20")
  crossfade [a|b|50%]  - Sposta crossfader (es: "crossfade b", "crossfade 50%")
  sync [a|b]           - Sincronizza BPM deck
  beatmatch a b        - Beatmatch automatico completo

🔊 VOLUME:
  volume [a|b] [50%]   - Imposta volume (es: "volume a 75%")
  master [50%]         - Volume master (es: "master 80%")

🎛️ EQ CONTROLS:
  eq [a|b] high/mid/low [50%]  - Regola EQ (es: "eq a high 75%")
  kill [a|b] bass/mid/high     - Kill EQ band (es: "kill a bass")

✨ EFFECTS:
  fx [1-4] [50%]       - Controllo FX (es: "fx 1 75%", "fx 2 off")

🎵 PITCH/TEMPO:
  pitch [a|b] [±%]     - Regola pitch (es: "pitch a +2", "pitch b -1.5")

🚨 EMERGENCY:
  emergency stop       - Stop immediato tutti i deck
  panic                - Alias per emergency stop

🔍 RICERCA:
  search house 120-130      - Cerca per genere e BPM
  search techno             - Cerca per genere
  cerca 128 bpm             - Cerca per BPM

ℹ️ INFO:
  status               - Mostra stato corrente
  help                 - Mostra questo aiuto

💡 ESEMPI BASE:
  play a               → Avvia deck A
  load b               → Carica traccia in deck B
  mix a to b 30        → Transizione da A a B in 30 secondi
  search house 120-130 → Cerca house tra 120-130 BPM
  browse down 5        → Scorri 5 tracce in giù

💡 ESEMPI AVANZATI:
  eq a bass 0          → Taglia i bassi su deck A
  kill b high          → Kill acuti su deck B
  fx 1 50%             → Attiva FX1 al 50%
  pitch a +2           → Aumenta pitch deck A di +2%
  beatmatch a b        → Sincronizza automaticamente A e B
  emergency stop       → Stop di emergenza
"""

    async def _cmd_status(self) -> str:
        """Show current status"""
        status = self.traktor.get_status()
        return f"""📊 STATO CORRENTE:
🎚️ Deck attivo: {self.current_deck}
📀 Deck A: {"▶️ Playing" if status.get('deck_a_playing') else "⏸️ Stopped"}
📀 Deck B: {"▶️ Playing" if status.get('deck_b_playing') else "⏸️ Stopped"}
🎛️ Crossfader: {status.get('crossfader_position', 0.5):.0%}
🔊 Volume A: {status.get('volume_a', 0.75):.0%}
🔊 Volume B: {status.get('volume_b', 0.75):.0%}
🎵 Tracce in libreria: {len(self.last_search_results) if self.last_search_results else "N/A"}
"""

    async def _cmd_play(self, params: Dict) -> str:
        """Play deck"""
        deck = params.get("deck", "A")
        deck_id = DeckID.A if deck == "A" else DeckID.B

        success = self.traktor.force_play_deck(deck_id)
        self.current_deck = deck

        if success:
            return f"▶️ Deck {deck} playing"
        else:
            return f"❌ Failed to play Deck {deck}"

    async def _cmd_stop(self, params: Dict) -> str:
        """Stop deck"""
        deck = params.get("deck", "A")
        deck_id = DeckID.A if deck == "A" else DeckID.B

        success = self.traktor.pause_deck(deck_id)

        if success:
            return f"⏹️ Deck {deck} stopped"
        else:
            return f"❌ Failed to stop Deck {deck}"

    async def _cmd_pause(self, params: Dict) -> str:
        """Pause deck"""
        return await self._cmd_stop(params)  # Same as stop

    async def _cmd_load(self, params: Dict) -> str:
        """Load track to deck"""
        deck = params.get("deck", "A")
        deck_id = DeckID.A if deck == "A" else DeckID.B

        success = self.traktor.load_track_to_deck(deck_id)

        if success:
            self.current_deck = deck
            return f"📀 Track loaded to Deck {deck}"
        else:
            return f"❌ Failed to load track to Deck {deck}"

    async def _cmd_browse(self, params: Dict) -> str:
        """Browse tracks"""
        direction = params.get("direction", "down")
        steps = params.get("steps", 1)

        success = self.traktor.browse_tracks(direction, steps)

        if success:
            self.selected_track_index += steps if direction == "down" else -steps
            return f"📂 Browsed {steps} track(s) {direction}"
        else:
            return f"❌ Failed to browse tracks"

    async def _cmd_mix(self, params: Dict) -> str:
        """Perform automatic mix transition"""
        from_deck = params.get("from_deck", "A")
        to_deck = params.get("to_deck", "B")
        duration = params.get("duration", 30)

        from_deck_id = DeckID.A if from_deck == "A" else DeckID.B
        to_deck_id = DeckID.A if to_deck == "A" else DeckID.B

        result = f"🎚️ Starting mix: Deck {from_deck} → Deck {to_deck} ({duration}s)\n"

        # Sync target deck
        self.traktor.sync_deck(to_deck_id)
        await asyncio.sleep(0.5)
        result += f"✓ Deck {to_deck} synced\n"

        # Start target deck
        self.traktor.force_play_deck(to_deck_id)
        await asyncio.sleep(1)
        result += f"✓ Deck {to_deck} playing\n"

        # Gradual crossfade
        steps = 10
        step_duration = duration / steps

        for i in range(steps + 1):
            progress = i / steps
            if from_deck == "A":
                crossfader_pos = progress
            else:
                crossfader_pos = 1.0 - progress

            self.traktor.set_crossfader(crossfader_pos)

            if i < steps:
                await asyncio.sleep(step_duration)

        result += f"✓ Crossfade completed\n"

        # Stop source deck
        self.traktor.pause_deck(from_deck_id)
        result += f"✓ Deck {from_deck} stopped\n"

        self.current_deck = to_deck
        result += "✅ Mix completed!"

        return result

    async def _cmd_crossfade(self, params: Dict) -> str:
        """Set crossfader position"""
        position = params.get("position", 0.5)

        success = self.traktor.set_crossfader(position)

        if success:
            return f"🎚️ Crossfader set to {position:.0%}"
        else:
            return f"❌ Failed to set crossfader"

    async def _cmd_sync(self, params: Dict) -> str:
        """Sync deck BPM"""
        deck = params.get("deck", "A")
        deck_id = DeckID.A if deck == "A" else DeckID.B

        success = self.traktor.sync_deck(deck_id)

        if success:
            return f"🔄 Deck {deck} synced"
        else:
            return f"❌ Failed to sync Deck {deck}"

    async def _cmd_volume(self, params: Dict) -> str:
        """Set deck volume"""
        deck = params.get("deck", "A")
        level = params.get("level", 0.75)
        deck_id = DeckID.A if deck == "A" else DeckID.B

        success = self.traktor.set_deck_volume(deck_id, level)

        if success:
            return f"🔊 Deck {deck} volume set to {level:.0%}"
        else:
            return f"❌ Failed to set volume for Deck {deck}"

    async def _cmd_search(self, params: Dict) -> str:
        """Search music library"""
        genre = params.get("genre")
        bpm_min = params.get("bpm_min")
        bpm_max = params.get("bpm_max")

        # Build search criteria
        criteria = []
        if genre:
            criteria.append(f"genre: {genre}")
        if bpm_min and bpm_max:
            criteria.append(f"BPM: {bpm_min}-{bpm_max}")

        # Search
        tracks = await self.music_scanner.search_tracks(
            genre=genre,
            bpm_range=(bpm_min, bpm_max) if bpm_min and bpm_max else None
        )

        self.last_search_results = tracks
        self.selected_track_index = 0

        if not tracks:
            return f"📭 No tracks found for: {', '.join(criteria)}"

        # Format results
        result = f"🎵 Found {len(tracks)} track(s) for: {', '.join(criteria)}\n\n"

        for i, track in enumerate(tracks[:10], 1):
            bpm_str = f"{track.bpm:.0f} BPM" if track.bpm else "? BPM"
            result += f"{i}. '{track.title}' - {track.artist} ({track.genre}, {bpm_str})\n"

        if len(tracks) > 10:
            result += f"... and {len(tracks) - 10} more\n"

        result += f"\n💡 Use 'load a' to load selected track to Deck A"

        return result

    async def _cmd_eq(self, params: Dict) -> str:
        """Set EQ band level"""
        deck = params.get("deck", "A")
        band = params.get("band", "mid")
        level = params.get("level", 0.5)

        deck_id = DeckID.A if deck == "A" else DeckID.B
        success = self.traktor.set_eq(deck_id, band, level)

        if success:
            return f"🎚️ Deck {deck} EQ {band.upper()} set to {level:.0%}"
        else:
            return f"❌ Failed to set EQ for Deck {deck}"

    async def _cmd_kill(self, params: Dict) -> str:
        """Kill (zero) specific EQ band"""
        deck = params.get("deck", "A")
        band = params.get("band", "low")

        deck_id = DeckID.A if deck == "A" else DeckID.B
        success = self.traktor.set_eq(deck_id, band, 0.0)

        if success:
            return f"💀 Deck {deck} {band.upper()} KILLED (0%)"
        else:
            return f"❌ Failed to kill {band} on Deck {deck}"

    async def _cmd_fx(self, params: Dict) -> str:
        """Control FX unit"""
        unit = params.get("unit", 1)
        level = params.get("level", 0.5)

        if level is None:
            level = 0.5

        success = self.traktor.set_fx_drywet(unit, level)

        if success:
            status = "OFF" if level == 0.0 else f"{level:.0%}"
            return f"✨ FX{unit} set to {status}"
        else:
            return f"❌ Failed to set FX{unit}"

    async def _cmd_pitch(self, params: Dict) -> str:
        """Adjust pitch/tempo"""
        deck = params.get("deck", "A")
        amount = params.get("amount", 0.0)

        deck_id = DeckID.A if deck == "A" else DeckID.B

        # Convert to MIDI value (0-127, 64 = center/no change)
        # Amount is -1.0 to +1.0, map to 0-127
        midi_value = int(64 + (amount * 63))
        midi_value = max(0, min(127, midi_value))

        # Get the MIDI mapping for pitch
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_pitch', (1, 45))
        success = self.traktor._send_midi_command(channel, cc, midi_value, f"Pitch {deck}")

        if success:
            sign = "+" if amount >= 0 else ""
            return f"🎵 Deck {deck} pitch: {sign}{amount*100:.1f}%"
        else:
            return f"❌ Failed to set pitch for Deck {deck}"

    async def _cmd_cue(self, params: Dict) -> str:
        """Jump to/set cue point"""
        deck = params.get("deck", "A")
        deck_id = DeckID.A if deck == "A" else DeckID.B

        # Get MIDI mapping for cue
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_cue', (1, 24))
        success = self.traktor._send_midi_command(channel, cc, 127, f"Cue {deck}")

        if success:
            return f"📍 Deck {deck} CUE activated"
        else:
            return f"❌ Failed to activate CUE on Deck {deck}"

    async def _cmd_emergency(self, params: Dict) -> str:
        """Emergency stop all decks"""
        result = "🚨 EMERGENCY STOP - Stopping all decks\n"

        # Stop all decks
        for deck_name in ["A", "B"]:
            deck_id = DeckID.A if deck_name == "A" else DeckID.B
            self.traktor.pause_deck(deck_id)

        # Crossfader to center
        self.traktor.set_crossfader(0.5)

        # Reset volumes
        for deck_name in ["A", "B"]:
            deck_id = DeckID.A if deck_name == "A" else DeckID.B
            self.traktor.set_deck_volume(deck_id, 0.75)

        result += "✅ All decks stopped\n"
        result += "✅ Crossfader centered\n"
        result += "✅ Volumes reset to 75%"

        return result

    async def _cmd_master(self, params: Dict) -> str:
        """Set master volume"""
        level = params.get("level", 0.75)

        # Get MIDI mapping for master volume
        channel, cc = self.traktor.MIDI_MAP.get('master_volume', (1, 33))
        midi_value = int(level * 127)
        success = self.traktor._send_midi_command(channel, cc, midi_value, "Master Volume")

        if success:
            return f"🔊 Master volume set to {level:.0%}"
        else:
            return f"❌ Failed to set master volume"

    async def _cmd_beatmatch(self, params: Dict) -> str:
        """Automatic beatmatching between two decks"""
        deck1 = params.get("deck1", "A")
        deck2 = params.get("deck2", "B")

        result = f"🎯 Beatmatching Deck {deck1} ↔ Deck {deck2}\n"

        # Sync deck2 to deck1
        deck2_id = DeckID.A if deck2 == "A" else DeckID.B
        self.traktor.sync_deck(deck2_id)
        await asyncio.sleep(0.5)
        result += f"✓ Deck {deck2} synced to Deck {deck1}\n"

        # Match volumes
        for deck_name in [deck1, deck2]:
            deck_id = DeckID.A if deck_name == "A" else DeckID.B
            self.traktor.set_deck_volume(deck_id, 0.75)
        result += f"✓ Volumes matched at 75%\n"

        # EQ reset (neutral position)
        for deck_name in [deck1, deck2]:
            deck_id = DeckID.A if deck_name == "A" else DeckID.B
            for band in ["high", "mid", "low"]:
                self.traktor.set_eq(deck_id, band, 0.5)
        result += f"✓ EQs reset to neutral\n"

        result += "✅ Beatmatch complete!"

        return result

    def print_help(self):
        """Print help at startup"""
        print("\n" + "=" * 70)
        print("🎛️ SIMPLE DJ CONTROLLER - Rule-Based System (NO AI)")
        print("=" * 70)
        print("\n💡 Type 'help' for available commands")
        print("💡 Type 'status' to see current state")
        print("💡 Examples:")
        print("   - search house 120-130")
        print("   - load a")
        print("   - play a")
        print("   - mix a to b 30")
        print("\n" + "=" * 70 + "\n")


# Factory function
def get_simple_dj_controller(config: DJConfig) -> SimpleDJController:
    """Get Simple DJ Controller instance"""
    return SimpleDJController(config)


# CLI Interface
async def run_cli():
    """Run CLI interface"""
    from config import get_config

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Get config
    config = get_config()

    # Create controller
    controller = SimpleDJController(config)

    try:
        # Start
        await controller.start()

        # Command loop
        while True:
            try:
                command = input("\nDJ> ").strip()

                if command.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                if not command:
                    continue

                result = await controller.execute_command(command)
                print(result)

            except KeyboardInterrupt:
                print("\n👋 Interrupted by user")
                break
            except EOFError:
                print("\n👋 EOF received")
                break

    finally:
        controller.stop()


if __name__ == "__main__":
    asyncio.run(run_cli())
