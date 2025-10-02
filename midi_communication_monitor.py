#!/usr/bin/env python3
"""
📡 MIDI Communication Monitor - Sistema Leggero di Verifica
Monitoraggio semplice e pratico della comunicazione GUI-Traktor
"""

import time
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CommandStatus(Enum):
    """Stati comando semplificati"""
    SENT = "sent"           # Comando inviato via MIDI
    WAITING = "waiting"     # Attesa risposta Traktor
    VERIFIED = "verified"   # State aggiornato come atteso
    TIMEOUT = "timeout"     # Timeout - Traktor non ha risposto
    FAILED = "failed"       # Errore invio MIDI

@dataclass
class CommandTracking:
    """Tracking semplice di un comando"""
    command_name: str
    deck_id: Optional[str] = None
    timestamp: float = 0.0
    status: CommandStatus = CommandStatus.SENT
    timeout_seconds: float = 2.0
    expected_state_change: Optional[str] = None  # es. "loaded=True"

class MIDICommunicationMonitor:
    """
    Monitor leggero per comunicazione MIDI
    Approccio pratico: delay + timeout detection
    """

    def __init__(self, traktor_controller):
        self.controller = traktor_controller
        self.current_command: Optional[CommandTracking] = None
        self.command_history: list = []
        self.max_history = 50

        # Callbacks per GUI
        self.on_command_sent: Optional[Callable] = None
        self.on_command_verified: Optional[Callable] = None
        self.on_command_timeout: Optional[Callable] = None
        self.on_command_failed: Optional[Callable] = None

        # Statistics
        self.stats = {
            'total_sent': 0,
            'total_verified': 0,
            'total_timeout': 0,
            'total_failed': 0
        }

    def track_command(self, command_name: str, deck_id: Optional[str] = None,
                     expected_state: Optional[str] = None, timeout: float = 2.0):
        """
        Inizia tracking di un comando

        Args:
            command_name: Nome comando (es. "Load Track", "Play Deck")
            deck_id: Deck interessato (A/B/C/D)
            expected_state: Cambio stato atteso (es. "loaded=True")
            timeout: Secondi max per considerare timeout
        """
        self.current_command = CommandTracking(
            command_name=command_name,
            deck_id=deck_id,
            timestamp=time.time(),
            status=CommandStatus.SENT,
            timeout_seconds=timeout,
            expected_state_change=expected_state
        )

        self.stats['total_sent'] += 1

        if self.on_command_sent:
            self.on_command_sent(self.current_command)

        logger.info(f"📤 Tracking: {command_name} (deck: {deck_id}, timeout: {timeout}s)")

    def mark_verified(self):
        """Segna comando corrente come verificato"""
        if not self.current_command:
            return

        self.current_command.status = CommandStatus.VERIFIED
        self.stats['total_verified'] += 1

        if self.on_command_verified:
            self.on_command_verified(self.current_command)

        logger.info(f"✅ Verified: {self.current_command.command_name}")

        # Aggiungi a history e cleanup
        self._archive_command()

    def mark_failed(self, error: str = ""):
        """Segna comando corrente come fallito"""
        if not self.current_command:
            return

        self.current_command.status = CommandStatus.FAILED
        self.stats['total_failed'] += 1

        if self.on_command_failed:
            self.on_command_failed(self.current_command, error)

        logger.warning(f"❌ Failed: {self.current_command.command_name} - {error}")

        self._archive_command()

    def check_timeout(self) -> bool:
        """
        Verifica se comando corrente è in timeout

        Returns:
            bool: True se in timeout
        """
        if not self.current_command:
            return False

        if self.current_command.status != CommandStatus.SENT:
            return False

        elapsed = time.time() - self.current_command.timestamp

        if elapsed > self.current_command.timeout_seconds:
            self.current_command.status = CommandStatus.TIMEOUT
            self.stats['total_timeout'] += 1

            if self.on_command_timeout:
                self.on_command_timeout(self.current_command)

            logger.warning(f"⏱️ Timeout: {self.current_command.command_name} ({elapsed:.1f}s)")

            self._archive_command()
            return True

        return False

    def _archive_command(self):
        """Archivia comando in history"""
        if self.current_command:
            self.command_history.append(self.current_command)

            # Mantieni solo ultimi N comandi
            if len(self.command_history) > self.max_history:
                self.command_history = self.command_history[-self.max_history:]

            self.current_command = None

    def get_success_rate(self) -> float:
        """Calcola success rate"""
        total = self.stats['total_sent']
        if total == 0:
            return 0.0

        verified = self.stats['total_verified']
        return (verified / total) * 100

    def get_stats_summary(self) -> Dict[str, Any]:
        """Ottieni riepilogo statistiche"""
        return {
            'sent': self.stats['total_sent'],
            'verified': self.stats['total_verified'],
            'timeout': self.stats['total_timeout'],
            'failed': self.stats['total_failed'],
            'success_rate': self.get_success_rate(),
            'current_tracking': self.current_command is not None
        }

    def get_recent_history(self, count: int = 10) -> list:
        """Ottieni cronologia recente"""
        return self.command_history[-count:]

    def is_tracking(self) -> bool:
        """Verifica se sta trackando un comando"""
        return self.current_command is not None

    def reset_stats(self):
        """Reset statistiche"""
        self.stats = {
            'total_sent': 0,
            'total_verified': 0,
            'total_timeout': 0,
            'total_failed': 0
        }
        self.command_history.clear()
        self.current_command = None

if __name__ == "__main__":
    print("📡 MIDI Communication Monitor")
    print("Sistema leggero di verifica comunicazione GUI-Traktor")