#!/usr/bin/env python3
"""
🎵 Autonomous Audio Engine
Real-time audio analysis engine for autonomous DJ system
Provides beat detection, key analysis, energy monitoring, and structure analysis
"""

import librosa
import numpy as np
from scipy import signal
from typing import Dict, List, Optional, Tuple, NamedTuple
import threading
import time
import queue
from dataclasses import dataclass
from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

try:
    import essentia.standard as es
    ESSENTIA_AVAILABLE = True
except ImportError:
    print("⚠️  Essentia not available. Install with: pip install essentia")
    ESSENTIA_AVAILABLE = False

@dataclass
class AudioFeatures:
    """Complete audio analysis results for a track"""
    # Basic Properties
    duration: float
    sample_rate: int
    tempo: float
    key: str

    # Energy and Dynamics
    energy_level: float  # 1-10 scale
    rms_energy: np.ndarray
    spectral_centroid: np.ndarray

    # Rhythmic Features
    beat_times: np.ndarray
    onset_times: np.ndarray
    tempo_stability: float

    # Harmonic Features
    chroma: np.ndarray
    harmonic_compatibility: Dict[str, float]

    # Structural Analysis
    segment_boundaries: List[float]
    intro_duration: float
    outro_duration: float

    # Real-time Analysis
    current_position: float = 0.0
    current_energy: float = 5.0
    beats_until_phrase: int = 0
    optimal_mix_points: List[float] = None

class RealTimeAnalyzer:
    """Real-time audio analysis for live mixing decisions"""

    def __init__(self, sample_rate: int = 44100, frame_size: int = 2048):
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.hop_length = frame_size // 4

        # Real-time buffers
        self.audio_buffer = queue.Queue(maxsize=100)
        self.features_buffer = queue.Queue(maxsize=50)

        # Analysis state
        self.is_analyzing = False
        self.current_track_features = None

        # Threading
        self.analysis_thread = None
        self.stop_event = threading.Event()

        # Essentia analyzers (if available)
        if ESSENTIA_AVAILABLE:
            self.beat_tracker = es.BeatTrackerMultiFeature()
            self.key_detector = es.KeyExtractor()
            self.onset_detector = es.OnsetDetectionGlobal()

        print("🎵 Real-time Audio Analyzer initialized")

    def start_analysis(self, track_path: Optional[str] = None):
        """Start real-time analysis thread"""
        if self.is_analyzing:
            self.stop_analysis()

        self.is_analyzing = True
        self.stop_event.clear()

        if track_path:
            # Pre-analyze the track for structure
            self.current_track_features = self.analyze_track_structure(track_path)

        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()

        print(f"🔄 Started real-time analysis for: {track_path or 'live input'}")

    def stop_analysis(self):
        """Stop real-time analysis"""
        self.is_analyzing = False
        self.stop_event.set()

        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=2.0)

        print("⏹️  Stopped real-time analysis")

    def analyze_track_structure(self, track_path: str) -> AudioFeatures:
        """Complete structural analysis of a track"""
        try:
            # Load audio
            y, sr = librosa.load(track_path, sr=self.sample_rate)
            duration = librosa.get_duration(y=y, sr=sr)

            print(f"🔍 Analyzing track structure: {Path(track_path).name}")

            # Tempo and beat analysis
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units='frames')
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)

            # Key detection
            key = self._detect_key(y, sr)

            # Energy analysis
            rms = librosa.feature.rms(y=y, frame_length=self.frame_size, hop_length=self.hop_length)[0]
            energy_level = self._calculate_energy_level(rms)

            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0]

            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)

            # Chroma for harmonic analysis
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=self.hop_length)

            # Structural segmentation
            segment_boundaries = self._detect_segments(y, sr)
            intro_duration, outro_duration = self._detect_intro_outro(y, sr, beat_times)

            # Harmonic compatibility
            harmonic_compatibility = self._calculate_harmonic_compatibility(key)

            # Optimal mix points
            optimal_mix_points = self._find_optimal_mix_points(y, sr, beat_times, segment_boundaries)

            # Tempo stability
            tempo_stability = self._calculate_tempo_stability(beat_times)

            features = AudioFeatures(
                duration=duration,
                sample_rate=sr,
                tempo=tempo,
                key=key,
                energy_level=energy_level,
                rms_energy=rms,
                spectral_centroid=spectral_centroid,
                beat_times=beat_times,
                onset_times=onset_times,
                tempo_stability=tempo_stability,
                chroma=chroma,
                harmonic_compatibility=harmonic_compatibility,
                segment_boundaries=segment_boundaries,
                intro_duration=intro_duration,
                outro_duration=outro_duration,
                optimal_mix_points=optimal_mix_points
            )

            print(f"✅ Analysis complete: {tempo:.1f} BPM, Key: {key}, Energy: {energy_level:.1f}/10")
            return features

        except Exception as e:
            print(f"❌ Error analyzing track {track_path}: {e}")
            return None

    def _analysis_loop(self):
        """Main real-time analysis loop"""
        while not self.stop_event.is_set():
            try:
                # Get audio frame from buffer
                if not self.audio_buffer.empty():
                    audio_frame = self.audio_buffer.get_nowait()

                    # Analyze frame
                    frame_features = self._analyze_audio_frame(audio_frame)

                    # Update current track position and features
                    if self.current_track_features:
                        self._update_position_features(frame_features)

                    # Store results
                    if not self.features_buffer.full():
                        self.features_buffer.put_nowait(frame_features)

                time.sleep(0.01)  # 10ms loop for responsiveness

            except queue.Empty:
                time.sleep(0.005)
            except Exception as e:
                print(f"⚠️  Analysis loop error: {e}")
                time.sleep(0.1)

    def _analyze_audio_frame(self, audio_frame: np.ndarray) -> Dict:
        """Analyze single audio frame for real-time features"""
        try:
            # Basic energy analysis
            rms = np.sqrt(np.mean(audio_frame ** 2))
            energy = min(10.0, max(1.0, rms * 50))  # Scale to 1-10

            # Spectral centroid for brightness
            fft = np.abs(np.fft.rfft(audio_frame))
            freqs = np.fft.rfftfreq(len(audio_frame), 1/self.sample_rate)
            spectral_centroid = np.sum(freqs * fft) / np.sum(fft) if np.sum(fft) > 0 else 1000

            # Beat detection (simplified for real-time)
            beat_strength = self._detect_beat_strength(audio_frame)

            return {
                'timestamp': time.time(),
                'energy': energy,
                'spectral_centroid': spectral_centroid,
                'beat_strength': beat_strength,
                'rms': rms
            }

        except Exception as e:
            print(f"⚠️  Frame analysis error: {e}")
            return {'timestamp': time.time(), 'energy': 5.0, 'spectral_centroid': 1000, 'beat_strength': 0.5, 'rms': 0.1}

    def _detect_key(self, y: np.ndarray, sr: int) -> str:
        """Detect musical key of audio"""
        try:
            if ESSENTIA_AVAILABLE:
                # Use Essentia for professional key detection
                key, scale, strength = self.key_detector(y.astype(np.float32))
                return f"{key} {scale}"
            else:
                # Fallback: chroma-based key detection
                chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                chroma_mean = np.mean(chroma, axis=1)

                # Major keys
                major_profiles = np.array([
                    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],  # C major template
                ])

                key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

                best_correlation = -1
                best_key = 'C major'

                for shift in range(12):
                    profile = np.roll(major_profiles[0], shift)
                    correlation = np.corrcoef(chroma_mean, profile)[0, 1]
                    if correlation > best_correlation:
                        best_correlation = correlation
                        best_key = f"{key_names[shift]} major"

                return best_key

        except Exception as e:
            print(f"⚠️  Key detection error: {e}")
            return "C major"

    def _calculate_energy_level(self, rms: np.ndarray) -> float:
        """Calculate energy level on 1-10 scale"""
        try:
            # Normalize RMS to perceptual energy scale
            rms_db = librosa.amplitude_to_db(rms, ref=np.max)
            mean_energy = np.mean(rms_db)

            # Map dB range to 1-10 scale
            # Typical range: -60dB (quiet) to 0dB (loud)
            energy = 1 + (mean_energy + 60) / 60 * 9
            return max(1.0, min(10.0, energy))

        except Exception as e:
            print(f"⚠️  Energy calculation error: {e}")
            return 5.0

    def _detect_segments(self, y: np.ndarray, sr: int) -> List[float]:
        """Detect structural segments (intro, verse, chorus, etc.)"""
        try:
            # Use spectral features for segmentation
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

            # Compute self-similarity matrix
            S = librosa.segment.cross_similarity(mfcc, mfcc, metric='cosine')

            # Detect boundaries
            boundaries = librosa.segment.agglomerative(S, k=8)
            boundary_times = librosa.frames_to_time(boundaries, sr=sr)

            return boundary_times.tolist()

        except Exception as e:
            print(f"⚠️  Segment detection error: {e}")
            return [0.0]

    def _detect_intro_outro(self, y: np.ndarray, sr: int, beat_times: np.ndarray) -> Tuple[float, float]:
        """Detect intro and outro durations"""
        try:
            duration = librosa.get_duration(y=y, sr=sr)

            # Simple heuristic: intro is typically 16-32 beats
            beats_per_minute = len(beat_times) / (duration / 60)
            intro_beats = min(32, len(beat_times) // 8)
            outro_beats = min(32, len(beat_times) // 8)

            intro_duration = beat_times[intro_beats] if intro_beats < len(beat_times) else 30.0
            outro_start = beat_times[-outro_beats] if outro_beats < len(beat_times) else duration - 30.0
            outro_duration = duration - outro_start

            return intro_duration, outro_duration

        except Exception as e:
            print(f"⚠️  Intro/outro detection error: {e}")
            return 30.0, 30.0

    def _calculate_harmonic_compatibility(self, key: str) -> Dict[str, float]:
        """Calculate harmonic compatibility with other keys"""
        try:
            # Circle of fifths compatibility
            major_keys = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']

            current_key = key.split()[0]  # Extract key name

            if current_key not in major_keys:
                return {}

            current_index = major_keys.index(current_key)
            compatibility = {}

            for i, other_key in enumerate(major_keys):
                # Distance in circle of fifths
                distance = min(abs(i - current_index), 12 - abs(i - current_index))

                # Compatibility score (0-1)
                if distance == 0:
                    score = 1.0  # Same key
                elif distance == 1:
                    score = 0.9  # Adjacent fifths
                elif distance == 2:
                    score = 0.7  # Two steps
                elif distance <= 4:
                    score = 0.5  # Moderate compatibility
                else:
                    score = 0.2  # Low compatibility

                compatibility[f"{other_key} major"] = score

            return compatibility

        except Exception as e:
            print(f"⚠️  Harmonic compatibility error: {e}")
            return {}

    def _find_optimal_mix_points(self, y: np.ndarray, sr: int, beat_times: np.ndarray, segments: List[float]) -> List[float]:
        """Find optimal points for mixing in/out"""
        try:
            mix_points = []

            # Add segment boundaries as potential mix points
            for segment_time in segments:
                if 30 < segment_time < len(y)/sr - 30:  # Avoid too early/late
                    mix_points.append(segment_time)

            # Add phrase boundaries (every 16 beats)
            phrase_length = 16
            for i in range(phrase_length, len(beat_times) - phrase_length, phrase_length):
                mix_points.append(beat_times[i])

            # Sort and remove duplicates
            mix_points = sorted(list(set(mix_points)))

            return mix_points[:20]  # Limit to 20 best points

        except Exception as e:
            print(f"⚠️  Mix point detection error: {e}")
            return []

    def _calculate_tempo_stability(self, beat_times: np.ndarray) -> float:
        """Calculate how stable the tempo is (0-1)"""
        try:
            if len(beat_times) < 4:
                return 0.5

            # Calculate beat intervals
            intervals = np.diff(beat_times)

            # Coefficient of variation (lower = more stable)
            cv = np.std(intervals) / np.mean(intervals)

            # Convert to stability score (0-1)
            stability = max(0, 1 - cv * 5)  # Scale factor

            return stability

        except Exception as e:
            print(f"⚠️  Tempo stability error: {e}")
            return 0.5

    def _detect_beat_strength(self, audio_frame: np.ndarray) -> float:
        """Detect beat strength in audio frame"""
        try:
            # Simple onset strength using spectral flux
            fft = np.abs(np.fft.rfft(audio_frame))

            if hasattr(self, '_prev_fft'):
                # Spectral flux (positive differences)
                flux = np.sum(np.maximum(0, fft - self._prev_fft))
                beat_strength = min(1.0, flux / (np.sum(fft) + 1e-6))
            else:
                beat_strength = 0.5

            self._prev_fft = fft
            return beat_strength

        except Exception as e:
            return 0.5

    def _update_position_features(self, frame_features: Dict):
        """Update current position and contextual features"""
        if not self.current_track_features:
            return

        try:
            # Update current energy
            self.current_track_features.current_energy = frame_features['energy']

            # Estimate current position (simplified)
            # In real implementation, this would come from Traktor
            self.current_track_features.current_position += 0.01  # Assume 10ms frames

            # Calculate beats until next phrase
            current_time = self.current_track_features.current_position
            beat_times = self.current_track_features.beat_times

            # Find next beat after current position
            future_beats = beat_times[beat_times > current_time]
            if len(future_beats) > 0:
                # Find next phrase boundary (every 16 beats)
                current_beat_index = len(beat_times) - len(future_beats)
                beats_to_phrase = 16 - (current_beat_index % 16)
                self.current_track_features.beats_until_phrase = beats_to_phrase

        except Exception as e:
            print(f"⚠️  Position update error: {e}")

    def get_current_analysis(self) -> Optional[Dict]:
        """Get latest real-time analysis results"""
        try:
            if not self.features_buffer.empty():
                return self.features_buffer.get_nowait()
            return None
        except queue.Empty:
            return None

    def get_track_features(self) -> Optional[AudioFeatures]:
        """Get current track's complete features"""
        return self.current_track_features

    def is_optimal_mix_point(self, current_time: float, tolerance: float = 2.0) -> bool:
        """Check if current time is near an optimal mix point"""
        if not self.current_track_features or not self.current_track_features.optimal_mix_points:
            return False

        for mix_point in self.current_track_features.optimal_mix_points:
            if abs(current_time - mix_point) <= tolerance:
                return True

        return False

    def add_audio_frame(self, audio_data: np.ndarray):
        """Add audio frame to analysis buffer"""
        try:
            if not self.audio_buffer.full():
                self.audio_buffer.put_nowait(audio_data)
        except queue.Full:
            # Drop frame if buffer is full
            pass

def test_audio_engine():
    """Test the autonomous audio engine"""
    print("🧪 Testing Autonomous Audio Engine")
    print("=" * 50)

    analyzer = RealTimeAnalyzer()

    # Test with a sample file (if available)
    test_files = [
        "/Users/Fiore/Music/test.mp3",
        "/System/Library/Sounds/Sosumi.aiff"
    ]

    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n🎵 Testing with: {test_file}")

            # Analyze track structure
            features = analyzer.analyze_track_structure(test_file)

            if features:
                print(f"✅ Analysis successful:")
                print(f"  Duration: {features.duration:.1f}s")
                print(f"  Tempo: {features.tempo:.1f} BPM")
                print(f"  Key: {features.key}")
                print(f"  Energy: {features.energy_level:.1f}/10")
                print(f"  Intro: {features.intro_duration:.1f}s")
                print(f"  Outro: {features.outro_duration:.1f}s")
                print(f"  Mix points: {len(features.optimal_mix_points)}")
                print(f"  Tempo stability: {features.tempo_stability:.2f}")

            break
    else:
        print("⚠️  No test audio files found")

    print("\n✅ Audio engine test complete!")

if __name__ == "__main__":
    test_audio_engine()