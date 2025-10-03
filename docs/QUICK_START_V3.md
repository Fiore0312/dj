# 🚀 Quick Start Guide - Autonomous DJ System v3.0

## TL;DR - Get Started in 5 Minutes

```bash
# 1. Ensure Traktor is running with IAC Driver enabled
# 2. Run the autonomous system
python3 autonomous_dj_agent_v3.py

# That's it! The system will:
# ✅ Parse your Traktor collection (5822 tracks)
# ✅ Select first compatible track
# ✅ Navigate to exact position
# ✅ Start mixing autonomously
```

---

## 📋 Prerequisites

### 1. macOS IAC Driver Setup
**Required**: Traktor needs MIDI connection

```bash
# Open Audio MIDI Setup
open "/Applications/Utilities/Audio MIDI Setup.app"

# Enable IAC Driver:
# 1. Window → Show MIDI Studio
# 2. Double-click "IAC Driver"
# 3. Check "Device is online"
# 4. Ensure "Bus 1" exists
```

### 2. Traktor Pro 3 Setup
**Required**: Traktor must be running

1. **Launch Traktor Pro 3**
2. **Enable MIDI**: Preferences → Controller Manager
3. **Verify collection.nml exists**:
   - Location: `~/Documents/Native Instruments/Traktor 3.11.1/collection.nml`
   - Should contain your music library

### 3. Python Dependencies
**Required**: Install packages

```bash
pip install python-rtmidi mutagen aiohttp

# Optional (for AI features)
pip install claude-agent-sdk
```

---

## 🎯 Usage Scenarios

### Scenario 1: Full Autonomous Session (Recommended)

**What it does**: Sistema completamente autonomo che seleziona tracce, naviga e mixa automaticamente

```bash
python3 autonomous_dj_agent_v3.py
```

**Output**:
```
🎧🎧🎧 ... 🎧🎧🎧
AUTONOMOUS DJ SYSTEM v3.0
Complete solution with Traktor collection integration
🎧🎧🎧 ... 🎧🎧🎧

🚀 Initializing Autonomous DJ System v3.0...
✅ Connected to Traktor via MIDI
✅ Collection parsed: 5822 tracks
✅ Smart Navigator ready
✅ Intelligent Track Selector ready
🎉 System initialized successfully!

🎧 STARTING AUTONOMOUS DJ SESSION
Venue: club
Event: party
Duration: 1.0 hours

🎵 Selecting first track...
   Loading: Artist - Title
🎯 Navigating to: Artist - Title
   Strategy: down, Steps: 4280
✅ Track loaded successfully in Deck A
▶️  Starting playback...

🔄 Loop #1
🎯 Time to prepare next track...
✅ Selected: Next Artist - Next Title
📀 Loading to Deck B...
🎚️  Starting transition...
✅ Transition complete!
```

**Features**:
- ✅ Automatic track selection (BPM/key compatible)
- ✅ Deterministic navigation (exact position)
- ✅ Smooth transitions (8s crossfade)
- ✅ Energy curve following (warm up → peak)
- ✅ Anti-repetition (history tracking)

**Press Ctrl+C to stop**

---

### Scenario 2: Test Individual Components

#### Test Traktor Collection Parser
```bash
python3 traktor_collection_parser.py
```

**Output**:
```
📂 Collection found: /Users/Fiore/Documents/.../collection.nml
✅ Collection parsed successfully!

📊 Collection Statistics:
   Total tracks: 5822
   Tracks with BPM: 4520
   Tracks with Key: 2299
   Average BPM: 111.9

🎵 Sample Tracks:
   Artist - Title
   BPM: 128.0  Key: 8A
   Position: 0
```

**Use case**: Verify collection parsing works

---

#### Test Smart Navigator
```bash
python3 smart_traktor_navigator.py
```

**Output**:
```
🧭 Smart Traktor Navigator Test
✅ Collection loaded: 5822 tracks
🎛️  Connecting to Traktor...
✅ Connected

🎯 Testing navigation path calculation...
   Target: 50
   Strategy: down
   Steps: 50
   Estimated time: 4.00s

🚀 Testing actual navigation...
   Test track: Artist - Title
   Position: 50

✅ Navigation test SUCCESSFUL!

📊 Navigation Statistics:
   Success rate: 100.0%
   Total navigations: 1
   Avg steps per navigation: 50.0
```

**Use case**: Verify navigation system works

---

### Scenario 3: Python API Usage

#### Load Specific Track
```python
import asyncio
from traktor_collection_parser import TraktorCollectionParser
from smart_traktor_navigator import SmartTraktorNavigator, load_track_by_path
from traktor_control import TraktorController, DeckID
from config import DJConfig

async def main():
    # Setup
    config = DJConfig()
    traktor = TraktorController(config)
    traktor.connect_with_gil_safety()

    parser = TraktorCollectionParser()
    parser.parse_collection()

    # Find track by artist/title
    all_tracks = parser.get_all_tracks()
    my_track = [t for t in all_tracks if "Artist Name" in t.artist][0]

    # Load to Deck A
    navigator = SmartTraktorNavigator(traktor, parser)
    await navigator.navigate_to_track(my_track, DeckID.A, verify=True)

    print(f"✅ Loaded: {my_track.artist} - {my_track.title}")

asyncio.run(main())
```

---

#### Get Compatible Tracks
```python
from traktor_collection_parser import TraktorCollectionParser

parser = TraktorCollectionParser()
parser.parse_collection()

# Get track
all_tracks = parser.get_all_tracks()
current = all_tracks[0]

# Find compatible tracks
compatible = parser.get_compatible_tracks(current, bpm_tolerance=6.0)

print(f"Current: {current.artist} - {current.title}")
print(f"BPM: {current.bpm}  Key: {current.get_camelot_key()}")
print(f"\nFound {len(compatible)} compatible tracks:")

for track in compatible[:10]:
    print(f"  {track.artist} - {track.title}")
    print(f"    BPM: {track.bpm}  Key: {track.get_camelot_key()}")
```

---

#### Filter by BPM/Key
```python
from traktor_collection_parser import TraktorCollectionParser

parser = TraktorCollectionParser()
parser.parse_collection()

# Get tracks in BPM range
house_tracks = parser.get_tracks_by_bpm_range(120, 130)
print(f"House tracks (120-130 BPM): {len(house_tracks)}")

# Get tracks in specific key
tracks_8a = parser.get_tracks_by_key("8A")
print(f"Tracks in 8A: {len(tracks_8a)}")

# Collection statistics
stats = parser.get_collection_stats()
print(f"\nTop Genres:")
for genre, count in list(stats['genres'].items())[:5]:
    print(f"  {genre}: {count} tracks")
```

---

## 🔧 Troubleshooting

### Issue: "Collection.nml not found"

**Solution 1**: Specify path manually
```python
from traktor_collection_parser import TraktorCollectionParser

parser = TraktorCollectionParser("/path/to/collection.nml")
parser.parse_collection()
```

**Solution 2**: Find collection manually
```bash
# macOS
find ~/Documents -name "collection.nml" 2>/dev/null

# Common locations:
# ~/Documents/Native Instruments/Traktor 3.11.1/collection.nml
# ~/Documents/Native Instruments/Traktor 3/collection.nml
```

---

### Issue: "Failed to connect to Traktor"

**Check**:
1. Traktor is running
2. IAC Driver is enabled (Audio MIDI Setup)
3. IAC Driver "Bus 1" exists

**Test MIDI**:
```bash
python3 -c "
import rtmidi
midi = rtmidi.MidiOut()
ports = midi.get_ports()
print('Available MIDI ports:', ports)
# Should show: ['Driver IAC Bus 1']
"
```

**Solution**: Enable IAC Driver
```bash
# Open Audio MIDI Setup
open "/Applications/Utilities/Audio MIDI Setup.app"

# Window → Show MIDI Studio
# Double-click "IAC Driver"
# Check "Device is online"
```

---

### Issue: "GIL error / Fatal Python error"

**Already Fixed!** v3.0 uses GIL-safe connection

**Verification**:
```python
from traktor_control import TraktorController
from config import DJConfig

config = DJConfig()
traktor = TraktorController(config)

# Use GIL-safe method
success = traktor.connect_with_gil_safety()
print(f"Connected: {success}")
print(f"Simulation mode: {traktor.simulation_mode}")
```

---

### Issue: "Navigation too slow"

**Normal**: Large position deltas take time
- Position 50: ~4 seconds
- Position 500: ~40 seconds
- Position 4280: ~5-6 minutes

**Speed up**: Use reset strategy
```python
# In smart_traktor_navigator.py, line 88-90
# Force reset strategy for all navigations
return NavigationPath(
    strategy=NavigationStrategy.RESET_AND_DOWN,
    steps=target_position,
    ...
)
```

**Future**: Binary search or Traktor search command

---

### Issue: "Track selection not optimal"

**Tune parameters**: Adjust in `autonomous_dj_agent_v3.py`

```python
# Line 490: BPM tolerance
compatible = self.parser.get_compatible_tracks(
    current_track,
    bpm_tolerance=10.0  # Increase from 6.0
)

# Line 560: Energy scoring weight
score += energy_match * 10.0  # Increase from 5.0

# Line 570: Anti-repetition length
recently_played = set(context.played_tracks[-20:])  # Increase from 10
```

---

## 📊 Performance Tips

### Optimization 1: Cache Collection Parse
```python
# First run: Parse and save cache
parser = TraktorCollectionParser()
parser.parse_collection()
parser.save_cache(".traktor_cache.json")

# Subsequent runs: Load cache
parser = TraktorCollectionParser()
if parser.load_cache(".traktor_cache.json"):
    print("✅ Loaded from cache")
else:
    parser.parse_collection()
```

### Optimization 2: Faster Navigation
```python
# Reduce delay between steps (risky - may miss steps)
navigator.navigation_delay = 0.05  # Default: 0.08
```

### Optimization 3: Pre-filter Tracks
```python
# Filter before selection for performance
selector = IntelligentTrackSelector(parser)

# Only consider tracks with BPM and key
valid_tracks = [t for t in parser.get_all_tracks()
                if t.bpm and t.musical_key is not None]

# Use filtered list
# (Modify selector to accept track list)
```

---

## 🎛️ Advanced Configuration

### Custom Energy Curve
```python
from autonomous_dj_agent_v3 import AutonomousDJMasterV3, DJContext

dj = AutonomousDJMasterV3(config)
await dj.initialize()

# Custom energy curve (15 points = 15 segments)
dj.context.target_energy_curve = [
    0.2, 0.3, 0.4, 0.5, 0.6,  # Warm up (33%)
    0.7, 0.8, 0.9, 0.9, 0.9,  # Peak (33%)
    0.8, 0.7, 0.6, 0.5, 0.4   # Cool down (33%)
]

await dj.start_autonomous_session(
    venue="festival",
    event="main_stage",
    duration_hours=3.0
)
```

### Custom Transition Duration
```python
# In autonomous_dj_agent_v3.py, line 980
async def _execute_transition(...):
    steps = 32  # Increase from 16 (16s instead of 8s)
    for i in range(steps + 1):
        ...
        await asyncio.sleep(0.5)  # 16s total
```

### Genre-Specific Sessions
```python
# Pre-filter to specific genre
parser = TraktorCollectionParser()
parser.parse_collection()

house_tracks = [t for t in parser.get_all_tracks()
                if t.genre and "House" in t.genre]

print(f"House tracks: {len(house_tracks)}")

# Create custom selector with filtered tracks
# (Requires modification to IntelligentTrackSelector)
```

---

## 📚 Next Steps

### Learn More
1. Read [AUTONOMOUS_DJ_V3_SUMMARY.md](AUTONOMOUS_DJ_V3_SUMMARY.md) - Complete documentation
2. Read [GIL_FIX_SUMMARY.md](GIL_FIX_SUMMARY.md) - GIL threading fix details
3. Explore source code - Well-commented components

### Extend the System
1. **Add Visual Feedback**: Screenshot + OCR verification
2. **Implement Traktor OSC**: Bidirectional communication
3. **Train ML Model**: Learn user preferences
4. **Build Web Dashboard**: Real-time monitoring
5. **Add Effects Control**: Automatic FX application

### Join Development
- GitHub: (add your repo URL)
- Issues: Report bugs and feature requests
- Contributions: PRs welcome!

---

## 🎉 Success Checklist

- [ ] IAC Driver enabled
- [ ] Traktor running
- [ ] Python dependencies installed
- [ ] Collection.nml found
- [ ] Test: `python3 traktor_collection_parser.py` ✅
- [ ] Test: `python3 smart_traktor_navigator.py` ✅
- [ ] Run: `python3 autonomous_dj_agent_v3.py` 🎉
- [ ] Enjoy autonomous mixing! 🎧

---

**Need Help?**
- Check [AUTONOMOUS_DJ_V3_SUMMARY.md](AUTONOMOUS_DJ_V3_SUMMARY.md) for detailed docs
- Review troubleshooting section above
- Check logs for specific error messages

**System Status**: ✅ Ready for use!

**Happy Mixing!** 🎧🔥