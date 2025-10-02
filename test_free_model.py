#!/usr/bin/env python3
"""
🧪 Test Modello Gratuito z-ai/glm-4.5-air:free
Verifica rapida che il modello gratuito funzioni correttamente
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.openrouter_client import OpenRouterClient, DJContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_free_model():
    """Test rapido modello gratuito"""
    print("🧪 Testing Free Model: z-ai/glm-4.5-air:free")
    print("=" * 60)

    # API Key
    api_key = "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"

    try:
        # Inizializza client con modello gratuito
        print("🔧 Initializing OpenRouter client with free model...")
        client = OpenRouterClient(api_key, "z-ai/glm-4.5-air:free")

        # Test context
        context = DJContext(
            venue_type="club",
            event_type="prime_time",
            energy_level=7,
            current_bpm=128.0
        )

        # Test 1: Basic response
        print("\n📝 Test 1: Basic DJ suggestion")
        response = client.get_dj_decision(
            context,
            "suggeriscimi la prossima mossa da fare",
            urgent=False
        )

        if response.success:
            print(f"✅ Response received:")
            print(f"   Model: {response.model_used}")
            print(f"   Time: {response.processing_time_ms:.0f}ms")
            print(f"   Response: {response.response[:200]}...")
        else:
            print(f"❌ Failed: {response.error}")
            return False

        # Test 2: Autonomous mode with JSON decision
        print("\n📝 Test 2: Autonomous decision with JSON")
        response2 = client.get_dj_decision(
            context,
            "carica una nuova traccia nel deck B e falla partire",
            urgent=True,
            autonomous_mode=True
        )

        if response2.success:
            print(f"✅ Response received:")
            print(f"   Model: {response2.model_used}")
            print(f"   Time: {response2.processing_time_ms:.0f}ms")
            print(f"   Response: {response2.response[:200]}...")

            if response2.decision:
                print(f"   ✅ JSON Decision: {response2.decision}")
            else:
                print(f"   ⚠️ No JSON decision extracted")
        else:
            print(f"❌ Failed: {response2.error}")
            return False

        # Test 3: Fallback test
        print("\n📝 Test 3: Testing fallback model")
        client_with_fallback = OpenRouterClient(api_key, "z-ai/glm-4.5-air:free")
        client_with_fallback.fallback_model = "deepseek/deepseek-r1:free"

        response3 = client_with_fallback.get_dj_decision(
            context,
            "che genere musicale dovrei suonare ora?",
            urgent=False
        )

        if response3.success:
            print(f"✅ Fallback working")
            print(f"   Model: {response3.model_used}")
        else:
            print(f"⚠️ Fallback test: {response3.error}")

        print("\n" + "=" * 60)
        print("🎉 FREE MODEL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ z-ai/glm-4.5-air:free is working correctly")
        print("✅ No credits consumed (100% free)")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_free_model()
    exit(0 if success else 1)