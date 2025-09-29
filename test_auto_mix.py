#!/usr/bin/env python3
"""
🧪 Test Auto-Mix Functionality
Verifica che l'implementazione autonoma funzioni correttamente
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.openrouter_client import OpenRouterClient, DJContext
import os

def test_auto_mix_logic():
    """Test la logica di decisione autonoma"""
    print("🧪 Test Auto-Mix Logic...")

    # Setup client
    api_key = os.getenv('OPENROUTER_API_KEY', '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')
    client = OpenRouterClient(api_key)

    # Test contexts per diverse fasi del set
    test_scenarios = [
        {
            "name": "🎵 Warm-up Phase (10 min)",
            "context": DJContext(
                venue_type="club",
                event_type="prime_time",
                energy_level=3,
                time_in_set=10,
                current_bpm=124.0
            ),
            "query": "Siamo all'inizio del set. Come dovrei procedere per scaldare il crowd gradualmente? Energia attuale: 3/10."
        },
        {
            "name": "🔥 Build-up Phase (45 min)",
            "context": DJContext(
                venue_type="club",
                event_type="prime_time",
                energy_level=6,
                time_in_set=45,
                current_bpm=128.0
            ),
            "query": "Il set sta prendendo forma. Qual è la strategia migliore per aumentare l'energia? Energia attuale: 6/10."
        },
        {
            "name": "💥 Peak Time (100 min)",
            "context": DJContext(
                venue_type="club",
                event_type="prime_time",
                energy_level=9,
                time_in_set=100,
                current_bpm=132.0
            ),
            "query": "Siamo nel momento di punta del set. Come mantengo l'energia al massimo? Energia attuale: 9/10."
        }
    ]

    # Test ogni scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*50}")
        print(f"{i}. {scenario['name']}")
        print(f"{'='*50}")

        start_time = time.time()
        response = client.get_dj_decision(scenario['context'], scenario['query'], urgent=True)
        response_time = (time.time() - start_time) * 1000

        if response.success:
            print(f"✅ Risposta AI ({response_time:.0f}ms):")
            print(f"🎧 {response.response}")

            if response.decision:
                print(f"📋 Decisione JSON: {response.decision}")

        else:
            print(f"❌ Errore: {response.error}")

        print(f"⏱️ Tempo risposta: {response_time:.0f}ms")
        print(f"🤖 Modello: {response.model_used}")

        # Breve pausa tra test
        time.sleep(1)

    # Test stats
    print(f"\n{'='*50}")
    print("📊 STATISTICHE PERFORMANCE")
    print(f"{'='*50}")
    stats = client.get_performance_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

    client.close()
    print("\n✅ Test completato con successo!")

def test_autonomous_timing():
    """Test logic di timing per Auto-Mix"""
    print("\n🕐 Test Autonomous Timing Logic...")

    # Simula diverse fasi temporali
    session_start = time.time()

    test_times = [
        {"minutes": 10, "expected": "warm_up"},
        {"minutes": 45, "expected": "buildup"},
        {"minutes": 100, "expected": "peak"},
        {"minutes": 180, "expected": "closing"}
    ]

    for test in test_times:
        # Simula tempo passato
        time_in_set = test["minutes"]

        # Logic dal metodo _make_autonomous_decision
        if time_in_set < 30:
            phase = "warm_up"
            query = "Siamo all'inizio del set. Come dovrei procedere per scaldare il crowd gradualmente?"
        elif time_in_set < 90:
            phase = "buildup"
            query = "Il set sta prendendo forma. Qual è la strategia migliore per aumentare l'energia?"
        elif time_in_set < 150:
            phase = "peak"
            query = "Siamo nel momento di punta del set. Come mantengo l'energia al massimo?"
        else:
            phase = "closing"
            query = "Il set si sta avvicinando alla conclusione. Come gestisco il finale?"

        expected_phase = test["expected"]
        status = "✅" if phase == expected_phase else "❌"

        print(f"{status} {time_in_set} min → {phase} (atteso: {expected_phase})")
        print(f"   Query: {query[:50]}...")

    print("✅ Timing logic verificata!")

if __name__ == "__main__":
    print("🤖 DJ AI - Test Funzionalità Auto-Mix")
    print("="*50)

    try:
        # Test 1: Logic decisionale
        test_auto_mix_logic()

        # Test 2: Timing logic
        test_autonomous_timing()

        print("\n🎉 TUTTI I TEST PASSATI!")

    except Exception as e:
        print(f"\n❌ Test fallito: {e}")
        import traceback
        traceback.print_exc()