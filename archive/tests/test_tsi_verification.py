#!/usr/bin/env python3
"""
🧪 TSI Mapping Verification Test
Tests all MIDI mappings are working correctly with Traktor
"""

import mido
import time
from typing import Dict, List

class TSIVerificationTest:
    """Test all TSI MIDI mappings"""

    def __init__(self):
        self.test_mappings = {
            # Transport Tests
            'deck_a_play': (1, 20, 'Play/Pause Deck A'),
            'deck_b_play': (1, 21, 'Play/Pause Deck B'),
            'deck_a_cue': (1, 24, 'Cue Deck A'),
            'deck_b_cue': (1, 25, 'Cue Deck B'),

            # Volume Tests
            'deck_a_volume': (1, 28, 'Volume Deck A'),
            'deck_b_volume': (1, 29, 'Volume Deck B'),
            'crossfader': (1, 32, 'Crossfader'),
            'master_volume': (1, 33, 'Master Volume'),

            # Browser Tests
            'browser_up': (1, 37, 'Browser Up'),
            'browser_down': (1, 38, 'Browser Down'),
            'load_deck_a': (1, 39, 'Load Deck A'),
            'load_deck_b': (1, 40, 'Load Deck B'),

            # EQ Tests
            'deck_a_eq_high': (1, 34, 'Deck A EQ High'),
            'deck_a_eq_mid': (1, 35, 'Deck A EQ Mid'),
            'deck_a_eq_low': (1, 36, 'Deck A EQ Low'),
            'deck_b_eq_high': (1, 50, 'Deck B EQ High'),
            'deck_b_eq_mid': (1, 51, 'Deck B EQ Mid'),
            'deck_b_eq_low': (1, 52, 'Deck B EQ Low'),
        }

    def run_verification_test(self) -> Dict[str, bool]:
        """Run complete verification test"""
        print("🧪 Starting TSI Mapping Verification...")
        print("🎯 This will test all MIDI mappings with Traktor")
        print("📋 Watch Traktor for responses to each test\n")

        results = {}

        try:
            # Connect to MIDI
            output = mido.open_output('Bus 1')  # macOS IAC Driver
            print("✅ Connected to IAC Driver Bus 1")

        except Exception as e:
            print(f"❌ Could not connect to MIDI: {e}")
            return results

        # Test each mapping
        for control_name, (channel, cc, description) in self.test_mappings.items():
            print(f"🎛️ Testing: {description} (Ch{channel}, CC{cc})")

            try:
                # Send test MIDI message
                msg = mido.Message('control_change',
                                 channel=channel-1,  # mido uses 0-based channels
                                 control=cc,
                                 value=127)
                output.send(msg)

                # Wait for user verification
                response = input("   Did Traktor respond correctly? (y/n/skip): ").lower()

                if response == 'y':
                    results[control_name] = True
                    print("   ✅ PASSED\n")
                elif response == 'skip':
                    results[control_name] = None
                    print("   ⏭️ SKIPPED\n")
                else:
                    results[control_name] = False
                    print("   ❌ FAILED\n")

                time.sleep(0.5)  # Brief pause between tests

            except Exception as e:
                print(f"   ❌ ERROR: {e}\n")
                results[control_name] = False

        output.close()

        # Show results
        self.show_test_results(results)
        return results

    def show_test_results(self, results: Dict[str, bool]):
        """Show final test results"""

        print("\n🎯 TEST RESULTS SUMMARY")
        print("=" * 50)

        passed = sum(1 for v in results.values() if v is True)
        failed = sum(1 for v in results.values() if v is False)
        skipped = sum(1 for v in results.values() if v is None)

        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️ Skipped: {skipped}")

        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for control, result in results.items():
                if result is False:
                    channel, cc, desc = self.test_mappings[control]
                    print(f"   • {desc}: Channel {channel}, CC {cc}")

        if passed == len([v for v in results.values() if v is not None]):
            print("\n🎉 ALL TESTS PASSED! TSI mappings are working correctly!")
        else:
            print(f"\n⚠️ Some tests failed. Check Traktor Controller Manager mappings.")

if __name__ == "__main__":
    tester = TSIVerificationTest()
    tester.run_verification_test()
