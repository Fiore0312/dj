#!/usr/bin/env python3
"""
🎧 DJ AI System - Launcher REFACTORED
Avvia sistema DJ AI con interfaccia refactored e verifica comandi real-time
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main launcher per sistema refactored"""
    print("="*80)
    print("🎧 DJ AI SYSTEM - REFACTORED VERSION v2.0")
    print("="*80)
    print("✨ New Features:")
    print("  ✅ Real-time command verification with Traktor")
    print("  ✅ Visual feedback for every action")
    print("  ✅ Automatic retry on command failure")
    print("  ✅ Command history and success rate tracking")
    print("  ✅ Free AI model (z-ai/glm-4.5-air:free)")
    print("="*80)

    try:
        # Import GUI refactored
        from gui.dj_interface_refactored import DJInterfaceRefactored

        # Create and run interface
        print("\n🚀 Launching refactored GUI...")
        interface = DJInterfaceRefactored()
        interface.run()

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("Assicurati che tutti i moduli siano installati:")
        print("  pip install -r requirements_simple.txt")
        return 1

    except KeyboardInterrupt:
        print("\n\n⚠️ Sistema interrotto dall'utente")
        return 0

    except Exception as e:
        print(f"\n❌ Errore fatale: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())