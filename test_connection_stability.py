#!/usr/bin/env python3
"""
🧪 Connection Pool Stability Test
Test that verifies connection pool doesn't overflow
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.openrouter_client import OpenRouterClient, DJContext
import time
import os

def test_connection_stability():
    """Test multiple rapid requests without pool overflow"""

    print("🧪 CONNECTION POOL STABILITY TEST")
    print("=" * 40)

    api_key = os.getenv('OPENROUTER_API_KEY') or "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"
    client = OpenRouterClient(api_key)

    context = DJContext(venue_type="club", energy_level=5)

    print("🔄 Sending 10 rapid requests to test pool stability...")

    success_count = 0
    for i in range(10):
        print(f"   Request {i+1}/10...", end=" ")

        try:
            start_time = time.time()
            response = client.get_dj_decision(
                context,
                f"quick test {i+1}",
                urgent=True
            )
            end_time = time.time()

            if response.success:
                print(f"✅ OK ({(end_time-start_time)*1000:.0f}ms)")
                success_count += 1
            else:
                print(f"❌ FAILED: {response.error}")

        except Exception as e:
            print(f"❌ ERROR: {e}")

        # Small delay to test rate limiting
        time.sleep(0.1)

    # Final stats
    print(f"\n📊 RESULTS:")
    print(f"   Success: {success_count}/10")
    print(f"   Failure: {10-success_count}/10")

    if success_count >= 8:
        print("✅ CONNECTION POOL STABLE!")
    else:
        print("⚠️ Connection issues persist")

    # Cleanup
    client.close_session()
    print("🧹 Session cleaned up")

if __name__ == "__main__":
    test_connection_stability()
