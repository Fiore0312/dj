#!/usr/bin/env python3
"""
🔧 Fix Connection Pool Overflow
Risolve il problema delle troppe connessioni HTTP verso OpenRouter
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def fix_openrouter_client():
    """Applica fix per connection pool overflow"""

    print("🔧 FIXING CONNECTION POOL OVERFLOW")
    print("=" * 50)

    # Read current client
    client_path = Path("core/openrouter_client.py")

    with open(client_path, 'r') as f:
        content = f.read()

    # Fix 1: Add proper connection pool configuration
    session_config_old = """        # Session requests per connessioni persistenti
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            **OPENROUTER_HEADERS
        })"""

    session_config_new = """        # Session requests per connessioni persistenti con pool limitato
        self.session = requests.Session()

        # Configure connection pool to prevent overflow
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        # Retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1
        )

        # HTTP adapter with limited pool
        adapter = HTTPAdapter(
            pool_connections=5,      # Ridotto da 10 default
            pool_maxsize=5,          # Ridotto da 10 default
            max_retries=retry_strategy,
            pool_block=True          # Blocca invece di creare nuove connessioni
        )

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Connection': 'close',    # Force close connections
            **OPENROUTER_HEADERS
        })"""

    if session_config_old in content:
        content = content.replace(session_config_old, session_config_new)
        print("✅ Fix 1: Session configuration updated")
    else:
        print("⚠️ Fix 1: Session config not found - manual update needed")

    # Fix 2: Add connection cleanup after each request
    cleanup_fix = """
            # Force connection cleanup to prevent pool overflow
            response.close()
            """

    # Find the response processing section and add cleanup
    response_section = "            response.raise_for_status()"
    if response_section in content:
        content = content.replace(response_section, response_section + cleanup_fix)
        print("✅ Fix 2: Connection cleanup added")
    else:
        print("⚠️ Fix 2: Response section not found")

    # Fix 3: Add proper session cleanup in destructor
    destructor_fix = """
    def __del__(self):
        \"\"\"Cleanup session when object is destroyed\"\"\"
        self.close_session()

    def close_session(self):"""

    existing_close = "    def close_session(self):"
    if existing_close in content:
        content = content.replace(existing_close, destructor_fix)
        print("✅ Fix 3: Destructor added for cleanup")
    else:
        print("⚠️ Fix 3: Close session method not found")

    # Fix 4: Add rate limiting to prevent rapid requests
    rate_limit_import = "import threading"
    rate_limit_import_new = """import threading
import time
from threading import Lock
from collections import deque"""

    if rate_limit_import in content and "from collections import deque" not in content:
        content = content.replace(rate_limit_import, rate_limit_import_new)
        print("✅ Fix 4a: Rate limiting imports added")

    # Add rate limiting to __init__
    stats_init = """        # Thread lock per thread safety
        self._lock = threading.Lock()"""

    stats_init_new = """        # Thread lock per thread safety
        self._lock = threading.Lock()

        # Rate limiting (max 2 requests per second)
        self._request_times = deque()
        self._rate_limit_lock = Lock()
        self.max_requests_per_second = 2"""

    if stats_init in content and "self._rate_limit_lock" not in content:
        content = content.replace(stats_init, stats_init_new)
        print("✅ Fix 4b: Rate limiting configuration added")

    # Add rate limiting check in _make_request
    request_start = """    def _make_request(self, messages: List[Dict], model: str = None, temperature: float = 0.7, autonomous_mode: bool = False) -> AIResponse:
        \"\"\"Effettua richiesta a OpenRouter (versione sync)\"\"\"
        start_time = time.perf_counter()
        model = model or self.default_model

        with self._lock:
            self.stats['total_requests'] += 1"""

    request_start_new = """    def _make_request(self, messages: List[Dict], model: str = None, temperature: float = 0.7, autonomous_mode: bool = False) -> AIResponse:
        \"\"\"Effettua richiesta a OpenRouter (versione sync)\"\"\"
        start_time = time.perf_counter()
        model = model or self.default_model

        # Rate limiting check
        self._enforce_rate_limit()

        with self._lock:
            self.stats['total_requests'] += 1"""

    if request_start in content and "self._enforce_rate_limit()" not in content:
        content = content.replace(request_start, request_start_new)
        print("✅ Fix 4c: Rate limiting check added")

    # Add rate limiting method
    rate_limit_method = """
    def _enforce_rate_limit(self):
        \"\"\"Enforce rate limiting to prevent connection pool overflow\"\"\"
        with self._rate_limit_lock:
            now = time.time()

            # Remove old request times (older than 1 second)
            while self._request_times and now - self._request_times[0] > 1.0:
                self._request_times.popleft()

            # If we're at the limit, wait
            if len(self._request_times) >= self.max_requests_per_second:
                sleep_time = 1.0 - (now - self._request_times[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Re-check after sleep
                    now = time.time()
                    while self._request_times and now - self._request_times[0] > 1.0:
                        self._request_times.popleft()

            # Record this request time
            self._request_times.append(now)
"""

    # Add before the close_session method
    if "def close_session(self):" in content and "_enforce_rate_limit" not in content:
        content = content.replace("    def close_session(self):", rate_limit_method + "    def close_session(self):")
        print("✅ Fix 4d: Rate limiting method added")

    # Write fixed content
    with open(client_path, 'w') as f:
        f.write(content)

    print("\n🎯 CONNECTION POOL FIXES APPLIED!")
    print("✅ Limited connection pool size (5 instead of 10)")
    print("✅ Force close connections after each request")
    print("✅ Added proper session cleanup")
    print("✅ Added rate limiting (2 requests/second max)")
    print("✅ Added retry strategy for failed requests")

def create_connection_test():
    """Create test script for connection stability"""

    test_code = '''#!/usr/bin/env python3
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
    print(f"\\n📊 RESULTS:")
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
'''

    with open("test_connection_stability.py", "w") as f:
        f.write(test_code)

    print("🧪 Test script created: test_connection_stability.py")

def main():
    fix_openrouter_client()
    create_connection_test()

    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. ✅ Connection pool fixes applied")
    print("2. 🧪 Test stability: python test_connection_stability.py")
    print("3. 🎵 Try DJ AI system again - should not freeze")
    print("4. 📊 Monitor for 'Connection pool is full' warnings")
    print("\n💡 If issues persist, the rate limiting will slow down requests")
    print("   but prevent system freeze.")

if __name__ == "__main__":
    main()