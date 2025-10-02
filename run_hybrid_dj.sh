#!/bin/bash
#
# 🎛️ Hybrid DJ Master - Launcher Script
# Starts the hybrid autonomous/manual DJ system
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "🎛️  HYBRID DJ MASTER - Launcher"
echo "=========================================="
echo ""

# Check virtual environment
if [ -d "dj_env" ]; then
    echo "✅ Virtual environment found"
    source dj_env/bin/activate
else
    echo "⚠️  Virtual environment not found"
    echo "Creating dj_env..."
    python3 -m venv dj_env
    source dj_env/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements_simple.txt
fi

# Check dependencies
echo ""
echo "Checking dependencies..."
python3 -c "import rtmidi" 2>/dev/null && echo "✅ python-rtmidi installed" || echo "⚠️  python-rtmidi missing"
python3 -c "import mutagen" 2>/dev/null && echo "✅ mutagen installed" || echo "⚠️  mutagen missing"
python3 -c "import aiohttp" 2>/dev/null && echo "✅ aiohttp installed" || echo "⚠️  aiohttp missing"

# Check Claude SDK
if python3 -c "import claude_agent_sdk" 2>/dev/null; then
    echo "✅ claude-agent-sdk installed"
    SDK_AVAILABLE=true
else
    echo "⚠️  claude-agent-sdk not installed (AI modes disabled)"
    SDK_AVAILABLE=false
fi

# Check API keys
echo ""
echo "Checking API keys..."

# Load .env file properly (skip comments and empty lines)
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ ANTHROPIC_API_KEY found (AI modes enabled)"
    AI_ENABLED=true
else
    echo "⚠️  ANTHROPIC_API_KEY not found"
    echo "   AI modes will be DISABLED"
    echo "   To enable: export ANTHROPIC_API_KEY=your-key"
    echo "   Or add to .env: ANTHROPIC_API_KEY=sk-ant-..."
    AI_ENABLED=false
fi

# Check OpenRouter key (optional, not used by hybrid system)
if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "ℹ️  OPENROUTER_API_KEY found (not used by hybrid system)"
fi

# Check macOS IAC Driver
echo ""
echo "Checking MIDI setup..."
if system_profiler SPAudioDataType 2>/dev/null | grep -q "IAC Driver"; then
    echo "✅ macOS IAC Driver available"
else
    echo "⚠️  Cannot detect IAC Driver status"
    echo "   Make sure IAC Driver is enabled in Audio MIDI Setup"
fi

# Check music library
echo ""
echo "Checking music library..."
if [ -d "$HOME/Music" ]; then
    TRACK_COUNT=$(find "$HOME/Music" -type f \( -name "*.mp3" -o -name "*.flac" -o -name "*.wav" -o -name "*.m4a" \) 2>/dev/null | wc -l | tr -d ' ')
    echo "✅ Music library: $TRACK_COUNT tracks found"
else
    echo "⚠️  Music library not found at $HOME/Music"
fi

# Mode selection
echo ""
echo "=========================================="
echo "🎛️  System Ready!"
echo "=========================================="
echo ""

if [ "$AI_ENABLED" = true ] && [ "$SDK_AVAILABLE" = true ]; then
    echo "Available modes:"
    echo "  1. MANUAL     - Full manual control (default)"
    echo "  2. AUTONOMOUS - AI decides everything"
    echo "  3. ASSISTED   - AI suggests, you approve"
    echo ""
    echo "Start with MANUAL mode (switch anytime with /auto or /assist)"
else
    echo "⚠️  Only MANUAL mode available (AI disabled)"
    echo ""
    echo "To enable AI modes:"
    echo "  1. Install Claude SDK: pip install claude-agent-sdk"
    echo "  2. Set API key: export ANTHROPIC_API_KEY=your-key"
fi

echo ""
echo "Starting Hybrid DJ Master..."
echo ""

# Launch the system
python3 autonomous_dj_master.py

echo ""
echo "=========================================="
echo "👋 Hybrid DJ Master stopped"
echo "=========================================="
