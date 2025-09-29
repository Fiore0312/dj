#!/usr/bin/env python3
"""
🆓 Find True Free Models on OpenRouter
Script per trovare i modelli veramente gratuiti per DJ interattivo
"""

import requests
import json
import time
from typing import List, Dict, Any

def get_all_openrouter_models() -> List[Dict[str, Any]]:
    """Ottieni tutti i modelli disponibili da OpenRouter"""
    url = "https://openrouter.ai/api/v1/models"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        return []

def is_truly_free(model: Dict[str, Any]) -> bool:
    """Verifica se un modello è veramente gratuito"""
    pricing = model.get("pricing", {})

    # Controlla tutti i costi
    prompt_cost = float(pricing.get("prompt", "1"))
    completion_cost = float(pricing.get("completion", "1"))
    request_cost = float(pricing.get("request", "1"))

    # Modello gratuito se tutti i costi sono 0
    return prompt_cost == 0.0 and completion_cost == 0.0 and request_cost == 0.0

def analyze_model_for_dj(model: Dict[str, Any]) -> Dict[str, Any]:
    """Analizza un modello per uso DJ interattivo"""
    analysis = {
        "id": model.get("id"),
        "name": model.get("name"),
        "context_length": model.get("context_length", 0),
        "pricing": model.get("pricing", {}),
        "is_free": is_truly_free(model),
        "dj_suitability_score": 0,
        "features": [],
        "limitations": []
    }

    # Calcola punteggio idoneità DJ
    score = 0

    # Context length (importante per conversazioni)
    context_len = analysis["context_length"]
    if context_len >= 32000:
        score += 3
        analysis["features"].append("Long context (32K+)")
    elif context_len >= 8000:
        score += 2
        analysis["features"].append("Medium context (8K+)")
    elif context_len >= 4000:
        score += 1
        analysis["features"].append("Short context (4K+)")
    else:
        analysis["limitations"].append("Very short context (<4K)")

    # Verifica velocità (se nel nome ci sono indicatori)
    name_lower = model.get("name", "").lower()
    if any(fast_indicator in name_lower for fast_indicator in ["fast", "quick", "turbo", "instant"]):
        score += 2
        analysis["features"].append("Fast model")

    # Verifica se supporta istruzioni/chat
    if any(chat_indicator in name_lower for chat_indicator in ["chat", "instruct", "assistant"]):
        score += 2
        analysis["features"].append("Chat/instruction optimized")

    # Penalizza modelli sperimentali o beta
    if any(experimental in name_lower for experimental in ["beta", "alpha", "experimental", "preview"]):
        score -= 1
        analysis["limitations"].append("Experimental/beta model")

    # Bonus per modelli popolari/stabili
    if any(stable in name_lower for stable in ["stable", "production", "v1", "final"]):
        score += 1
        analysis["features"].append("Stable model")

    analysis["dj_suitability_score"] = max(0, score)
    return analysis

def find_best_free_models_for_dj():
    """Trova i migliori modelli gratuiti per DJ interattivo"""
    print("🔍 Searching for truly free models on OpenRouter...")
    print("="*60)

    # Ottieni tutti i modelli
    all_models = get_all_openrouter_models()
    print(f"📊 Found {len(all_models)} total models")

    # Filtra solo i gratuiti
    free_models = [model for model in all_models if is_truly_free(model)]
    print(f"🆓 Found {len(free_models)} truly free models")

    if not free_models:
        print("❌ No truly free models found!")
        return []

    # Analizza per uso DJ
    analyzed_models = []
    for model in free_models:
        analysis = analyze_model_for_dj(model)
        analyzed_models.append(analysis)

    # Ordina per punteggio idoneità DJ
    analyzed_models.sort(key=lambda x: x["dj_suitability_score"], reverse=True)

    # Mostra top 10
    print(f"\n🎯 TOP 10 FREE MODELS FOR DJ INTERACTIVE USE:")
    print("="*60)

    for i, model in enumerate(analyzed_models[:10], 1):
        print(f"\n{i}. {model['name']}")
        print(f"   ID: {model['id']}")
        print(f"   Context: {model['context_length']:,} tokens")
        print(f"   DJ Score: {model['dj_suitability_score']}/10")

        if model['features']:
            print(f"   ✅ Features: {', '.join(model['features'])}")

        if model['limitations']:
            print(f"   ⚠️ Limitations: {', '.join(model['limitations'])}")

        # Mostra pricing per conferma
        pricing = model['pricing']
        print(f"   💰 Pricing: prompt=${pricing.get('prompt', '0')}, completion=${pricing.get('completion', '0')}")

    # Raccomandazioni specifiche
    print(f"\n🎧 RECOMMENDATIONS FOR DJ INTERACTIVE USE:")
    print("="*50)

    if analyzed_models:
        top_model = analyzed_models[0]
        print(f"🥇 BEST CHOICE: {top_model['id']}")
        print(f"   Perfect for: Real-time DJ chat with good context")
        print(f"   Expected response time: 2-8 seconds")

        if len(analyzed_models) > 1:
            backup_model = analyzed_models[1]
            print(f"\n🥈 BACKUP CHOICE: {backup_model['id']}")
            print(f"   Use if primary model has issues")

    # Salva risultati completi
    with open("free_models_analysis.json", "w") as f:
        json.dump(analyzed_models, f, indent=2)
    print(f"\n💾 Full analysis saved to: free_models_analysis.json")

    return analyzed_models[:5]  # Return top 5

def test_model_speed(model_id: str, api_key: str) -> float:
    """Test velocità risposta di un modello"""
    print(f"\n⏱️ Testing speed for {model_id}...")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": "Say 'test' quickly"}
        ],
        "max_tokens": 10
    }

    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data, timeout=30)
        end_time = time.time()

        if response.status_code == 200:
            response_time = (end_time - start_time) * 1000
            print(f"   ✅ Response time: {response_time:.1f}ms")
            return response_time
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            return float('inf')

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return float('inf')

if __name__ == "__main__":
    print("🆓 OpenRouter Free Models Finder for DJ Interactive Use")
    print("Finding the fastest, most suitable free models...")
    print()

    # Trova modelli gratuiti
    best_models = find_best_free_models_for_dj()

    if best_models:
        print(f"\n🚀 RECOMMENDED CONFIGURATION:")
        print("="*40)
        print(f"PRIMARY_MODEL = '{best_models[0]['id']}'")
        if len(best_models) > 1:
            print(f"FALLBACK_MODEL = '{best_models[1]['id']}'")

        print(f"\n📝 Update your config.py with:")
        print(f"openrouter_model: str = \"{best_models[0]['id']}\"")
        if len(best_models) > 1:
            print(f"openrouter_fallback_model: str = \"{best_models[1]['id']}\"")
    else:
        print("❌ No suitable free models found!")

    print(f"\n✅ Analysis complete!")