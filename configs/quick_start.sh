#!/bin/bash
# Quick Start - Autonomous DJ Agent con OpenRouter

echo "🎛️ AUTONOMOUS DJ AGENT - Quick Start"
echo "===================================="
echo ""

# Attiva virtual environment
echo "📦 Attivando virtual environment..."
source dj_env/bin/activate

# Verifica API key
if grep -q "OPENROUTER_API_KEY" .env 2>/dev/null; then
    echo "✅ API Key OpenRouter configurata"
    export $(grep OPENROUTER_API_KEY .env | xargs)
else
    echo "⚠️ API Key non trovata in .env (userò fallback hardcoded)"
fi

echo ""
echo "🚀 Avvio Autonomous DJ Agent (Hybrid Mode)..."
echo ""
echo "Il sistema rileverà automaticamente quale backend usare:"
echo "  • Se hai ANTHROPIC_API_KEY → Claude SDK"
echo "  • Altrimenti → OpenRouter (FREE)"
echo ""

# Avvia agente
python autonomous_dj_hybrid.py
