# **TRAKTOR PRO 3.1 \- Guida Completa per Agente AI DJ**

## **INDICE**

1. [Architettura del Sistema](https://claude.ai/chat/5295a8c5-8402-404b-8773-86db460f137d#architettura)  
2. [Componenti Interfaccia](https://claude.ai/chat/5295a8c5-8402-404b-8773-86db460f137d#componenti)  
3. [Deck e Controlli](https://claude.ai/chat/5295a8c5-8402-404b-8773-86db460f137d#deck)  
4. [Mixer e Routing Audio](https://claude.ai/chat/5295a8c5-8402-404b-8773-86db460f137d#mixer)  
5. [Sincronizzazione e Beatgrid](https://claude.ai/chat/5295a8c5-8402-404b-8773-86db460f137d#sync)  
6. [Effetti (FX)](https://claude.ai/chat/5295a8c5-8402-404b-8773-86db460f137d#effetti)  
7. [Browser e Gestione Tracce](https://claude.ai/chat/5295a8c5-8402-404b-8773-86db460f137d#browser)  
8. [Workflow DJ Operativo](https://claude.ai/chat/5295a8c5-8402-404b-8773-86db460f137d#workflow)  
9. [Comandi MIDI Mappabili](https://claude.ai/chat/5295a8c5-8402-404b-8773-86db460f137d#midi)  
10. [Configurazioni e Preferenze](https://claude.ai/chat/5295a8c5-8402-404b-8773-86db460f137d#preferenze)

---

## **1\. ARCHITETTURA DEL SISTEMA {\#architettura}**

### **1.1 Componenti Principali**

TRAKTOR PRO 3.1  
├── Application Menu Bar (File, View, Help)  
├── Header (controlli globali, layout, preferences)  
├── Global Section (FX Units, Master Control, Recorders)  
├── Decks (A, B, C, D)  
├── Mixer (4 canali \+ crossfader)  
└── Browser (Track Collection, Playlists, Explorer)

### **1.2 Tipi di Deck Disponibili**

* **Track Deck**: riproduzione tracce standard  
* **STEM Deck**: controllo 4 elementi musicali separati (.stem.mp4)  
* **Remix Deck**: 4 slot per sample/loop (fino 64 sample per set)  
* **Live Input**: ingresso audio esterno

### **1.3 Mixing Modes**

* **Internal Mixing**: usa mixer integrato TRAKTOR  
* **External Mixing**: usa mixer esterno (bypass mixer interno)

---

## **2\. COMPONENTI INTERFACCIA {\#componenti}**

### **2.1 Header**

Elementi:  
\- TRAKTOR Logo (about screen)  
\- MIDI indicator (segnale MIDI/NHL in ingresso)  
\- Connection indicator (stato controller: blu=tutti, arancio=alcuni, off=nessuno)  
\- Audio indicator (blu=connesso, rosso=no interface, arancio=soundcard interna)  
\- LOAD indicator (carico CPU per audio buffer)  
\- Master Output level meter  
\- System Clock (ora di sistema)  
\- Battery indicator (stato batteria computer)  
\- Recording indicator (rosso=recording attivo)  
\- Layout selector (menu layout)  
\- Maximize Browser button  
\- Preferences button  
\- Cruise Mode button (mixing automatico)  
\- Tooltip button (abilita tooltip)  
\- Fullscreen button  
\- NI Logo

### **2.2 Global Section**

#### **Master Control Panel**

Controlli:  
\- SNAP: abilita snap mode (cue/loop su beat più vicino)  
\- MASTER CLOCK TEMPO display (BPM attuale e offset)  
\- MAIN knob (volume master output)  
\- LIMITER: abilita limiter su master  
\- MASTER: Deck come Tempo Master  
\- AUTO: assegnazione automatica Tempo Master  
\- LINK/EXT: sync Ableton Link o MIDI Clock  
\- QUANT: abilita quantize mode (jump senza perdere sync)

Controlli Aggiuntivi (hover su MASTER CLOCK):  
\- TAP button (tap tempo)  
\- Bend buttons (±tempo momentaneo)  
\- Tempo Up/Down (±step-wise)  
\- Metronome tick (click metronomo)

Se MIDI Clock abilitato:  
\- Offset display  
\- MASTER CLOCK START (enable/disable MIDI Clock)  
\- MASTER CLOCK SYNC (reset slave esterni)

#### **FX Units (1-4, default 2 attivi)**

Modalità:  
1\. SINGLE FX MODE (controllo completo 1 effetto)  
   \- D/W knob (dry/wet mix)  
   \- FX Selector  
   \- 3x Parameter knobs  
   \- 2x FX buttons (funzioni specifiche effetto)  
   \- RST button (reset parametri)  
   \- FX On button

2\. GROUP FX MODE (catena 3 effetti)  
   \- D/W knob (dry/wet totale)  
   \- 3x FX Selector  
   \- 3x Amount knob  
   \- 3x Effect On button  
   \- FX On button

Routing:  
\- Insert (default): FX prima channel filter  
\- Send: FX indipendente da signal flow (richiede input/output esterni)  
\- Post Fader: FX dopo volume fader (solo Internal Mixing)

#### **AUDIO RECORDER**

Controlli:  
\- Broadcast button (streaming)  
\- Display (dimensione file \+ tempo)  
\- CUT button (salva e inizia nuovo file)  
\- Recording meter (livello recording)  
\- Record GAIN knob  
\- Record button (start/stop \+ save)

Configurazione (Preferences \> Mix Recorder):  
\- Source: Internal/External  
\- Directory: percorso salvataggio  
\- Prefix: prefisso nome file  
\- Split File at Size: max 2048 MB

#### **LOOP RECORDER**

Controlli:  
\- DRY/WET knob (ratio main/recorded)  
\- Progress bar (lunghezza recording)  
\- SIZE button (lunghezza iniziale)  
\- Delete/Undo/Redo  
\- Play button  
\- Record button  
\- Source drop-down (Deck A/B/C/D, Main, EXT, AUX)

---

## **3\. DECK E CONTROLLI {\#deck}**

### **3.1 Controlli Comuni (tutti i Deck)**

#### **Deck Header**

Informazioni Display:  
\- Cover artwork  
\- Track title  
\- Artist name  
\- Album title  
\- Track time (elapsed)  
\- Remaining time  
\- Current tempo (BPM)  
\- Tempo fader position (%)  
\- Base tempo

Remix Deck aggiunge:  
\- Quantize value selector  
\- Quantize enable dot  
\- Tempo (modificabile)  
\- Capture source  
\- Beat count

#### **Synchronization Controls**

\- SYNC button: sincronizza a Tempo Master  
\- MASTER button: imposta Deck come Tempo Master  
\- Phase meter: offset beat (per sync manuale)  
\- Tempo bend buttons (± momentaneo)  
\- Tempo fader: ±2% a ±100% (configurabile)

#### **Transport Controls**

Playback Normale:  
\- Play/Pause  
\- CUE (set/jump Floating Cue Point)  
\- CUP (Cue/Play): jump \+ play on release  
\- Flux Mode: timeline virtuale continua durante loop/cue  
\- Reverse Mode: playback invertito

Scratch Control (Timecode):  
\- Relative Mode button  
\- Absolute Mode button

#### **Loop Controls**

\- Loop Size control (1/32 a 32 beats)  
\- Arrow buttons (scorrimento valori loop)  
\- Loop In button (set start point)  
\- Loop Out button (set end point)  
\- ACTIVE button (enable/disable loop)

Visualizzazione:  
\- Active loop evidenziata verde in Waveform/Stripe

### **3.2 Track Deck**

#### **Waveform Display**

Caratteristiche:  
\- Colori: chiaro=alte freq, scuro=basse freq  
\- Beatgrid markers visibili  
\- Zoom controls (+ \- \=)  
\- Playhead position configurabile (0-100%)

Color Modes:  
\- Ultraviolet  
\- Infrared  
\- X-Ray  
\- Spectrum

#### **Stripe View**

Funzioni:  
\- Overview intera traccia  
\- Tutti cue/loop markers  
\- Click per jump  
\- Keylock toggle  
\- Flash rosso \= Track End Warning

### **3.3 STEM Deck**

#### **Multi-Track Waveform**

4 STEM Channels, ognuno con:  
\- Volume control  
\- Filter On/Off \+ Amount knob  
\- FX Send On/Off \+ Amount knob  
\- Waveform individuale \+ Beatgrid  
\- STEM Part name

Requisiti:  
\- File .stem.mp4  
\- Analisi OBBLIGATORIA pre-caricamento

### **3.4 Remix Deck**

#### **Sample Slot (4 per deck)**

Componenti:  
\- Sample name  
\- Slot Player (waveform \+ playhead rosso)  
\- Volume control  
\- Filter control (LP/HP)  
\- Sample Cell (container)  
\- Play Type indicator (Loop/One-shot)  
\- Page Selector (1-4, tot 16 sample per page \= 64 max)

Hover Controls:  
\- Keylock button  
\- FX button (routing a FX Unit)  
\- Monitor button (routing a cue channel)  
\- Punch mode (posizione fissa a timeline)  
\- Mute button

#### **Sample Grid**

Struttura:  
\- 4 colonne × 16 righe \= 64 Sample Cells totali  
\- 4 pagine × 16 sample  
\- Organizzazione: Remix Set (.trak file)

### **3.5 Advanced Panel**

#### **CUE Page (Track/STEM Deck)**

Controlli:  
\- 8 Hotcue buttons (cue points o loop in points)  
\- Prev/Next Cue (skip tra cue points)  
\- Cue Point Position (min:sec:ms)  
\- Cue Point List (selezione)  
\- Cue Point Type menu (6 tipi)  
\- Delete Cue Point  
\- MAP button (remap hotcue)  
\- STORE button (salva \+ assign next free hotcue)

Cue Point Types:  
1\. Floating Cue Point (bianco)  
2\. Cue Point (blu)  
3\. Load (giallo) \- jump automatico al load  
4\. Fade Out (arancio) \- trigger auto prossima traccia  
5\. Fade In (arancio) \- marker ingresso auto  
6\. Grid/Beatmarker (bianco) \- riferimento beatgrid  
7\. Loop In Point (verde)

#### **MOVE Page**

Controlli:  
\- Move Mode menu (BeatJump, Loop, Loop In, Loop Out)  
\- Move Size control (step size in beats)  
\- LOOP mode (step \= current loop size)  
\- Cue Move BWD/FWD (movimento ±)  
\- FINE mode (step size fine)

#### **GRID Page**

Controlli:  
\- Move Grid BWD/FWD  
\- Analysis Lock button  
\- BPM Edit Display (double-click per edit manuale)  
\- Set Gridmarker (a playback position)  
\- Delete Gridmarker  
\- AUTO Grid (calcola BPM \+ set gridmarker)  
\- TAP (tap BPM, attivo dopo 4° tap)  
\- RESET Gridmarker  
\- BPM x2 / BPM /2  
\- Beat Tick (metronomo audible)  
\- BPM INC/DEC (micro-step)

#### **Advanced Panel \- Remix Deck**

Sample Cell Parameters:  
\- SAMPLE PITCH control (±semitoni)  
\- SAMPLE GAIN control (livello)  
\- BPM x2 / BPM /2  
\- BPM Edit Display  
\- Move Grid Left/Right  
\- Trigger Type (Latch/Gate mode)  
\- Reverse Playback  
\- Play Type (One-Shot/Loop)  
\- Sync Type (On/Off sync a Remix Deck tempo)  
\- BPM Increase/Decrease

---

## **4\. MIXER E ROUTING AUDIO {\#mixer}**

### **4.1 Mixer Channel (4 canali: A, B, C, D)**

Controlli (dall'alto):  
1\. GAIN knob (pre-fader input level)  
   \- GAIN View button (show/hide)  
     
2\. Channel Level Meter (volume \+ clipping indicator)

3\. EQ Section:  
   \- HI knob \+ Kill button  
   \- MID knob \+ Kill button    
   \- LOW knob \+ Kill button  
     
   EQ Types (Preferences):  
   \- Classic (standard 3-band)  
   \- P600 (Japanese mixer model)  
   \- NUO (Spanish mixer model)  
   \- Xone (British mixer, 4-band)  
   \- Z ISO (KONTROL Z2, 24dB/oct slope)  
   \- P800 (recent Japanese model)

4\. Mixer FX:  
   \- Mixer FX On button  
   \- Mixer FX drop-down menu  
   \- Mixer FX Amount knob  
     
   Available Mixer FX:  
   \- Filter (default, non rimovibile, arancio)  
   \- Reverb (rosso)  
   \- Dual Delay (verde)  
   \- Noise (blu)  
   \- Time Gater (giallo)  
   \- Flanger  
   \- Barber Pole  
   \- Dotted Delay  
   \- Modern Krush  
     
   (4 selezionabili contemporaneamente in Preferences)

5\. Channel Fader (volume)

6\. CUE button (routing a headphone cue)

7\. KEY button (lock key)  
   \- KEY knob (±key senza alterare tempo)

8\. FX Assign buttons (4, uno per FX Unit)

9\. PAN knob (balance L/R, visibile se Advanced Panel aperto)

### **4.2 Crossfader Controls**

\- Crossfader (transizione L/R)  
\- Crossfader Assign buttons (L/R per ogni channel)  
\- Fade left/right buttons (step-by-step)  
\- Auto fade left/right buttons (auto movimento)

Configurazione (Preferences):  
\- Auto Crossfade Time: durata auto fade  
\- Smooth/Sharp: curva crossfader

### **4.3 Headphone Cue**

Controlli:  
\- Headphone Cue Vol: ratio cue/master in cuffie  
\- Headphone Cue Mix: volume cue  
\- CUE buttons (per channel, su Mixer channels)

Requisiti:  
\- Audio interface multi-channel  
\- Output Monitor (Internal Mixing) o Output Preview (External Mixing)

### **4.4 AUX Control**

\- Volume control per input AUX  
\- Utilizzo: microfono, turntable, synth esterno  
\- Configurazione: Preferences \> Input Routing \> Input Aux

### **4.5 Auto-Gain e Headroom**

Auto-Gain (Preferences \> Mixer):  
\- Enable Autogain: livellamento automatico tracce  
\- Previene dominanza volume tra tracce

Headroom (Preferences \> Mixer):  
\- None, \-3dB, \-6dB, \-9dB, \-12dB  
\- Riserva pre-clipping per picchi transienti  
\- Apply Headroom to Channel Meters: visualizza su meter

Limiter:  
\- Enable Limiter: previene clipping master  
\- Limiter Types:  
  \* Classic: permette slight digital distortion  
  \* Transparent: compressione meno udibile  
\- Posizione visibile su Master meter (prima LED rossi)

---

## **5\. SINCRONIZZAZIONE E BEATGRID {\#sync}**

### **5.1 Sistema di Sincronizzazione**

#### **Concetti Base**

\- Beatgrid: analisi automatica BPM \+ posizione beat  
\- Tempo Master: riferimento tempo per sync (Deck o Master Clock)  
\- Master Clock: tempo globale di riferimento  
\- AUTO mode: assegnazione automatica Tempo Master

#### **Sync Modes (Preferences \> Transport)**

1\. TEMPOSYNC:  
   \- Solo sincronizzazione tempo  
   \- Fase allineata al click SYNC  
   \- SYNC dim se fase shift manuale  
   \- Tempo sempre sincronizzato

2\. BEATSYNC (raccomandato):  
   \- Sincronizzazione tempo \+ fase  
   \- Fase allineata al click SYNC  
   \- SYNC dim se fase shift (scratch, stop)  
   \- Re-allineamento automatico al rilascio  
   \- RICHIEDE beatgrid corretti

Nota: Re-allineamento rapido \= doppio click SYNC

#### **Auto Master Mode (Preferences \> Transport)**

Opzioni:  
\- Remix Decks can be Tempo Master: On/Off  
\- Only On-Air Decks can be Tempo Master: On/Off  
  \* On: solo Deck udibili possono diventare Master  
  \* Off: qualsiasi Deck playing può diventare Master

Comportamento AUTO:  
1\. Deck synced diventa Master quando Deck Master corrente finisce/stop  
2\. Master Clock diventa Master quando nessun Deck synced rimane  
3\. MASTER button si illumina in Master Control Panel

### **5.2 Ableton Link**

#### **Setup**

Requisiti:  
\- Stessa rete locale (Ethernet/Wi-Fi/Thunderbolt/direct connection)  
\- Preferences \> External Sync \> External Clock Source \= LINK

Connessione:  
1\. Click LINK button (Master Control Panel)  
2\. Join/start Link session  
3\. Moving bar \= global phase (anche se Deck stopped)  
4\. Numero su LINK button \= app connesse

Sincronizzazione Deck:  
\- Master Clock diventa Tempo Master (AUTO disabilitato)  
\- Deck SYNC → sincronizza a Link timeline  
\- Primo partecipante imposta tempo iniziale  
\- Qualsiasi partecipante può modificare tempo dopo

#### **Downbeat Matching**

\- Barra blu sotto LINK button \= fase Link timeline  
\- Release downbeat quando barra vuota  
\- Reset Downbeat function: mapping disponibile  
  (Add In \> Master Clock \> Ableton Link \> Reset Downbeat)

Warning: Reset può causare skip 1-2 beat indietro

### **5.3 MIDI Clock**

#### **Come Slave (ricevere MIDI Clock)**

Setup:  
1\. Preferences \> Controller Manager  
2\. Add \> Generic MIDI  
3\. In-Port \= porta MIDI Clock in ingresso  
4\. Preferences \> External Sync \> External Clock Source \= EXT  
5\. Master Control Panel \> click EXT  
6\. Start su dispositivo master

Offset: regolare su dispositivo master (sending)

#### **Come Master (inviare MIDI Clock)**

Setup:  
1\. Preferences \> Controller Manager \> Generic MIDI  
2\. Out-Port \= porta destinazione  
3\. Preferences \> External Sync \> Enable MIDI Clock  
4\. Master Control Panel \> Start/Stop button (blu quando attivo)

Controlli aggiuntivi:  
\- SYNC button: trigger MIDI Stop \+ Start (re-sync)  
\- Tempo Display: mostra BPM MIDI Clock  
\- Offset: regolazione sync

### **5.4 Correzione Beatgrid**

#### **Procedura**

1\. Load traccia in Deck  
2\. Play  
3\. Advanced Panel \> GRID page  
4\. Beat Tick On (ascolta tick vs beat traccia)

Correzione:  
\- MOVE GRID BWD/FWD: spostamento beatgrid  
\- BPM INC/DEC: compressione/espansione beatgrid (micro-step)

Ricostruzione manuale:  
1\. Delete Beatgrid Marker  
2\. Skip a un beat nella traccia  
3\. Set Beatgrid Marker (crea nuovo beatgrid da posizione)

Alternative:  
\- TAP: tappa tempo manualmente  
\- BPM Edit Display: inserimento manuale BPM  
\- AUTO Grid: ricalcolo automatico (solo tracce già analizzate)  
\- BPM x2 / BPM /2: raddoppio/dimezzamento BPM

#### **Analysis Lock**

\- Analysis Lock button: blocca tutti valori contro:  
  \* Future track analysis  
  \* Modifiche utente  
\- Previene alterazioni accidentali beatgrid corretti

---

## **6\. EFFETTI (FX) {\#effetti}**

### **6.1 FX Units (1-4)**

#### **Configurazione Globale (Preferences \> Effects)**

FX Unit Routing (per ogni FX Unit):  
\- Insert (default): FX pre-channel filter, D/W controlla mix  
\- Send: FX indipendente, richiede Input/Output esterni  
\- Post Fader: FX post-volume fader (solo Internal Mixing)

FX Panel Mode (per ogni FX Unit):  
\- Single: controllo dettagliato 1 effetto  
\- Group: catena 3 effetti

FX Units Available:  
\- 2 FX Units (default): FX1, FX2  
\- 4 FX Units: FX1, FX2, FX3, FX4 (condividono pannelli a coppie)

#### **Assignment**

\- FX Unit On buttons su Mixer channels (4 per channel)  
\- Ogni FX Unit assegnabile a multipli channels contemporaneamente  
\- Routing per Sample Slot (Remix Deck): individuale, richiede enable

#### **Snapshots**

Salvataggio:  
1\. FX Unit number \> context menu  
2\. Save Snapshot  
3\. Parametri salvati richiamati automaticamente al prossimo select effetto

Reset:  
\- Single Mode: RST button (reset all parameters)  
\- Group Mode: double-click su knob individuale

### **6.2 Catalogo Effetti (40 totali)**

#### **Delay Effects**

1\. DELAY (Classic tempo-synced)  
   Single Mode:  
   \- FILTER: carbonized HP/LP (bandpass-like)  
   \- FEEDB: feedback strength  
   \- RATE: delay time (1/32 \- 4/4 bars, 7 values)  
   \- FRZ: freeze (input closed, feedback max)  
   \- SPRD: stereo spread (L/R offset)  
   Group Mode: RATE control a medium feedback

2\. DELAY T3  
   Single Mode:  
   \- FILTER: HP/LP bipolar (center=open)  
   \- FEEDB: feedback strength  
   \- RATE: delay time (4/4 \- 1/32, inverted vs classic)  
   \- FRZ: freeze  
   \- FR.R: free run (non-quantized, continuous)  
   Group Mode: RATE control

3\. TAPE DELAY (Analog emulation)  
   Single Mode:  
   \- FILT: HP filter  
   \- FBK: feedback  
   \- SPEED: tape delay speed  
   \- FRZ: freeze  
   \- ACCL: higher acceleration  
   Group Mode: ACCL control

4\. RAMP DELAY (Transition time)  
   Single Mode:  
   \- FILTER: bipolar LP/HP  
   \- DURATION: ramp length (1/4 \- 16 bars, 7 values)  
   \- RATE: delay speed (4/4 \- 1/32)  
   \- FRZ: freeze  
   \- FB+: feedback a 90%  
   Group Mode: RATE (duration fixed 2 bars)

#### **Reverb Effects**

5\. REVERB (Classic)  
   Single Mode:  
   \- HP: high-pass in loop  
   \- LP: low-pass in loop  
   \- SIZE: room size (small \- vast)  
   \- FRZ: freeze  
   Group Mode: SIZE control

6\. REVERB T3  
   Single Mode: identico a REVERB  
   (versione TRAKTOR 3/SCRATCH)

7\. ICEVERB (Self-oscillating)  
   Single Mode:  
   \- ICING: filter resonance (color intensity)  
   \- COLOR: filter cutoff (reverb color)  
   \- SIZE: room size  
   \- FRZ: freeze (SIZE attivo per pitch effects)  
   Group Mode: SIZE control

#### **Flanger Effects**

8\. FLANGER (Classic tempo-based)  
   Single Mode:  
   \- SPRD: stereo spread (phase offset L/R)  
   \- FEEDB: feedback amount  
   \- RATE: oscillation rate (16 bars \- 1/16, 11 values)  
   \- UP: inverted oscillation direction  
   \- FR.R: free run (30 sec \- 1/30 sec)  
   \- LFO RESET: restart oscillation  
   Group Mode: RATE control (freerun)

9\. FLANGER PULSE (Semi-automatic)  
   Single Mode:  
   \- SHAPE: flanger pulse shape  
   \- FEEDB: feedback strength  
   \- AMNT: modulation amount (bipolar)  
   \- FB-: inverted feedback (uneven harmonics)  
   \- SPR: stereo spread  
   Group Mode: AMNT control

10\. FLANGER FLUX (Manual)  
    Single Mode:  
    \- FEEDB: feedback amount  
    \- PITCH: pitch control (center=neutral)  
    \- FB-: inverted feedback  
    \- SPR: stereo spread  
    Group Mode: PITCH control

#### **Phaser Effects**

11\. PHASER (Classic tempo-based)  
    Single Mode: identico a FLANGER  
    \- SPRD: stereo spread  
    \- FEEDB: feedback  
    \- RATE: oscillation rate  
    \- UP: inverted direction  
    \- FR.R: free run  
    \- LFO RST: reset  
    Group Mode: RATE (freerun)

12\. PHASER PULSE (Auto-controlled)  
    Single Mode:  
    \- SHAPE: phaser pulse shape  
    \- FEEDB: feedback  
    \- AMNT: modulation amount (bipolar)  
    \- 8PL: 6/8 pole switch  
    \- SPRD: stereo spread  
    Group Mode: AMNT control

13\. PHASER FLUX (Manual)  
    Single Mode:  
    \- FEEDB: feedback  
    \- PITCH: pitch (center=neutral)  
    \- 8PL: 6/8 pole switch  
    \- SPR: stereo spread  
    Group Mode: PITCH control

#### **Filter Effects**

14\. FILTER LFO (Ladder architecture)  
    Single Mode:  
    \- D/RNG: dry-range combination  
    \- SHAPE: LFO shape (triangle \- sawtooth)  
    \- RES: resonance  
    \- RATE: filter oscillation (16 bars \- 1/16)  
    \- UP: inverted direction  
    \- FR.R: free run  
    Group Mode: RATE (freerun)

15\. FILTER PULSE (Auto-controlled)  
    Single Mode:  
    \- SOFTEN: cutoff envelope smoothness  
    \- RES: resonance  
    \- AMT: modulation frequency (bipolar, center=neutral)  
    \- P.SN: peak sensitivity (50%-80%)  
    \- P.MD: enable peak mode  
    Group Mode: AMNT control

16\. FILTER (Classic 2-knob)  
    Single Mode:  
    \- HP: high-pass cutoff (left=bypass)  
    \- RES: resonance  
    \- LP: low-pass cutoff (right=bypass)  
    \- BRJ: band reject mode  
    \- DJM: DJ mode (1-knob bipolar)  
    Group Mode: LP/HP bipolar control

17\. FILTER:92 LFO (Xone:92 model)  
    Single Mode: identico a FILTER LFO  
    \- D/RNG, SHAPE, RES, RATE, UP, FR.R

18\. FILTER:92 PULSE (Xone:92 model)  
    Single Mode: identico a FILTER PULSE  
    \- SOFTEN, RES, AMT, P.SN, P.MD

19\. FORMANT FILTER (Vowel imitation)  
    Single Mode:  
    \- SHARP: vowel presence  
    \- TALK: formant morph (a,e,i,o,u, dark-bright)  
    \- TYP: German/English sound  
    Group Mode: TALK control

20\. PEAK FILTER (Frequency peak)  
    Single Mode:  
    \- D/W: mix \+ filter frequency increase  
    \- PUMP: brickwall limitation  
    \- EDGE: peak width (resonance)  
    \- FREQ: emphasized frequency  
    \- KILL: invert peak (notch filter)  
    Group Mode: FREQ control

#### **Gater/Slicer Effects**

21\. GATER (Rhythmic muting)  
    Single Mode:  
    \- NOISE: hissing noise amount  
    \- SHAPE: gate shape (hold/decay %)  
    \- RATE: gater rate (Off, 1/4, 1/8, 1/16, 1/32)  
    \- MTE: mute music (solo noise)  
    \- STT: stutter (3/16 gate, override RATE)  
    Group Mode: RATE control  
      
    Nota: richiede beatgrid accurati \+ Auto Mode

22\. BEATMASHER 2 (Buffer-based)  
    Single Mode:  
    \- ON: sample 1 bar audio (re-sample \= off/on)  
    \- GATE: mix/gate sampled material (bipolar)  
    \- ROT: rotate sample (1/8 note steps)  
    \- LEN: playback length  
    \- WRP: re-sync ogni bar  
    \- REV: reverse playback  
    Group Mode: LEN control

23\. BEATSLICER BUFFER  
    Single Mode:  
    \- BUZZ: beat-roll effect (repetition rate)  
    \- STYLE: pattern group (1-5)  
    \- PAT: pattern dentro gruppo (first=bypass)  
    \- GO: buffer \+ manipulate (1 bar loop)  
    \- 2 BAR: usa 2 bars per slicing  
    Group Mode: PAT control

#### **Grain/Pitch Effects**

24\. REVERSE GRAIN (Backward loop)  
    Single Mode:  
    \- ON: sample \+ play backward  
    \- PITCH: pitch control (0-100)  
    \- GRAIN: grain size  
    \- SPEED: grain playback speed  
    \- INV: reverse grain order  
    \- FWD: forward playback  
    Group Mode: GRAIN control

25\. TRANSPOSE STRETCH (Pitch-shifter)  
    Single Mode:  
    \- STRCH: time stretch (full left=input open)  
    \- GRNSZ: grain size (333ms \- 5ms, richiede GRN On)  
    \- KEY: pitch (center=neutral, ±octaves)  
    \- GRN: enable grain size control  
    \- ST.2: 2 bars instead 1 bar in stretch mode  
    Group Mode: KEY control  
      
    Nota: caricare con STRCH full left\!

#### **Distortion/Modulation Effects**

26\. RING MODULATOR  
    Single Mode:  
    \- AM-RM: morph AM-RM (soft-harsh)  
    \- RAW: oscillator shape (sine-square)  
    \- PITCH: modulation frequency (100Hz \- 8371Hz)  
    Group Mode: RAW \+ PITCH combination

27\. DIGITAL LOFI (Bit/Sample reduction)  
    Single Mode:  
    \- BIT: bit rate reduction  
    \- SMTH: sample rate smooth (lag)  
    \- SRTE: sample rate reduction (100Hz min)  
    \- SPREAD: stereo offset  
    Group Mode: SRTE \+ BIT combination  
      
    Nota: SRTE richiede SMTH attivo

28\. MULHOLLAND DRIVE (Overdrive)  
    Single Mode:  
    \- TONE: feedback tone frequency  
    \- FEEDB: feedback amount (0% \= tube distortion)  
    \- DRIVE: overdrive unit select (bipolar morph)  
    \- FB-: inverted feedback (uneven harmonics)  
    Group Mode: DRIVE control  
      
    Warning: high DRIVE+FEEDB \= suono senza input

#### **Turntable/Bouncer Effects**

29\. TURNTABLE FX  
    Single Mode:  
    \- BRK: brake effect (velocità B.SPD)  
    \- AMNT: rocking motion amount  
    \- R.SPD: rocking speed  
    \- B.SPD: braking speed (wind down/up time)  
    \- RCK: trigger rocking  
    \- REW: rewind effect  
    Group Mode: BRK \+ B.SPD

30\. AUTO BOUNCER (Pattern-based)  
    Single Mode:  
    \- TRANS: transposition pattern (bipolar)  
    \- BEND: speed increase/decrease pattern (bipolar)  
    \- PATTERN: 5 patterns (0-4)  
    \- X2: double density  
    \- ALT: alternative patterns 0-4  
    Group Mode: BEND control

31\. BOUNCER (Manual)  
    Single Mode:  
    \- TRANS: transposition repetitions (bipolar)  
    \- FILTER: low-pass (right=open)  
    \- SPEED: repetition speed  
    \- AUT: re-sample every 2 beats  
    \- X2: double speed  
    Group Mode: SPEED control

### **6.3 Mixer FX (1-Knob Effects)**

Caratteristiche:  
\- 1 knob per channel (Mixer FX Amount)  
\- Pre-selezione 4 su 8 disponibili (Preferences \> Mixer)  
\- Filter sempre presente (non rimovibile, arancio)

Available Mixer FX:  
1\. Filter (default, arancio)  
   \- Bipolar: center=bypass  
   \- Left: low-pass (taglia alte freq)  
   \- Right: high-pass (taglia basse freq)

2\. Reverb (rosso)  
   \- Room size control

3\. Dual Delay (verde)  
   \- Dual delay lines

4\. Noise (blu)  
   \- Noise injection

5\. Time Gater (giallo)  
   \- Tempo-synced gating

6\. Flanger  
   \- Flanging effect

7\. Barber Pole  
   \- Endless pitch rise/fall

8\. Dotted Delay  
   \- Dotted rhythm delay

9\. Modern Krush (Crush)  
   \- Bit crushing

Controlli:  
\- Mixer FX On button (channel)  
\- Mixer FX drop-down menu (select FX)  
\- Mixer FX Amount knob (effect amount)  
\- Pointer color \= selected FX

---

## **7\. BROWSER E GESTIONE TRACCE {\#browser}**

### **7.1 Componenti Browser**

Struttura:  
├── Preview Player (preview pre-load)  
├── Search field (live search basata su tag)  
├── Browser Tree (folders/playlists)  
│   ├── Track Collection (Artist, Release, Label, Genre)  
│   ├── Playlists (user playlists)  
│   ├── Explorer (filesystem \+ Archive/History)  
│   ├── Audio Recordings (file AUDIO RECORDER)  
│   ├── iTunes (libreria \+ playlists iTunes)  
│   └── History (history playlists recenti)  
├── Cover Artwork display  
├── Status bar (progress, errors, status)  
├── Track List (tracks con metadata table)  
└── Favorites (accesso rapido playlists/folders)

### **7.2 Track Collection**

#### **Formati Audio Supportati**

Compatibili:  
\- MP3  
\- M4A (AAC, NO DRM)  
\- WAV  
\- AIFF  
\- FLAC  
\- OGG Vorbis

Non Supportati:  
\- WMA  
\- DRM-protected files (iTunes acquisti protetti)

#### **Import Methods**

1\. Drag & Drop:  
   \- Drag files → Track Collection folder  
   \- Analisi metadata automatica

2\. Import Music Folders:  
   \- Right-click Track Collection \> Import Music Folders  
   \- Import da cartella musica locale OS

3\. Add Music from Other Folders:  
   \- Preferences \> File Management \> Music Folders \> Add  
   \- Subfolders incluse automaticamente

4\. iTunes Import:  
   \- iTunes folder \> select tracks  
   \- Right-click \> Import to Collection  
   \- Options: as Tracks, as Looped Samples, as One-Shot-Samples

5\. Remix Sets Import:  
   \- Drag .trak file → All Remix Sets folder

#### **Track Status Icons**

\- A, B, C, D: currently loaded in Deck  
\- Checkmark: already played  
\- Exclamation: not found (moved/renamed/unavailable)  
\- Lock: locked Beatgrid  
\- Triangle (History only): played (preview not marked)

Sort by Status:  
1\. Already played (top)  
2\. Currently playing (center)  
3\. Unplayed (below)  
4\. Missing (bottom)

### **7.3 Track Analysis**

#### **Automatic Analysis**

Trigger Conditions (Preferences \> File Management):  
\- Import: Analyze new imported tracks  
\- On Load: Analyze new tracks when loading into deck  
\- Manual: no auto analysis

Generated Data:  
\- BPM (tempo)  
\- Beatgrid (beat positions)  
\- Key (musical key)  
\- Waveform (visual representation)  
\- Stripe (overview)  
\- Auto-Gain value

STEM Files:  
\- OBBLIGATORIA analisi pre-load  
\- Non caricabili se non analizzati

#### **Manual Analysis**

Procedura:  
1\. Right-click track(s)/Playlist \> Analyze (Async)  
2\. Select options:  
     
   ALL mode:  
   \- Usa impostazioni default (Preferences \> Analyze Options)  
   \- Locked tracks: NO overwrite BPM/Beatgrid/Gain/Key  
     
   SPECIAL mode:  
   \- BPM: calcola tempo  
     \* BPM Range: Automatic, o range specifico (migliore accuratezza)  
   \- Set Beatgrid: crea beatgrid \+ align downbeat  
   \- Key: rileva chiave musicale  
   \- Gain: sostituisce con Auto-Gain value  
   \- Replace Locked Values: overwrite locked tracks  
   \- Parallel Processing: analisi parallela (high CPU load)

3\. Click OK

Nota: Parallel Processing \= NO usare in live session

#### **Analysis Options (Preferences \> Analyze Options)**

BPM Detection:  
\- BPM Range: min-max BPM o Automatic  
  \* Automatic: AI per correct tempo \+ downbeat  
  \* Range specifico: migliore accuratezza genere omogeneo  
\- Set Beatgrid when detecting BPM: auto beatgrid \+ downbeat align  
\- Store Beatmarker as Hotcue: beatmarker usabile come hotcue

Musical Key:  
\- Displayed in Traktor: notazione display  
  \* Musical  
  \* Musical (all sharps)  
  \* Open Key  
\- Written to File Tags: notazione metadata file  
  \* Musical  
  \* Musical (all sharps)  
  \* Open Key  
  \* Key Text

### **7.4 Metadata Editing**

#### **Inline Editing (Track List)**

Procedura:  
1\. Select track  
2\. Click campo metadata (es. artist)  
3\. Edit  
4\. Enter (confirm) o Esc (abort)

Note:  
\- Disable: Preferences \> Browser Details \> Allow Inline Editing (OFF)  
\- iTunes users: edit solo in iTunes (raccomandato)

#### **Edit Dialog (Full Properties)**

Apertura:  
\- Right-click track(s) \> Edit

Single Track:  
1\. Edit campi individuali  
2\. Drop-down menu \= tag precedenti salvati  
3\. Apply/OK (confirm), Restore (undo), Cancel (abort)

Multiple Tracks:  
\- Checkbox checked \= valore condiviso (will overwrite)  
\- Checkbox unchecked \= valori diversi  
\- Previous/Next buttons \= edit individuale  
\- Apply/OK per salvare

Available Fields:  
\- Artist, Title, Album, BPM, Genre, Label, Comment, etc.

#### **Cover Artwork Management**

Import:  
1\. Right-click track(s) \> Import Cover  
2\. Select .jpeg file  
3\. Confirm (stored in track file)

Delete:  
1\. Right-click track(s) \> Delete Cover

### **7.5 Playlists**

#### **Creating Playlists**

Method 1 \- Empty Playlist:  
1\. Right-click Playlists folder \> Create Playlist  
2\. Enter name  
3\. OK

Method 2 \- From Selected Tracks:  
1\. Select tracks in Track List  
2\. Drag to Playlists folder  
3\. Enter name  
4\. OK

#### **Adding Tracks**

\- Drag tracks → Playlist (append end)  
\- Drag tracks → Track List position (insert at orange line)

#### **Sorting**

By Original Order:  
\- Click \#-column header

By Category:  
\- Click column header (second click \= invert order)  
\- Resets a original order al restart TRAKTOR  
\- Consolidate: right-click Playlist \> Consolidate (make permanent)

Change Original Order:  
1\. Sort by \# (original order)  
2\. Drag track(s) up/down (orange line \= drop position)

#### **Playlist Folders**

Create:  
1\. Right-click Playlist folder \> Create Folder  
2\. Enter name  
3\. OK  
4\. Drag playlists to folder

#### **Playlist Operations**

Export:  
\- Right-click Playlist \> Export Playlist  
\- Crea folder con tracce \+ .nml file

Import:  
\- Method 1: Right-click Playlists \> Import Playlist  
\- Method 2: Drag .nml file → Playlists folder

Import iTunes Playlist:  
1\. iTunes folder \> right-click playlist  
2\. Import to Playlists  
3\. Enter name  
4\. OK

Rename:  
\- Right-click Playlist \> Rename

Delete:  
\- Right-click Playlist \> Delete Playlist

Remove Duplicates:  
\- Right-click Playlist \> Remove Duplicates

Clear:  
\- Right-click Playlist \> Clear Playlist (remove all tracks)

Save as Webpage:  
1\. Right-click Playlist \> Save as Webpage  
2\. Enter name \+ destination  
3\. Select columns (List Options)  
4\. OK (creates HTML file)

Search in Playlists:  
\- Right-click track(s) \> Search in Playlists  
\- Report shows all playlists containing track(s)

#### **Special Playlists**

Preparation Playlist:  
\- Right-click Playlist \> Select as Preparation List  
\- Icon changes to preparation icon  
\- Add tracks: Right-click track \> Append/Add as Next to Preparation  
\- Track shows diamond icon

History Playlists:  
\- Auto-created ogni sessione  
\- Stored: Explorer \> Archive folder  
\- Location: Documents/Native Instruments/Traktor/History (Win)  
            Users/\~/Native Instruments/Traktor/History (Mac)  
\- Labeled: date \+ time  
\- Additional columns: Start-Time, Duration, Deck

### **7.6 Track Collection Maintenance**

#### **Consistency Check**

Esecuzione:  
\- Right-click Track Collection \> Check Consistency  
\- Auto at startup: Preferences \> File Management \> Show Consistency Check Report on Startup

Report Tabs:  
1\. Overview:  
   \- Total Tracks  
   \- Tracks Missing  
   \- Tracks Not Analyzed  
   \- Tracks Missing Stripe  
   \- Total Tracks To Analyze

2\. Missing Tracks:  
   \- Lista tracce mancanti

3\. Tracks To Analyze:  
   \- Lista tracce da (ri)analizzare

Actions:  
\- Relocate: apre Relocate dialog  
\- Remove Missing: rimuove riferimenti tracce non esistenti  
\- Analyze: avvia analisi tracce pendenti

#### **Relocate Missing Tracks**

Procedura:  
1\. Right-click track(s) \> Relocate  
2\. Navigate a destinazione (top-level folder per multiple)  
3\. Confirm

#### **Delete from Collection**

1\. Right-click track(s) \> Delete from Collection  
2\. Options:  
   \- delete from collection: solo da Collection \+ Playlists  
   \- additionally remove TRAKTOR tags: \+ rimuovi tags TRAKTOR da file  
   \- additionally delete file(s) from hard drive: \+ elimina file

#### **Backup & Restore**

Save Collection:  
\- Right-click Track Collection \> Save Collection  
\- Auto-save: ogni chiusura TRAKTOR

Export Collection:  
1\. Right-click Track Collection \> Export the Collection  
2\. Enter title (mantieni $ iniziale)  
3\. Destination path  
4\. Export Format  
5\. Copy Tracks To Destination: ON  
6\. OK

Restore from Backup:  
1\. Right-click Track Collection \> Import another Collection  
2\. Navigate: Backup \> Collection folder  
3\. Select backup version  
4\. OK

Clear Collection:  
1\. Right-click Track Collection \> Clear Collection  
2\. Options:  
   \- clear collection  
   \- additionally remove Traktor tags  
   \- additionally delete file(s) from hard drive

### **7.7 Favorites**

Pre-Assigned:  
\- Preparation  
\- History  
\- Track Collection  
\- All Tracks  
\- All Remix Sets  
\- Demo Tracks  
\- Demo Remix Sets

Assign Custom:  
\- Drag folder/playlist → free Favorite slot

### **7.8 Preview Player**

Requisiti:  
\- Output Preview (External Mixing) o Output Monitor (Internal Mixing)  
\- Preferences \> Input/Output Routing

Usage:  
1\. Drag track → Preview Player  
2\. Click play button  
3\. Click Stripe per skip  
4\. Click play per stop

Features:  
\- NO load/play state change  
\- NO play count increment

---

## **8\. WORKFLOW DJ OPERATIVO {\#workflow}**

### **8.1 Workflow Base**

1\. IMPORT MUSIC  
   → Drag files to Track Collection  
   → Auto metadata analysis

2\. BROWSE MUSIC  
   → Navigate Browser Tree  
   → Text search in Search field  
   → Preview in Preview Player

3\. LOAD TRACKS  
   → Drag to Deck o Right-click \> Load into Deck  
   → Auto analysis: BPM, Beatgrid, Waveform

4\. START PLAYBACK  
   → Adjust Mixer controls  
   → Set crossfader position  
   → Click Play button

5\. LOAD NEXT TRACK  
   → Browse mentre track playing  
   → Load in opposite Deck

6\. SYNC TRACKS  
   → Click SYNC button su stopped Deck  
   → Beats match automatically

7\. PREVIEW TRANSITION  
   → CUE button su Mixer channel  
   → VOL/MIX knobs per headphone balance  
   → Find right position

8\. MIX  
   → EQ adjustments (take out bass next track)  
   → Apply FX se necessario  
   → Crossfade transition

9\. CUE POINTS  
   → Create/store on Hotcue buttons  
   → Instant jump to stored positions

10\. LOOP  
    → Enable loops (predefined sizes)  
    → Store on Hotcue buttons  
    → Extend/shorten transitions

11\. REMIX (optional)  
    → STEM Decks: control individual elements  
    → Remix Decks: trigger samples/loops

### **8.2 Mixing Your First Two Tracks**

#### **Prerequisites Setup**

1\. Crossfader → left-most position  
2\. Mixer channel A → assign left crossfader  
3\. Mixer channel B → assign right crossfader  
4\. Channel fader A → maximum  
5\. Channel fader B → maximum  
6\. MAIN knob → center (0.0 dB)  
7\. Amplification system volume → minimum

#### **Execution Steps**

1\. LOAD FIRST TRACK (Deck A)  
   \- Browse Track Collection  
   \- Drag track → Deck A  
   \- Auto analysis: BPM \+ Beatgrid \+ Waveform

2\. START PLAYBACK (Deck A)  
   \- Click Play button  
   \- Waveform moves  
   \- Channel \+ Master meters illuminate  
   \- Slowly increase amplification volume

3\. LOAD SECOND TRACK (Deck B)  
   \- Browse similar tempo track  
   \- Drag track → Deck B  
   \- Auto analysis

4\. SYNC TEMPOS  
   \- Click SYNC button (Deck B)  
   \- Equal tempo in Deck Headers  
   \- Tempo fader B moves automatically  
   \- SYNC button lights up

5\. START PLAYBACK (Deck B)  
   \- When Deck A almost over  
   \- Click Play button (Deck B)  
   \- Waveform moves  
   \- Channel B meter illuminates  
   \- Beat-accurate sync

6\. MIX IN SIGNAL  
   \- Drag crossfader toward center (hold moment)  
   \- Deck B audio fades in  
   \- Move crossfader to right-most position  
   \- Deck A audio fades out  
     
   Alternative:  
   \- Fade left/right buttons (step-wise)  
   \- Autofade buttons (automatic)

7\. REPEAT  
   \- Deck B \= new Tempo Master (AUTO mode)  
   \- Load next track → Deck A  
   \- Repeat process

### **8.3 EQing During Transition**

Common Technique \- Bass Swap:

Before Transition:  
1\. LOW knob (Deck B) → minimum (take out bass)

During Transition:  
2\. Crossfader → move left to center  
   \- Both tracks audible  
   \- Deck B no bass

3\. LOW knobs:  
   \- Deck B → gradually increase  
   \- Deck A → gradually decrease  
   \- Both tracks audible  
   \- Deck A no bass

4\. Crossfader → complete to right  
   \- Only Deck B audible

Alternative:  
\- EQ Kill buttons per immediate kill/restore frequency bands

Benefits:  
\- Prevent clipping (two full volume tracks together)  
\- Smoother transitions  
\- Better frequency management

### **8.4 Using Cue Channel**

Setup:  
1\. Switch Layout → Mixer (see cue controls \+ CUE buttons)

Preview Next Track:  
1\. CUE button (next track Mixer channel) → click  
   \- Button lights up  
   \- Signal → headphone cue channel

2\. VOL knob → adjust cue volume (moderate level)

3\. MIX knob → adjust balance  
   \- Counter-clockwise: more cued track  
   \- Clockwise: more main mix

Find Transition Point:  
\- Preview next track in headphones  
\- Find right position  
\- Fade in using crossfader

Requirements:  
\- Multi-channel audio interface  
\- Output Monitor (Internal) o Output Preview (External)  
\- Configured in Preferences \> Output Routing

### **8.5 Hotcues and Loops**

#### **Storing Cue Points**

1\. Open Advanced Panel (click button)  
2\. Select CUE page  
3\. Playback/scroll to position  
4\. Click Hotcue button (empty)  
   → Cue Point stored  
   → Button lights blue

#### **Storing Loops**

1\. Playback/scroll to position  
2\. Activate Loop (desired size)  
3\. Click Hotcue button (empty)  
   → Loop stored  
   → Button lights green

#### **Triggering Hotcues**

Deck Playing:  
\- Click Hotcue → jump \+ continue playback

Deck Stopped:  
\- Click & hold Hotcue → jump \+ play while held  
\- Release → jump back \+ pause

#### **Remapping Hotcues**

1\. Click Hotcue (to remap)  
2\. Click MAP button (enable MAP mode)  
3\. Click target Hotcue button  
   → Cue/Loop mapped to new button  
   → Original button empty

#### **Flux Mode**

Function:  
\- Virtual playhead continua durante loop/cue  
\- Release \= jump avanti a posizione "virtuale"  
\- Prevents losing phrasing

Enable:  
\- Click Flux Mode button

Visualization:  
\- Green playhead in Waveform  
\- Flux Mode indicator flash in Deck Header

Usage:  
1\. Enable Flux Mode  
2\. Trigger Hotcue/Loop  
3\. Hold while track plays  
4\. Release → jump ahead (quanto tenuto)

#### **Reverse Mode**

Enable:  
\- Click & hold Reverse Mode button  
\- Track plays backward  
\- Release → resume normal

### **8.6 Key Lock**

Function:  
\- Disaccoppia pitch (key) da tempo (BPM)  
\- Permette cambio tempo senza alterare tonalità

Lock at Original Key:  
1\. Load track  
2\. Tempo fader → original position  
3\. KEY button (Stripe) o KEY button (Mixer) → click  
4\. Move tempo fader  
   → Tempo changes, key unchanged

Change Key Without Tempo:  
1\. Load track  
2\. KEY button → click (lock key)  
3\. KEY knob → turn clockwise/counter-clockwise  
   → Key changes, tempo unchanged

### **8.7 Cruise Mode (Auto Mixing)**

Function:  
\- Auto mix tracks one after another  
\- From selected Playlist or Track Collection

Enable:  
1\. Select Playlist or Track Collection  
2\. Load track → Deck  
3\. Click Play  
4\. Click Cruise Mode button (Header)

Behavior:  
\- Current track continues  
\- Channel fader playing track → max  
\- Channel fader next track → min  
\- Crossfader → center (remains)  
\- Next track auto-loaded opposite Deck  
\- Next track auto-starts few seconds before end  
\- Channel faders auto-move for transition

Optimization:  
\- Set Fade In/Out Cue Points in tracks  
\- Use Playlist for track order  
\- Manual trigger: pull down channel fader playing track

Requirements:  
\- At least one track playing when engaging  
\- Works with External Mixing mode

---

## **9\. COMANDI MIDI MAPPABILI {\#midi}**

### **9.1 Controller Manager Overview**

Location: Preferences \> Controller Manager

Sections:  
1\. Device Setup  
   \- Device: select mapping to edit  
   \- In-Port: MIDI input (set to specific port, not "All")  
   \- Out-Port: MIDI output (set to specific port, not "All")  
   \- Add: Generic Keyboard, Generic MIDI, Import, Native devices  
   \- Edit: Edit Comment, Duplicate, Export, Delete, Show Version  
   \- Device Target: Decks A-D or Deck Focus  
   \- Modifier State: current value 8 modifiers (debugging)

2\. Assignment Table  
   \- Control: function assignment name  
   \- I/O: In (input) o Out (output)  
   \- Assignment: target (Deck A-D, Device Target, Global)  
   \- Mode: interaction mode  
   \- Mapped to: source (input) o target (output)  
   \- Cond1/Cond2: modifier conditions  
   \- Comment: user comment

3\. Device Mapping  
   \- Learn: auto-map by moving control  
   \- Assignment Drop-Down: manual assignment  
   \- Reset: delete assignment  
   \- Comment: assignment comment

4\. Mapping Details  
   \- Modifier Conditions: M1-M8 \+ Value  
   \- Type of Controller: Button, Fader/Knob, Encoder  
   \- Assignment: Deck A-D, Device Target, Global  
   \- Interaction Mode \+ Options (depend su Type)

### **9.2 Controller Types**

#### **Button**

Interaction Modes:  
\- Toggle: press/release \= enable, press/release again \= disable  
\- Hold: pressed \= on, released \= off (default)  
\- Invert: inverted action  
\- Direct: specify 0 or 1 (force specific state)

Button Options:  
\- Value (Direct mode): 0 or 1  
\- Invert (Toggle/Hold): inverted movement  
\- Auto Repeat: holding repeats input  
\- Resolution: fine/coarse increment/decrement

#### **Fader/Knob**

Interaction Modes:  
\- Direct: external position \= TRAKTOR position  
\- Relative: TRAKTOR position shiftable (best for incremental)

Fader/Knob Options:  
\- Soft Takeover (Direct): avoid parameter jumps  
\- Invert (Direct/Relative): high values \= low, vice versa

#### **Encoder**

Enc-Mode:  
\- 7Fh/01h (standard, most controllers)  
\- 3Fh/41h (alternate, se invertito o troppo coarse)

Encoder Options:  
\- Rotary Sensitivity (Relative): speed TRAKTOR control  
\- Rotary Acceleration (Relative): speed-based influence (0% raccomandato)  
\- Invert (Direct/Relative): inverted action

### **9.3 Assignable MIDI Controls (Completo)**

#### **AUDIO RECORDER**

In/Out:  
\- Record/Stop  
\- Cut  
\- Gain Adjust  
\- Load Last Recording

#### **Browser**

List Operations:  
\- Delete, Reset Played-State, Analyze, Restore Auto-Gain  
\- Detect BPM, BPM Unlock/Lock, Edit, Relocate  
\- Add as Track/One-Shot/Loop To Collection  
\- Set to One-Shot/Looped/Track  
\- Select Up/Down, Page Up/Down, Top/Bottom  
\- Select Extend Up/Down, Page Up/Down, Top/Bottom  
\- Select All, Consolidate, Search, Search Clear  
\- Search in Playlists, Show In Explorer, Clear  
\- Expand Content Set, Jump To Current Track  
\- Append/Add As Next To Preparation List  
\- Export as Remix Set

Tree Operations:  
\- Save Collection, Delete, Reset Played-State  
\- Analyze, Restore AutoGain, Edit, Relocate  
\- Import Collection/Music Folders, Export, Export Printable  
\- Rename Playlist or Folder  
\- Select Up/Down, Expand/Collapse  
\- Create/Delete Playlist/Playlist Folder  
\- Refresh Explorer Folder Content  
\- Check Consistency, Add Folder To Music Folders

Favorites:  
\- Selector  
\- Add Selected Tracks To Favorite

#### **Deck Common (Track/STEM/Remix)**

Loading:  
\- Load Next, Load Previous, Load Selected, Unload

Transport:  
\- Play/Pause, Cue, CUP

Navigation:  
\- Jog Touch On, Jog Turn  
\- Seek Position

Tempo:  
\- Set as Tempo Master  
\- Sync On, Phase Sync, Tempo Sync  
\- Tempo Bend, Tempo Bend (stepless)  
\- Tempo Adjust  
\- Tempo Range Selector

Key:  
\- Keylock On, Keylock On (Preserve Pitch)  
\- Key Adjust

Analysis:  
\- Analyze Loaded Track

Deck Config:  
\- Deck Flavor Selector (Track/Remix/STEM/Live)  
\- Deck Size Selector (Micro/Small/Essential/Full/Advanced)  
\- Advanced Panel Toggle  
\- Advanced Panel Tab Selector (MOVE/CUE/GRID)

Timecode:  
\- Scratch Control On  
\- Playback Mode Int/Rel/Abs  
\- Platter/Scope View Selector  
\- Calibrate, Reset Tempo Offset

Move:  
\- Size Selector, Mode Selector, Move, Beatjump

Loop:  
\- Loop In/Set Cue, Loop Out, Loop Size Selector  
\- Loop Set, Loop Size Select \+ Set  
\- Backward Loop Size Select \+ Set  
\- Loop Active On

Output (Out only):  
\- Phase, Beat Phase  
\- Deck is Loaded, Is In Active Loop

Freeze Mode:  
\- Freeze Mode On  
\- Freeze Slice Size Adjust  
\- Freeze Slice Count Adjust  
\- Slice Trigger (1-16)

#### **FX Unit**

\- Unit On  
\- Dry/Wet Adjust  
\- Knob 1, Knob 2, Knob 3  
\- Button 1, Button 2, Button 3  
\- Effect 1/2/3 Selector  
\- FX Unit Mode Selector (Single/Group)  
\- FX Store Preset  
\- Effect LFO Reset

#### **Global**

\- Snap On, Quant On  
\- Broadcasting On, Cruise Mode On  
\- Show Slider Values On, Tool Tips On  
\- Send Monitor State

#### **Layout**

\- Only Browser On  
\- Layout Selector  
\- Fullscreen On  
\- Deck Focus Selector  
\- Toggle Last Focus

#### **LOOP RECORDER**

\- Record, Size, Dry/Wet Adjust  
\- Play/Pause, Delete, Undo/Redo  
\- Playback Position (Out), Undo State (Out), State (Out)

#### **Master Clock**

\- Ableton Link \> Reset Downbeat  
\- Auto Master Mode  
\- Master Tempo Selector (Clock/Deck A/B/C/D)  
\- Set Tempo Master, Tempo Bend Up/Down  
\- Beat Tap, Tick On  
\- Clock Int/Ext, Clock Send, Clock Trigger MIDI Sync

#### **Mixer**

Channel:  
\- Gain Adjust, Auto-Gain Adjust, Auto-Gain View On  
\- FX Unit 1/2/3/4 On, Deck Effect On  
\- Mixer FX Adjust, Mixer FX On, Mixer FX Selector  
\- Balance Adjust, Monitor Cue On, Volume Adjust

Master:  
\- Master Volume Adjust, Limiter On  
\- Monitor Volume Adjust, Monitor Mix Adjust  
\- Microphone Gain Adjust

EQ:  
\- High/Mid/MidLow/Low Adjust  
\- High/Mid/MidLow/Low Kill

Crossfader:  
\- X-Fader Position, Curve Adjust  
\- Assign Left, Assign Right  
\- Auto X-Fade Left, Auto X-Fade Right

#### **Modifier**

\- Modifier \#1 \- \#8 (In/Out)

#### **Preview Player**

\- Load Selected, Play/Pause, Seek Position, Unload

#### **Remix Deck**

Remix Set:  
\- Save Remix Set, Load Set from List

Slot:  
\- Slot Volume Adjust  
\- Slot Filter On, Slot Filter Adjust  
\- Slot Capture/Trigger/Mute  
\- Slot Mute On  
\- Slot Stop/Delete/Load from List  
\- Slot Retrigger  
\- Slot Play Mode (Loop/One-shot)  
\- Slot Keylock On  
\- Slot State (Out)  
\- Slot FX On, Slot Monitor On, Slot Punch On

Deck:  
\- Quantize Selector, Quantize On  
\- Capture Source Selector  
\- Sample Page Selector

Legacy:  
\- Play All Slots, Trigger All Slots  
\- Slot Retrigger Play, Slot Load from List  
\- Slot Unload, Slot Capture from Deck/Loop Recorder  
\- Slot Copy from Slot, Play Mode All Slots  
\- Slot Size x2/÷2/Reset/Adjust

Direct Mapping:  
\- Slot X Cell Y Trigger (In)  
\- Slot X Cell Y State (Out)  
\- Cell Load/Delete/Reverse/Capture Modifier

Meters (Out):  
\- Slot Pre-Fader Level (L/R/L+R)

Step Sequencer:  
\- Sequencer On, Swing Amount  
\- Selected Sample, Pattern Length  
\- Enable Step 1-16

#### **Track Deck (specifico)**

Loading:  
\- Load into Next Stopped Deck  
\- Load, Loop, and Play  
\- Duplicate Track Deck A/B/C/D

Display:  
\- Waveform Zoom Adjust  
\- DAW View (STEM Deck)

Key:  
\- Keylock On, Keylock On (Preserve Pitch)  
\- Key Adjust

Cue:  
\- Set Cue and Store as next Hotcue  
\- Store Floating Cue/Loop as next Hotcue  
\- Delete current Hotcue  
\- Jump to Next/Prev Cue/Loop  
\- Map Hotcue, Select/Set+Store Hotcue  
\- Delete Hotcue, Cue Type Selector  
\- Hotcue 1-8 Type (Out)

Grid:  
\- Autogrid, Reset BPM  
\- Copy Phase from Tempo Master  
\- Set/Delete Grid Marker, Move Grid Marker  
\- BPM Adjust, BPM Lock On  
\- BPM x2, BPM /2, Beat Tap  
\- Tick On

---

## **10\. CONFIGURAZIONI E PREFERENZE {\#preferenze}**

### **10.1 Audio Setup**

Audio Setup:  
\- Audio Device: select audio interface  
\- Sample Rate: 44.1kHz (standard), 48kHz, 88.2kHz, 96kHz  
  \* Higher \= more CPU load  
\- Buffer Size: 256-512 recommended  
  \* Lower \= lower latency, more CPU load  
\- Latency: calculated from Sample Rate \+ Buffer Size  
  \* Target: 5-15 ms  
  \* macOS: slider  
  \* Windows: Settings button (driver control panel)

Phono/Line:  
\- Input Channel: Phono/Line switch (AUDIO 4/8 DJ only)

Routing:  
\- Swap Channels: reroute channel pairs

Built-in Soundcard:  
\- Win Built-In: fallback se Audio Device rimosso

Multi-Core:  
\- Enable Multi-Core Processor Support: reduce CPU load  
  \* Disable se running secondo real-time app

### **10.2 Output Routing**

Internal Mixing Mode:  
\- Output Monitor: pre-listen output pair  
  \* CUE buttons → separate output  
  \* Preview Player output (Internal Mixing)  
  \* Mono: merge channels  
\- Output Master: master output pair  
  \* Mono: merge channels  
\- Output Record: recording output pair  
  \* Separate output per recording device

External Mixing Mode:  
\- Output Deck A/B/C/D: output pair per deck  
  \* Can sum multiple decks to one pair  
\- Output Preview: Preview Player output  
\- Output FX Return: send effects output

### **10.3 Input Routing**

\- Input Deck A/B/C/D: input pair per deck  
  \* Can sum multiple decks to one pair  
  \* Volume Meters: signal level display  
\- Input FX Send (Ext): send effects input  
\- Input Aux: auxiliary input (Internal Mixing only)

### **10.4 External Sync**

External Clock Source:  
\- LINK: Ableton Link (LINK in Master Control Panel)  
\- EXT: MIDI Clock (EXT in Master Control Panel)

MIDI Clock Settings:  
\- Enable MIDI Clock: add MIDI Clock controls to Master Control Panel

### **10.5 Timecode Setup**

Timecode Inputs:  
\- Control signal Scopes (visual quality)

Tracking:  
\- Track Start Position: 0-10 min (sticker/worn lead-in)  
\- Turntable Speed: 45 RPM mode (requires 45 RPM playback)  
\- Tracking Alert: visual feedback bad signal (red flash)  
\- Load next track when flipping record: auto-load next  
\- Use playlist scrolling zone: enable Browse zone  
\- Switch to Absolute mode in lead-in: auto Absolute  
\- Switch to Absolute mode when loading: force Absolute

### **10.6 Loading**

Loading:  
\- Loading only into stopped Deck: prevent accidental load  
\- Stop playback at end of track: auto-stop  
\- Duplicate Deck when loading same track: copy deck state  
\- Load next at end of track: auto-load next playlist track  
\- Initially Cue to Load Marker: jump to Load Marker  
\- Activate Fade & Fade Out Markers: enable auto crossfades  
\- Cruise Loops Playlist: repeat playlist in Cruise Mode

Resetting Controls:  
\- Reset all Deck controls when loading track: defaults  
\- Reset all mixer controls when loading track: defaults

### **10.7 Transport**

Tempo:  
\- Set Tempo Range To: global range (2%-100%)  
  \* 100% \= full stop possible  
\- Current Tempo Range: per-Deck display

Tempo Bend:  
\- Sensitivity: 0-200% (default 100%)  
\- Tempo Bend Progressive Sensitivity: progressive speed change

Sync Mode:  
\- TempoSync: tempo-only sync  
  \* Phase aligned at SYNC click  
  \* SYNC dim if phase shift  
  \* Tempo remains synced  
\- BeatSync: tempo \+ phase sync (raccomandato)  
  \* Phase aligned at SYNC click  
  \* SYNC dim if phase shift (scratch/stop)  
  \* Auto re-align at release  
  \* REQUIRES accurate beatgrids

Auto Master Mode:  
\- Remix Decks can be Tempo Master: On/Off  
\- Only On-Air Decks can be Tempo Master: On/Off  
  \* On: solo audible Decks \= Master  
  \* Off: any playing Deck \= Master

Key Lock:  
\- Key Lock Modes:  
  \* Scratch: disabled \<-30% or \>+50% speed  
  \* Normal: enabled full tempo range

Loops:  
\- Auto-Detect Size: threshold auto-detect loop

Play Count:  
\- Min. Playtime: threshold mark as played

Beat Counter:  
\- Bars per Phrase: bars per phrase (4 beats per bar)  
  \* Influences Beats/Beats to Cue display

Mouse Control:  
\- Vinyl: click waveform \= stop (like vinyl)  
  \* Drag \= scratch/spin  
\- Snap: click \= jump to nearest beat \+ stop

Cue Play (CUP Mode):  
\- Instant: playback starts immediately  
\- On Release: playback starts after release

### **10.8 Decks Layout**

Deck Flavor:  
\- A, B, C, D: Track Deck/Remix Deck/STEM Deck/Live Input

Deck Layout:  
\- Size A & B: Micro/Small/Essential/Full/Advanced  
\- Size C & D: Micro/Small/Essential/Full/Advanced  
\- Show Deck C & D: display/hide lower decks

Tempo Fader:  
\- Enable/disable per Deck

Platter/Scope:  
\- Off/Minimized/Platter/Scope per Deck (Scratch mode)

Miscellaneous:  
\- Grid Mode: Full/Dim/Ticks/Invisible  
\- Show Minute Markers: Stripe markers  
\- Show Bar Markers: Waveform markers  
\- Color Mode: Ultraviolet/Infrared/X-Ray/Spectrum

Deck Header:  
\- Show Cover Art: cover icon  
\- Show Phase Meter: phase meter

### **10.9 Track Decks**

Deck Header:  
\- Top/Middle/Bottom Row: information displayed (3 fields × 3 rows)  
  \* Top \= larger, Bottom \= smaller

Advanced Tabs:  
\- A, B, C, D: default Advanced Panel page (MOVE/CUE/GRID)

Miscellaneous:  
\- Track End Warning: 0-120 seconds before end (Stripe flash red)  
\- PlayMarker Position: 0-100 (0=left, 50=center, 100=right)  
\- Stripe View Fit: Record/Track  
  \* Record: whole Stripe \= record length  
  \* Track: Stripe \= track length  
\- Default Zoom: \-1.00 (far out) to \+1.00 (close in)

### **10.10 Remix Decks**

Remix Deck Layout:  
\- Show Volume Fader: display/hide  
\- Show Filter Fader: display/hide  
\- Permanently Show Slot Indicators: always visible/on hover  
\- Set Auto-Gain When Loading Samples: use stored Auto-Gain

Behaviors:  
\- Auto-Enable Deck Play on Sample Trigger: force Play On  
\- One-Shot Samples Ignore Punch Mode: ignore Punch  
\- One-Shot Samples Ignore Quantize Mode: ignore Quantize

Saving:  
\- Auto-Save Edited Remix Sets: auto-save on deck changes  
  \* No dialogs, overwrite existing  
  \* OFF \= discard changes (preferred for consistent state)

### **10.11 Mixer**

EQ/Filter Selection:  
\- EQ Type: Classic/P600/NUO/Xone/Z ISO/P800  
\- Filter Type: Ladder/Xone/Z

Mixer FX:  
\- Mixer FX Slot 1/2/3/4: select 4 of 8 available

Crossfader:  
\- Auto Crossfade Time: duration auto fade  
\- Smooth/Sharp: crossfader curve

Mixer Layout:  
\- EQ \+ Fader: show/hide  
\- Filter \+ Key \+ Gain \+ Cue \+ Balance: show/hide  
\- Crossfader: show/hide

Internal Mixing Mode:  
\- Enable Autogain: auto level incoming signals  
\- Enable Limiter: prevent clipping  
\- Limiter Type: Classic/Transparent  
\- Headroom: None/-3dB/-6dB/-9dB/-12dB  
\- Apply Headroom to Channel Meters: visual on meters

External Mixing Mode:  
\- Enable Master Volume Control: MAIN knob active  
\- Enable EQ \+ GAIN: EQ/GAIN controls active  
\- Enable Mixer FX: Mixer FX active  
\- Enable Autogain: auto level  
\- Limiter Type: Classic/Transparent  
\- Enable Limiter: prevent clipping  
\- Headroom: None/-3dB/-6dB/-9dB/-12dB  
\- Apply Headroom to Channel Meters: visual on meters

### **10.12 Global Settings**

Global Section:  
\- Show Global Section: display/hide  
\- Left: FX Unit 1/LOOP RECORDER default  
\- Right: FX Unit 2/AUDIO RECORDER default

Miscellaneous:  
\- Fullscreen Resolution: Desktop/lower (zoomed)  
\- Switch to Fullscreen on Startup: auto fullscreen  
\- Show Tooltips: enable/disable  
\- Deck Focus: Software/Hardware/None  
\- Show value when over control: hover display value  
\- Enable Deck Header Warnings: warnings in headers  
\- Reset Hidden Dialogs: restore dialogs con "Don't Show Again"

Usage Data:  
\- Yes, enable Usage Data Tracking  
\- No, I don't want to contribute  
\- Per-computer setting

### **10.13 Effects**

FX Unit Routing (per FX Unit):  
\- Insert/Send/Post Fader

FX Units:  
\- 2 FX Units / 4 FX Units

FX Panel Mode (per FX Unit):  
\- Single / Group

FX Pre-Selection:  
\- Available Effects: all 40 effects  
\- Pre-Selected Effects: subset visible in selectors  
\- Add/Remove: manage selection  
\- Up/Down: reorder

Restore parameters when switching FX: reset to defaults

### **10.14 Mix Recorder**

Source:  
\- Source: Internal/External  
\- External Input: input channel

File:  
\- Directory: save path  
\- Prefix: filename prefix  
\- Split File at Size: max 2048 MB

### **10.15 Loop Recorder**

Latency:  
\- Rec. Latency: adjust recording latency (External Mixing)

Overdubbing:  
\- LoopDecay: fade out % durante overdubbing

### **10.16 Broadcasting**

Proxy Settings:  
\- Custom: manual proxy  
  \* Proxy Address: IP  
  \* Port: default 8000  
\- Default: system proxy  
\- None: no proxy

Server Settings:  
\- Address: computer IP  
\- Port: default 8000  
\- Mount Path: directory path  
\- Password: server password  
\- Format: sound quality (higher \= more bandwidth)

Metadata Settings:  
\- Stream URL: broadcast URL  
\- Stream Name: broadcast title  
\- Stream Description: description  
\- Stream Genre: music genre

### **10.17 Browser Details**

Editing:  
\- Allow Inline Editing in List Window: double-click edit  
\- Font & Font Size: Browser font  
\- List Row Height: Track List row height

Browser Details:  
\- Show Preview Player  
\- Show Cover Art  
\- Show Playlist Favorites  
\- Show Track Info  
\- Show Status Bar/Error Messages

### **10.18 Layout Manager**

\- Change Name: rename layout  
\- Rename: confirm  
\- Personal Layouts: list custom layouts  
  \* Active \= currently active  
  \* Order \= Layout Selector order  
\- Add: create new layout (from standard templates)  
\- Remove: delete layout  
\- Duplicate: copy layout  
\- Move Up/Down: reorder list

### **10.19 File Management**

File Management:  
\- Import Music-Folders at Startup: auto-import new  
\- Determine track-time automatically: estimate pre-analysis  
\- Analyze new imported tracks: auto on import  
\- Analyze new tracks when loading into deck: auto on load  
\- Save created Loops and Samples automatically: auto-save  
\- Show Consistency Check Report on Startup: auto-check

File structure mode (export):  
\- None: no change  
\- Flat: 01 Artist \- Title format  
\- Artist: sub-folders by artist  
\- Label: sub-folders by label

Tag writing mode:  
\- Do not write any tags to files  
\- Only write custom Traktor tags  
\- Write all tags to files

Directories:  
\- Root Dir: Collection/Playlists/Settings/History/Mappings  
\- Sample Dir: Sample files  
\- Remix Sets Dir: Remix Sets  
\- iTunes Music Library: iTunes Library path  
\- Reset buttons: restore defaults

Music Folders:  
\- Add: add music folders  
\- Delete: remove from list  
\- Change: update path

### **10.20 Analyze Options**

BPM Detection:  
\- BPM Range: min-max or Automatic  
  \* Automatic: AI tempo \+ downbeat  
  \* Specific range: better accuracy  
\- Set Beatgrid when detecting BPM: auto beatgrid \+ align  
\- Store Beatmarker as Hotcue: beatmarker as hotcue

Musical Key:  
\- Displayed in Traktor: Musical/Musical (sharps)/Open Key  
\- Written to File Tags: Musical/Musical (sharps)/Open Key/Key Text

### **10.21 Controller Manager**

Device Setup:  
\- Device: select mapping  
\- In-Port: MIDI input (avoid "All")  
\- Out-Port: MIDI output (avoid "All")  
\- Add: Generic Keyboard/MIDI, Import, Native devices  
\- Edit: Comment, Duplicate, Export, Delete, Version  
\- Device Target: Decks A-D / Deck Focus  
\- Modifier State: M1-M8 current values

Assignment Table:  
\- Sortable by column (click header)  
\- Selected control \= yellow  
\- Same Mapped to \= darker yellow  
\- Control: function name  
\- I/O: In/Out  
\- Assignment: target  
\- Mode: interaction mode  
\- Mapped to: source/target  
\- Cond1/Cond2: modifiers  
\- Comment: user text

Device Mapping:  
\- Learn: auto-map (toggle off when done\!)  
\- Assignment Drop-Down: manual map (MIDI ch 1-16)  
\- Reset: delete assignment  
\- Comment: text

Mapping Details:  
\- Modifier Conditions: M1-M8 \+ Value (0-7)  
\- Type of Controller: Button/Fader/Knob/Encoder  
\- Assignment: Deck/Global  
\- Interaction Mode \+ Options

---

## **APPENDICE: NOTE OPERATIVE PER AGENTE AI**

### **Priorità Operative**

1\. Beatgrid Accuracy: fondamentale per tutte sync operations  
2\. Gain Staging: prevent clipping, maintain headroom  
3\. Smooth Transitions: EQ management, tempo matching  
4\. Track Selection: energy flow, key compatibility  
5\. Creative Elements: FX, loops, hotcues appropriati

### **Workflow Ottimale**

Preparation Phase:  
1\. Verify all tracks analyzed  
2\. Check beatgrid accuracy (use GRID page)  
3\. Set Load Markers strategic positions  
4\. Store Hotcues important positions  
5\. Organize Playlists by energy/genre/key

Performance Phase:  
1\. Load track 1 → Deck A, start playback  
2\. Monitor Master Level (avoid clipping)  
3\. Preview track 2 in headphones (CUE)  
4\. Load track 2 → Deck B  
5\. SYNC button (auto tempo match)  
6\. EQ preparation (LOW knob track 2 → min)  
7\. Start playback track 2 (quantized to beat)  
8\. Crossfade transition (gradual)  
9\. EQ swap (LOW track 1 ↓, LOW track 2 ↑)  
10\. Complete transition  
11\. Track 2 \= new Tempo Master  
12\. Repeat from step 3

Advanced Techniques:  
\- Flux Mode: maintain phrase during creative cuts  
\- Hotcues: instant jump to chorus/break/drop  
\- Loops: extend sections, build tension  
\- FX: enhance transitions, create interest  
\- STEM manipulation: isolate elements, creative mixing

### **Error Prevention**

Critical:  
\- NEVER load track into playing Deck without confirmation  
\- ALWAYS verify SYNC before starting playback  
\- ALWAYS check Headroom/Limiter settings  
\- NEVER exceed red zone on meters  
\- ALWAYS preview transition in headphones first

Best Practices:  
\- Use AUTO mode for automatic Tempo Master assignment  
\- Enable SNAP \+ QUANT for seamless jumps  
\- Lock beatgrids when correct (Analysis Lock)  
\- Save Collection regularly  
\- Use Consistency Check periodically

### **MIDI Control Integration**

Essential Mappings:  
\- Play/Pause: transport control  
\- SYNC: tempo synchronization  
\- CUE: jump to cue point  
\- Loop controls: quick loop enable/disable  
\- FX assign: instant FX routing  
\- Crossfader: smooth transitions  
\- EQ knobs: frequency management  
\- Gain knobs: level control  
\- Hotcue buttons: stored position access

Advanced Mappings:  
\- Beatjump: phrase navigation  
\- Loop move: creative loop placement  
\- FX parameters: detailed effect control  
\- Tempo bend: micro tempo adjustments  
\- Key adjust: harmonic mixing

---

**FINE DOCUMENTO**

*Versione: TRAKTOR PRO 3.1 (02/2019)*  
 *Documento creato per training agente AI DJ autonomo*  
 *Tutti comandi, opzioni e workflow inclusi senza omissioni*

