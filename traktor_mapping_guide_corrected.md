# 🗺️ Guida Mapping Traktor Corretta - AI DJ System

**AGGIORNATA**: Mapping verificati e corretti per corrispondenza effettiva con Traktor Pro 3

## ⚠️ IMPORTANTE: Setup Preliminare

### 1. Abilitare IAC Driver
1. Aprire **Audio MIDI Setup** (in /Applications/Utilities/)
2. **Window** → **Show MIDI Studio**
3. Doppio click su **IAC Driver**
4. ✅ Spuntare **"Device is online"**
5. Verificare che **Bus 1** sia presente nella lista
6. Chiudere Audio MIDI Setup

### 2. Setup Traktor Pro 3
1. Avviare **Traktor Pro 3**
2. **Traktor** → **Preferences** (o Cmd+,)
3. Sidebar sinistra: **Controller Manager**

## 🎛️ Creazione Device AI DJ Controller

### Se il device non esiste:
1. Click **"Add..."** in basso a sinistra
2. Selezionare **"Generic MIDI"**
3. **Device Name**: `AI DJ Controller`
4. **In-Port**: Selezionare `IAC Driver Bus 1`
5. **Out-Port**: Selezionare `IAC Driver Bus 1`
6. Click **"OK"**

### Se il device esiste già:
1. Selezionare **"AI DJ Controller"** nella lista
2. Verificare che In-Port e Out-Port siano `IAC Driver Bus 1`

## 📋 Mapping MIDI Corretti

**ATTENZIONE**: Questi mapping corrispondono esattamente al codice Python aggiornato

### TRANSPORT CONTROLS (CH1 CC20-27)
| Comando | Channel | CC | Target Traktor | Type | Mode |
|---------|---------|----|--------------  |------|------|
| Play Deck A | 1 | 20 | Deck A → Play | Button | Toggle |
| Play Deck B | 1 | 21 | Deck B → Play | Button | Toggle |
| Play Deck C | 1 | 22 | Deck C → Play | Button | Toggle |
| Play Deck D | 1 | 23 | Deck D → Play | Button | Toggle |
| Cue Deck A | 1 | 24 | Deck A → Cue | Button | Hold |
| Cue Deck B | 1 | 25 | Deck B → Cue | Button | Hold |
| Cue Deck C | 1 | 26 | Deck C → Cue | Button | Hold |
| Cue Deck D | 1 | 27 | Deck D → Cue | Button | Hold |

### VOLUME CONTROLS (CH1 CC28-33)
| Comando | Channel | CC | Target Traktor | Type | Mode |
|---------|---------|----|--------------  |------|------|
| Volume Deck A | 1 | 28 | Deck A → Volume | Fader | Direct |
| Volume Deck B | 1 | 29 | Deck B → Volume | Fader | Direct |
| Volume Deck C | 1 | 30 | Deck C → Volume | Fader | Direct |
| Volume Deck D | 1 | 31 | Deck D → Volume | Fader | Direct |
| Crossfader | 1 | 32 | Mixer → Crossfader | Fader | Direct |
| Master Volume | 1 | 33 | Mixer → Main Volume | Fader | Direct |

### EQ CONTROLS (CH1 CC34-36, 50-52)
| Comando | Channel | CC | Target Traktor | Type | Mode |
|---------|---------|----|--------------  |------|------|
| EQ High Deck A | 1 | 34 | Deck A → EQ High | Fader | Direct |
| EQ Mid Deck A | 1 | 35 | Deck A → EQ Mid | Fader | Direct |
| EQ Low Deck A | 1 | 36 | Deck A → EQ Low | Fader | Direct |
| EQ High Deck B | 1 | 50 | Deck B → EQ High | Fader | Direct |
| EQ Mid Deck B | 1 | 51 | Deck B → EQ Mid | Fader | Direct |
| EQ Low Deck B | 1 | 52 | Deck B → EQ Low | Fader | Direct |

### BROWSER CONTROLS (CH1 CC37-40) ⭐ ESSENZIALI
| Comando | Channel | CC | Target Traktor | Type | Mode |
|---------|---------|----|--------------  |------|------|
| Browser Up | 1 | 37 | Browser → List Up | Button | Trigger |
| Browser Down | 1 | 38 | Browser → List Down | Button | Trigger |
| Load Deck A | 1 | 39 | Browser → Load → Deck A | Button | Trigger |
| Load Deck B | 1 | 40 | Browser → Load → Deck B | Button | Trigger |

### SYNC CONTROLS (CH1 CC41-44)
| Comando | Channel | CC | Target Traktor | Type | Mode |
|---------|---------|----|--------------  |------|------|
| Sync Deck A | 1 | 41 | Deck A → Sync | Button | Toggle |
| Sync Deck B | 1 | 42 | Deck B → Sync | Button | Toggle |
| Sync Deck C | 1 | 43 | Deck C → Sync | Button | Toggle |
| Sync Deck D | 1 | 44 | Deck D → Sync | Button | Toggle |

### PITCH CONTROLS (CH1 CC45-48)
| Comando | Channel | CC | Target Traktor | Type | Mode |
|---------|---------|----|--------------  |------|------|
| Pitch Deck A | 1 | 45 | Deck A → Tempo | Fader | Direct |
| Pitch Deck B | 1 | 46 | Deck B → Tempo | Fader | Direct |
| Pitch Deck C | 1 | 47 | Deck C → Tempo | Fader | Direct |
| Pitch Deck D | 1 | 48 | Deck D → Tempo | Fader | Direct |

## 📋 Procedura Step-by-Step

### Per ogni mapping:
1. Con **AI DJ Controller** selezionato, click **"Add In..."**
2. **Learn**: Click e muovere il controllo in Traktor
3. **Device**: Selezionare `IAC Driver Bus 1`
4. **Channel**: Impostare il Channel dalla tabella
5. **Note/CC**: Selezionare **CC** e impostare il numero dalla tabella
6. **Assignment**: Trovare il controllo corretto di Traktor
7. **Type**: Impostare Button o Fader secondo tabella
8. **Mode**: Impostare Toggle/Hold/Trigger/Direct secondo tabella

### Navigazione Menu Traktor per Assignment:

#### DECK CONTROLS:
- **Deck A/B/C/D** → **Transport** → **Play** (per Play)
- **Deck A/B/C/D** → **Transport** → **Cue** (per Cue)
- **Deck A/B/C/D** → **Mixer** → **Volume** (per Volume)
- **Deck A/B/C/D** → **EQ** → **High/Mid/Low** (per EQ)
- **Deck A/B/C/D** → **Transport** → **Sync** (per Sync)
- **Deck A/B/C/D** → **Transport** → **Tempo** (per Pitch)

#### MIXER CONTROLS:
- **Mixer** → **Main** → **Volume** (per Master Volume)
- **Mixer** → **Crossfader** (per Crossfader)

#### BROWSER CONTROLS:
- **Browser** → **List** → **Up** (per Browser Up)
- **Browser** → **List** → **Down** (per Browser Down)
- **Browser** → **Load** → **Deck A** (per Load Deck A)
- **Browser** → **Load** → **Deck B** (per Load Deck B)

## ✅ Verifica Setup

### Dopo aver completato i mapping:
1. **File** → **Save** per salvare i mapping
2. Chiudere Preferences
3. Eseguire il test: `python test_midi_mapping_verification.py`
4. Verificare che ogni comando risponda correttamente

### Risoluzione Problemi:
- **Comando non risponde**: Verificare Channel e CC number
- **Comando sbagliato**: Controllare Assignment target
- **Risposta parziale**: Verificare Type (Button vs Fader)
- **Comportamento errato**: Verificare Mode (Toggle/Hold/Trigger/Direct)

## 🚨 CONTROLLI CRITICI PER FUNZIONAMENTO

### PRIORITY 1 - ESSENZIALI:
- ✅ Play Deck A/B (CC 20-21)
- ✅ Browser Up/Down (CC 37-38)
- ✅ Load Deck A/B (CC 39-40)
- ✅ Volume Deck A/B (CC 28-29)
- ✅ Crossfader (CC 32)

### PRIORITY 2 - IMPORTANTI:
- Cue Deck A/B (CC 24-25)
- Sync Deck A/B (CC 41-42)
- EQ Controls (CC 34-36, 50-52)

### PRIORITY 3 - OPZIONALI:
- Deck C/D controls
- Pitch controls
- Master Volume

## 📞 Test Rapido

Dopo il setup, testare i comandi critici:
```bash
# Test immediato con Python
python -c "
from traktor_control import TraktorController
from config import get_config
controller = TraktorController(get_config())
if controller.connect():
    print('✅ MIDI OK')
    controller.browse_track_down()  # Test browser
    controller.play_deck('A')       # Test play
else:
    print('❌ MIDI Failed')
"
```

## 📈 Note Tecniche

- **Range CC**: 20-52 + 80-103 per evitare conflitti
- **Channel 1**: AI Control commands
- **Channel 3**: Human Override (emergency)
- **Channel 4**: Effects (avanzato)
- **IAC Latency**: ~2-5ms su macOS (accettabile per DJ)

---

**Versione**: 1.1 - Mappings Verificati
**Compatibilità**: Traktor Pro 3.x
**Testato**: macOS con IAC Driver
**Aggiornato**: 2025-09-28