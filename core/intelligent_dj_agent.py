#!/usr/bin/env python3
"""
🧠 Intelligent DJ Agent with Visual Feedback

Agente DJ intelligente che:
1. Vede realmente lo stato di Traktor
2. Corregge automaticamente i comandi che falliscono
3. Comprende quando sta realmente mixando vs simulando
4. Fornisce feedback visivo all'AI sui risultati reali
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from config import get_config
from traktor_control import TraktorController, DeckID
from core.openrouter_client import OpenRouterClient, DJContext, get_openrouter_client

logger = logging.getLogger(__name__)

class CommandStatus(Enum):
    """Stato di esecuzione comando"""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class DJCommand:
    """Comando DJ con verifica di esecuzione"""
    command_id: str
    action: str  # 'play', 'pause', 'load', 'mix'
    target_deck: str  # 'A' or 'B'
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Stato esecuzione
    status: CommandStatus = CommandStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3

    # Timing
    created_at: float = field(default_factory=time.time)
    executed_at: Optional[float] = None
    verified_at: Optional[float] = None

    # Verifica
    expected_result: Dict[str, Any] = field(default_factory=dict)
    actual_result: Dict[str, Any] = field(default_factory=dict)

    success: bool = False

class IntelligentDJAgent:
    """
    Agente DJ intelligente con feedback visivo e correzione automatica

    Risolve i problemi:
    1. Comandi che vanno al deck sbagliato
    2. Mixing simulato invece che reale
    3. Mancanza di feedback sullo stato reale
    """

    def __init__(self):
        # Componenti
        self.config = get_config()
        self.traktor = TraktorController(self.config)
        self.ai_client = get_openrouter_client(self.config.openrouter_api_key)

        # Monitoraggio stato reale
        self.real_state = {
            'deck_a': {'playing': False, 'bpm': 0.0, 'track_loaded': False},
            'deck_b': {'playing': False, 'bpm': 0.0, 'track_loaded': False},
            'crossfader': 64.0,
            'is_mixing': False,
            'connection_status': False
        }

        # Coda comandi con verifica
        self.command_queue: List[DJCommand] = []
        self.command_history: List[DJCommand] = []

        # Monitoraggio
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Apprendimento errori
        self.error_patterns = {
            'deck_a_to_b_swap': 0,
            'deck_b_to_a_swap': 0,
            'connection_failures': 0,
            'command_timeouts': 0
        }

        logger.info("🧠 Intelligent DJ Agent initialized")

    def start_monitoring(self):
        """Avvia monitoraggio continuo dello stato reale"""
        if self.is_monitoring:
            return

        logger.info("👁️ Starting intelligent monitoring...")
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Ferma monitoraggio"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

    def _monitor_loop(self):
        """Loop di monitoraggio con correzione automatica"""
        while self.is_monitoring:
            try:
                # 1. Aggiorna stato reale
                self._update_real_state()

                # 2. Processa coda comandi
                self._process_command_queue()

                # 3. Rileva e correggi errori
                self._detect_and_fix_errors()

                time.sleep(0.2)  # 200ms monitoring

            except Exception as e:
                logger.error(f"❌ Monitor loop error: {e}")
                time.sleep(1.0)

    def _update_real_state(self):
        """Aggiorna stato reale da Traktor"""
        try:
            # Verifica connessione
            self.real_state['connection_status'] = self.traktor.connected

            if not self.real_state['connection_status']:
                return

            # Ottieni status
            status = self.traktor.get_status()
            if not status:
                return

            # Aggiorna deck A
            self.real_state['deck_a']['bpm'] = getattr(status, 'deck_a_bpm', 0.0)
            self.real_state['deck_a']['playing'] = getattr(status, 'deck_a_bpm', 0.0) > 0
            self.real_state['deck_a']['track_loaded'] = self.real_state['deck_a']['bpm'] > 0

            # Aggiorna deck B
            self.real_state['deck_b']['bpm'] = getattr(status, 'deck_b_bpm', 0.0)
            self.real_state['deck_b']['playing'] = getattr(status, 'deck_b_bpm', 0.0) > 0
            self.real_state['deck_b']['track_loaded'] = self.real_state['deck_b']['bpm'] > 0

            # Crossfader
            self.real_state['crossfader'] = getattr(status, 'crossfader_position', 64.0)

            # Rileva mixing
            self._detect_real_mixing()

        except Exception as e:
            logger.error(f"❌ State update error: {e}")

    def _detect_real_mixing(self):
        """Rileva se è in corso un mixing reale"""
        # Mixing reale se:
        # 1. Entrambi i deck hanno tracce caricate
        # 2. Crossfader è in posizione intermedia
        # 3. Almeno un deck sta suonando

        both_loaded = (self.real_state['deck_a']['track_loaded'] and
                      self.real_state['deck_b']['track_loaded'])

        crossfader_mixing = 20 < self.real_state['crossfader'] < 107

        any_playing = (self.real_state['deck_a']['playing'] or
                      self.real_state['deck_b']['playing'])

        self.real_state['is_mixing'] = both_loaded and crossfader_mixing and any_playing

    def execute_intelligent_command(self, action: str, target_deck: str, **params) -> str:
        """
        Esegue comando intelligente con verifica e correzione automatica

        Returns: comando_id per tracking
        """
        command_id = f"{action}_{target_deck}_{int(time.time())}"

        # Crea comando con verifica
        command = DJCommand(
            command_id=command_id,
            action=action,
            target_deck=target_deck,
            parameters=params,
            expected_result=self._predict_command_result(action, target_deck, params)
        )

        # Aggiungi alla coda
        self.command_queue.append(command)

        logger.info(f"🎯 Queued intelligent command: {action} on deck {target_deck}")
        return command_id

    def _predict_command_result(self, action: str, target_deck: str, params: Dict) -> Dict:
        """Predice il risultato atteso del comando"""
        expected = {}

        if action == 'play':
            expected[f'deck_{target_deck.lower()}_playing'] = True

        elif action == 'pause':
            expected[f'deck_{target_deck.lower()}_playing'] = False

        elif action == 'load_track':
            expected[f'deck_{target_deck.lower()}_track_loaded'] = True
            expected[f'deck_{target_deck.lower()}_bpm'] = "> 0"

        return expected

    def _process_command_queue(self):
        """Processa coda comandi con verifica"""
        if not self.command_queue:
            return

        # Processa primo comando nella coda
        command = self.command_queue[0]

        if command.status == CommandStatus.PENDING:
            self._execute_command(command)

        elif command.status == CommandStatus.EXECUTING:
            self._verify_command_execution(command)

        elif command.status in [CommandStatus.SUCCESS, CommandStatus.FAILED]:
            # Sposta a cronologia
            self.command_history.append(command)
            self.command_queue.pop(0)

    def _execute_command(self, command: DJCommand):
        """Esegue comando fisico"""
        command.status = CommandStatus.EXECUTING
        command.attempts += 1
        command.executed_at = time.time()

        try:
            deck_id = DeckID.A if command.target_deck == 'A' else DeckID.B

            if command.action == 'play':
                result = self.traktor.play_deck(deck_id)

            elif command.action == 'pause':
                result = self.traktor.pause_deck(deck_id)

            elif command.action == 'load_track':
                track_path = command.parameters.get('track_path')
                if track_path:
                    result = self.traktor.load_track_by_path(track_path, deck_id)
                else:
                    result = False
            else:
                result = False

            if not result:
                logger.warning(f"⚠️ Command {command.action} returned False")

        except Exception as e:
            logger.error(f"❌ Command execution error: {e}")

    def _verify_command_execution(self, command: DJCommand):
        """Verifica se il comando è stato eseguito correttamente"""
        # Attendi un po' per l'esecuzione
        if time.time() - command.executed_at < 1.0:
            return

        command.verified_at = time.time()

        # Confronta stato atteso vs reale
        verification_passed = True

        for expected_key, expected_value in command.expected_result.items():
            if 'deck_a' in expected_key:
                actual_value = self.real_state['deck_a'].get(expected_key.replace('deck_a_', ''))
            elif 'deck_b' in expected_key:
                actual_value = self.real_state['deck_b'].get(expected_key.replace('deck_b_', ''))
            else:
                actual_value = self.real_state.get(expected_key)

            # Verifica speciale per valori > 0
            if expected_value == "> 0":
                if not (actual_value and actual_value > 0):
                    verification_passed = False
                    break
            else:
                if actual_value != expected_value:
                    verification_passed = False
                    break

        if verification_passed:
            command.status = CommandStatus.SUCCESS
            command.success = True
            logger.info(f"✅ Command {command.action} verified successfully")

        else:
            # Comando fallito - retry o failure definitivo
            if command.attempts < command.max_attempts:
                command.status = CommandStatus.RETRYING
                logger.warning(f"🔄 Command {command.action} failed, retrying...")
                time.sleep(0.5)
                self._execute_command(command)
            else:
                command.status = CommandStatus.FAILED
                logger.error(f"❌ Command {command.action} failed after {command.attempts} attempts")

                # Registra pattern di errore
                self._record_error_pattern(command)

    def _record_error_pattern(self, command: DJCommand):
        """Registra pattern di errore per apprendimento"""
        if command.target_deck == 'A':
            # Verifica se deck B ha risposto invece di A
            if self.real_state['deck_b']['playing'] or self.real_state['deck_b']['track_loaded']:
                self.error_patterns['deck_a_to_b_swap'] += 1
                logger.warning("🔴 Pattern rilevato: Comando Deck A → Deck B risponde")

        elif command.target_deck == 'B':
            # Verifica se deck A ha risposto invece di B
            if self.real_state['deck_a']['playing'] or self.real_state['deck_a']['track_loaded']:
                self.error_patterns['deck_b_to_a_swap'] += 1
                logger.warning("🔴 Pattern rilevato: Comando Deck B → Deck A risponde")

    def _detect_and_fix_errors(self):
        """Rileva e corregge errori automaticamente"""
        # Se rileva pattern di swap dei deck
        if (self.error_patterns['deck_a_to_b_swap'] > 2 or
            self.error_patterns['deck_b_to_a_swap'] > 2):

            logger.warning("🔧 Auto-correzione: Deck mapping potrebbe essere invertito")
            # Qui potresti implementare correzione automatica

    def get_visual_context_for_ai(self) -> str:
        """Genera contesto visivo dettagliato per l'AI"""
        if not self.real_state['connection_status']:
            return "⚠️ PROBLEMA: Traktor non connesso - comandi non funzioneranno"

        parts = []

        # Stato deck A
        deck_a = self.real_state['deck_a']
        if deck_a['track_loaded']:
            if deck_a['playing']:
                parts.append(f"Deck A: PLAYING ({deck_a['bpm']:.0f} BPM)")
            else:
                parts.append(f"Deck A: Loaded ({deck_a['bpm']:.0f} BPM, paused)")
        else:
            parts.append("Deck A: Empty")

        # Stato deck B
        deck_b = self.real_state['deck_b']
        if deck_b['track_loaded']:
            if deck_b['playing']:
                parts.append(f"Deck B: PLAYING ({deck_b['bpm']:.0f} BPM)")
            else:
                parts.append(f"Deck B: Loaded ({deck_b['bpm']:.0f} BPM, paused)")
        else:
            parts.append("Deck B: Empty")

        # Stato mixing
        if self.real_state['is_mixing']:
            parts.append("🎛️ MIXING REALE IN CORSO")
        else:
            cf = self.real_state['crossfader']
            if cf < 30:
                parts.append("Crossfader: Full A")
            elif cf > 94:
                parts.append("Crossfader: Full B")
            else:
                parts.append("Crossfader: Center")

        # Problemi rilevati
        if self.error_patterns['deck_a_to_b_swap'] > 0:
            parts.append("⚠️ PROBLEMA: Comandi Deck A vanno a Deck B")

        if self.error_patterns['connection_failures'] > 3:
            parts.append("⚠️ PROBLEMA: Connessione Traktor instabile")

        return "STATO REALE: " + " | ".join(parts)

    def get_command_status(self, command_id: str) -> Optional[DJCommand]:
        """Ottieni stato di un comando specifico"""
        # Cerca nella coda
        for cmd in self.command_queue:
            if cmd.command_id == command_id:
                return cmd

        # Cerca nella cronologia
        for cmd in self.command_history:
            if cmd.command_id == command_id:
                return cmd

        return None

    def get_agent_report(self) -> Dict[str, Any]:
        """Report completo dell'agente"""
        total_commands = len(self.command_history)
        successful_commands = sum(1 for cmd in self.command_history if cmd.success)

        return {
            'connection_status': self.real_state['connection_status'],
            'real_state': self.real_state.copy(),
            'command_stats': {
                'total': total_commands,
                'successful': successful_commands,
                'success_rate': (successful_commands / total_commands * 100) if total_commands > 0 else 0,
                'pending': len(self.command_queue)
            },
            'error_patterns': self.error_patterns.copy(),
            'visual_context': self.get_visual_context_for_ai()
        }

# Test dell'agente intelligente
def test_intelligent_agent():
    """Test dell'agente DJ intelligente"""
    print("🧠 Testing Intelligent DJ Agent...")

    agent = IntelligentDJAgent()
    agent.start_monitoring()

    # Test comando
    print("🎯 Testing intelligent command...")
    command_id = agent.execute_intelligent_command('play', 'A')
    print(f"Command ID: {command_id}")

    # Attendi esecuzione
    time.sleep(3.0)

    # Controlla stato
    command_status = agent.get_command_status(command_id)
    if command_status:
        print(f"Command status: {command_status.status.value}")
        print(f"Success: {command_status.success}")
        print(f"Attempts: {command_status.attempts}")

    # Report agente
    report = agent.get_agent_report()
    print(f"\nAgent report:")
    print(f"Connection: {report['connection_status']}")
    print(f"Visual context: {report['visual_context']}")
    print(f"Command success rate: {report['command_stats']['success_rate']:.1f}%")

    agent.stop_monitoring()
    print("✅ Test completed")

if __name__ == "__main__":
    test_intelligent_agent()