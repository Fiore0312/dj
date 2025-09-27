"""
🎛️ Core Module - Autonomous DJ System
Central components for Claude AI integration and system management
"""

from .claude_config import (
    ClaudeConfig, ClaudeModel, DJTaskType, DJTaskConfig,
    get_config, get_task_config, validate_api_key
)

from .sdk_master_agent import (
    SDKMasterAgent, DJContext, AIResponse,
    get_sdk_master
)

__all__ = [
    'ClaudeConfig',
    'ClaudeModel',
    'DJTaskType',
    'DJTaskConfig',
    'SDKMasterAgent',
    'DJContext',
    'AIResponse',
    'get_config',
    'get_task_config',
    'get_sdk_master',
    'validate_api_key'
]

__version__ = "2.0.0"
__author__ = "Autonomous DJ System - Claude AI Powered"