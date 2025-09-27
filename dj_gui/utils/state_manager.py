"""
State Management System for DJ GUI
Centralized state management with event-driven updates and thread-safe operations.
"""

import threading
import time
from typing import Any, Dict, List, Callable, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DJState(Enum):
    """DJ system operational states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"


class DeckState(Enum):
    """Individual deck states."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    CUEING = "cueing"
    LOADING = "loading"


@dataclass
class TrackInfo:
    """Track information data structure."""
    title: str = ""
    artist: str = ""
    album: str = ""
    genre: str = ""
    bpm: float = 0.0
    duration: float = 0.0
    file_path: str = ""
    key: str = ""
    energy: int = 5  # 1-10 scale

    @property
    def display_name(self) -> str:
        """Get formatted track name for display."""
        if self.artist and self.title:
            return f"{self.artist} - {self.title}"
        elif self.title:
            return self.title
        elif self.file_path:
            return self.file_path.split('/')[-1]
        return "Unknown Track"


@dataclass
class DeckStatus:
    """Deck status information."""
    deck_id: str = "A"
    state: DeckState = DeckState.STOPPED
    track: TrackInfo = field(default_factory=TrackInfo)
    position: float = 0.0  # Position in seconds
    bpm: float = 0.0
    pitch: float = 0.0  # Pitch adjustment (-100 to +100)
    volume: float = 1.0  # Volume (0.0 to 1.0)
    gain: float = 1.0    # Gain (0.0 to 2.0)
    eq_high: float = 0.0 # EQ High (-1.0 to +1.0)
    eq_mid: float = 0.0  # EQ Mid (-1.0 to +1.0)
    eq_low: float = 0.0  # EQ Low (-1.0 to +1.0)
    cue_point: float = 0.0  # Cue point in seconds
    loop_start: float = 0.0
    loop_end: float = 0.0
    loop_active: bool = False
    sync_enabled: bool = False
    keylock_enabled: bool = False

    @property
    def position_percent(self) -> float:
        """Get position as percentage of track duration."""
        if self.track.duration > 0:
            return (self.position / self.track.duration) * 100
        return 0.0


@dataclass
class MixerStatus:
    """Mixer status information."""
    crossfader_position: float = 0.0  # -1.0 (full A) to +1.0 (full B)
    master_volume: float = 1.0
    headphone_volume: float = 0.5
    headphone_mix: float = 0.0  # 0.0 (master) to 1.0 (cue)
    booth_volume: float = 1.0
    record_enabled: bool = False

    @property
    def crossfader_percent(self) -> float:
        """Get crossfader position as percentage (0-100)."""
        return ((self.crossfader_position + 1.0) / 2.0) * 100


@dataclass
class AgentStatus:
    """DJ Agent status information."""
    active: bool = False
    current_action: str = "Idle"
    genre_preference: str = "Auto"
    energy_target: int = 5  # 1-10 scale
    behavior_profile: str = "Balanced"
    next_transition_time: float = 0.0
    confidence_score: float = 0.0  # 0.0 to 1.0
    total_tracks_played: int = 0
    session_start_time: float = 0.0

    @property
    def session_duration(self) -> float:
        """Get session duration in seconds."""
        if self.session_start_time > 0:
            return time.time() - self.session_start_time
        return 0.0


@dataclass
class SystemStatus:
    """Overall system status."""
    dj_state: DJState = DJState.STOPPED
    deck_a: DeckStatus = field(default_factory=lambda: DeckStatus(deck_id="A"))
    deck_b: DeckStatus = field(default_factory=lambda: DeckStatus(deck_id="B"))
    mixer: MixerStatus = field(default_factory=MixerStatus)
    agent: AgentStatus = field(default_factory=AgentStatus)
    audio_levels: Dict[str, float] = field(default_factory=dict)
    midi_connected: bool = False
    last_update: float = field(default_factory=time.time)

    def __post_init__(self):
        """Initialize audio levels."""
        if not self.audio_levels:
            self.audio_levels = {
                "master_left": 0.0,
                "master_right": 0.0,
                "deck_a_left": 0.0,
                "deck_a_right": 0.0,
                "deck_b_left": 0.0,
                "deck_b_right": 0.0
            }


class StateManager:
    """
    Thread-safe state manager for DJ GUI application.
    Provides centralized state management with event-driven updates.
    """

    def __init__(self):
        self._state = SystemStatus()
        self._lock = threading.RLock()
        self._observers: Dict[str, List[Callable]] = {
            'state_change': [],
            'deck_update': [],
            'mixer_update': [],
            'agent_update': [],
            'audio_levels': [],
            'track_change': [],
            'error': []
        }
        self._running = True

        logger.info("State Manager initialized")

    def get_state(self) -> SystemStatus:
        """Get current system state (thread-safe copy)."""
        with self._lock:
            # Return a copy to prevent external modification
            import copy
            return copy.deepcopy(self._state)

    def update_dj_state(self, new_state: DJState) -> None:
        """Update overall DJ system state."""
        with self._lock:
            old_state = self._state.dj_state
            self._state.dj_state = new_state
            self._state.last_update = time.time()

        if old_state != new_state:
            self._notify_observers('state_change', {
                'old_state': old_state,
                'new_state': new_state,
                'timestamp': time.time()
            })
            logger.info(f"DJ state changed: {old_state.value} -> {new_state.value}")

    def update_deck(self, deck_id: str, **kwargs) -> None:
        """Update deck status with provided parameters."""
        with self._lock:
            deck = self._state.deck_a if deck_id.upper() == "A" else self._state.deck_b
            old_state = deck.state
            old_track = deck.track.display_name

            # Update provided fields
            for key, value in kwargs.items():
                if hasattr(deck, key):
                    setattr(deck, key, value)
                elif key.startswith('track_') and hasattr(deck.track, key[6:]):
                    setattr(deck.track, key[6:], value)

            self._state.last_update = time.time()

        # Notify observers of changes
        self._notify_observers('deck_update', {
            'deck_id': deck_id,
            'deck_status': deck,
            'timestamp': time.time()
        })

        # Check for significant changes
        if old_state != deck.state:
            logger.info(f"Deck {deck_id} state changed: {old_state.value} -> {deck.state.value}")

        if old_track != deck.track.display_name:
            self._notify_observers('track_change', {
                'deck_id': deck_id,
                'old_track': old_track,
                'new_track': deck.track.display_name,
                'timestamp': time.time()
            })
            logger.info(f"Deck {deck_id} track changed: {deck.track.display_name}")

    def update_mixer(self, **kwargs) -> None:
        """Update mixer status with provided parameters."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._state.mixer, key):
                    setattr(self._state.mixer, key, value)

            self._state.last_update = time.time()

        self._notify_observers('mixer_update', {
            'mixer_status': self._state.mixer,
            'timestamp': time.time()
        })

    def update_agent(self, **kwargs) -> None:
        """Update agent status with provided parameters."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._state.agent, key):
                    setattr(self._state.agent, key, value)

            self._state.last_update = time.time()

        self._notify_observers('agent_update', {
            'agent_status': self._state.agent,
            'timestamp': time.time()
        })

    def update_audio_levels(self, levels: Dict[str, float]) -> None:
        """Update audio level meters."""
        with self._lock:
            self._state.audio_levels.update(levels)
            self._state.last_update = time.time()

        self._notify_observers('audio_levels', {
            'levels': levels,
            'timestamp': time.time()
        })

    def set_track_info(self, deck_id: str, track_info: TrackInfo) -> None:
        """Set complete track information for a deck."""
        with self._lock:
            deck = self._state.deck_a if deck_id.upper() == "A" else self._state.deck_b
            old_track = deck.track.display_name
            deck.track = track_info
            self._state.last_update = time.time()

        if old_track != track_info.display_name:
            self._notify_observers('track_change', {
                'deck_id': deck_id,
                'old_track': old_track,
                'new_track': track_info.display_name,
                'track_info': track_info,
                'timestamp': time.time()
            })
            logger.info(f"Deck {deck_id} loaded: {track_info.display_name}")

    def report_error(self, error_type: str, message: str, details: Optional[Dict] = None) -> None:
        """Report system error."""
        error_data = {
            'type': error_type,
            'message': message,
            'details': details or {},
            'timestamp': time.time()
        }

        logger.error(f"System error [{error_type}]: {message}")
        self._notify_observers('error', error_data)

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to state change events."""
        if event_type not in self._observers:
            raise ValueError(f"Invalid event type: {event_type}")

        self._observers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type} events")

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from state change events."""
        if event_type in self._observers:
            try:
                self._observers[event_type].remove(callback)
                logger.debug(f"Unsubscribed from {event_type} events")
            except ValueError:
                logger.warning(f"Callback not found for {event_type} events")

    def _notify_observers(self, event_type: str, data: Any) -> None:
        """Notify all observers of an event."""
        for callback in self._observers.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in observer callback for {event_type}: {e}")

    def get_deck_status(self, deck_id: str) -> DeckStatus:
        """Get current status for specific deck."""
        with self._lock:
            deck = self._state.deck_a if deck_id.upper() == "A" else self._state.deck_b
            import copy
            return copy.deepcopy(deck)

    def get_mixer_status(self) -> MixerStatus:
        """Get current mixer status."""
        with self._lock:
            import copy
            return copy.deepcopy(self._state.mixer)

    def get_agent_status(self) -> AgentStatus:
        """Get current agent status."""
        with self._lock:
            import copy
            return copy.deepcopy(self._state.agent)

    def get_audio_levels(self) -> Dict[str, float]:
        """Get current audio levels."""
        with self._lock:
            return dict(self._state.audio_levels)

    def shutdown(self) -> None:
        """Shutdown state manager and cleanup resources."""
        self._running = False
        logger.info("State Manager shutdown")


# Global state manager instance
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get global state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


def initialize_state_manager() -> StateManager:
    """Initialize and return global state manager."""
    global _state_manager
    _state_manager = StateManager()
    return _state_manager


# Export main classes and functions
__all__ = [
    'StateManager', 'SystemStatus', 'DeckStatus', 'MixerStatus', 'AgentStatus',
    'TrackInfo', 'DJState', 'DeckState',
    'get_state_manager', 'initialize_state_manager'
]