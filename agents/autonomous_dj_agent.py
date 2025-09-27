#!/usr/bin/env python3
"""
🎧 Autonomous DJ Agent - Claude AI Powered
Professional AI DJ system with real-time decision making and mixing intelligence
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import threading
from pathlib import Path

# Import core Claude AI components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    SDKMasterAgent, DJContext, AIResponse, DJTaskType,
    get_sdk_master, validate_api_key
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DJState(Enum):
    """Current state of the DJ system"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    MIXING = "mixing"
    TRANSITIONING = "transitioning"
    PAUSED = "paused"
    ERROR = "error"

class MixingStyle(Enum):
    """Different mixing approaches"""
    QUICK_CUT = "quick_cut"
    BEATMATCH = "beatmatch"
    HARMONIC = "harmonic"
    EXTENDED = "extended"
    CREATIVE = "creative"

@dataclass
class Track:
    """Enhanced track representation"""
    id: str
    title: str
    artist: str
    file_path: str
    duration: float = 0.0
    bpm: Optional[float] = None
    key: Optional[str] = None
    genre: Optional[str] = None
    energy_level: float = 0.5  # 0-1 scale
    vocal_presence: bool = False
    intro_length: float = 0.0
    outro_length: float = 0.0
    breakdown_points: List[float] = None
    mix_in_point: float = 0.0
    mix_out_point: float = 0.0
    ai_analysis: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.breakdown_points is None:
            self.breakdown_points = []

@dataclass
class MixSession:
    """Current mixing session state"""
    session_id: str
    start_time: float
    current_deck: str = "A"
    deck_a_track: Optional[Track] = None
    deck_b_track: Optional[Track] = None
    crossfader_position: float = 0.0  # -1 (A) to 1 (B)
    track_queue: List[Track] = None
    played_tracks: List[Track] = None
    set_duration_target: int = 60  # minutes
    venue_type: str = "club"
    crowd_energy: float = 0.5

    def __post_init__(self):
        if self.track_queue is None:
            self.track_queue = []
        if self.played_tracks is None:
            self.played_tracks = []

class AutonomousDJAgent:
    """
    Professional AI-powered DJ system using Claude for intelligent decision making
    """

    def __init__(self, music_library_path: Optional[str] = None):
        """Initialize the Autonomous DJ Agent"""
        self.sdk_master = get_sdk_master()
        self.state = DJState.IDLE
        self.mix_session: Optional[MixSession] = None
        self.music_library_path = music_library_path
        self.track_library: Dict[str, Track] = {}
        self.performance_stats = {
            'tracks_played': 0,
            'successful_transitions': 0,
            'crowd_satisfaction': 0.0,
            'ai_decisions_made': 0,
            'average_response_time': 0.0
        }

        # AI decision cache for performance
        self.decision_cache: Dict[str, AIResponse] = {}
        self.cache_ttl = 300  # 5 minutes

        # Real-time mixing parameters
        self.mixing_style = MixingStyle.HARMONIC
        self.auto_gain_control = True
        self.harmonic_mixing = True
        self.energy_flow_management = True

        logger.info("🎧 Autonomous DJ Agent initialized with Claude AI")

    async def start_dj_session(self, session_config: Dict[str, Any]) -> bool:
        """Start a new DJ session"""
        try:
            self.state = DJState.ANALYZING

            # Create new mix session
            session_id = f"session_{int(time.time())}"
            self.mix_session = MixSession(
                session_id=session_id,
                start_time=time.time(),
                set_duration_target=session_config.get('duration', 60),
                venue_type=session_config.get('venue', 'club')
            )

            # Update Claude AI context
            self.sdk_master.update_dj_context(
                venue_type=self.mix_session.venue_type,
                time_in_set=0,
                crowd_energy=self.mix_session.crowd_energy
            )

            # Load music library
            await self._scan_music_library()

            # AI: Get opening track recommendation
            opening_tracks = list(self.track_library.values())[:10]
            ai_response = await self.sdk_master.suggest_next_track(
                current_track=None,
                available_tracks=[asdict(t) for t in opening_tracks]
            )

            if ai_response.success:
                logger.info(f"🤖 AI Opening suggestion: {ai_response.response[:100]}...")

            # Select opening track
            opening_track = await self._select_opening_track(session_config)
            if opening_track:
                await self._load_track("A", opening_track)
                logger.info(f"🎵 Loaded opening track: {opening_track.artist} - {opening_track.title}")

            self.state = DJState.IDLE
            logger.info(f"✅ DJ Session {session_id} started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start DJ session: {e}")
            self.state = DJState.ERROR
            return False

    async def _scan_music_library(self) -> None:
        """Scan and analyze music library with AI"""
        if not self.music_library_path or not Path(self.music_library_path).exists():
            logger.warning("⚠️ Music library path not found, using demo tracks")
            self._create_demo_tracks()
            return

        logger.info("🔍 Scanning music library...")

        # Scan for audio files
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac'}
        music_files = []

        for ext in audio_extensions:
            music_files.extend(Path(self.music_library_path).glob(f"**/*{ext}"))

        logger.info(f"📚 Found {len(music_files)} audio files")

        # Process files in batches for AI analysis
        batch_size = 5
        for i in range(0, min(len(music_files), 20), batch_size):  # Limit to 20 for demo
            batch = music_files[i:i+batch_size]
            await self._analyze_track_batch(batch)

    def _create_demo_tracks(self) -> None:
        """Create demo tracks for testing"""
        demo_tracks = [
            Track(
                id="demo_1",
                title="One More Time",
                artist="Daft Punk",
                file_path="demo/one_more_time.mp3",
                duration=320.0,
                bpm=123.0,
                key="D major",
                genre="House",
                energy_level=0.8,
                vocal_presence=True
            ),
            Track(
                id="demo_2",
                title="Levels",
                artist="Avicii",
                file_path="demo/levels.mp3",
                duration=200.0,
                bpm=126.0,
                key="C# minor",
                genre="Progressive House",
                energy_level=0.9,
                vocal_presence=True
            ),
            Track(
                id="demo_3",
                title="Strobe",
                artist="Deadmau5",
                file_path="demo/strobe.mp3",
                duration=640.0,
                bpm=128.0,
                key="F# minor",
                genre="Progressive House",
                energy_level=0.7,
                vocal_presence=False
            ),
            Track(
                id="demo_4",
                title="Titanium",
                artist="David Guetta ft. Sia",
                file_path="demo/titanium.mp3",
                duration=245.0,
                bpm=126.0,
                key="E♭ minor",
                genre="Electro House",
                energy_level=0.85,
                vocal_presence=True
            ),
            Track(
                id="demo_5",
                title="Animals",
                artist="Martin Garrix",
                file_path="demo/animals.mp3",
                duration=302.0,
                bpm=128.0,
                key="F# minor",
                genre="Big Room",
                energy_level=0.95,
                vocal_presence=False
            )
        ]

        for track in demo_tracks:
            self.track_library[track.id] = track

        logger.info(f"✅ Created {len(demo_tracks)} demo tracks")

    async def _analyze_track_batch(self, track_files: List[Path]) -> None:
        """Analyze a batch of tracks with AI"""
        for file_path in track_files:
            try:
                # Create basic track info
                track_id = file_path.stem
                track = Track(
                    id=track_id,
                    title=file_path.stem.replace('_', ' ').title(),
                    artist="Unknown Artist",
                    file_path=str(file_path),
                    duration=180.0  # Default duration
                )

                # AI analysis
                ai_response = await self.sdk_master.analyze_track({
                    'title': track.title,
                    'file_path': str(file_path),
                    'filename': file_path.name
                })

                if ai_response.success:
                    track.ai_analysis = {
                        'analysis': ai_response.response,
                        'confidence': ai_response.confidence,
                        'timestamp': time.time()
                    }

                self.track_library[track_id] = track

            except Exception as e:
                logger.error(f"❌ Failed to analyze {file_path}: {e}")

    async def _select_opening_track(self, session_config: Dict[str, Any]) -> Optional[Track]:
        """AI-powered opening track selection"""
        available_tracks = list(self.track_library.values())

        if not available_tracks:
            return None

        # AI selection based on venue and energy
        query = f"""
Select the best opening track for a {session_config.get('venue', 'club')} set.
Consider: energy buildup, crowd engagement, set opener characteristics.
Available tracks: {[f"{t.artist} - {t.title}" for t in available_tracks[:5]]}
"""

        ai_response = await self.sdk_master.make_dj_decision(
            DJTaskType.TRACK_ANALYSIS, query
        )

        # For demo, select first track with appropriate energy
        for track in available_tracks:
            if track.energy_level < 0.8:  # Good opener energy
                return track

        return available_tracks[0] if available_tracks else None

    async def _load_track(self, deck: str, track: Track) -> bool:
        """Load track onto specified deck"""
        try:
            if deck == "A":
                self.mix_session.deck_a_track = track
            elif deck == "B":
                self.mix_session.deck_b_track = track

            logger.info(f"🎵 Loaded {track.artist} - {track.title} on Deck {deck}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load track on Deck {deck}: {e}")
            return False

    async def perform_intelligent_mix(self) -> bool:
        """Perform AI-guided intelligent mixing"""
        if not self.mix_session or self.state != DJState.IDLE:
            return False

        try:
            self.state = DJState.MIXING

            current_track = (self.mix_session.deck_a_track
                           if self.mix_session.current_deck == "A"
                           else self.mix_session.deck_b_track)

            if not current_track:
                logger.warning("⚠️ No current track for mixing")
                return False

            # AI: Get next track suggestion
            available_tracks = [t for t in self.track_library.values()
                              if t.id not in [t.id for t in self.mix_session.played_tracks]]

            ai_response = await self.sdk_master.suggest_next_track(
                current_track=asdict(current_track),
                available_tracks=[asdict(t) for t in available_tracks[:10]]
            )

            if ai_response.success:
                logger.info(f"🤖 AI Mixing advice: {ai_response.response[:150]}...")

            # Select next track (simplified for demo)
            next_track = await self._select_next_track(current_track, available_tracks)

            if next_track:
                # Load next track on opposite deck
                target_deck = "B" if self.mix_session.current_deck == "A" else "A"
                await self._load_track(target_deck, next_track)

                # Perform transition
                await self._perform_transition(current_track, next_track)

                # Update session state
                self.mix_session.played_tracks.append(current_track)
                self.mix_session.current_deck = target_deck

                self.performance_stats['tracks_played'] += 1
                self.performance_stats['successful_transitions'] += 1

            self.state = DJState.IDLE
            return True

        except Exception as e:
            logger.error(f"❌ Intelligent mix failed: {e}")
            self.state = DJState.ERROR
            return False

    async def _select_next_track(self, current_track: Track,
                                available_tracks: List[Track]) -> Optional[Track]:
        """AI-powered next track selection"""
        if not available_tracks:
            return None

        # Find harmonically compatible tracks
        compatible_tracks = []

        for track in available_tracks:
            # Simple harmonic compatibility check
            if (track.key and current_track.key and
                self._are_keys_compatible(current_track.key, track.key)):
                compatible_tracks.append(track)

        # If no compatible tracks, use energy-based selection
        if not compatible_tracks:
            compatible_tracks = sorted(available_tracks,
                                     key=lambda t: abs(t.energy_level - current_track.energy_level))

        return compatible_tracks[0] if compatible_tracks else None

    def _are_keys_compatible(self, key1: str, key2: str) -> bool:
        """Check if two musical keys are compatible for mixing"""
        # Simplified harmonic compatibility (Camelot wheel logic)
        compatible_pairs = [
            ("C major", "G major"), ("C major", "F major"),
            ("D minor", "A minor"), ("D minor", "G minor"),
            ("F# minor", "C# minor"), ("F# minor", "B minor"),
            # Add more pairs as needed
        ]

        return (key1, key2) in compatible_pairs or (key2, key1) in compatible_pairs

    async def _perform_transition(self, current_track: Track, next_track: Track) -> None:
        """Perform AI-guided transition between tracks"""
        self.state = DJState.TRANSITIONING

        # AI: Get transition advice
        transition_query = f"""
Current: {current_track.artist} - {current_track.title} ({current_track.bpm} BPM, {current_track.key})
Next: {next_track.artist} - {next_track.title} ({next_track.bpm} BPM, {next_track.key})

Provide specific transition advice: timing, effects, crossfader movement, EQ adjustments.
"""

        ai_response = await self.sdk_master.make_dj_decision(
            DJTaskType.MIXING_DECISION, transition_query, urgent=True
        )

        if ai_response.success:
            logger.info(f"🤖 Transition advice: {ai_response.response}")

        # Simulate transition timing
        transition_duration = 8.0  # seconds
        logger.info(f"🔄 Transitioning from {current_track.title} to {next_track.title}")

        # Simulate crossfader movement
        steps = 20
        for i in range(steps):
            progress = i / (steps - 1)
            crossfader_pos = -1 + (2 * progress)  # -1 to 1
            self.mix_session.crossfader_position = crossfader_pos

            await asyncio.sleep(transition_duration / steps)

        logger.info("✅ Transition completed")

    async def get_real_time_advice(self, situation: str) -> AIResponse:
        """Get real-time DJ advice from Claude AI"""
        return await self.sdk_master.get_mixing_advice(situation)

    async def analyze_crowd_response(self, crowd_data: Dict[str, Any]) -> AIResponse:
        """Analyze crowd response and get recommendations"""
        query = f"""
Crowd analysis data: {json.dumps(crowd_data, indent=2)}

Analyze crowd energy and engagement. Recommend:
1. Track selection adjustments
2. Energy level changes
3. Genre transitions
4. Timing modifications
"""
        return await self.sdk_master.make_dj_decision(DJTaskType.CROWD_ANALYSIS, query)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        if not self.mix_session:
            return {}

        elapsed_time = time.time() - self.mix_session.start_time

        return {
            'session_id': self.mix_session.session_id,
            'elapsed_time_minutes': round(elapsed_time / 60, 1),
            'current_state': self.state.value,
            'tracks_played': len(self.mix_session.played_tracks),
            'current_track': (asdict(self.mix_session.deck_a_track)
                            if self.mix_session.current_deck == "A"
                            else asdict(self.mix_session.deck_b_track)) or None,
            'queue_length': len(self.mix_session.track_queue),
            'crossfader_position': self.mix_session.crossfader_position,
            'crowd_energy': self.mix_session.crowd_energy,
            'performance_stats': self.performance_stats,
            'sdk_stats': self.sdk_master.get_performance_stats()
        }

    async def stop_session(self) -> bool:
        """Stop the current DJ session"""
        try:
            if self.mix_session:
                session_duration = time.time() - self.mix_session.start_time
                logger.info(f"🛑 Stopping DJ session after {session_duration/60:.1f} minutes")

                self.mix_session = None
                self.state = DJState.IDLE

                return True
            return False

        except Exception as e:
            logger.error(f"❌ Failed to stop session: {e}")
            return False

# Example usage and testing
async def test_autonomous_dj():
    """Test the Autonomous DJ Agent"""
    print("🎧 Testing Autonomous DJ Agent with Claude AI")
    print("=" * 60)

    # Check API key
    if not validate_api_key():
        print("❌ Claude API key required for testing")
        print("💡 Set ANTHROPIC_API_KEY environment variable")
        return

    # Initialize DJ agent
    dj = AutonomousDJAgent()

    # Start session
    session_config = {
        'venue': 'club',
        'duration': 120,  # 2 hours
        'genre': 'house'
    }

    print("🚀 Starting DJ session...")
    success = await dj.start_dj_session(session_config)

    if success:
        print("✅ DJ session started successfully")

        # Get session stats
        stats = dj.get_session_stats()
        print(f"📊 Session stats: {json.dumps(stats, indent=2)}")

        # Test intelligent mixing
        print("\n🤖 Testing intelligent mixing...")
        mix_success = await dj.perform_intelligent_mix()
        print(f"Mix success: {mix_success}")

        # Test real-time advice
        print("\n💡 Testing real-time advice...")
        advice = await dj.get_real_time_advice("The crowd seems bored, energy is low")
        print(f"AI Advice: {advice.response}")

        # Stop session
        await dj.stop_session()
        print("🛑 Session stopped")

    else:
        print("❌ Failed to start DJ session")

if __name__ == "__main__":
    asyncio.run(test_autonomous_dj())