#!/bin/bash
#
# Quick test for Hybrid DJ Master - MANUAL mode
#

echo "🧪 Testing Hybrid DJ Master - MANUAL Mode"
echo "=========================================="
echo ""

# Activate virtual environment
source dj_env/bin/activate

# Create test input file
cat > /tmp/dj_test_commands.txt <<EOF
/status
search techno
/help
/quit
EOF

echo "📝 Test commands:"
cat /tmp/dj_test_commands.txt
echo ""
echo "🚀 Starting system with test input..."
echo ""

# Run with test input
timeout 30s python autonomous_dj_master.py < /tmp/dj_test_commands.txt 2>&1 | tail -50

echo ""
echo "✅ Test completed!"
