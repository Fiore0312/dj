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

    # Mappatura MIDI CC per controlli principali
    MIDI_MAP = {
        # Volume faders (AI Control - Channel 1)
        'deck_a_volume': (MIDIChannel.AI_CONTROL.value, 7),
        'deck_b_volume': (MIDIChannel.AI_CONTROL.value, 8),
        'deck_c_volume': (MIDIChannel.AI_CONTROL.value, 9),
        'deck_d_volume': (MIDIChannel.AI_CONTROL.value, 10),

        # Crossfader
        'crossfader': (MIDIChannel.AI_CONTROL.value, 11),

        # EQ Controls
        'deck_a_eq_high': (MIDIChannel.AI_CONTROL.value, 12),
        'deck_a_eq_mid': (MIDIChannel.AI_CONTROL.value, 13),
        'deck_a_eq_low': (MIDIChannel.AI_CONTROL.value, 14),
        'deck_b_eq_high': (MIDIChannel.AI_CONTROL.value, 15),
        'deck_b_eq_mid': (MIDIChannel.AI_CONTROL.value, 16),
        'deck_b_eq_low': (MIDIChannel.AI_CONTROL.value, 17),

        # Transport Controls
        'deck_a_play': (MIDIChannel.AI_CONTROL.value, 20),
        'deck_b_play': (MIDIChannel.AI_CONTROL.value, 21),
        'deck_c_play': (MIDIChannel.AI_CONTROL.value, 22),
        'deck_d_play': (MIDIChannel.AI_CONTROL.value, 23),

        'deck_a_cue': (MIDIChannel.AI_CONTROL.value, 24),
        'deck_b_cue': (MIDIChannel.AI_CONTROL.value, 25),
        'deck_c_cue': (MIDIChannel.AI_CONTROL.value, 26),
        'deck_d_cue': (MIDIChannel.AI_CONTROL.value, 27),

        'deck_a_sync': (MIDIChannel.AI_CONTROL.value, 28),
        'deck_b_sync': (MIDIChannel.AI_CONTROL.value, 29),
        'deck_c_sync': (MIDIChannel.AI_CONTROL.value, 30),
        'deck_d_sync': (MIDIChannel.AI_CONTROL.value, 31),

        # Human Override (Channel 3)
        'emergency_stop': (MIDIChannel.HUMAN_OVERRIDE.value, 80),
        'ai_enable': (MIDIChannel.HUMAN_OVERRIDE.value, 81),
        'master_volume': (MIDIChannel.HUMAN_OVERRIDE.value, 85),
        'headphone_volume': (MIDIChannel.HUMAN_OVERRIDE.value, 90),
        'headphone_mix': (MIDIChannel.HUMAN_OVERRIDE.value, 91),

        # Effects (Channel 4)
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
            DeckID.A: {'playing': False, 'cued': False},
            DeckID.B: {'playing': False, 'cued': False},
            DeckID.C: {'playing': False, 'cued': False},
            DeckID.D: {'playing': False, 'cued': False},
        }

        # Statistiche
        self.stats = {
            'commands_sent': 0,
            'status_received': 0,
            'errors': 0,
            'uptime_start': time.time()
        }

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
        """Play deck (se già in play, non fa nulla)"""
        if self.deck_states[deck]['playing']:
            logger.debug(f"Deck {deck.value} già in play")
            return True

        return self.toggle_play_pause(deck)

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