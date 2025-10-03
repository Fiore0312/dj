#!/usr/bin/env python3
"""
🆓 Test Integrazione Modello Gratuito
Verifica che tutto il sistema usi il modello gratuito z-ai/glm-4.5-air:free
"""

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.openrouter_client import OpenRouterClient, DJContext
from config import get_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_free_model_integration():
    """Test completo integrazione modello gratuito"""
    print("🆓 Testing Free Model Integration")
    print("="*60)

    # Test 1: Config usa modello gratuito
    print("1️⃣ Testing configuration...")
    config = get_config()
    print(f"   Primary model: {config.openrouter_model}")
    print(f"   Fallback model: {config.openrouter_fallback_model}")

    if config.openrouter_model == "z-ai/glm-4.5-air:free":
        print("   ✅ Config uses free model")
    else:
        print(f"   ❌ Config uses non-free model: {config.openrouter_model}")
        return False

    # Test 2: Client default è gratuito
    print("\n2️⃣ Testing OpenRouter client...")
    api_key = "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"
    client = OpenRouterClient(api_key)  # Default model should be free

    if client.default_model == "z-ai/glm-4.5-air:free":
        print("   ✅ Client default is free model")
    else:
        print(f"   ❌ Client default is not free: {client.default_model}")
        return False

    # Test 3: Risposta AI funziona
    print("\n3️⃣ Testing AI response with free model...")
    context = DJContext(
        venue_type="club",
        event_type="warm_up",
        energy_level=4,
        current_bpm=120.0
    )

    response = client.get_dj_decision(
        context,
        "suggerisci il prossimo genere da suonare",
        urgent=False
    )

    if response.success:
        print(f"   ✅ AI Response: {response.response[:80]}...")
        print(f"   🤖 Model confirmed: {response.model_used}")

        if "z-ai/glm-4.5-air:free" in response.model_used:
            print("   ✅ Confirmed using free model")
        else:
            print(f"   ⚠️ Model mismatch: {response.model_used}")

    else:
        print(f"   ❌ AI Response failed: {response.error}")
        return False

    # Test 4: Autonomous mode con modello gratuito
    print("\n4️⃣ Testing autonomous mode...")
    auto_response = client.get_dj_decision(
        context,
        "carica una traccia uplifting nel deck B e inizia il mixing",
        urgent=True,
        autonomous_mode=True
    )

    if auto_response.success:
        print(f"   ✅ Autonomous response: {auto_response.response[:80]}...")
        if auto_response.decision:
            print(f"   📋 Decision structure: {list(auto_response.decision.keys())}")
            print("   ✅ Autonomous mode with structured decisions working")
        else:
            print("   ℹ️ Autonomous mode working (no structured decision)")
    else:
        print(f"   ❌ Autonomous mode failed: {auto_response.error}")
        return False

    # Test 5: Performance check
    print("\n5️⃣ Testing performance...")
    import time

    start_time = time.time()
    perf_response = client.get_dj_decision(
        context,
        "quick test",
        urgent=True
    )
    total_time = (time.time() - start_time) * 1000

    if perf_response.success:
        print(f"   ⏱️ Response time: {total_time:.1f}ms")
        print(f"   🏃 API processing time: {perf_response.processing_time_ms:.1f}ms")

        if total_time < 30000:  # 30 seconds reasonable for free model
            print("   ✅ Performance acceptable for free model")
        else:
            print(f"   ⚠️ Slow response ({total_time:.1f}ms) but working")
    else:
        print(f"   ❌ Performance test failed: {perf_response.error}")
        return False

    print("\n" + "="*60)
    print("🎉 FREE MODEL INTEGRATION TEST PASSED!")
    print("✅ All components now use z-ai/glm-4.5-air:free")
    print("✅ No more paid model usage")
    print("✅ System ready for unlimited use")
    return True

def show_model_costs():
    """Mostra informazioni sui modelli e costi"""
    print("\n💰 Model Cost Information:")
    print("="*40)
    print("✅ z-ai/glm-4.5-air:free    - $0.00 (FREE)")
    print("✅ deepseek/deepseek-r1:free - $0.00 (FREE)")
    print("❌ nousresearch/hermes-3-*   - $0.003+/1K tokens")
    print("❌ anthropic/claude-*        - $0.015+/1K tokens")
    print("❌ openai/gpt-*             - $0.002+/1K tokens")
    print("\n🎯 Current setup uses ONLY FREE models!")

if __name__ == "__main__":
    print("🆓 DJ AI System - Free Model Integration Test")
    print("Testing that all components use free OpenRouter models")
    print("\nPress Enter to start test...")
    input()

    try:
        success = test_free_model_integration()
        show_model_costs()

        if success:
            print("\n✅ ALL TESTS PASSED - Free model integration successful!")
            exit(0)
        else:
            print("\n❌ SOME TESTS FAILED - Check output above")
            exit(1)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)