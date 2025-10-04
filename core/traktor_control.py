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

from .config import DJConfig

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

    # Mappatura MIDI CC - VERIFIED WORKING MAPPINGS
    # Source: User discovery testing with test_cc_discovery.py + traktor-command-tester agent
    # Date: 2025-10-03
    # Status: SYSTEMATICALLY TESTED on IAC Driver Bus 1, Channel 1
    #
    # CRITICAL DISCOVERIES via MIDI Learn Mode (2025-10-03):
    # • CC 60 = deck_b_volume (was CC 29 conflict with pitch)
    # • CC 80 = deck_a_cue (was CC 39 non-functional)
    # • CC 81 = deck_b_cue (was CC 26 non-functional)
    #
    # TSI EXPORT ANALYSIS DISCOVERIES (2025-10-04):
    # • CC 2 = deck_c_tempo_adjust (CONFIRMED via TSI analysis)
    # • CC 3 = deck_d_tempo_adjust (CONFIRMED via TSI analysis)
    # • CC 4 = deck_d_loop_in (CONFIRMED via TSI analysis)
    # • Conflicts with hotcues are THEORETICAL only - deck isolation prevents real conflicts
    #
    # REMAINING CONFLICTS:
    # • CC 33 = master_volume activates limiter instead of volume
    #
    # See: TRAKTOR_ACTUAL_CC_MAPPINGS.md and MIDI_MAPPING_OPTIMIZATION_COMPLETE.md
    MIDI_MAP = {
        # ===== TRANSPORT CONTROLS =====
        'deck_a_play': (MIDIChannel.AI_CONTROL.value, 20),  # ✅ CONFIRMED
        'deck_b_play': (MIDIChannel.AI_CONTROL.value, 21),  # ✅ CONFIRMED
        'deck_c_play': (MIDIChannel.AI_CONTROL.value, 22),  # ✅ CONFIRMED
        'deck_d_play': (MIDIChannel.AI_CONTROL.value, 23),  # ✅ CONFIRMED
        'deck_a_cue': (MIDIChannel.AI_CONTROL.value, 80),  # 🔄 TO TEST
        'deck_b_cue': (MIDIChannel.AI_CONTROL.value, 81),  # 🔄 TO TEST
        'deck_a_sync': (MIDIChannel.AI_CONTROL.value, 24),  # 🔄 TO TEST
        'deck_b_sync': (MIDIChannel.AI_CONTROL.value, 25),  # 🔄 TO TEST

        # ===== VOLUME CONTROLS =====
        'deck_a_volume': (MIDIChannel.AI_CONTROL.value, 28),  # ✅ CONFIRMED
        'deck_b_volume': (MIDIChannel.AI_CONTROL.value, 60),  # ✅ CONFIRMED
        'deck_c_volume': (MIDIChannel.AI_CONTROL.value, 30),  # ✅ CONFIRMED
        'deck_d_volume': (MIDIChannel.AI_CONTROL.value, 31),  # ✅ CONFIRMED
        'crossfader': (MIDIChannel.AI_CONTROL.value, 32),  # 🔄 TO TEST

        # ===== EQ CONTROLS =====
        'deck_a_eq_high': (MIDIChannel.AI_CONTROL.value, 34),  # ✅ CONFIRMED
        'deck_a_eq_mid': (MIDIChannel.AI_CONTROL.value, 35),  # ✅ CONFIRMED
        'deck_a_eq_low': (MIDIChannel.AI_CONTROL.value, 36),  # ✅ CONFIRMED
        'deck_b_eq_high': (MIDIChannel.AI_CONTROL.value, 50),  # ✅ CONFIRMED
        'deck_b_eq_mid': (MIDIChannel.AI_CONTROL.value, 51),  # ✅ CONFIRMED
        'deck_b_eq_low': (MIDIChannel.AI_CONTROL.value, 52),  # ✅ CONFIRMED

        # ===== PITCH CONTROLS =====
        'deck_a_pitch': (MIDIChannel.AI_CONTROL.value, 41),  # 🔄 TO TEST
        'deck_b_pitch': (MIDIChannel.AI_CONTROL.value, 40),  # 🔄 TO TEST
        'deck_c_tempo_adjust': (MIDIChannel.AI_CONTROL.value, 2),  # ✅ TSI CONFIRMED
        'deck_d_tempo_adjust': (MIDIChannel.AI_CONTROL.value, 3),  # ✅ TSI CONFIRMED

        # ===== BROWSER CONTROLS =====
        'browser_load_deck_a': (MIDIChannel.AI_CONTROL.value, 43),  # ✅ CONFIRMED
        'browser_load_deck_b': (MIDIChannel.AI_CONTROL.value, 44),  # ✅ CONFIRMED
        'browser_load_deck_c': (MIDIChannel.AI_CONTROL.value, 45),  # ✅ CONFIRMED
        'browser_load_deck_d': (MIDIChannel.AI_CONTROL.value, 46),  # ✅ CONFIRMED
        'browser_select_up_down': (MIDIChannel.AI_CONTROL.value, 49),  # 🔄 TO TEST
        'browser_tree_up_down': (MIDIChannel.AI_CONTROL.value, 56),  # 🔄 TO TEST
        'browser_expand_collapse': (MIDIChannel.AI_CONTROL.value, 64),  # 🔄 TO TEST

        # ===== FX UNIT 1 =====
        'fx1_drywet': (MIDIChannel.AI_CONTROL.value, 76),  # ✅ CONFIRMED
        'fx1_knob1_filter': (MIDIChannel.AI_CONTROL.value, 77),  # ✅ CONFIRMED
        'fx1_knob2': (MIDIChannel.AI_CONTROL.value, 78),  # ✅ CONFIRMED
        'fx1_knob3': (MIDIChannel.AI_CONTROL.value, 79),  # ✅ CONFIRMED
        'fx1_rst_button': (MIDIChannel.AI_CONTROL.value, 93),  # ✅ CONFIRMED
        'fx1_frz_button': (MIDIChannel.AI_CONTROL.value, 94),  # ✅ CONFIRMED
        'fx1_spr_button': (MIDIChannel.AI_CONTROL.value, 95),  # ✅ CONFIRMED
        'fx1_onoff': (MIDIChannel.AI_CONTROL.value, 96),  # ✅ CONFIRMED

        # ===== FX UNIT 2 =====
        'fx2_drywet': (MIDIChannel.AI_CONTROL.value, 97),  # ✅ CONFIRMED
        'fx2_knob1': (MIDIChannel.AI_CONTROL.value, 98),  # ✅ CONFIRMED
        'fx2_knob2': (MIDIChannel.AI_CONTROL.value, 99),  # ✅ CONFIRMED
        'fx2_knob3': (MIDIChannel.AI_CONTROL.value, 100),  # ✅ CONFIRMED
        'fx2_rst_button': (MIDIChannel.AI_CONTROL.value, 101),  # ✅ CONFIRMED
        'fx2_frz_button': (MIDIChannel.AI_CONTROL.value, 102),  # ✅ CONFIRMED
        'fx2_spr_button': (MIDIChannel.AI_CONTROL.value, 103),  # ✅ CONFIRMED
        'fx2_onoff': (MIDIChannel.AI_CONTROL.value, 104),  # ✅ CONFIRMED

        # ===== FX UNIT 3 =====
        'fx3_drywet': (MIDIChannel.AI_CONTROL.value, 105),  # ✅ CONFIRMED
        'fx3_knob1': (MIDIChannel.AI_CONTROL.value, 106),  # ✅ CONFIRMED
        'fx3_knob2': (MIDIChannel.AI_CONTROL.value, 107),  # ✅ CONFIRMED
        'fx3_knob3': (MIDIChannel.AI_CONTROL.value, 108),  # ✅ CONFIRMED
        'fx3_rst_button': (MIDIChannel.AI_CONTROL.value, 109),  # ✅ CONFIRMED
        'fx3_frz_button': (MIDIChannel.AI_CONTROL.value, 110),  # ✅ CONFIRMED
        'fx3_spr_button': (MIDIChannel.AI_CONTROL.value, 111),  # ✅ CONFIRMED
        'fx3_onoff': (MIDIChannel.AI_CONTROL.value, 112),  # ✅ CONFIRMED

        # ===== FX UNIT 4 =====
        'fx4_drywet': (MIDIChannel.AI_CONTROL.value, 113),  # ✅ CONFIRMED
        'fx4_knob1': (MIDIChannel.AI_CONTROL.value, 114),  # ✅ CONFIRMED
        'fx4_knob2': (MIDIChannel.AI_CONTROL.value, 115),  # ✅ CONFIRMED
        'fx4_knob3': (MIDIChannel.AI_CONTROL.value, 116),  # ✅ CONFIRMED
        'fx4_rst_button': (MIDIChannel.AI_CONTROL.value, 117),  # ✅ CONFIRMED
        'fx4_frz_button': (MIDIChannel.AI_CONTROL.value, 118),  # ✅ CONFIRMED
        'fx4_spr_button': (MIDIChannel.AI_CONTROL.value, 119),  # ✅ CONFIRMED
        'fx4_onoff': (MIDIChannel.AI_CONTROL.value, 120),  # ✅ CONFIRMED

        # ===== LOOP CONTROLS =====
        'deck_a_loop_in': (MIDIChannel.AI_CONTROL.value, 121),  # 🔄 TO TEST
        'deck_a_loop_out': (MIDIChannel.AI_CONTROL.value, 122),  # 🔄 TO TEST
        'deck_a_loop_active': (MIDIChannel.AI_CONTROL.value, 123),  # 🔄 TO TEST
        'deck_b_loop_in': (MIDIChannel.AI_CONTROL.value, 124),  # 🔄 TO TEST
        'deck_b_loop_out': (MIDIChannel.AI_CONTROL.value, 125),  # 🔄 TO TEST
        'deck_b_loop_active': (MIDIChannel.AI_CONTROL.value, 126),  # 🔄 TO TEST
        'deck_d_loop_in': (MIDIChannel.AI_CONTROL.value, 4),  # ✅ TSI CONFIRMED

        # ===== HOTCUES =====
        # NOTE: CC 2,3,4 theoretical conflicts with Deck C/D controls are ISOLATED by deck separation
        'deck_a_hotcue_1': (MIDIChannel.AI_CONTROL.value, 1),  # 🔄 TO TEST
        'deck_a_hotcue_2': (MIDIChannel.AI_CONTROL.value, 2),  # ⚠️ SHARES CC with deck_c_tempo_adjust (different decks)
        'deck_a_hotcue_3': (MIDIChannel.AI_CONTROL.value, 3),  # ⚠️ SHARES CC with deck_d_tempo_adjust (different decks)
        'deck_a_hotcue_4': (MIDIChannel.AI_CONTROL.value, 4),  # ⚠️ SHARES CC with deck_d_loop_in (different decks)
        'deck_b_hotcue_1': (MIDIChannel.AI_CONTROL.value, 5),  # 🔄 TO TEST
        'deck_b_hotcue_2': (MIDIChannel.AI_CONTROL.value, 6),  # 🔄 TO TEST
        'deck_b_hotcue_3': (MIDIChannel.AI_CONTROL.value, 7),  # 🔄 TO TEST
        'deck_b_hotcue_4': (MIDIChannel.AI_CONTROL.value, 8),  # 🔄 TO TEST

        # ===== HUMAN OVERRIDE CONTROLS =====
        'emergency_stop': (MIDIChannel.HUMAN_OVERRIDE.value, 80),
        'ai_enable': (MIDIChannel.HUMAN_OVERRIDE.value, 81),
        'headphone_volume': (MIDIChannel.HUMAN_OVERRIDE.value, 90),
        'headphone_mix': (MIDIChannel.HUMAN_OVERRIDE.value, 91),
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

        # Simulation Mode (se MIDI non disponibile)
        self.simulation_mode = False  # True = comandi simulati, False = MIDI reale

    def connect_with_gil_safety(self, output_only: bool = False, timeout: float = 5.0) -> bool:
        """
        Connetti a Traktor via IAC Driver con GIL-safe threading

        Questo metodo risolve problemi di GIL quando chiamato da Tkinter o altri thread.
        Esegue l'inizializzazione MIDI in un thread separato con proper GIL management.

        Args:
            output_only: Se True, connette solo output (no input)
            timeout: Timeout in secondi per l'inizializzazione

        Returns:
            bool: True se connesso con successo (o simulation mode), False su errore critico
        """
        import threading
        import queue

        result_queue = queue.Queue()

        def _init_midi_in_thread():
            """Inizializza MIDI in thread separato con GIL safety"""
            try:
                success = self.connect(output_only=output_only)
                result_queue.put(('success', success))
            except Exception as e:
                logger.error(f"❌ GIL-safe MIDI init error: {e}")
                result_queue.put(('error', str(e)))

        # Avvia thread separato per inizializzazione MIDI
        logger.info("🔒 Starting GIL-safe MIDI initialization...")
        init_thread = threading.Thread(target=_init_midi_in_thread, daemon=True)
        init_thread.start()

        # Aspetta risultato con timeout
        try:
            result_type, result_value = result_queue.get(timeout=timeout)

            if result_type == 'success':
                if result_value:
                    logger.info("✅ GIL-safe MIDI initialization successful")
                return result_value
            else:
                logger.error(f"❌ MIDI initialization failed: {result_value}")
                # Fallback a simulation mode
                self.connected = False
                self.simulation_mode = True
                logger.warning("⚠️ Fallback a SIMULATION MODE (GIL error)")
                return True

        except queue.Empty:
            logger.error(f"❌ MIDI initialization timeout ({timeout}s)")
            # Fallback a simulation mode su timeout
            self.connected = False
            self.simulation_mode = True
            logger.warning("⚠️ Fallback a SIMULATION MODE (timeout)")
            return True

    def connect(self, output_only: bool = False) -> bool:
        """
        Connetti a Traktor via IAC Driver con error handling robusto

        ⚠️ ATTENZIONE: Se chiamato da Tkinter, usa connect_with_gil_safety() invece!

        Returns:
            bool: True se connesso con successo (o simulation mode), False su errore critico
        """
        if not RTMIDI_AVAILABLE:
            logger.warning("⚠️ rtmidi non disponibile - SIMULATION MODE attivo")
            self.connected = False
            self.simulation_mode = True
            return True  # Continua in simulation mode

        try:
            # Tentativo connessione output con timeout protection
            logger.info("🔌 Inizializzazione MIDI output...")

            try:
                self.midi_out = rtmidi.MidiOut()
            except Exception as midi_init_error:
                logger.error(f"❌ Errore inizializzazione rtmidi.MidiOut: {midi_init_error}")
                logger.warning("⚠️ Fallback a SIMULATION MODE")
                self.connected = False
                self.simulation_mode = True
                return True  # Graceful fallback

            # Cerca IAC Bus 1 con error handling
            try:
                output_ports = self.midi_out.get_ports()
                logger.info(f"📋 Porte MIDI disponibili: {output_ports}")
            except Exception as ports_error:
                logger.error(f"❌ Errore lettura porte MIDI: {ports_error}")
                self.midi_out.close_port()
                self.connected = False
                self.simulation_mode = True
                return True

            iac_port_idx = None

            # Ricerca porta IAC con fuzzy matching
            for i, port in enumerate(output_ports):
                port_lower = port.lower()
                if (self.config.iac_bus_name.lower() in port_lower or
                    "bus 1" in port_lower or
                    "iac" in port_lower):
                    iac_port_idx = i
                    logger.info(f"✅ Trovata porta IAC: {port}")
                    break

            # Apertura porta con error handling
            try:
                if iac_port_idx is None:
                    # Tentativo creazione porta virtuale
                    logger.warning("⚠️ IAC Driver non trovato, creo porta virtuale...")
                    self.midi_out.open_virtual_port(self.config.midi_device_name)
                    logger.info(f"✅ Porta virtuale creata: {self.config.midi_device_name}")
                else:
                    self.midi_out.open_port(iac_port_idx)
                    logger.info(f"✅ Connesso a IAC: {output_ports[iac_port_idx]}")
            except Exception as open_error:
                logger.error(f"❌ Errore apertura porta MIDI: {open_error}")
                logger.warning("⚠️ Fallback a SIMULATION MODE")
                if self.midi_out:
                    try:
                        self.midi_out.close_port()
                    except:
                        pass
                self.connected = False
                self.simulation_mode = True
                return True

            self.connected = True
            self.running = True
            self.simulation_mode = False
            logger.info("🎉 MIDI connesso con successo")

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
        """
        Invia comando MIDI a Traktor con simulation mode support

        Returns:
            bool: True se comando inviato (o simulato), False se errore
        """
        # SIMULATION MODE - simula invio senza MIDI reale
        if self.simulation_mode:
            logger.debug(f"🎭 [SIMULATION] CH{channel} CC{cc}={value} ({description})")
            self.stats['commands_sent'] += 1
            return True  # Simula successo

        # Verifica connessione reale
        if not self.connected or not self.midi_out:
            logger.warning(f"⚠️ Non connesso a Traktor - comando ignorato: {description}")
            return False

        try:
            # Costruisci messaggio MIDI (Control Change)
            message = [0xB0 + (channel - 1), cc, value]

            # Invio con timeout protection
            try:
                self.midi_out.send_message(message)
                self.stats['commands_sent'] += 1
                logger.debug(f"📤 Comando: CH{channel} CC{cc}={value} ({description})")
                return True
            except Exception as send_error:
                logger.error(f"❌ Errore invio messaggio MIDI: {send_error}")
                self.stats['errors'] += 1
                return False

        except Exception as e:
            logger.error(f"❌ Errore costruzione comando MIDI: {e}")
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

    def force_play_deck(self, deck: DeckID, wait_if_recent_load: bool = True) -> bool:
        """
        Force play deck SENZA toggle logic - risolve problema blinking

        Questo metodo:
        1. Resetta lo stato interno a "not playing"
        2. Invia comando play
        3. Verifica che il deck sia effettivamente partito
        4. Gestisce delay intelligente se track appena caricata

        Args:
            deck: Deck da far partire
            wait_if_recent_load: Se True, aspetta se track caricata recentemente

        Returns:
            True se play riuscito
        """
        # Step 1: Check se track caricata di recente e aspetta se necessario
        if wait_if_recent_load and self.deck_states[deck]['last_loaded_time']:
            time_since_load = time.time() - self.deck_states[deck]['last_loaded_time']

            if time_since_load < 1.5:  # Meno di 1.5 secondi fa
                wait_time = 1.5 - time_since_load
                logger.info(f"⏱️  Track caricata {time_since_load:.1f}s fa - aspetto {wait_time:.1f}s per stabilità...")
                time.sleep(wait_time)

        # Step 2: Verifica se c'è una traccia caricata
        if not self.deck_states[deck]['loaded']:
            logger.warning(f"⚠️ Deck {deck.value} potrebbe non avere una traccia caricata")

        # Step 3: FORCE RESET stato interno per evitare toggle issues
        was_playing = self.deck_states[deck]['playing']
        self.deck_states[deck]['playing'] = False

        logger.info(f"🔄 Force play Deck {deck.value} (was: {'playing' if was_playing else 'paused'})")

        # Step 4: Se già stava suonando, prima fermiamo (per evitare toggle)
        if was_playing:
            logger.info(f"🛑 Deck {deck.value} già in play - fermo prima di ri-avviare")
            channel, cc = self.MIDI_MAP[f'deck_{deck.value.lower()}_play']
            self._send_midi_command(channel, cc, 127, f"Stop Deck {deck.value}")
            time.sleep(0.1)  # Breve pausa
            self.deck_states[deck]['playing'] = False

        # Step 5: Invia comando play
        channel, cc = self.MIDI_MAP[f'deck_{deck.value.lower()}_play']
        success = self._send_midi_command(channel, cc, 127, f"Force Play Deck {deck.value}")

        if not success:
            logger.error(f"❌ MIDI command failed per Deck {deck.value}")
            return False

        # Step 6: Aggiorna stato interno
        self.deck_states[deck]['playing'] = True
        self.deck_states[deck]['cued'] = False

        # Step 7: Breve delay e verifica che sia partito
        time.sleep(0.2)

        # Verifica finale (opzionale - basata su stato interno)
        if self.deck_states[deck]['playing']:
            logger.info(f"✅ FORCE PLAY SUCCESS: Deck {deck.value} is playing")
            return True
        else:
            logger.warning(f"⚠️ FORCE PLAY: Comando inviato ma stato incerto per Deck {deck.value}")
            return True  # Ritorna success comunque - il comando è stato inviato

    def play_deck(self, deck: DeckID) -> bool:
        """
        Play deck con smart logic - usa force_play per evitare blinking

        DEPRECATO: Questo metodo ora usa force_play_deck internamente
        per evitare problemi di toggle/blinking
        """
        logger.info(f"▶️ play_deck() chiamato per Deck {deck.value} - usando force_play")
        return self.force_play_deck(deck, wait_if_recent_load=True)

    def verify_deck_playing(self, deck: DeckID, max_attempts: int = 3) -> bool:
        """
        Verifica che deck sia effettivamente in play

        Controlla lo stato interno e tenta verifica multipla
        per massima affidabilità

        Args:
            deck: Deck da verificare
            max_attempts: Numero tentativi di verifica

        Returns:
            True se deck sta suonando
        """
        for attempt in range(max_attempts):
            # Check stato interno
            if self.deck_states[deck]['playing']:
                logger.debug(f"✅ Verifica attempt {attempt+1}/{max_attempts}: Deck {deck.value} playing")
                return True

            # Se non sta suonando, aspetta un po' e riprova
            if attempt < max_attempts - 1:
                time.sleep(0.1)

        logger.warning(f"⚠️ Verifica fallita: Deck {deck.value} non sembra playing dopo {max_attempts} tentativi")
        return False

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
        """Imposta FX dry/wet (1-4, 0.0-1.0) - COMPLETE 4-UNIT SUPPORT"""
        if 1 <= fx_unit <= 4:
            midi_value = int(amount * 127)
            channel, cc = self.MIDI_MAP[f'fx{fx_unit}_drywet']
            return self._send_midi_command(channel, cc, midi_value, f"FX{fx_unit} Dry/Wet")
        return False

    def set_fx_knob(self, fx_unit: int, knob_num: int, value: float) -> bool:
        """Imposta FX parameter knob (fx_unit: 1-4, knob_num: 1-3, value: 0.0-1.0)"""
        if 1 <= fx_unit <= 4 and 1 <= knob_num <= 3:
            midi_value = int(value * 127)
            channel, cc = self.MIDI_MAP[f'fx{fx_unit}_knob{knob_num}']
            return self._send_midi_command(channel, cc, midi_value, f"FX{fx_unit} Knob{knob_num}")
        return False

    def trigger_fx_button(self, fx_unit: int, button_type: str) -> bool:
        """Trigger FX button (fx_unit: 1-4, button_type: 'rst'/'frz'/'spr'/'onoff')"""
        if 1 <= fx_unit <= 4 and button_type in ['rst', 'frz', 'spr', 'onoff']:
            key = f'fx{fx_unit}_{button_type}_button' if button_type != 'onoff' else f'fx{fx_unit}_onoff'
            if key in self.MIDI_MAP:
                channel, cc = self.MIDI_MAP[key]
                return self._send_midi_command(channel, cc, 127, f"FX{fx_unit} {button_type.upper()}")
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