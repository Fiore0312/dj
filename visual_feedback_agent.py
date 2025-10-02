#!/usr/bin/env python3
"""
👁️ Visual Feedback Agent for DJ AI

Agente che "vede" realmente lo stato di Traktor tramite:
- Feedback MIDI in tempo reale
- Verifica comandi eseguiti vs comandati
- Correzione automatica errori
- Stato visivo delle tracce e deck
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

from traktor_control import TraktorController, DeckID
from core.openrouter_client import OpenRouterClient, DJContext

logger = logging.getLogger(__name__)

class DeckState(Enum):
    """Stato reale del deck"""
    EMPTY = "empty"
    LOADED = "loaded"
    PLAYING = "playing"
    PAUSED = "paused"
    CUEING = "cueing"

@dataclass
class RealDeckStatus:
    """Stato reale verificato di un deck"""
    deck_id: str
    state: DeckState = DeckState.EMPTY
    track_loaded: Optional[str] = None
    is_playing: bool = False
    bpm: float = 0.0
    position: float = 0.0
    volume: float = 0.0
    last_updated: float = field(default_factory=time.time)

    # Verifica comandi
    last_command: Optional[str] = None
    command_executed: bool = False
    command_timestamp: float = 0.0

@dataclass
class MixerStatus:
    """Stato reale del mixer"""
    crossfader: float = 64.0  # 0=A, 127=B, 64=center
    master_volume: float = 100.0
    deck_a_volume: float = 100.0
    deck_b_volume: float = 100.0
    is_mixing: bool = False
    mix_start_time: Optional[float] = None

class VisualFeedbackAgent:
    """
    Agente che monitora visivamente lo stato reale di Traktor
    e corregge automaticamente i comandi che non vengono eseguiti
    """

    def __init__(self):
        self.traktor = TraktorController()
        self.ai_client = OpenRouterClient()

        # Stato reale monitorato
        self.deck_a = RealDeckStatus("A")
        self.deck_b = RealDeckStatus("B")
        self.mixer = MixerStatus()

        # Monitoraggio
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.feedback_interval = 0.1  # 100ms feedback rate

        # Correzione errori
        self.correction_enabled = True
        self.max_retries = 3
        self.command_timeout = 2.0  # Secondi per considerare comando fallito

        # Storico per apprendimento
        self.command_history: List[Dict] = []
        self.error_patterns: Dict[str, int] = {}

        logger.info("👁️ Visual Feedback Agent initialized")

    def start_monitoring(self):
        """Avvia monitoraggio continuo dello stato reale"""
        if self.is_monitoring:
            return

        logger.info("🔄 Starting visual monitoring...")
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Ferma monitoraggio"""
        logger.info("🛑 Stopping visual monitoring...")
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

    def _monitor_loop(self):
        """Loop principale di monitoraggio"""
        while self.is_monitoring:
            try:
                # Aggiorna stato reale
                self._update_real_status()

                # Verifica comandi pendenti
                self._verify_pending_commands()

                # Correggi errori se necessario
                if self.correction_enabled:
                    self._auto_correct_errors()

                time.sleep(self.feedback_interval)

            except Exception as e:
                logger.error(f"❌ Monitor loop error: {e}")
                time.sleep(1.0)

    def _update_real_status(self):
        """Aggiorna lo stato reale dei deck tramite feedback MIDI"""
        try:
            # Ottieni status da Traktor
            status = self.traktor.get_status()
            if not status:
                return

            current_time = time.time()

            # Aggiorna Deck A
            self.deck_a.bpm = status.get('deck_a_bpm', 0.0)
            self.deck_a.is_playing = status.get('deck_a_playing', False)
            self.deck_a.position = status.get('deck_a_position', 0.0)
            self.deck_a.volume = status.get('deck_a_volume', 0.0)

            # Determina stato Deck A
            if self.deck_a.bpm > 0:
                if self.deck_a.is_playing:
                    self.deck_a.state = DeckState.PLAYING
                else:
                    self.deck_a.state = DeckState.LOADED
            else:
                self.deck_a.state = DeckState.EMPTY

            # Aggiorna Deck B
            self.deck_b.bpm = status.get('deck_b_bpm', 0.0)
            self.deck_b.is_playing = status.get('deck_b_playing', False)
            self.deck_b.position = status.get('deck_b_position', 0.0)
            self.deck_b.volume = status.get('deck_b_volume', 0.0)

            # Determina stato Deck B
            if self.deck_b.bpm > 0:
                if self.deck_b.is_playing:
                    self.deck_b.state = DeckState.PLAYING
                else:
                    self.deck_b.state = DeckState.LOADED
            else:
                self.deck_b.state = DeckState.EMPTY

            # Aggiorna mixer
            self.mixer.crossfader = status.get('crossfader', 64.0)
            self.mixer.deck_a_volume = status.get('deck_a_volume', 100.0)
            self.mixer.deck_b_volume = status.get('deck_b_volume', 100.0)

            # Rileva mixing attivo
            self._detect_active_mixing()

            # Aggiorna timestamp
            self.deck_a.last_updated = current_time
            self.deck_b.last_updated = current_time

        except Exception as e:
            logger.error(f"❌ Status update failed: {e}")

    def _detect_active_mixing(self):
        """Rileva se è in corso un mixing reale"""
        # Mixing attivo se:
        # 1. Entrambi i deck hanno tracce
        # 2. Crossfader non è completamente su un lato
        # 3. Almeno un deck sta suonando

        both_loaded = (self.deck_a.state in [DeckState.LOADED, DeckState.PLAYING] and
                      self.deck_b.state in [DeckState.LOADED, DeckState.PLAYING])

        crossfader_mixing = 10 < self.mixer.crossfader < 117  # Non agli estremi

        at_least_one_playing = self.deck_a.is_playing or self.deck_b.is_playing

        was_mixing = self.mixer.is_mixing
        self.mixer.is_mixing = both_loaded and crossfader_mixing and at_least_one_playing

        # Segna inizio mixing
        if self.mixer.is_mixing and not was_mixing:
            self.mixer.mix_start_time = time.time()
            logger.info("🎛️ Real mixing detected - started")
        elif not self.mixer.is_mixing and was_mixing:
            mix_duration = time.time() - (self.mixer.mix_start_time or 0)
            logger.info(f"🎛️ Real mixing completed - duration: {mix_duration:.1f}s")

    def execute_verified_command(self, command: str, target_deck: str, **params) -> bool:
        """
        Esegue comando e verifica che sia stato realmente eseguito
        """
        logger.info(f"🎯 Executing verified command: {command} on deck {target_deck}")

        # Registra comando
        command_info = {
            'command': command,
            'deck': target_deck,
            'params': params,
            'timestamp': time.time(),
            'attempts': 0,
            'success': False
        }

        deck_status = self.deck_a if target_deck == "A" else self.deck_b
        deck_id = DeckID.A if target_deck == "A" else DeckID.B

        for attempt in range(self.max_retries):
            command_info['attempts'] = attempt + 1

            # Salva stato pre-comando
            pre_state = {
                'playing': deck_status.is_playing,
                'bpm': deck_status.bpm,
                'state': deck_status.state
            }

            # Esegui comando
            success = False
            if command == 'play':
                success = self.traktor.play_deck(deck_id)
            elif command == 'pause':
                success = self.traktor.pause_deck(deck_id)
            elif command == 'load_track':
                track_path = params.get('track_path')
                if track_path:
                    success = self.traktor.load_track_by_path(track_path, deck_id)
            elif command == 'stop':
                success = self.traktor.stop_deck(deck_id)

            if not success:
                logger.warning(f"⚠️ Command {command} returned False on attempt {attempt + 1}")
                continue

            # Attendi e verifica esecuzione
            time.sleep(0.5)  # Attendi esecuzione comando
            self._update_real_status()  # Forza aggiornamento stato

            # Verifica se comando è stato eseguito
            verified = self._verify_command_execution(command, target_deck, pre_state)

            if verified:
                logger.info(f"✅ Command {command} verified on deck {target_deck} (attempt {attempt + 1})")
                command_info['success'] = True
                break
            else:
                logger.warning(f"❌ Command {command} not verified on attempt {attempt + 1}")
                time.sleep(0.5)  # Pausa prima del retry

        # Registra nel history
        self.command_history.append(command_info)

        # Aggiorna pattern di errore
        if not command_info['success']:
            error_key = f"{command}_{target_deck}"
            self.error_patterns[error_key] = self.error_patterns.get(error_key, 0) + 1
            logger.error(f"❌ Command {command} failed after {self.max_retries} attempts on deck {target_deck}")

        return command_info['success']

    def _verify_command_execution(self, command: str, target_deck: str, pre_state: Dict) -> bool:
        """Verifica se il comando è stato realmente eseguito"""
        deck_status = self.deck_a if target_deck == "A" else self.deck_b

        if command == 'play':
            # Verifica che il deck stia suonando
            return deck_status.is_playing and not pre_state['playing']

        elif command == 'pause':
            # Verifica che il deck sia in pausa
            return not deck_status.is_playing and pre_state['playing']

        elif command == 'load_track':
            # Verifica che il BPM sia cambiato (traccia caricata)
            return deck_status.bpm > 0 and deck_status.bpm != pre_state['bpm']

        elif command == 'stop':
            # Verifica che il deck sia fermato
            return not deck_status.is_playing

        return False

    def _verify_pending_commands(self):
        """Verifica comandi pendenti che potrebbero non essere stati eseguiti"""
        current_time = time.time()

        for deck_status in [self.deck_a, self.deck_b]:
            if (deck_status.last_command and
                not deck_status.command_executed and
                current_time - deck_status.command_timestamp > self.command_timeout):

                logger.warning(f"⏰ Command timeout on deck {deck_status.deck_id}: {deck_status.last_command}")
                deck_status.last_command = None

    def _auto_correct_errors(self):
        """Correzione automatica degli errori rilevati"""
        # Esempio: se un deck dovrebbe suonare ma non suona
        if (self.deck_a.last_command == 'play' and
            not self.deck_a.is_playing and
            self.deck_a.state == DeckState.LOADED):

            logger.info("🔧 Auto-correcting: Deck A should be playing")
            self.traktor.play_deck(DeckID.A)

    def get_real_status_report(self) -> Dict[str, Any]:
        """Ottieni report completo dello stato reale"""
        return {
            'timestamp': time.time(),
            'deck_a': {
                'state': self.deck_a.state.value,
                'playing': self.deck_a.is_playing,
                'bpm': self.deck_a.bpm,
                'position': self.deck_a.position,
                'volume': self.deck_a.volume,
                'track_loaded': self.deck_a.track_loaded
            },
            'deck_b': {
                'state': self.deck_b.state.value,
                'playing': self.deck_b.is_playing,
                'bpm': self.deck_b.bpm,
                'position': self.deck_b.position,
                'volume': self.deck_b.volume,
                'track_loaded': self.deck_b.track_loaded
            },
            'mixer': {
                'crossfader': self.mixer.crossfader,
                'is_mixing': self.mixer.is_mixing,
                'mixing_duration': time.time() - (self.mixer.mix_start_time or time.time()) if self.mixer.is_mixing else 0
            },
            'monitoring': {
                'is_active': self.is_monitoring,
                'command_success_rate': self._calculate_success_rate(),
                'common_errors': dict(list(self.error_patterns.items())[:5])
            }
        }

    def _calculate_success_rate(self) -> float:
        """Calcola tasso di successo comandi"""
        if not self.command_history:
            return 1.0

        successful = sum(1 for cmd in self.command_history if cmd['success'])
        return successful / len(self.command_history)

    def get_ai_visual_context(self) -> str:
        """Genera contesto visivo per l'AI che descrive cosa sta realmente accadendo"""
        status = self.get_real_status_report()

        context_parts = []

        # Stato deck
        deck_a_desc = f"Deck A: {status['deck_a']['state']}"
        if status['deck_a']['playing']:
            deck_a_desc += f" (PLAYING at {status['deck_a']['bpm']:.0f} BPM)"
        elif status['deck_a']['bpm'] > 0:
            deck_a_desc += f" (loaded, {status['deck_a']['bpm']:.0f} BPM)"

        deck_b_desc = f"Deck B: {status['deck_b']['state']}"
        if status['deck_b']['playing']:
            deck_b_desc += f" (PLAYING at {status['deck_b']['bpm']:.0f} BPM)"
        elif status['deck_b']['bpm'] > 0:
            deck_b_desc += f" (loaded, {status['deck_b']['bpm']:.0f} BPM)"

        context_parts.extend([deck_a_desc, deck_b_desc])

        # Stato mixing
        if status['mixer']['is_mixing']:
            mix_duration = status['mixer']['mixing_duration']
            context_parts.append(f"MIXING ACTIVE (duration: {mix_duration:.1f}s)")
        else:
            cf_pos = "center" if 50 < status['mixer']['crossfader'] < 77 else ("A" if status['mixer']['crossfader'] < 50 else "B")
            context_parts.append(f"Crossfader: {cf_pos}")

        # Stato monitoraggio
        success_rate = status['monitoring']['command_success_rate'] * 100
        context_parts.append(f"Command success: {success_rate:.0f}%")

        return "REAL STATE: " + " | ".join(context_parts)

# Test del visual feedback agent
def test_visual_feedback():
    """Test del sistema di feedback visivo"""
    print("👁️ Testing Visual Feedback Agent...")

    agent = VisualFeedbackAgent()

    # Avvia monitoraggio
    agent.start_monitoring()
    print("✅ Monitoring started")

    # Test stato iniziale
    time.sleep(1.0)
    initial_status = agent.get_real_status_report()
    print(f"📊 Initial status: {json.dumps(initial_status, indent=2)}")

    # Test contesto AI
    ai_context = agent.get_ai_visual_context()
    print(f"🤖 AI Context: {ai_context}")

    # Test comando verificato
    print("\n🎯 Testing verified command execution...")
    success = agent.execute_verified_command('play', 'A')
    print(f"Command success: {success}")

    # Attendi e controlla stato finale
    time.sleep(2.0)
    final_status = agent.get_real_status_report()
    print(f"📊 Final status: {json.dumps(final_status, indent=2)}")

    # Ferma monitoraggio
    agent.stop_monitoring()
    print("✅ Test completed")

if __name__ == "__main__":
    test_visual_feedback()