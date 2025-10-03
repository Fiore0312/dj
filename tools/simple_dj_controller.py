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

    # Browser Navigation (NEW)
    TREE_UP = "tree_up"
    TREE_DOWN = "tree_down"
    TREE_ENTER = "tree_enter"
    TREE_EXIT = "tree_exit"
    TREE_EXPAND = "tree_expand"
    TREE_COLLAPSE = "tree_collapse"
    PAGE_UP = "page_up"
    PAGE_DOWN = "page_down"

    # Loop Controls (NEW)
    LOOP_IN = "loop_in"
    LOOP_OUT = "loop_out"
    LOOP_ACTIVATE = "loop_activate"
    LOOP_SIZE = "loop_size"

    # Hotcue (NEW)
    HOTCUE = "hotcue"
    HOTCUE_DELETE = "hotcue_delete"

    # Beatjump (NEW)
    BEATJUMP = "beatjump"

    # Advanced Deck (NEW)
    KEYLOCK = "keylock"
    QUANTIZE = "quantize"
    FLUX = "flux"

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

            # === NEW NAVIGATION COMMANDS ===
            elif cmd_type == CommandType.TREE_UP:
                return await self._cmd_tree_up(params)

            elif cmd_type == CommandType.TREE_DOWN:
                return await self._cmd_tree_down(params)

            elif cmd_type == CommandType.TREE_ENTER:
                return await self._cmd_tree_enter(params)

            elif cmd_type == CommandType.TREE_EXIT:
                return await self._cmd_tree_exit(params)

            elif cmd_type == CommandType.TREE_EXPAND:
                return await self._cmd_tree_expand(params)

            elif cmd_type == CommandType.TREE_COLLAPSE:
                return await self._cmd_tree_collapse(params)

            elif cmd_type == CommandType.PAGE_UP:
                return await self._cmd_page_up(params)

            elif cmd_type == CommandType.PAGE_DOWN:
                return await self._cmd_page_down(params)

            # === LOOP CONTROLS ===
            elif cmd_type == CommandType.LOOP_IN:
                return await self._cmd_loop_in(params)

            elif cmd_type == CommandType.LOOP_OUT:
                return await self._cmd_loop_out(params)

            elif cmd_type == CommandType.LOOP_ACTIVATE:
                return await self._cmd_loop_activate(params)

            elif cmd_type == CommandType.LOOP_SIZE:
                return await self._cmd_loop_size(params)

            # === HOTCUE ===
            elif cmd_type == CommandType.HOTCUE:
                return await self._cmd_hotcue(params)

            elif cmd_type == CommandType.HOTCUE_DELETE:
                return await self._cmd_hotcue_delete(params)

            # === BEATJUMP ===
            elif cmd_type == CommandType.BEATJUMP:
                return await self._cmd_beatjump(params)

            # === ADVANCED DECK CONTROLS ===
            elif cmd_type == CommandType.KEYLOCK:
                return await self._cmd_keylock(params)

            elif cmd_type == CommandType.QUANTIZE:
                return await self._cmd_quantize(params)

            elif cmd_type == CommandType.FLUX:
                return await self._cmd_flux(params)

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

        # === NEW NAVIGATION COMMANDS ===

        # TREE NAVIGATION
        if re.match(r"(tree|folder|playlist|cartella)", cmd):
            if "up" in cmd or "su" in cmd or "sopra" in cmd:
                return CommandType.TREE_UP, {}
            elif "down" in cmd or "giù" in cmd or "sotto" in cmd:
                return CommandType.TREE_DOWN, {}
            elif "enter" in cmd or "entra" in cmd or "open" in cmd or "apri" in cmd:
                return CommandType.TREE_ENTER, {}
            elif "exit" in cmd or "esci" in cmd or "back" in cmd or "indietro" in cmd:
                return CommandType.TREE_EXIT, {}
            elif "expand" in cmd or "espandi" in cmd:
                return CommandType.TREE_EXPAND, {}
            elif "collapse" in cmd or "chiudi" in cmd:
                return CommandType.TREE_COLLAPSE, {}

        # PAGE NAVIGATION
        if "page" in cmd or "pagina" in cmd:
            if "up" in cmd or "su" in cmd:
                return CommandType.PAGE_UP, {}
            elif "down" in cmd or "giù" in cmd:
                return CommandType.PAGE_DOWN, {}

        # LOOP CONTROLS
        if re.match(r"(loop)", cmd):
            deck = self._extract_deck(cmd)
            if "in" in cmd and "out" not in cmd:
                return CommandType.LOOP_IN, {"deck": deck}
            elif "out" in cmd:
                return CommandType.LOOP_OUT, {"deck": deck}
            elif "activate" in cmd or "attiva" in cmd or "on" in cmd:
                return CommandType.LOOP_ACTIVATE, {"deck": deck, "active": True}
            elif "deactivate" in cmd or "disattiva" in cmd or "off" in cmd:
                return CommandType.LOOP_ACTIVATE, {"deck": deck, "active": False}
            elif "toggle" in cmd:
                return CommandType.LOOP_ACTIVATE, {"deck": deck, "active": None}  # Toggle
            else:
                # Check for loop size (e.g., "loop 4 beats", "loop 8")
                size = self._extract_number(cmd, default=4)
                return CommandType.LOOP_SIZE, {"deck": deck, "size": size}

        # HOTCUE
        if re.match(r"(hotcue|hot cue|cue)", cmd) and not re.match(r"^cue\s*$", cmd):
            deck = self._extract_deck(cmd)
            number = self._extract_hotcue_number(cmd)
            if "delete" in cmd or "cancella" in cmd or "remove" in cmd:
                return CommandType.HOTCUE_DELETE, {"deck": deck, "number": number}
            else:
                return CommandType.HOTCUE, {"deck": deck, "number": number}

        # BEATJUMP
        if re.match(r"(beatjump|beat jump|jump)", cmd):
            deck = self._extract_deck(cmd)
            direction, beats = self._extract_beatjump_params(cmd)
            return CommandType.BEATJUMP, {"deck": deck, "direction": direction, "beats": beats}

        # ADVANCED DECK CONTROLS
        if "keylock" in cmd or "key lock" in cmd:
            deck = self._extract_deck(cmd)
            state = self._extract_toggle_state(cmd)
            return CommandType.KEYLOCK, {"deck": deck, "state": state}

        if "quantize" in cmd:
            deck = self._extract_deck(cmd)
            state = self._extract_toggle_state(cmd)
            return CommandType.QUANTIZE, {"deck": deck, "state": state}

        if "flux" in cmd:
            deck = self._extract_deck(cmd)
            state = self._extract_toggle_state(cmd)
            return CommandType.FLUX, {"deck": deck, "state": state}

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

    def _extract_hotcue_number(self, cmd: str) -> int:
        """Extract hotcue number (1-8) from command"""
        # Try to find number in command
        match = re.search(r"(?:hotcue|cue|hot cue)\s*(\d+)", cmd)
        if match:
            number = int(match.group(1))
            # Clamp to valid range
            return max(1, min(8, number))

        # Default to hotcue 1
        return 1

    def _extract_beatjump_params(self, cmd: str) -> Tuple[str, int]:
        """Extract direction (forward/backward) and beat count (1/4) from beatjump command"""
        # Default values
        direction = "forward"
        beats = 1

        # Detect direction
        if "back" in cmd or "indietro" in cmd or "backward" in cmd or "-" in cmd:
            direction = "backward"
        elif "forward" in cmd or "avanti" in cmd or "fwd" in cmd or "+" in cmd:
            direction = "forward"

        # Extract beat count (usually 1 or 4)
        match = re.search(r"(\d+)\s*(?:beat|battute?)", cmd)
        if match:
            beats = int(match.group(1))
        else:
            # Check for just a number
            match = re.search(r"\s(\d+)(?:\s|$)", cmd)
            if match:
                beats = int(match.group(1))

        # Valid beat counts are typically 1 or 4
        if beats not in [1, 4]:
            beats = 1 if beats < 3 else 4

        return direction, beats

    def _extract_toggle_state(self, cmd: str) -> str:
        """Extract on/off/toggle state for keylock/quantize/flux"""
        if "on" in cmd or "attiva" in cmd or "enable" in cmd:
            return "on"
        elif "off" in cmd or "disattiva" in cmd or "disable" in cmd:
            return "off"
        else:
            return "toggle"  # Default to toggle

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

📂 CARICAMENTO & BROWSER:
  load [a|b]           - Carica traccia selezionata nel deck
  browse up/down [N]   - Naviga lista browser (es: "browse down 5")

📁 NAVIGAZIONE TREE (NUOVO):
  tree up/down         - Su/giù nell'albero playlist
  tree enter           - Entra in cartella/playlist
  tree exit            - Esci da cartella (torna indietro)
  tree expand/collapse - Espandi/chiudi cartella
  page up/down         - Pagina su/giù nel browser

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

🔁 LOOP CONTROLS (NUOVO):
  loop in [a|b]        - Imposta punto IN del loop
  loop out [a|b]       - Imposta punto OUT del loop
  loop activate [a|b]  - Attiva loop
  loop [4|8] [a|b]     - Imposta loop di N battute

🎯 HOTCUES (NUOVO):
  hotcue [1-8] [a|b]   - Triggera hotcue (es: "hotcue 3 a")
  delete hotcue [1-8]  - Cancella hotcue

⏭️ BEATJUMP (NUOVO):
  beatjump forward [1|4] [a|b]  - Salta avanti N battute
  beatjump back [1|4] [a|b]     - Salta indietro N battute

🔧 CONTROLLI AVANZATI (NUOVO):
  keylock [on|off] [a|b]  - Attiva/disattiva keylock
  quantize [on|off] [a|b] - Attiva/disattiva quantize
  flux [on|off] [a|b]     - Attiva/disattiva flux mode

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
  tree enter           → Entra in playlist selezionata
  tree down            → Scorri playlist verso il basso
  mix a to b 30        → Transizione da A a B in 30 secondi

💡 ESEMPI AVANZATI:
  loop in a            → Imposta inizio loop su deck A
  loop 4 b             → Loop di 4 battute su deck B
  hotcue 3 a           → Triggera hotcue 3 su deck A
  beatjump back 4 b    → Salta indietro 4 battute su deck B
  keylock on a         → Attiva keylock su deck A
  tree exit            → Torna al livello superiore
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

    # === NEW NAVIGATION & ADVANCED COMMAND HANDLERS ===

    async def _cmd_tree_up(self, params: Dict) -> str:
        """Navigate up in browser tree"""
        channel, cc = self.traktor.MIDI_MAP.get('browser_tree_up', (1, 55))
        success = self.traktor._send_midi_command(channel, cc, 127, "Tree Up")
        return "📁 ⬆️ Browser tree up" if success else "❌ Failed to navigate tree up"

    async def _cmd_tree_down(self, params: Dict) -> str:
        """Navigate down in browser tree"""
        channel, cc = self.traktor.MIDI_MAP.get('browser_tree_down', (1, 56))
        success = self.traktor._send_midi_command(channel, cc, 127, "Tree Down")
        return "📁 ⬇️ Browser tree down" if success else "❌ Failed to navigate tree down"

    async def _cmd_tree_enter(self, params: Dict) -> str:
        """Enter folder/playlist in browser"""
        channel, cc = self.traktor.MIDI_MAP.get('browser_tree_enter', (1, 57))
        success = self.traktor._send_midi_command(channel, cc, 127, "Tree Enter")
        return "📂 ➡️ Entered folder" if success else "❌ Failed to enter folder"

    async def _cmd_tree_exit(self, params: Dict) -> str:
        """Exit current folder/go back"""
        channel, cc = self.traktor.MIDI_MAP.get('browser_tree_exit', (1, 58))
        success = self.traktor._send_midi_command(channel, cc, 127, "Tree Exit")
        return "📂 ⬅️ Exited folder" if success else "❌ Failed to exit folder"

    async def _cmd_tree_expand(self, params: Dict) -> str:
        """Expand folder in tree"""
        channel, cc = self.traktor.MIDI_MAP.get('browser_tree_expand', (1, 59))
        success = self.traktor._send_midi_command(channel, cc, 127, "Tree Expand")
        return "📂 ⊞ Folder expanded" if success else "❌ Failed to expand folder"

    async def _cmd_tree_collapse(self, params: Dict) -> str:
        """Collapse folder in tree"""
        channel, cc = self.traktor.MIDI_MAP.get('browser_tree_collapse', (1, 60))
        success = self.traktor._send_midi_command(channel, cc, 127, "Tree Collapse")
        return "📂 ⊟ Folder collapsed" if success else "❌ Failed to collapse folder"

    async def _cmd_page_up(self, params: Dict) -> str:
        """Page up in browser"""
        channel, cc = self.traktor.MIDI_MAP.get('browser_page_up', (1, 61))
        success = self.traktor._send_midi_command(channel, cc, 127, "Page Up")
        return "📄 ⬆️ Page up" if success else "❌ Failed page up"

    async def _cmd_page_down(self, params: Dict) -> str:
        """Page down in browser"""
        channel, cc = self.traktor.MIDI_MAP.get('browser_page_down', (1, 62))
        success = self.traktor._send_midi_command(channel, cc, 127, "Page Down")
        return "📄 ⬇️ Page down" if success else "❌ Failed page down"

    async def _cmd_loop_in(self, params: Dict) -> str:
        """Set loop in point"""
        deck = params.get("deck", "A")
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_loop_in', (1, 70))
        success = self.traktor._send_midi_command(channel, cc, 127, f"Loop In {deck}")
        return f"🔁 Deck {deck} loop IN set" if success else f"❌ Failed to set loop in on Deck {deck}"

    async def _cmd_loop_out(self, params: Dict) -> str:
        """Set loop out point"""
        deck = params.get("deck", "A")
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_loop_out', (1, 71))
        success = self.traktor._send_midi_command(channel, cc, 127, f"Loop Out {deck}")
        return f"🔁 Deck {deck} loop OUT set" if success else f"❌ Failed to set loop out on Deck {deck}"

    async def _cmd_loop_activate(self, params: Dict) -> str:
        """Activate/deactivate loop"""
        deck = params.get("deck", "A")
        active = params.get("active", True)
        value = 127 if active else 0
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_loop_active', (1, 72))
        success = self.traktor._send_midi_command(channel, cc, value, f"Loop {'ON' if active else 'OFF'} {deck}")
        status = "activated" if active else "deactivated"
        return f"🔁 Deck {deck} loop {status}" if success else f"❌ Failed to {status} loop on Deck {deck}"

    async def _cmd_loop_size(self, params: Dict) -> str:
        """Set loop size"""
        deck = params.get("deck", "A")
        beats = params.get("beats", 4)
        # Map beats to MIDI value (simplified: 4 beats = 64, 8 beats = 96, etc.)
        midi_value = min(127, max(0, int(beats * 16)))
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_loop_size', (1, 73))
        success = self.traktor._send_midi_command(channel, cc, midi_value, f"Loop Size {deck}")
        return f"🔁 Deck {deck} loop size: {beats} beats" if success else f"❌ Failed to set loop size on Deck {deck}"

    async def _cmd_hotcue(self, params: Dict) -> str:
        """Set/trigger hotcue"""
        deck = params.get("deck", "A")
        number = params.get("number", 1)
        # CC 80-87 for deck A, 88-95 for deck B
        base_cc = 80 if deck == "A" else 88
        cc_num = base_cc + (number - 1)
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_hotcue_{number}', (1, cc_num))
        success = self.traktor._send_midi_command(channel, cc, 127, f"Hotcue {number} {deck}")
        return f"🎯 Deck {deck} hotcue {number} triggered" if success else f"❌ Failed to trigger hotcue {number} on Deck {deck}"

    async def _cmd_hotcue_delete(self, params: Dict) -> str:
        """Delete hotcue"""
        deck = params.get("deck", "A")
        number = params.get("number", 1)
        base_cc = 80 if deck == "A" else 88
        cc_num = base_cc + (number - 1)
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_hotcue_{number}', (1, cc_num))
        # Send 0 to delete
        success = self.traktor._send_midi_command(channel, cc, 0, f"Delete Hotcue {number} {deck}")
        return f"🗑️ Deck {deck} hotcue {number} deleted" if success else f"❌ Failed to delete hotcue {number} on Deck {deck}"

    async def _cmd_beatjump(self, params: Dict) -> str:
        """Beatjump forward/backward"""
        deck = params.get("deck", "A")
        direction = params.get("direction", "forward")
        beats = params.get("beats", 1)

        # Determine CC based on deck, direction, and beat count
        suffix = "fwd" if direction == "forward" else "back"
        cc_key = f'deck_{deck.lower()}_beatjump_{suffix}_{beats}'

        # Default CC values if not in map
        default_cc = 96 if deck == "A" else 102
        if direction == "backward":
            default_cc += 1
        if beats == 4:
            default_cc += 2

        channel, cc = self.traktor.MIDI_MAP.get(cc_key, (1, default_cc))
        success = self.traktor._send_midi_command(channel, cc, 127, f"Beatjump {direction} {beats} {deck}")

        arrow = "➡️" if direction == "forward" else "⬅️"
        return f"⏭️ Deck {deck} beatjump {arrow} {beats} beat(s)" if success else f"❌ Failed beatjump on Deck {deck}"

    async def _cmd_keylock(self, params: Dict) -> str:
        """Toggle/set keylock"""
        deck = params.get("deck", "A")
        state = params.get("state", "toggle")
        # Use 127 for on, 0 for off, 64 for toggle
        value = 127 if state == "on" else (0 if state == "off" else 64)
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_keylock', (1, 108))
        success = self.traktor._send_midi_command(channel, cc, value, f"Keylock {state} {deck}")
        return f"🔒 Deck {deck} keylock {state}" if success else f"❌ Failed to set keylock on Deck {deck}"

    async def _cmd_quantize(self, params: Dict) -> str:
        """Toggle/set quantize"""
        deck = params.get("deck", "A")
        state = params.get("state", "toggle")
        value = 127 if state == "on" else (0 if state == "off" else 64)
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_quantize', (1, 110))
        success = self.traktor._send_midi_command(channel, cc, value, f"Quantize {state} {deck}")
        return f"📐 Deck {deck} quantize {state}" if success else f"❌ Failed to set quantize on Deck {deck}"

    async def _cmd_flux(self, params: Dict) -> str:
        """Toggle/set flux mode"""
        deck = params.get("deck", "A")
        state = params.get("state", "toggle")
        value = 127 if state == "on" else (0 if state == "off" else 64)
        channel, cc = self.traktor.MIDI_MAP.get(f'deck_{deck.lower()}_flux', (1, 112))
        success = self.traktor._send_midi_command(channel, cc, value, f"Flux {state} {deck}")
        return f"🌊 Deck {deck} flux mode {state}" if success else f"❌ Failed to set flux on Deck {deck}"

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
