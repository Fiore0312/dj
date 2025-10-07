# Bugs and Fixes Log

**Project**: DJ Agent Coordination System
**Started**: 2025-10-07

---

## 🐛 Bug #001: browser_tree_up/down MIDI_MAP Key Error

**Date Found**: 2025-10-07
**Severity**: 🔴 CRITICAL
**Status**: ✅ FIXED

### Description
Methods `browser_tree_up()` and `browser_tree_down()` in `traktor_control.py` were attempting to access a non-existent MIDI_MAP key `'browser_tree_up_down'`, causing KeyError and preventing browser navigation.

### Location
- **File**: `/Users/Fiore/dj/core/traktor_control.py`
- **Lines**: 737-757 (original)
- **Methods**: `browser_tree_up()`, `browser_tree_down()`

### Symptoms
```python
# Error when calling browser_tree_down()
KeyError: 'browser_tree_up_down'

# Stack trace showed:
  File "test_02_agent_coordination_navigation.py", line 73, in navigate_down
    success = controller.browser_tree_down()
  File "traktor_control.py", line 754, in browser_tree_down
    channel, cc = self.MIDI_MAP['browser_tree_up_down']
KeyError: 'browser_tree_up_down'
```

### Root Cause Analysis
1. **Historical Context**: The code was written expecting a unified bidirectional CC mapping (one CC with different values for UP/DOWN)
2. **Discovery Mismatch**: The `BROWSER_NAVIGATION_DISCOVERY.md` documented separate CCs (CC72 for DOWN, CC73 for UP)
3. **MIDI_MAP State**: The MIDI_MAP was updated with discovered keys (`'browser_tree_down'` and `'browser_tree_up'`) but methods weren't updated
4. **Key Mismatch**:
   - Methods looked for: `'browser_tree_up_down'`
   - MIDI_MAP contained: `'browser_tree_up'` (CC73) and `'browser_tree_down'` (CC72)

### Investigation Steps
1. Ran test and observed KeyError
2. Searched for `browser_tree` in traktor_control.py
3. Found methods using wrong key name
4. Checked MIDI_MAP for actual key names
5. Found correct keys: `'browser_tree_up'` and `'browser_tree_down'`
6. Verified these match BROWSER_NAVIGATION_DISCOVERY.md

### Fix Applied

**Original Code (BROKEN)**:
```python
def browser_tree_up(self, force_direction_value: Optional[int] = None) -> bool:
    """Navigate UP in browser tree using browser_tree_up_down mapping"""
    channel, cc = self.MIDI_MAP['browser_tree_up_down']  # ❌ WRONG KEY
    value = force_direction_value if force_direction_value is not None else 1
    return self._send_midi_command(channel, cc, value, f"Browser Tree UP (value={value})")

def browser_tree_down(self, force_direction_value: Optional[int] = None) -> bool:
    """Navigate DOWN in browser tree using browser_tree_up_down mapping"""
    channel, cc = self.MIDI_MAP['browser_tree_up_down']  # ❌ WRONG KEY
    value = force_direction_value if force_direction_value is not None else 127
    return self._send_midi_command(channel, cc, value, f"Browser Tree DOWN (value={value})")
```

**Fixed Code**:
```python
def browser_tree_up(self, force_direction_value: Optional[int] = None) -> bool:
    """Navigate UP in browser tree using CC73 (DISCOVERED working config)"""
    channel, cc = self.MIDI_MAP['browser_tree_up']  # ✅ CORRECT KEY
    value = force_direction_value if force_direction_value is not None else 127
    return self._send_midi_command(channel, cc, value, f"Browser Tree UP (CC{cc}, value={value})")

def browser_tree_down(self, force_direction_value: Optional[int] = None) -> bool:
    """Navigate DOWN in browser tree using CC72 (DISCOVERED working config)"""
    channel, cc = self.MIDI_MAP['browser_tree_down']  # ✅ CORRECT KEY
    value = force_direction_value if force_direction_value is not None else 127
    return self._send_midi_command(channel, cc, value, f"Browser Tree DOWN (CC{cc}, value={value})")
```

### Changes Made
1. Updated key references:
   - `browser_tree_up()`: Now uses `self.MIDI_MAP['browser_tree_up']` (CC73)
   - `browser_tree_down()`: Now uses `self.MIDI_MAP['browser_tree_down']` (CC72)
2. Changed default value to 127 for both (button press standard)
3. Updated docstrings to reference discovered configuration
4. Improved log messages to show CC number

### Verification
**Test**: `test_02_agent_coordination_navigation.py`

**Before Fix**:
```
⬇️ Navigating DOWN 12 step(s)...
  Step 1/12: ❌ Error: 'browser_tree_up_down'
❌ Navigation failed
```

**After Fix**:
```
⬇️ Navigating DOWN 12 step(s)...
  Step 1/12: ✅
  Step 2/12: ✅
  ...
  Step 12/12: ✅
✅ Navigation successful
```

### Impact
- ✅ Browser tree navigation now functional
- ✅ 12-step navigation test passed
- ✅ Aligns with BROWSER_NAVIGATION_DISCOVERY.md
- ✅ Uses correct CC72/CC73 commands

### Related Files
- `/Users/Fiore/dj/core/traktor_control.py` (fixed)
- `/Users/Fiore/dj/docs/BROWSER_NAVIGATION_DISCOVERY.md` (reference)
- `/Users/Fiore/dj/tests/test_02_agent_coordination_navigation.py` (verification)

### Prevention
- Keep MIDI_MAP keys synchronized with method implementations
- Run navigation tests when updating MIDI mappings
- Document discovered commands in both code and markdown files

---

## 🐛 Bug #002: Screenshot Size Exceeds API Limit

**Date Found**: 2025-10-07
**Severity**: 🟡 MEDIUM
**Status**: ✅ FIXED

### Description
Screenshots captured from Retina display (2880x1800) exceeded Claude API's 5MB image limit, causing API errors when music-vision-navigator attempted analysis.

### Location
- **Component**: music-vision-navigator agent
- **Issue**: Raw screenshots too large for API consumption

### Symptoms
```
API Error: 400
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "image exceeds 5 MB maximum: 10347836 bytes > 5242880 bytes"
  }
}
```

### Root Cause
1. macOS `screencapture` produces high-resolution images
2. Retina display (2880x1800) creates ~4-10MB files
3. No compression applied before sending to API
4. API has hard 5MB limit for images

### Fix Strategy
Implemented aggressive automatic compression pipeline:

1. **Target Size**: 200KB (25x smaller than API limit for safety margin)
2. **Compression Algorithm**:
   ```python
   - Start: 1280px width max, JPEG quality=40
   - Iterate:
     * Resize if width > target
     * Save with JPEG compression
     * Check file size
     * If > 200KB:
       - Reduce quality (down to 25)
       - OR reduce resolution (down to 640px)
     * Repeat until size OK
   - Validate: Reject if still > 200KB
   ```

### Implementation

**Created**: `capture_display_compressed()` function in `test_01_music_vision_capture.py`

**Key Features**:
- Iterative compression with size validation
- Maintains aspect ratio during resize
- Uses PIL LANCZOS resampling for quality
- Automatic cleanup of raw files
- Returns None if compression fails

**Results**:
```
Display 1 (Retina 2880x1800):
  Original: 4237.0 KB
  Compressed: 42.6 KB (1280x800)
  Reduction: 99.0%

Display 2 (HP 1920x1080):
  Original: 1958.8 KB
  Compressed: 38.2 KB (1280x720)
  Reduction: 98.0%
```

### Agent Integration
Updated `music-vision-navigator.md` with:
- Added screenshot capture capability
- Added CRITICAL 200KB size limit rule
- Embedded compression function in agent instructions
- Added validation: "NEVER analyze screenshots > 200KB"

### Verification
**Test**: `test_01_music_vision_capture.py`
- ✅ Both displays compressed successfully
- ✅ All screenshots under 200KB
- ✅ Image quality sufficient for UI analysis
- ✅ No API errors during submission

### Impact
- ✅ Enables screenshot-based visual analysis
- ✅ Works on both Retina and standard displays
- ✅ Prevents API errors
- ✅ Reusable compression function

### Related Files
- `/Users/Fiore/dj/tests/test_01_music_vision_capture.py` (implementation)
- `/Users/Fiore/dj/.claude/agents/music-vision-navigator.md` (updated agent)
- `/Users/Fiore/dj/tests/test_results/screenshots/` (compressed screenshots)

---

---

## 🐛 Bug #003: Agent Screenshot Capture Not Detecting Traktor Window

**Date Found**: 2025-10-07
**Severity**: 🟡 MEDIUM
**Status**: 🔄 WORKAROUND (User-provided screenshots)

### Description
music-vision-navigator agent's automatic screenshot capture via `screencapture -D 2` consistently captures desktop wallpaper instead of Traktor window, even when Traktor is running fullscreen on Display 2.

### Location
- **Component**: music-vision-navigator agent screenshot capture
- **Tool**: macOS `screencapture -D 2`
- **Display**: Secondary display (HP monitor)

### Symptoms
```
Agent captures Display 2 → Gets desktop wallpaper (sunset/boats)
User captures Display 2 → Gets Traktor interface correctly
```

**Evidence**:
- Agent screenshot: Desktop wallpaper only
- User screenshot (same time/display): Traktor interface visible
- Traktor confirmed running and fullscreen on Display 2

### Root Cause Analysis
**Possible Causes**:
1. **Window Layer Issue**: Traktor may be on a different window layer invisible to `screencapture -D`
2. **Display Capture Timing**: Window composition delay between capture and actual display
3. **macOS Permissions**: Screen recording permissions not properly configured
4. **Fullscreen Mode**: Traktor's fullscreen implementation may be non-standard
5. **Display Selection**: `screencapture -D 2` may not reliably target correct physical display

### Investigation Steps
1. Verified Traktor running and visible on Display 2
2. Agent captured screenshot → wallpaper only
3. User captured screenshot immediately after → Traktor visible
4. Confirmed both using Display 2
5. Checked screenshot file sizes and content

### Current Workaround ✅

**Solution**: Use user-provided screenshots for verification
- User captures with Cmd+Shift+4 or screenshot tool
- Provides path to agent for analysis
- Agent reads and analyzes user screenshot
- **Works perfectly** - confirmed Test 03 navigation success

### Impact
- ⚠️ Agent cannot auto-verify visual state
- ✅ Agent can analyze user-provided screenshots
- ✅ Does not block agent coordination functionality
- ✅ MIDI commands execute correctly regardless

### Related Files
- `/Users/Fiore/dj/.claude/agents/music-vision-navigator.md` (agent definition)
- `/Users/Fiore/dj/tests/test_results/screenshots/display_2.jpg` (agent capture - wallpaper)
- `/Users/Fiore/Desktop/Screenshot 2025-10-07 alle 21.10.09.png` (user capture - Traktor)

### Future Investigation Required
- [ ] Test different `screencapture` parameters
- [ ] Try alternative capture methods (PyObjC, AppKit)
- [ ] Check if Traktor has capture protection
- [ ] Test with different fullscreen modes
- [ ] Investigate macOS display management APIs
- [ ] Check if window ID capture works better than display number

### Prevention
- Use user-provided screenshots for critical verifications
- Document screenshot paths in agent prompts
- Agent confirms screenshot content before analysis
- Add screenshot validation step before analysis

---

## 📊 Bug Statistics

| Metric | Count |
|--------|-------|
| Total Bugs Found | 3 |
| Critical Bugs | 1 |
| Medium Bugs | 2 |
| Bugs Fixed | 2 |
| Workarounds | 1 |
| Fix Success Rate | 100% |

---

## 🎯 Common Patterns

### Pattern #1: Documentation-Code Drift
**Seen in**: Bug #001

When documentation (BROWSER_NAVIGATION_DISCOVERY.md) describes working configuration, but code hasn't been updated to match.

**Prevention**:
- Update code immediately after discovery
- Run integration tests after mapping changes
- Keep MIDI_MAP and methods synchronized

### Pattern #2: External API Constraints
**Seen in**: Bug #002

Features that depend on external APIs (Claude) must respect API limits and constraints.

**Prevention**:
- Check API documentation for limits
- Implement validation before API calls
- Add compression/optimization pipelines
- Use safe margins (200KB vs 5MB limit)

---

## 🔄 Future Monitoring

### Areas to Watch
1. **MIDI Mapping Consistency**: Verify after any Traktor mapping updates
2. **Screenshot Sizes**: Monitor if different displays or resolutions cause issues
3. **Agent Coordination**: Watch for timing issues in multi-step operations
4. **Memory Leaks**: Long-running agent sessions

### Test Coverage
- ✅ Browser navigation (test_02)
- ✅ Screenshot capture (test_01)
- ⚠️ Visual verification (pending)
- ⚠️ Track loading (pending)
- ⚠️ Deck control (pending)

---

**Last Updated**: 2025-10-07 21:00
**Maintained By**: Agent Coordination Test System
