# 🎛️ CONFIGURAZIONE TRAKTOR PER DJ AI SYSTEM

## ⚠️ SETUP OBBLIGATORIO - SEGUI QUESTI PASSI

### **PASSO 1: Configurazione IAC Driver (GIÀ FATTO)**
✅ **COMPLETATO** - IAC Driver Bus 1 è già configurato e funzionante

### **PASSO 2: Import Mapping Traktor**

1. **Apri Traktor Pro 3**

2. **Vai in Preferences → Controller Manager**

3. **Clicca "Import" in basso a sinistra**

4. **Seleziona il file**: `/Users/Fiore/dj/traktor/AI_DJ_Complete.tsi`

5. **Verifica device "AI DJ Agent Controller" sia presente e attivo**

### **PASSO 3: Carica Tracce nei Deck (IMPORTANTE!)**

**Il problema "Play A non fa partire traccia" è normale!**

Il sistema DJ AI invia solo comandi MIDI. Devi:

1. **Caricare manualmente una traccia nel Deck A**:
   - Drag & drop da Browser a Deck A
   - Oppure seleziona traccia e premi Load A

2. **Caricare una traccia nel Deck B**:
   - Stessa procedura per Deck B

3. **Ora i comandi Play/Pause funzioneranno!**

### **PASSO 4: Test Configurazione**

1. **Carica tracce in Deck A e B**

2. **Avvia DJ AI System**:
   ```bash
   export OPENROUTER_MODEL="nousresearch/hermes-3-llama-3.1-405b"
   python3 dj_ai.py
   ```

3. **Test nella GUI**:
   - ✅ **MIDI Test**: Dovrebbe dire "OK" e Traktor dovrebbe lampeggiare
   - ✅ **Play A**: Dovrebbe avviare la traccia del Deck A
   - ✅ **Chat AI**: Dovrebbe rispondere ai messaggi

## 🎯 **MAPPING CONTROLLI DISPONIBILI**

Il mapping `AI_DJ_Complete.tsi` include:

### **Channel 1 - AI Control (Funzionano):**
- **Volume Deck A/B/C/D**: CC 7,8,9,10
- **Crossfader**: CC 11
- **EQ High/Mid/Low**: CC 12-17
- **Play/Pause**: CC 20-23 (Trigger - funziona solo con tracce caricate!)
- **Cue**: CC 24-27
- **Sync**: CC 28-31

### **Channel 2 - Status Feedback (In arrivo):**
- **BPM feedback**: CC 40-43
- **Position feedback**: CC 44-47

### **Channel 3 - Human Override:**
- **Emergency Stop**: CC 80
- **Master Volume**: CC 85

## 🚨 **RISOLUZIONE PROBLEMI**

### **❌ "Play A non funziona"**
**CAUSA**: Nessuna traccia caricata nel Deck A
**SOLUZIONE**: Carica una traccia nel Deck A tramite Browser Traktor

### **❌ "Chat AI non risponde"**
**CAUSA**: Modello deepseek rate-limited
**SOLUZIONE**: Usa il comando:
```bash
export OPENROUTER_MODEL="nousresearch/hermes-3-llama-3.1-405b"
python3 dj_ai.py
```

### **❌ "MIDI Test fallisce"**
**CAUSA**: IAC Driver o mapping non configurato
**SOLUZIONE**:
1. Verifica Audio MIDI Setup → IAC Driver → "Device is online"
2. Importa `AI_DJ_Complete.tsi` in Controller Manager

## ✅ **CONFIGURAZIONE COMPLETA FINALE**

1. ✅ IAC Driver attivo
2. ✅ Mapping importato in Traktor
3. ✅ Tracce caricate in Deck A e B
4. ✅ Modello AI funzionante (hermes)

**Ora tutto dovrebbe funzionare perfettamente!** 🎉