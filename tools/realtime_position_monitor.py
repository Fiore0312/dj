#!/usr/bin/env python3
"""
⏱️ Real-time Position Monitor
Advanced real-time monitoring system for precise mix timing and decision making
Monitors track position, energy levels, beat positions, and optimal mix points
"""

import time
import threading
import logging
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import queue
import math

# Audio analysis imports
try:
    from autonomous_audio_engine import RealTimeAnalyzer, AudioFeatures
    from music_library import TrackInfo
    from traktor_control import TraktorController
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class MixAlert(Enum):
    """Types of mixing alerts"""
    OPTIMAL_MIX_POINT = "optimal_mix_point"
    TRACK_ENDING_SOON = "track_ending_soon"
    ENERGY_CHANGE_NEEDED = "energy_change_needed"
    BEAT_PHRASE_BOUNDARY = "beat_phrase_boundary"
    EMERGENCY_MIX_NEEDED = "emergency_mix_needed"

@dataclass
class MixOpportunity:
    """Represents a mixing opportunity with timing and quality info"""
    alert_type: MixAlert
    position_seconds: float
    optimal_mix_window: Tuple[float, float]  # (start, end) in seconds
    confidence: float  # 0.0 to 1.0
    quality_score: float  # 0.0 to 1.0 (how good this mix point is)
    reasoning: str
    urgency_level: int = 1  # 1=low, 2=medium, 3=high, 4=critical
    expires_at: float = 0.0  # Timestamp when this opportunity expires

@dataclass
class PositionState:
    """Current position state of the playing track"""
    track: Optional[TrackInfo] = None
    position_seconds: float = 0.0
    position_percentage: float = 0.0
    remaining_seconds: float = 0.0

    # Beat-level information
    current_beat: int = 0
    beats_until_phrase: int = 0
    current_phrase: int = 0

    # Energy and dynamics
    current_energy: float = 5.0
    energy_trend: float = 0.0  # -1 to 1 (decreasing to increasing)
    rms_level: float = 0.5

    # Mix point analysis
    in_mix_zone: bool = False
    next_mix_point: Optional[float] = None
    time_to_next_mix: Optional[float] = None

    # Structural information
    in_intro: bool = False
    in_outro: bool = False
    in_breakdown: bool = False
    in_buildup: bool = False

class RealTimePositionMonitor:
    """
    Advanced real-time monitoring system that provides:
    - Precise track position tracking
    - Optimal mix point detection and alerting
    - Beat-accurate timing for transitions
    - Energy level monitoring and trend analysis
    - Structural analysis (intro/outro/breakdown detection)
    - Emergency situation detection
    """

    def __init__(self, update_interval: float = 0.1):
        """
        Initialize the real-time monitor

        Args:
            update_interval: How often to update position (seconds)
        """
        self.update_interval = update_interval

        # Core components
        self.traktor_controller: Optional[TraktorController] = None
        self.audio_analyzer: Optional[RealTimeAnalyzer] = None

        # Monitoring state
        self.is_monitoring = False
        self.position_state = PositionState()
        self.last_update_time = 0.0

        # Mix opportunity detection
        self.mix_opportunities = queue.Queue()
        self.detected_opportunities: List[MixOpportunity] = []
        self.opportunity_callbacks: List[Callable[[MixOpportunity], None]] = []

        # Configuration
        self.config = {
            'mix_point_lookahead': 30.0,  # Seconds to look ahead for mix points
            'emergency_threshold': 10.0,   # Seconds before track ends to trigger emergency
            'phrase_length_beats': 16,     # Typical phrase length
            'energy_change_threshold': 1.0, # Energy change threshold for alerts
            'beat_tolerance': 0.1          # Beat timing tolerance in seconds
        }

        # Threading
        self.monitor_thread: Optional[threading.Thread] = None
        self.analysis_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # Performance metrics
        self.metrics = {
            'total_updates': 0,
            'mix_opportunities_detected': 0,
            'average_update_frequency': 0.0,
            'position_accuracy': 0.95
        }

        logger.info("⏱️ Real-time Position Monitor initialized")

    def start_monitoring(self, traktor_controller: TraktorController,
                        audio_analyzer: Optional[RealTimeAnalyzer] = None) -> bool:
        """Start real-time monitoring"""
        try:
            logger.info("🚀 Starting real-time position monitoring...")

            self.traktor_controller = traktor_controller
            self.audio_analyzer = audio_analyzer

            if not self.traktor_controller:
                logger.error("❌ Traktor controller required for monitoring")
                return False

            self.is_monitoring = True
            self.stop_event.clear()

            # Start monitoring threads
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self.analysis_thread = threading.Thread(
                target=self._analysis_loop, daemon=True
            )

            self.monitor_thread.start()
            self.analysis_thread.start()

            logger.info("✅ Real-time monitoring started")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start monitoring: {e}")
            return False

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        try:
            logger.info("🛑 Stopping real-time monitoring...")

            self.is_monitoring = False
            self.stop_event.set()

            # Wait for threads to finish
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2.0)
            if self.analysis_thread and self.analysis_thread.is_alive():
                self.analysis_thread.join(timeout=2.0)

            logger.info("✅ Real-time monitoring stopped")

        except Exception as e:
            logger.error(f"❌ Error stopping monitoring: {e}")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("👁️ Position monitoring loop started")

        while self.is_monitoring and not self.stop_event.is_set():
            try:
                start_time = time.time()

                # Update position state
                self._update_position_state()

                # Detect mix opportunities
                self._detect_mix_opportunities()

                # Update performance metrics
                self._update_metrics(start_time)

                # Sleep for remaining interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed)
                time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(self.update_interval)

        logger.info("👁️ Position monitoring loop stopped")

    def _analysis_loop(self):
        """Audio analysis loop for advanced mix point detection"""
        logger.info("🔬 Analysis loop started")

        while self.is_monitoring and not self.stop_event.is_set():
            try:
                if self.audio_analyzer and self.position_state.track:
                    # Perform advanced audio analysis
                    self._analyze_current_audio()

                time.sleep(0.5)  # Analysis every 500ms

            except Exception as e:
                logger.error(f"❌ Analysis loop error: {e}")
                time.sleep(1.0)

        logger.info("🔬 Analysis loop stopped")

    def _update_position_state(self):
        """Update current position state from Traktor"""
        try:
            if not self.traktor_controller:
                return

            # Get current status from Traktor
            status = self.traktor_controller.get_comprehensive_status()
            if not status:
                return

            # Update basic position info
            self.position_state.position_seconds = status.get('position', 0.0)

            # Calculate percentage and remaining time
            if self.position_state.track and hasattr(self.position_state.track, 'duration'):
                duration = getattr(self.position_state.track, 'duration', 180.0)
                if duration > 0:
                    self.position_state.position_percentage = min(1.0,
                        self.position_state.position_seconds / duration)
                    self.position_state.remaining_seconds = max(0,
                        duration - self.position_state.position_seconds)

            # Update beat information
            self._update_beat_info(status)

            # Update energy information
            self._update_energy_info(status)

            # Update structural information
            self._update_structural_info()

            # Update mix point information
            self._update_mix_point_info()

            self.last_update_time = time.time()

        except Exception as e:
            logger.debug(f"Position state update failed: {e}")

    def _update_beat_info(self, status: Dict[str, Any]):
        """Update beat-level timing information"""
        try:
            current_bpm = status.get('bpm', 128.0)
            if current_bpm <= 0:
                return

            # Calculate current beat based on position and BPM
            beats_per_second = current_bpm / 60.0
            total_beats = int(self.position_state.position_seconds * beats_per_second)

            self.position_state.current_beat = total_beats
            self.position_state.beats_until_phrase = (
                self.config['phrase_length_beats'] -
                (total_beats % self.config['phrase_length_beats'])
            )
            self.position_state.current_phrase = total_beats // self.config['phrase_length_beats']

        except Exception as e:
            logger.debug(f"Beat info update failed: {e}")

    def _update_energy_info(self, status: Dict[str, Any]):
        """Update energy and dynamics information"""
        try:
            # Get RMS level from status or audio analyzer
            new_rms = status.get('rms_level', 0.5)
            self.position_state.rms_level = new_rms

            # Calculate energy level (simplified)
            self.position_state.current_energy = min(10.0, max(1.0, new_rms * 10))

            # Calculate energy trend (basic moving average derivative)
            if hasattr(self, '_energy_history'):
                if len(self._energy_history) > 5:
                    recent_energy = sum(self._energy_history[-3:]) / 3
                    older_energy = sum(self._energy_history[-6:-3]) / 3
                    self.position_state.energy_trend = (recent_energy - older_energy) / 3.0
                    self.position_state.energy_trend = max(-1.0, min(1.0, self.position_state.energy_trend))
            else:
                self._energy_history = []

            self._energy_history.append(self.position_state.current_energy)
            if len(self._energy_history) > 20:
                self._energy_history.pop(0)

        except Exception as e:
            logger.debug(f"Energy info update failed: {e}")

    def _update_structural_info(self):
        """Update structural information (intro/outro/breakdown)"""
        try:
            if not self.position_state.track:
                return

            position = self.position_state.position_seconds
            duration = getattr(self.position_state.track, 'duration', 180.0)

            # Simple heuristics for structural elements
            self.position_state.in_intro = position < 32.0  # First 32 seconds
            self.position_state.in_outro = position > (duration - 32.0)  # Last 32 seconds

            # Breakdown/buildup detection based on energy trend
            if self.position_state.energy_trend < -0.5:
                self.position_state.in_breakdown = True
                self.position_state.in_buildup = False
            elif self.position_state.energy_trend > 0.5:
                self.position_state.in_breakdown = False
                self.position_state.in_buildup = True
            else:
                self.position_state.in_breakdown = False
                self.position_state.in_buildup = False

        except Exception as e:
            logger.debug(f"Structural info update failed: {e}")

    def _update_mix_point_info(self):
        """Update mix point and mix zone information"""
        try:
            if not self.position_state.track:
                return

            position = self.position_state.position_seconds

            # Check if we have optimal mix points from audio analysis
            if hasattr(self.position_state.track, 'optimal_mix_points'):
                mix_points = getattr(self.position_state.track, 'optimal_mix_points', [])

                if mix_points:
                    # Find next mix point
                    future_points = [mp for mp in mix_points if mp > position]
                    if future_points:
                        self.position_state.next_mix_point = min(future_points)
                        self.position_state.time_to_next_mix = self.position_state.next_mix_point - position

                        # Check if we're in a mix zone (within 10 seconds of optimal point)
                        self.position_state.in_mix_zone = self.position_state.time_to_next_mix <= 10.0
                    else:
                        # No more optimal points, check if we're in outro
                        duration = getattr(self.position_state.track, 'duration', 180.0)
                        if position > duration - 60.0:  # Last 60 seconds
                            self.position_state.in_mix_zone = True
                            self.position_state.time_to_next_mix = max(0, duration - position - 30.0)

        except Exception as e:
            logger.debug(f"Mix point info update failed: {e}")

    def _detect_mix_opportunities(self):
        """Detect and queue mix opportunities"""
        try:
            opportunities = []

            # 1. OPTIMAL MIX POINT DETECTION
            if (self.position_state.next_mix_point and
                self.position_state.time_to_next_mix and
                5.0 <= self.position_state.time_to_next_mix <= 15.0):

                opportunity = MixOpportunity(
                    alert_type=MixAlert.OPTIMAL_MIX_POINT,
                    position_seconds=self.position_state.position_seconds,
                    optimal_mix_window=(
                        self.position_state.next_mix_point - 5.0,
                        self.position_state.next_mix_point + 5.0
                    ),
                    confidence=0.9,
                    quality_score=0.9,
                    reasoning=f"Optimal mix point in {self.position_state.time_to_next_mix:.1f}s",
                    urgency_level=2,
                    expires_at=time.time() + self.position_state.time_to_next_mix + 5.0
                )
                opportunities.append(opportunity)

            # 2. PHRASE BOUNDARY DETECTION
            if self.position_state.beats_until_phrase <= 2:
                opportunity = MixOpportunity(
                    alert_type=MixAlert.BEAT_PHRASE_BOUNDARY,
                    position_seconds=self.position_state.position_seconds,
                    optimal_mix_window=(
                        self.position_state.position_seconds,
                        self.position_state.position_seconds + 4.0
                    ),
                    confidence=0.8,
                    quality_score=0.7,
                    reasoning=f"Phrase boundary in {self.position_state.beats_until_phrase} beats",
                    urgency_level=1,
                    expires_at=time.time() + 8.0
                )
                opportunities.append(opportunity)

            # 3. TRACK ENDING SOON
            if self.position_state.remaining_seconds <= self.config['emergency_threshold']:
                urgency = 4 if self.position_state.remaining_seconds <= 5.0 else 3

                opportunity = MixOpportunity(
                    alert_type=MixAlert.TRACK_ENDING_SOON,
                    position_seconds=self.position_state.position_seconds,
                    optimal_mix_window=(
                        self.position_state.position_seconds,
                        self.position_state.position_seconds + self.position_state.remaining_seconds
                    ),
                    confidence=1.0,
                    quality_score=0.5,
                    reasoning=f"Track ends in {self.position_state.remaining_seconds:.1f}s",
                    urgency_level=urgency,
                    expires_at=time.time() + self.position_state.remaining_seconds
                )
                opportunities.append(opportunity)

            # 4. ENERGY CHANGE DETECTION
            if abs(self.position_state.energy_trend) > self.config['energy_change_threshold']:
                trend_desc = "increasing" if self.position_state.energy_trend > 0 else "decreasing"

                opportunity = MixOpportunity(
                    alert_type=MixAlert.ENERGY_CHANGE_NEEDED,
                    position_seconds=self.position_state.position_seconds,
                    optimal_mix_window=(
                        self.position_state.position_seconds,
                        self.position_state.position_seconds + 20.0
                    ),
                    confidence=0.7,
                    quality_score=0.6,
                    reasoning=f"Energy {trend_desc} rapidly",
                    urgency_level=2,
                    expires_at=time.time() + 30.0
                )
                opportunities.append(opportunity)

            # Queue new opportunities and notify callbacks
            for opportunity in opportunities:
                if not self._is_duplicate_opportunity(opportunity):
                    self.mix_opportunities.put(opportunity)
                    self.detected_opportunities.append(opportunity)
                    self.metrics['mix_opportunities_detected'] += 1

                    # Notify callbacks
                    for callback in self.opportunity_callbacks:
                        try:
                            callback(opportunity)
                        except Exception as e:
                            logger.warning(f"⚠️ Opportunity callback failed: {e}")

            # Clean up expired opportunities
            self._cleanup_expired_opportunities()

        except Exception as e:
            logger.error(f"❌ Mix opportunity detection failed: {e}")

    def _is_duplicate_opportunity(self, new_opportunity: MixOpportunity) -> bool:
        """Check if this opportunity is a duplicate of recent ones"""
        try:
            current_time = time.time()
            recent_cutoff = current_time - 5.0  # Last 5 seconds

            for existing in self.detected_opportunities:
                if (existing.alert_type == new_opportunity.alert_type and
                    abs(existing.position_seconds - new_opportunity.position_seconds) < 2.0 and
                    existing.expires_at > recent_cutoff):
                    return True

            return False
        except:
            return False

    def _cleanup_expired_opportunities(self):
        """Remove expired opportunities"""
        try:
            current_time = time.time()
            self.detected_opportunities = [
                opp for opp in self.detected_opportunities
                if opp.expires_at > current_time
            ]
        except:
            pass

    def _analyze_current_audio(self):
        """Perform advanced audio analysis for mix point detection"""
        try:
            if not self.audio_analyzer:
                return

            # Get current audio features
            features = self.audio_analyzer.get_track_features()
            if not features:
                return

            # Update optimal mix points if available
            if hasattr(features, 'optimal_mix_points') and features.optimal_mix_points:
                if self.position_state.track:
                    # Update track with latest mix points
                    self.position_state.track.optimal_mix_points = features.optimal_mix_points

        except Exception as e:
            logger.debug(f"Audio analysis failed: {e}")

    def _update_metrics(self, start_time: float):
        """Update performance metrics"""
        try:
            self.metrics['total_updates'] += 1

            # Calculate update frequency
            if hasattr(self, '_last_metric_time'):
                time_diff = start_time - self._last_metric_time
                if time_diff > 0:
                    current_frequency = 1.0 / time_diff
                    if self.metrics['average_update_frequency'] == 0:
                        self.metrics['average_update_frequency'] = current_frequency
                    else:
                        # Moving average
                        alpha = 0.1
                        self.metrics['average_update_frequency'] = (
                            alpha * current_frequency +
                            (1 - alpha) * self.metrics['average_update_frequency']
                        )

            self._last_metric_time = start_time

        except Exception as e:
            logger.debug(f"Metrics update failed: {e}")

    def set_current_track(self, track: TrackInfo):
        """Set the currently monitored track"""
        try:
            logger.info(f"🎵 Now monitoring: {track.title} - {track.artist}")
            self.position_state.track = track

            # Reset position-dependent state
            self.position_state.position_seconds = 0.0
            self.position_state.position_percentage = 0.0
            self.position_state.current_beat = 0
            self.position_state.current_phrase = 0

            # Clear old opportunities
            while not self.mix_opportunities.empty():
                try:
                    self.mix_opportunities.get_nowait()
                except queue.Empty:
                    break

            self.detected_opportunities.clear()

        except Exception as e:
            logger.error(f"❌ Error setting current track: {e}")

    def add_opportunity_callback(self, callback: Callable[[MixOpportunity], None]):
        """Add callback for mix opportunity notifications"""
        self.opportunity_callbacks.append(callback)
        logger.info(f"➕ Added opportunity callback (total: {len(self.opportunity_callbacks)})")

    def remove_opportunity_callback(self, callback: Callable[[MixOpportunity], None]):
        """Remove opportunity callback"""
        if callback in self.opportunity_callbacks:
            self.opportunity_callbacks.remove(callback)
            logger.info(f"➖ Removed opportunity callback (total: {len(self.opportunity_callbacks)})")

    def get_next_opportunity(self, timeout: float = 1.0) -> Optional[MixOpportunity]:
        """Get the next mix opportunity from queue"""
        try:
            return self.mix_opportunities.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_current_state(self) -> PositionState:
        """Get current position state (copy)"""
        return PositionState(
            track=self.position_state.track,
            position_seconds=self.position_state.position_seconds,
            position_percentage=self.position_state.position_percentage,
            remaining_seconds=self.position_state.remaining_seconds,
            current_beat=self.position_state.current_beat,
            beats_until_phrase=self.position_state.beats_until_phrase,
            current_phrase=self.position_state.current_phrase,
            current_energy=self.position_state.current_energy,
            energy_trend=self.position_state.energy_trend,
            rms_level=self.position_state.rms_level,
            in_mix_zone=self.position_state.in_mix_zone,
            next_mix_point=self.position_state.next_mix_point,
            time_to_next_mix=self.position_state.time_to_next_mix,
            in_intro=self.position_state.in_intro,
            in_outro=self.position_state.in_outro,
            in_breakdown=self.position_state.in_breakdown,
            in_buildup=self.position_state.in_buildup
        )

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring performance statistics"""
        return {
            'is_monitoring': self.is_monitoring,
            'metrics': self.metrics.copy(),
            'opportunities_in_queue': self.mix_opportunities.qsize(),
            'opportunities_detected_total': len(self.detected_opportunities),
            'last_update_age': time.time() - self.last_update_time if self.last_update_time else 0
        }