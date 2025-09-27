#!/usr/bin/env python3
"""
🤖 OpenRouter Client - LLM Gratuito per DJ AI
Client semplificato per OpenRouter API con modelli gratuiti
"""

import requests
import json
import time
import logging
import threading
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import OPENROUTER_BASE_URL, OPENROUTER_HEADERS, FREE_MODELS

logger = logging.getLogger(__name__)

@dataclass
class DJContext:
    """Contesto DJ per l'AI"""
    venue_type: str = "club"
    event_type: str = "prime_time"
    current_genre: str = "house"
    energy_level: int = 5  # 1-10
    crowd_response: str = "neutral"
    time_in_set: int = 0  # minuti
    current_bpm: float = 128.0
    target_bpm: float = 128.0
    last_track: Optional[str] = None
    next_track_suggestion: Optional[str] = None

@dataclass
class AIResponse:
    """Risposta AI standardizzata"""
    success: bool
    response: str
    decision: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    model_used: str = ""
    error: Optional[str] = None

class OpenRouterClient:
    """Client OpenRouter per DJ AI decisions"""

    def __init__(self, api_key: str, default_model: str = "nousresearch/hermes-3-llama-3.1-405b"):
        """Inizializza client OpenRouter"""
        self.api_key = api_key
        self.default_model = default_model

        # Session requests per connessioni persistenti
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            **OPENROUTER_HEADERS
        })

        # Statistiche performance
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'model_usage': {},
            'start_time': time.time()
        }

        # Thread lock per thread safety
        self._lock = threading.Lock()

    def _make_request(self, messages: List[Dict], model: str = None, temperature: float = 0.7) -> AIResponse:
        """Effettua richiesta a OpenRouter (versione sync)"""
        start_time = time.perf_counter()
        model = model or self.default_model

        with self._lock:
            self.stats['total_requests'] += 1

        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 500,  # Limitato per risposte concise
                "stream": False
            }

            response = self.session.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                json=payload,
                timeout=30  # 30 secondi timeout
            )

            processing_time = (time.perf_counter() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']

                # Aggiorna statistiche
                with self._lock:
                    self.stats['successful_requests'] += 1
                    self.stats['model_usage'][model] = self.stats['model_usage'].get(model, 0) + 1

                # Prova a estrarre decisioni JSON se presenti
                decision = self._extract_decision(content)

                return AIResponse(
                    success=True,
                    response=content,
                    decision=decision,
                    confidence=0.8,  # Default confidence
                    processing_time_ms=processing_time,
                    model_used=model
                )
            else:
                with self._lock:
                    self.stats['failed_requests'] += 1

                return AIResponse(
                    success=False,
                    response="",
                    processing_time_ms=processing_time,
                    model_used=model,
                    error=f"HTTP {response.status_code}: {response.text}"
                )

        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            with self._lock:
                self.stats['failed_requests'] += 1

            logger.error(f"OpenRouter request failed: {e}")
            return AIResponse(
                success=False,
                response="",
                processing_time_ms=processing_time,
                model_used=model,
                error=str(e)
            )


    def _extract_decision(self, content: str) -> Optional[Dict[str, Any]]:
        """Estrae decisioni JSON dal testo se presenti"""
        try:
            # Cerca JSON nella risposta
            start = content.find('{')
            end = content.rfind('}') + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)

            return None
        except:
            return None

    def get_dj_decision(self, context: DJContext, query: str, urgent: bool = False) -> AIResponse:
        """Ottieni decisione DJ dall'AI"""

        # Costruisci prompt contestuale
        system_prompt = self._build_system_prompt(context)
        user_prompt = self._build_user_prompt(query, context, urgent)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Scegli modello in base all'urgenza
        model = self.default_model
        temperature = 0.3 if urgent else 0.7  # Più deterministico se urgente

        # Usa modello più veloce se urgente
        if urgent and "deepseek-r1" in self.default_model:
            model = "deepseek/deepseek-v3-base:free"  # Più veloce per urgenti

        return self._make_request(messages, model, temperature)

    def _build_system_prompt(self, context: DJContext) -> str:
        """Costruisci system prompt contestuale"""
        return f"""Sei un CONSULENTE DJ AI professionale che fornisce consigli tecnici a DJ umani in tempo reale.

🎧 TUO RUOLO: Sei un assistente/consulente che aiuta DJ umani con:
- Suggerimenti tecnici per mixing e transizioni
- Consigli su BPM, tonalità e combinazioni di tracce
- Strategie per gestire l'energia della folla
- Indicazioni su timing e progressione del set

❗ IMPORTANTE: Tu NON suoni, mixi o manipoli direttamente la musica. Fornisci solo consigli professionali che il DJ umano può implementare manualmente sui suoi strumenti (Traktor, mixer, controller).

CONTESTO SESSIONE ATTUALE:
- Venue: {context.venue_type}
- Tipo evento: {context.event_type}
- Genere dominante: {context.current_genre}
- Livello energia: {context.energy_level}/10
- Reazione crowd: {context.crowd_response}
- Tempo nel set: {context.time_in_set} minuti
- BPM attuale: {context.current_bpm}
- BPM target: {context.target_bpm}

🎯 LINEE GUIDA RISPOSTA:
1. Sii conciso e actionable (max 2-3 frasi)
2. Suggerisci tecniche DJ specifiche (beatmatching, EQ, effetti)
3. Considera l'evoluzione naturale del set e crowd response
4. Fornisci consigli su timing delle transizioni
5. Includi suggerimenti su BPM, key harmony, progressione energia

ESEMPI DI CONSIGLI VALIDI:
- "Aumenta gradualmente il BPM a 132 nei prossimi 2 mix per mantenere l'energia"
- "Usa un filter sweep e abbassa i bassi per 16 bar prima della transizione"
- "Questo è il momento perfetto per introdurre un breakdown progressive"
- "Considera un mix più lungo (64 bar) per lasciare che il crowd si connetti alla traccia"

Se richiesto specificamente, includi JSON con parametri tecnici precisi."""

    def _build_user_prompt(self, query: str, context: DJContext, urgent: bool) -> str:
        """Costruisci user prompt"""
        urgency = "URGENTE - " if urgent else ""

        prompt = f"{urgency}{query}"

        # Aggiungi contesto extra se necessario
        if context.last_track:
            prompt += f"\nTrack precedente: {context.last_track}"

        if context.next_track_suggestion:
            prompt += f"\nProssimo suggerimento: {context.next_track_suggestion}"

        return prompt

    def get_track_selection_advice(self, available_tracks: List[Dict], context: DJContext) -> AIResponse:
        """Ottieni consigli per selezione track"""

        # Limita a top 10 per non sovraccaricare
        tracks_summary = []
        for track in available_tracks[:10]:
            summary = f"'{track.get('title', 'Unknown')}' - {track.get('artist', 'Unknown')} ({track.get('genre', 'Unknown')}, {track.get('bpm', 'Unknown')} BPM)"
            tracks_summary.append(summary)

        query = f"""Suggerisci il miglior track per il prossimo mix:

TRACKS DISPONIBILI:
{chr(10).join(tracks_summary)}

Considera:
- Compatibilità BPM (corrente: {context.current_bpm})
- Progressione energia (attuale: {context.energy_level}/10)
- Armonia di genere (attuale: {context.current_genre})
- Momento del set ({context.time_in_set} min, {context.event_type})

Rispondi con raccomandazione e motivazione."""

        return self.get_dj_decision(context, query)

    def get_mixing_advice(self, situation: str, context: DJContext) -> AIResponse:
        """Ottieni consigli di mixing per situazione specifica"""
        query = f"Situazione: {situation}. Che azione di mixing consigli?"
        return self.get_dj_decision(context, query, urgent=True)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Ottieni statistiche performance"""
        uptime = time.time() - self.stats['start_time']

        success_rate = (self.stats['successful_requests'] / max(self.stats['total_requests'], 1)) * 100

        avg_response_time = (
            sum(self.stats.get('response_times', [])) /
            max(len(self.stats.get('response_times', [])), 1)
        )

        return {
            'uptime_seconds': round(uptime, 1),
            'total_requests': self.stats['total_requests'],
            'success_rate': round(success_rate, 1),
            'average_response_time_ms': round(avg_response_time, 1),
            'model_usage': self.stats['model_usage'].copy(),
            'failed_requests': self.stats['failed_requests']
        }

    def test_connection(self) -> AIResponse:
        """Testa connessione OpenRouter"""
        test_context = DJContext()
        return self.get_dj_decision(test_context, "Test connessione - rispondi solo 'Connesso e pronto!'")

    def close(self):
        """Chiudi sessione HTTP"""
        if self.session:
            self.session.close()

# Factory function per compatibilità
def get_openrouter_client(api_key: str, model: str = None) -> OpenRouterClient:
    """Ottieni client OpenRouter configurato"""
    if model is None:
        model = FREE_MODELS["hermes"]["name"]

    return OpenRouterClient(api_key, model)

# Test function
def test_openrouter():
    """Test OpenRouter connection"""
    import os

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY non impostata")
        return

    client = get_openrouter_client(api_key)

    print("🧪 Test connessione OpenRouter...")

    # Test basic connection
    response = client.test_connection()

    if response.success:
        print(f"✅ Connessione OK: {response.response}")
        print(f"⏱️ Tempo risposta: {response.processing_time_ms:.0f}ms")
        print(f"🤖 Modello: {response.model_used}")
    else:
        print(f"❌ Connessione fallita: {response.error}")

    # Test DJ decision
    context = DJContext(
        venue_type="club",
        event_type="prime_time",
        energy_level=7,
        current_bpm=128
    )

    response = client.get_dj_decision(context, "Il crowd sta ballando bene, come procedo?")

    if response.success:
        print(f"\n🎛️ Consiglio DJ: {response.response}")
        if response.decision:
            print(f"📋 Decisione: {response.decision}")
    else:
        print(f"\n❌ Errore consiglio DJ: {response.error}")

    # Stats
    stats = client.get_performance_stats()
    print(f"\n📊 Stats: {stats}")

    client.close()

if __name__ == "__main__":
    test_openrouter()