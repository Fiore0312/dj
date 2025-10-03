#!/usr/bin/env python3
"""
🤖 Test Debug Chat AI - Diagnosi problemi chat
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from config import get_config
from core.openrouter_client import get_openrouter_client, DJContext

def test_chat_debug():
    print("🤖 DEBUG CHAT AI PROBLEM")
    print("=" * 50)

    try:
        config = get_config()

        print(f"🔑 API Key presente: {'✅ SÌ' if config.openrouter_api_key else '❌ NO'}")
        if config.openrouter_api_key:
            print(f"    Key preview: {config.openrouter_api_key[:20]}...")

        print(f"🤖 Modello configurato: {config.openrouter_model}")

        # Test diversi modelli per trovare quello funzionante
        models_to_test = [
            "nousresearch/hermes-3-llama-3.1-405b",
            "deepseek/deepseek-r1:free",
            "deepseek/deepseek-v3-base:free"
        ]

        working_model = None

        for model in models_to_test:
            print(f"\n🧪 Test modello: {model}")

            try:
                client = get_openrouter_client(config.openrouter_api_key, model)

                # Test connessione rapida
                response = client.test_connection()

                if response.success:
                    print(f"   ✅ FUNZIONA! Latenza: {response.processing_time_ms:.0f}ms")
                    working_model = model

                    # Test chat semplice
                    chat_response = client.get_dj_decision(
                        DJContext(),
                        "Ciao! Puoi rispondere a questo messaggio di test?",
                        urgent=True
                    )

                    if chat_response.success:
                        print(f"   💬 Chat OK: {chat_response.response[:50]}...")
                        break
                    else:
                        print(f"   ❌ Chat fallita: {chat_response.error}")

                else:
                    print(f"   ❌ Non funziona: {response.error}")

            except Exception as e:
                print(f"   ❌ Errore: {e}")

        if working_model:
            print(f"\n🎯 SOLUZIONE CHAT:")
            print(f"   Modello funzionante: {working_model}")
            print(f"   Comando: export OPENROUTER_MODEL='{working_model}'")

            # Test scenario DJ completo
            print(f"\n🎧 Test scenario DJ completo...")
            client = get_openrouter_client(config.openrouter_api_key, working_model)

            dj_context = DJContext(
                venue_type="club",
                event_type="peak_time",
                energy_level=7,
                current_bpm=128,
                crowd_response="energetic"
            )

            test_messages = [
                "La folla è molto energica, cosa dovrei fare?",
                "Dovrei aumentare il volume del deck A?",
                "Quale BPM mi consigli per mantenere l'energia?"
            ]

            for msg in test_messages:
                print(f"\n   Q: {msg}")
                resp = client.get_dj_decision(dj_context, msg)
                if resp.success:
                    print(f"   A: {resp.response[:100]}...")
                else:
                    print(f"   ❌: {resp.error}")

            client.close()

        else:
            print(f"\n❌ NESSUN MODELLO FUNZIONA")
            print(f"   Possibili cause:")
            print(f"   1. API Key non valida")
            print(f"   2. Tutti i modelli gratuiti rate-limited")
            print(f"   3. Problema connessione internet")

    except Exception as e:
        print(f"❌ Errore test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_debug()