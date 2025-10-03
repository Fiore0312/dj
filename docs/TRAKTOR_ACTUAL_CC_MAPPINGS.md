# TRAKTOR PRO 3 - ACTUAL CC MAPPINGS

**Source**: Discovered by user testing with IAC Driver Bus 1, Channel 1
**File**: cc_mapping_found.txt
**Status**: ✅ CONFIRMED WORKING

---

## WORKING CC MAPPINGS (Channel 1)

### Transport & Playback

| CC | Function | Notes |
|----|----------|-------|
| **20** | **Play/Pause Deck A** | Confirmed working |
| **21** | **Play/Pause Deck B** | Confirmed working |
| **24** | **Sync/Grid Deck A** | Aligns track to nearest grid line |
| **25** | **Sync/Grid Deck B** | Aligns track to nearest grid line |
| **39** | **Cue Deck A** | Flash/blink track in deck A |
| **80-87** | **MAP Button Deck A** | Toggle MAP mode (8 CCs, all do same thing) |
| **89-95** | **MAP Button Deck B** | Toggle MAP mode (7 CCs, all do same thing) |

### Volume & Mixing

| CC | Function | Notes |
|----|----------|-------|
| **28** | **Volume Deck A** | Confirmed working |
| **29** | **⚠️ ERROR** | Controls BOTH Volume Deck B AND Pitch Deck B - needs fixing! |
| **32** | **Crossfader** | Confirmed working (left, right, center) |
| **33** | **Master Volume** | Main output volume |

### EQ Controls

| CC | Function | Notes |
|----|----------|-------|
| **34** | **EQ High Deck A** | High frequency knob |
| **35** | **EQ Mid Deck A** | Mid frequency knob |
| **36** | **EQ Low Deck A** | Low frequency knob |
| **50** | **EQ High Deck B** | High frequency knob |
| **51** | **EQ Mid Deck B** | Mid frequency knob |
| **52** | **EQ Low Deck B** | Low frequency knob |

### Pitch/Tempo Control

| CC | Function | Notes |
|----|----------|-------|
| **40** | **Pitch Control Deck B** | Moves pitch slider all the way down |
| **41** | **Pitch Control Deck A** | Pitch fader control |
| **42** | **Pitch Control Deck B** | Moves to center then down again |

### Browser & Track Selection

| CC | Function | Notes |
|----|----------|-------|
| **37** | **Scroll Track List** | Scrolls current track list |
| **38** | **Scroll Track List** | Alternative scroll control |
| **55** | **Scroll Track Collection Tree** | Navigate folder tree |
| **56** | **Scroll Track Collection Tree** | Alternative tree navigation |
| **59** | **Open Artists Folder** | Opens "Artists" in track collection |
| **60** | **Open Artists Folder** | Same as CC 59 |

### Unmapped CCs (Available for Assignment)

The following CCs showed no response and are available for MIDI Learn:

- CC 1-6, 7-8, 9-13, 14-19, 22-23, 26-27, 30-31
- CC 43-49, 53-54, 57-58, 61-79
- CC 88, 96-127

---

## IMPORTANT NOTES

### ⚠️ Known Issues

1. **CC 29 Double Assignment**:
   - Controls BOTH Volume Deck B AND Pitch Control Deck B
   - This needs to be fixed in Traktor Controller Manager
   - Remove one of the assignments using MIDI Learn

2. **Redundant MAP Assignments**:
   - CC 80-87 (8 CCs) all toggle MAP button Deck A
   - CC 89-95 (7 CCs) all toggle MAP button Deck B
   - Consider removing redundant assignments to free up CCs

### 📋 Missing Critical Functions

The following essential DJ functions are **NOT YET MAPPED**:

#### Essential Controls Needed:
- ❌ **Load Track to Deck A**
- ❌ **Load Track to Deck B**
- ❌ **Hotcue 1-8 for Deck A**
- ❌ **Hotcue 1-8 for Deck B**
- ❌ **Loop In/Out**
- ❌ **Loop Size Controls**
- ❌ **Beatjump Forward/Back**
- ❌ **Sync Button** (musical sync)
- ❌ **Master Clock Assignment**
- ❌ **Filter/FX Controls**
- ❌ **Sample Deck Triggers**

---

## NEXT STEPS

### 1. Fix Conflicts
```
In Traktor Controller Manager:
1. Remove Volume Deck B from CC 29 (keep Pitch Control OR Volume, not both)
2. Clean up redundant MAP button assignments
```

### 2. Add Essential Commands via MIDI Learn

Use the interactive discovery tool to map remaining functions:
```bash
python test_cc_discovery.py
```

Recommended mappings for available CCs:

| Available CC | Suggested Mapping |
|--------------|-------------------|
| CC 1-8 | Hotcue 1-8 Deck A |
| CC 9-16 | Hotcue 1-8 Deck B |
| CC 43 | Load Track to Deck A |
| CC 44 | Load Track to Deck B |
| CC 45 | Loop In |
| CC 46 | Loop Out |
| CC 47 | Loop Size /2 |
| CC 48 | Loop Size x2 |
| CC 49 | Beatjump +1 |
| CC 53 | Beatjump -1 |
| CC 54 | Sync Deck A |
| CC 57 | Sync Deck B |
| CC 58 | Filter Deck A |
| CC 61 | Filter Deck B |

### 3. Export Complete Mapping

Once all commands are mapped, export from Traktor:
```
Preferences → Controller Manager →
Select "Generic MIDI" → Export → Save as "traktor_complete_mapping.tsi"
```

Then analyze with:
```bash
python extract_traktor_mappings.py traktor_complete_mapping.tsi
```

---

## UPDATE traktor_control.py

Based on discovered mappings, update the MIDI_MAP dictionary:

```python
MIDI_MAP = {
    # Transport - Deck A
    'deck_a_play': (MIDIChannel.DECK_CONTROL, 20),
    'deck_a_cue': (MIDIChannel.DECK_CONTROL, 39),
    'deck_a_sync_grid': (MIDIChannel.DECK_CONTROL, 24),

    # Transport - Deck B
    'deck_b_play': (MIDIChannel.DECK_CONTROL, 21),
    'deck_b_sync_grid': (MIDIChannel.DECK_CONTROL, 25),

    # Volume & Mixing
    'deck_a_volume': (MIDIChannel.DECK_CONTROL, 28),
    'deck_b_volume': (MIDIChannel.DECK_CONTROL, 29),  # ⚠️ CONFLICT - needs fix
    'crossfader': (MIDIChannel.DECK_CONTROL, 32),
    'master_volume': (MIDIChannel.DECK_CONTROL, 33),

    # EQ - Deck A
    'deck_a_eq_high': (MIDIChannel.DECK_CONTROL, 34),
    'deck_a_eq_mid': (MIDIChannel.DECK_CONTROL, 35),
    'deck_a_eq_low': (MIDIChannel.DECK_CONTROL, 36),

    # EQ - Deck B
    'deck_b_eq_high': (MIDIChannel.DECK_CONTROL, 50),
    'deck_b_eq_mid': (MIDIChannel.DECK_CONTROL, 51),
    'deck_b_eq_low': (MIDIChannel.DECK_CONTROL, 52),

    # Pitch Control
    'deck_a_pitch': (MIDIChannel.DECK_CONTROL, 41),
    'deck_b_pitch': (MIDIChannel.DECK_CONTROL, 40),  # or 42?

    # Browser
    'browser_scroll_tracks': (MIDIChannel.DECK_CONTROL, 37),
    'browser_scroll_tree': (MIDIChannel.DECK_CONTROL, 55),
    'browser_open_artists': (MIDIChannel.DECK_CONTROL, 59),
}
```

---

**Last Updated**: 2025-10-03
**Discovery Method**: Interactive testing with test_cc_discovery.py
**Tested On**: Traktor Pro 3 with IAC Driver Bus 1
