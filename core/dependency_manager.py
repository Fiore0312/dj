#!/usr/bin/env python3
"""
🔧 Dependency Manager per DJ AI System
Gestione centralizzata delle dipendenze opzionali ispirata a Librosa
Implementa lazy loading e graceful degradation
"""

import logging
from typing import Optional, Any, Dict, Type, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DependencyStatus:
    """Status delle dipendenze del sistema"""
    librosa_available: bool = False
    essentia_available: bool = False
    sounddevice_available: bool = False
    autonomous_available: bool = False
    audio_analysis_available: bool = False

class MockAudioFeatures:
    """Mock object per AudioFeatures quando non disponibile"""
    def __init__(self, **kwargs):
        self.mock = True
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<MockAudioFeatures: Advanced analysis not available>"

class MockLibrosa:
    """Mock object per librosa quando non disponibile"""
    def __init__(self):
        self.mock = True

    def load(self, *args, **kwargs):
        raise ImportError("librosa not available. Install with: pip install librosa")

    def __getattr__(self, name):
        def mock_function(*args, **kwargs):
            raise ImportError(f"librosa.{name} not available. Install with: pip install librosa")
        return mock_function

class MockEssentia:
    """Mock object per essentia quando non disponibile"""
    def __init__(self):
        self.mock = True

    def __getattr__(self, name):
        def mock_function(*args, **kwargs):
            raise ImportError(f"essentia.{name} not available. Install with: pip install essentia-tensorflow")
        return mock_function

class DependencyManager:
    """
    Gestore centralizzato delle dipendenze opzionali
    Implementa lazy loading e fallback per dipendenze pesanti
    """

    _instance: Optional['DependencyManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Lazy-loaded dependencies
        self._librosa = None
        self._essentia = None
        self._sounddevice = None
        self._audio_features_class = None
        self._real_time_analyzer_class = None

        # Dependency status cache
        self._status = None
        self._status_checked = False

        self._initialized = True
        logger.info("🔧 Dependency Manager initialized")

    @property
    def status(self) -> DependencyStatus:
        """Get dependency status (cached)"""
        if not self._status_checked:
            self._status = self._check_dependencies()
            self._status_checked = True
        return self._status

    def _check_dependencies(self) -> DependencyStatus:
        """Check which dependencies are available"""
        status = DependencyStatus()

        # Check librosa
        try:
            import librosa
            status.librosa_available = True
            logger.debug("✅ librosa available")
        except ImportError as e:
            logger.debug(f"⚠️ librosa not available: {e}")

        # Check essentia (with timeout protection)
        try:
            # Quick availability check without full import
            import importlib.util
            spec = importlib.util.find_spec("essentia")
            if spec is not None:
                # Try a minimal import to avoid SDL2 issues
                import sys
                if 'essentia' not in sys.modules:
                    # Skip full import on macOS to avoid SDL2 timeout
                    import platform
                    if platform.system() == 'Darwin':
                        logger.debug("⚠️ essentia detected but skipping full import on macOS (SDL2 issues)")
                        status.essentia_available = False
                    else:
                        import essentia
                        status.essentia_available = True
                        logger.debug("✅ essentia available")
                else:
                    status.essentia_available = True
                    logger.debug("✅ essentia already loaded")
            else:
                status.essentia_available = False
                logger.debug("⚠️ essentia not installed")
        except Exception as e:
            logger.debug(f"⚠️ essentia check failed: {e}")
            status.essentia_available = False

        # Check sounddevice
        try:
            import sounddevice
            status.sounddevice_available = True
            logger.debug("✅ sounddevice available")
        except ImportError as e:
            logger.debug(f"⚠️ sounddevice not available: {e}")

        # Audio analysis availability
        status.audio_analysis_available = status.librosa_available and status.essentia_available

        # Autonomous system availability
        status.autonomous_available = (
            status.librosa_available and
            status.essentia_available and
            status.sounddevice_available
        )

        return status

    @property
    def librosa(self):
        """Get librosa with lazy loading"""
        if self._librosa is None:
            try:
                import librosa
                self._librosa = librosa
                logger.debug("📚 librosa loaded successfully")
            except ImportError as e:
                logger.warning(f"📚 librosa not available: {e}")
                self._librosa = MockLibrosa()
        return self._librosa

    @property
    def essentia(self):
        """Get essentia with lazy loading"""
        if self._essentia is None:
            try:
                import essentia
                self._essentia = essentia
                logger.debug("🎵 essentia loaded successfully")
            except ImportError as e:
                logger.warning(f"🎵 essentia not available: {e}")
                self._essentia = MockEssentia()
        return self._essentia

    @property
    def sounddevice(self):
        """Get sounddevice with lazy loading"""
        if self._sounddevice is None:
            try:
                import sounddevice
                self._sounddevice = sounddevice
                logger.debug("🔊 sounddevice loaded successfully")
            except ImportError as e:
                logger.warning(f"🔊 sounddevice not available: {e}")
                self._sounddevice = None
        return self._sounddevice

    def get_audio_features_class(self) -> Type:
        """Get AudioFeatures class with lazy loading"""
        if self._audio_features_class is None:
            if self.status.audio_analysis_available:
                try:
                    from autonomous_audio_engine import AudioFeatures
                    self._audio_features_class = AudioFeatures
                    logger.debug("🎛️ AudioFeatures class loaded")
                except ImportError as e:
                    logger.warning(f"🎛️ AudioFeatures not available: {e}")
                    self._audio_features_class = MockAudioFeatures
            else:
                self._audio_features_class = MockAudioFeatures
        return self._audio_features_class

    def get_real_time_analyzer_class(self) -> Optional[Type]:
        """Get RealTimeAnalyzer class with lazy loading"""
        if self._real_time_analyzer_class is None:
            if self.status.audio_analysis_available:
                try:
                    from autonomous_audio_engine import RealTimeAnalyzer
                    self._real_time_analyzer_class = RealTimeAnalyzer
                    logger.debug("📊 RealTimeAnalyzer class loaded")
                except ImportError as e:
                    logger.warning(f"📊 RealTimeAnalyzer not available: {e}")
                    self._real_time_analyzer_class = None
            else:
                self._real_time_analyzer_class = None
        return self._real_time_analyzer_class

    def create_audio_features(self, **kwargs) -> Union[Any, MockAudioFeatures]:
        """Factory method for AudioFeatures objects"""
        audio_features_class = self.get_audio_features_class()
        try:
            return audio_features_class(**kwargs)
        except Exception as e:
            logger.warning(f"Failed to create AudioFeatures: {e}")
            return MockAudioFeatures(**kwargs)

    def get_autonomous_components(self) -> Dict[str, Optional[Type]]:
        """Get all autonomous system components"""
        if not self.status.autonomous_available:
            logger.warning("🤖 Autonomous components not available")
            return {
                'AutonomousDecisionEngine': None,
                'AutonomousMixingController': None,
                'DJMemorySystem': None,
                'AudioFeatures': MockAudioFeatures,
                'RealTimeAnalyzer': None
            }

        try:
            from autonomous_decision_engine import AutonomousDecisionEngine
            from autonomous_mixing_controller import AutonomousMixingController
            from dj_memory_system import DJMemorySystem

            return {
                'AutonomousDecisionEngine': AutonomousDecisionEngine,
                'AutonomousMixingController': AutonomousMixingController,
                'DJMemorySystem': DJMemorySystem,
                'AudioFeatures': self.get_audio_features_class(),
                'RealTimeAnalyzer': self.get_real_time_analyzer_class()
            }
        except ImportError as e:
            logger.error(f"🤖 Failed to load autonomous components: {e}")
            return {
                'AutonomousDecisionEngine': None,
                'AutonomousMixingController': None,
                'DJMemorySystem': None,
                'AudioFeatures': MockAudioFeatures,
                'RealTimeAnalyzer': None
            }

    def print_dependency_status(self):
        """Print comprehensive dependency status"""
        status = self.status

        print("🔧 DJ AI System - Dependency Status")
        print("=" * 40)
        print(f"📚 Librosa: {'✅ Available' if status.librosa_available else '❌ Missing'}")
        print(f"🎵 Essentia: {'✅ Available' if status.essentia_available else '❌ Missing'}")
        print(f"🔊 SoundDevice: {'✅ Available' if status.sounddevice_available else '❌ Missing'}")
        print(f"🎛️ Audio Analysis: {'✅ Available' if status.audio_analysis_available else '❌ Limited'}")
        print(f"🤖 Autonomous System: {'✅ Available' if status.autonomous_available else '❌ Fallback Mode'}")

        if not status.autonomous_available:
            print("\n💡 To enable autonomous features, install:")
            if not status.librosa_available:
                print("   pip install librosa")
            if not status.essentia_available:
                print("   pip install essentia-tensorflow")
            if not status.sounddevice_available:
                print("   pip install sounddevice")

# Global instance
_dependency_manager = None

def get_dependency_manager() -> DependencyManager:
    """Get global dependency manager instance"""
    global _dependency_manager
    if _dependency_manager is None:
        _dependency_manager = DependencyManager()
    return _dependency_manager

# Convenience functions
def get_audio_features_class() -> Type:
    """Get AudioFeatures class or mock"""
    return get_dependency_manager().get_audio_features_class()

def create_audio_features(**kwargs) -> Union[Any, MockAudioFeatures]:
    """Create AudioFeatures object or mock"""
    return get_dependency_manager().create_audio_features(**kwargs)

def is_autonomous_available() -> bool:
    """Check if autonomous system is available"""
    return get_dependency_manager().status.autonomous_available

def is_audio_analysis_available() -> bool:
    """Check if audio analysis is available"""
    return get_dependency_manager().status.audio_analysis_available

if __name__ == "__main__":
    # Test dependency manager
    dm = get_dependency_manager()
    dm.print_dependency_status()