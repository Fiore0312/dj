#!/usr/bin/env python3
"""
🔧 Claude SDK Configuration
Centralized configuration for Claude API integration
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeModel(Enum):
    """Available Claude models for different tasks"""
    SONNET_4_0 = "claude-sonnet-4-20250514"  # Latest for real-time DJ decisions
    SONNET_3_5 = "claude-3-5-sonnet-latest"  # Fallback for compatibility
    HAIKU_3_5 = "claude-3-5-haiku-latest"    # Fast responses for UI interactions

@dataclass
class ClaudeConfig:
    """Configuration for Claude API"""
    api_key: Optional[str] = None
    model: ClaudeModel = ClaudeModel.SONNET_4_0
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    rate_limit_requests_per_minute: int = 60

    # DJ-specific settings
    real_time_mode: bool = True
    low_latency_responses: bool = True
    music_analysis_depth: str = "professional"  # basic, standard, professional

    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            logger.warning("⚠️ No Claude API key found. Set ANTHROPIC_API_KEY environment variable")

class DJTaskType(Enum):
    """Types of DJ tasks for Claude AI"""
    TRACK_ANALYSIS = "track_analysis"
    MIXING_DECISION = "mixing_decision"
    GENRE_CLASSIFICATION = "genre_classification"
    CROWD_ANALYSIS = "crowd_analysis"
    TRANSITION_SUGGESTION = "transition_suggestion"
    EFFECT_RECOMMENDATION = "effect_recommendation"
    SETLIST_CREATION = "setlist_creation"
    REAL_TIME_FEEDBACK = "real_time_feedback"

@dataclass
class DJTaskConfig:
    """Configuration for specific DJ tasks"""
    task_type: DJTaskType
    priority: str = "normal"  # low, normal, high, critical
    max_response_time_ms: int = 500  # For real-time tasks
    context_window: int = 1000  # Tokens of context to maintain

    # Task-specific parameters
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

# Global configuration instance
DEFAULT_CONFIG = ClaudeConfig()

# Task-specific configurations
DJ_TASK_CONFIGS = {
    DJTaskType.REAL_TIME_FEEDBACK: DJTaskConfig(
        task_type=DJTaskType.REAL_TIME_FEEDBACK,
        priority="high",
        max_response_time_ms=200,
        context_window=500
    ),
    DJTaskType.MIXING_DECISION: DJTaskConfig(
        task_type=DJTaskType.MIXING_DECISION,
        priority="high",
        max_response_time_ms=300,
        context_window=800
    ),
    DJTaskType.TRACK_ANALYSIS: DJTaskConfig(
        task_type=DJTaskType.TRACK_ANALYSIS,
        priority="normal",
        max_response_time_ms=1000,
        context_window=1500
    ),
    DJTaskType.SETLIST_CREATION: DJTaskConfig(
        task_type=DJTaskType.SETLIST_CREATION,
        priority="low",
        max_response_time_ms=5000,
        context_window=2000
    )
}

def get_config() -> ClaudeConfig:
    """Get the global Claude configuration"""
    return DEFAULT_CONFIG

def get_task_config(task_type: DJTaskType) -> DJTaskConfig:
    """Get configuration for a specific DJ task"""
    return DJ_TASK_CONFIGS.get(task_type, DJTaskConfig(task_type=task_type))

def validate_api_key() -> bool:
    """Validate that Claude API key is available"""
    config = get_config()
    if not config.api_key:
        logger.error("❌ Claude API key not found")
        logger.info("💡 Set ANTHROPIC_API_KEY environment variable")
        logger.info("💡 Get your API key from: https://console.anthropic.com/")
        return False

    logger.info("✅ Claude API key configured")
    return True

def get_model_for_task(task_type: DJTaskType) -> ClaudeModel:
    """Get the optimal Claude model for a specific task"""
    # Real-time tasks use fastest model
    if task_type in [DJTaskType.REAL_TIME_FEEDBACK, DJTaskType.MIXING_DECISION]:
        return ClaudeModel.HAIKU_3_5

    # Complex analysis uses most capable model
    elif task_type in [DJTaskType.TRACK_ANALYSIS, DJTaskType.SETLIST_CREATION]:
        return ClaudeModel.SONNET_4_0

    # Default to balanced model
    return ClaudeModel.SONNET_3_5

# Example usage and testing
if __name__ == "__main__":
    print("🔧 Claude Configuration Test")
    print("=" * 40)

    # Test configuration
    config = get_config()
    print(f"Model: {config.model.value}")
    print(f"Max tokens: {config.max_tokens}")
    print(f"Real-time mode: {config.real_time_mode}")

    # Test API key validation
    api_valid = validate_api_key()
    print(f"API Key valid: {api_valid}")

    # Test task configurations
    print("\n🎛️ DJ Task Configurations:")
    for task_type in DJTaskType:
        task_config = get_task_config(task_type)
        optimal_model = get_model_for_task(task_type)
        print(f"  {task_type.value}: {task_config.priority} priority, "
              f"{task_config.max_response_time_ms}ms max, "
              f"model: {optimal_model.value}")