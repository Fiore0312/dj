#!/usr/bin/env python3
"""
🎵 Enhanced Track Selection System
Advanced track selection with harmonic compatibility, energy curve analysis,
and machine learning-based preferences for autonomous DJ system
"""

import time
import math
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np

# Core imports
try:
    from music_library import MusicLibraryScanner, TrackInfo
    from ai_dj_agent import DJContext
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CompatibilityType(Enum):
    """Types of track compatibility"""
    HARMONIC = "harmonic"
    RHYTHMIC = "rhythmic"
    ENERGY = "energy"
    GENRE = "genre"
    STRUCTURAL = "structural"

@dataclass
class CompatibilityScore:
    """Detailed compatibility scoring between tracks"""
    total_score: float = 0.0
    harmonic_score: float = 0.0
    rhythmic_score: float = 0.0
    energy_score: float = 0.0
    genre_score: float = 0.0
    structural_score: float = 0.0
    crowd_score: float = 0.0
    novelty_score: float = 0.0
    confidence: float = 0.8

@dataclass
class EnergyPoint:
    """Energy level at specific time in set"""
    time_minutes: float
    target_energy: float
    tolerance: float = 0.5

@dataclass
class TrackHistory:
    """Track play history and performance metrics"""
    track: TrackInfo
    played_times: List[float] = field(default_factory=list)
    successful_transitions_from: List[str] = field(default_factory=list)
    successful_transitions_to: List[str] = field(default_factory=list)
    crowd_response_scores: List[float] = field(default_factory=list)
    average_mix_quality: float = 0.8

class EnhancedTrackSelector:
    """
    Advanced track selection system that uses:
    - Harmonic mixing (Circle of Fifths compatibility)
    - Energy curve progression analysis
    - Structural analysis for optimal mix points
    - Machine learning from successful mixes
    - Real-time crowd response simulation
    """

    def __init__(self, music_scanner: Optional[MusicLibraryScanner] = None):
        self.music_scanner = music_scanner

        # Advanced compatibility matrices
        self.harmonic_compatibility = self._build_harmonic_compatibility_matrix()
        self.genre_compatibility = self._build_genre_compatibility_matrix()

        # Learning systems
        self.track_history: Dict[str, TrackHistory] = {}
        self.successful_combinations: Dict[Tuple[str, str], float] = {}

        # Energy curve templates for different event types
        self.energy_curves = self._build_energy_curve_templates()

        # Performance tracking
        self.selection_metrics = {
            'total_selections': 0,
            'successful_selections': 0,
            'crowd_satisfaction_avg': 0.8,
            'mix_quality_avg': 0.8
        }

        logger.info("🎵 Enhanced Track Selector initialized")

    def select_next_track(self, current_track: TrackInfo, context: DJContext,
                         candidates: Optional[List[TrackInfo]] = None,
                         exclude_recent: bool = True) -> Optional[TrackInfo]:
        """
        Select the optimal next track using advanced compatibility analysis

        Args:
            current_track: Currently playing track
            context: Current DJ context (venue, energy, etc.)
            candidates: Optional list of candidate tracks (if None, uses full library)
            exclude_recent: Whether to exclude recently played tracks

        Returns:
            Optimal next track or None if no suitable track found
        """
        try:
            if not candidates and self.music_scanner:
                candidates = self.music_scanner.tracks

            if not candidates:
                logger.warning("⚠️ No candidate tracks available")
                return None

            logger.info(f"🎯 Selecting next track after: {current_track.title}")
            logger.info(f"📊 Analyzing {len(candidates)} candidates")

            # Filter candidates
            filtered_candidates = self._filter_candidates(
                candidates, current_track, context, exclude_recent
            )

            logger.info(f"🔍 Filtered to {len(filtered_candidates)} suitable candidates")

            if not filtered_candidates:
                # Emergency fallback - relax constraints
                filtered_candidates = candidates[:20]  # Top 20 as emergency

            # Score all candidates
            scored_tracks = []
            for candidate in filtered_candidates:
                compatibility = self._calculate_comprehensive_compatibility(
                    current_track, candidate, context
                )
                scored_tracks.append((compatibility.total_score, candidate, compatibility))

            # Sort by total score
            scored_tracks.sort(reverse=True, key=lambda x: x[0])

            # Select best track with some randomization for creativity
            best_tracks = scored_tracks[:5]  # Top 5 candidates

            # Weighted random selection from top candidates
            weights = [score for score, _, _ in best_tracks]
            if weights:
                selected_idx = self._weighted_random_choice(weights)
                selected_track = best_tracks[selected_idx][1]
                selected_compatibility = best_tracks[selected_idx][2]

                # Log selection reasoning
                logger.info(f"✅ Selected: {selected_track.title} - {selected_track.artist}")
                logger.info(f"📈 Compatibility scores: H:{selected_compatibility.harmonic_score:.1f} "
                          f"R:{selected_compatibility.rhythmic_score:.1f} "
                          f"E:{selected_compatibility.energy_score:.1f} "
                          f"Total:{selected_compatibility.total_score:.1f}")

                # Update learning data
                self._record_selection(current_track, selected_track, selected_compatibility)

                return selected_track

            return None

        except Exception as e:
            logger.error(f"❌ Track selection failed: {e}")
            return None

    def _calculate_comprehensive_compatibility(self, current_track: TrackInfo,
                                             candidate_track: TrackInfo,
                                             context: DJContext) -> CompatibilityScore:
        """Calculate comprehensive compatibility between two tracks"""
        try:
            score = CompatibilityScore()

            # 1. HARMONIC COMPATIBILITY (25% weight)
            score.harmonic_score = self._calculate_harmonic_compatibility(
                current_track, candidate_track
            ) * 25.0

            # 2. RHYTHMIC COMPATIBILITY (20% weight)
            score.rhythmic_score = self._calculate_rhythmic_compatibility(
                current_track, candidate_track
            ) * 20.0

            # 3. ENERGY PROGRESSION (20% weight)
            score.energy_score = self._calculate_energy_compatibility(
                current_track, candidate_track, context
            ) * 20.0

            # 4. GENRE COMPATIBILITY (15% weight)
            score.genre_score = self._calculate_genre_compatibility(
                current_track, candidate_track, context
            ) * 15.0

            # 5. STRUCTURAL COMPATIBILITY (10% weight)
            score.structural_score = self._calculate_structural_compatibility(
                current_track, candidate_track
            ) * 10.0

            # 6. CROWD RESPONSE PREDICTION (5% weight)
            score.crowd_score = self._predict_crowd_response(
                current_track, candidate_track, context
            ) * 5.0

            # 7. NOVELTY FACTOR (5% weight)
            score.novelty_score = self._calculate_novelty_score(candidate_track) * 5.0

            # Total score
            score.total_score = (score.harmonic_score + score.rhythmic_score +
                               score.energy_score + score.genre_score +
                               score.structural_score + score.crowd_score +
                               score.novelty_score)

            # Apply learning-based adjustments
            score = self._apply_learning_adjustments(score, current_track, candidate_track)

            return score

        except Exception as e:
            logger.error(f"❌ Compatibility calculation failed: {e}")
            return CompatibilityScore()

    def _calculate_harmonic_compatibility(self, track1: TrackInfo, track2: TrackInfo) -> float:
        """Calculate harmonic compatibility using Circle of Fifths"""
        try:
            if not (hasattr(track1, 'key') and hasattr(track2, 'key')):
                return 0.5  # Neutral score if keys unknown

            key1 = getattr(track1, 'key', 'C')
            key2 = getattr(track2, 'key', 'C')

            if not key1 or not key2:
                return 0.5

            # Use advanced harmonic compatibility matrix
            compatibility = self.harmonic_compatibility.get(key1, {}).get(key2, 0.5)

            # Boost for perfect matches
            if key1 == key2:
                compatibility = min(1.0, compatibility + 0.2)

            return compatibility

        except Exception as e:
            logger.debug(f"Harmonic compatibility calculation failed: {e}")
            return 0.5

    def _calculate_rhythmic_compatibility(self, track1: TrackInfo, track2: TrackInfo) -> float:
        """Calculate rhythmic compatibility based on BPM and time signatures"""
        try:
            if not (hasattr(track1, 'bpm') and hasattr(track2, 'bpm')):
                return 0.5

            bpm1 = getattr(track1, 'bpm', 128.0)
            bpm2 = getattr(track2, 'bpm', 128.0)

            if not bpm1 or not bpm2:
                return 0.5

            # Calculate BPM compatibility
            bpm_diff = abs(bpm1 - bpm2)

            # Perfect match
            if bpm_diff == 0:
                return 1.0

            # Harmonic BPM relationships (double/half time)
            if abs(bpm1 - bpm2 * 2) < 2 or abs(bpm2 - bpm1 * 2) < 2:
                return 0.9

            # 3/4 time relationships
            if abs(bpm1 - bpm2 * 1.5) < 2 or abs(bpm2 - bpm1 * 1.5) < 2:
                return 0.8

            # Linear compatibility based on BPM difference
            if bpm_diff <= 3:
                return 1.0 - (bmp_diff / 10.0)
            elif bpm_diff <= 6:
                return 0.8 - (bpm_diff - 3) / 15.0
            elif bmp_diff <= 12:
                return 0.6 - (bpm_diff - 6) / 20.0
            else:
                return max(0.2, 0.6 - (bpm_diff - 12) / 30.0)

        except Exception as e:
            logger.debug(f"Rhythmic compatibility calculation failed: {e}")
            return 0.5

    def _calculate_energy_compatibility(self, track1: TrackInfo, track2: TrackInfo,
                                      context: DJContext) -> float:
        """Calculate energy progression compatibility"""
        try:
            if not (hasattr(track1, 'energy') and hasattr(track2, 'energy')):
                return 0.5

            current_energy = getattr(track1, 'energy', 5.0)
            next_energy = getattr(track2, 'energy', 5.0)

            # Get target energy for this point in set
            target_energy = self._get_target_energy_for_time(context)

            # Calculate how well the next track fits the energy curve
            energy_diff_from_target = abs(next_energy - target_energy)
            target_score = max(0.0, 1.0 - energy_diff_from_target / 5.0)

            # Calculate energy progression appropriateness
            energy_change = next_energy - current_energy

            # Evaluate based on event type and timing
            if context.event_type == 'warm_up':
                # Gradual build preferred
                if 0.5 <= energy_change <= 1.5:
                    progression_score = 1.0
                elif -0.5 <= energy_change <= 2.0:
                    progression_score = 0.8
                else:
                    progression_score = 0.4

            elif context.event_type == 'prime_time':
                # Maintain high energy with strategic peaks
                if -0.5 <= energy_change <= 1.0:
                    progression_score = 1.0
                elif -1.0 <= energy_change <= 1.5:
                    progression_score = 0.8
                else:
                    progression_score = 0.5

            elif context.event_type == 'closing':
                # Gradual wind down
                if -1.5 <= energy_change <= 0.0:
                    progression_score = 1.0
                elif -2.0 <= energy_change <= 0.5:
                    progression_score = 0.8
                else:
                    progression_score = 0.4
            else:
                # Default: slight preference for building
                if 0.0 <= energy_change <= 1.0:
                    progression_score = 1.0
                elif -0.5 <= energy_change <= 1.5:
                    progression_score = 0.8
                else:
                    progression_score = 0.5

            # Combine target fit and progression appropriateness
            return (target_score * 0.6) + (progression_score * 0.4)

        except Exception as e:
            logger.debug(f"Energy compatibility calculation failed: {e}")
            return 0.5

    def _calculate_genre_compatibility(self, track1: TrackInfo, track2: TrackInfo,
                                     context: DJContext) -> float:
        """Calculate genre compatibility and flow"""
        try:
            if not (hasattr(track1, 'genre') and hasattr(track2, 'genre')):
                return 0.5

            genre1 = getattr(track1, 'genre', '').lower()
            genre2 = getattr(track2, 'genre', '').lower()

            if not genre1 or not genre2:
                return 0.5

            # Use genre compatibility matrix
            compatibility = self.genre_compatibility.get(genre1, {}).get(genre2, 0.5)

            # Context-based adjustments
            if context.venue_type == 'club':
                # Club prefers electronic genres
                if genre2 in ['house', 'techno', 'tech house', 'deep house', 'progressive house']:
                    compatibility = min(1.0, compatibility + 0.1)
            elif context.venue_type == 'bar':
                # Bar prefers more chill genres
                if genre2 in ['chill', 'nu-disco', 'lounge', 'downtempo']:
                    compatibility = min(1.0, compatibility + 0.1)

            return compatibility

        except Exception as e:
            logger.debug(f"Genre compatibility calculation failed: {e}")
            return 0.5

    def _calculate_structural_compatibility(self, track1: TrackInfo, track2: TrackInfo) -> float:
        """Calculate structural mixing compatibility"""
        try:
            # Check for optimal mix points if available
            if (hasattr(track1, 'optimal_mix_points') and
                hasattr(track2, 'intro_duration')):

                mix_points = getattr(track1, 'optimal_mix_points', [])
                intro_duration = getattr(track2, 'intro_duration', 16.0)

                if mix_points and intro_duration:
                    # Good structural compatibility if intro matches mix points
                    if intro_duration >= 16.0:  # Sufficient intro for mixing
                        return 0.9
                    elif intro_duration >= 8.0:
                        return 0.7
                    else:
                        return 0.4

            # Default structural score based on track lengths
            duration1 = getattr(track1, 'duration', 180.0)
            duration2 = getattr(track2, 'duration', 180.0)

            if duration1 > 60.0 and duration2 > 60.0:  # Both tracks long enough for mixing
                return 0.8
            else:
                return 0.5

        except Exception as e:
            logger.debug(f"Structural compatibility calculation failed: {e}")
            return 0.5

    def _predict_crowd_response(self, track1: TrackInfo, track2: TrackInfo,
                              context: DJContext) -> float:
        """Predict crowd response to track selection"""
        try:
            # Simple crowd response simulation based on context
            base_score = 0.7

            # Energy level appropriateness
            if hasattr(track2, 'energy'):
                track_energy = getattr(track2, 'energy', 5.0)

                if context.venue_type == 'club':
                    if 6.0 <= track_energy <= 9.0:
                        base_score += 0.2
                elif context.venue_type == 'bar':
                    if 4.0 <= track_energy <= 7.0:
                        base_score += 0.2

            # Genre popularity for venue
            if hasattr(track2, 'genre'):
                genre = getattr(track2, 'genre', '').lower()
                if context.venue_type == 'club' and genre in ['house', 'techno']:
                    base_score += 0.1
                elif context.venue_type == 'bar' and genre in ['chill', 'nu-disco']:
                    base_score += 0.1

            # Time-based adjustments
            if context.event_type == 'prime_time':
                base_score += 0.1  # Prime time gets boost

            return min(1.0, base_score)

        except Exception as e:
            logger.debug(f"Crowd response prediction failed: {e}")
            return 0.7

    def _calculate_novelty_score(self, track: TrackInfo) -> float:
        """Calculate novelty/freshness score"""
        try:
            track_id = track.filepath

            if track_id in self.track_history:
                history = self.track_history[track_id]

                # Reduce score based on recent plays
                recent_plays = [t for t in history.played_times if time.time() - t < 3600]  # Last hour

                if len(recent_plays) == 0:
                    return 1.0
                elif len(recent_plays) == 1:
                    return 0.7
                elif len(recent_plays) == 2:
                    return 0.4
                else:
                    return 0.1  # Heavily played recently
            else:
                return 1.0  # Never played

        except Exception as e:
            logger.debug(f"Novelty score calculation failed: {e}")
            return 0.8

    def _build_harmonic_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build comprehensive harmonic compatibility matrix"""
        # Circle of Fifths based compatibility
        compatibility_matrix = {
            'C': {'C': 1.0, 'G': 0.9, 'F': 0.9, 'Am': 0.9, 'Em': 0.8, 'Dm': 0.8, 'D': 0.7, 'A': 0.6},
            'G': {'G': 1.0, 'D': 0.9, 'C': 0.9, 'Em': 0.9, 'Bm': 0.8, 'Am': 0.8, 'A': 0.7, 'E': 0.6},
            'D': {'D': 1.0, 'A': 0.9, 'G': 0.9, 'Bm': 0.9, 'F#m': 0.8, 'Em': 0.8, 'E': 0.7, 'B': 0.6},
            'A': {'A': 1.0, 'E': 0.9, 'D': 0.9, 'F#m': 0.9, 'C#m': 0.8, 'Bm': 0.8, 'B': 0.7, 'F#': 0.6},
            'E': {'E': 1.0, 'B': 0.9, 'A': 0.9, 'C#m': 0.9, 'G#m': 0.8, 'F#m': 0.8, 'F#': 0.7, 'C#': 0.6},

            # Minor keys
            'Am': {'Am': 1.0, 'Em': 0.9, 'Dm': 0.9, 'C': 0.9, 'G': 0.8, 'F': 0.8, 'Bm': 0.7, 'E': 0.6},
            'Em': {'Em': 1.0, 'Bm': 0.9, 'Am': 0.9, 'G': 0.9, 'D': 0.8, 'C': 0.8, 'F#m': 0.7, 'B': 0.6},
            'Bm': {'Bm': 1.0, 'F#m': 0.9, 'Em': 0.9, 'D': 0.9, 'A': 0.8, 'G': 0.8, 'C#m': 0.7, 'F#': 0.6},

            # Add more keys as needed...
        }

        # Add symmetric relationships and defaults
        all_keys = list(compatibility_matrix.keys())
        for key1 in all_keys:
            if key1 not in compatibility_matrix:
                compatibility_matrix[key1] = {}
            for key2 in all_keys:
                if key2 not in compatibility_matrix[key1]:
                    # Use reverse lookup or default
                    if key2 in compatibility_matrix and key1 in compatibility_matrix[key2]:
                        compatibility_matrix[key1][key2] = compatibility_matrix[key2][key1]
                    else:
                        compatibility_matrix[key1][key2] = 0.5  # Default

        return compatibility_matrix

    def _build_genre_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build genre compatibility matrix"""
        return {
            'house': {'house': 1.0, 'deep house': 0.9, 'tech house': 0.8, 'progressive house': 0.8, 'techno': 0.7},
            'techno': {'techno': 1.0, 'tech house': 0.9, 'house': 0.7, 'minimal': 0.8, 'progressive techno': 0.9},
            'deep house': {'deep house': 1.0, 'house': 0.9, 'nu-disco': 0.8, 'chill': 0.7, 'lounge': 0.6},
            'trance': {'trance': 1.0, 'progressive trance': 0.9, 'uplifting trance': 0.8, 'psytrance': 0.7},
            'chill': {'chill': 1.0, 'lounge': 0.9, 'downtempo': 0.8, 'ambient': 0.7, 'deep house': 0.6},
            # Add more genres...
        }

    def _build_energy_curve_templates(self) -> Dict[str, List[EnergyPoint]]:
        """Build energy curve templates for different event types"""
        return {
            'warm_up': [
                EnergyPoint(0, 3.0), EnergyPoint(15, 4.0),
                EnergyPoint(30, 5.0), EnergyPoint(45, 6.0)
            ],
            'prime_time': [
                EnergyPoint(0, 7.0), EnergyPoint(20, 8.0),
                EnergyPoint(40, 8.5), EnergyPoint(60, 8.0), EnergyPoint(80, 7.5)
            ],
            'closing': [
                EnergyPoint(0, 8.0), EnergyPoint(15, 7.0),
                EnergyPoint(30, 6.0), EnergyPoint(45, 5.0), EnergyPoint(60, 4.0)
            ]
        }

    def _get_target_energy_for_time(self, context: DJContext) -> float:
        """Get target energy level for current time in set"""
        try:
            time_in_set = context.time_in_set
            event_type = context.event_type

            if event_type not in self.energy_curves:
                return 6.0  # Default

            curve = self.energy_curves[event_type]

            # Find appropriate energy point
            for i, point in enumerate(curve):
                if time_in_set <= point.time_minutes:
                    if i == 0:
                        return point.target_energy
                    else:
                        # Interpolate between points
                        prev_point = curve[i-1]
                        ratio = (time_in_set - prev_point.time_minutes) / (point.time_minutes - prev_point.time_minutes)
                        return prev_point.target_energy + (point.target_energy - prev_point.target_energy) * ratio

            # Beyond last point, use last energy
            return curve[-1].target_energy

        except Exception as e:
            logger.debug(f"Target energy calculation failed: {e}")
            return 6.0

    def _filter_candidates(self, candidates: List[TrackInfo], current_track: TrackInfo,
                          context: DJContext, exclude_recent: bool) -> List[TrackInfo]:
        """Filter candidate tracks based on basic constraints"""
        filtered = []

        for candidate in candidates:
            # Skip current track
            if candidate.filepath == current_track.filepath:
                continue

            # Skip recently played tracks
            if exclude_recent and self._was_played_recently(candidate):
                continue

            # Basic compatibility filters
            if hasattr(candidate, 'bmp') and hasattr(current_track, 'bpm'):
                bmp_diff = abs(candidate.bmp - current_track.bpm)
                if bpm_diff > 20:  # Skip tracks with very different BPM
                    continue

            filtered.append(candidate)

        return filtered

    def _was_played_recently(self, track: TrackInfo, hours: float = 2.0) -> bool:
        """Check if track was played recently"""
        track_id = track.filepath
        if track_id in self.track_history:
            recent_cutoff = time.time() - (hours * 3600)
            recent_plays = [t for t in self.track_history[track_id].played_times if t > recent_cutoff]
            return len(recent_plays) > 0
        return False

    def _weighted_random_choice(self, weights: List[float]) -> int:
        """Select index using weighted random choice"""
        total_weight = sum(weights)
        if total_weight <= 0:
            return 0

        r = np.random.random() * total_weight
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return i
        return len(weights) - 1

    def _apply_learning_adjustments(self, score: CompatibilityScore,
                                  current_track: TrackInfo,
                                  candidate_track: TrackInfo) -> CompatibilityScore:
        """Apply machine learning adjustments based on historical performance"""
        try:
            # Check for successful historical combinations
            combination_key = (current_track.filepath, candidate_track.filepath)
            if combination_key in self.successful_combinations:
                historical_success = self.successful_combinations[combination_key]
                # Boost score based on historical success
                score.total_score *= (1.0 + historical_success * 0.2)

            return score
        except:
            return score

    def _record_selection(self, from_track: TrackInfo, selected_track: TrackInfo,
                         compatibility: CompatibilityScore):
        """Record track selection for learning purposes"""
        try:
            # Update track history
            track_id = selected_track.filepath
            if track_id not in self.track_history:
                self.track_history[track_id] = TrackHistory(selected_track)

            self.track_history[track_id].played_times.append(time.time())

            # Update selection metrics
            self.selection_metrics['total_selections'] += 1

            logger.info(f"📝 Recorded selection: {from_track.title} → {selected_track.title}")

        except Exception as e:
            logger.debug(f"Selection recording failed: {e}")

    def record_transition_success(self, from_track: TrackInfo, to_track: TrackInfo,
                                success: bool, quality_score: float = 0.8):
        """Record transition success for learning"""
        try:
            combination_key = (from_track.filepath, to_track.filepath)

            if success:
                # Update successful combinations
                if combination_key in self.successful_combinations:
                    # Running average
                    current_score = self.successful_combinations[combination_key]
                    self.successful_combinations[combination_key] = (current_score + quality_score) / 2
                else:
                    self.successful_combinations[combination_key] = quality_score

                # Update track history
                from_track_id = from_track.filepath
                to_track_id = to_track.filepath

                if from_track_id in self.track_history:
                    self.track_history[from_track_id].successful_transitions_to.append(to_track_id)

                if to_track_id in self.track_history:
                    self.track_history[to_track_id].successful_transitions_from.append(from_track_id)
                    self.track_history[to_track_id].crowd_response_scores.append(quality_score)

            logger.info(f"📊 Recorded transition: {from_track.title} → {to_track.title} "
                      f"(Success: {success}, Quality: {quality_score})")

        except Exception as e:
            logger.debug(f"Transition success recording failed: {e}")

    def get_queue_recommendations(self, current_track: TrackInfo, context: DJContext,
                                 queue_length: int = 5) -> List[TrackInfo]:
        """Get recommended tracks for queue (next 3-5 tracks)"""
        try:
            recommendations = []
            virtual_current = current_track
            virtual_context = context

            for i in range(queue_length):
                next_track = self.select_next_track(
                    virtual_current, virtual_context,
                    exclude_recent=(i == 0)  # Only exclude recent for immediate next
                )

                if next_track:
                    recommendations.append(next_track)
                    virtual_current = next_track
                    # Update virtual context for next iteration
                    virtual_context.time_in_set += 4  # Assume ~4 min per track
                    if hasattr(next_track, 'energy'):
                        virtual_context.energy_level = int(getattr(next_track, 'energy', 5.0))
                else:
                    break

            logger.info(f"🎵 Generated {len(recommendations)} track recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"❌ Queue recommendations failed: {e}")
            return []

    def get_selection_stats(self) -> Dict[str, Any]:
        """Get current selection performance statistics"""
        return {
            'selection_metrics': self.selection_metrics.copy(),
            'tracks_in_history': len(self.track_history),
            'successful_combinations': len(self.successful_combinations),
            'avg_compatibility_score': self._calculate_average_compatibility()
        }

    def _calculate_average_compatibility(self) -> float:
        """Calculate average compatibility score from successful combinations"""
        if not self.successful_combinations:
            return 0.8
        return sum(self.successful_combinations.values()) / len(self.successful_combinations)