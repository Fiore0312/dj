#!/bin/bash

echo "🔧 FIX CHAT AI - Configurazione modello funzionante"
echo "=================================================="

# Imposta il modello AI funzionante
export OPENROUTER_MODEL="nousresearch/hermes-3-llama-3.1-405b"

echo "✅ Modello configurato: $OPENROUTER_MODEL"
echo ""
echo "🚀 Ora avvia il sistema DJ AI:"
echo "   python3 dj_ai.py"
echo ""
echo "💡 La chat dovrebbe funzionare perfettamente!"

# Avvia il sistema con il modello corretto
python3 dj_ai.py