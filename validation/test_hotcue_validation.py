#!/usr/bin/env python3
"""
🎯 HOTCUE Validation Tool - Comprehensive Testing of 32-HOTCUE System
Tests all HOTCUE mappings, validates conflict resolution, and verifies system integrity
"""

import time
import json
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'core'))

try:
    from core.traktor_control import TraktorController, DeckID, get_traktor_controller
    from core.config import get_config
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Core modules not available: {e}")
    try:
        # Fallback: try without core prefix
        from traktor_control import TraktorController, DeckID, get_traktor_controller
        from config import get_config
        CORE_AVAILABLE = True
    except ImportError as e2:
        print(f"❌ Fallback import also failed: {e2}")
        CORE_AVAILABLE = False
        # Create mock classes for type hints
        class DeckID:
            A = "A"
            B = "B"
            C = "C"
            D = "D"
            value = "A"

@dataclass
class HOTCUEValidationResult:
    """Result of HOTCUE validation test"""
    deck: str
    hotcue_number: int
    cc: int
    success: bool
    error_message: str = ""
    response_time_ms: float = 0.0

@dataclass
class ValidationReport:
    """Complete validation report"""
    timestamp: str
    total_hotcues: int
    successful_tests: int
    failed_tests: int
    success_rate: float
    conflict_resolution_verified: bool
    deck_results: Dict[str, List[HOTCUEValidationResult]]
    recommendations: List[str]
    system_ready: bool

class HOTCUEValidator:
    def __init__(self):
        self.controller: Optional[TraktorController] = None
        self.validation_results: List[HOTCUEValidationResult] = []

        # Expected HOTCUE mappings (matching traktor_control.py)
        self.expected_mappings = {
            # DECK A - Conflict-free CC range (86-93)
            'A': [86, 87, 88, 89, 90, 91, 92, 93],
            # DECK B - Clean CC range (94-96, 105-109)
            'B': [94, 95, 96, 105, 106, 107, 108, 109],
            # DECK C - Higher CC range (110-117)
            'C': [110, 111, 112, 113, 114, 115, 116, 117],
            # DECK D - Final CC range (118-125)
            'D': [118, 119, 120, 121, 122, 123, 124, 125]
        }

        # Original conflicting mappings for verification
        self.original_conflicts = {
            'deck_a_hotcue_2': 2,  # Should now be 87
            'deck_a_hotcue_3': 3,  # Should now be 88
            'deck_a_hotcue_4': 4,  # Should now be 89
        }

    def initialize_controller(self) -> bool:
        """Initialize Traktor controller"""
        if not CORE_AVAILABLE:
            print("❌ Core modules not available")
            return False

        try:
            print("🔌 Initializing Traktor controller...")
            config = get_config()
            self.controller = get_traktor_controller(config)

            # Use output-only mode for testing
            success = self.controller.connect_with_gil_safety(output_only=True, timeout=10.0)

            if success:
                print("✅ Controller initialized successfully")
                return True
            else:
                print("❌ Controller initialization failed")
                return False

        except Exception as e:
            print(f"❌ Controller initialization error: {e}")
            return False

    def validate_conflict_resolution(self) -> bool:
        """Verify that original conflicts have been resolved"""
        print("\n🔍 VALIDATING CONFLICT RESOLUTION")
        print("=" * 60)

        if not self.controller:
            print("❌ Controller not initialized")
            return False

        conflict_resolved = True

        # Check that Deck A HOTCUE 2,3,4 no longer use CC 2,3,4
        for hotcue_name, old_cc in self.original_conflicts.items():
            # Get current mapping from controller
            if hasattr(self.controller, 'MIDI_MAP') and hotcue_name in self.controller.MIDI_MAP:
                current_channel, current_cc = self.controller.MIDI_MAP[hotcue_name]

                if current_cc == old_cc:
                    print(f"❌ CONFLICT NOT RESOLVED: {hotcue_name} still uses CC {old_cc}")
                    conflict_resolved = False
                else:
                    print(f"✅ CONFLICT RESOLVED: {hotcue_name} CC {old_cc} → CC {current_cc}")
            else:
                print(f"⚠️  Mapping not found: {hotcue_name}")
                conflict_resolved = False

        return conflict_resolved

    def test_single_hotcue(self, deck: DeckID, hotcue_number: int) -> HOTCUEValidationResult:
        """Test single HOTCUE trigger"""
        start_time = time.time()

        try:
            # Get expected CC for this hotcue
            expected_cc = self.expected_mappings[deck.value][hotcue_number - 1]

            # Test HOTCUE trigger
            success = self.controller.trigger_hotcue(deck, hotcue_number)

            response_time = (time.time() - start_time) * 1000  # Convert to ms

            return HOTCUEValidationResult(
                deck=deck.value,
                hotcue_number=hotcue_number,
                cc=expected_cc,
                success=success,
                response_time_ms=response_time
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HOTCUEValidationResult(
                deck=deck.value,
                hotcue_number=hotcue_number,
                cc=0,
                success=False,
                error_message=str(e),
                response_time_ms=response_time
            )

    def test_deck_hotcues(self, deck: DeckID) -> List[HOTCUEValidationResult]:
        """Test all 8 hotcues for a specific deck"""
        print(f"\n🎯 TESTING DECK {deck.value} HOTCUES (8 tests)")
        print(f"{'='*40}")

        deck_results = []

        for hotcue_num in range(1, 9):
            print(f"   Testing HOTCUE {hotcue_num}...", end=" ")

            result = self.test_single_hotcue(deck, hotcue_num)
            deck_results.append(result)

            if result.success:
                print(f"✅ CC {result.cc} ({result.response_time_ms:.1f}ms)")
            else:
                print(f"❌ FAILED - {result.error_message}")

            # Brief delay between tests
            time.sleep(0.1)

        success_count = sum(1 for r in deck_results if r.success)
        print(f"   📊 Deck {deck.value} Results: {success_count}/8 successful")

        return deck_results

    def test_all_hotcues(self) -> List[HOTCUEValidationResult]:
        """Test all 32 hotcues across all 4 decks"""
        print("\n🎯 COMPREHENSIVE 32-HOTCUE SYSTEM TEST")
        print("=" * 60)

        all_results = []

        for deck in [DeckID.A, DeckID.B, DeckID.C, DeckID.D]:
            deck_results = self.test_deck_hotcues(deck)
            all_results.extend(deck_results)

        return all_results

    def analyze_results(self, results: List[HOTCUEValidationResult]) -> ValidationReport:
        """Analyze validation results and create report"""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - successful_tests
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0

        # Group results by deck
        deck_results = {}
        for result in results:
            if result.deck not in deck_results:
                deck_results[result.deck] = []
            deck_results[result.deck].append(result)

        # Generate recommendations
        recommendations = []
        if success_rate < 1.0:
            recommendations.append(f"Fix {failed_tests} failed HOTCUE mappings")
        if success_rate < 0.8:
            recommendations.append("Check Traktor Controller Manager configuration")
            recommendations.append("Verify IAC Driver Bus 1 is enabled")
        if success_rate == 1.0:
            recommendations.append("All HOTCUE mappings validated successfully")
            recommendations.append("System ready for production use")

        # Verify conflict resolution
        conflict_resolved = self.validate_conflict_resolution()

        return ValidationReport(
            timestamp=datetime.now().isoformat(),
            total_hotcues=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            conflict_resolution_verified=conflict_resolved,
            deck_results={deck: results for deck, results in deck_results.items()},
            recommendations=recommendations,
            system_ready=(success_rate == 1.0 and conflict_resolved)
        )

    def save_report(self, report: ValidationReport, filename: Optional[str] = None) -> str:
        """Save validation report to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hotcue_validation_report_{timestamp}.json"

        filepath = os.path.join(os.path.dirname(__file__), filename)

        # Convert dataclass to dict for JSON serialization
        report_dict = {
            'timestamp': report.timestamp,
            'total_hotcues': report.total_hotcues,
            'successful_tests': report.successful_tests,
            'failed_tests': report.failed_tests,
            'success_rate': report.success_rate,
            'conflict_resolution_verified': report.conflict_resolution_verified,
            'recommendations': report.recommendations,
            'system_ready': report.system_ready,
            'deck_results': {
                deck: [
                    {
                        'deck': r.deck,
                        'hotcue_number': r.hotcue_number,
                        'cc': r.cc,
                        'success': r.success,
                        'error_message': r.error_message,
                        'response_time_ms': r.response_time_ms
                    }
                    for r in results
                ]
                for deck, results in report.deck_results.items()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(report_dict, f, indent=2)

        return filepath

    def print_summary_report(self, report: ValidationReport):
        """Print comprehensive summary report"""
        print("\n" + "="*80)
        print("🎯 HOTCUE VALIDATION SUMMARY REPORT")
        print("="*80)

        print(f"📅 Timestamp: {report.timestamp}")
        print(f"🎛️  System: 32-HOTCUE Professional System")
        print(f"📊 Total Tests: {report.total_hotcues}")
        print(f"✅ Successful: {report.successful_tests}")
        print(f"❌ Failed: {report.failed_tests}")
        print(f"📈 Success Rate: {report.success_rate:.1%}")

        # Conflict resolution status
        if report.conflict_resolution_verified:
            print(f"🔧 Conflict Resolution: ✅ VERIFIED")
        else:
            print(f"🔧 Conflict Resolution: ❌ FAILED")

        # System readiness
        if report.system_ready:
            print(f"🚀 System Status: ✅ READY FOR PRODUCTION")
        else:
            print(f"🚀 System Status: ⚠️  NEEDS ATTENTION")

        # Deck-by-deck breakdown
        print(f"\n📋 DECK BREAKDOWN:")
        for deck, results in report.deck_results.items():
            successful = sum(1 for r in results if r.success)
            total = len(results)
            print(f"   Deck {deck}: {successful}/{total} ({successful/total:.1%})")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"   {i}. {rec}")

        print("="*80)

    def run_full_validation(self) -> bool:
        """Run complete HOTCUE validation suite"""
        print("🎯 HOTCUE VALIDATION TOOL")
        print("Complete 32-HOTCUE System Testing & Validation")
        print("="*80)

        # Initialize controller
        if not self.initialize_controller():
            return False

        try:
            # Run all tests
            results = self.test_all_hotcues()

            # Analyze results
            report = self.analyze_results(results)

            # Save report
            report_file = self.save_report(report)

            # Print summary
            self.print_summary_report(report)

            print(f"\n💾 Report saved: {report_file}")

            return report.system_ready

        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False

        finally:
            if self.controller:
                self.controller.disconnect()

def main():
    """Main function"""
    print("🎯 Starting HOTCUE Validation...")

    validator = HOTCUEValidator()
    success = validator.run_full_validation()

    if success:
        print("\n🏆 VALIDATION COMPLETED SUCCESSFULLY")
        print("💯 32-HOTCUE System is ready for production use!")
        return 0
    else:
        print("\n⚠️  VALIDATION COMPLETED WITH ISSUES")
        print("🔧 Please review the report and fix identified problems")
        return 1

if __name__ == "__main__":
    exit(main())