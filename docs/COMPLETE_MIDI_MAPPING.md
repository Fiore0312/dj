# Complete MIDI Mapping Reference - AI DJ System

## Overview

This document provides the complete MIDI CC (Control Change) mapping for the AI DJ system with Traktor Pro 3. **Based on actual configuration from traktor_control.py**.

## MIDI Channels

- **Channel 1**: AI Control Commands (main control)
- **Channel 2**: Status Feedback (from Traktor)
- **Channel 3**: Human Override (emergency controls)
- **Channel 4**: Effects Control (FX units)

---

## 📀 DECK TRANSPORT CONTROLS

### Play/Pause
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 20 | Deck A Play/Pause | 127 | Toggle Play/Pause on Deck A |
| CC 21 | Deck B Play/Pause | 127 | Toggle Play/Pause on Deck B |
| CC 22 | Deck C Play/Pause | 127 | Toggle Play/Pause on Deck C |
| CC 23 | Deck D Play/Pause | 127 | Toggle Play/Pause on Deck D |

### Cue Points
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 24 | Deck A Cue | 127 | Jump to/Set Cue Point on Deck A |
| CC 25 | Deck B Cue | 127 | Jump to/Set Cue Point on Deck B |
| CC 26 | Deck C Cue | 127 | Jump to/Set Cue Point on Deck C |
| CC 27 | Deck D Cue | 127 | Jump to/Set Cue Point on Deck D |

**Commands:**
- `play a` / `play b` - Toggle play/pause
- `cue a` / `cue b` - Jump to cue point

---

## 🔊 VOLUME & MIXER CONTROLS

### Deck Volumes
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 28 | Deck A Volume | 0-127 | 0 = Mute, 127 = Max volume |
| CC 29 | Deck B Volume | 0-127 | 0 = Mute, 127 = Max volume |
| CC 30 | Deck C Volume | 0-127 | 0 = Mute, 127 = Max volume |
| CC 31 | Deck D Volume | 0-127 | 0 = Mute, 127 = Max volume |

### Crossfader & Master
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 32 | Crossfader | 0-127 | 0 = Full A, 64 = Center, 127 = Full B |
| CC 33 | Master Volume | 0-127 | 0 = Mute, 127 = Max master volume |

**Commands:**
- `volume a 75%` - Set Deck A volume to 75%
- `crossfade b` - Move crossfader to Deck B (127)
- `crossfade 50%` - Center crossfader (64)
- `master 80%` - Set master volume to 80%

---

## 🎛️ EQ CONTROLS

### Deck A EQ
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 34 | Deck A EQ High | 0-127 | 0 = Kill, 64 = Neutral, 127 = Boost |
| CC 35 | Deck A EQ Mid | 0-127 | 0 = Kill, 64 = Neutral, 127 = Boost |
| CC 36 | Deck A EQ Low | 0-127 | 0 = Kill, 64 = Neutral, 127 = Boost |

### Deck B EQ
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 50 | Deck B EQ High | 0-127 | 0 = Kill, 64 = Neutral, 127 = Boost |
| CC 51 | Deck B EQ Mid | 0-127 | 0 = Kill, 64 = Neutral, 127 = Boost |
| CC 52 | Deck B EQ Low | 0-127 | 0 = Kill, 64 = Neutral, 127 = Boost |

**Commands:**
- `eq a high 75%` - Set Deck A high EQ to 75%
- `kill a bass` - Kill bass on Deck A (set to 0)
- `eq b mid 50%` - Set Deck B mid to neutral (64)

---

## 📂 BROWSER & TRACK LOADING

### Browser Navigation (Basic)
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 37 | Browser Up | 127 | Scroll up in track list |
| CC 38 | Browser Down | 127 | Scroll down in track list |
| CC 49 | Browser Select/Enter | 127 | Select highlighted item |

### Track Loading
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 39 | Load Track to Deck A | 127 | Load selected track to Deck A |
| CC 40 | Load Track to Deck B | 127 | Load selected track to Deck B |

**Commands:**
- `browse up` / `browse down` - Navigate track list
- `browse down 5` - Scroll down 5 tracks
- `load a` - Load selected track to Deck A
- `load b` - Load selected track to Deck B

---

## 📁 BROWSER TREE NAVIGATION (NEW)

### Tree Navigation
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 55 | Browser Tree Up | 127 | Navigate up in tree structure |
| CC 56 | Browser Tree Down | 127 | Navigate down in tree structure |
| CC 57 | Browser Tree Enter | 127 | Enter folder/playlist |
| CC 58 | Browser Tree Exit | 127 | Exit folder (go back to parent) |
| CC 59 | Browser Tree Expand | 127 | Expand folder |
| CC 60 | Browser Tree Collapse | 127 | Collapse folder |

### Page Navigation
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 61 | Browser Page Up | 127 | Jump page up in list |
| CC 62 | Browser Page Down | 127 | Jump page down in list |
| CC 63 | Browser Top | 127 | Jump to top of list |
| CC 64 | Browser Bottom | 127 | Jump to bottom of list |

**Commands:**
- `tree up` / `tree down` - Navigate tree structure
- `tree enter` - Enter selected folder/playlist
- `tree exit` - Go back to parent folder
- `tree expand` / `tree collapse` - Expand/collapse folders
- `page up` / `page down` - Fast navigation

---

## 🔄 SYNC CONTROLS

| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 41 | Deck A Sync | 127 | Sync Deck A to master tempo |
| CC 42 | Deck B Sync | 127 | Sync Deck B to master tempo |
| CC 43 | Deck C Sync | 127 | Sync Deck C to master tempo |
| CC 44 | Deck D Sync | 127 | Sync Deck D to master tempo |

**Commands:**
- `sync a` - Sync Deck A
- `sync b` - Sync Deck B
- `beatmatch a b` - Full beatmatch (sync + volume + EQ)

---

## 🎵 PITCH/TEMPO CONTROLS

| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 45 | Deck A Pitch | 0-127 | 64 = 0%, 0 = -8%, 127 = +8% |
| CC 46 | Deck B Pitch | 0-127 | 64 = 0%, 0 = -8%, 127 = +8% |
| CC 47 | Deck C Pitch | 0-127 | 64 = 0%, 0 = -8%, 127 = +8% |
| CC 48 | Deck D Pitch | 0-127 | 64 = 0%, 0 = -8%, 127 = +8% |

**Commands:**
- `pitch a +2` - Increase pitch by +2% on Deck A
- `pitch b -1.5` - Decrease pitch by -1.5% on Deck B

---

## 🔁 LOOP CONTROLS (NEW)

### Deck A Loops
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 70 | Deck A Loop In | 127 | Set loop in point |
| CC 71 | Deck A Loop Out | 127 | Set loop out point |
| CC 72 | Deck A Loop Active | 0-127 | 0 = Off, 127 = On, toggle loop |
| CC 73 | Deck A Loop Size | 0-127 | Set loop size in beats |

### Deck B Loops
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 74 | Deck B Loop In | 127 | Set loop in point |
| CC 75 | Deck B Loop Out | 127 | Set loop out point |
| CC 76 | Deck B Loop Active | 0-127 | 0 = Off, 127 = On, toggle loop |
| CC 77 | Deck B Loop Size | 0-127 | Set loop size in beats |

**Commands:**
- `loop in a` - Set loop in point on Deck A
- `loop out a` - Set loop out point on Deck A
- `loop activate a` - Activate loop on Deck A
- `loop 4 a` - Set 4-beat loop on Deck A
- `loop 8 b` - Set 8-beat loop on Deck B

---

## 🎯 HOTCUES (NEW)

### Deck A Hotcues
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 80 | Deck A Hotcue 1 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 81 | Deck A Hotcue 2 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 82 | Deck A Hotcue 3 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 83 | Deck A Hotcue 4 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 84 | Deck A Hotcue 5 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 85 | Deck A Hotcue 6 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 86 | Deck A Hotcue 7 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 87 | Deck A Hotcue 8 | 0-127 | 0 = Delete, 127 = Set/Trigger |

### Deck B Hotcues
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 88 | Deck B Hotcue 1 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 89 | Deck B Hotcue 2 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 90 | Deck B Hotcue 3 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 91 | Deck B Hotcue 4 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 92 | Deck B Hotcue 5 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 93 | Deck B Hotcue 6 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 94 | Deck B Hotcue 7 | 0-127 | 0 = Delete, 127 = Set/Trigger |
| CC 95 | Deck B Hotcue 8 | 0-127 | 0 = Delete, 127 = Set/Trigger |

**Commands:**
- `hotcue 3 a` - Trigger/set hotcue 3 on Deck A
- `delete hotcue 5 b` - Delete hotcue 5 on Deck B
- `hotcue 1 a` - Jump to hotcue 1 on Deck A

---

## ⏭️ BEATJUMP (NEW)

### Deck A Beatjump
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 96 | Deck A Beatjump Forward 1 | 127 | Jump forward 1 beat |
| CC 97 | Deck A Beatjump Backward 1 | 127 | Jump backward 1 beat |
| CC 98 | Deck A Beatjump Forward 4 | 127 | Jump forward 4 beats |
| CC 99 | Deck A Beatjump Backward 4 | 127 | Jump backward 4 beats |

### Deck B Beatjump
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 102 | Deck B Beatjump Forward 1 | 127 | Jump forward 1 beat |
| CC 103 | Deck B Beatjump Backward 1 | 127 | Jump backward 1 beat |
| CC 104 | Deck B Beatjump Forward 4 | 127 | Jump forward 4 beats |
| CC 105 | Deck B Beatjump Backward 4 | 127 | Jump backward 4 beats |

**Commands:**
- `beatjump forward 1 a` - Jump forward 1 beat on Deck A
- `beatjump back 4 b` - Jump backward 4 beats on Deck B
- `jump forward 4 a` - Same as beatjump forward

---

## 🔧 ADVANCED DECK CONTROLS (NEW)

### Deck A Advanced
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 108 | Deck A Keylock | 0-127 | 0 = Off, 64 = Toggle, 127 = On |
| CC 110 | Deck A Quantize | 0-127 | 0 = Off, 64 = Toggle, 127 = On |
| CC 112 | Deck A Flux Mode | 0-127 | 0 = Off, 64 = Toggle, 127 = On |

### Deck B Advanced
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 109 | Deck B Keylock | 0-127 | 0 = Off, 64 = Toggle, 127 = On |
| CC 111 | Deck B Quantize | 0-127 | 0 = Off, 64 = Toggle, 127 = On |
| CC 113 | Deck B Flux Mode | 0-127 | 0 = Off, 64 = Toggle, 127 = On |

**Commands:**
- `keylock on a` - Enable keylock on Deck A
- `quantize off b` - Disable quantize on Deck B
- `flux toggle a` - Toggle flux mode on Deck A

---

## ✨ EFFECTS (FX)

### FX Units (Channel 4)
| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 100 | FX Unit 1 Dry/Wet | 0-127 | 0 = Dry (off), 127 = Wet (full) |
| CC 101 | FX Unit 2 Dry/Wet | 0-127 | 0 = Dry (off), 127 = Wet (full) |
| CC 102 | FX Unit 3 Dry/Wet | 0-127 | 0 = Dry (off), 127 = Wet (full) |
| CC 103 | FX Unit 4 Dry/Wet | 0-127 | 0 = Dry (off), 127 = Wet (full) |

**Commands:**
- `fx 1 75%` - Set FX Unit 1 to 75% wet
- `fx 2 off` - Turn off FX Unit 2 (0)
- `fx 3 50%` - Set FX Unit 3 to 50%

---

## 🚨 EMERGENCY CONTROLS (Channel 3)

| CC Number | Function | Value Range | Description |
|-----------|----------|-------------|-------------|
| CC 80 | Emergency Stop All | 127 | Stop all decks immediately |
| CC 81 | AI Enable/Disable | 0-127 | 0 = Disable AI, 127 = Enable AI |
| CC 90 | Headphone Volume | 0-127 | Headphone cue volume |
| CC 91 | Headphone Mix | 0-127 | Cue/Master mix balance |

**Commands:**
- `emergency stop` - Stop all decks, center crossfader
- `panic` - Alias for emergency stop

---

## 📊 MIDI MAPPING SUMMARY

### CC Ranges by Function
- **Transport (20-27)**: Play/Pause and Cue controls for all 4 decks
- **Volume (28-33)**: Individual deck volumes, crossfader, master volume
- **EQ Deck A (34-36)**: High, Mid, Low EQ for Deck A
- **Browser Basic (37-40)**: Up/Down navigation and loading
- **Sync (41-44)**: Sync controls for all 4 decks
- **Pitch (45-48)**: Pitch adjustment for all 4 decks
- **Browser Select (49)**: Select/Enter item in browser
- **EQ Deck B (50-52)**: High, Mid, Low EQ for Deck B
- **Tree Navigation (55-60)**: Advanced playlist tree navigation
- **Page Navigation (61-64)**: Fast browser navigation
- **Loops (70-77)**: Loop controls for Deck A & B
- **Hotcues (80-95)**: 8 hotcues for Deck A & B (16 total)
- **Beatjump (96-99, 102-105)**: Beat-accurate jumping
- **Advanced (108-114)**: Keylock, Quantize, Flux for both decks
- **Effects (100-103)** on Channel 4: FX units dry/wet
- **Emergency (80-91)** on Channel 3: Safety controls

**Total**: 75+ MIDI CC mappings across 4 channels

---

## 🔌 Traktor Pro 3 Configuration

### Step 1: Enable IAC Driver (macOS)

1. Open **Audio MIDI Setup** (`/Applications/Utilities`)
2. Window → **Show MIDI Studio**
3. Double-click **IAC Driver** icon
4. ☑️ Check **"Device is online"**
5. Verify **Bus 1** exists in the list
6. Click **Apply**

### Step 2: Import TSI Mapping

1. Open **Traktor Pro 3**
2. Preferences → **Controller Manager**
3. Click **Import** button (bottom left)
4. Navigate to: `/Users/Fiore/dj/AI_DJ_Perfect_Mapping.tsi`
5. Select file and click **Open**
6. Verify device shows: **Generic MIDI** on **IAC Driver Bus 1**
7. Ensure **In-Port** and **Out-Port** both show **Bus 1**
8. Click **OK** to save

### Step 3: Verify MIDI Communication

```bash
# Test MIDI connectivity
cd /Users/Fiore/dj
python3 traktor_control.py

# Should show:
# ✓ MIDI Output: IAC Driver Bus 1
# ✓ Ready for commands
```

### Step 4: Test Basic Commands

```bash
# Run hybrid DJ system
./run_hybrid_dj.sh

# Test in manual mode (type these commands):
load a          # Should load track to Deck A
play a          # Should start Deck A
tree down       # Should navigate tree
tree enter      # Should enter folder
```

---

## 🎯 Usage Examples

### Example 1: Autonomous Track Selection
```
Command sequence:
1. tree down           # Navigate to "House" playlist in tree
2. tree enter          # Enter the playlist
3. browse down 5       # Scroll 5 tracks down in list
4. load a              # Load selected track to Deck A
5. play a              # Start playing Deck A
6. sync a              # Sync to master tempo
```

### Example 2: Professional Loop Mixing
```
Command sequence:
1. loop in a           # Set loop start point
2. loop out a          # Set loop end point
3. loop activate a     # Activate the loop
4. hotcue 1 a          # Save loop position as hotcue 1
5. eq a bass 0         # Kill bass for transition
6. beatjump forward 4  # Jump 4 beats ahead
```

### Example 3: Complete DJ Set Workflow
```
Command sequence:
1. tree enter          # Enter "Techno" playlist
2. load a              # Load first track to A
3. play a              # Start deck A
4. volume a 80%        # Set volume
5. browse down 3       # Find next compatible track
6. load b              # Load to deck B
7. sync b              # Sync BPM to deck A
8. mix a to b 30       # 30-second automatic transition
9. hotcue 3 b          # Mark drop point on deck B
10. tree exit          # Go back to main playlists
```

### Example 4: Creative Performance
```
Command sequence:
1. loop 4 a            # Create 4-beat loop on A
2. hotcue 1 a          # Save loop as hotcue 1
3. beatjump back 4 a   # Jump back 4 beats
4. eq a high 0         # Kill highs
5. fx 1 75%            # Add reverb effect
6. keylock on a        # Enable keylock
7. pitch a +2          # Increase tempo
```

---

## 📝 Important Notes

### MIDI Value Conventions
- **127**: Maximum / On / Trigger action
- **64**: Center / Neutral / Toggle
- **0**: Minimum / Off / Delete

### EQ Values
- **0-63**: Cut/Kill (0 = full kill)
- **64**: Neutral (no change)
- **65-127**: Boost

### Crossfader Position
- **0**: Full Deck A
- **64**: Center (both decks equal)
- **127**: Full Deck B

### Loop Size Calculation
Approximate MIDI value = beats × 16
- 1 beat = 16
- 4 beats = 64
- 8 beats = 128 (clamped to 127)

---

## 🔗 Related Files

- **Python MIDI Map**: [traktor_control.py](traktor_control.py:65-220) - MIDI_MAP dictionary
- **Command Parser**: [simple_dj_controller.py](simple_dj_controller.py) - Natural language commands
- **TSI File**: [AI_DJ_Perfect_Mapping.tsi](AI_DJ_Perfect_Mapping.tsi) - Traktor import file
- **Hybrid Controller**: [autonomous_dj_master.py](autonomous_dj_master.py) - AI integration

---

## 📞 Troubleshooting

### MIDI Not Working
1. Check IAC Driver is online in Audio MIDI Setup
2. Verify Bus 1 exists and is enabled
3. Restart Traktor after importing TSI
4. Check Controller Manager shows "IAC Driver Bus 1"

### Wrong Deck Loading
- Verify CC 39 = Deck A, CC 40 = Deck B in Traktor mapping
- Re-import TSI file if mappings are incorrect

### Tree Navigation Not Working
- Ensure you're in Browser view in Traktor (F3)
- Tree commands (CC 55-60) require Tree panel to be visible
- Try `tree down` followed by `tree enter` to test

---

**Version**: 2.0 (Corrected)
**Last Updated**: 2025-01-02
**Status**: ✅ Verified against traktor_control.py
**Source**: Based on actual implementation in `/Users/Fiore/dj/traktor_control.py`
