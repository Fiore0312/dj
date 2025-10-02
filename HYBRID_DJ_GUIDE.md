# 🎛️ Hybrid DJ Master - Complete Guide

## Overview

**Hybrid DJ Master** is a revolutionary DJ system that combines the best of both worlds:
- **AI Autonomy**: Claude Agent SDK for intelligent decision-making
- **Manual Control**: Full human override capability at any time
- **Assisted Mode**: AI suggests, you approve

### Key Features

✅ **3 Operation Modes** (switch anytime):
- **MANUAL**: You control everything (pattern-based commands)
- **AUTONOMOUS**: AI DJs autonomously, you provide feedback
- **ASSISTED**: AI suggests actions, you approve/reject

✅ **Complete DJ Control**:
- Playback (play, stop, pause)
- Mixing (crossfader, volume, sync)
- EQ (high/mid/low per deck)
- FX (4 independent units)
- Pitch control
- Cue points
- Master volume
- Emergency stop

✅ **Professional MIDI Integration**:
- Direct Traktor Pro control via macOS IAC Driver
- Real-time MIDI communication (<10ms latency)
- Extended command mapping (40+ controls)

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│         HYBRID DJ MASTER CONTROLLER                 │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   MANUAL     │  │  AUTONOMOUS  │  │ ASSISTED │ │
│  │    MODE      │  │    MODE      │  │   MODE   │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │
│         │                 │                 │       │
│         └─────────────────┴─────────────────┘       │
│                           │                         │
└───────────────────────────┼─────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
    ┌───────▼────────┐            ┌────────▼────────┐
    │  Simple DJ     │            │  Claude Agent   │
    │  Controller    │            │      SDK        │
    │ (Pattern-based)│            │  (AI Tools)     │
    └───────┬────────┘            └────────┬────────┘
            │                              │
            └──────────────┬───────────────┘
                           │
                  ┌────────▼────────┐
                  │ Traktor Control │
                  │  (MIDI Layer)   │
                  └────────┬────────┘
                           │
                   ┌───────▼────────┐
                   │  Traktor Pro 3 │
                   │ (via IAC Driver)│
                   └────────────────┘
```

### Component Details

#### 1. **Autonomous DJ Master** (`autonomous_dj_master.py`)
- Main orchestrator
- Mode switching logic
- Command routing
- AI monitoring loop
- Session state management

#### 2. **Simple DJ Controller** (`simple_dj_controller.py`)
- Pattern-based command parsing
- Rule-based control (no AI)
- 40+ natural language commands
- Regex matching for flexibility

#### 3. **Claude Agent SDK Integration**
- 16 custom `@tool` decorators
- AI decision-making
- Tool calling for MIDI actions
- Context-aware reasoning

#### 4. **Traktor Control** (`traktor_control.py`)
- MIDI abstraction layer
- Complete CC mapping
- GIL-safe threading
- Error handling

---

## Operation Modes

### 1. MANUAL Mode (Default)

**Description**: Full human control using natural language commands.

**How it works**:
- Pattern matching on user input
- Direct MIDI command execution
- No AI involvement
- Instant response

**Example Commands**:
```
play deck A
mix to B in 16 beats
set crossfader to 50%
search techno
eq high deck A to 80%
kill bass deck B
set fx1 to 50%
pitch deck A +2%
emergency stop
```

**Use Cases**:
- Traditional DJ workflow
- No internet connection
- Low latency requirement
- Learning the system

---

### 2. AUTONOMOUS Mode

**Description**: AI takes full control, you provide context/feedback.

**How it works**:
- AI monitors session state every 5 seconds
- Analyzes: venue, energy, crowd, track position
- Makes decisions autonomously
- Uses Claude SDK tools to execute actions

**Switching**:
```
/auto
```

**AI Monitoring Loop**:
```python
while session.ai_monitoring:
    await asyncio.sleep(5)  # Every 5 seconds

    # AI analyzes current state
    prompt = """
    Current State:
    - Venue: club
    - Energy: 75%
    - Crowd: dancing
    - Deck A: 80% played
    - Deck B: Empty

    Should I take any action?
    """

    # AI decides and acts
    ai_decision = await query(prompt, tools=[...])
```

**User Role**:
- Provide context: "energy is high", "crowd is dancing"
- Override anytime with `/manual`
- Emergency stop always available

**Use Cases**:
- Continuous DJ sessions
- Autopilot mode
- Testing AI capabilities
- Hands-free operation

---

### 3. ASSISTED Mode

**Description**: AI suggests actions, you approve before execution.

**How it works**:
- You give natural language request
- AI analyzes and suggests ONE action
- You approve (`yes`) or reject
- Only approved actions are executed

**Switching**:
```
/assist
```

**Example Workflow**:
```
You: mix to deck B with smooth transition
AI: 💡 Suggestion:
    I recommend:
    1. Load next compatible track to Deck B
    2. Sync Deck B to Deck A
    3. Gradual crossfade over 16 beats
    4. Cut bass on Deck A during transition

    [Execute this? Type 'yes' to approve]

You: yes
AI: ✅ Executing approved actions...
```

**Use Cases**:
- Learning from AI
- Safety-critical sessions
- Hybrid human-AI collaboration
- Building trust in AI

---

## Command Reference

### System Commands (All Modes)

| Command | Description |
|---------|-------------|
| `/manual` | Switch to MANUAL mode |
| `/auto` | Switch to AUTONOMOUS mode (requires API key) |
| `/assist` | Switch to ASSISTED mode (requires API key) |
| `/status` | Show session state and metrics |
| `/help` | Show all available commands |
| `/quit` | Exit system |

---

### Manual Commands (MANUAL Mode)

#### Playback
```
play deck A/B
stop deck A/B
pause deck A/B
```

#### Loading
```
load track to deck A
browse up/down
search [query]
```

#### Mixing
```
mix to B
crossfade to 50%
sync deck B
```

#### Volume
```
set volume deck A to 80%
volume A max
volume B half
```

#### EQ Controls
```
eq high deck A to 80%
eq mid deck B to 50%
eq low deck A to 20%
kill bass deck B
kill high deck A
```

#### Effects
```
set fx1 to 50%
fx2 wet 80%
fx3 dry
```

#### Pitch/Tempo
```
pitch deck A +2%
pitch deck B -1.5%
tempo A up
```

#### Cue Points
```
cue 1 deck A
trigger cue 2 deck B
```

#### Master & Emergency
```
set master volume to 80%
master 100%
emergency stop
panic
```

#### Macros
```
beatmatch A and B
```

---

### Claude SDK Tools (AUTONOMOUS/ASSISTED Modes)

AI can use these tools directly:

| Tool | Description | Parameters |
|------|-------------|------------|
| `load_track_to_deck` | Load selected track | `deck: A/B` |
| `play_deck` | Start playing | `deck: A/B` |
| `stop_deck` | Stop playing | `deck: A/B` |
| `set_crossfader` | Set crossfader | `position: 0.0-1.0` |
| `set_deck_volume` | Set deck volume | `deck: A/B, volume: 0.0-1.0` |
| `set_eq` | Set EQ band | `deck: A/B, band: high/mid/low, level: 0.0-1.0` |
| `set_fx` | Set FX mix | `unit: 1-4, mix: 0.0-1.0` |
| `sync_deck` | Sync to master | `deck: A/B` |
| `set_pitch` | Adjust pitch | `deck: A/B, amount: -1.0 to 1.0` |
| `trigger_cue` | Trigger cue point | `deck: A/B, point: 1-4` |
| `set_master_volume` | Set master out | `level: 0.0-1.0` |
| `kill_eq_band` | Kill EQ band | `deck: A/B, band: high/mid/low` |
| `beatmatch_decks` | Auto beatmatch | `deck1: A/B, deck2: A/B` |
| `search_music_library` | Search tracks | `query: string, limit: int` |
| `get_session_state` | Get state | None |
| `emergency_stop` | EMERGENCY STOP | None |

---

## Installation & Setup

### Prerequisites

1. **macOS** with Audio MIDI Setup
2. **Traktor Pro 3** installed
3. **Python 3.8+**
4. **Music library** at `~/Music`

### Step 1: Install Dependencies

```bash
cd /Users/Fiore/dj
source dj_env/bin/activate
pip install -r requirements_simple.txt
```

### Step 2: Install Claude SDK (for AI modes)

```bash
pip install claude-agent-sdk
```

### Step 3: Set API Key (for AI modes)

```bash
# Option 1: Environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# Option 2: Add to .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

### Step 4: Configure macOS IAC Driver

1. Open **Audio MIDI Setup** (⌘+Space → "Audio MIDI Setup")
2. Window → **Show MIDI Studio**
3. Double-click **IAC Driver**
4. Check "**Device is online**"
5. Ensure "**Bus 1**" exists

### Step 5: Import Traktor Mapping

1. Open **Traktor Pro 3**
2. Preferences → **Controller Manager**
3. Click **Import** → Select `traktor/AI_DJ_Complete.tsi`
4. Ensure mapping is **enabled**

---

## Quick Start

### Easiest Way: Launcher Script

```bash
cd /Users/Fiore/dj
./run_hybrid_dj.sh
```

The launcher will:
- ✅ Check virtual environment
- ✅ Verify dependencies
- ✅ Detect API keys
- ✅ Check IAC Driver
- ✅ Count music library
- ✅ Start the system

### Manual Start

```bash
cd /Users/Fiore/dj
source dj_env/bin/activate
python autonomous_dj_master.py
```

---

## Usage Examples

### Example 1: Manual DJ Session

```
$ ./run_hybrid_dj.sh

============================================================
🎛️  AUTONOMOUS DJ MASTER - Hybrid Control System
============================================================

Current Mode: MANUAL
AI Available: ✅ YES

📋 MODE COMMANDS:
  /manual     - Switch to MANUAL mode (default)
  /auto       - Switch to AUTONOMOUS mode (AI decides)
  /assist     - Switch to ASSISTED mode (AI suggests)
  /status     - Show current session state
  /help       - Show all available commands
  /quit       - Exit system

💡 In MANUAL mode, use natural language commands:
  'play deck A', 'mix to B', 'search techno', etc.

============================================================

DJ Command> search house techno
🔍 Found 10 tracks:
1. Amelie Lens - In My Mind (132 BPM, Techno)
2. Charlotte de Witte - Sgadi Li Mi (140 BPM, Techno)
3. Adam Beyer - Your Mind (128 BPM, Tech House)
...

DJ Command> play deck A
▶️ Deck A playing

DJ Command> set volume A to 80%
🔊 Deck A volume: 80%

DJ Command> eq low A to 60%
🎚️ Deck A EQ LOW: 60%

DJ Command> mix to B
🎯 Beatmatching Deck A ↔ Deck B
✓ Deck B synced
✓ Volumes matched at 75%
✓ EQs reset to neutral
✅ Beatmatch complete!
```

---

### Example 2: Autonomous AI Session

```
DJ Command> /auto
✅ Mode switched: MANUAL → AUTONOMOUS
🤖 AI monitoring started (watching session every 5s)

DJ Command> energy is high, crowd is dancing

🤖 AI: Analyzing session state...
🤖 AI: Energy level detected as HIGH. Loading uptempo track.
      Using tool: search_music_library(query="140 BPM techno energetic")
      Found: "Amelie Lens - Contradiction" (140 BPM)

🤖 AI: Loading track to Deck B...
      Using tool: load_track_to_deck(deck="B")
      ✅ Track loaded

🤖 AI: Deck A at 75% completion. Preparing smooth transition.
      Using tool: sync_deck(deck="B")
      ✅ Deck B synced

🤖 AI: Starting gradual crossfade...
      Using tool: set_crossfader(position=0.3)
      Using tool: set_crossfader(position=0.5)
      Using tool: set_crossfader(position=0.7)
      ✅ Transition complete

[5 seconds later]

🤖 AI: Monitoring session, no action required.

DJ Command> crowd response is negative

🤖 AI: Crowd response negative. Adjusting energy down.
      Searching for: "125 BPM melodic techno"
      ...
```

---

### Example 3: Assisted Mode Session

```
DJ Command> /assist
✅ Mode switched: MANUAL → ASSISTED
💡 AI will suggest actions, you approve/reject

DJ Command> I want to build energy gradually

💡 AI Suggestion:
   To build energy gradually, I recommend:

   1. Search for track with +5 BPM higher than current
   2. Load to Deck B
   3. Sync and beatmatch
   4. Long crossfade (32 beats)
   5. Gradually increase high EQ on new track

   This creates smooth energy build without jarring transition.

   [Execute this? Type 'yes' to approve]

DJ Command> yes

✅ Executing approved actions...
   🔍 Searching for 135 BPM tracks...
   ✅ Found "Adam Beyer - Your Mind" (135 BPM)
   ✅ Loading to Deck B...
   ✅ Syncing Deck B...
   🎚️ Starting gradual crossfade...
   🎚️ Increasing high EQ on Deck B...
   ✅ Energy build complete!
```

---

## Session State

### Tracked Metrics

The system tracks:

- **Mode**: current operation mode
- **AI Monitoring**: active/inactive
- **Venue Type**: club, festival, bar, etc.
- **Event Type**: party, concert, chill session
- **Energy Level**: 0.0 to 1.0
- **Crowd Response**: positive, neutral, negative
- **Current Tracks**: Deck A and B
- **Track Position**: 0.0 to 1.0 for each deck
- **Decision Metrics**: total, approved, rejected

### View State

```
DJ Command> /status

📊 AUTONOMOUS DJ MASTER - System Status
============================================================

🎛️ Operation Mode: AUTONOMOUS
🤖 AI Monitoring: ✅ Active
⏱️  Monitoring Interval: 5s

📍 Session Context:
  Venue: club
  Event: party
  Energy Level: 75%
  Crowd Response: positive

🎵 Decks:
  Deck A: Amelie Lens - In My Mind (80.0%)
  Deck B: Charlotte de Witte - Sgadi Li Mi (15.0%)

📈 Performance:
  Total Decisions: 47
  Approved: 42
  Rejected: 5

============================================================
```

---

## MIDI Mapping Reference

### Complete CC Mapping

| Control | Channel | CC | Range |
|---------|---------|-----|-------|
| Deck A Play | 1 | 20 | 0-127 |
| Deck B Play | 1 | 21 | 0-127 |
| Deck A Volume | 1 | 28 | 0-127 |
| Deck B Volume | 1 | 29 | 0-127 |
| Crossfader | 1 | 32 | 0-127 |
| Master Volume | 1 | 33 | 0-127 |
| Deck A EQ High | 1 | 34 | 0-127 |
| Deck A EQ Mid | 1 | 35 | 0-127 |
| Deck A EQ Low | 1 | 36 | 0-127 |
| Deck B EQ High | 1 | 50 | 0-127 |
| Deck B EQ Mid | 1 | 51 | 0-127 |
| Deck B EQ Low | 1 | 52 | 0-127 |
| Deck A Sync | 1 | 41 | 0-127 |
| Deck B Sync | 1 | 42 | 0-127 |
| Deck A Pitch | 1 | 45 | 0-127 |
| Deck B Pitch | 1 | 46 | 0-127 |
| Deck A Cue | 1 | 24 | 0-127 |
| Deck B Cue | 1 | 25 | 0-127 |
| FX1 Dry/Wet | 4 | 100 | 0-127 |
| FX2 Dry/Wet | 4 | 101 | 0-127 |
| FX3 Dry/Wet | 4 | 102 | 0-127 |
| FX4 Dry/Wet | 4 | 103 | 0-127 |
| Emergency Stop | 3 | 80 | 0-127 |

---

## Troubleshooting

### Issue: AI modes not available

**Symptoms**:
```
⚠️  AI MODES DISABLED
To enable AI: export ANTHROPIC_API_KEY=your-key
Only MANUAL mode available
```

**Solution**:
```bash
# Install Claude SDK
pip install claude-agent-sdk

# Set API key
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Or add to .env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

---

### Issue: MIDI connection failed

**Symptoms**:
```
❌ Failed to connect to Traktor
```

**Solutions**:

1. **Check IAC Driver**:
   - Open Audio MIDI Setup
   - Verify "IAC Driver" is online
   - Ensure "Bus 1" exists

2. **Restart Traktor**:
   - Quit Traktor Pro
   - Re-open and verify MIDI is enabled

3. **Check MIDI ports**:
   ```bash
   python3 -c "import rtmidi; m=rtmidi.MidiOut(); print(m.get_ports())"
   ```
   Should show: `['IAC Driver Bus 1']`

---

### Issue: Commands not working in MANUAL mode

**Symptoms**:
```
❌ Unknown command: play a
```

**Solution**:

Commands use pattern matching. Try variations:
- `play deck A` (explicit)
- `play A` (short)
- `start deck A` (synonym)
- `fai partire deck A` (Italian)

Check available commands: `/help`

---

### Issue: AI not taking actions in AUTONOMOUS mode

**Symptoms**:
```
🤖 AI: Monitoring session, no action required.
[Never does anything]
```

**Possible Causes**:

1. **No context provided**:
   - Provide feedback: "energy is low", "crowd dancing"

2. **Session state unclear**:
   - Check with `/status`
   - Update venue/event context

3. **Tracks missing**:
   - Ensure music library scanned
   - Load initial track manually

---

### Issue: High API costs in AUTONOMOUS mode

**Symptoms**:
```
💸 Anthropic API usage too high
```

**Solutions**:

1. **Increase monitoring interval**:
   ```python
   session.monitoring_interval = 10  # 10 seconds instead of 5
   ```

2. **Switch to ASSISTED mode**:
   ```
   /assist
   ```
   (AI only runs when you ask)

3. **Use MANUAL mode**:
   ```
   /manual
   ```
   (No AI costs)

---

## Performance Tips

### Optimize for Speed

1. **MANUAL mode**: Fastest, no AI latency
2. **Pre-scan library**: Run `music_library.py` before session
3. **Reduce monitoring interval**: If AI too slow in AUTONOMOUS

### Optimize for Quality

1. **AUTONOMOUS mode**: Best AI decisions
2. **Provide rich context**: Venue, energy, crowd response
3. **Let AI monitor longer**: Better pattern recognition

### Optimize for Cost

1. **Use ASSISTED mode**: AI only when needed
2. **Start with MANUAL**: Switch to AI for complex mixes
3. **Increase interval**: 10s instead of 5s

---

## Advanced Usage

### Custom Session Context

```python
# Modify session state programmatically
session.venue_type = "underground_club"
session.event_type = "techno_night"
session.energy_level = 0.9
session.crowd_response = "euphoric"
```

### Custom Monitoring Interval

```python
# Check every 10 seconds instead of 5
session.monitoring_interval = 10
```

### Custom Auto-Approve Threshold

```python
# Only auto-approve high-confidence decisions
session.auto_approve_threshold = 0.95
```

---

## API Reference

### AutonomousDJMaster Class

```python
class AutonomousDJMaster:
    async def start()
    async def process_command(command: str) -> str
    def stop()

    # Internal
    async def _switch_mode(mode: OperationMode) -> str
    async def _process_manual_command(cmd: str) -> str
    async def _process_autonomous_context(ctx: str) -> str
    async def _process_assisted_command(cmd: str) -> str
    async def _autonomous_monitoring_loop()
    async def _ai_autonomous_decision()
```

### SessionState Dataclass

```python
@dataclass
class SessionState:
    mode: OperationMode = OperationMode.MANUAL
    ai_monitoring: bool = False
    monitoring_interval: int = 5
    auto_approve_threshold: float = 0.85

    venue_type: str = "club"
    event_type: str = "party"
    energy_level: float = 0.5
    crowd_response: str = "neutral"

    current_deck_a: Optional[str] = None
    current_deck_b: Optional[str] = None
    deck_a_position: float = 0.0
    deck_b_position: float = 0.0

    total_decisions: int = 0
    approved_decisions: int = 0
    rejected_decisions: int = 0
```

---

## FAQ

### Q: Can I switch modes during a live session?

**A**: Yes! Use `/manual`, `/auto`, or `/assist` anytime.

---

### Q: Does AUTONOMOUS mode require internet?

**A**: Yes, it calls Anthropic's Claude API. MANUAL mode works offline.

---

### Q: How much does AI mode cost?

**A**: ~$3 per 1M input tokens. Typical session:
- 5s interval = 720 decisions/hour
- ~200 tokens per decision
- 144K tokens/hour ≈ **$0.43/hour**

---

### Q: Can AI make mistakes?

**A**: Yes. That's why we have:
- ASSISTED mode (approve before execution)
- Manual override (switch to MANUAL anytime)
- Emergency stop (always available)

---

### Q: What happens if Traktor crashes?

**A**: System detects connection loss and stops sending MIDI. Restart Traktor and reconnect.

---

### Q: Can I use this with other DJ software?

**A**: Currently Traktor-only. MIDI mappings would need adaptation for Serato/Rekordbox.

---

## Credits

Built with:
- **Claude Agent SDK** v0.1.0 (Anthropic)
- **python-rtmidi** v1.4.9 (MIDI communication)
- **mutagen** v1.46.0 (Music metadata)
- **Traktor Pro 3** (Native Instruments)

---

## License

This project is open-source and educational. Use at your own risk in live performances.

---

## Support

Issues? Check:
1. This guide's Troubleshooting section
2. `/help` command in the app
3. GitHub issues (if applicable)

**Happy DJing! 🎧🎛️🤖**
