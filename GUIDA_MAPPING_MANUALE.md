# 🎛️ GUIDA MAPPING MANUALE TRAKTOR

## ⚡ CONFIGURAZIONE RAPIDA - 5 MINUTI

Poiché il file TSI non si importa, creiamo il mapping manualmente in Traktor.

### 🔧 **PASSO 1: Setup Controller in Traktor**

1. **Apri Traktor Pro 3**

2. **Vai in Preferences → Controller Manager**

3. **Clicca "Add Generic" → "Generic MIDI"**

4. **Configura Device:**
   - **Device Name**: `DJ AI Controller`
   - **In-Port**: `Bus 1` (IAC Driver)
   - **Out-Port**: `Bus 1` (IAC Driver)
   - **Spunta "In-Port" e "Out-Port"**

5. **Clicca "Add" per confermare**

### 🎯 **PASSO 2: Mappings Essenziali (7 controlli principali)**

#### **A. Volume Deck A**
1. Clicca "Add In..."
2. **Learn** → nella GUI DJ AI clicca il pulsante volume deck A
3. **Assignment**: `Deck A → Volume`
4. **Type**: `Fader`
5. **Interaction Mode**: `Direct`

#### **B. Volume Deck B**
1. Clicca "Add In..."
2. **Learn** → nella GUI DJ AI clicca il pulsante volume deck B
3. **Assignment**: `Deck B → Volume`
4. **Type**: `Fader`

#### **C. Play Deck A**
1. Clicca "Add In..."
2. **Learn** → nella GUI DJ AI clicca "Play A"
3. **Assignment**: `Deck A → Play`
4. **Type**: `Button` (IMPORTANTE!)
5. **Interaction Mode**: `Toggle`

#### **D. Play Deck B**
1. Clicca "Add In..."
2. **Learn** → nella GUI DJ AI clicca "Play B"
3. **Assignment**: `Deck B → Play`
4. **Type**: `Button`
5. **Interaction Mode**: `Toggle`

#### **E. Crossfader**
1. Clicca "Add In..."
2. **Learn** → nella GUI DJ AI muovi il crossfader
3. **Assignment**: `Mixer → Crossfader`
4. **Type**: `Fader`

#### **F. Cue Deck A**
1. Clicka "Add In..."
2. **Learn** → nella GUI DJ AI clicca "Cue A"
3. **Assignment**: `Deck A → Cue`
4. **Type**: `Button`
5. **Interaction Mode**: `Hold`

#### **G. Cue Deck B**
1. Clicca "Add In..."
2. **Learn** → nella GUI DJ AI clicca "Cue B"
3. **Assignment**: `Deck B → Cue`
4. **Type**: `Button`
5. **Interaction Mode**: `Hold`

### ⚡ **PASSO 3: Test Rapido**

1. **Carica una traccia nel Deck A** (drag & drop dal Browser)
2. **Carica una traccia nel Deck B**
3. **Nella GUI DJ AI clicca "Play A"** → La traccia dovrebbe partire!
4. **Clicca "Play B"** → Anche questa dovrebbe partire!
5. **Muovi il Crossfader** → Senti il mix tra le due tracce

### 📋 **VALORI MIDI ESATTI (Per Mapping Avanzato)**

Se vuoi creare tutti i mappings manualmente senza Learn:

```text
CONTROLLO                MIDI           TRAKTOR ASSIGNMENT
─────────────────────────────────────────────────────────────
Volume Deck A           CH1 CC7        Deck A → Volume
Volume Deck B           CH1 CC8        Deck B → Volume
Crossfader              CH1 CC11       Mixer → Crossfader
Play Deck A             CH1 CC20       Deck A → Play (Button)
Play Deck B             CH1 CC21       Deck B → Play (Button)
Cue Deck A              CH1 CC24       Deck A → Cue (Button)
Cue Deck B              CH1 CC25       Deck B → Cue (Button)
Sync Deck A             CH1 CC28       Deck A → Sync (Button)
Sync Deck B             CH1 CC29       Deck B → Sync (Button)

EQ Deck A High          CH1 CC12       Deck A → EQ High
EQ Deck A Mid           CH1 CC13       Deck A → EQ Mid
EQ Deck A Low           CH1 CC14       Deck A → EQ Low
EQ Deck B High          CH1 CC15       Deck B → EQ High
EQ Deck B Mid           CH1 CC16       Deck B → EQ Mid
EQ Deck B Low           CH1 CC17       Deck B → EQ Low
```

### 🎯 **TIPI DI CONTROLLO**

- **Fader**: Volume, EQ, Crossfader (valori 0-127 continui)
- **Button**: Play, Pause, Cue, Sync (trigger on/off)
- **Toggle**: Per Play/Pause (alterna tra stati)
- **Hold**: Per Cue (attivo mentre premuto)

### 🚨 **RISOLUZIONE PROBLEMI**

#### **❌ "Learn" non rileva i comandi**
- Assicurati che DJ AI System sia avviato
- Verifica che IAC Driver Bus 1 sia online
- Prova a cliccare più volte il controllo

#### **❌ "Play A funziona ma non senti audio"**
- Verifica che ci sia una traccia caricata nel Deck A
- Controlla il volume del deck in Traktor
- Verifica che il crossfader non sia completamente su B

#### **❌ "MIDI viene rilevato ma non funziona"**
- Controlla che il Type sia corretto (Button vs Fader)
- Per Play/Pause usa "Toggle" mode
- Per Cue usa "Hold" mode

### ✅ **CONFIGURAZIONE MINIMA FUNZIONANTE**

Con questi 7 mappings puoi già fare un DJ set completo:
1. ✅ Volume Deck A/B
2. ✅ Play Deck A/B
3. ✅ Crossfader
4. ✅ Cue Deck A/B

**Tempo stimato configurazione**: 5-10 minuti
**Risultato**: Sistema DJ AI completamente funzionale! 🎉
