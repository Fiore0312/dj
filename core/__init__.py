"""
🎛️ Core Module - Autonomous DJ System
Central components for OpenRouter AI integration and system management
"""

from .openrouter_client import (
    OpenRouterClient, DJContext, AIResponse,
    get_openrouter_client
)

__all__ = [
    'OpenRouterClient',
    'DJContext',
    'AIResponse',
    'get_openrouter_client'
]

__version__ = "2.0.0"
__author__ = "Autonomous DJ System - Claude AI Powered"