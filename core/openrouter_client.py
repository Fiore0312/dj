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
import time
from threading import Lock
from collections import deque
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from .config import OPENROUTER_BASE_URL, OPENROUTER_HEADERS, FREE_MODELS

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

    def __init__(self, api_key: str, default_model: str = "meta-llama/llama-3.3-8b-instruct:free"):
        """Inizializza client OpenRouter"""
        self.api_key = api_key
        self.default_model = default_model

        # Session requests per connessioni persistenti con pool limitato
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

        # Rate limiting (max 2 requests per second)
        self._request_times = deque()
        self._rate_limit_lock = Lock()
        self.max_requests_per_second = 2

    def _make_request(self, messages: List[Dict], model: str = None, temperature: float = 0.7, autonomous_mode: bool = False) -> AIResponse:
        """Effettua richiesta a OpenRouter (versione sync)"""
        start_time = time.perf_counter()
        model = model or self.default_model

        # Rate limiting check
        self._enforce_rate_limit()

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
                decision = self._extract_decision(content, autonomous_mode)

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


    def _extract_decision(self, content: str, autonomous_mode: bool = False) -> Optional[Dict[str, Any]]:
        """Estrae decisioni JSON dal testo se presenti"""
        try:
            # Cerca JSON nella risposta
            start = content.find('{')
            end = content.rfind('}') + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)

            # Se è modalità autonoma e non c'è JSON, prova a inferire l'azione
            if autonomous_mode:
                content_lower = content.lower()
                decision = {}

                # Caricamento tracce
                if "caric" in content_lower and "deck a" in content_lower:
                    decision["load_track"] = "A"
                elif "caric" in content_lower and "deck b" in content_lower:
                    decision["load_track"] = "B"

                # Play commands - check multiple phrases for play
                play_keywords = ["play", "parti", "avvia", "suona", "faccio partire", "fai partire", "fa partire"]
                has_play_command = any(word in content_lower for word in play_keywords)

                if has_play_command:
                    if "deck a" in content_lower:
                        decision["play_deck"] = "A"
                    elif "deck b" in content_lower:
                        decision["play_deck"] = "B"
                    elif "traccia" in content_lower or "brano" in content_lower:
                        decision["play_track"] = True

                # MIXING COMMANDS - Nuova logica per mixing tra deck
                mixing_keywords = ["mixa", "mix", "transiz", "passa", "cambia", "switch", "crossfade"]
                has_mixing_command = any(word in content_lower for word in mixing_keywords)

                if has_mixing_command:
                    # Detect specific mixing scenarios
                    if ("deck b" in content_lower and "deck a" in content_lower) or ("deck a" in content_lower and "deck b" in content_lower):
                        decision["mixing_mode"] = "A_to_B"
                        decision["crossfader_target"] = 127  # Move to B side
                    elif "deck b" in content_lower and ("passa" in content_lower or "switch" in content_lower or "mixa" in content_lower):
                        decision["mixing_mode"] = "A_to_B"
                        decision["crossfader_target"] = 127  # Move to B side
                    elif "deck a" in content_lower and ("passa" in content_lower or "switch" in content_lower or "mixa" in content_lower):
                        decision["mixing_mode"] = "B_to_A"
                        decision["crossfader_target"] = 0    # Move to A side
                    else:
                        # Generic mixing - default to center
                        decision["crossfader_move"] = 64

                # COMPLEX WORKFLOW DETECTION - "carica deck B e mixa"
                if ("caric" in content_lower and "deck b" in content_lower and has_mixing_command):
                    decision["complex_workflow"] = "load_B_and_mix"
                    decision["load_track"] = "B"
                    decision["mixing_mode"] = "A_to_B"
                    decision["crossfader_target"] = 127
                elif ("caric" in content_lower and "deck a" in content_lower and has_mixing_command):
                    decision["complex_workflow"] = "load_A_and_mix"
                    decision["load_track"] = "A"
                    decision["mixing_mode"] = "B_to_A"
                    decision["crossfader_target"] = 0

                # VOLUME CONTROLS per mixing
                if "alza volume" in content_lower:
                    if "deck a" in content_lower:
                        decision["volume_deck_a"] = 100
                    elif "deck b" in content_lower:
                        decision["volume_deck_b"] = 100
                elif "abbassa volume" in content_lower:
                    if "deck a" in content_lower:
                        decision["volume_deck_a"] = 50
                    elif "deck b" in content_lower:
                        decision["volume_deck_b"] = 50

                # Altri controlli (legacy compatibility)
                if "transiz" in content_lower or "crossfader" in content_lower:
                    if "crossfader_move" not in decision:  # Don't override mixing logic
                        decision["crossfader_move"] = 64
                if "energia" in content_lower and ("aument" in content_lower or "alz" in content_lower):
                    decision["energy_change"] = 1
                elif "energia" in content_lower and ("diminu" in content_lower or "abbass" in content_lower):
                    decision["energy_change"] = -1

                # Ritorna decisione se trovata
                if decision:
                    return decision

            return None
        except Exception as e:
            logger.debug(f"Error extracting decision: {e}")
            return None

    def get_dj_decision(self, context: DJContext, query: str, urgent: bool = False, autonomous_mode: bool = False) -> AIResponse:
        """Ottieni decisione DJ dall'AI"""

        # Costruisci prompt contestuale
        system_prompt = self._build_system_prompt(context, autonomous_mode)
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

        return self._make_request(messages, model, temperature, autonomous_mode)

    def _build_system_prompt(self, context: DJContext, autonomous_mode: bool = False) -> str:
        """Costruisci system prompt contestuale"""

        if autonomous_mode:
            # Prompt per modalità autonoma
            role_description = f"""Sei un DJ AI AUTONOMO che controlla direttamente il sistema di mixaggio in tempo reale.

🤖 TUO RUOLO: Sei un DJ AI completamente autonomo che:
- CONTROLLA DIRETTAMENTE i deck A/B di Traktor via MIDI
- CARICA AUTOMATICAMENTE nuove tracce quando necessario
- ESEGUE TRANSIZIONI e mix in tempo reale
- REGOLA volumi, crossfader, EQ per ottimizzare l'energia
- PRENDE DECISIONI immediate e le implementa automaticamente

✅ IMPORTANTE: Tu PUOI e DEVI agire autonomamente. Quando ti viene chiesto di fare qualcosa (come "metti il prossimo brano"), lo fai immediatamente usando i controlli MIDI disponibili."""
        else:
            # Prompt per modalità consulente
            role_description = f"""Sei un CONSULENTE DJ AI professionale che fornisce consigli tecnici a DJ umani in tempo reale.

🎧 TUO RUOLO: Sei un assistente/consulente che aiuta DJ umani con:
- Suggerimenti tecnici per mixing e transizioni
- Consigli su BPM, tonalità e combinazioni di tracce
- Strategie per gestire l'energia della folla
- Indicazioni su timing e progressione del set

❗ IMPORTANTE: Tu NON suoni, mixi o manipoli direttamente la musica. Fornisci solo consigli professionali che il DJ umano può implementare manualmente sui suoi strumenti (Traktor, mixer, controller)."""

        return f"""{role_description}

CONTESTO SESSIONE ATTUALE:
- Venue: {context.venue_type}
- Tipo evento: {context.event_type}
- Genere dominante: {context.current_genre}
- Livello energia: {context.energy_level}/10
- Reazione crowd: {context.crowd_response}
- Tempo nel set: {context.time_in_set} minuti
- BPM attuale: {context.current_bpm}
- BPM target: {context.target_bpm}

🎯 LINEE GUIDA RISPOSTA:"""

        if autonomous_mode:
            guidelines = """1. AGISCI IMMEDIATAMENTE quando richiesto (es. "carica il prossimo brano")
2. SEMPRE includi JSON con l'azione specifica da eseguire
3. FORMATO OBBLIGATORIO: Testo descrittivo + JSON su linea separata
4. Considera timing ottimale per transizioni e cambi traccia
5. Mantieni l'energia e flow del set

⚡ IMPORTANTE: OGNI risposta autonoma DEVE includere JSON con l'azione!

AZIONI AUTONOME DISPONIBILI:
- {"load_track": "A"} - Carica prossima traccia nel deck A
- {"load_track": "B"} - Carica prossima traccia nel deck B
- {"crossfader_move": 64} - Muovi crossfader (0-127)
- {"eq_adjustment": {"deck": "A", "type": "mid", "value": 0.8}}

ESEMPI CORRETTI (OBBLIGATORIO QUESTO FORMATO):
Query: "carica prossimo brano nel deck A"
Risposta: "Carico immediatamente la prossima traccia nel Deck A.
{"load_track": "A"}"

Query: "fai la transizione"
Risposta: "Eseguo transizione con crossfader.
{"crossfader_move": 32}"

❌ NON DIMENTICARE MAI IL JSON! Senza JSON l'azione non viene eseguita!"""
        else:
            guidelines = """1. Sii conciso e actionable (max 2-3 frasi)
2. Suggerisci tecniche DJ specifiche (beatmatching, EQ, effetti)
3. Considera l'evoluzione naturale del set e crowd response
4. Fornisci consigli su timing delle transizioni
5. Includi suggerimenti su BPM, key harmony, progressione energia

ESEMPI DI CONSIGLI VALIDI:
- "Aumenta gradualmente il BPM a 132 nei prossimi 2 mix per mantenere l'energia"
- "Usa un filter sweep e abbassa i bassi per 16 bar prima della transizione"
- "Questo è il momento perfetto per introdurre un breakdown progressive"
- "Considera un mix più lungo (64 bar) per lasciare che il crowd si connetti alla traccia\""""

        return f"""{role_description}

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
{guidelines}

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

    def _enforce_rate_limit(self):
        """Enforce rate limiting to prevent connection pool overflow"""
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

    def __del__(self):
        """Cleanup session when object is destroyed"""
        self.close_session()

    def close_session(self):
        """Chiudi sessione HTTP"""
        if hasattr(self, 'session') and self.session:
            self.session.close()

    def close(self):
        """Chiudi sessione HTTP"""
        self.close_session()

# Factory function per compatibilità
def get_openrouter_client(api_key: str, model: str = None) -> OpenRouterClient:
    """Ottieni client OpenRouter configurato"""
    # HOTFIX: Hardcode API key corretta per evitare problemi di configurazione
    HARDCODED_API_KEY = "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"

    if not api_key:
        # Prova a ottenere dalla variabile ambiente
        import os
        api_key = os.getenv('OPENROUTER_API_KEY')

    # Se ancora non c'è, usa l'hardcoded
    if not api_key:
        api_key = HARDCODED_API_KEY
        print(f"🔄 HOTFIX: Usando API key hardcoded: {api_key[:20]}...{api_key[-10:]}")

    if not api_key:
        raise ValueError("❌ OpenRouter API key non disponibile. Impostala con: export OPENROUTER_API_KEY='your-key'")

    if model is None:
        # Usa il modello veloce ottimale per DJ
        model = FREE_MODELS["llama_fast"]["name"]

    return OpenRouterClient(api_key, model)

# Test function
def test_openrouter():
    """Test OpenRouter connection"""
    try:
        from config import get_config
        config = get_config()
        api_key = config.openrouter_api_key
    except:
        import os
        api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key:
        print("❌ OPENROUTER_API_KEY non disponibile")
        print("   Assicurati di:")
        print("   1. Aver creato il file .env con: python3 setup_secure.py")
        print("   2. O impostato: export OPENROUTER_API_KEY='your-key'")
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