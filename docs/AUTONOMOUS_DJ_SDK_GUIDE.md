# 🤖 Autonomous DJ Agent - Claude Agent SDK Edition

## Overview

Il sistema **Autonomous DJ Agent** è un DJ completamente autonomo che utilizza Claude Agent SDK per controllare Traktor Pro via MIDI. Il sistema combina intelligenza artificiale con controllo professionale del DJ hardware, permettendo sia operazioni autonome che interazioni conversazionali in tempo reale.

## 🌟 Caratteristiche Principali

### 1. **Claude Agent SDK Integration**
- Utilizza l'ultimo Claude Agent SDK (v0.1.0) con Sonnet 4
- Custom tools per controllo completo di Traktor
- System prompt ottimizzato per comportamento DJ professionale
- Streaming responses per feedback in tempo reale

### 2. **Controllo Traktor Completo**
- Load tracks da browser Traktor
- Play/Stop deck con anti-blinking logic
- Crossfader professionale con transizioni graduali
- Sync automatico BPM per beatmatching
- Controllo volume per mixing smooth

### 3. **Libreria Musicale Intelligente**
- Scansione automatica con metadata extraction
- Ricerca per genere, BPM, artista
- Compatibilità BPM avanzata (±15%, double/half time)
- Database SQLite per performance ottimali

### 4. **Mixing Professionale**
- Transizioni graduali configura bili (default 30s)
- Sync automatico prima del mix
- Crossfade smooth con step interpolation
- Volume balancing durante transizioni

## 📋 Requisiti

### Software Requirements
- **Python 3.8+** (verificato con 3.12.3)
- **Traktor Pro 3** (o compatibile)
- **macOS** con Audio MIDI Setup e IAC Driver

### Python Packages
```bash
# Core dependencies (già installate)
python-rtmidi>=1.4.9
mido>=1.2.10
mutagen>=1.46.0
pydantic-settings>=2.10.0

# NEW: Claude Agent SDK
claude-agent-sdk>=0.1.0
```

### Hardware/MIDI Setup
1. **IAC Driver** attivo in Audio MIDI Setup
   - Apri "Audio MIDI Setup"
   - Window → Show MIDI Studio
   - Double-click "IAC Driver"
   - Check "Device is online"
   - Verifica che "Bus 1" esista

2. **Traktor Pro** con mapping MIDI
   - Import `traktor/AI_DJ_Complete.tsi`
   - Verifica che "Generic MIDI" sia abilitato
   - IAC Driver Bus 1 come input/output

### API Keys
- **Anthropic API Key** (richiesta per Claude Agent SDK)
  - Ottieni da: https://console.anthropic.com/
  - Imposta con: `export ANTHROPIC_API_KEY="your-key"`
  - O salvala in `.env` file

## 🚀 Quick Start

### Installazione

1. **Clone o naviga nella directory del progetto:**
```bash
cd /Users/Fiore/dj
```

2. **Installa dipendenze:**
```bash
pip install -r requirements_simple.txt
```

3. **Verifica installazione Claude Agent SDK:**
```bash
python -c "import claude_agent_sdk; print('✅ SDK available')"
```

4. **Setup API key:**
```bash
# Metodo 1: Environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# Metodo 2: .env file (creato automaticamente dal launcher)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### Avvio Rapido

**Metodo 1: Launcher Automatico (Raccomandato)**
```bash
python run_autonomous_dj.py
```

Il launcher:
- ✅ Verifica tutti i requisiti
- ✅ Controlla connessione Traktor MIDI
- ✅ Setup configurazione API
- ✅ Mostra guida interattiva
- ✅ Lancia l'agente autonomo

**Metodo 2: Avvio Diretto**
```bash
python autonomous_dj_sdk_agent.py
```

## 🎛️ Utilizzo

### Modalità Interattiva

Dopo l'avvio, ti verrà chiesto:

```
Venue type (club/bar/festival) [club]: club
Event type (warm_up/prime_time/closing) [prime_time]: prime_time

🎤 Autonomous DJ Agent ready!
DJ Command>
```

### Comandi Naturali

L'agente comprende linguaggio naturale. Esempi:

```bash
# Iniziare il set
DJ Command> Start the set with a house track around 125 BPM

# Mixing
DJ Command> Mix to an energetic tech-house track

# Ricerca specifica
DJ Command> Find and play a melodic track by Deadmau5

# Transizione professionale
DJ Command> Do a smooth 45-second transition to deck B

# Controllo manuale
DJ Command> Lower the volume on deck A and bring up deck B
```

### Comandi Speciali

```bash
# Stato sistema
DJ Command> status

# Modalità autonoma (completamente automatica)
DJ Command> auto
Autonomous set duration (minutes) [60]: 120

# Uscita
DJ Command> quit
```

## 🧠 Come Funziona l'Agente

### Custom Tools (Decorator @tool)

L'agente ha accesso a 11 custom tools per Traktor:

1. **load_track_to_deck** - Carica traccia selezionata
2. **play_deck** - Avvia riproduzione
3. **stop_deck** - Ferma deck
4. **set_crossfader** - Posiziona crossfader
5. **set_deck_volume** - Controlla volume
6. **sync_deck** - Sync BPM al master
7. **browse_tracks** - Naviga browser
8. **search_music_library** - Cerca tracce
9. **get_compatible_tracks** - Trova tracce mixabili
10. **get_traktor_status** - Status sistema
11. **professional_mix_transition** - Mix completo automatico

### System Prompt Ottimizzato

L'agente è programmato con:
- **Ruolo**: Professional autonomous DJ
- **Principi**: Beatmatching, transizioni smooth, energy progression
- **Workflow**: Passo-passo con spiegazioni tecniche
- **Tools awareness**: Sa quali tools usare e quando

### Esempio di Reasoning

Quando riceve "Mix to the next track":

```
1. 🔍 Analizza: BPM corrente, genere, energia
2. 🎵 Cerca: get_compatible_tracks(current_bpm=128)
3. 📜 Naviga: browse_tracks(direction="down")
4. 📥 Carica: load_track_to_deck(deck="B")
5. 🎚️ Esegue: professional_mix_transition(from_deck="A", to_deck="B")
```

## 🎯 Modalità Autonoma

### Avvio
```bash
DJ Command> auto
Autonomous set duration (minutes) [60]: 120
```

### Comportamento
- ✅ Seleziona traccia iniziale basata su venue/event
- ✅ Ogni 3-4 minuti cerca prossima traccia compatibile
- ✅ Esegue transizioni professionali automatiche
- ✅ Mantiene progressione energetica coerente
- ✅ Considera harmonic mixing e BPM compatibility

### Monitoraggio
L'agente logga tutte le azioni:
```
🎤 User command: auto
🔧 Tool used: search_music_library
🔧 Tool used: browse_tracks
🔧 Tool used: load_track_to_deck
🔧 Tool used: professional_mix_transition
✅ Track loaded: 'Track Name' - Artist (128 BPM)
🎚️ Crossfader: 0.00 → 1.00 over 30s
```

## 🔧 Troubleshooting

### Issue: "Claude Agent SDK not installed"
```bash
# Soluzione
pip install claude-agent-sdk
```

### Issue: "ANTHROPIC_API_KEY not set"
```bash
# Soluzione 1: Export
export ANTHROPIC_API_KEY="sk-ant-..."

# Soluzione 2: .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### Issue: "Traktor MIDI not detected"
```bash
# Verifica IAC Driver
# 1. Apri Audio MIDI Setup
# 2. Window → Show MIDI Studio
# 3. Double-click IAC Driver
# 4. ✓ "Device is online"

# Test manuale
python -c "import rtmidi; print(rtmidi.MidiOut().get_ports())"
```

### Issue: "No tracks found"
```bash
# Verifica music path
# Default: /Users/Fiore/Music

# Scan manuale
python music_library.py
```

### Issue: "Agent not responding"
```bash
# Check API key validity
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'
```

## 📚 File Structure

```
/Users/Fiore/dj/
├── autonomous_dj_sdk_agent.py     # Main agent (NEW)
├── run_autonomous_dj.py           # Launcher (NEW)
├── requirements_simple.txt        # Updated con SDK
├── config.py                      # Configuration
├── traktor_control.py            # MIDI control
├── music_library.py              # Music scanning
├── core/
│   └── openrouter_client.py     # Legacy (for fallback)
├── traktor/
│   └── AI_DJ_Complete.tsi       # Traktor mapping
└── AUTONOMOUS_DJ_SDK_GUIDE.md   # This file
```

## 🎓 Advanced Usage

### Custom Tools Extension

Vuoi aggiungere nuovi tools? Usa il decorator `@tool`:

```python
from claude_agent_sdk import tool

@tool(
    name="my_custom_tool",
    description="What this tool does"
)
async def my_custom_tool(param: str) -> str:
    """
    Detailed docstring for the agent to understand usage.

    Args:
        param: Parameter description

    Returns:
        Result description
    """
    # Your implementation
    return "Tool result"
```

### System Prompt Customization

Modifica `_build_system_prompt()` in `AutonomousDJAgent`:

```python
def _build_system_prompt(self) -> str:
    return """Your custom DJ personality and instructions..."""
```

### Integration con GUI

Per integrare con GUI tkinter esistente:

```python
# In gui/dj_interface.py
from autonomous_dj_sdk_agent import AutonomousDJAgent

# Create agent
self.sdk_agent = AutonomousDJAgent(config)

# Execute commands
async def send_to_agent(self, user_input):
    response = await self.sdk_agent.execute_command(user_input)
    self.update_chat(response)
```

## 🔬 Testing

### Test Connessione
```bash
# Test MIDI
python traktor_control.py

# Test Music Library
python music_library.py

# Test Agent
python autonomous_dj_sdk_agent.py
```

### Simulation Mode
Se Traktor non è disponibile, il sistema usa simulation mode:
```python
# In traktor_control.py
self.simulation_mode = True  # Comandi simulati, nessun MIDI reale
```

## 🚦 Best Practices

### 1. Preparazione Set
- Scansiona libreria prima: `await music_scanner.scan_library()`
- Verifica connessione Traktor
- Check API key validity

### 2. Durante il Set
- Usa comandi naturali chiari
- Monitora log per tool execution
- Verifica transizioni con `status`

### 3. Troubleshooting
- Check logs in console
- Usa `get_traktor_status` tool
- Test individual tools se necessario

## 📞 Support

### Documentation
- Claude Agent SDK: https://docs.anthropic.com/en/api/agent-sdk
- Traktor MIDI: traktor/AI_DJ_Complete.tsi comments
- Project README: /Users/Fiore/dj/CLAUDE.md

### Logs
```bash
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎉 What's New (Claude Agent SDK Edition)

### vs. Previous OpenRouter Implementation

| Feature | OpenRouter (Old) | Claude Agent SDK (New) |
|---------|-----------------|----------------------|
| LLM Model | Free models (GLM-4.5) | Claude Sonnet 4 (premium) |
| Tool Calling | Manual JSON parsing | Native @tool decorator |
| Response | Text-only | Streaming + tool execution |
| Error Handling | Manual | SDK-managed |
| Custom Tools | N/A | 11 custom DJ tools |
| Autonomy | Limited | Full agent autonomy |
| Reasoning | Basic | Advanced multi-step |

### Key Improvements
- ✅ **Native tool execution** con @tool decorator
- ✅ **Streaming responses** per feedback real-time
- ✅ **Better reasoning** con Claude Sonnet 4
- ✅ **Robust error handling** gestito dall'SDK
- ✅ **Professional mixing** logic integrata
- ✅ **State management** migliorato

## 🎵 Enjoy Your Autonomous DJ! 🎵

Per domande o problemi, controlla:
1. Questa documentazione
2. Console logs
3. `python run_autonomous_dj.py --help`
