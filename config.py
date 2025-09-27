#!/usr/bin/env python3
"""
⚙️ Configurazione Sistema DJ AI
Configurazione ultra-semplice per sistema DJ AI con OpenRouter
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path

@dataclass
class DJConfig:
    """Configurazione principale sistema DJ AI"""

    # OpenRouter API
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "deepseek/deepseek-r1:free"  # Modello primario gratuito 2025
    openrouter_fallback_model: str = "nousresearch/hermes-3-llama-3.1-405b"  # Backup creatività musicale

    # Musica
    music_library_path: str = "/Users/Fiore/Music"
    supported_formats: list = None

    # MIDI
    midi_device_name: str = "AI_DJ_Controller"
    iac_bus_name: str = "Bus 1"  # macOS IAC Driver

    # GUI
    window_width: int = 800
    window_height: int = 600
    theme: str = "dark"

    # DJ Settings
    default_bpm_range: tuple = (120, 140)
    transition_time_seconds: int = 30
    energy_levels: list = None

    def __post_init__(self):
        """Inizializza valori di default"""
        if self.supported_formats is None:
            self.supported_formats = ['.mp3', '.flac', '.wav', '.m4a', '.aiff', '.ogg']

        if self.energy_levels is None:
            self.energy_levels = [
                "Chill/Ambient",
                "Low Energy",
                "Medium Energy",
                "High Energy",
                "Peak Time",
                "Festival/Rave"
            ]

    @classmethod
    def load_from_env(cls) -> 'DJConfig':
        """Carica configurazione da variabili ambiente"""
        config = cls()

        # API Key priority: environment > persistent settings > None
        config.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

        # Note: Persistent settings loading moved to avoid circular imports
        # API key will be loaded separately by the system when needed

        # Override da env se disponibili
        if os.getenv('MUSIC_PATH'):
            config.music_library_path = os.getenv('MUSIC_PATH')

        if os.getenv('OPENROUTER_MODEL'):
            config.openrouter_model = os.getenv('OPENROUTER_MODEL')

        return config

    def validate(self) -> tuple[bool, str]:
        """Valida configurazione"""

        # Controlla API key
        if not self.openrouter_api_key:
            return False, "OpenRouter API key mancante. Impostala con: export OPENROUTER_API_KEY='your-key'"

        # Controlla path musica
        music_path = Path(self.music_library_path)
        if not music_path.exists():
            return False, f"Cartella musica non trovata: {self.music_library_path}"

        # Controlla che ci siano file musicali
        music_files = []
        for ext in self.supported_formats:
            music_files.extend(music_path.glob(f"**/*{ext}"))

        if len(music_files) == 0:
            return False, f"Nessun file musicale trovato in: {self.music_library_path}"

        return True, f"Configurazione valida. {len(music_files)} brani trovati."

# Configurazione OpenRouter API
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

OPENROUTER_HEADERS = {
    "HTTP-Referer": "https://github.com/Fiore0312/dj",
    "X-Title": "AI DJ System"
}

# Modelli gratuiti raccomandati 2025
FREE_MODELS = {
    "deepseek_r1": {
        "name": "deepseek/deepseek-r1:free",
        "description": "Primary 2025 - Reasoning avanzato, performance eccellenti",
        "context_length": 128000,
        "good_for": ["reasoning", "analysis", "real_time", "primary"]
    },
    "hermes": {
        "name": "nousresearch/hermes-3-llama-3.1-405b",
        "description": "Fallback - Eccellente per creatività musicale e decisioni DJ",
        "context_length": 128000,
        "good_for": ["creative", "music", "fallback"]
    },
    "deepseek_v3": {
        "name": "deepseek/deepseek-v3-base:free",
        "description": "Ultra-veloce per operazioni urgenti",
        "context_length": 32768,
        "good_for": ["speed", "urgent", "lightweight"]
    },
}

# Venue types per DJ decisions
VENUE_TYPES = {
    "club": {
        "description": "Club notturno",
        "typical_genres": ["house", "techno", "progressive", "deep house"],
        "energy_curve": "gradual_build",
        "bpm_range": (125, 135)
    },
    "festival": {
        "description": "Festival/Outdoor",
        "typical_genres": ["EDM", "big room", "progressive house", "trance"],
        "energy_curve": "high_energy",
        "bpm_range": (128, 140)
    },
    "bar": {
        "description": "Bar/Lounge",
        "typical_genres": ["chill", "nu-disco", "indie dance", "house"],
        "energy_curve": "steady_medium",
        "bpm_range": (115, 128)
    },
    "wedding": {
        "description": "Matrimonio/Evento privato",
        "typical_genres": ["pop", "rock", "classics", "dance"],
        "energy_curve": "varied",
        "bpm_range": (110, 140)
    },
    "radio": {
        "description": "Radio/Streaming",
        "typical_genres": ["pop", "hip-hop", "electronic", "indie"],
        "energy_curve": "consistent",
        "bpm_range": (90, 130)
    }
}

# Event types per DJ strategy
EVENT_TYPES = {
    "opening": "Set di apertura - energia graduale",
    "prime_time": "Prime time - energia alta",
    "closing": "Closing - energia massima poi graduale discesa",
    "after_hours": "After hours - underground e profondo",
    "warm_up": "Warm up - preparazione crowd",
    "cool_down": "Cool down - rilassamento graduale"
}

def get_config() -> DJConfig:
    """Ottieni configurazione del sistema"""
    return DJConfig.load_from_env()

def load_api_key_from_persistent_settings() -> Optional[str]:
    """Carica API key dai settings persistenti, evitando import circolari"""
    try:
        # Import locale per evitare circular imports
        from core.persistent_config import get_persistent_settings
        persistent = get_persistent_settings()
        if hasattr(persistent, 'openrouter_api_key') and persistent.openrouter_api_key:
            return persistent.openrouter_api_key
    except Exception as e:
        # Fallback gracefully if persistent config fails
        print(f"⚠️  Could not load API key from persistent settings: {e}")
    return None

def check_system_requirements() -> Dict[str, Any]:
    """Controlla requisiti sistema"""
    status = {
        "python_version": True,
        "music_library": False,
        "midi_system": False,
        "api_key": False,
        "errors": []
    }

    # Controlla Python version
    import sys
    if sys.version_info < (3, 8):
        status["python_version"] = False
        status["errors"].append("Python 3.8+ richiesto")

    # Controlla music library
    config = get_config()
    music_path = Path(config.music_library_path)
    if music_path.exists():
        music_files = []
        for ext in config.supported_formats:
            music_files.extend(music_path.glob(f"**/*{ext}"))

        if len(music_files) > 0:
            status["music_library"] = True
            status["music_files_count"] = len(music_files)
        else:
            status["errors"].append("Nessun file musicale trovato")
    else:
        status["errors"].append(f"Cartella musica non trovata: {config.music_library_path}")

    # Controlla API key - priority: config > persistent settings
    api_key = config.openrouter_api_key
    if not api_key:
        api_key = load_api_key_from_persistent_settings()

    if api_key:
        status["api_key"] = True
        # Update config with loaded API key for immediate use
        config.openrouter_api_key = api_key
    else:
        status["errors"].append("OpenRouter API key mancante - aggiungila in ~/.config/dj_ai/user_settings.json o via OPENROUTER_API_KEY env var")

    # Controlla MIDI (basic check)
    try:
        import rtmidi
        status["midi_system"] = True
    except ImportError:
        status["errors"].append("rtmidi non installato: pip install python-rtmidi")

    return status

if __name__ == "__main__":
    # Test configurazione
    print("🔧 Test Configurazione Sistema DJ AI")
    print("=" * 50)

    config = get_config()
    valid, message = config.validate()

    print(f"Configurazione: {'✅ Valida' if valid else '❌ Invalida'}")
    print(f"Messaggio: {message}")

    print(f"\nImpostazioni:")
    print(f"  API Key: {'✅ Presente' if config.openrouter_api_key else '❌ Mancante'}")
    print(f"  Modello: {config.openrouter_model}")
    print(f"  Musica: {config.music_library_path}")
    print(f"  MIDI: {config.midi_device_name}")

    print(f"\nRequisiti Sistema:")
    status = check_system_requirements()
    for key, value in status.items():
        if key != "errors":
            icon = "✅" if value else "❌"
            print(f"  {key}: {icon}")

    if status["errors"]:
        print(f"\n❌ Errori:")
        for error in status["errors"]:
            print(f"  - {error}")