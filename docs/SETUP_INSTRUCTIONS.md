# 🎯 ISTRUZIONI SETUP TRAKTOR MIDI - PASSO PASSO

## ⚠️ PROBLEMA SCOPERTO

Il file TSI che hai esportato **NON contiene alcun mapping Generic MIDI** per IAC Driver!

Contiene solo configurazioni per controller hardware Native Instruments:
- Traktor Kontrol X1 MK2
- Traktor Kontrol Z2

**Questo spiega perché i comandi MIDI dal nostro Python non funzionano!**

## ✅ SOLUZIONE: Creare Mapping da Zero con MIDI Learn

### Fase 1: Setup IAC Driver (Già Fatto ✓)

Hai già abilitato IAC Driver Bus 1 in Audio MIDI Setup.

### Fase 2: Creare Device Generic MIDI in Traktor

1. **Apri Traktor Pro 3**

2. **Preferences → Controller Manager**

3. **Click "Add..." (in basso a sinistra)**

4. **Seleziona "Generic MIDI"**

5. **Rinomina in "AI DJ Control"** (doppio-click sul nome)

6. **Configura porte**:
   - **In-Port**: `None` (non riceviamo da hardware)
   - **Out-Port**: `IAC Driver Bus 1`

7. **Click "Add In..."** per iniziare a mappare

### Fase 3: Mappare PRIMO Comando (Play/Pause Deck A)

Ora testiamo il sistema con UN SOLO comando per verificare che funzioni:

1. **In Controller Manager, click "Add In..."**

2. **Naviga nel menu**:
   ```
   Deck Common → Transport → Play/Pause
   ```

3. **Configura il mapping**:
   - **Device Target**: `Deck A`
   - **Mapped to**: `Ch 1.Note.C 0` (cambiamo dopo)
   - **Interaction Mode**: `Toggle`
   - **Type of Controller**: `Button`

4. **Click sul pulsante "Learn"** (diventa giallo ⚠️)

5. **SENZA CHIUDERE TRAKTOR**, apri un nuovo terminale e esegui:

```bash
cd /Users/Fiore/dj
python3 -c "
import rtmidi
import time

# Connetti a IAC
midi_out = rtmidi.MidiOut()
ports = midi_out.get_ports()
print('Porte disponibili:', ports)

# Cerca IAC Driver
iac_port = None
for i, port in enumerate(ports):
    if 'IAC' in port or 'Bus 1' in port:
        iac_port = i
        break

if iac_port is not None:
    midi_out.open_port(iac_port)
    print(f'✅ Connesso a: {ports[iac_port]}')

    # Invia CC 20 = 127
    print('📡 Invio CC 20 = 127...')
    midi_out.send_message([0xB0, 20, 127])  # Channel 1, CC 20, Value 127

    time.sleep(0.5)
    midi_out.close_port()
    print('✅ Comando inviato!')
else:
    print('❌ IAC Driver non trovato!')
"
```

6. **Osserva Traktor**: Dovrebbe aver catturato automaticamente `Ch 1.CC 20`

7. **Click "Learn"** di nuovo per disattivare (torna grigio)

8. **TESTA IL COMANDO**:
   - Carica una traccia nel Deck A
   - Esegui di nuovo lo script Python sopra
   - **Deck A dovrebbe avviarsi/fermarsi!** ▶️⏸️

### Fase 4: Se Funziona → Mappa Tutti i Comandi

Se il test del Play/Pause funziona, procedi a mappare tutti gli altri comandi seguendo la stessa procedura.

#### Comandi Essenziali da Mappare:

```
TRANSPORT:
CC 20 → Deck A Play/Pause
CC 21 → Deck B Play/Pause
CC 22 → Deck A Cue
CC 23 → Deck B Cue
CC 24 → Deck A Sync
CC 25 → Deck B Sync

MIXER:
CC 28 → Deck A Volume (Fader, 0-127)
CC 29 → Deck B Volume (Fader, 0-127)
CC 32 → Crossfader (Fader, 0-127)

EQ:
CC 34 → Deck A EQ High (Knob, 0-127)
CC 35 → Deck A EQ Mid (Knob, 0-127)
CC 36 → Deck A EQ Low (Knob, 0-127)
CC 50 → Deck B EQ High (Knob, 0-127)
CC 51 → Deck B EQ Mid (Knob, 0-127)
CC 52 → Deck B EQ Low (Knob, 0-127)

BROWSER:
CC 37 → Move Down (Encoder +1/-1)
CC 38 → Move Up (Encoder +1/-1)
CC 39 → Load to Deck A (Button)
CC 40 → Load to Deck B (Button)

LOOPS (Deck A):
CC 70 → Loop In (Button)
CC 71 → Loop Out (Button)
CC 72 → Loop Active Toggle (Button)
CC 73 → Loop Size /2 (Button)
CC 74 → Loop Size x2 (Button)

HOTCUES (Deck A):
CC 80-87 → Hotcue 1-8 (Button, Toggle mode)
```

### Fase 5: Export del Mapping Finale

Una volta completato:

1. **Seleziona "AI DJ Control"** in Controller Manager

2. **Click "Export..."**

3. **Salva come**: `AI_DJ_IAC_Mapping.tsi`

4. **Chiudi Preferences**

5. **Copia il file nel repository**:
```bash
cp "/Users/Fiore/Documents/Native Instruments/Traktor/AI_DJ_IAC_Mapping.tsi" /Users/Fiore/dj/traktor/
```

## 🔧 ALTERNATIVA: Script Auto-Mapping

Posso creare uno script che automatizza il mapping usando MIDI Learn:

1. Tu avvii lo script
2. Lo script ti dice quale comando mappare
3. Tu clicchi "Learn" in Traktor
4. Lo script invia il CC number
5. Tu clicchi "Learn" di nuovo
6. Ripeti per tutti i comandi

Vuoi che crei questo script?

## 📝 NOTE IMPORTANTI

- **Traktor DEVE essere in esecuzione** durante il MIDI Learn
- **IAC Driver DEVE essere abilitato**
- **Controller Manager DEVE essere aperto** con "Learn" attivo
- **Ogni CC number** può essere mappato a UNA SOLA funzione
- **Button vs Fader/Knob**: Scegli il tipo corretto per ogni comando

## 🎯 PROSSIMO PASSO

**PRIMA FAI IL TEST con Play/Pause!**

Se il Deck A si avvia/ferma quando esegui lo script Python, allora il sistema funziona e puoi procedere a mappare tutti gli altri comandi.

Se NON funziona, debuggiamo insieme il problema prima di continuare.
