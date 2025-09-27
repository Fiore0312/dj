#!/usr/bin/env python3
"""
🧠 Autonomous Decision Engine
AI-powered decision making engine for autonomous DJ mixing
Uses OpenRouter + Sequential Thinking MCP for intelligent DJ decisions
"""

import time
import json
import logging
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
from pathlib import Path

# Core dependencies
from config import DJConfig, get_config
from music_library import MusicLibraryScanner, TrackInfo, get_music_scanner

# MCP and AI integration
try:
    from core.openrouter_client import OpenRouterClient, DJContext
    OPENROUTER_AVAILABLE = True
except ImportError:
    OPENROUTER_AVAILABLE = False
    print("⚠️ OpenRouter client not available")

# Audio analysis
try:
    from autonomous_audio_engine import AudioFeatures, RealTimeAnalyzer
    AUDIO_ENGINE_AVAILABLE = True
except ImportError:
    AUDIO_ENGINE_AVAILABLE = False
    print("⚠️ Audio engine not available")

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """Types of DJ decisions"""
    TRACK_SELECTION = "track_selection"
    MIX_TIMING = "mix_timing"
    TRANSITION_TYPE = "transition_type"
    ENERGY_MANAGEMENT = "energy_management"
    EMERGENCY_ACTION = "emergency_action"

class DecisionUrgency(Enum):
    """Urgency levels for decisions"""
    LOW = "low"           # Plan ahead (>60s)
    MEDIUM = "medium"     # Prepare (30-60s)
    HIGH = "high"         # Execute soon (10-30s)
    CRITICAL = "critical" # Execute now (<10s)

@dataclass
class DJDecision:
    """A DJ decision with context and reasoning"""
    decision_type: DecisionType
    urgency: DecisionUrgency
    decision_data: Dict
    reasoning: str
    confidence: float  # 0-1
    timestamp: float
    context: Dict

    # Execution tracking
    executed: bool = False
    execution_time: Optional[float] = None
    success: Optional[bool] = None
    feedback: Optional[str] = None

@dataclass
class MixContext:
    """Current mixing context for decisions"""
    # Current track info
    current_track: Optional[TrackInfo] = None
    current_position: float = 0.0  # Seconds
    current_bpm: float = 120.0
    current_key: Optional[str] = None
    current_energy: float = 5.0

    # Next track info
    next_track: Optional[TrackInfo] = None
    next_prepared: bool = False

    # Session context
    venue_type: str = "club"
    event_type: str = "prime_time"
    session_duration: float = 0.0  # Minutes
    crowd_energy: float = 5.0

    # Technical state
    crossfader_position: float = 0.0  # -1 to 1
    deck_a_playing: bool = True
    deck_b_playing: bool = False

    # Timing and planning
    next_mix_point: Optional[float] = None
    time_to_mix: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for AI processing"""
        return {
            'current_track': {
                'title': self.current_track.title if self.current_track else 'None',
                'artist': self.current_track.artist if self.current_track else 'None',
                'bpm': self.current_bpm,
                'key': self.current_key or 'Unknown',
                'energy': self.current_energy,
                'position_seconds': self.current_position,
                'duration': self.current_track.duration if self.current_track else 0
            },
            'next_track': {
                'title': self.next_track.title if self.next_track else 'None',
                'prepared': self.next_prepared
            },
            'session': {
                'venue_type': self.venue_type,
                'event_type': self.event_type,
                'duration_minutes': self.session_duration,
                'crowd_energy': self.crowd_energy
            },
            'technical': {
                'crossfader': self.crossfader_position,
                'deck_a_playing': self.deck_a_playing,
                'deck_b_playing': self.deck_b_playing
            },
            'timing': {
                'next_mix_point': self.next_mix_point,
                'time_to_mix': self.time_to_mix
            }
        }

class AutonomousDecisionEngine:
    """AI-powered autonomous decision engine for DJ mixing"""

    def __init__(self, config: DJConfig = None):
        self.config = config or get_config()

        # Core components
        self.music_scanner = get_music_scanner(self.config)
        self.audio_analyzer = RealTimeAnalyzer() if AUDIO_ENGINE_AVAILABLE else None

        # AI client
        self.ai_client = None
        if OPENROUTER_AVAILABLE:
            try:
                self.ai_client = OpenRouterClient(self.config.openrouter_api_key)
                print("🧠 AI decision engine connected to OpenRouter")
            except Exception as e:
                print(f"⚠️ Failed to initialize AI client: {e}")

        # State management
        self.current_context = MixContext()
        self.decision_history: List[DJDecision] = []
        self.candidate_tracks: List[TrackInfo] = []

        # Decision queue and processing
        self.decision_queue = queue.PriorityQueue()
        self.is_processing = False
        self.processing_thread = None

        # Performance tracking
        self.decision_stats = {
            'total_decisions': 0,
            'successful_decisions': 0,
            'avg_decision_time': 0.0,
            'confidence_scores': []
        }

        print("🧠 Autonomous Decision Engine initialized")

    def start_processing(self):
        """Start the decision processing thread"""
        if self.is_processing:
            return

        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._decision_loop, daemon=True)
        self.processing_thread.start()
        print("🔄 Decision processing started")

    def stop_processing(self):
        """Stop the decision processing thread"""
        self.is_processing = False
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        print("⏹️ Decision processing stopped")

    def update_context(self, **kwargs):
        """Update the current mixing context"""
        for key, value in kwargs.items():
            if hasattr(self.current_context, key):
                setattr(self.current_context, key, value)

        # Trigger decision analysis if significant changes
        if any(key in ['current_position', 'current_energy', 'crowd_energy'] for key in kwargs):
            self._queue_decision_analysis()

    def _queue_decision_analysis(self):
        """Queue a decision analysis based on current context"""
        try:
            # Determine urgency based on context
            urgency = self._calculate_decision_urgency()

            # Priority: Critical=0, High=1, Medium=2, Low=3
            priority = {
                DecisionUrgency.CRITICAL: 0,
                DecisionUrgency.HIGH: 1,
                DecisionUrgency.MEDIUM: 2,
                DecisionUrgency.LOW: 3
            }[urgency]

            analysis_task = {
                'type': 'context_analysis',
                'urgency': urgency,
                'timestamp': time.time(),
                'context': self.current_context.to_dict()
            }

            self.decision_queue.put((priority, time.time(), analysis_task))

        except Exception as e:
            logger.error(f"Error queueing decision analysis: {e}")

    def _calculate_decision_urgency(self) -> DecisionUrgency:
        """Calculate urgency based on current context"""
        try:
            # Check if we need immediate action
            if self.current_context.time_to_mix is not None:
                if self.current_context.time_to_mix <= 10:
                    return DecisionUrgency.CRITICAL
                elif self.current_context.time_to_mix <= 30:
                    return DecisionUrgency.HIGH
                elif self.current_context.time_to_mix <= 60:
                    return DecisionUrgency.MEDIUM

            # Check if next track is prepared
            if not self.current_context.next_prepared:
                # Estimate time remaining in current track
                if self.current_context.current_track and self.current_context.current_track.duration:
                    time_remaining = self.current_context.current_track.duration - self.current_context.current_position
                    if time_remaining <= 60:
                        return DecisionUrgency.HIGH
                    elif time_remaining <= 120:
                        return DecisionUrgency.MEDIUM

            return DecisionUrgency.LOW

        except Exception as e:
            logger.error(f"Error calculating urgency: {e}")
            return DecisionUrgency.MEDIUM

    def _decision_loop(self):
        """Main decision processing loop"""
        while self.is_processing:
            try:
                # Get next decision task (blocks until available)
                priority, timestamp, task = self.decision_queue.get(timeout=1.0)

                # Process the decision task
                self._process_decision_task(task)

                # Mark task as done
                self.decision_queue.task_done()

            except queue.Empty:
                # No tasks, continue loop
                continue
            except Exception as e:
                logger.error(f"Error in decision loop: {e}")
                time.sleep(0.1)

    def _process_decision_task(self, task: Dict):
        """Process a single decision task"""
        try:
            start_time = time.time()

            if task['type'] == 'context_analysis':
                decisions = self._analyze_context_and_decide(task['context'], task['urgency'])

                # Store decisions
                for decision in decisions:
                    self.decision_history.append(decision)
                    self._execute_decision_if_needed(decision)

                # Update stats
                processing_time = time.time() - start_time
                self._update_decision_stats(len(decisions), processing_time)

        except Exception as e:
            logger.error(f"Error processing decision task: {e}")

    def _analyze_context_and_decide(self, context: Dict, urgency: DecisionUrgency) -> List[DJDecision]:
        """Analyze context and make decisions using AI"""
        decisions = []

        try:
            if not self.ai_client:
                # Fallback to rule-based decisions
                return self._fallback_decisions(context, urgency)

            # Prepare AI prompt for decision making
            prompt = self._build_decision_prompt(context, urgency)

            # Get AI decision using sequential thinking for complex analysis
            ai_context = DJContext(
                venue_type=context['session']['venue_type'],
                event_type=context['session']['event_type'],
                energy_level=int(context['session']['crowd_energy']),
                current_bpm=context['current_track']['bpm']
            )

            # Use sequential thinking for complex decisions
            use_sequential_thinking = urgency in [DecisionUrgency.HIGH, DecisionUrgency.CRITICAL]

            response = self.ai_client.get_dj_decision(
                ai_context,
                prompt,
                urgent=urgency == DecisionUrgency.CRITICAL
            )

            if response.success:
                decisions = self._parse_ai_response(response.response, context, urgency)
            else:
                logger.warning(f"AI decision failed: {response.response}")
                decisions = self._fallback_decisions(context, urgency)

        except Exception as e:
            logger.error(f"Error in AI decision analysis: {e}")
            decisions = self._fallback_decisions(context, urgency)

        return decisions

    def _build_decision_prompt(self, context: Dict, urgency: DecisionUrgency) -> str:
        """Build AI prompt for decision making"""

        current_track = context['current_track']
        session = context['session']
        timing = context['timing']

        prompt = f"""
🎧 AUTONOMOUS DJ DECISION REQUEST

CURRENT SITUATION:
- Track: "{current_track['title']}" by {current_track['artist']}
- Position: {current_track['position_seconds']:.1f}s / {current_track['duration']:.1f}s
- BPM: {current_track['bpm']}, Key: {current_track['key']}, Energy: {current_track['energy']}/10
- Venue: {session['venue_type']}, Event: {session['event_type']}
- Crowd Energy: {session['crowd_energy']}/10
- Session Duration: {session['duration_minutes']:.1f} minutes

URGENCY LEVEL: {urgency.value.upper()}

DECISIONS NEEDED:
"""

        # Add specific decision requirements based on urgency and context
        if urgency == DecisionUrgency.CRITICAL:
            prompt += """
🚨 CRITICAL DECISIONS (Execute immediately):
1. Should I start the mix transition NOW?
2. What crossfader movement is needed?
3. Any emergency EQ adjustments needed?
"""
        elif urgency == DecisionUrgency.HIGH:
            prompt += """
⚡ HIGH PRIORITY DECISIONS (Execute within 30s):
1. What track should I mix in next?
2. When exactly should I start the transition?
3. What type of transition (cut, fade, filter, etc.)?
4. Any pre-transition preparations needed?
"""
        elif urgency == DecisionUrgency.MEDIUM:
            prompt += """
🎯 MEDIUM PRIORITY DECISIONS (Plan for next 60s):
1. Which tracks are best candidates for next mix?
2. Should I adjust current track energy/EQ?
3. What's the optimal timing strategy?
4. Any crowd energy management needed?
"""
        else:  # LOW
            prompt += """
📋 STRATEGIC PLANNING (Next 2-3 tracks):
1. What's the overall energy curve strategy?
2. Which tracks should I prepare and queue?
3. Any genre or style transitions to plan?
4. How to maintain crowd engagement?
"""

        if timing.get('time_to_mix'):
            prompt += f"\n⏰ Time to next optimal mix point: {timing['time_to_mix']:.1f} seconds"

        prompt += """

RESPOND WITH:
1. Your analysis of the current situation
2. Specific decisions with reasoning
3. Confidence level (1-10) for each decision
4. Any risks or concerns to monitor

Keep responses concise but actionable. Focus on concrete decisions I can execute.
"""

        return prompt

    def _parse_ai_response(self, response: str, context: Dict, urgency: DecisionUrgency) -> List[DJDecision]:
        """Parse AI response into structured decisions"""
        decisions = []

        try:
            # For now, create a general decision based on AI response
            # In a more advanced version, we could parse structured JSON responses

            decision = DJDecision(
                decision_type=DecisionType.TRACK_SELECTION,  # Default type
                urgency=urgency,
                decision_data={
                    'ai_response': response,
                    'action_type': 'ai_analysis',
                    'context_snapshot': context
                },
                reasoning=response,
                confidence=0.8,  # Default confidence
                timestamp=time.time(),
                context=context
            )

            decisions.append(decision)

            # Extract specific actionable decisions from response
            if "mix transition NOW" in response.lower() or "start mixing" in response.lower():
                mix_decision = DJDecision(
                    decision_type=DecisionType.MIX_TIMING,
                    urgency=DecisionUrgency.CRITICAL,
                    decision_data={
                        'action': 'start_transition',
                        'immediate': True
                    },
                    reasoning="AI recommends immediate transition",
                    confidence=0.9,
                    timestamp=time.time(),
                    context=context
                )
                decisions.append(mix_decision)

            # Look for track selection recommendations
            if "next track" in response.lower() or "recommend" in response.lower():
                # Get candidate tracks for selection
                candidates = self._get_track_candidates(context)
                if candidates:
                    selection_decision = DJDecision(
                        decision_type=DecisionType.TRACK_SELECTION,
                        urgency=urgency,
                        decision_data={
                            'candidates': [asdict(track) for track in candidates[:3]],
                            'selection_criteria': response
                        },
                        reasoning=f"AI analysis suggests track selection: {response[:200]}...",
                        confidence=0.7,
                        timestamp=time.time(),
                        context=context
                    )
                    decisions.append(selection_decision)

        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")

        return decisions

    def _fallback_decisions(self, context: Dict, urgency: DecisionUrgency) -> List[DJDecision]:
        """Fallback rule-based decisions when AI is not available"""
        decisions = []

        try:
            current_track = context['current_track']

            # Rule-based decision: prepare next track if not ready
            if not context['next_track']['prepared']:
                time_remaining = current_track['duration'] - current_track['position_seconds']

                if time_remaining <= 90:  # 1.5 minutes remaining
                    candidates = self._get_track_candidates(context)
                    if candidates:
                        decision = DJDecision(
                            decision_type=DecisionType.TRACK_SELECTION,
                            urgency=DecisionUrgency.HIGH if time_remaining <= 60 else DecisionUrgency.MEDIUM,
                            decision_data={
                                'candidates': [asdict(track) for track in candidates[:1]],
                                'selection_criteria': 'rule_based_compatibility'
                            },
                            reasoning=f"Rule-based selection: {time_remaining:.1f}s remaining, need next track",
                            confidence=0.6,
                            timestamp=time.time(),
                            context=context
                        )
                        decisions.append(decision)

            # Rule-based decision: energy management
            crowd_energy = context['session']['crowd_energy']
            current_energy = current_track['energy']

            if abs(crowd_energy - current_energy) > 2:
                energy_decision = DJDecision(
                    decision_type=DecisionType.ENERGY_MANAGEMENT,
                    urgency=DecisionUrgency.MEDIUM,
                    decision_data={
                        'current_energy': current_energy,
                        'target_energy': crowd_energy,
                        'adjustment': 'increase' if crowd_energy > current_energy else 'decrease'
                    },
                    reasoning=f"Energy mismatch: crowd={crowd_energy}, track={current_energy}",
                    confidence=0.7,
                    timestamp=time.time(),
                    context=context
                )
                decisions.append(energy_decision)

        except Exception as e:
            logger.error(f"Error in fallback decisions: {e}")

        return decisions

    def _get_track_candidates(self, context: Dict) -> List[TrackInfo]:
        """Get compatible track candidates for current context"""
        try:
            current_track = context['current_track']

            if not self.music_scanner:
                return []

            # Get harmonically compatible tracks
            candidates = self.music_scanner.get_harmonically_compatible_tracks(
                current_key=current_track['key'],
                current_bpm=current_track['bpm'],
                current_energy=int(current_track['energy']),
                limit=10
            )

            return candidates

        except Exception as e:
            logger.error(f"Error getting track candidates: {e}")
            return []

    def _execute_decision_if_needed(self, decision: DJDecision):
        """Execute decision if it requires immediate action"""
        try:
            if decision.urgency == DecisionUrgency.CRITICAL:
                # Execute critical decisions immediately
                if decision.decision_type == DecisionType.MIX_TIMING:
                    self._execute_mix_decision(decision)
                elif decision.decision_type == DecisionType.EMERGENCY_ACTION:
                    self._execute_emergency_action(decision)

                decision.executed = True
                decision.execution_time = time.time()

        except Exception as e:
            logger.error(f"Error executing decision: {e}")
            decision.success = False
            decision.feedback = str(e)

    def _execute_mix_decision(self, decision: DJDecision):
        """Execute a mixing decision"""
        # This would integrate with the autonomous mixing controller
        # For now, we just log the decision
        action_data = decision.decision_data
        logger.info(f"🎛️ Executing mix decision: {action_data}")

        # Placeholder for actual MIDI/mixing control
        # self.mixing_controller.execute_transition(action_data)

        decision.success = True
        decision.feedback = "Mix decision logged (placeholder execution)"

    def _execute_emergency_action(self, decision: DJDecision):
        """Execute emergency action"""
        action_data = decision.decision_data
        logger.warning(f"🚨 Emergency action: {action_data}")

        # Placeholder for emergency actions (stop, fade out, etc.)
        decision.success = True
        decision.feedback = "Emergency action logged"

    def _update_decision_stats(self, num_decisions: int, processing_time: float):
        """Update decision processing statistics"""
        self.decision_stats['total_decisions'] += num_decisions

        # Update average processing time
        current_avg = self.decision_stats['avg_decision_time']
        total_decisions = self.decision_stats['total_decisions']
        self.decision_stats['avg_decision_time'] = (
            (current_avg * (total_decisions - num_decisions) + processing_time) / total_decisions
        )

    def get_recent_decisions(self, limit: int = 10) -> List[DJDecision]:
        """Get recent decisions"""
        return self.decision_history[-limit:] if self.decision_history else []

    def get_decision_stats(self) -> Dict:
        """Get decision engine statistics"""
        stats = self.decision_stats.copy()
        stats['decision_queue_size'] = self.decision_queue.qsize()
        stats['recent_decisions'] = len(self.get_recent_decisions())
        return stats

def test_decision_engine():
    """Test the autonomous decision engine"""
    print("🧪 Testing Autonomous Decision Engine")
    print("=" * 50)

    # Initialize decision engine
    config = get_config()
    engine = AutonomousDecisionEngine(config)

    # Start processing
    engine.start_processing()

    # Simulate context updates
    print("\n🎵 Simulating DJ session...")

    # Update context with track playing
    engine.update_context(
        current_bpm=128.0,
        current_key="A minor",
        current_energy=7.0,
        current_position=180.0,  # 3 minutes in
        venue_type="club",
        event_type="prime_time",
        crowd_energy=8.0
    )

    # Wait for processing
    time.sleep(2)

    # Simulate approaching mix point
    engine.update_context(
        current_position=240.0,  # 4 minutes in
        time_to_mix=30.0,  # 30 seconds to mix
        next_prepared=False
    )

    # Wait for processing
    time.sleep(2)

    # Get recent decisions
    decisions = engine.get_recent_decisions()
    print(f"\n📊 Recent decisions ({len(decisions)}):")
    for i, decision in enumerate(decisions):
        print(f"  {i+1}. {decision.decision_type.value} ({decision.urgency.value})")
        print(f"     Confidence: {decision.confidence:.2f}")
        print(f"     Reasoning: {decision.reasoning[:100]}...")

    # Get stats
    stats = engine.get_decision_stats()
    print(f"\n📈 Decision Engine Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Stop processing
    engine.stop_processing()

    print("\n✅ Decision engine test complete!")

if __name__ == "__main__":
    test_decision_engine()