#!/usr/bin/env python3
"""
🤖 SDK Master Agent
Centralized controller for all Claude AI operations in the Autonomous DJ System
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json

try:
    import anthropic
    from anthropic import Anthropic, AsyncAnthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    print("❌ Claude SDK not available. Install with: pip install anthropic")
    CLAUDE_AVAILABLE = False

from .claude_config import (
    ClaudeConfig, DJTaskType, DJTaskConfig,
    get_config, get_task_config, get_model_for_task,
    validate_api_key
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DJContext:
    """Context information for DJ decisions"""
    current_track: Optional[Dict[str, Any]] = None
    next_track: Optional[Dict[str, Any]] = None
    crowd_energy: float = 0.5  # 0-1 scale
    time_in_set: int = 0  # minutes
    venue_type: str = "club"  # club, festival, wedding, etc.
    genre_preference: str = "auto"
    bpm_range: tuple = (120, 130)
    key_signature: Optional[str] = None
    mix_style: str = "professional"  # quick, professional, extended

@dataclass
class AIResponse:
    """Standardized AI response format"""
    success: bool
    response: str
    confidence: float = 0.0
    processing_time_ms: int = 0
    task_type: DJTaskType = DJTaskType.REAL_TIME_FEEDBACK
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class SDKMasterAgent:
    """Master controller for Claude SDK operations"""

    def __init__(self, config: Optional[ClaudeConfig] = None):
        """Initialize the SDK Master Agent"""
        self.config = config or get_config()
        self.client: Optional[Anthropic] = None
        self.async_client: Optional[AsyncAnthropic] = None
        self.dj_context = DJContext()
        self.conversation_history: List[Dict[str, str]] = []
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'average_response_time': 0.0,
            'errors': []
        }

        # Initialize Claude client
        if CLAUDE_AVAILABLE:
            self._initialize_clients()
        else:
            logger.error("❌ Claude SDK not available")

    def _initialize_clients(self) -> bool:
        """Initialize Claude API clients"""
        try:
            if not validate_api_key():
                return False

            self.client = Anthropic(api_key=self.config.api_key)
            self.async_client = AsyncAnthropic(api_key=self.config.api_key)

            logger.info("✅ Claude SDK Master Agent initialized")
            logger.info(f"🎛️ Model: {self.config.model.value}")
            logger.info(f"🎛️ Real-time mode: {self.config.real_time_mode}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Claude clients: {e}")
            return False

    def update_dj_context(self, **kwargs) -> None:
        """Update the current DJ context"""
        for key, value in kwargs.items():
            if hasattr(self.dj_context, key):
                setattr(self.dj_context, key, value)
                logger.debug(f"🎛️ Updated DJ context: {key} = {value}")

    def get_dj_context_string(self) -> str:
        """Get formatted DJ context for Claude"""
        context = asdict(self.dj_context)
        return f"""
Current DJ Session Context:
- Current Track: {context.get('current_track', 'None')}
- Next Track: {context.get('next_track', 'None')}
- Crowd Energy: {context['crowd_energy']}/1.0
- Set Duration: {context['time_in_set']} minutes
- Venue: {context['venue_type']}
- Genre Preference: {context['genre_preference']}
- BPM Range: {context['bpm_range'][0]}-{context['bpm_range'][1]}
- Mix Style: {context['mix_style']}
"""

    async def make_dj_decision(self, task_type: DJTaskType, query: str,
                              urgent: bool = False) -> AIResponse:
        """Make an AI-powered DJ decision"""
        if not self.async_client:
            return AIResponse(
                success=False,
                response="Claude client not initialized",
                task_type=task_type
            )

        start_time = time.time()
        task_config = get_task_config(task_type)
        model = get_model_for_task(task_type)

        try:
            # Build the prompt with context
            system_prompt = self._build_system_prompt(task_type)
            user_prompt = f"{self.get_dj_context_string()}\n\nQuery: {query}"

            # Add conversation history for context
            messages = []
            if self.conversation_history:
                messages.extend(self.conversation_history[-3:])  # Last 3 exchanges

            messages.append({"role": "user", "content": user_prompt})

            # Adjust parameters for urgency
            max_tokens = 1000 if urgent else self.config.max_tokens
            temperature = 0.3 if urgent else self.config.temperature

            # Make the API call
            response = await self.async_client.messages.create(
                model=model.value,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )

            # Process response
            response_text = response.content[0].text if response.content else ""
            processing_time = int((time.time() - start_time) * 1000)

            # Update metrics
            self._update_metrics(True, processing_time)

            # Store in conversation history
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": response_text})

            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return AIResponse(
                success=True,
                response=response_text,
                confidence=self._calculate_confidence(response_text),
                processing_time_ms=processing_time,
                task_type=task_type,
                metadata={
                    'model_used': model.value,
                    'tokens_used': len(response_text.split()),
                    'urgent': urgent
                }
            )

        except Exception as e:
            error_msg = f"Claude API error: {e}"
            logger.error(f"❌ {error_msg}")

            self._update_metrics(False, int((time.time() - start_time) * 1000))

            return AIResponse(
                success=False,
                response=f"AI decision failed: {str(e)}",
                task_type=task_type,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

    def _build_system_prompt(self, task_type: DJTaskType) -> str:
        """Build system prompt based on task type"""
        base_prompt = """You are an elite professional DJ assistant powered by Claude AI.
You have extensive knowledge of music theory, DJ techniques, crowd psychology, and audio engineering.
Your responses are concise, actionable, and tailored for real-time DJ performance."""

        task_prompts = {
            DJTaskType.MIXING_DECISION: """
Focus on: Beat matching, harmonic mixing, energy flow, transition timing.
Provide specific BPM recommendations, key compatibility, and mix techniques.
Consider crowd energy and set progression.""",

            DJTaskType.TRACK_ANALYSIS: """
Analyze: Genre, energy level, vocal presence, breakdown points, key signature.
Provide: BPM, musical key, mix-in/out points, compatible tracks, crowd appeal rating.""",

            DJTaskType.CROWD_ANALYSIS: """
Assess: Crowd energy, dance floor engagement, musical preferences.
Recommend: Genre shifts, energy adjustments, track selection strategies.""",

            DJTaskType.REAL_TIME_FEEDBACK: """
Provide instant, actionable feedback for live DJ performance.
Be extremely concise - maximum 2 sentences. Focus on immediate actions.""",

            DJTaskType.EFFECT_RECOMMENDATION: """
Suggest: Filter sweeps, reverb throws, echo delays, loop rolls.
Consider: Current track breakdown, energy buildup, transition points."""
        }

        return base_prompt + "\n\n" + task_prompts.get(task_type, "")

    def _calculate_confidence(self, response: str) -> float:
        """Calculate confidence score based on response characteristics"""
        # Simple confidence calculation based on response structure
        confidence = 0.5

        # Higher confidence for specific recommendations
        if any(word in response.lower() for word in ['bpm', 'key', 'beat', 'bars']):
            confidence += 0.2

        # Higher confidence for structured responses
        if any(char in response for char in ['•', '1.', '2.', '-']):
            confidence += 0.1

        # Lower confidence for uncertain language
        if any(word in response.lower() for word in ['maybe', 'possibly', 'uncertain']):
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def _update_metrics(self, success: bool, response_time: int):
        """Update performance metrics"""
        self.performance_metrics['total_requests'] += 1

        if success:
            self.performance_metrics['successful_requests'] += 1

        # Update average response time
        total = self.performance_metrics['total_requests']
        current_avg = self.performance_metrics['average_response_time']
        self.performance_metrics['average_response_time'] = (
            (current_avg * (total - 1) + response_time) / total
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        metrics = self.performance_metrics
        return {
            'total_requests': metrics['total_requests'],
            'success_rate': (metrics['successful_requests'] / max(1, metrics['total_requests'])) * 100,
            'average_response_time_ms': round(metrics['average_response_time'], 2),
            'dj_context': asdict(self.dj_context),
            'conversation_length': len(self.conversation_history)
        }

    # Convenience methods for common DJ tasks
    async def analyze_track(self, track_info: Dict[str, Any]) -> AIResponse:
        """Analyze a track for DJ purposes"""
        query = f"Analyze this track for DJ mixing: {json.dumps(track_info, indent=2)}"
        return await self.make_dj_decision(DJTaskType.TRACK_ANALYSIS, query)

    async def suggest_next_track(self, current_track: Dict[str, Any],
                               available_tracks: List[Dict[str, Any]]) -> AIResponse:
        """Suggest the best next track from available options"""
        self.update_dj_context(current_track=current_track)

        query = f"""
Current track: {json.dumps(current_track, indent=2)}
Available tracks: {json.dumps(available_tracks[:5], indent=2)}

Suggest the best next track and explain why. Consider harmonic mixing, energy flow, and crowd engagement.
"""
        return await self.make_dj_decision(DJTaskType.MIXING_DECISION, query)

    async def get_mixing_advice(self, situation: str) -> AIResponse:
        """Get real-time mixing advice"""
        query = f"DJ situation: {situation}. Provide immediate mixing advice."
        return await self.make_dj_decision(DJTaskType.REAL_TIME_FEEDBACK, query, urgent=True)

    async def create_setlist(self, duration_minutes: int, genre: str,
                           available_tracks: List[Dict[str, Any]]) -> AIResponse:
        """Create an optimized setlist"""
        self.update_dj_context(time_in_set=0, genre_preference=genre)

        query = f"""
Create a {duration_minutes}-minute {genre} setlist from these tracks:
{json.dumps(available_tracks[:20], indent=2)}

Consider energy progression, harmonic flow, and crowd engagement.
"""
        return await self.make_dj_decision(DJTaskType.SETLIST_CREATION, query)

# Global SDK Master Agent instance
_sdk_master = None

def get_sdk_master() -> SDKMasterAgent:
    """Get the global SDK Master Agent instance"""
    global _sdk_master
    if _sdk_master is None:
        _sdk_master = SDKMasterAgent()
    return _sdk_master

# Example usage and testing
async def test_sdk_master():
    """Test the SDK Master Agent"""
    print("🤖 Testing SDK Master Agent")
    print("=" * 50)

    master = get_sdk_master()

    # Test track analysis
    test_track = {
        "title": "One More Time",
        "artist": "Daft Punk",
        "bpm": 123,
        "key": "D major",
        "genre": "House"
    }

    print("🎵 Testing track analysis...")
    result = await master.analyze_track(test_track)
    print(f"Success: {result.success}")
    print(f"Response: {result.response[:200]}...")
    print(f"Processing time: {result.processing_time_ms}ms")

    # Test performance stats
    print("\n📊 Performance Statistics:")
    stats = master.get_performance_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    # Run tests if Claude SDK is available
    if CLAUDE_AVAILABLE:
        asyncio.run(test_sdk_master())
    else:
        print("❌ Claude SDK not available for testing")