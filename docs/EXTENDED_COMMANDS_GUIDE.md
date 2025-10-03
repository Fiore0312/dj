# Extended Commands Guide - AI DJ System

## Overview

This guide provides detailed usage examples, workflows, and troubleshooting for all MIDI commands in the AI DJ system.

---

## 🧪 Testing Your Mapping

### Interactive Test Tool

Use the interactive tester to verify all commands work correctly:

```bash
python test_midi_mapping_interactive.py
```

This will:
1. Test each command category one by one
2. Ask for your visual confirmation after each command
3. Help debug failures with detailed information
4. Generate a complete test report

---

## 📋 Command Categories

### 1. Transport Controls (CC 20-27)

#### Deck A/B Play/Pause (CC 20-21)
**What it does**: Toggles play/pause state for the deck

**Usage**:
```python
# From Python
traktor.play_deck(DeckID.A)  # Toggles play/pause

# From chat
"play a"
"pause b"
"stop a"
```

**Visual Feedback**: Deck play button lights up/dims in Traktor

**Troubleshooting**:
- ❌ No response → Check deck has track loaded
- ❌ Wrong deck plays → Verify CC mapping (20=A, 21=B)

---

#### Cue Point (CC 24-25)
**What it does**: Jumps to the cue point or sets it if not defined

**Usage**:
```python
# Set/jump to cue
traktor._send_midi_command(channel=1, cc=24, value=127, desc="Cue A")

# From chat
"cue a"
"jump to cue b"
```

**Visual Feedback**: Playhead jumps to cue marker

**Troubleshooting**:
- ❌ No cue set → First trigger sets cue point at current position
- ❌ Nothing happens → Track might not be loaded

---

### 2. Volume & Mixer (CC 28-33, 32)

#### Deck Volume (CC 28-29)
**What it does**: Controls individual deck volume faders

**Value Range**:
- `0` = Mute
- `64` = Unity (0dB)
- `127` = Maximum

**Usage**:
```python
# Set deck A to 75%
traktor.set_deck_volume(DeckID.A, 0.75)  # Value: 0.75 * 127 = 95

# From chat
"volume a 80%"
"mute b"
```

**Visual Feedback**: Volume fader moves in Traktor mixer section

---

#### Crossfader (CC 32)
**What it does**: Controls the crossfader position

**Value Range**:
- `0` = Full Deck A
- `64` = Center (both decks equal)
- `127` = Full Deck B

**Usage**:
```python
# Move to deck B
traktor.set_crossfader(1.0)  # Value: 127

# Center
traktor.set_crossfader(0.5)  # Value: 64

# From chat
"crossfade b"
"crossfade 50%"
"center crossfader"
```

**Visual Feedback**: Crossfader moves left/right

---

### 3. EQ Controls (CC 34-36, 50-52)

#### EQ Bands
**What it does**: Controls High/Mid/Low EQ for each deck

**Value Range**:
- `0` = Full Kill (-∞dB)
- `64` = Neutral (0dB, no change)
- `127` = Full Boost (+12dB)

**Deck A EQ**:
- CC 34 = High
- CC 35 = Mid
- CC 36 = Low

**Deck B EQ**:
- CC 50 = High
- CC 51 = Mid
- CC 52 = Low

**Usage**:
```python
# Kill bass on deck A
traktor.set_eq(DeckID.A, "low", 0.0)  # Value: 0

# Boost high on deck B
traktor.set_eq(DeckID.B, "high", 1.0)  # Value: 127

# Neutral mid
traktor.set_eq(DeckID.A, "mid", 0.5)  # Value: 64

# From chat
"eq a bass 0"
"kill a low"
"eq b high 75%"
```

**Visual Feedback**: EQ knobs rotate in Traktor

**Typical Workflow**:
```
1. "kill a bass"     # Cut bass before transition
2. "play b"          # Start incoming track
3. "eq a bass 50%"   # Gradually bring back
```

---

### 4. Browser Navigation

#### Basic Scrolling (CC 37-38)
**What it does**: Scroll up/down in the track list

**Usage**:
```python
# Scroll down 5 tracks
for _ in range(5):
    traktor._send_midi_command(1, 38, 127, "Browse Down")
    time.sleep(0.1)

# From chat
"browse down 5"
"scroll up"
```

**Visual Feedback**: Selection moves in browser list

**Troubleshooting**:
- ❌ No movement → Ensure browser is focused (click on it)
- ❌ Jumps too far → Check scroll sensitivity in Traktor preferences

---

#### Tree Navigation (CC 55-60) **[NEW]**
**What it does**: Navigate the playlist/folder tree structure

**Commands**:
- CC 55 = Tree Up (navigate to previous folder)
- CC 56 = Tree Down (navigate to next folder)
- CC 57 = Tree Enter (open selected folder/playlist)
- CC 58 = Tree Exit (go back to parent)
- CC 59 = Tree Expand (expand folder without entering)
- CC 60 = Tree Collapse (collapse folder)

**Usage**:
```python
# Navigate to playlist
traktor._send_midi_command(1, 56, 127, "Tree Down")  # Move to next item
traktor._send_midi_command(1, 57, 127, "Tree Enter") # Enter playlist

# Go back
traktor._send_midi_command(1, 58, 127, "Tree Exit")  # Exit to parent

# From chat
"tree down"
"tree enter"
"open playlist"
"go back"
```

**Visual Feedback**:
- Tree selection moves
- Folder opens/closes
- Track list updates

**Troubleshooting**:
- ❌ No response → Press **F3** to open Browser view
- ❌ Tree not visible → Click on "Tree" tab in browser
- ❌ Wrong item selected → Use tree up/down first

**Workflow Example**:
```
1. "tree down"    # Select "House" folder
2. "tree enter"   # Open it
3. "browse down 3" # Find specific track
4. "load a"       # Load to deck A
5. "tree exit"    # Go back to root
```

---

#### Page Navigation (CC 61-64) **[NEW]**
**What it does**: Fast navigation in large lists

**Commands**:
- CC 61 = Page Up (jump ~10 tracks up)
- CC 62 = Page Down (jump ~10 tracks down)
- CC 63 = Top (jump to first track)
- CC 64 = Bottom (jump to last track)

**Usage**:
```python
# Jump to top of list
traktor._send_midi_command(1, 63, 127, "Browser Top")

# From chat
"page down"
"jump to top"
"go to bottom"
```

---

### 5. Loop Controls (CC 70-77) **[NEW]**

#### Set Loop In/Out Points
**What it does**: Defines the start and end of a loop region

**Commands**:
- CC 70 (Deck A) / CC 74 (Deck B) = Loop In
- CC 71 (Deck A) / CC 75 (Deck B) = Loop Out

**Usage**:
```python
# Manual loop on deck A
traktor._send_midi_command(1, 70, 127, "Loop In A")   # Set start
time.sleep(2)  # Play for 2 seconds
traktor._send_midi_command(1, 71, 127, "Loop Out A")  # Set end

# From chat
"loop in a"
"loop out a"
```

**Visual Feedback**:
- Green markers appear on waveform
- Loop region highlighted

---

#### Loop Activate (CC 72, 76)
**What it does**: Activates/deactivates the defined loop

**Value Range**:
- `0` = Loop OFF
- `127` = Loop ON

**Usage**:
```python
# Activate loop
traktor._send_midi_command(1, 72, 127, "Loop Active A")

# Deactivate
traktor._send_midi_command(1, 72, 0, "Loop Off A")

# From chat
"loop activate a"
"loop on a"
"loop off a"
```

**Visual Feedback**:
- Playback repeats within loop region
- Loop active indicator lights up

---

#### Loop Size (CC 73, 77)
**What it does**: Sets loop size in beats

**Value Calculation**: `MIDI_value ≈ beats × 16`
- 1 beat = 16
- 4 beats = 64
- 8 beats = 96

**Usage**:
```python
# Set 4-beat loop
traktor._send_midi_command(1, 73, 64, "Loop Size 4")

# From chat
"loop 4 a"
"loop 8 b"
```

**Pro Workflow**:
```
1. "play a"         # Start deck
2. "loop 4 a"       # Set 4-beat loop
3. "loop activate"  # Enable it
4. "hotcue 1 a"     # Save as hotcue for later
```

---

### 6. Hotcues (CC 80-95) **[NEW]**

#### What They Do
Hotcues are instant jump points you can store and trigger during your set.

**CC Mapping**:
- Deck A: CC 80-87 (hotcues 1-8)
- Deck B: CC 88-95 (hotcues 1-8)

**Behavior**:
- **Value 127** = Store (if empty) or Jump to (if stored)
- **Value 0** = Delete hotcue

**Usage**:
```python
# Store hotcue 3 on deck A
traktor._send_midi_command(1, 82, 127, "Hotcue 3 A")

# Jump to it (send again)
traktor._send_midi_command(1, 82, 127, "Hotcue 3 A")

# Delete it
traktor._send_midi_command(1, 82, 0, "Delete Hotcue 3 A")

# From chat
"hotcue 3 a"
"jump to hotcue 5 b"
"delete hotcue 2 a"
```

**Visual Feedback**:
- Hotcue appears on waveform (colored marker)
- Button lights up in Traktor

**Creative Workflow**:
```
1. "loop in a"      # Mark intro start
2. "loop out a"     # Mark intro end
3. "hotcue 1 a"     # Save intro position
4. "play a"         # Continue playing
   [find drop]
5. "hotcue 2 a"     # Save drop position
6. "hotcue 1 a"     # Jump back to intro
```

---

### 7. Beatjump (CC 96-107) **[NEW]**

#### What It Does
Jumps forward or backward by exact beat count while maintaining sync.

**CC Mapping**:
- Deck A Forward 1: CC 96
- Deck A Back 1: CC 97
- Deck A Forward 4: CC 98
- Deck A Back 4: CC 99
- Deck B Forward 1: CC 102
- Deck B Back 1: CC 103
- Deck B Forward 4: CC 104
- Deck B Back 4: CC 105

**Usage**:
```python
# Jump forward 4 beats on deck A
traktor._send_midi_command(1, 98, 127, "Beatjump +4 A")

# Jump back 1 beat on deck B
traktor._send_midi_command(1, 103, 127, "Beatjump -1 B")

# From chat
"beatjump forward 4 a"
"jump back 1 b"
"skip 4 beats a"
```

**Visual Feedback**:
- Playhead jumps on waveform
- Position updates instantly

**Use Cases**:
- Skip boring intro/outro
- Loop breakdowns precisely
- Creative stuttering effects
- Phrase-aligned mixing

**Example**:
```
# Skip 32 beats (8 bars)
"beatjump forward 4 a"  # +4
"beatjump forward 4 a"  # +8
"beatjump forward 4 a"  # +12
... (repeat 8 times = 32 beats)
```

---

### 8. Advanced Deck Controls (CC 108-114) **[NEW]**

#### Keylock (CC 108, 109)
**What it does**: Locks the track's musical key when changing tempo

**Value Range**:
- `0` = Keylock OFF
- `64` = Toggle
- `127` = Keylock ON

**Usage**:
```python
# Enable keylock on deck A
traktor._send_midi_command(1, 108, 127, "Keylock ON A")

# Toggle
traktor._send_midi_command(1, 108, 64, "Keylock Toggle A")

# From chat
"keylock on a"
"keylock off b"
```

**When to Use**:
- ✅ When pitching tracks up/down significantly
- ✅ For harmonic mixing
- ❌ Don't use for small tempo adjustments (sounds unnatural)

---

#### Quantize (CC 110, 111)
**What it does**: Snaps all actions (cues, loops, hotcues) to the beat grid

**Usage**:
```python
# Enable quantize
traktor._send_midi_command(1, 110, 127, "Quantize ON A")

# From chat
"quantize on a"
"quantize off b"
```

**When to Use**:
- ✅ Live performance (prevents off-beat triggers)
- ✅ Fast mixing
- ❌ Disable for scratching or manual beat matching

---

#### Flux Mode (CC 112, 113)
**What it does**: Track continues in background during loops/cues

**Usage**:
```python
# Enable flux
traktor._send_midi_command(1, 112, 127, "Flux ON A")

# From chat
"flux on a"
"flux mode b"
```

**When to Use**:
- ✅ Creative loops without losing track position
- ✅ Drop back to original position after loop
- Example: Loop 4 beats, when you release, track continues where it would have been

---

### 9. Effects (FX) (CC 100-103)

#### FX Dry/Wet
**What it does**: Controls the mix between dry signal and effect

**Value Range**:
- `0` = 100% Dry (no effect)
- `64` = 50/50 mix
- `127` = 100% Wet (full effect)

**Usage**:
```python
# Half wet on FX1
traktor._send_midi_command(4, 100, 64, "FX1 50%")  # Note: Channel 4

# From chat
"fx 1 75%"
"fx 2 off"
```

**Troubleshooting**:
- ❌ No effect → Check FX is assigned to deck in Traktor
- ❌ Wrong effect → Change in FX unit selector

---

## 🎯 Complete Workflows

### Workflow 1: Autonomous Track Discovery & Load

```bash
# Goal: Find and load a house track from your library

1. tree down              # Navigate to "House" folder
2. tree enter             # Open folder
3. browse down 5          # Find specific track
4. load a                 # Load to deck A
5. play a                 # Start playing
6. tree exit              # Return to root for next track
```

---

### Workflow 2: Professional Loop Transition

```bash
# Goal: Seamless loop-based transition from A to B

# Setup deck A loop
1. play a                 # Start deck A
2. loop in a              # Mark loop start (e.g., at drop)
3. loop out a             # Mark loop end (4-8 beats)
4. loop activate a        # Enable loop
5. hotcue 1 a             # Save loop position

# Bring in deck B
6. tree enter             # Find next track
7. load b                 # Load to deck B
8. sync b                 # Match BPM
9. volume b 50%           # Start at half volume
10. play b                # Start deck B

# Transition
11. eq a bass 0           # Cut bass from A
12. volume b 100%         # Bring up B
13. eq b bass 0           # Cut B bass briefly
14. loop off a            # Release A loop
15. eq a bass 50%         # Restore A bass
16. crossfade b           # Move to deck B
17. stop a                # Stop deck A
```

---

### Workflow 3: Creative Beatjump Performance

```bash
# Goal: Dynamic stuttering effect

1. play a
2. beatjump back 1 a      # Jump back 1 beat
3. beatjump forward 1 a   # Jump forward (repeat for stutter)
4. beatjump back 4 a      # Jump back 4 (phrase repeat)
5. beatjump forward 4 a   # Continue
```

---

## 🛠️ Troubleshooting by Category

### Transport Not Working
- [ ] Track loaded in deck?
- [ ] Deck in focus?
- [ ] Check CC mapping: 20=A, 21=B

### Browser Navigation Not Working
- [ ] Press F3 to open browser
- [ ] Tree panel visible?
- [ ] Correct view selected?

### Loops Not Working
- [ ] Track playing?
- [ ] Loop in/out set correctly?
- [ ] Loop size appropriate? (4-8 beats recommended)

### Hotcues Not Working
- [ ] Deck loaded with track?
- [ ] Try setting hotcue manually first to verify Traktor config
- [ ] Check if hotcues already full (max 8 per deck)

### Beatjump Not Accurate
- [ ] Beat grid analyzed correctly in Traktor?
- [ ] Quantize enabled for grid snap?
- [ ] Track has stable BPM?

---

## 📊 Testing Checklist

Use this checklist before a live set:

### Pre-Set Validation
```bash
# Run interactive test
python test_midi_mapping_interactive.py

# Verify critical commands:
- [ ] Play/Pause both decks
- [ ] Load tracks
- [ ] Crossfader movement
- [ ] Volume controls
- [ ] EQ kill/boost
- [ ] Sync function
- [ ] Tree navigation (F3 view)
- [ ] Loop activation
- [ ] At least 2 hotcues per deck
- [ ] Beatjump forward/back
```

### Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Commands delayed | Check MIDI buffer in preferences |
| Wrong deck responds | Re-import TSI, verify CC numbers |
| Tree nav doesn't work | Press F3, click Tree panel |
| Loops jump incorrectly | Analyze beat grid in Traktor |
| Hotcues don't trigger | Check deck has track loaded |

---

## 📚 Additional Resources

- **MIDI Reference**: See [COMPLETE_MIDI_MAPPING.md](COMPLETE_MIDI_MAPPING.md)
- **Python API**: Check [traktor_control.py](traktor_control.py) MIDI_MAP dictionary
- **Test Tool**: Run [test_midi_mapping_interactive.py](test_midi_mapping_interactive.py)
- **TSI File**: Import [AI_DJ_Perfect_Mapping.tsi](AI_DJ_Perfect_Mapping.tsi) in Traktor

---

**Version**: 1.0
**Last Updated**: 2025-01-02
**Status**: ✅ Complete with all 75+ commands documented
