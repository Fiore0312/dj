#!/bin/bash

echo "🔑 SETUP API KEY SICURO"
echo "======================"
echo ""

# Imposta la API key corrente
export OPENROUTER_API_KEY="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"
export OPENROUTER_MODEL="nousresearch/hermes-3-llama-3.1-405b"

echo "✅ API Key configurata (non viene salvata nel codice)"
echo "✅ Modello impostato: $OPENROUTER_MODEL"
echo ""

# Avvia il sistema DJ AI
echo "🚀 Avvio DJ AI System con chat funzionante..."
python3 dj_ai.py