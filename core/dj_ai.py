#!/usr/bin/env python3
"""
🎧 DJ AI System - Launcher Principale
Sistema DJ AI completo - Lancio con un singolo comando
"""

import sys
import os
import asyncio
import logging
import time
from pathlib import Path

# Aggiungi project root al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Configura logging sistema"""
    log_level = os.getenv('DJ_LOG_LEVEL', 'INFO')

    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_banner():
    """Banner di avvio"""
    banner = """
🎧 ═══════════════════════════════════════════════════════════════════════════════ 🎧
                              DJ AI SYSTEM v2.0
                          Powered by OpenRouter & Claude AI
🎧 ═══════════════════════════════════════════════════════════════════════════════ 🎧

    🤖 AI-Powered DJ Mixing     🎛️ Traktor Pro Integration     💬 Real-time Chat
    🎵 Smart Music Selection    🔄 Automatic Transitions       🚨 Human Override

                           Ultra-semplificato • Professionale

🎧 ═══════════════════════════════════════════════════════════════════════════════ 🎧
"""
    print(banner)

def check_dependencies():
    """Controlla dipendenze critiche"""
    print("🔍 Controllo dipendenze...")

    missing_deps = []

    # Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ richiesto")
        return False

    # Dipendenze critiche
    critical_deps = [
        ('tkinter', 'GUI interface'),
        ('asyncio', 'Async operations'),
        ('threading', 'Multi-threading'),
        ('pathlib', 'Path operations'),
        ('json', 'JSON handling'),
        ('time', 'Timing operations'),
        ('logging', 'Logging system')
    ]

    for dep, description in critical_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}: OK")
        except ImportError:
            print(f"❌ {dep}: MANCANTE ({description})")
            missing_deps.append(dep)

    # Dipendenze opzionali con installazione automatica
    optional_deps = [
        ('rtmidi', 'python-rtmidi', 'MIDI communication'),
        ('mutagen', 'mutagen', 'Music metadata'),
        ('aiohttp', 'aiohttp', 'HTTP async client'),
    ]

    for module, package, description in optional_deps:
        try:
            __import__(module)
            print(f"✅ {module}: OK")
        except ImportError:
            print(f"⚠️  {module}: MANCANTE ({description})")
            print(f"   Installa con: pip install {package}")
            missing_deps.append(module)

    if missing_deps:
        print(f"\n❌ Dipendenze mancanti: {', '.join(missing_deps)}")
        print("🔧 Esegui: pip install -r requirements.txt")
        return False

    print("✅ Tutte le dipendenze sono disponibili")
    return True

def check_system_config():
    """Controlla configurazione sistema"""
    print("\n🔧 Controllo configurazione sistema...")

    # Import moduli del sistema
    try:
        from config import get_config, check_system_requirements
        config = get_config()
        requirements = check_system_requirements()

        print(f"✅ Configurazione caricata")
        print(f"🎵 Libreria musica: {config.music_library_path}")
        print(f"🤖 Modello AI: {config.openrouter_model}")

        # Status dettagliato
        for key, value in requirements.items():
            if key != "errors":
                icon = "✅" if value else "❌"
                print(f"{icon} {key}: {value}")

        if requirements["errors"]:
            print("\n⚠️  Attenzione:")
            for error in requirements["errors"]:
                print(f"   • {error}")

        # Verifica critici
        critical_ok = requirements.get("python_version", False) and \
                     requirements.get("music_library", False)

        if not critical_ok:
            print("\n❌ Configurazione sistema incompleta")
            return False

        print("✅ Configurazione sistema OK")
        return True

    except Exception as e:
        print(f"❌ Errore controllo configurazione: {e}")
        return False

def setup_environment():
    """Setup environment automatico"""
    print("\n⚙️  Setup ambiente...")

    try:
        # Verifica directory
        dirs_to_check = ['config', 'gui', 'traktor', 'core', 'midi']
        for dir_name in dirs_to_check:
            dir_path = project_root / dir_name
            if dir_path.exists():
                print(f"✅ Directory {dir_name}: OK")
            else:
                print(f"❌ Directory {dir_name}: MANCANTE")
                return False

        # Crea directory per dati se non esistono
        data_dirs = ['.dj_cache', '.dj_logs']
        for data_dir in data_dirs:
            data_path = project_root / data_dir
            data_path.mkdir(exist_ok=True)

        print("✅ Ambiente configurato correttamente")
        return True

    except Exception as e:
        print(f"❌ Errore setup ambiente: {e}")
        return False

def launch_gui():
    """Lancia interfaccia GUI"""
    print("\n🖥️  Avvio interfaccia grafica...")

    try:
        from gui.dj_interface import DJInterface

        print("✅ Moduli GUI caricati")
        print("🚀 Avvio DJ AI Interface...")

        # Crea e avvia interfaccia
        app = DJInterface()
        print("📱 Interfaccia creata, apertura finestra...")

        app.run()

    except ImportError as e:
        print(f"❌ Errore import GUI: {e}")
        print("🔧 Debug traceback completo:")
        import traceback
        traceback.print_exc()
        print("🔧 Verifica che tutti i moduli GUI siano presenti")
        return False
    except Exception as e:
        print(f"❌ Errore avvio GUI: {e}")
        return False

def launch_cli():
    """Lancia interfaccia CLI (alternativa)"""
    print("\n💻 Avvio interfaccia CLI...")

    try:
        from config import get_config
        from core.openrouter_client import get_openrouter_client
        from traktor_control import get_traktor_controller

        print("🔧 Modalità CLI non ancora implementata")
        print("📱 Usa la GUI con: python dj_ai.py")

        return False

    except Exception as e:
        print(f"❌ Errore CLI: {e}")
        return False

def show_help():
    """Mostra help"""
    help_text = """
🎧 DJ AI System - Help

UTILIZZO:
  python dj_ai.py                    # Avvia interfaccia GUI (default)
  python dj_ai.py --cli              # Avvia interfaccia CLI
  python dj_ai.py --check            # Solo controllo sistema
  python dj_ai.py --help             # Mostra questo help

SETUP PREREQUISITI:
  1. Installa dipendenze: pip install -r requirements.txt
  2. Configura IAC Driver (macOS): Apri Audio MIDI Setup > IAC Driver
  3. Ottieni API key: https://openrouter.ai/
  4. Imposta API key: export OPENROUTER_API_KEY="your-key"
  5. Apri Traktor Pro e configura MIDI (vedi traktor/)

UTILIZZO VELOCE:
  1. python dj_ai.py
  2. Inserisci API key nella GUI
  3. Seleziona venue e tipo evento
  4. Clicca "AVVIA DJ AI"
  5. Interagisci con l'AI via chat

TROUBLESHOOTING:
  - Problemi MIDI: Verifica IAC Driver in Audio MIDI Setup
  - Problemi API: Controlla chiave OpenRouter
  - Problemi musica: Verifica path /Users/Fiore/Music
  - Problemi Traktor: Assicurati che sia aperto

Per supporto: https://github.com/Fiore0312/dj
"""
    print(help_text)

def main():
    """Main function"""

    # Parse argomenti semplici
    args = sys.argv[1:]

    if '--help' in args or '-h' in args:
        show_help()
        return 0

    # Setup base
    setup_logging()
    print_banner()

    # Controlli sistema
    if not check_dependencies():
        print("\n❌ Dipendenze mancanti. Installa requirements e riprova.")
        return 1

    if not check_system_config():
        print("\n❌ Configurazione sistema incompleta.")
        print("💡 Verifica che /Users/Fiore/Music esista e contenga musica")
        print("💡 Configura OPENROUTER_API_KEY")
        if '--check' not in args:
            print("💡 Usa --check per controllo dettagliato")
        return 1

    if not setup_environment():
        print("\n❌ Setup ambiente fallito.")
        return 1

    # Solo controllo
    if '--check' in args:
        print("\n✅ Controllo sistema completato con successo!")
        print("🚀 Sistema pronto per l'avvio")
        return 0

    # Avvio interfaccia
    if '--cli' in args:
        # CLI mode (futuro)
        if not launch_cli():
            print("\n❌ Avvio CLI fallito.")
            return 1
    else:
        # GUI mode (default)
        if not launch_gui():
            print("\n❌ Avvio GUI fallito.")
            print("💡 Prova modalità CLI con: python dj_ai.py --cli")
            return 1

    print("\n👋 DJ AI System chiuso")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Interruzione utente")
        print("👋 DJ AI System fermato")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Errore fatale: {e}")
        print("🔧 Riavvia il sistema o controlla i log")
        sys.exit(1)