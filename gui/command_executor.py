#!/usr/bin/env python3
"""
🎛️ Command Executor with Verification
Sistema di esecuzione comandi MIDI con verifica feedback da Traktor
"""

import time
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

from traktor_control import TraktorController, DeckID

# Import MIDI Communication Monitor for enhanced tracking
try:
    from midi_communication_monitor import MIDICommunicationMonitor
    MIDI_MONITOR_AVAILABLE = True
except ImportError:
    MIDI_MONITOR_AVAILABLE = False
    MIDICommunicationMonitor = None

logger = logging.getLogger(__name__)

class CommandStatus(Enum):
    """Stati esecuzione comando"""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    VERIFYING = "verifying"

@dataclass
class CommandResult:
    """Risultato esecuzione comando"""
    status: CommandStatus
    command_name: str
    execution_time_ms: float
    verified: bool = False
    error: Optional[str] = None
    traktor_state_before: Optional[Dict] = None
    traktor_state_after: Optional[Dict] = None
    retry_count: int = 0

class CommandExecutor:
    """
    Esecutore comandi con verifica feedback
    """

    def __init__(self, traktor_controller: TraktorController, use_midi_monitor: bool = True):
        self.controller = traktor_controller
        self.last_command_result: Optional[CommandResult] = None
        self.command_history: list = []

        # Configurazione
        self.verification_delay = 0.5  # Secondi da aspettare prima di verificare
        self.verification_timeout = 3.0  # Secondi max per verifica
        self.max_retries = 2  # Numero max retry per comando fallito

        # Callbacks per feedback GUI
        self.on_command_start: Optional[Callable] = None
        self.on_command_success: Optional[Callable] = None
        self.on_command_failed: Optional[Callable] = None
        self.on_verification_status: Optional[Callable] = None

        # MIDI Communication Monitor (opzionale, per tracking avanzato)
        self.midi_monitor: Optional[MIDICommunicationMonitor] = None
        if use_midi_monitor and MIDI_MONITOR_AVAILABLE:
            try:
                self.midi_monitor = MIDICommunicationMonitor(traktor_controller)
                logger.info("✅ MIDI Communication Monitor enabled")
            except Exception as e:
                logger.warning(f"⚠️ Could not enable MIDI monitor: {e}")
                self.midi_monitor = None

    def execute_load_track(self, deck: DeckID, direction: str = "down") -> CommandResult:
        """
        Esegui load track con verifica completa
        """
        command_name = f"Load Track to Deck {deck.value}"
        logger.info(f"🎵 Executing: {command_name}")

        # Start MIDI monitor tracking if available
        if self.midi_monitor:
            self.midi_monitor.track_command(
                command_name=command_name,
                deck_id=deck.value,
                expected_state="loaded=True",
                timeout=self.verification_timeout
            )

        if self.on_command_start:
            self.on_command_start(command_name)

        start_time = time.time()

        # Cattura stato PRIMA del comando
        state_before = self._capture_deck_state(deck)

        # Esegui comando con retry logic
        success = False
        retry_count = 0
        last_error = None

        while not success and retry_count <= self.max_retries:
            try:
                if retry_count > 0:
                    logger.info(f"🔄 Retry {retry_count}/{self.max_retries}...")
                    time.sleep(0.5)  # Breve pausa tra retry

                success = self.controller.load_next_track_smart(deck, direction)

                if not success:
                    last_error = "Controller returned False"

            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ Exception during command: {e}")

            retry_count += 1

        execution_time_ms = (time.time() - start_time) * 1000

        if not success:
            # Mark MIDI monitor as failed
            if self.midi_monitor:
                self.midi_monitor.mark_failed(last_error or "Unknown error")

            result = CommandResult(
                status=CommandStatus.FAILED,
                command_name=command_name,
                execution_time_ms=execution_time_ms,
                verified=False,
                error=last_error,
                traktor_state_before=state_before,
                retry_count=retry_count - 1
            )

            if self.on_command_failed:
                self.on_command_failed(result)

            self.last_command_result = result
            self.command_history.append(result)
            return result

        # Comando inviato con successo - ORA VERIFICHIAMO
        logger.info(f"✅ MIDI command sent - VERIFYING with Traktor...")

        if self.on_verification_status:
            self.on_verification_status("Verifica caricamento in Traktor...")

        # Aspetta che Traktor processi il comando
        time.sleep(self.verification_delay)

        # Verifica stato DOPO comando
        verified, state_after = self._verify_load_track(deck, state_before)

        # Update MIDI monitor
        if self.midi_monitor:
            if verified:
                self.midi_monitor.mark_verified()
            else:
                # Check for timeout
                if not self.midi_monitor.check_timeout():
                    self.midi_monitor.mark_failed("Verification failed - track not loaded")

        result = CommandResult(
            status=CommandStatus.SUCCESS if verified else CommandStatus.FAILED,
            command_name=command_name,
            execution_time_ms=execution_time_ms,
            verified=verified,
            traktor_state_before=state_before,
            traktor_state_after=state_after,
            error=None if verified else "Verification failed - track not loaded in Traktor",
            retry_count=retry_count - 1
        )

        # Callback appropriato
        if verified and self.on_command_success:
            self.on_command_success(result)
        elif not verified and self.on_command_failed:
            self.on_command_failed(result)

        self.last_command_result = result
        self.command_history.append(result)

        return result

    def execute_play_deck(self, deck: DeckID) -> CommandResult:
        """
        Esegui play deck con verifica
        """
        command_name = f"Play Deck {deck.value}"
        logger.info(f"▶️ Executing: {command_name}")

        # Start MIDI monitor tracking
        if self.midi_monitor:
            self.midi_monitor.track_command(
                command_name=command_name,
                deck_id=deck.value,
                expected_state="playing=True",
                timeout=self.verification_timeout
            )

        if self.on_command_start:
            self.on_command_start(command_name)

        start_time = time.time()

        # Stato prima
        state_before = self._capture_deck_state(deck)

        # Esegui con retry
        success = False
        retry_count = 0
        last_error = None

        while not success and retry_count <= self.max_retries:
            try:
                if retry_count > 0:
                    logger.info(f"🔄 Retry {retry_count}/{self.max_retries}...")
                    time.sleep(0.3)

                success = self.controller.play_deck(deck)

                if not success:
                    last_error = "Controller returned False"

            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ Exception during command: {e}")

            retry_count += 1

        execution_time_ms = (time.time() - start_time) * 1000

        if not success:
            # Mark MIDI monitor as failed
            if self.midi_monitor:
                self.midi_monitor.mark_failed(last_error or "Unknown error")

            result = CommandResult(
                status=CommandStatus.FAILED,
                command_name=command_name,
                execution_time_ms=execution_time_ms,
                verified=False,
                error=last_error,
                traktor_state_before=state_before,
                retry_count=retry_count - 1
            )

            if self.on_command_failed:
                self.on_command_failed(result)

            self.last_command_result = result
            self.command_history.append(result)
            return result

        # Verifica esecuzione
        logger.info(f"✅ MIDI command sent - VERIFYING play status...")

        if self.on_verification_status:
            self.on_verification_status("Verifica riproduzione in Traktor...")

        time.sleep(self.verification_delay)

        verified, state_after = self._verify_play_deck(deck, state_before)

        # Update MIDI monitor
        if self.midi_monitor:
            if verified:
                self.midi_monitor.mark_verified()
            else:
                if not self.midi_monitor.check_timeout():
                    self.midi_monitor.mark_failed("Verification failed - deck not playing")

        result = CommandResult(
            status=CommandStatus.SUCCESS if verified else CommandStatus.FAILED,
            command_name=command_name,
            execution_time_ms=execution_time_ms,
            verified=verified,
            traktor_state_before=state_before,
            traktor_state_after=state_after,
            error=None if verified else "Verification failed - deck not playing in Traktor",
            retry_count=retry_count - 1
        )

        if verified and self.on_command_success:
            self.on_command_success(result)
        elif not verified and self.on_command_failed:
            self.on_command_failed(result)

        self.last_command_result = result
        self.command_history.append(result)

        return result

    def execute_crossfader(self, position: float) -> CommandResult:
        """
        Esegui crossfader move con verifica
        """
        command_name = f"Crossfader to {position:.2f}"
        logger.info(f"🎛️ Executing: {command_name}")

        if self.on_command_start:
            self.on_command_start(command_name)

        start_time = time.time()

        success = False
        retry_count = 0
        last_error = None

        while not success and retry_count <= self.max_retries:
            try:
                if retry_count > 0:
                    time.sleep(0.2)

                success = self.controller.set_crossfader(position)

                if not success:
                    last_error = "Controller returned False"

            except Exception as e:
                last_error = str(e)

            retry_count += 1

        execution_time_ms = (time.time() - start_time) * 1000

        # Per crossfader, assumiamo verifica positiva se comando non fallisce
        verified = success

        result = CommandResult(
            status=CommandStatus.SUCCESS if success else CommandStatus.FAILED,
            command_name=command_name,
            execution_time_ms=execution_time_ms,
            verified=verified,
            error=last_error if not success else None,
            retry_count=retry_count - 1
        )

        if success and self.on_command_success:
            self.on_command_success(result)
        elif not success and self.on_command_failed:
            self.on_command_failed(result)

        self.last_command_result = result
        self.command_history.append(result)

        return result

    def _capture_deck_state(self, deck: DeckID) -> Dict[str, Any]:
        """Cattura stato corrente del deck"""
        try:
            state = self.controller.deck_states.get(deck, {})
            return {
                'loaded': state.get('loaded', False),
                'playing': state.get('playing', False),
                'track_name': state.get('track_name'),
                'track_id': state.get('track_id'),
                'load_source_position': state.get('load_source_position'),
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"❌ Error capturing deck state: {e}")
            return {}

    def _verify_load_track(self, deck: DeckID, state_before: Dict) -> tuple[bool, Dict]:
        """
        Verifica che traccia sia effettivamente caricata in Traktor
        """
        try:
            # Cattura nuovo stato
            state_after = self._capture_deck_state(deck)

            # Verifica cambiamenti
            loaded_before = state_before.get('loaded', False)
            loaded_after = state_after.get('loaded', False)

            track_id_before = state_before.get('track_id')
            track_id_after = state_after.get('track_id')

            # Successo se:
            # 1. Ora è loaded (anche se lo era prima, potrebbe essere nuova traccia)
            # 2. Track ID è cambiato (nuova traccia)
            verified = loaded_after and (track_id_after != track_id_before or track_id_after is not None)

            logger.info(f"🔍 Verification: loaded_before={loaded_before}, loaded_after={loaded_after}")
            logger.info(f"🔍 Verification: track_id_before={track_id_before}, track_id_after={track_id_after}")
            logger.info(f"🔍 Verification result: {'✅ VERIFIED' if verified else '❌ NOT VERIFIED'}")

            return verified, state_after

        except Exception as e:
            logger.error(f"❌ Error during verification: {e}")
            return False, {}

    def _verify_play_deck(self, deck: DeckID, state_before: Dict) -> tuple[bool, Dict]:
        """
        Verifica che deck sia effettivamente in play
        """
        try:
            state_after = self._capture_deck_state(deck)

            playing_before = state_before.get('playing', False)
            playing_after = state_after.get('playing', False)

            # Successo se ora sta suonando
            verified = playing_after

            logger.info(f"🔍 Verification: playing_before={playing_before}, playing_after={playing_after}")
            logger.info(f"🔍 Verification result: {'✅ VERIFIED' if verified else '❌ NOT VERIFIED'}")

            return verified, state_after

        except Exception as e:
            logger.error(f"❌ Error during verification: {e}")
            return False, {}

    def get_last_result(self) -> Optional[CommandResult]:
        """Ottieni risultato ultimo comando"""
        return self.last_command_result

    def get_command_history(self, last_n: int = 10) -> list:
        """Ottieni cronologia comandi"""
        return self.command_history[-last_n:]

    def get_success_rate(self) -> float:
        """Calcola success rate comandi"""
        if not self.command_history:
            return 0.0

        successful = sum(1 for cmd in self.command_history if cmd.status == CommandStatus.SUCCESS and cmd.verified)
        return successful / len(self.command_history)

    def reset_history(self):
        """Reset cronologia"""
        self.command_history.clear()
        self.last_command_result = None
        if self.midi_monitor:
            self.midi_monitor.reset_stats()

    def get_midi_monitor_stats(self) -> Optional[Dict[str, Any]]:
        """
        Ottieni statistiche dal MIDI monitor
        Returns None se monitor non disponibile
        """
        if not self.midi_monitor:
            return None
        return self.midi_monitor.get_stats_summary()

    def get_midi_monitor_history(self, count: int = 10) -> list:
        """
        Ottieni cronologia comandi dal MIDI monitor
        """
        if not self.midi_monitor:
            return []
        return self.midi_monitor.get_recent_history(count)

if __name__ == "__main__":
    print("🎛️ Command Executor with Verification System")
    print("This module provides verified command execution for Traktor control")
    if MIDI_MONITOR_AVAILABLE:
        print("✅ MIDI Communication Monitor integration available")
    else:
        print("⚠️ MIDI Communication Monitor not available (optional)")