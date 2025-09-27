# 🔍 Istruzioni Debug MIDI - Icona Traktor Non Lampeggia

## 🚨 PROBLEMA: L'icona MIDI di Traktor non si accende

L'icona MIDI in Traktor dovrebbe lampeggiare quando riceve segnali MIDI, ma attualmente non succede.

## 🧪 TEST DA ESEGUIRE IN ORDINE

### 1. Test Ultra-Basilare (PRIMO TEST)
```bash
python debug_midi_basic.py
```

**Cosa verifica:**
- ✅ Se rtmidi funziona
- ✅ Quali porte MIDI esistono nel sistema
- ✅ Se può creare porte virtuali
- ✅ Se può inviare messaggi MIDI
- ✅ Test loop continuo (come il tuo script originale)

**Cosa osservare:**
- Lista di tutte le porte MIDI
- Se trova porte di Traktor
- Se riesce a inviare messaggi
- **SE L'ICONA MIDI LAMPEGGIA IN TRAKTOR**

### 2. Test macOS IAC Driver (SE IL PRIMO FALLISCE)
```bash
python test_macos_iac.py
```

**Cosa fa:**
- ✅ Configura l'IAC Driver nativo di macOS
- ✅ Usa il sistema MIDI integrato di macOS
- ✅ Test specifico per macOS

**Requisiti:**
1. Apri "Audio MIDI Setup" (Applicazioni > Utility)
2. Menu Window > Show MIDI Studio
3. Doppio click su "IAC Driver"
4. Spunta "Device is online"
5. Assicurati che "Bus 1" esista

### 3. Test Libreria Alternativa (SE GLI ALTRI FALLISCONO)
```bash
python test_mido_alternative.py
```

**Cosa verifica:**
- ✅ Se mido funziona meglio di rtmidi
- ✅ Backend MIDI alternativi
- ✅ Diversi metodi di comunicazione

## 🎛️ CONFIGURAZIONE TRAKTOR RICHIESTA

### Prima di testare, assicurati che:

1. **Traktor Pro è aperto e funzionante**
2. **MIDI è abilitato in Traktor:**
   - Preferences > Controller Manager
   - Aggiungi "Generic MIDI" se non presente
   - Configura Input/Output

### Configurazione minima Traktor:
```
Controller Manager > Add > Generic MIDI
├── Input Device: [scegli dalla lista]
├── Output Device: [scegli dalla lista]
└── Mapping: CC 127 -> qualsiasi controllo
```

## 🔍 COSA CERCARE NEI TEST

### ✅ Segnali di successo:
- "Porte Traktor rilevate"
- "Messaggio inviato con successo"
- "Porta virtuale creata"
- **ICONA MIDI LAMPEGGIA IN TRAKTOR**

### ❌ Segnali di problemi:
- "Nessuna porta Traktor trovata"
- "Errore invio messaggio"
- "rtmidi non disponibile"
- **ICONA MIDI NON LAMPEGGIA**

## 🛠️ SOLUZIONI PER PROBLEMI COMUNI

### Se "Nessuna porta Traktor trovata":
```bash
# 1. Assicurati che Traktor sia aperto
# 2. Riavvia Traktor
# 3. Verifica in Traktor Preferences > Controller Manager
```

### Se "Errore creazione porta virtuale":
```bash
# macOS: Abilita IAC Driver
# 1. Apri Audio MIDI Setup
# 2. Show MIDI Studio
# 3. IAC Driver > Device is online
```

### Se "rtmidi non disponibile":
```bash
pip uninstall python-rtmidi
pip install python-rtmidi
```

### Se l'icona MIDI non lampeggia MA i messaggi vengono inviati:
1. **Verifica mappature in Traktor:**
   - Controller Manager > Generic MIDI
   - Aggiungi mapping per CC 127
   - Test che la mappatura funzioni

2. **Riavvia Traktor**
3. **Controlla che MIDI sia abilitato globalmente in Traktor**

## 📊 DIAGNOSI RAPIDA

Esegui questo per una diagnosi immediata:
```bash
python debug_midi_basic.py
```

**Osserva l'output per:**
- Quante porte MIDI sono trovate
- Se Traktor appare nelle porte
- Se i messaggi vengono inviati senza errori
- **SE L'ICONA MIDI LAMPEGGIA**

## 🆘 SE NULLA FUNZIONA

### Controlli di sistema macOS:
1. **Permessi audio:**
   - Preferenze Sistema > Sicurezza e Privacy > Privacy > Microfono
   - Assicurati che Terminal/Python abbia accesso

2. **Driver audio:**
   - Riavvia Core Audio: `sudo killall coreaudiod`
   - Riavvia il Mac

3. **Reinstalla dipendenze:**
   ```bash
   pip uninstall mido python-rtmidi
   pip install mido python-rtmidi
   ```

### Test manuale Traktor:
1. Apri Traktor
2. Preferences > Controller Manager
3. Generic MIDI > Learn
4. Muovi un controllo (es. crossfader)
5. Osserva se l'icona MIDI lampeggia

Se nemmeno questo fa lampeggiare l'icona, il problema è nella configurazione MIDI di Traktor, non nel nostro codice.

## 📞 Report del Test

Dopo aver eseguito i test, riporta:
1. **Quale test ha funzionato/fallito**
2. **Messaggi di errore specifici**
3. **Se l'icona MIDI ha mai lampeggiato**
4. **Lista delle porte MIDI trovate**
5. **Versione di Traktor in uso**

Questo mi aiuterà a identificare il problema esatto e fornire una soluzione mirata.