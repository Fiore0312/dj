#!/usr/bin/env python3
"""
🎛️ Traktor Control - Sistema MIDI Semplificato
Controllo semplice e diretto di Traktor via MIDI con mappatura AI DJ
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import threading

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False
    print("⚠️ rtmidi non disponibile. Installa con: pip install python-rtmidi")

from config import DJConfig

logger = logging.getLogger(__name__)

class MIDIChannel(Enum):
    """Canali MIDI per diversi tipi di controllo"""
    AI_CONTROL = 1      # AI invia comandi
    STATUS_FEEDBACK = 2  # Traktor invia stato
    HUMAN_OVERRIDE = 3   # Controlli umani
    EFFECTS = 4         # Effetti condivisi

class DeckID(Enum):
    """Identificatori deck"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"

@dataclass
class MIDICommand:
    """Comando MIDI strutturato"""
    channel: int
    cc: int
    value: int
    description: str = ""

@dataclass
class TraktorStatus:
    """Stato attuale di Traktor"""
    deck_a_bpm: float = 0.0
    deck_b_bpm: float = 0.0
    deck_a_position: float = 0.0
    deck_b_position: float = 0.0
    crossfader_position: int = 64
    master_volume: int = 100
    ai_enabled: bool = True
    last_update: float = 0.0

class TraktorController:
    """Controller semplificato per Traktor"""

    # Mappatura MIDI CC corretta per controlli standard Traktor
    # Basata sui mapping standard e verificata con test tool
    MIDI_MAP = {
        # TRANSPORT CONTROLS - Compatibili con Traktor standard
        'deck_a_play': (MIDIChannel.AI_CONTROL.value, 20),
        'deck_b_play': (MIDIChannel.AI_CONTROL.value, 21),
        'deck_c_play': (MIDIChannel.AI_CONTROL.value, 22),
        'deck_d_play': (MIDIChannel.AI_CONTROL.value, 23),

        'deck_a_cue': (MIDIChannel.AI_CONTROL.value, 24),
        'deck_b_cue': (MIDIChannel.AI_CONTROL.value, 25),
        'deck_c_cue': (MIDIChannel.AI_CONTROL.value, 26),
        'deck_d_cue': (MIDIChannel.AI_CONTROL.value, 27),

        # VOLUME CONTROLS - Standard range per evitare conflitti
        'deck_a_volume': (MIDIChannel.AI_CONTROL.value, 28),
        'deck_b_volume': (MIDIChannel.AI_CONTROL.value, 29),
        'deck_c_volume': (MIDIChannel.AI_CONTROL.value, 30),
        'deck_d_volume': (MIDIChannel.AI_CONTROL.value, 31),

        # CROSSFADER E MASTER - Range alto per evitare conflitti
        'crossfader': (MIDIChannel.AI_CONTROL.value, 32),
        'master_volume': (MIDIChannel.AI_CONTROL.value, 33),

        # EQ CONTROLS - Range dedicato per Deck A
        'deck_a_eq_high': (MIDIChannel.AI_CONTROL.value, 34),
        'deck_a_eq_mid': (MIDIChannel.AI_CONTROL.value, 35),
        'deck_a_eq_low': (MIDIChannel.AI_CONTROL.value, 36),

        # BROWSER CONTROLS - Essenziali per track loading
        'browser_up': (MIDIChannel.AI_CONTROL.value, 37),
        'browser_down': (MIDIChannel.AI_CONTROL.value, 38),
        'browser_load_deck_a': (MIDIChannel.AI_CONTROL.value, 39),
        'browser_load_deck_b': (MIDIChannel.AI_CONTROL.value, 40),
        'browser_select_item': (MIDIChannel.AI_CONTROL.value, 49),  # Browser enter/select

        # SYNC CONTROLS - Range dedicato
        'deck_a_sync': (MIDIChannel.AI_CONTROL.value, 41),
        'deck_b_sync': (MIDIChannel.AI_CONTROL.value, 42),
        'deck_c_sync': (MIDIChannel.AI_CONTROL.value, 43),
        'deck_d_sync': (MIDIChannel.AI_CONTROL.value, 44),

        # PITCH CONTROLS - Range dedicato
        'deck_a_pitch': (MIDIChannel.AI_CONTROL.value, 45),
        'deck_b_pitch': (MIDIChannel.AI_CONTROL.value, 46),
        'deck_c_pitch': (MIDIChannel.AI_CONTROL.value, 47),
        'deck_d_pitch': (MIDIChannel.AI_CONTROL.value, 48),

        # EQ CONTROLS EXTENDED - Deck B
        'deck_b_eq_high': (MIDIChannel.AI_CONTROL.value, 50),
        'deck_b_eq_mid': (MIDIChannel.AI_CONTROL.value, 51),
        'deck_b_eq_low': (MIDIChannel.AI_CONTROL.value, 52),

        # COMPATIBILITÀ LEGACY - Mantengo alcuni vecchi mapping
        'deck_a_load_selected': (MIDIChannel.AI_CONTROL.value, 39),  # Alias per browser_load_deck_a
        'deck_b_load_selected': (MIDIChannel.AI_CONTROL.value, 40),  # Alias per browser_load_deck_b
        'browser_scroll_up': (MIDIChannel.AI_CONTROL.value, 37),     # Alias per browser_up
        'browser_scroll_down': (MIDIChannel.AI_CONTROL.value, 38),   # Alias per browser_down

        # Human Override (Channel 3) - Range alto per sicurezza
        'emergency_stop': (MIDIChannel.HUMAN_OVERRIDE.value, 80),
        'ai_enable': (MIDIChannel.HUMAN_OVERRIDE.value, 81),
        'headphone_volume': (MIDIChannel.HUMAN_OVERRIDE.value, 90),
        'headphone_mix': (MIDIChannel.HUMAN_OVERRIDE.value, 91),

        # Effects (Channel 4) - Range molto alto
        'fx1_drywet': (MIDIChannel.EFFECTS.value, 100),
        'fx2_drywet': (MIDIChannel.EFFECTS.value, 101),
        'fx3_drywet': (MIDIChannel.EFFECTS.value, 102),
        'fx4_drywet': (MIDIChannel.EFFECTS.value, 103),
    }

    # Status feedback CC mappings (Channel 2 - INPUT da Traktor)
    STATUS_MAP = {
        40: 'deck_a_bpm',
        41: 'deck_b_bpm',
        42: 'deck_c_bpm',
        43: 'deck_d_bpm',
        44: 'deck_a_position',
        45: 'deck_b_position',
        46: 'deck_c_position',
        47: 'deck_d_position',
        50: 'master_bpm',
        51: 'beat_phase',
    }

    def __init__(self, config: DJConfig):
        self.config = config
        self.midi_out: Optional[rtmidi.MidiOut] = None
        self.midi_in: Optional[rtmidi.MidiIn] = None
        self.connected = False
        self.status = TraktorStatus()

        # Threading per status updates
        self.status_thread: Optional[threading.Thread] = None
        self.running = False

        # Stato deck interno per tracking play/pause
        self.deck_states = {
            DeckID.A: {
                'playing': False,
                'cued': False,
                'loaded': False,
                'track_name': None,
                'track_id': None,
                'last_loaded_time': None,
                'load_source_position': None
            },
            DeckID.B: {
                'playing': False,
                'cued': False,
                'loaded': False,
                'track_name': None,
                'track_id': None,
                'last_loaded_time': None,
                'load_source_position': None
            },
            DeckID.C: {
                'playing': False,
                'cued': False,
                'loaded': False,
                'track_name': None,
                'track_id': None,
                'last_loaded_time': None,
                'load_source_position': None
            },
            DeckID.D: {
                'playing': False,
                'cued': False,
                'loaded': False,
                'track_name': None,
                'track_id': None,
                'last_loaded_time': None,
                'load_source_position': None
            },
        }

        # BROWSER POSITION TRACKING - Nuovo sistema intelligente
        self.browser_state = {
            'current_position': 0,  # Posizione attuale nel browser (stimata)
            'total_tracks': 1000,   # Stima totale tracce (verrà aggiornata)
            'navigation_history': [],  # Storia navigazione [position, timestamp]
            'loaded_track_positions': set(),  # Set posizioni già caricate
            'loaded_track_ids': set(),  # Set track IDs già caricati
            'last_navigation_time': 0.0,
            'consecutive_duplicates': 0,  # Counter duplicati consecutivi
            'smart_navigation_enabled': True,
            'anti_duplicate_radius': 5,  # Evita posizioni vicine a tracce già caricate
        }

        # Statistiche
        self.stats = {
            'commands_sent': 0,
            'status_received': 0,
            'errors': 0,
            'uptime_start': time.time()
        }

        # State Synchronization System
        self.state_synchronizer: Optional[Any] = None  # Will be initialized when needed
        self.sync_enabled = True
        self.last_state_verification = 0.0
        self.state_verification_interval = 15.0  # Verify every 15 seconds

    def connect(self, output_only: bool = False) -> bool:
        """Connetti a Traktor via IAC Driver"""
        if not RTMIDI_AVAILABLE:
            logger.error("rtmidi non disponibile")
            return False

        try:
            # Connessione output (inviamo comandi a Traktor)
            self.midi_out = rtmidi.MidiOut()

            # Cerca IAC Bus 1
            output_ports = self.midi_out.get_ports()
            iac_port_idx = None

            for i, port in enumerate(output_ports):
                if self.config.iac_bus_name in port or "Bus 1" in port:
                    iac_port_idx = i
                    break

            if iac_port_idx is None:
                # Crea porta virtuale se IAC non trovato
                self.midi_out.open_virtual_port(self.config.midi_device_name)
                logger.info(f"✅ Porta virtuale creata: {self.config.midi_device_name}")
            else:
                self.midi_out.open_port(iac_port_idx)
                logger.info(f"✅ Connesso a IAC: {output_ports[iac_port_idx]}")

            self.connected = True
            self.running = True

            # Se output_only, salta connessione input e test
            if output_only:
                logger.info("ℹ️ Modalità output-only, saltando input e test")
                return True

            # Connessione input (riceviamo status da Traktor)
            self.midi_in = rtmidi.MidiIn()
            self.midi_in.set_callback(self._status_callback)

            input_ports = self.midi_in.get_ports()
            iac_in_idx = None

            for i, port in enumerate(input_ports):
                if self.config.iac_bus_name in port or "Bus 1" in port:
                    iac_in_idx = i
                    break

            if iac_in_idx is not None:
                self.midi_in.open_port(iac_in_idx)
                logger.info(f"✅ Input connesso: {input_ports[iac_in_idx]}")
            else:
                self.midi_in.open_virtual_port(f"{self.config.midi_device_name}_IN")
                logger.info("✅ Porta input virtuale creata")

            # Test connessione
            self.test_connection()

            return True

        except Exception as e:
            logger.error(f"❌ Errore connessione Traktor: {e}")
            return False

    def _status_callback(self, message, data):
        """Callback per messaggi di status da Traktor"""
        try:
            midi_message, timestamp = message

            if len(midi_message) >= 3:
                status_byte, cc, value = midi_message[0], midi_message[1], midi_message[2]
                channel = (status_byte & 0x0F) + 1

                # Solo messaggi di status (Channel 2)
                if channel == MIDIChannel.STATUS_FEEDBACK.value and cc in self.STATUS_MAP:
                    status_key = self.STATUS_MAP[cc]

                    # Converti valore MIDI in range appropriato
                    if 'bpm' in status_key:
                        # BPM: da 0-127 a 60-200 BPM
                        bpm_value = 60 + (value / 127) * 140
                        setattr(self.status, status_key, bpm_value)
                    elif 'position' in status_key:
                        # Posizione: da 0-127 a 0.0-1.0
                        pos_value = value / 127.0
                        setattr(self.status, status_key, pos_value)
                    else:
                        setattr(self.status, status_key, value)

                    self.status.last_update = time.time()
                    self.stats['status_received'] += 1

                    logger.debug(f"📥 Status: {status_key} = {value}")

        except Exception as e:
            logger.error(f"❌ Errore callback status: {e}")

    def _send_midi_command(self, channel: int, cc: int, value: int, description: str = "") -> bool:
        """Invia comando MIDI a Traktor"""
        if not self.connected or not self.midi_out:
            logger.error("Non connesso a Traktor")
            return False

        try:
            # Costruisci messaggio MIDI (Control Change)
            message = [0xB0 + (channel - 1), cc, value]

            self.midi_out.send_message(message)
            self.stats['commands_sent'] += 1

            logger.debug(f"📤 Comando: CH{channel} CC{cc}={value} ({description})")
            return True

        except Exception as e:
            logger.error(f"❌ Errore invio comando: {e}")
            self.stats['errors'] += 1
            return False

    def test_connection(self) -> bool:
        """Testa connessione con Traktor"""
        logger.info("🧪 Test connessione Traktor...")

        # Invia alcuni comandi di test
        test_commands = [
            ('emergency_stop', 0),  # Reset
            ('ai_enable', 127),     # Abilita AI
            ('deck_a_volume', 64),  # Volume medio
            ('crossfader', 64),     # Crossfader centro
        ]

        success_count = 0
        for cmd_name, value in test_commands:
            if cmd_name in self.MIDI_MAP:
                channel, cc = self.MIDI_MAP[cmd_name]
                if self._send_midi_command(channel, cc, value, f"Test {cmd_name}"):
                    success_count += 1
                time.sleep(0.1)

        success_rate = success_count / len(test_commands)
        logger.info(f"📊 Test completato: {success_count}/{len(test_commands)} comandi OK ({success_rate*100:.0f}%)")

        return success_rate > 0.5

    # Metodi di controllo semplificati
    def set_deck_volume(self, deck: DeckID, volume: float) -> bool:
        """Imposta volume deck (0.0-1.0)"""
        midi_value = int(volume * 127)
        channel, cc = self.MIDI_MAP[f'deck_{deck.value.lower()}_volume']
        return self._send_midi_command(channel, cc, midi_value, f"Deck {deck.value} Volume")

    def set_crossfader(self, position: float) -> bool:
        """Imposta crossfader (0.0=A, 1.0=B)"""
        midi_value = int(position * 127)
        channel, cc = self.MIDI_MAP['crossfader']
        return self._send_midi_command(channel, cc, midi_value, "Crossfader")

    def set_eq(self, deck: DeckID, eq_type: str, value: float) -> bool:
        """Imposta EQ (eq_type: 'high'/'mid'/'low', value: 0.0-1.0, 0.5=neutro)"""
        midi_value = int(value * 127)
        key = f'deck_{deck.value.lower()}_eq_{eq_type}'

        if key in self.MIDI_MAP:
            channel, cc = self.MIDI_MAP[key]
            return self._send_midi_command(channel, cc, midi_value, f"Deck {deck.value} EQ {eq_type}")
        return False

    def play_deck(self, deck: DeckID) -> bool:
        """Play deck robusto con verifica stato traccia"""
        # Verifica se deck è già in play
        if self.deck_states[deck]['playing']:
            logger.debug(f"Deck {deck.value} già in play")
            return True

        # Verifica se c'è una traccia caricata (robustness check)
        if not self.deck_states[deck]['loaded']:
            logger.warning(f"⚠️ Deck {deck.value} may not have a track loaded - playing anyway")

        # Verifica timing dal caricamento (se molto recente, potrebbe non essere pronto)
        if self.deck_states[deck]['last_loaded_time']:
            import time
            time_since_load = time.time() - self.deck_states[deck]['last_loaded_time']
            if time_since_load < 1.0:  # Meno di 1 secondo fa
                logger.warning(f"⚠️ Deck {deck.value} track loaded {time_since_load:.1f}s ago - may not be ready")

        # Tenta play
        success = self.toggle_play_pause(deck)

        if success:
            logger.info(f"🎉 ROBUST PLAY SUCCESS: Deck {deck.value} started playing")
        else:
            logger.error(f"❌ ROBUST PLAY FAILED: Deck {deck.value} play command failed")

        return success

    def pause_deck(self, deck: DeckID) -> bool:
        """Pause deck (se già in pause, non fa nulla)"""
        if not self.deck_states[deck]['playing']:
            logger.debug(f"Deck {deck.value} già in pause")
            return True

        return self.toggle_play_pause(deck)

    def toggle_play_pause(self, deck: DeckID) -> bool:
        """Toggle play/pause deck (Traktor usa trigger)"""
        channel, cc = self.MIDI_MAP[f'deck_{deck.value.lower()}_play']

        # Per Traktor trigger: invia valore >64 per attivare toggle
        success = self._send_midi_command(channel, cc, 127, f"Deck {deck.value} Toggle Play/Pause")

        if success:
            # Aggiorna stato interno
            self.deck_states[deck]['playing'] = not self.deck_states[deck]['playing']
            action = "Play" if self.deck_states[deck]['playing'] else "Pause"
            logger.info(f"✅ Deck {deck.value} → {action}")

        return success

    def cue_deck(self, deck: DeckID) -> bool:
        """Cue deck (trigger)"""
        channel, cc = self.MIDI_MAP[f'deck_{deck.value.lower()}_cue']
        success = self._send_midi_command(channel, cc, 127, f"Deck {deck.value} Cue")

        if success:
            # Quando si fa cue, il deck va in pause
            self.deck_states[deck]['playing'] = False
            self.deck_states[deck]['cued'] = True
            logger.info(f"✅ Deck {deck.value} → Cue (Auto-paused)")

        return success

    def sync_deck(self, deck: DeckID) -> bool:
        """Sync deck"""
        channel, cc = self.MIDI_MAP[f'deck_{deck.value.lower()}_sync']
        return self._send_midi_command(channel, cc, 127, f"Deck {deck.value} Sync")

    def set_fx_drywet(self, fx_unit: int, amount: float) -> bool:
        """Imposta FX dry/wet (1-4, 0.0-1.0)"""
        if 1 <= fx_unit <= 4:
            midi_value = int(amount * 127)
            channel, cc = self.MIDI_MAP[f'fx{fx_unit}_drywet']
            return self._send_midi_command(channel, cc, midi_value, f"FX{fx_unit} Dry/Wet")
        return False

    def load_track_to_deck(self, deck: DeckID) -> bool:
        """Carica la traccia selezionata nel deck specificato"""
        try:
            # Use new browser_load_deck naming
            if deck == DeckID.A:
                channel, cc = self.MIDI_MAP['browser_load_deck_a']
            elif deck == DeckID.B:
                channel, cc = self.MIDI_MAP['browser_load_deck_b']
            else:
                # Fallback to legacy naming for C/D
                channel, cc = self.MIDI_MAP[f'deck_{deck.value.lower()}_load_selected']
            success = self._send_midi_command(channel, cc, 127, f"Load track to Deck {deck.value}")

            if success:
                # Aggiorna stato tracking
                import time
                self.deck_states[deck]['loaded'] = True
                self.deck_states[deck]['last_loaded_time'] = time.time()
                self.deck_states[deck]['track_name'] = f"Track_{int(time.time())}"  # Placeholder
                self.deck_states[deck]['playing'] = False  # Reset play state
                self.deck_states[deck]['cued'] = False     # Reset cue state

                logger.info(f"🎵 Traccia caricata nel Deck {deck.value}")
                self.stats['commands_sent'] += 1
            else:
                logger.error(f"❌ Errore caricamento traccia nel Deck {deck.value}")

            return success
        except KeyError:
            logger.error(f"❌ Comando load non disponibile per Deck {deck.value}")
            return False

    def browse_track_up(self) -> bool:
        """Naviga verso l'alto nel browser"""
        channel, cc = self.MIDI_MAP['browser_up']
        return self._send_midi_command(channel, cc, 127, "Browser Scroll Up")

    def browse_track_down(self) -> bool:
        """Naviga verso il basso nel browser"""
        channel, cc = self.MIDI_MAP['browser_down']
        return self._send_midi_command(channel, cc, 127, "Browser Scroll Down")

    def select_browser_item(self) -> bool:
        """Seleziona item corrente nel browser"""
        channel, cc = self.MIDI_MAP['browser_select_item']
        return self._send_midi_command(channel, cc, 127, "Browser Select Item")

    def browser_back(self) -> bool:
        """Torna indietro nel browser"""
        channel, cc = self.MIDI_MAP['browser_back']
        return self._send_midi_command(channel, cc, 127, "Browser Back")

    def load_next_track(self, target_deck: DeckID, direction: str = "down") -> bool:
        """
        Navigazione intelligente del browser e caricamento traccia

        Args:
            target_deck: Deck dove caricare la traccia
            direction: "up" o "down" per navigazione

        Returns:
            bool: True se operazione completata con successo
        """
        try:
            # Naviga nel browser
            if direction == "up":
                nav_success = self.browse_track_up()
            else:
                nav_success = self.browse_track_down()

            if not nav_success:
                logger.error("❌ Errore navigazione browser")
                return False

            # Breve pausa per permettere a Traktor di aggiornare
            time.sleep(0.1)

            # Seleziona l'item
            select_success = self.select_browser_item()
            if not select_success:
                logger.error("❌ Errore selezione item browser")
                return False

            # Breve pausa
            time.sleep(0.1)

            # Carica nel deck
            load_success = self.load_track_to_deck(target_deck)

            if load_success:
                logger.info(f"✅ Traccia caricata con successo nel Deck {target_deck.value}")
                return True
            else:
                logger.error(f"❌ Errore caricamento nel Deck {target_deck.value}")
                return False

        except Exception as e:
            logger.error(f"❌ Errore load_next_track: {e}")
            return False

    # ==========================================
    # INTELLIGENT BROWSER POSITION TRACKING
    # ==========================================

    def _update_browser_position(self, direction: str, steps: int = 1) -> None:
        """Aggiorna la posizione stimata del browser"""
        current_time = time.time()

        if direction == "up":
            new_position = max(0, self.browser_state['current_position'] - steps)
        else:  # down
            new_position = min(
                self.browser_state['total_tracks'] - 1,
                self.browser_state['current_position'] + steps
            )

        # Aggiorna stato
        old_position = self.browser_state['current_position']
        self.browser_state['current_position'] = new_position
        self.browser_state['last_navigation_time'] = current_time

        # Aggiungi alla storia
        self.browser_state['navigation_history'].append([new_position, current_time])

        # Mantieni solo gli ultimi 100 movimenti
        if len(self.browser_state['navigation_history']) > 100:
            self.browser_state['navigation_history'] = self.browser_state['navigation_history'][-100:]

        logger.debug(f"📍 Browser position: {old_position} → {new_position} (direction: {direction})")

    def _is_position_safe_to_load(self, position: int) -> bool:
        """Verifica se una posizione è sicura da caricare (non duplicata)"""
        # Controlla se questa posizione è già stata caricata
        if position in self.browser_state['loaded_track_positions']:
            return False

        # Controlla il raggio anti-duplicazione
        radius = self.browser_state['anti_duplicate_radius']
        for loaded_pos in self.browser_state['loaded_track_positions']:
            if abs(position - loaded_pos) <= radius:
                logger.debug(f"⚠️ Position {position} troppo vicina a {loaded_pos} (radius: {radius})")
                return False

        return True

    def _find_safe_navigation_target(self, preferred_direction: str, max_attempts: int = 20) -> Optional[int]:
        """Trova una posizione sicura nel browser evitando duplicati"""
        current_pos = self.browser_state['current_position']

        # Prova diverse distanze di navigazione
        for distance in [1, 3, 5, 8, 12, 15, 20, 30]:
            for direction in [preferred_direction, "up" if preferred_direction == "down" else "down"]:
                if direction == "up":
                    target_pos = max(0, current_pos - distance)
                else:
                    target_pos = min(self.browser_state['total_tracks'] - 1, current_pos + distance)

                if self._is_position_safe_to_load(target_pos):
                    logger.info(f"🎯 Safe position found: {target_pos} (distance: {distance}, direction: {direction})")
                    return target_pos

        logger.warning(f"⚠️ No safe position found after {max_attempts} attempts")
        return None

    def _smart_navigate_to_position(self, target_position: int) -> bool:
        """Naviga intelligentemente verso una posizione specifica"""
        current_pos = self.browser_state['current_position']
        distance = target_position - current_pos

        if distance == 0:
            logger.debug("📍 Already at target position")
            return True

        direction = "down" if distance > 0 else "up"
        steps = abs(distance)

        logger.info(f"🧭 Navigating {steps} steps {direction} (from {current_pos} to {target_position})")

        # Naviga un passo alla volta per maggiore precisione
        success_count = 0
        for step in range(steps):
            if direction == "down":
                nav_success = self.browse_track_down()
            else:
                nav_success = self.browse_track_up()

            if nav_success:
                success_count += 1
                self._update_browser_position(direction, 1)
                time.sleep(0.05)  # Breve pausa tra i passi
            else:
                logger.warning(f"⚠️ Navigation failed at step {step + 1}/{steps}")
                break

        success_rate = success_count / steps if steps > 0 else 1.0
        logger.info(f"📊 Navigation completed: {success_count}/{steps} steps ({success_rate:.1%})")

        return success_rate > 0.8  # Considera successo se almeno 80% dei passi funziona

    def load_next_track_smart(self, target_deck: DeckID, preferred_direction: str = "down") -> bool:
        """
        Carica intelligentemente la prossima traccia evitando duplicati

        Args:
            target_deck: Deck dove caricare la traccia
            preferred_direction: Direzione preferita per la ricerca

        Returns:
            bool: True se operazione completata con successo
        """
        try:
            logger.info(f"🧠 Smart track loading for Deck {target_deck.value} (direction: {preferred_direction})")

            # Verifica se smart navigation è abilitata
            if not self.browser_state['smart_navigation_enabled']:
                logger.info("🔄 Smart navigation disabled, falling back to basic navigation")
                return self.load_next_track(target_deck, preferred_direction)

            # Trova una posizione sicura
            safe_target = self._find_safe_navigation_target(preferred_direction)

            if safe_target is None:
                # Fallback: prova navigazione semplice con warning
                logger.warning("⚠️ No safe position found, attempting basic navigation")
                self.browser_state['consecutive_duplicates'] += 1

                # Se troppi duplicati consecutivi, disabilita temporaneamente smart navigation
                if self.browser_state['consecutive_duplicates'] >= 3:
                    logger.warning("🚫 Too many consecutive duplicates, disabling smart navigation for this session")
                    self.browser_state['smart_navigation_enabled'] = False

                return self.load_next_track(target_deck, preferred_direction)

            # Naviga verso la posizione sicura
            nav_success = self._smart_navigate_to_position(safe_target)
            if not nav_success:
                logger.error("❌ Failed to navigate to safe position")
                return False

            # Seleziona l'item
            select_success = self.select_browser_item()
            if not select_success:
                logger.error("❌ Failed to select browser item")
                return False

            time.sleep(0.1)

            # Carica nel deck con tracking avanzato
            load_success = self._load_track_to_deck_with_tracking(target_deck, safe_target)

            if load_success:
                logger.info(f"✅ Smart track loading successful for Deck {target_deck.value}")
                self.browser_state['consecutive_duplicates'] = 0  # Reset counter
                return True
            else:
                logger.error(f"❌ Failed to load track to Deck {target_deck.value}")
                return False

        except Exception as e:
            logger.error(f"❌ Error in smart track loading: {e}")
            return False

    def _load_track_to_deck_with_tracking(self, deck: DeckID, browser_position: int) -> bool:
        """Carica traccia con tracking avanzato della posizione"""
        try:
            # Use new browser_load_deck naming
            if deck == DeckID.A:
                channel, cc = self.MIDI_MAP['browser_load_deck_a']
            elif deck == DeckID.B:
                channel, cc = self.MIDI_MAP['browser_load_deck_b']
            else:
                # Fallback to legacy naming for C/D
                channel, cc = self.MIDI_MAP[f'deck_{deck.value.lower()}_load_selected']

            success = self._send_midi_command(channel, cc, 127, f"Smart Load track to Deck {deck.value}")

            if success:
                # Genera ID traccia unico basato su posizione e tempo
                current_time = time.time()
                track_id = f"track_{browser_position}_{int(current_time)}"

                # Aggiorna stato deck con informazioni complete
                self.deck_states[deck]['loaded'] = True
                self.deck_states[deck]['last_loaded_time'] = current_time
                self.deck_states[deck]['track_id'] = track_id
                self.deck_states[deck]['track_name'] = f"Track_Pos_{browser_position}"
                self.deck_states[deck]['load_source_position'] = browser_position
                self.deck_states[deck]['playing'] = False  # Reset play state
                self.deck_states[deck]['cued'] = False     # Reset cue state

                # Aggiorna browser state
                self.browser_state['loaded_track_positions'].add(browser_position)
                self.browser_state['loaded_track_ids'].add(track_id)

                logger.info(f"🎵 Track loaded: Deck {deck.value} ← Position {browser_position} (ID: {track_id})")
                self.stats['commands_sent'] += 1

                return True
            else:
                logger.error(f"❌ MIDI command failed for Deck {deck.value}")
                return False

        except KeyError as e:
            logger.error(f"❌ MIDI mapping not found: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error in track loading: {e}")
            return False

    def get_browser_status(self) -> Dict[str, Any]:
        """Ottieni stato dettagliato del browser e tracking"""
        return {
            'current_position': self.browser_state['current_position'],
            'loaded_positions': list(self.browser_state['loaded_track_positions']),
            'loaded_track_count': len(self.browser_state['loaded_track_ids']),
            'navigation_history_length': len(self.browser_state['navigation_history']),
            'consecutive_duplicates': self.browser_state['consecutive_duplicates'],
            'smart_navigation_enabled': self.browser_state['smart_navigation_enabled'],
            'anti_duplicate_radius': self.browser_state['anti_duplicate_radius'],
            'decks_state': {
                deck.value: {
                    'loaded': state['loaded'],
                    'track_id': state['track_id'],
                    'load_position': state['load_source_position'],
                    'playing': state['playing']
                }
                for deck, state in self.deck_states.items()
            }
        }

    def reset_browser_tracking(self) -> None:
        """Reset completo del tracking browser (utile per debug)"""
        logger.info("🔄 Resetting browser tracking...")
        self.browser_state['loaded_track_positions'].clear()
        self.browser_state['loaded_track_ids'].clear()
        self.browser_state['navigation_history'].clear()
        self.browser_state['consecutive_duplicates'] = 0
        self.browser_state['smart_navigation_enabled'] = True

        # Reset anche deck states
        for deck_state in self.deck_states.values():
            deck_state['track_id'] = None
            deck_state['load_source_position'] = None
            deck_state['loaded'] = False

        logger.info("✅ Browser tracking reset completed")

    # ==========================================
    # STATE SYNCHRONIZATION INTEGRATION
    # ==========================================

    def initialize_state_sync(self):
        """Inizializza sistema sincronizzazione stato"""
        try:
            from traktor_state_sync import create_state_synchronizer
            self.state_synchronizer = create_state_synchronizer(self)
            if self.sync_enabled:
                self.state_synchronizer.start_auto_sync()
            logger.info("✅ State synchronization system initialized")
        except ImportError:
            logger.warning("⚠️ State synchronization module not available")
        except Exception as e:
            logger.error(f"❌ Failed to initialize state synchronization: {e}")

    def verify_state_sync(self) -> Optional[Dict[str, Any]]:
        """Verifica manuale sincronizzazione stato"""
        if not self.state_synchronizer:
            logger.warning("⚠️ State synchronizer not initialized")
            return None

        try:
            report = self.state_synchronizer.verify_all_states()
            self.last_state_verification = time.time()

            # Convert dataclass to dict for JSON serialization
            return {
                'timestamp': report.timestamp,
                'overall_status': report.overall_sync_status.value,
                'total_discrepancies': report.total_discrepancies,
                'critical_issues': report.critical_issues,
                'recommendations': report.recommendations,
                'deck_states': {
                    deck_name: {
                        'sync_status': state.sync_status.value,
                        'discrepancies': state.discrepancies,
                        'internal_loaded': state.internal_loaded,
                        'internal_playing': state.internal_playing,
                        'traktor_loaded': state.traktor_loaded,
                        'traktor_playing': state.traktor_playing,
                        'traktor_bpm': state.traktor_bpm
                    }
                    for deck_name, state in report.deck_states.items()
                }
            }
        except Exception as e:
            logger.error(f"❌ State verification failed: {e}")
            return None

    def force_state_reset(self):
        """Reset forzato di tutti gli stati"""
        logger.info("🔄 Performing forced state reset...")

        # Reset browser tracking
        self.reset_browser_tracking()

        # Reset state synchronizer se disponibile
        if self.state_synchronizer:
            self.state_synchronizer.reset_all_sync_states()

        # Reset statistiche
        self.stats['commands_sent'] = 0
        self.stats['status_received'] = 0
        self.stats['errors'] = 0

        logger.info("✅ Forced state reset completed")

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Ottieni stato comprensivo sistema + sincronizzazione"""
        base_status = self.get_status()
        browser_status = self.get_browser_status()

        # Sync status se disponibile
        sync_status = None
        if self.state_synchronizer:
            sync_status = self.state_synchronizer.get_sync_status_summary()

        return {
            'traktor_status': {
                'deck_a_bpm': base_status.deck_a_bpm,
                'deck_b_bpm': base_status.deck_b_bpm,
                'deck_a_position': base_status.deck_a_position,
                'deck_b_position': base_status.deck_b_position,
                'crossfader_position': base_status.crossfader_position,
                'master_volume': base_status.master_volume,
                'ai_enabled': base_status.ai_enabled,
                'last_update': base_status.last_update
            },
            'browser_status': browser_status,
            'sync_status': sync_status,
            'connection_status': {
                'connected': self.connected,
                'midi_available': RTMIDI_AVAILABLE,
                'last_verification': self.last_state_verification,
                'sync_enabled': self.sync_enabled
            },
            'statistics': self.stats
        }

    def auto_verify_if_needed(self):
        """Verifica automatica stato se necessaria"""
        current_time = time.time()
        if (self.sync_enabled and
            current_time - self.last_state_verification > self.state_verification_interval):

            logger.debug("🔍 Performing automatic state verification...")
            self.verify_state_sync()

    def _enhanced_send_midi_command(self, channel: int, cc: int, value: int, description: str) -> bool:
        """Send MIDI command con verifica stato post-command"""
        # Send comando normale
        success = self._send_midi_command(channel, cc, value, description)

        # Se il comando ha successo e riguarda un cambio di stato, schedula verifica
        if success and any(keyword in description.lower() for keyword in ['play', 'load', 'cue']):
            # Verifica stato dopo breve delay per permettere a Traktor di rispondere
            threading.Timer(1.0, self.auto_verify_if_needed).start()

        return success

    def emergency_stop(self) -> bool:
        """EMERGENCY STOP - ferma tutto immediatamente"""
        channel, cc = self.MIDI_MAP['emergency_stop']
        success = self._send_midi_command(channel, cc, 127, "EMERGENCY STOP")

        # Anche volume master a zero
        channel, cc = self.MIDI_MAP['master_volume']
        self._send_midi_command(channel, cc, 0, "Master Volume OFF")

        logger.warning("🚨 EMERGENCY STOP attivato!")
        return success

    def enable_ai(self, enabled: bool) -> bool:
        """Abilita/disabilita controllo AI"""
        value = 127 if enabled else 0
        channel, cc = self.MIDI_MAP['ai_enable']
        return self._send_midi_command(channel, cc, value, f"AI {'ON' if enabled else 'OFF'}")

    def get_status(self) -> TraktorStatus:
        """Ottieni status corrente di Traktor"""
        return self.status

    def get_deck_state(self, deck: DeckID) -> Dict[str, bool]:
        """Ottieni stato specifico deck"""
        return self.deck_states[deck].copy()

    def is_deck_playing(self, deck: DeckID) -> bool:
        """Verifica se deck è in play"""
        return self.deck_states[deck]['playing']

    def is_deck_cued(self, deck: DeckID) -> bool:
        """Verifica se deck è cued"""
        return self.deck_states[deck]['cued']

    def mix_to_deck_b(self) -> bool:
        """Professional transition from A to B"""
        try:
            # Check if both decks have tracks
            if not self.deck_states[DeckID.A]['loaded'] or not self.deck_states[DeckID.B]['loaded']:
                logger.warning("Both decks must have tracks loaded for mixing")
                return False

            # Start playing B if not already
            if not self.deck_states[DeckID.B]['playing']:
                self.play_deck(DeckID.B)
                import time
                time.sleep(0.5)  # Let it stabilize

            # Gradual crossfade A → B
            crossfade_steps = [0.2, 0.4, 0.6, 0.8, 1.0]
            for position in crossfade_steps:
                self.set_crossfader(position)
                import time
                time.sleep(0.6)  # 600ms between steps

            logger.info("✅ Professional mix A→B completed")
            return True

        except Exception as e:
            logger.error(f"❌ Mix to deck B failed: {e}")
            return False

    def sync_decks(self, master_deck: DeckID, slave_deck: DeckID) -> bool:
        """Sync slave deck to master deck BPM"""
        try:
            # Send sync command to slave deck
            success = self.sync_deck(slave_deck)
            if success:
                logger.info(f"🎯 Deck {slave_deck.value} synced to {master_deck.value}")
            return success
        except Exception as e:
            logger.error(f"❌ Deck sync failed: {e}")
            return False

    def volume_balance_for_mixing(self, deck_a_vol: float = 0.8, deck_b_vol: float = 0.8) -> bool:
        """Professional volume balancing for mixing"""
        try:
            success_a = self.set_deck_volume(DeckID.A, deck_a_vol)
            success_b = self.set_deck_volume(DeckID.B, deck_b_vol)

            if success_a and success_b:
                logger.info(f"🔊 Volume balanced: A={deck_a_vol:.1f}, B={deck_b_vol:.1f}")
            return success_a and success_b
        except Exception as e:
            logger.error(f"❌ Volume balancing failed: {e}")
            return False

    def get_mixing_status(self) -> Dict[str, Any]:
        """Get comprehensive mixing status"""
        return {
            'deck_a_playing': self.deck_states[DeckID.A]['playing'],
            'deck_b_playing': self.deck_states[DeckID.B]['playing'],
            'deck_a_loaded': self.deck_states[DeckID.A]['loaded'],
            'deck_b_loaded': self.deck_states[DeckID.B]['loaded'],
            'ready_for_mixing': (
                self.deck_states[DeckID.A]['loaded'] and
                self.deck_states[DeckID.B]['loaded']
            ),
            'both_playing': (
                self.deck_states[DeckID.A]['playing'] and
                self.deck_states[DeckID.B]['playing']
            )
        }

    def get_stats(self) -> Dict[str, Any]:
        """Ottieni statistiche controller"""
        uptime = time.time() - self.stats['uptime_start']
        return {
            'connected': self.connected,
            'uptime_seconds': round(uptime, 1),
            'commands_sent': self.stats['commands_sent'],
            'status_received': self.stats['status_received'],
            'errors': self.stats['errors'],
            'status': self.status.to_dict() if hasattr(self.status, 'to_dict') else str(self.status)
        }

    def disconnect(self):
        """Disconnetti da Traktor"""
        logger.info("🛑 Disconnessione da Traktor...")

        self.running = False
        self.connected = False

        try:
            if self.midi_out:
                self.midi_out.close()
            if self.midi_in:
                self.midi_in.close()
        except:
            pass

        logger.info("✅ Disconnesso da Traktor")

# Factory function
def get_traktor_controller(config: DJConfig = None) -> TraktorController:
    """Ottieni controller Traktor configurato"""
    if config is None:
        from config import get_config
        config = get_config()

    return TraktorController(config)

# Test function
async def test_traktor_control():
    """Test controller Traktor"""
    from config import get_config

    config = get_config()
    controller = get_traktor_controller(config)

    print("🎛️ Test Traktor Controller")
    print("=" * 50)

    # Test connessione
    if not controller.connect():
        print("❌ Connessione fallita")
        return

    print("✅ Connesso a Traktor")

    # Test controlli base
    print("\n🧪 Test controlli base...")

    # Test volume
    controller.set_deck_volume(DeckID.A, 0.7)
    controller.set_deck_volume(DeckID.B, 0.6)

    # Test crossfader
    controller.set_crossfader(0.3)  # Verso A
    await asyncio.sleep(1)
    controller.set_crossfader(0.7)  # Verso B
    await asyncio.sleep(1)
    controller.set_crossfader(0.5)  # Centro

    # Test EQ
    controller.set_eq(DeckID.A, 'high', 0.7)
    controller.set_eq(DeckID.A, 'mid', 0.5)
    controller.set_eq(DeckID.A, 'low', 0.3)

    # Test transport
    controller.play_deck(DeckID.A)
    await asyncio.sleep(0.5)
    controller.sync_deck(DeckID.B)

    # Test FX
    controller.set_fx_drywet(1, 0.3)

    print("✅ Test controlli completato")

    # Mostra status
    print(f"\n📊 Status:")
    status = controller.get_status()
    print(f"   Deck A BPM: {status.deck_a_bpm:.1f}")
    print(f"   Deck B BPM: {status.deck_b_bpm:.1f}")
    print(f"   Crossfader: {status.crossfader_position}")

    # Statistiche
    print(f"\n📈 Statistiche:")
    stats = controller.get_stats()
    for key, value in stats.items():
        if key != 'status':
            print(f"   {key}: {value}")

    # Disconnetti
    controller.disconnect()
    print("\n👋 Test completato")

if __name__ == "__main__":
    asyncio.run(test_traktor_control())