#!/usr/bin/env python3
"""
🔄 Traktor State Synchronization System
Sistema avanzato per sincronizzazione stato tra sistema interno e Traktor reale
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path

from traktor_control import TraktorController, DeckID, TraktorStatus

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """Stati sincronizzazione"""
    SYNCED = "synced"
    OUT_OF_SYNC = "out_of_sync"
    UNKNOWN = "unknown"
    VERIFYING = "verifying"

@dataclass
class DeckSyncState:
    """Stato sincronizzazione deck"""
    deck_id: DeckID
    internal_loaded: bool
    internal_playing: bool
    internal_track_name: Optional[str]
    traktor_loaded: Optional[bool] = None
    traktor_playing: Optional[bool] = None
    traktor_bpm: Optional[float] = None
    traktor_position: Optional[float] = None
    last_verification: float = 0.0
    sync_status: SyncStatus = SyncStatus.UNKNOWN
    discrepancies: List[str] = None

    def __post_init__(self):
        if self.discrepancies is None:
            self.discrepancies = []

@dataclass
class SystemSyncReport:
    """Report completo sincronizzazione sistema"""
    timestamp: float
    overall_sync_status: SyncStatus
    deck_states: Dict[str, DeckSyncState]
    total_discrepancies: int
    critical_issues: List[str]
    recommendations: List[str]
    next_verification: float

class TraktorStateSynchronizer:
    """Sistema sincronizzazione stato Traktor"""

    def __init__(self, traktor_controller: TraktorController):
        self.controller = traktor_controller
        self.sync_states: Dict[DeckID, DeckSyncState] = {}
        self.verification_interval = 10.0  # Verifica ogni 10 secondi
        self.last_full_verification = 0.0
        self.auto_sync_enabled = True
        self.verification_thread: Optional[threading.Thread] = None
        self.running = False

        # Tracking delle modifiche
        self.state_change_history: List[Dict] = []
        self.discrepancy_alerts: Set[str] = set()

        # Inizializza stati
        self._initialize_sync_states()

    def _initialize_sync_states(self):
        """Inizializza stati sincronizzazione per tutti i deck"""
        for deck in DeckID:
            internal_state = self.controller.deck_states[deck]
            self.sync_states[deck] = DeckSyncState(
                deck_id=deck,
                internal_loaded=internal_state['loaded'],
                internal_playing=internal_state['playing'],
                internal_track_name=internal_state['track_name'],
                last_verification=time.time()
            )

    def start_auto_sync(self):
        """Avvia sincronizzazione automatica"""
        if self.running:
            return

        self.running = True
        self.verification_thread = threading.Thread(
            target=self._auto_verification_loop,
            daemon=True
        )
        self.verification_thread.start()
        logger.info("🔄 Auto-sync started")

    def stop_auto_sync(self):
        """Ferma sincronizzazione automatica"""
        self.running = False
        if self.verification_thread:
            self.verification_thread.join(timeout=5.0)
        logger.info("🔄 Auto-sync stopped")

    def _auto_verification_loop(self):
        """Loop verifica automatica"""
        while self.running:
            try:
                self.verify_all_states()
                time.sleep(self.verification_interval)
            except Exception as e:
                logger.error(f"❌ Error in auto-verification: {e}")
                time.sleep(self.verification_interval)

    def verify_all_states(self) -> SystemSyncReport:
        """Verifica completa stati tutti i deck"""
        logger.debug("🔍 Starting comprehensive state verification...")

        # Aggiorna stati interni da controller
        self._update_internal_states()

        # Verifica ogni deck
        for deck in DeckID:
            self._verify_deck_state(deck)

        # Genera report
        report = self._generate_sync_report()

        # Log risultati
        self._log_verification_results(report)

        # Auto-correzione se abilitata
        if self.auto_sync_enabled:
            self._auto_correct_discrepancies(report)

        self.last_full_verification = time.time()
        return report

    def _update_internal_states(self):
        """Aggiorna stati interni da controller"""
        for deck in DeckID:
            internal_state = self.controller.deck_states[deck]
            sync_state = self.sync_states[deck]

            # Controlla se ci sono stati cambiamenti
            changed = False
            if sync_state.internal_loaded != internal_state['loaded']:
                changed = True
                logger.debug(f"🔄 Deck {deck.value} loaded state changed: {sync_state.internal_loaded} → {internal_state['loaded']}")

            if sync_state.internal_playing != internal_state['playing']:
                changed = True
                logger.debug(f"🔄 Deck {deck.value} playing state changed: {sync_state.internal_playing} → {internal_state['playing']}")

            # Aggiorna stato
            sync_state.internal_loaded = internal_state['loaded']
            sync_state.internal_playing = internal_state['playing']
            sync_state.internal_track_name = internal_state['track_name']

            # Registra cambiamento
            if changed:
                self.state_change_history.append({
                    'timestamp': time.time(),
                    'deck': deck.value,
                    'type': 'internal_change',
                    'loaded': internal_state['loaded'],
                    'playing': internal_state['playing']
                })

    def _verify_deck_state(self, deck: DeckID):
        """Verifica stato specifico deck"""
        sync_state = self.sync_states[deck]
        sync_state.sync_status = SyncStatus.VERIFYING
        sync_state.discrepancies.clear()

        try:
            # Ottieni stato Traktor (simulato - in realtà dovremmo leggere feedback MIDI)
            traktor_state = self._get_traktor_deck_state(deck)

            # Aggiorna stato Traktor nel sync_state
            if traktor_state:
                sync_state.traktor_loaded = traktor_state.get('loaded')
                sync_state.traktor_playing = traktor_state.get('playing')
                sync_state.traktor_bpm = traktor_state.get('bpm')
                sync_state.traktor_position = traktor_state.get('position')

                # Verifica discrepanze
                self._check_discrepancies(sync_state, traktor_state)

            sync_state.last_verification = time.time()

        except Exception as e:
            logger.error(f"❌ Error verifying deck {deck.value}: {e}")
            sync_state.sync_status = SyncStatus.UNKNOWN

    def _get_traktor_deck_state(self, deck: DeckID) -> Optional[Dict]:
        """
        Ottieni stato deck da Traktor
        NOTA: Questo è simulato - implementazione reale richiederebbe feedback MIDI
        """
        try:
            # Per ora usiamo lo stato interno come baseline
            # In implementazione reale, leggeremmo status MIDI da Traktor
            status = self.controller.get_status()

            # Simulazione lettura stato Traktor
            if deck == DeckID.A:
                return {
                    'loaded': True if status.deck_a_bpm > 0 else False,
                    'playing': self._estimate_playing_state(deck),
                    'bpm': status.deck_a_bpm,
                    'position': status.deck_a_position
                }
            elif deck == DeckID.B:
                return {
                    'loaded': True if status.deck_b_bpm > 0 else False,
                    'playing': self._estimate_playing_state(deck),
                    'bpm': status.deck_b_bpm,
                    'position': status.deck_b_position
                }
            else:
                # Deck C/D - stato sconosciuto
                return {
                    'loaded': None,
                    'playing': None,
                    'bpm': 0.0,
                    'position': 0.0
                }

        except Exception as e:
            logger.error(f"❌ Error getting Traktor state for deck {deck.value}: {e}")
            return None

    def _estimate_playing_state(self, deck: DeckID) -> Optional[bool]:
        """
        Stima stato playing dal cambio posizione
        NOTA: In implementazione reale, avremmo feedback MIDI diretto
        """
        try:
            # Controllo semplificato: se la posizione cambia, probabilmente sta suonando
            if hasattr(self, '_last_positions'):
                current_pos = 0.0
                if deck == DeckID.A:
                    current_pos = self.controller.get_status().deck_a_position
                elif deck == DeckID.B:
                    current_pos = self.controller.get_status().deck_b_position

                last_pos = self._last_positions.get(deck, 0.0)
                position_changed = abs(current_pos - last_pos) > 0.01

                self._last_positions[deck] = current_pos
                return position_changed
            else:
                self._last_positions = {}
                return None

        except Exception:
            return None

    def _check_discrepancies(self, sync_state: DeckSyncState, traktor_state: Dict):
        """Controlla discrepanze tra stato interno e Traktor"""
        discrepancies = []

        # Verifica loaded state
        if (sync_state.traktor_loaded is not None and
            sync_state.internal_loaded != sync_state.traktor_loaded):
            discrepancies.append(
                f"Loaded state mismatch: internal={sync_state.internal_loaded}, "
                f"traktor={sync_state.traktor_loaded}"
            )

        # Verifica playing state
        if (sync_state.traktor_playing is not None and
            sync_state.internal_playing != sync_state.traktor_playing):
            discrepancies.append(
                f"Playing state mismatch: internal={sync_state.internal_playing}, "
                f"traktor={sync_state.traktor_playing}"
            )

        # Verifica BPM consistency
        if sync_state.traktor_bpm and sync_state.traktor_bpm > 0:
            if sync_state.internal_loaded and sync_state.traktor_bpm < 50:
                discrepancies.append(
                    f"BPM inconsistency: internal says loaded but BPM={sync_state.traktor_bpm}"
                )

        sync_state.discrepancies = discrepancies

        # Determina sync status
        if discrepancies:
            sync_state.sync_status = SyncStatus.OUT_OF_SYNC
        else:
            sync_state.sync_status = SyncStatus.SYNCED

    def _generate_sync_report(self) -> SystemSyncReport:
        """Genera report completo sincronizzazione"""
        total_discrepancies = sum(len(state.discrepancies) for state in self.sync_states.values())

        # Determina stato generale
        if total_discrepancies == 0:
            overall_status = SyncStatus.SYNCED
        elif total_discrepancies > 5:
            overall_status = SyncStatus.OUT_OF_SYNC
        else:
            overall_status = SyncStatus.UNKNOWN

        # Identifica problemi critici
        critical_issues = []
        for deck, state in self.sync_states.items():
            if state.sync_status == SyncStatus.OUT_OF_SYNC:
                for discrepancy in state.discrepancies:
                    if "loaded" in discrepancy.lower():
                        critical_issues.append(f"Deck {deck.value}: {discrepancy}")

        # Genera raccomandazioni
        recommendations = []
        if critical_issues:
            recommendations.append("Run full system reset and re-verify MIDI mapping")
            recommendations.append("Check Traktor Pro feedback settings")

        if total_discrepancies > 3:
            recommendations.append("Consider disabling auto-sync temporarily")

        return SystemSyncReport(
            timestamp=time.time(),
            overall_sync_status=overall_status,
            deck_states={deck.value: state for deck, state in self.sync_states.items()},
            total_discrepancies=total_discrepancies,
            critical_issues=critical_issues,
            recommendations=recommendations,
            next_verification=time.time() + self.verification_interval
        )

    def _log_verification_results(self, report: SystemSyncReport):
        """Log risultati verifica"""
        if report.overall_sync_status == SyncStatus.SYNCED:
            logger.info(f"✅ All decks synchronized ({report.total_discrepancies} issues)")
        else:
            logger.warning(f"⚠️ Synchronization issues detected: {report.total_discrepancies} discrepancies")

        for deck_name, state in report.deck_states.items():
            if state.discrepancies:
                logger.warning(f"🔄 Deck {deck_name}: {', '.join(state.discrepancies)}")

    def _auto_correct_discrepancies(self, report: SystemSyncReport):
        """Auto-correzione discrepanze quando possibile"""
        if not self.auto_sync_enabled:
            return

        for deck_name, state in report.deck_states.items():
            if state.sync_status == SyncStatus.OUT_OF_SYNC:
                try:
                    self._attempt_deck_correction(DeckID(deck_name), state)
                except Exception as e:
                    logger.error(f"❌ Auto-correction failed for deck {deck_name}: {e}")

    def _attempt_deck_correction(self, deck: DeckID, state: DeckSyncState):
        """Tentativo correzione singolo deck"""
        logger.info(f"🔧 Attempting auto-correction for deck {deck.value}")

        # Reset stato interno se discrepanza maggiore
        if len(state.discrepancies) > 2:
            logger.info(f"🔄 Resetting internal state for deck {deck.value}")
            self.controller.deck_states[deck]['loaded'] = False
            self.controller.deck_states[deck]['playing'] = False
            self.controller.deck_states[deck]['track_name'] = None

    def force_sync_deck(self, deck: DeckID, traktor_state: Dict):
        """Forza sincronizzazione deck con stato Traktor specifico"""
        logger.info(f"🔧 Force syncing deck {deck.value}")

        # Aggiorna stato interno per matchare Traktor
        self.controller.deck_states[deck]['loaded'] = traktor_state.get('loaded', False)
        self.controller.deck_states[deck]['playing'] = traktor_state.get('playing', False)
        self.controller.deck_states[deck]['track_name'] = traktor_state.get('track_name')

        # Aggiorna sync state
        self.sync_states[deck].internal_loaded = traktor_state.get('loaded', False)
        self.sync_states[deck].internal_playing = traktor_state.get('playing', False)
        self.sync_states[deck].sync_status = SyncStatus.SYNCED
        self.sync_states[deck].discrepancies.clear()

    def get_sync_status_summary(self) -> Dict[str, Any]:
        """Ottieni riassunto stato sincronizzazione"""
        return {
            'last_verification': self.last_full_verification,
            'auto_sync_enabled': self.auto_sync_enabled,
            'total_discrepancies': sum(len(state.discrepancies) for state in self.sync_states.values()),
            'synced_decks': [
                deck.value for deck, state in self.sync_states.items()
                if state.sync_status == SyncStatus.SYNCED
            ],
            'out_of_sync_decks': [
                deck.value for deck, state in self.sync_states.items()
                if state.sync_status == SyncStatus.OUT_OF_SYNC
            ],
            'recent_changes': len(self.state_change_history[-10:])  # Ultimi 10 cambiamenti
        }

    def reset_all_sync_states(self):
        """Reset completo tutti gli stati sincronizzazione"""
        logger.info("🔄 Resetting all sync states...")

        # Reset controller states
        for deck in DeckID:
            self.controller.deck_states[deck]['loaded'] = False
            self.controller.deck_states[deck]['playing'] = False
            self.controller.deck_states[deck]['track_name'] = None
            self.controller.deck_states[deck]['track_id'] = None
            self.controller.deck_states[deck]['load_source_position'] = None

        # Reset browser tracking se disponibile
        if hasattr(self.controller, 'reset_browser_tracking'):
            self.controller.reset_browser_tracking()

        # Reinizializza sync states
        self._initialize_sync_states()

        # Clear history
        self.state_change_history.clear()
        self.discrepancy_alerts.clear()

        logger.info("✅ All sync states reset completed")

# Factory function
def create_state_synchronizer(traktor_controller: TraktorController) -> TraktorStateSynchronizer:
    """Crea e configura synchronizer"""
    return TraktorStateSynchronizer(traktor_controller)

if __name__ == "__main__":
    print("🔄 Traktor State Synchronization System")
    print("This module provides advanced state synchronization between internal tracking and Traktor Pro")
    print("Use create_state_synchronizer(controller) to initialize")