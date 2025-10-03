# 🎛️ Guida Setup MIDI per DJ AI System

## ✅ Prerequisiti MIDI Test

Per utilizzare il **Test MIDI** nella GUI e la comunicazione con Traktor Pro, devi configurare:

### 1. 🔧 **macOS IAC Driver Setup**

**Passo 1**: Apri **Audio MIDI Setup**
```bash
# Trovalo in: Applicazioni > Utilità > Audio MIDI Setup
# Oppure usa Spotlight: CMD+Space e cerca "Audio MIDI Setup"
```

**Passo 2**: Mostra MIDI Studio
- Menu: `Finestra` > `Mostra MIDI Studio`
- Oppure: `CMD+2`

**Passo 3**: Configura IAC Driver
- Fai doppio click su **"IAC Driver"**
- ✅ Spunta: **"Il dispositivo è online"**
- Verifica che esista **"Bus 1"** (dovrebbe essere già presente)
- Se non c'è, clicca **"+"** per aggiungere un bus

**Passo 4**: Conferma Setup
- Chiudi la finestra di configurazione
- L'IAC Driver dovrebbe ora apparire come dispositivo MIDI disponibile

### 2. 🎧 **Traktor Pro 3 Setup**

**Passo 1**: Apri Traktor Pro 3

**Passo 2**: Vai in Controller Manager
- Menu: `Help` > `Controller Manager`

**Passo 3**: Importa Mapping AI DJ
- Clicca **"Import"**
- Seleziona: `traktor/AI_DJ_Complete.tsi`
- Conferma importazione

**Passo 4**: Configura Device
- Device: **"Generic MIDI"**
- In Port: **"Bus 1"** (IAC Driver)
- Out Port: **"Bus 1"** (IAC Driver)

**Passo 5**: Attiva Mapping
- ✅ Spunta il mapping **"AI_DJ_Complete"**
- Clicca **"Close"**

### 3. 🧪 **Test Connessione**

**Nel DJ AI System GUI:**
1. Avvia il sistema: `python3 dj_ai.py`
2. Clicca **"🎛️ Test MIDI"**
3. Verifica che:
   - Status cambi in "🟡 MIDI: Testing..."
   - Vengano inviati 5 segnali ogni 3 secondi
   - **L'icona MIDI in Traktor lampeggi** 🔴⚡
   - Status finale: "✅ MIDI: Test completato!"

### 4. ❌ **Troubleshooting**

**"❌ MIDI: Connessione fallita"**
- ✅ Verifica che IAC Driver sia online
- ✅ Verifica che Traktor sia aperto
- ✅ Verifica che il mapping sia attivo
- ✅ Riavvia Traktor se necessario

**"❌ MIDI: Errore test"**
- ✅ Chiudi altre app che usano MIDI
- ✅ Riavvia Audio MIDI Setup
- ✅ Verifica permessi macOS per accesso MIDI

**"L'icona MIDI non lampeggia"**
- ✅ Il mapping potrebbe non essere corretto
- ✅ Verifica che Bus 1 sia selezionato in Traktor
- ✅ Prova a re-importare il file .tsi

### 5. 🎯 **Test Completo**

Una volta che il test MIDI funziona:
1. **Avvia DJ AI**: Compila venue/evento e clicca "🚀 AVVIA DJ AI"
2. **Chat con AI**: Inizia a chattare per decisioni di mixing
3. **Controlli manuali**: Usa slider e bottoni per override
4. **Monitoring**: Osserva status bar per latenza e modello AI

---

## 📞 **Supporto**

Se hai problemi:
1. Verifica che tutti i passaggi siano stati seguiti
2. Riavvia Traktor Pro 3
3. Riavvia DJ AI System
4. Controlla log nella GUI per errori specifici

**🎵 Buon mixing!** 🚀
