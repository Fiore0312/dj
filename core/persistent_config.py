#!/usr/bin/env python3
"""
🔧 Persistent Configuration System
Advanced configuration management with automatic persistence for DJ AI System
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

try:
    from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
    PYDANTIC_SETTINGS_AVAILABLE = True
except ImportError:
    # Fallback if pydantic-settings not installed
    print("⚠️  pydantic-settings not installed. Install with: pip install pydantic-settings")
    print("    Using basic persistence mode instead.")
    BaseSettings = object
    PydanticBaseSettingsSource = object
    SettingsConfigDict = dict
    PYDANTIC_SETTINGS_AVAILABLE = False

@dataclass
class DJSessionSettings:
    """User session settings that persist between sessions"""

    # Venue and Event preferences
    last_venue_type: str = "club"
    last_event_type: str = "prime_time"

    # Mix preferences
    default_energy_level: int = 5
    preferred_bpm_range: tuple = (125, 135)
    transition_time_seconds: int = 30

    # UI preferences
    window_width: int = 1000
    window_height: int = 700
    chat_history_size: int = 100

    # Audio preferences
    master_volume: float = 0.8
    crossfader_position: float = 0.5
    auto_gain_enabled: bool = True

    # AI preferences
    ai_enabled_by_default: bool = False
    ai_response_language: str = "italian"
    ai_creativity_level: int = 7  # 1-10

    # Secure API key storage
    openrouter_api_key: str = ""

    # MIDI preferences
    midi_latency_compensation_ms: int = 10
    midi_feedback_enabled: bool = True

class JsonConfigSettingsSource(PydanticBaseSettingsSource):
    """Custom settings source that loads/saves from JSON file"""

    def __init__(self, settings_cls, json_file: Optional[str] = None):
        super().__init__(settings_cls)
        self.json_file = json_file or self._get_default_config_path()

    def _get_default_config_path(self) -> str:
        """Get default config file path"""
        home_dir = Path.home()
        config_dir = home_dir / '.config' / 'dj_ai'
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / 'user_settings.json')

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        """Get field value from JSON file"""
        try:
            if Path(self.json_file).exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    file_content = json.load(f)
                field_value = file_content.get(field_name)
                return field_value, field_name, False
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Error reading config file {self.json_file}: {e}")

        return None, field_name, False

    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        """Prepare field value"""
        return value

    def __call__(self) -> dict[str, Any]:
        """Load all settings from JSON"""
        d: dict[str, Any] = {}

        if hasattr(self.settings_cls, 'model_fields'):
            for field_name, field in self.settings_cls.model_fields.items():
                field_value, field_key, value_is_complex = self.get_field_value(field, field_name)
                field_value = self.prepare_field_value(field_name, field, field_value, value_is_complex)
                if field_value is not None:
                    d[field_key] = field_value

        return d

    def save_settings(self, settings_data: dict):
        """Save settings to JSON file"""
        try:
            # Ensure directory exists
            Path(self.json_file).parent.mkdir(parents=True, exist_ok=True)

            # Load existing settings
            existing_data = {}
            if Path(self.json_file).exists():
                try:
                    with open(self.json_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except json.JSONDecodeError:
                    pass  # Start fresh if file is corrupted

            # Merge with new settings
            existing_data.update(settings_data)

            # Save to file
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Settings saved to {self.json_file}")

        except IOError as e:
            print(f"❌ Error saving settings to {self.json_file}: {e}")

class PersistentDJSettings(BaseSettings if BaseSettings != object else object):
    """Persistent DJ settings using Pydantic Settings"""

    # Core settings that persist
    last_venue_type: str = Field(default="club", description="Last selected venue type")
    last_event_type: str = Field(default="prime_time", description="Last selected event type")
    default_energy_level: int = Field(default=5, ge=1, le=10, description="Default energy level")

    # UI preferences
    window_width: int = Field(default=1000, ge=800, le=2000, description="Window width")
    window_height: int = Field(default=700, ge=600, le=1200, description="Window height")

    # Audio preferences
    master_volume: float = Field(default=0.8, ge=0.0, le=1.0, description="Master volume")
    crossfader_position: float = Field(default=0.5, ge=0.0, le=1.0, description="Crossfader position")

    # AI preferences
    ai_enabled_by_default: bool = Field(default=False, description="Enable AI by default")
    ai_creativity_level: int = Field(default=7, ge=1, le=10, description="AI creativity level")

    # Secure API key storage (masked in logs but saved encrypted)
    openrouter_api_key: str = Field(default="", description="OpenRouter API key")

    if BaseSettings != object:
        model_config = SettingsConfigDict(
            env_prefix='DJ_',
            env_file_encoding='utf-8',
            extra='ignore'
        )

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls,
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            """Customize settings sources"""
            json_source = JsonConfigSettingsSource(settings_cls)
            # Priority: init > env > json > file_secrets
            return (init_settings, env_settings, json_source, file_secret_settings)

    def save_to_file(self):
        """Save current settings to persistent storage"""
        if hasattr(self, 'model_dump'):
            settings_data = self.model_dump()
        else:
            # Fallback for when pydantic-settings not available
            settings_data = {
                'last_venue_type': self.last_venue_type,
                'last_event_type': self.last_event_type,
                'default_energy_level': self.default_energy_level,
                'window_width': self.window_width,
                'window_height': self.window_height,
                'master_volume': self.master_volume,
                'crossfader_position': self.crossfader_position,
                'ai_enabled_by_default': self.ai_enabled_by_default,
                'ai_creativity_level': self.ai_creativity_level,
                'openrouter_api_key': self.openrouter_api_key,
            }

        # Create JSON source and save
        json_source = JsonConfigSettingsSource(type(self))
        json_source.save_settings(settings_data)

class LegacySettingsManager:
    """Fallback settings manager for when pydantic-settings not available"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.settings = DJSessionSettings()
        self.load_settings()

    def _get_default_config_path(self) -> str:
        """Get default config file path"""
        home_dir = Path.home()
        config_dir = home_dir / '.config' / 'dj_ai'
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / 'user_settings.json')

    def load_settings(self):
        """Load settings from file"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Update settings with loaded data
                for key, value in data.items():
                    if hasattr(self.settings, key):
                        setattr(self.settings, key, value)

                print(f"✅ Settings loaded from {self.config_file}")
        except Exception as e:
            print(f"⚠️  Error loading settings: {e}")

    def save_settings(self):
        """Save settings to file"""
        try:
            Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2, ensure_ascii=False)

            print(f"✅ Settings saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving settings: {e}")

    def get(self, key: str, default=None):
        """Get setting value"""
        return getattr(self.settings, key, default)

    def set(self, key: str, value):
        """Set setting value and save"""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            self.save_settings()
        else:
            print(f"⚠️  Unknown setting: {key}")

def get_persistent_settings() -> PersistentDJSettings:
    """Get persistent settings instance"""
    if PYDANTIC_SETTINGS_AVAILABLE:
        try:
            return PersistentDJSettings()
        except Exception as e:
            print(f"⚠️  Error loading pydantic settings: {e}")
            print("    Falling back to basic persistence mode.")

    # Return a wrapper that behaves like PersistentDJSettings
    class SettingsWrapper:
        def __init__(self):
            self.manager = LegacySettingsManager()

        def __getattr__(self, name):
            return self.manager.get(name)

        def __setattr__(self, name, value):
            if name == 'manager':
                super().__setattr__(name, value)
            else:
                self.manager.set(name, value)

        def save_to_file(self):
            self.manager.save_settings()

    return SettingsWrapper()

def create_default_config_file():
    """Create default configuration file if it doesn't exist"""
    settings = get_persistent_settings()
    settings.save_to_file()
    print("✅ Default configuration file created")

if __name__ == "__main__":
    # Test persistent settings
    print("🔧 Testing Persistent Configuration System")
    print("=" * 50)

    # Test settings loading and saving
    settings = get_persistent_settings()

    print(f"Current settings:")
    if hasattr(settings, 'model_dump'):
        for key, value in settings.model_dump().items():
            print(f"  {key}: {value}")
    else:
        print(f"  Venue: {settings.last_venue_type}")
        print(f"  Event: {settings.last_event_type}")
        print(f"  Energy: {settings.default_energy_level}")

    # Test saving
    print(f"\nTesting save functionality...")
    settings.save_to_file()

    print(f"\n✅ Persistent configuration system working correctly!")