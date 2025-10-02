#!/bin/bash
# Quick launcher for Simple DJ Controller (Rule-based, NO AI)

echo "🎛️ Starting Simple DJ Controller (Rule-Based System)"
echo "=================================================="
echo ""
echo "✨ Features:"
echo "  - NO AI required (pure rule-based)"
echo "  - Direct MIDI control"
echo "  - Fast and predictable"
echo "  - Works 100% offline"
echo ""
echo "=================================================="
echo ""

cd "$(dirname "$0")"
source dj_env/bin/activate
python simple_dj_controller.py
