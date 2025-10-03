# 🆓 OpenRouter Setup - Modelli LLM Gratuiti

## TL;DR - Quick Start

**NON serve API key Anthropic!** Il sistema può usare OpenRouter con modelli **completamente gratuiti**.

```bash
# Attiva environment
source dj_env/bin/activate

# Avvia agente ibrido (auto-detect backend)
python autonomous_dj_hybrid.py
```

Il sistema **rileva automaticamente** quale backend usare:
- ✅ Se hai `ANTHROPIC_API_KEY` → Usa Claude SDK (premium)
- ✅ Se NON hai key Anthropic → Usa OpenRouter (FREE)

## 🎯 Opzioni Disponibili

### Opzione 1: OpenRouter GRATUITO (Raccomandato per iniziare)

**Vantaggi:**
- ✅ Completamente GRATIS
- ✅ Nessuna carta di credito richiesta
- ✅ Modelli: GLM-4.5-Air, DeepSeek-R1, Llama 3.3
- ✅ Hardcoded fallback (funziona senza API key!)

**Come usare:**
```bash
# Il sistema ha già una API key OpenRouter hardcoded
# Funziona out-of-the-box!
python autonomous_dj_hybrid.py
```

**Opzionale: Usa la TUA OpenRouter key**
```bash
# Se vuoi usare la tua key (rate limits migliori)
export OPENROUTER_API_KEY="sk-or-v1-your-key"
python autonomous_dj_hybrid.py
```

Ottieni key gratis su: https://openrouter.ai/keys

### Opzione 2: Claude Agent SDK (Premium)

**Vantaggi:**
- ✅ Claude Sonnet 4 (miglior qualità)
- ✅ Native tool calling
- ✅ Reasoning avanzato

**Svantaggi:**
- ❌ A pagamento (~$1-2 per sessione)
- ❌ Richiede Anthropic API key

**Come usare:**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key"
python autonomous_dj_hybrid.py
```

Ottieni key su: https://console.anthropic.com/

## 🚀 Avvio Rapido - OpenRouter FREE

### Step 1: Verifica Installazione
```bash
source dj_env/bin/activate
python -c "import claude_agent_sdk; print('SDK OK')"
```

### Step 2: Avvia Agente Ibrido
```bash
python autonomous_dj_hybrid.py
```

### Step 3: Configura Sessione
```
🔍 Backend Detection:
  Claude SDK: ❌
  OpenRouter: ✅

  Selected: OPENROUTER

🚀 Using OpenRouter (FREE models)

Venue type (club/bar/festival) [club]: club
Event type (warm_up/prime_time/closing) [prime_time]: prime_time
```

### Step 4: Dai Comandi
```
DJ Command> Play a house track to start the set

🤖 I'll search for a house track and load it to Deck A.
{"action": "search_library", "genre": "house"}

🎵 Found 45 track(s):
1. 'Deep Vibes' - DJ X (125 BPM)
2. 'Night Drive' - Artist Y (128 BPM)
...
```

## 📊 Confronto Backend

| Feature | OpenRouter FREE | Claude SDK (Anthropic) |
|---------|----------------|----------------------|
| **Costo** | Gratis | ~$1-2 per sessione |
| **Setup** | Zero config | Richiede API key |
| **Modelli** | GLM-4.5, DeepSeek-R1 | Claude Sonnet 4 |
| **Tool Calling** | JSON parsing | Native @tool |
| **Qualità** | Buona | Eccellente |
| **Rate Limits** | Condivisi (free tier) | Personali |
| **Latency** | ~2-4s | ~1-2s |

## 🔧 Modelli OpenRouter Gratuiti

### Configurazione Attuale (in `core/openrouter_client.py`)

**Modello Primario:**
```python
"llama_fast": {
    "name": "meta-llama/llama-3.3-8b-instruct:free",
    "description": "Llama 3.3 8B - Fast, free"
}
```

**Modello Fallback:**
```python
"glm_free": {
    "name": "z-ai/glm-4.5-air:free",
    "description": "GLM-4.5-Air - Completely free"
}

"deepseek_free": {
    "name": "deepseek/deepseek-r1:free",
    "description": "DeepSeek-R1 - Free reasoning model"
}
```

## 🎛️ Come Funziona (Tecnicamente)

### OpenRouter Backend

1. **Detection**: Sistema rileva assenza di `ANTHROPIC_API_KEY`
2. **Fallback**: Usa `OpenRouterClient` da `core/openrouter_client.py`
3. **Parsing**: Estrae azioni JSON dalle risposte LLM
4. **Execution**: Esegue tool functions (load_track, play_deck, etc.)

### System Prompt OpenRouter

```python
"""You are a PROFESSIONAL DJ AI controlling Traktor Pro.

AVAILABLE ACTIONS (respond with JSON):
- {"action": "load_track", "deck": "A"}
- {"action": "play_deck", "deck": "A"}
- {"action": "professional_mix", "from_deck": "A", "to_deck": "B"}

RESPOND FORMAT:
1. Brief explanation
2. JSON command on separate line
"""
```

### Example Flow

```
User: "Start with a house track"
  ↓
OpenRouter LLM: "I'll search for house tracks and load one.
                 {"action": "search_library", "genre": "house"}"
  ↓
Agent: Extract JSON → Execute tool_search_music_library()
  ↓
Result: "🎵 Found 45 tracks..."
```

## 📝 Esempi Pratici

### Esempio 1: Start Set
```bash
DJ Command> Start the set with a warm-up house track around 120 BPM

🤖 I'll search for a house track at 120 BPM and load it to Deck A.
{"action": "search_library", "genre": "house", "min_bpm": 118, "max_bpm": 122}

🎵 Found 23 track(s):
1. 'Chill Vibes' - DJ Cool (120 BPM)
...

{"action": "load_track", "deck": "A"}
✅ Track loaded successfully to Deck A

{"action": "play_deck", "deck": "A"}
▶️ Deck A is now playing
```

### Esempio 2: Professional Mix
```bash
DJ Command> Mix to deck B with a smooth 45 second transition

🤖 I'll execute a professional crossfade from Deck A to Deck B over 45 seconds.
{"action": "professional_mix", "from_deck": "A", "to_deck": "B", "duration": 45}

🎚️ Starting professional mix: Deck A → Deck B
✓ Deck B synced
✓ Deck B playing
✓ Crossfade completed over 45s
✓ Deck A stopped
✅ Professional mix transition completed!
```

## 🔍 Troubleshooting

### Issue: "Backend Detection shows both ❌"
```bash
# Installa dipendenze
source dj_env/bin/activate
pip install claude-agent-sdk

# Sistema userà hardcoded OpenRouter fallback
```

### Issue: "OpenRouter rate limit"
Se usi la key condivisa hardcoded, potresti incontrare rate limits. Soluzione:

```bash
# Ottieni TUA key OpenRouter (gratis)
# 1. Vai su: https://openrouter.ai/keys
# 2. Crea account (gratis, no CC)
# 3. Genera API key

# 4. Imposta key
export OPENROUTER_API_KEY="sk-or-v1-your-key"

# 5. Riavvia
python autonomous_dj_hybrid.py
```

### Issue: "Slow response times"
OpenRouter free tier può essere più lento nei picchi. Soluzioni:

1. **Usa model più veloce**: Modifica in `config.py`
2. **Ottieni API key personale**: Rate limits migliori
3. **Upgrade a Claude SDK**: Se hai budget (~$10/mese)

## 🆚 Quando Usare Cosa?

### Usa OpenRouter FREE se:
- ✅ Stai testando il sistema
- ✅ Budget limitato o zero
- ✅ Learning/development
- ✅ Set occasionali (<1h/giorno)

### Usa Claude SDK (Anthropic) se:
- ✅ Sessioni professionali
- ✅ Serve massima qualità
- ✅ Hai budget (~$1-2/sessione)
- ✅ Uso intensivo (>2h/giorno)

## 📚 Risorse

### OpenRouter
- Dashboard: https://openrouter.ai/
- Docs: https://openrouter.ai/docs
- Models: https://openrouter.ai/models
- Pricing: https://openrouter.ai/docs/pricing

### Anthropic (Claude)
- Console: https://console.anthropic.com/
- Docs: https://docs.anthropic.com/
- Pricing: https://www.anthropic.com/pricing

## 🎉 Quick Commands Cheat Sheet

```bash
# Setup
source dj_env/bin/activate

# Run with auto-detection
python autonomous_dj_hybrid.py

# Force OpenRouter (no Anthropic key)
unset ANTHROPIC_API_KEY
python autonomous_dj_hybrid.py

# Use custom OpenRouter key
export OPENROUTER_API_KEY="sk-or-v1-..."
python autonomous_dj_hybrid.py

# Test connection
python -c "from core.openrouter_client import get_openrouter_client; client = get_openrouter_client(None); print(client.test_connection())"
```

## ✨ Conclusione

**NON hai bisogno di pagare nulla!** Il sistema funziona perfettamente con OpenRouter e modelli gratuiti.

Per iniziare:
```bash
source dj_env/bin/activate
python autonomous_dj_hybrid.py
```

Enjoy your FREE autonomous DJ! 🎵🎛️🆓
