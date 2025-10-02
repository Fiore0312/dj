#!/bin/bash
# Setup Anthropic API Key for Autonomous DJ Agent

echo "🔑 Anthropic API Key Setup"
echo "=========================================="
echo ""
echo "Per usare Claude Agent SDK serve una Anthropic API key."
echo "Puoi ottenerla gratuitamente (con crediti iniziali) da:"
echo "👉 https://console.anthropic.com/"
echo ""
echo "NOTA: Se non vuoi usare Anthropic, il sistema può usare"
echo "      OpenRouter con modelli gratuiti (fallback automatico)."
echo ""

read -p "Hai già una Anthropic API key? (y/n): " has_key

if [ "$has_key" = "y" ] || [ "$has_key" = "Y" ]; then
    echo ""
    read -p "Inserisci la tua Anthropic API key: " api_key

    if [ -z "$api_key" ]; then
        echo "❌ API key vuota. Uscita."
        exit 1
    fi

    # Salva in .env
    echo "ANTHROPIC_API_KEY=$api_key" > .env
    echo "✅ API key salvata in .env"
    echo ""
    echo "Per usarla, esegui:"
    echo "  export ANTHROPIC_API_KEY='$api_key'"
    echo ""
    echo "Oppure il sistema la leggerà automaticamente da .env"

else
    echo ""
    echo "📋 Opzioni disponibili:"
    echo ""
    echo "1. ANTHROPIC (Raccomandato per Claude Agent SDK)"
    echo "   - Vai su: https://console.anthropic.com/"
    echo "   - Crea account gratuito"
    echo "   - Ottieni API key (con \$5 crediti iniziali)"
    echo "   - Poi esegui nuovamente questo script"
    echo ""
    echo "2. OPENROUTER (Fallback con modelli gratuiti)"
    echo "   - Il sistema userà automaticamente OpenRouter"
    echo "   - Modelli gratuiti già configurati"
    echo "   - Nessuna API key richiesta"
    echo ""

    read -p "Vuoi continuare con OpenRouter (fallback)? (y/n): " use_openrouter

    if [ "$use_openrouter" = "y" ] || [ "$use_openrouter" = "Y" ]; then
        echo ""
        echo "✅ Sistema configurato per usare OpenRouter (fallback)"
        echo ""
        echo "NOTA: Per funzionalità complete (Claude Agent SDK),"
        echo "      ti servirà comunque una Anthropic API key."
        echo ""
        echo "Puoi sempre configurarla dopo con:"
        echo "  export ANTHROPIC_API_KEY='your-key'"
    else
        echo ""
        echo "❌ Setup annullato."
        echo "Configura una API key per continuare."
        exit 1
    fi
fi

echo ""
echo "🚀 Setup completato!"
echo ""
echo "Per avviare l'agente autonomo:"
echo "  source dj_env/bin/activate"
echo "  python autonomous_dj_sdk_agent.py"
echo ""
echo "O usa il launcher:"
echo "  python run_autonomous_dj.py"
