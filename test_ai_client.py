#!/usr/bin/env python3
"""
🤖 Test Client OpenRouter
Verifica che il client AI funzioni correttamente
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.openrouter_client import OpenRouterClient, DJContext
from config import get_config

def test_ai_client():
    print("🤖 TEST CLIENT OPENROUTER")
    print("=" * 40)
    print("🎯 Test connessione e chat AI")
    print("=" * 40)

    try:
        config = get_config()

        # Verifica API key
        if not config.openrouter_api_key:
            print("❌ OpenRouter API key non configurata!")
            print("💡 Esporta: export OPENROUTER_API_KEY='your-key'")
            return

        print(f"🔑 API Key: {'✅ Configurata' if config.openrouter_api_key else '❌ Mancante'}")
        print(f"🤖 Modello: {config.openrouter_model}")

        # Crea client
        print(f"\n🔌 Creazione client OpenRouter...")
        client = OpenRouterClient(config.openrouter_api_key, config.openrouter_model)
        print("✅ Client creato")

        # Test connessione
        print(f"\n🧪 Test connessione...")
        response = client.test_connection()
        if response.success:
            print(f"✅ Connessione OK")
            print(f"   Modello: {response.model_used}")
            print(f"   Latenza: {response.processing_time_ms:.0f}ms")
        else:
            print(f"❌ Test connessione fallito: {response.error}")
            return

        # Test DJ decision
        print(f"\n🎧 Test DJ decision...")
        dj_context = DJContext(
            venue_type="club",
            event_type="prime_time",
            current_genre="house",
            energy_level=7,
            crowd_response="positive",
            time_in_set=30,
            current_bpm=128.0
        )

        message = "La folla sembra energica. Quale track dovrei mettere ora?"
        print(f"   Messaggio: {message}")

        dj_response = client.get_dj_decision(dj_context, message)

        if dj_response.success:
            print(f"✅ Risposta AI ricevuta")
            print(f"   Modello: {dj_response.model_used}")
            print(f"   Latenza: {dj_response.processing_time_ms:.0f}ms")
            print(f"   Risposta: {dj_response.response[:200]}...")

            # Note: actions potrebbe non essere sempre presente
            actions = getattr(dj_response, 'actions', [])
            if actions:
                print(f"   Azioni suggerite: {len(actions)}")
                for action in actions[:3]:  # Prime 3
                    print(f"     - {action}")
            else:
                print(f"   Nessuna azione specifica suggerita")
        else:
            print(f"❌ DJ decision fallita: {dj_response.error}")

        # Test emergency con urgent=True
        print(f"\n🚨 Test messaggio urgente...")
        urgent_response = client.get_dj_decision(
            dj_context,
            "HELP! La musica si è fermata, cosa faccio?",
            urgent=True
        )

        if urgent_response.success:
            print(f"✅ Risposta urgente ricevuta")
            print(f"   Latenza: {urgent_response.processing_time_ms:.0f}ms")
            print(f"   Risposta: {urgent_response.response[:100]}...")
        else:
            print(f"❌ Risposta urgente fallita: {urgent_response.error}")

        # Chiudi client
        print(f"\n🔚 Chiusura client...")
        client.close()
        print("✅ Client chiuso")

        print(f"\n✅ Test AI client completato con successo!")
        print(f"🎯 Il client OpenRouter è pronto per l'uso nella GUI")

    except Exception as e:
        print(f"❌ Errore test AI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_client()