#!/usr/bin/env python3
"""
🤖 Complete Autonomous DJ System
Master orchestrator for fully autonomous DJ mixing
Integrates all components for hands-free operation
"""

import asyncio
import time
import logging
import threading
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Core configuration
from config import DJConfig, VENUE_TYPES, EVENT_TYPES, get_config

# Autonomous components (optional)
try:
    from autonomous_audio_engine import RealTimeAnalyzer, AudioFeatures
    from autonomous_decision_engine import AutonomousDecisionEngine, MixContext, DecisionUrgency, DJDecision
    from autonomous_mixing_controller import AutonomousMixingController, MixParameters, MixTransitionType
    from dj_memory_system import DJMemorySystem, MemoryType
    AUTONOMOUS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Autonomous components not available: {e}")
    print("💡 Run: pip install librosa essentia-tensorflow scikit-learn sounddevice")
    AUTONOMOUS_AVAILABLE = False
    # Fallback types
    AudioFeatures = None
    RealTimeAnalyzer = None
    AutonomousDecisionEngine = None
    MixContext = None
    DecisionUrgency = None
    DJDecision = None
    AutonomousMixingController = None
    MixParameters = None
    MixTransitionType = None
    DJMemorySystem = None
    MemoryType = None

# Music and control
from music_library import MusicLibraryScanner, TrackInfo, get_music_scanner

logger = logging.getLogger(__name__)

class AutonomousMode(Enum):
    """Autonomous operation modes"""
    MANUAL = "manual"          # Human control
    ASSISTED = "assisted"      # AI suggestions + human execution
    AUTONOMOUS = "autonomous"  # Full AI control

class SessionPhase(Enum):
    """DJ session phases"""
    STARTUP = "startup"
    WARM_UP = "warm_up"
    BUILDING = "building"
    PEAK_TIME = "peak_time"
    WIND_DOWN = "wind_down"
    CLOSING = "closing"

class DJSystemState(Enum):
    """Overall system state"""
    INITIALIZING = "initializing"
    READY = "ready"
    PLAYING = "playing"
    MIXING = "mixing"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class AutonomousSession:
    """Complete autonomous DJ session state"""
    session_id: str
    venue_type: str
    event_type: str
    target_duration: int  # minutes

    # Session state
    start_time: float
    current_phase: SessionPhase = SessionPhase.STARTUP
    autonomous_mode: AutonomousMode = AutonomousMode.AUTONOMOUS

    # Track management
    current_track: Optional[TrackInfo] = None
    next_track: Optional[TrackInfo] = None
    queue: List[TrackInfo] = None
    played_tracks: List[str] = None

    # Performance metrics
    energy_curve: List[float] = None
    crowd_response: List[float] = None
    transition_quality: List[float] = None
    session_energy_target: float = 5.0

    # Timing
    last_transition: Optional[float] = None
    next_transition_planned: Optional[float] = None

    def __post_init__(self):
        if self.queue is None:
            self.queue = []
        if self.played_tracks is None:
            self.played_tracks = []
        if self.energy_curve is None:
            self.energy_curve = []
        if self.crowd_response is None:
            self.crowd_response = []
        if self.transition_quality is None:
            self.transition_quality = []

    def get_session_progress(self) -> float:
        """Get session progress (0-1)"""
        elapsed = time.time() - self.start_time
        return min(1.0, elapsed / (self.target_duration * 60))

    def get_expected_energy(self) -> float:
        """Get expected energy level based on session phase and progress"""
        progress = self.get_session_progress()

        if self.current_phase == SessionPhase.STARTUP:
            return 3.0
        elif self.current_phase == SessionPhase.WARM_UP:
            return 4.0 + progress * 2.0  # 4-6
        elif self.current_phase == SessionPhase.BUILDING:
            return 6.0 + progress * 2.0  # 6-8
        elif self.current_phase == SessionPhase.PEAK_TIME:
            return 8.0 + progress * 1.0  # 8-9
        elif self.current_phase == SessionPhase.WIND_DOWN:
            return 8.0 - progress * 3.0  # 8-5
        elif self.current_phase == SessionPhase.CLOSING:
            return 5.0 - progress * 2.0  # 5-3
        else:
            return 5.0

class AutonomousDJSystem:
    """Complete autonomous DJ system orchestrator"""

    def __init__(self, config: DJConfig = None):
        self.config = config or get_config()

        # System state
        self.state = DJSystemState.INITIALIZING
        self.session: Optional[AutonomousSession] = None

        # Core components
        self.audio_engine = RealTimeAnalyzer()
        self.decision_engine = AutonomousDecisionEngine(self.config)
        self.mixing_controller = AutonomousMixingController(self.config)
        self.memory_system = DJMemorySystem(self.config)
        self.music_scanner = get_music_scanner(self.config)

        # System coordination
        self.main_loop_thread = None
        self.is_running = False
        self.loop_interval = 0.1  # 100ms main loop

        # Performance monitoring
        self.performance_metrics = {
            'uptime': 0.0,
            'tracks_mixed': 0,
            'successful_transitions': 0,
            'decision_accuracy': 0.0,
            'avg_crowd_response': 0.0
        }

        # Callbacks for external monitoring
        self.status_callbacks: List[Callable] = []
        self.event_callbacks: List[Callable] = []

        print("🤖 Autonomous DJ System initialized")

    async def initialize_system(self) -> bool:
        """Initialize all system components"""
        try:
            print("🔄 Initializing autonomous DJ system...")

            # Initialize music library
            print("📚 Scanning music library...")
            await self.music_scanner.scan_library()

            # Connect MIDI
            print("🎹 Connecting MIDI controller...")
            if not self.mixing_controller.connect_midi():
                print("⚠️ MIDI connection failed - using simulation mode")

            # Start processing threads
            print("🧠 Starting decision engine...")
            self.decision_engine.start_processing()

            print("🎛️ Starting mixing controller...")
            self.mixing_controller.start_processing()

            # Set up callbacks
            self.mixing_controller.set_status_callback(self._on_mixer_status)
            self.mixing_controller.set_error_callback(self._on_mixer_error)

            self.state = DJSystemState.READY
            print("✅ Autonomous DJ System ready")
            return True

        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            self.state = DJSystemState.ERROR
            return False

    def start_autonomous_session(self, venue_type: str, event_type: str,
                                duration_minutes: int = 120) -> str:
        """Start a new autonomous DJ session"""
        try:
            if self.state != DJSystemState.READY:
                raise RuntimeError("System not ready for new session")

            # Create session
            session_id = hashlib.md5(f"{time.time()}_{venue_type}_{event_type}".encode()).hexdigest()[:12]

            self.session = AutonomousSession(
                session_id=session_id,
                venue_type=venue_type,
                event_type=event_type,
                target_duration=duration_minutes,
                start_time=time.time()
            )

            # Initialize mix context
            self.decision_engine.update_context(
                venue_type=venue_type,
                event_type=event_type,
                session_duration=0.0,
                crowd_energy=self.session.get_expected_energy()
            )

            # Start main control loop
            self.is_running = True
            self.main_loop_thread = threading.Thread(target=self._main_control_loop, daemon=True)
            self.main_loop_thread.start()

            # Select and start first track
            self._start_first_track()

            self.state = DJSystemState.PLAYING
            self._notify_event("session_started", {"session_id": session_id})

            print(f"🎵 Autonomous session started: {session_id}")
            print(f"   Venue: {venue_type}, Event: {event_type}")
            print(f"   Duration: {duration_minutes} minutes")

            return session_id

        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            raise

    def stop_session(self):
        """Stop current autonomous session"""
        try:
            if self.session:
                self._notify_event("session_stopping", {"session_id": self.session.session_id})

                # Stop main loop
                self.is_running = False
                if self.main_loop_thread and self.main_loop_thread.is_alive():
                    self.main_loop_thread.join(timeout=2.0)

                # Store session memory
                self._store_session_memory()

                # Clean shutdown
                self.state = DJSystemState.READY
                session_id = self.session.session_id
                self.session = None

                self._notify_event("session_stopped", {"session_id": session_id})
                print(f"⏹️ Session stopped: {session_id}")

        except Exception as e:
            logger.error(f"Error stopping session: {e}")

    def _main_control_loop(self):
        """Main autonomous control loop"""
        while self.is_running and self.session:
            try:
                # Update session timing
                self._update_session_state()

                # Monitor current track progress
                self._monitor_track_progress()

                # Update decision context
                self._update_decision_context()

                # Execute any pending decisions
                self._process_autonomous_decisions()

                # Update performance metrics
                self._update_performance_metrics()

                # Sleep for next iteration
                time.sleep(self.loop_interval)

            except Exception as e:
                logger.error(f"Error in main control loop: {e}")
                time.sleep(1.0)  # Longer sleep on error

    def _start_first_track(self):
        """Select and start the first track"""
        try:
            # Get suitable opening tracks
            candidates = self.music_scanner.search_tracks(
                genre="house",  # Default genre
                bpm_range=(120, 130),  # Moderate BPM for opening
                energy_range=(3, 5),   # Low-medium energy for opening
                limit=10
            )

            if not candidates:
                # Fallback: get any tracks
                candidates = self.music_scanner.search_tracks(limit=10)

            if candidates:
                first_track = candidates[0]
                self.session.current_track = first_track
                self.session.played_tracks.append(first_track.filepath)

                # Update decision context
                self.decision_engine.update_context(
                    current_track=first_track,
                    current_bpm=first_track.bpm or 120.0,
                    current_key=first_track.key,
                    current_energy=first_track.energy or 4.0,
                    current_position=0.0
                )

                # Start audio analysis
                self.audio_engine.start_analysis(first_track.filepath)

                print(f"🎵 Starting with: {first_track.title} - {first_track.artist}")

            else:
                raise RuntimeError("No tracks available for autonomous session")

        except Exception as e:
            logger.error(f"Error starting first track: {e}")
            raise

    def _update_session_state(self):
        """Update session phase and state"""
        if not self.session:
            return

        try:
            progress = self.session.get_session_progress()
            session_minutes = (time.time() - self.session.start_time) / 60

            # Update session phase based on progress and event type
            if self.session.event_type == "prime_time":
                if progress < 0.1:
                    self.session.current_phase = SessionPhase.STARTUP
                elif progress < 0.3:
                    self.session.current_phase = SessionPhase.WARM_UP
                elif progress < 0.7:
                    self.session.current_phase = SessionPhase.BUILDING
                elif progress < 0.9:
                    self.session.current_phase = SessionPhase.PEAK_TIME
                else:
                    self.session.current_phase = SessionPhase.WIND_DOWN
            else:
                # Default progression
                if progress < 0.2:
                    self.session.current_phase = SessionPhase.WARM_UP
                elif progress < 0.8:
                    self.session.current_phase = SessionPhase.BUILDING
                else:
                    self.session.current_phase = SessionPhase.WIND_DOWN

            # Update target energy based on phase
            self.session.session_energy_target = self.session.get_expected_energy()

        except Exception as e:
            logger.error(f"Error updating session state: {e}")

    def _monitor_track_progress(self):
        """Monitor current track progress and plan transitions"""
        if not self.session or not self.session.current_track:
            return

        try:
            # Get current track analysis
            track_features = self.audio_engine.get_track_features()
            if not track_features:
                return

            current_position = track_features.current_position
            track_duration = track_features.duration

            # Update decision context with position
            self.decision_engine.update_context(
                current_position=current_position,
                current_energy=track_features.current_energy
            )

            # Check if we need to plan next track
            time_remaining = track_duration - current_position
            if time_remaining <= 90 and not self.session.next_track:  # 1.5 minutes remaining
                self._plan_next_track()

            # Check if we should start transition
            if time_remaining <= 30 and self.session.next_track:  # 30 seconds remaining
                self._execute_transition()

        except Exception as e:
            logger.error(f"Error monitoring track progress: {e}")

    def _plan_next_track(self):
        """Plan the next track to play"""
        try:
            if not self.session or not self.session.current_track:
                return

            # Get candidates based on current context
            candidates = self.music_scanner.get_optimal_mix_candidates(
                self.session.current_track.filepath,
                position_seconds=None  # Will use audio engine position
            )

            if candidates:
                # Select best candidate
                best_candidate = candidates[0]
                next_track = best_candidate['track']

                self.session.next_track = next_track
                self.session.next_transition_planned = time.time() + 30  # Plan for 30s from now

                # Update decision context
                self.decision_engine.update_context(
                    next_track=next_track,
                    next_prepared=True
                )

                print(f"🎯 Next track planned: {next_track.title} - {next_track.artist}")

        except Exception as e:
            logger.error(f"Error planning next track: {e}")

    def _execute_transition(self):
        """Execute transition to next track"""
        try:
            if not self.session or not self.session.next_track:
                return

            if self.state == DJSystemState.MIXING:
                return  # Already mixing

            self.state = DJSystemState.MIXING

            # Create mix parameters based on tracks
            mix_params = MixParameters(
                transition_type=MixTransitionType.FADE,
                duration_seconds=16.0,  # 16 beats
                start_position=0.0,
                target_deck='B' if self.mixing_controller.active_deck == 'A' else 'A',
                sync_bpm=True,
                eq_automation=True,
                use_effects=True
            )

            # Execute transition
            self.mixing_controller._execute_mix_transition(mix_params)

            # Store memory of this transition
            self._store_transition_memory(success_score=0.8)  # Default score

            # Update session state
            self.session.current_track = self.session.next_track
            self.session.next_track = None
            self.session.played_tracks.append(self.session.current_track.filepath)
            self.session.last_transition = time.time()

            # Update metrics
            self.performance_metrics['tracks_mixed'] += 1
            self.performance_metrics['successful_transitions'] += 1

            print(f"🔄 Transition executed to: {self.session.current_track.title}")

            # Return to playing state after transition
            self.state = DJSystemState.PLAYING

        except Exception as e:
            logger.error(f"Error executing transition: {e}")
            self.state = DJSystemState.PLAYING

    def _update_decision_context(self):
        """Update decision engine context"""
        if not self.session:
            return

        try:
            session_minutes = (time.time() - self.session.start_time) / 60

            self.decision_engine.update_context(
                venue_type=self.session.venue_type,
                event_type=self.session.event_type,
                session_duration=session_minutes,
                crowd_energy=self.session.session_energy_target
            )

        except Exception as e:
            logger.error(f"Error updating decision context: {e}")

    def _process_autonomous_decisions(self):
        """Process decisions from the decision engine"""
        try:
            recent_decisions = self.decision_engine.get_recent_decisions(limit=5)

            for decision in recent_decisions:
                if not decision.executed and decision.urgency == DecisionUrgency.CRITICAL:
                    # Execute critical decisions immediately
                    self.mixing_controller.execute_mix_decision(decision)
                    decision.executed = True
                    decision.execution_time = time.time()

        except Exception as e:
            logger.error(f"Error processing decisions: {e}")

    def _store_transition_memory(self, success_score: float):
        """Store memory of transition for learning"""
        try:
            if not self.session:
                return

            context = {
                'venue_type': self.session.venue_type,
                'event_type': self.session.event_type,
                'session_time': (time.time() - self.session.start_time) / 60,
                'source_track': asdict(self.session.current_track) if self.session.current_track else None,
                'target_track': asdict(self.session.next_track) if self.session.next_track else None
            }

            outcome = {
                'success_score': success_score,
                'crowd_response': self.session.session_energy_target / 10.0,
                'technical_quality': 0.8  # Default
            }

            self.memory_system.store_memory(
                MemoryType.SUCCESSFUL_TRANSITION if success_score > 0.6 else MemoryType.FAILED_TRANSITION,
                context,
                outcome=outcome
            )

        except Exception as e:
            logger.error(f"Error storing transition memory: {e}")

    def _store_session_memory(self):
        """Store complete session memory"""
        try:
            if not self.session:
                return

            session_data = {
                'session_id': self.session.session_id,
                'venue_type': self.session.venue_type,
                'event_type': self.session.event_type,
                'duration': (time.time() - self.session.start_time) / 60,
                'tracks_played': len(self.session.played_tracks),
                'energy_progression': self.session.energy_curve,
                'crowd_response': self.session.crowd_response
            }

            print(f"💾 Session memory stored: {session_data}")

        except Exception as e:
            logger.error(f"Error storing session memory: {e}")

    def _update_performance_metrics(self):
        """Update system performance metrics"""
        try:
            if self.session:
                self.performance_metrics['uptime'] = time.time() - self.session.start_time

                # Calculate decision accuracy (placeholder)
                decisions = self.decision_engine.get_recent_decisions()
                if decisions:
                    successful = sum(1 for d in decisions if d.success is True)
                    self.performance_metrics['decision_accuracy'] = successful / len(decisions)

        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")

    def _on_mixer_status(self, status: Dict):
        """Handle mixer status updates"""
        self._notify_status_callbacks(status)

    def _on_mixer_error(self, error: str):
        """Handle mixer errors"""
        logger.error(f"Mixer error: {error}")
        self._notify_event("mixer_error", {"error": error})

    def _notify_status_callbacks(self, status: Dict):
        """Notify status callbacks"""
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")

    def _notify_event(self, event_type: str, data: Dict):
        """Notify event callbacks"""
        event = {"type": event_type, "data": data, "timestamp": time.time()}
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

    def add_status_callback(self, callback: Callable):
        """Add status update callback"""
        self.status_callbacks.append(callback)

    def add_event_callback(self, callback: Callable):
        """Add event callback"""
        self.event_callbacks.append(callback)

    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        status = {
            'state': self.state.value,
            'session': asdict(self.session) if self.session else None,
            'performance_metrics': self.performance_metrics,
            'decision_stats': self.decision_engine.get_decision_stats(),
            'mixing_stats': self.mixing_controller.get_mixing_stats(),
            'memory_stats': self.memory_system.get_memory_stats()
        }
        return status

    def shutdown(self):
        """Shutdown the autonomous DJ system"""
        try:
            print("🔄 Shutting down Autonomous DJ System...")

            # Stop session if running
            if self.session:
                self.stop_session()

            # Stop components
            self.decision_engine.stop_processing()
            self.mixing_controller.stop_processing()
            self.audio_engine.stop_analysis()

            self.state = DJSystemState.STOPPED
            print("⏹️ Autonomous DJ System shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

def test_autonomous_system():
    """Test the complete autonomous DJ system"""
    print("🧪 Testing Complete Autonomous DJ System")
    print("=" * 60)

    async def run_test():
        # Initialize system
        system = AutonomousDJSystem()

        # Add test callbacks
        def status_callback(status):
            print(f"📊 Status: {status.get('mixing_state', 'unknown')}")

        def event_callback(event):
            print(f"📢 Event: {event['type']} - {event['data']}")

        system.add_status_callback(status_callback)
        system.add_event_callback(event_callback)

        try:
            # Initialize
            if await system.initialize_system():
                print("✅ System initialized successfully")

                # Start autonomous session
                session_id = system.start_autonomous_session(
                    venue_type="club",
                    event_type="prime_time",
                    duration_minutes=5  # Short test session
                )

                print(f"🎵 Test session started: {session_id}")

                # Let it run for a bit
                await asyncio.sleep(10)

                # Get status
                status = system.get_system_status()
                print(f"\n📊 System Status:")
                print(f"  State: {status['state']}")
                if status['session']:
                    print(f"  Session Phase: {status['session']['current_phase']}")
                    print(f"  Progress: {status['session'].get('progress', 0):.1%}")

                # Stop session
                system.stop_session()

            else:
                print("❌ System initialization failed")

        finally:
            system.shutdown()

    # Run the test
    asyncio.run(run_test())
    print("\n✅ Autonomous system test complete!")

if __name__ == "__main__":
    test_autonomous_system()