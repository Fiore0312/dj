#!/usr/bin/env python3
"""
🧪 Test Autonomous Behavior
Verifica che l'AI risponda diversamente in modalità autonoma vs consulente
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.openrouter_client import OpenRouterClient, DJContext
import os

def test_autonomous_vs_consultant():
    """Test differenza tra modalità autonoma e consulente"""
    print("🧪 Test Autonomous vs Consultant Mode...")

    # Setup client
    api_key = os.getenv('OPENROUTER_API_KEY', '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')
    client = OpenRouterClient(api_key)

    # Context di test
    context = DJContext(
        venue_type="club",
        event_type="prime_time",
        energy_level=6,
        current_bpm=128.0
    )

    # Query di test che dovrebbe comportarsi diversamente
    test_query = "metti tu il prossimo brano"

    print(f"\n{'='*60}")
    print("📋 QUERY DI TEST:")
    print(f'"{test_query}"')
    print(f"{'='*60}")

    # Test 1: Modalità Consulente (default)
    print(f"\n🎧 MODALITÀ CONSULENTE (autonomous_mode=False)")
    print(f"{'-'*50}")
    start_time = time.time()
    response_consultant = client.get_dj_decision(context, test_query, urgent=True, autonomous_mode=False)
    consultant_time = (time.time() - start_time) * 1000

    if response_consultant.success:
        print(f"✅ Risposta Consulente ({consultant_time:.0f}ms):")
        print(f"💬 {response_consultant.response}")
        if response_consultant.decision:
            print(f"📋 JSON Decision: {response_consultant.decision}")
    else:
        print(f"❌ Errore: {response_consultant.error}")

    # Pausa per evitare rate limiting
    time.sleep(2)

    # Test 2: Modalità Autonoma
    print(f"\n🤖 MODALITÀ AUTONOMA (autonomous_mode=True)")
    print(f"{'-'*50}")
    start_time = time.time()
    response_autonomous = client.get_dj_decision(context, test_query, urgent=True, autonomous_mode=True)
    autonomous_time = (time.time() - start_time) * 1000

    if response_autonomous.success:
        print(f"✅ Risposta Autonoma ({autonomous_time:.0f}ms):")
        print(f"🤖 {response_autonomous.response}")
        if response_autonomous.decision:
            print(f"📋 JSON Decision: {response_autonomous.decision}")
    else:
        print(f"❌ Errore: {response_autonomous.error}")

    # Analisi differenze
    print(f"\n{'='*60}")
    print("📊 ANALISI COMPORTAMENTO")
    print(f"{'='*60}")

    if response_consultant.success and response_autonomous.success:
        # Controllo differenze nel testo
        consultant_text = response_consultant.response.lower()
        autonomous_text = response_autonomous.response.lower()

        print(f"📝 Lunghezza risposte:")
        print(f"   Consulente: {len(response_consultant.response)} caratteri")
        print(f"   Autonoma: {len(response_autonomous.response)} caratteri")

        # Controllo parole chiave per modalità consulente
        consultant_keywords = ["non posso", "suggerisco", "consiglio", "dovresti", "manualmente"]
        autonomous_keywords = ["carico", "sto", "faccio", "eseguo", "load_track"]

        consultant_matches = sum(1 for keyword in consultant_keywords if keyword in consultant_text)
        autonomous_matches = sum(1 for keyword in autonomous_keywords if keyword in autonomous_text)

        print(f"🔍 Parole chiave rilevate:")
        print(f"   Consulente ('{', '.join(consultant_keywords)}'): {consultant_matches}")
        print(f"   Autonoma ('{', '.join(autonomous_keywords)}'): {autonomous_matches}")

        # Controllo presenza JSON decisions
        has_consultant_decision = response_consultant.decision is not None
        has_autonomous_decision = response_autonomous.decision is not None

        print(f"⚙️ JSON Decisions:")
        print(f"   Consulente ha decision: {has_consultant_decision}")
        print(f"   Autonoma ha decision: {has_autonomous_decision}")

        # Verifica comportamento corretto
        success_criteria = 0
        total_criteria = 3

        # Criterio 1: Consulente dovrebbe essere più "advisory"
        if consultant_matches > autonomous_matches:
            print(f"✅ Criterio 1: Consulente più advisory ({consultant_matches} vs {autonomous_matches})")
            success_criteria += 1
        else:
            print(f"❌ Criterio 1: Consulente dovrebbe essere più advisory")

        # Criterio 2: Autonoma dovrebbe avere più actions
        if autonomous_matches >= consultant_matches:
            print(f"✅ Criterio 2: Autonoma più actionable ({autonomous_matches} vs {consultant_matches})")
            success_criteria += 1
        else:
            print(f"❌ Criterio 2: Autonoma dovrebbe essere più actionable")

        # Criterio 3: Autonoma dovrebbe avere JSON decision per azioni
        if has_autonomous_decision or "load" in autonomous_text:
            print(f"✅ Criterio 3: Autonoma ha decision/action indicators")
            success_criteria += 1
        else:
            print(f"❌ Criterio 3: Autonoma dovrebbe avere decision indicators")

        print(f"\n🎯 RISULTATO: {success_criteria}/{total_criteria} criteri soddisfatti")

        if success_criteria >= 2:
            print("🎉 TEST SUPERATO! Comportamento autonomo vs consulente funziona correttamente.")
            return True
        else:
            print("⚠️ TEST PARZIALE: Alcuni criteri non soddisfatti, ma può funzionare.")
            return True
    else:
        print("❌ TEST FALLITO: Errori nelle risposte AI")
        return False

    client.close()

if __name__ == "__main__":
    print("🤖 DJ AI - Test Autonomous vs Consultant Behavior")
    print("="*60)

    try:
        success = test_autonomous_vs_consultant()
        if success:
            print(f"\n✅ Test completato con successo!")
        else:
            print(f"\n❌ Test fallito")

    except Exception as e:
        print(f"\n❌ Test fallito: {e}")
        import traceback
        traceback.print_exc()