# Traktor Pro 3 MIDI Setup - Approccio Corretto

## 🎯 IMPORTANTE: Come Funziona Veramente

**Traktor NON ha CC numbers fissi predefiniti!**

A differenza di altri software DJ, Traktor ti permette di assegnare **QUALSIASI CC number** a **QUALSIASI funzione** usando la modalità **MIDI Learn**.

## ✅ Approccio Corretto per il Nostro Sistema

### Opzione 1: Usare MIDI Learn in Traktor (CONSIGLIATO)

Invece di indovinare i CC numbers, dobbiamo:

1. **Aprire Traktor Pro 3**
2. **Preferences → Controller Manager**
3. **Add... → Generic MIDI**
4. **In-Port**: None
5. **Out-Port**: IAC Driver Bus 1
6. **Add In...** per ogni comando che vogliamo mappare
7. **Click "Learn"** (diventa giallo)
8. **Inviare il CC number dal nostro script Python**
9. **Traktor riconosce automaticamente il CC e lo assegna**

### Opzione 2: Importare TSI File Pre-configurato

Se hai già un file TSI con mapping funzionanti:

1. **Preferences → Controller Manager**
2. **Import...** → Seleziona il file `.tsi`
3. **Verificare In-Port e Out-Port**

## 🔧 Setup Passo-Passo con MIDI Learn

### Fase 1: Preparazione

```bash
# 1. Abilita IAC Driver
# Audio MIDI Setup → Window → Show MIDI Studio
# Double-click IAC Driver → Check "Device is online"

# 2. Avvia Traktor Pro 3

# 3. Apri Controller Manager
# Preferences → Controller Manager
```

### Fase 2: Creare Mapping Generic MIDI

1. Click **Add...** → **Generic MIDI**
2. Rinomina in "AI DJ Control"
3. **In-Port**: None (solo ricezione)
4. **Out-Port**: IAC Driver Bus 1

### Fase 3: Mappare i Comandi (Esempio: Play/Pause Deck A)

1. Click **Add In...** (sotto Assignment Table)
2. Naviga: **Deck Common → Play/Pause**
3. Seleziona **Assignment**: Deck A
4. **Type of Controller**: Button
5. **Interaction Mode**: Toggle
6. Click **Learn** (diventa giallo)
7. **Esegui lo script Python** che invia CC 20 = 127
8. **Traktor cattura automaticamente** "Ch 1.CC 20"
9. Click **Learn** di nuovo per disattivare

### Fase 4: Ripeti per Ogni Comando

Ecco la lista dei comandi essenziali da mappare:

#### Transport Controls
- Deck A Play/Pause → CC 20
- Deck B Play/Pause → CC 21
- Deck A Cue → CC 22
- Deck B Cue → CC 23
- Deck A Sync → CC 24
- Deck B Sync → CC 25

#### Volume & Mixer
- Deck A Volume → CC 28
- Deck B Volume → CC 29
- Deck A Filter → CC 30
- Deck B Filter → CC 31
- Crossfader → CC 32

#### EQ Controls
- Deck A EQ High → CC 34
- Deck A EQ Mid → CC 35
- Deck A EQ Low → CC 36
- Deck B EQ High → CC 50
- Deck B EQ Mid → CC 51
- Deck B EQ Low → CC 52

#### Browser
- Move Up → CC 37
- Move Down → CC 38
- Load to Deck A → CC 39
- Load to Deck B → CC 40

#### Loops
- Deck A Loop In → CC 70
- Deck A Loop Out → CC 71
- Deck A Loop Active → CC 72
- Deck A Loop Size /2 → CC 73
- Deck A Loop Size x2 → CC 74

#### Hotcues (Deck A)
- Hotcue 1 → CC 80
- Hotcue 2 → CC 81
- Hotcue 3 → CC 82
- Hotcue 4 → CC 83
- Hotcue 5 → CC 84
- Hotcue 6 → CC 85
- Hotcue 7 → CC 86
- Hotcue 8 → CC 87

## 🛠️ Script di Test per MIDI Learn

Usa questo script mentre hai MIDI Learn attivo in Traktor:

```bash
python test_cc_discovery.py
```

1. **Opzione 3**: Test singolo CC
2. **In Traktor**: Click "Learn" per il comando desiderato
3. **Nello script**: Inserisci il CC number (es. 20)
4. **Osserva Traktor**: Dovrebbe catturare il CC automaticamente
5. **Click Learn** di nuovo per disattivare
6. **Test**: Ripeti il comando per verificare che funzioni

## 📋 Lista Comandi Traktor Disponibili

### Deck Common
- Play/Pause
- Cue
- Cup (Cue + Play)
- Sync
- Master
- Keylock
- Load Selected Track
- Unload Track
- Deck Focus

### Track Deck
- Tempo Bend +/-
- Tempo Fader (Pitch)
- Hotcue 1-8 (Store/Delete/Trigger)
- Loop In/Out/Active
- Loop Size
- Move Loop
- Beatjump

### Mixer
- Volume (Deck A/B/C/D)
- Gain
- EQ High/Mid/Low
- Filter
- Crossfader
- Crossfader Curve

### Browser
- Tree Up/Down
- List Up/Down
- Favorites Add/Remove
- Load to Deck

### FX Units
- FX 1/2/3/4 On/Off
- FX Amount
- FX Button 1/2/3

## ⚡ Automation Script per MIDI Learn

Possiamo creare uno script che automatizza il mapping:

```python
# auto_midi_learn.py
# Invia sequenzialmente tutti i CC numbers
# mentre tu clicchi "Learn" in Traktor per ogni comando
```

## 🔍 Verifica Mapping Esistente

Se hai già un file `.tsi` importato, puoi verificare i mapping:

1. **Preferences → Controller Manager**
2. **Seleziona il device** nella lista
3. **Guarda Assignment Table** per vedere tutti i CC mappati

## 📝 Export del Mapping

Una volta completato il mapping:

1. **Seleziona il device** in Controller Manager
2. **Export...** → Salva come `AI_DJ_Perfect_Mapping.tsi`
3. **Commit nel repository** per backup

## 🎯 Prossimi Passi

1. [ ] Aprire Traktor e verificare se esiste già un mapping "AI DJ" o "Generic MIDI"
2. [ ] Se esiste, export del mapping e analisi
3. [ ] Se non esiste, creare nuovo mapping usando MIDI Learn
4. [ ] Testare ogni comando con lo script `test_cc_discovery.py`
5. [ ] Export del mapping finale
6. [ ] Aggiornare `traktor_control.py` con i CC numbers corretti

## 📚 Risorse

- [Native Instruments - Controller Manager Guide](https://support.native-instruments.com/hc/en-us/articles/209590569)
- [DJ TechTools - MIDI Mapping Tutorial](https://djtechtools.com/2015/02/26/intro-to-basic-midi-mapping-with-traktor/)
- Traktor Pro 3 Manual - Section "Configuring MIDI Controller"
