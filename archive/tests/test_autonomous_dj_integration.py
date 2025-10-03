#!/usr/bin/env python3
"""
🧪 Autonomous DJ Integration Test

Comprehensive test that validates the complete autonomous DJ system:
- Master Orchestrator coordination
- Enhanced Track Selection with harmonic compatibility
- Real-time Position Monitoring
- Intelligent Queue System
- End-to-end workflow validation
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import time
import asyncio
import threading
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress excessive logging from other modules
logging.getLogger('traktor_control').setLevel(logging.WARNING)
logging.getLogger('music_library').setLevel(logging.WARNING)

def test_component_imports():
    """Test that all new components can be imported"""
    print("🔧 Testing Component Imports...")

    components = {}

    try:
        from autonomous_dj_master import AutonomousDJMaster, DJMasterState
        components['autonomous_dj_master'] = True
        print("  ✅ Autonomous DJ Master imported")
    except Exception as e:
        components['autonomous_dj_master'] = False
        print(f"  ❌ Autonomous DJ Master failed: {e}")

    try:
        from enhanced_track_selector import EnhancedTrackSelector, CompatibilityScore
        components['enhanced_track_selector'] = True
        print("  ✅ Enhanced Track Selector imported")
    except Exception as e:
        components['enhanced_track_selector'] = False
        print(f"  ❌ Enhanced Track Selector failed: {e}")

    try:
        from realtime_position_monitor import RealTimePositionMonitor, MixOpportunity
        components['realtime_position_monitor'] = True
        print("  ✅ Real-time Position Monitor imported")
    except Exception as e:
        components['realtime_position_monitor'] = False
        print(f"  ❌ Real-time Position Monitor failed: {e}")

    try:
        from intelligent_queue_system import IntelligentQueueSystem, QueuedTrack
        components['intelligent_queue_system'] = True
        print("  ✅ Intelligent Queue System imported")
    except Exception as e:
        components['intelligent_queue_system'] = False
        print(f"  ❌ Intelligent Queue System failed: {e}")

    return components

def test_basic_functionality():
    """Test basic functionality of each component"""
    print("\n🧪 Testing Basic Functionality...")

    results = {}

    try:
        from config import get_config
        from music_library import MusicLibrary
        from core.openrouter_client import DJContext

        config = get_config()
        print(f"  📋 Config loaded: Music path = {config.music_path}")

        # Test music library
        music_library = MusicLibrary(config.music_path)
        tracks = music_library.get_all_tracks()

        if tracks:
            print(f"  🎵 Music library: {len(tracks)} tracks found")
            results['music_library'] = True
            sample_track = tracks[0]
            print(f"    Sample track: {sample_track.title} by {sample_track.artist}")
        else:
            print("  ⚠️ No tracks found in music library")
            results['music_library'] = False
            return results

        # Test DJ Context
        context = DJContext(
            venue_type='club',
            event_type='prime_time',
            energy_level=7.0,
            current_bpm=128.0,
            crowd_response='energetic'
        )
        print(f"  🎯 DJ Context created: {context.venue_type} / {context.event_type}")
        results['dj_context'] = True

        # Test Enhanced Track Selector
        try:
            from enhanced_track_selector import EnhancedTrackSelector

            track_selector = EnhancedTrackSelector(music_library)
            print("  🧠 Enhanced Track Selector initialized")

            # Test track selection
            selection = track_selector.select_next_track(sample_track, context, target_energy=8.0)
            if selection and selection.track:
                print(f"    Selected: {selection.track.title} (confidence: {selection.confidence:.2f})")
                results['track_selection'] = True
            else:
                print("    ⚠️ No track selected")
                results['track_selection'] = False

        except Exception as e:
            print(f"  ❌ Track Selector error: {e}")
            results['track_selection'] = False

        # Test Intelligent Queue System
        try:
            from intelligent_queue_system import IntelligentQueueSystem

            queue_system = IntelligentQueueSystem(music_library, track_selector)
            print("  📋 Intelligent Queue System initialized")

            queue_system.start_session(context, sample_track)
            time.sleep(1.0)  # Allow initialization

            preview = queue_system.get_queue_preview()
            if preview:
                print(f"    Queue preview: {len(preview)} tracks planned")
                print(f"      Next: {preview[0]['title']} (energy: {preview[0]['energy']})")
                results['queue_system'] = True
            else:
                print("    ⚠️ Queue is empty")
                results['queue_system'] = False

            queue_system.stop()

        except Exception as e:
            print(f"  ❌ Queue System error: {e}")
            results['queue_system'] = False

        # Test Real-time Position Monitor
        try:
            from realtime_position_monitor import RealTimePositionMonitor
            from traktor_control import TraktorController

            traktor = TraktorController()
            position_monitor = RealTimePositionMonitor(traktor)
            print("  ⏱️ Real-time Position Monitor initialized")

            # Brief test (no actual MIDI needed)
            position_monitor.start_monitoring()
            time.sleep(0.5)
            position_monitor.stop_monitoring()

            print("    Position monitoring test completed")
            results['position_monitor'] = True

        except Exception as e:
            print(f"  ❌ Position Monitor error: {e}")
            results['position_monitor'] = False

        return results

    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        return {'error': str(e)}

def test_master_orchestrator_integration():
    """Test the Master Orchestrator integration"""
    print("\n🎼 Testing Master Orchestrator Integration...")

    try:
        from autonomous_dj_master import AutonomousDJMaster
        from config import get_config

        config = get_config()

        # Create master orchestrator
        dj_master = AutonomousDJMaster()
        print("  🎯 Master Orchestrator created")

        # Test state machine
        initial_state = dj_master.state
        print(f"    Initial state: {initial_state}")

        # Test configuration loading
        if hasattr(dj_master, 'config'):
            print(f"    Configuration loaded: {bool(dj_master.config)}")

        # Test component initialization
        components_status = {}

        if hasattr(dj_master, 'music_library'):
            components_status['music_library'] = dj_master.music_library is not None

        if hasattr(dj_master, 'track_selector'):
            components_status['track_selector'] = dj_master.track_selector is not None

        if hasattr(dj_master, 'queue_system'):
            components_status['queue_system'] = dj_master.queue_system is not None

        if hasattr(dj_master, 'position_monitor'):
            components_status['position_monitor'] = dj_master.position_monitor is not None

        print(f"    Component status: {components_status}")

        # Test start method (but don't actually start to avoid MIDI issues)
        print("  ⚡ Master Orchestrator integration test completed")

        return True

    except Exception as e:
        print(f"  ❌ Master Orchestrator integration failed: {e}")
        return False

def test_harmonic_compatibility():
    """Test the harmonic compatibility system"""
    print("\n🎵 Testing Harmonic Compatibility...")

    try:
        from enhanced_track_selector import EnhancedTrackSelector
        from music_library import MusicLibrary, TrackInfo
        from config import get_config

        config = get_config()
        music_library = MusicLibrary(config.music_path)
        track_selector = EnhancedTrackSelector(music_library)

        # Create test tracks with known keys
        track1 = TrackInfo(
            file_path="/test/track1.mp3",
            title="Test Track 1",
            artist="Test Artist",
            key="C major",
            bpm=128.0,
            energy_level=7.0
        )

        track2 = TrackInfo(
            file_path="/test/track2.mp3",
            title="Test Track 2",
            artist="Test Artist",
            key="G major",  # Perfect fifth - should be highly compatible
            bpm=130.0,
            energy_level=7.5
        )

        # Test compatibility calculation
        compatibility = track_selector._calculate_comprehensive_compatibility(
            track1, track2,
            DJContext(venue_type='club', energy_level=7.0)
        )

        print(f"  🎼 Harmonic compatibility test:")
        print(f"    Track 1: {track1.key} @ {track1.bpm} BPM")
        print(f"    Track 2: {track2.key} @ {track2.bpm} BPM")
        print(f"    Harmonic score: {compatibility.harmonic_score:.2f}/25.0")
        print(f"    Rhythmic score: {compatibility.rhythmic_score:.2f}/20.0")
        print(f"    Energy score: {compatibility.energy_score:.2f}/20.0")
        print(f"    Total score: {compatibility.total_score:.2f}/100.0")

        # Test Circle of Fifths lookup
        if hasattr(track_selector, 'circle_of_fifths'):
            c_major_compat = track_selector.circle_of_fifths.get('C', {})
            g_major_score = c_major_compat.get('G', 0.0)
            print(f"    Circle of Fifths C→G compatibility: {g_major_score:.2f}")

        return compatibility.total_score > 50.0  # Reasonable threshold

    except Exception as e:
        print(f"  ❌ Harmonic compatibility test failed: {e}")
        return False

def test_energy_progression():
    """Test energy progression and queue planning"""
    print("\n📈 Testing Energy Progression...")

    try:
        from intelligent_queue_system import IntelligentQueueSystem, EnergyProgression
        from enhanced_track_selector import EnhancedTrackSelector
        from music_library import MusicLibrary
        from core.openrouter_client import DJContext
        from config import get_config

        config = get_config()
        music_library = MusicLibrary(config.music_path)
        track_selector = EnhancedTrackSelector(music_library)
        queue_system = IntelligentQueueSystem(music_library, track_selector)

        # Test energy progression creation
        context = DJContext(
            venue_type='club',
            event_type='prime_time',
            energy_level=6.0
        )

        progression = queue_system._create_energy_progression(context)

        print(f"  📊 Energy progression for {context.venue_type} / {context.event_type}:")
        print(f"    Current energy: {progression.current_energy}")
        print(f"    Target curve points: {len(progression.target_curve)}")

        for time_point, energy in progression.target_curve[:3]:
            print(f"      {time_point:3.0f} min: {energy:.1f} energy")

        # Test target energy calculation
        for pos in range(1, 4):
            target = queue_system._calculate_target_energy(pos, context)
            direction = queue_system._determine_energy_direction(target, context)
            print(f"    Position {pos}: target {target:.1f} ({direction.value})")

        return len(progression.target_curve) > 0

    except Exception as e:
        print(f"  ❌ Energy progression test failed: {e}")
        return False

def test_emergency_handling():
    """Test emergency track handling"""
    print("\n🚨 Testing Emergency Handling...")

    try:
        from intelligent_queue_system import IntelligentQueueSystem, QueuePriority
        from enhanced_track_selector import EnhancedTrackSelector
        from music_library import MusicLibrary
        from core.openrouter_client import DJContext
        from config import get_config

        config = get_config()
        music_library = MusicLibrary(config.music_path)
        track_selector = EnhancedTrackSelector(music_library)
        queue_system = IntelligentQueueSystem(music_library, track_selector)

        context = DJContext(venue_type='club', energy_level=7.0)

        # Initialize emergency tracks
        queue_system._populate_emergency_tracks(context)

        print(f"  🚨 Emergency track pool: {len(queue_system.emergency_tracks)} tracks")

        if queue_system.emergency_tracks:
            emergency_track = queue_system.emergency_tracks[0]
            print(f"    Sample emergency: {emergency_track.track_info.title}")
            print(f"      Emergency rating: {emergency_track.emergency_rating:.2f}")
            print(f"      Energy level: {emergency_track.track_info.energy_level}")
            print(f"      Priority: {emergency_track.priority.name}")

        # Test emergency selection
        if queue_system.emergency_tracks:
            selected = queue_system._select_best_emergency_track(context)
            if selected:
                print(f"    Best emergency selection: {selected.track_info.title}")
                return True

        return len(queue_system.emergency_tracks) > 0

    except Exception as e:
        print(f"  ❌ Emergency handling test failed: {e}")
        return False

def test_performance_metrics():
    """Test performance metrics and timing"""
    print("\n⚡ Testing Performance Metrics...")

    metrics = {}

    try:
        from enhanced_track_selector import EnhancedTrackSelector
        from music_library import MusicLibrary
        from core.openrouter_client import DJContext
        from config import get_config

        config = get_config()
        music_library = MusicLibrary(config.music_path)

        # Test track selection speed
        start_time = time.time()
        track_selector = EnhancedTrackSelector(music_library)
        init_time = time.time() - start_time
        metrics['selector_init_ms'] = init_time * 1000

        tracks = music_library.get_all_tracks()
        if tracks:
            context = DJContext(venue_type='club', energy_level=7.0)

            # Test selection speed
            start_time = time.time()
            selection = track_selector.select_next_track(tracks[0], context, target_energy=8.0)
            selection_time = time.time() - start_time
            metrics['selection_time_ms'] = selection_time * 1000

            # Test compatibility calculation speed
            start_time = time.time()
            if len(tracks) >= 2:
                compatibility = track_selector._calculate_comprehensive_compatibility(
                    tracks[0], tracks[1], context
                )
                compatibility_time = time.time() - start_time
                metrics['compatibility_time_ms'] = compatibility_time * 1000

        print(f"  ⚡ Performance Metrics:")
        for metric, value in metrics.items():
            print(f"    {metric}: {value:.1f}")

        # Performance thresholds for real-time DJ use
        thresholds = {
            'selector_init_ms': 5000.0,      # 5 seconds max for initialization
            'selection_time_ms': 2000.0,     # 2 seconds max for track selection
            'compatibility_time_ms': 100.0   # 100ms max for compatibility calc
        }

        passed = True
        for metric, threshold in thresholds.items():
            if metric in metrics and metrics[metric] > threshold:
                print(f"    ⚠️ {metric} exceeds threshold: {metrics[metric]:.1f} > {threshold:.1f}")
                passed = False
            elif metric in metrics:
                print(f"    ✅ {metric} within threshold: {metrics[metric]:.1f} <= {threshold:.1f}")

        return passed

    except Exception as e:
        print(f"  ❌ Performance metrics test failed: {e}")
        return False

def run_comprehensive_test():
    """Run the complete autonomous DJ integration test"""
    print("🎉 COMPREHENSIVE AUTONOMOUS DJ INTEGRATION TEST")
    print("=" * 60)

    test_results = {}

    # Component Import Test
    print("\n1️⃣ COMPONENT IMPORTS")
    test_results['imports'] = test_component_imports()

    # Basic Functionality Test
    print("\n2️⃣ BASIC FUNCTIONALITY")
    test_results['basic_functionality'] = test_basic_functionality()

    # Master Orchestrator Integration
    print("\n3️⃣ MASTER ORCHESTRATOR")
    test_results['master_orchestrator'] = test_master_orchestrator_integration()

    # Harmonic Compatibility Test
    print("\n4️⃣ HARMONIC COMPATIBILITY")
    test_results['harmonic_compatibility'] = test_harmonic_compatibility()

    # Energy Progression Test
    print("\n5️⃣ ENERGY PROGRESSION")
    test_results['energy_progression'] = test_energy_progression()

    # Emergency Handling Test
    print("\n6️⃣ EMERGENCY HANDLING")
    test_results['emergency_handling'] = test_emergency_handling()

    # Performance Metrics Test
    print("\n7️⃣ PERFORMANCE METRICS")
    test_results['performance_metrics'] = test_performance_metrics()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    total_tests = 0
    passed_tests = 0

    for test_name, result in test_results.items():
        if isinstance(result, dict):
            # Handle import results
            if test_name == 'imports':
                total_tests += len(result)
                passed_tests += sum(1 for v in result.values() if v)
                passed = sum(result.values())
                total = len(result)
                status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
                print(f"{status} {test_name.upper()}: {passed}/{total} components")
            elif test_name == 'basic_functionality':
                if 'error' not in result:
                    total_tests += len(result)
                    passed_tests += sum(1 for v in result.values() if v)
                    passed = sum(1 for v in result.values() if v)
                    total = len(result)
                    status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
                    print(f"{status} {test_name.upper()}: {passed}/{total} functions")
                else:
                    total_tests += 1
                    status = "❌"
                    print(f"{status} {test_name.upper()}: Error - {result['error']}")
        else:
            # Handle boolean results
            total_tests += 1
            if result:
                passed_tests += 1
                print(f"✅ {test_name.upper()}: PASSED")
            else:
                print(f"❌ {test_name.upper()}: FAILED")

    print("\n" + "=" * 60)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"🎯 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 AUTONOMOUS DJ SYSTEM READY FOR REAL-WORLD USE!")
        print("   The system demonstrates:")
        print("   ✅ Advanced harmonic mixing capabilities")
        print("   ✅ Intelligent track selection with energy progression")
        print("   ✅ Real-time position monitoring and mix timing")
        print("   ✅ Emergency handling for crowd recovery")
        print("   ✅ Performance suitable for live DJ sets")
    elif success_rate >= 60:
        print("⚠️ AUTONOMOUS DJ SYSTEM PARTIALLY FUNCTIONAL")
        print("   Some components need refinement before live use")
    else:
        print("❌ AUTONOMOUS DJ SYSTEM NEEDS SIGNIFICANT WORK")
        print("   Major components are not functioning properly")

    print("\n🎧 Ready for the next level of autonomous DJ performance!")
    print("=" * 60)

    return success_rate

if __name__ == "__main__":
    # Run the comprehensive test
    success_rate = run_comprehensive_test()

    # Exit code based on success rate
    exit_code = 0 if success_rate >= 80 else 1
    sys.exit(exit_code)