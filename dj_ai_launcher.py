#!/usr/bin/env python3
"""
🚀 DJ AI System - Unified Launcher
Launcher intelligente con auto-detection GUI e fallback multipli
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def print_banner():
    """Banner sistema"""
    print("\n" + "="*80)
    print("🎧 DJ AI SYSTEM - UNIFIED LAUNCHER v2.1")
    print("="*80)
    print("✨ Features:")
    print("  ✅ Auto-detection GUI disponibile")
    print("  ✅ Fallback multipli per massima compatibilità")
    print("  ✅ Fix blinking track issue")
    print("  ✅ Real-time command verification")
    print("="*80 + "\n")

def check_gui_availability():
    """Check which GUIs are available"""
    available_guis = []

    # Check tkinter
    try:
        import tkinter
        available_guis.append('tkinter')
        logger.info("✅ Tkinter disponibile")
    except ImportError:
        logger.warning("⚠️  Tkinter non disponibile")

    # Check refactored GUI
    try:
        from gui.dj_interface_refactored import DJInterfaceRefactored
        available_guis.append('refactored')
        logger.info("✅ Refactored GUI disponibile")
    except ImportError as e:
        logger.warning(f"⚠️  Refactored GUI non disponibile: {e}")

    # Check original GUI
    try:
        from gui.dj_interface import DJInterface
        available_guis.append('original')
        logger.info("✅ Original GUI disponibile")
    except ImportError as e:
        logger.warning(f"⚠️  Original GUI non disponibile: {e}")

    return available_guis

def launch_refactored_gui():
    """Launch refactored GUI (v2.0)"""
    try:
        print("🚀 Launching Refactored GUI (v2.0)...")
        from gui.dj_interface_refactored import DJInterfaceRefactored

        interface = DJInterfaceRefactored()
        interface.run()
        return True

    except Exception as e:
        logger.error(f"❌ Refactored GUI failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def launch_original_gui():
    """Launch original GUI"""
    try:
        print("🚀 Launching Original GUI...")
        from gui.dj_interface import DJInterface

        interface = DJInterface()
        interface.run()
        return True

    except Exception as e:
        logger.error(f"❌ Original GUI failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def launch_cli_mode():
    """Launch command-line mode (no GUI)"""
    print("\n" + "="*80)
    print("📟 COMMAND-LINE MODE")
    print("="*80)
    print("GUI non disponibile. Avvio modalità command-line...")
    print()

    try:
        from traktor_control import TraktorController, DeckID
        from config import get_config

        config = get_config()
        traktor = TraktorController(config)

        print("🔌 Connecting to Traktor...")
        if not traktor.connect_with_gil_safety():
            print("❌ Failed to connect to Traktor MIDI")
            return False

        if traktor.simulation_mode:
            print("⚠️  Running in SIMULATION mode")
        else:
            print("✅ Connected to Traktor MIDI")

        print("\n" + "="*80)
        print("COMANDI DISPONIBILI:")
        print("="*80)
        print("  load_a    - Carica traccia su Deck A")
        print("  load_b    - Carica traccia su Deck B")
        print("  play_a    - Play Deck A")
        print("  play_b    - Play Deck B")
        print("  pause_a   - Pause Deck A")
        print("  pause_b   - Pause Deck B")
        print("  status    - Mostra stato decks")
        print("  quit      - Esci")
        print("="*80 + "\n")

        while True:
            try:
                command = input("DJ> ").strip().lower()

                if command == "quit" or command == "exit":
                    print("👋 Uscita...")
                    break

                elif command == "load_a":
                    print("🎵 Loading track to Deck A...")
                    traktor.load_next_track_smart(DeckID.A, "down")
                    print("✅ Track loaded")

                elif command == "load_b":
                    print("🎵 Loading track to Deck B...")
                    traktor.load_next_track_smart(DeckID.B, "down")
                    print("✅ Track loaded")

                elif command == "play_a":
                    print("▶️  Playing Deck A...")
                    traktor.force_play_deck(DeckID.A)
                    print("✅ Deck A playing")

                elif command == "play_b":
                    print("▶️  Playing Deck B...")
                    traktor.force_play_deck(DeckID.B)
                    print("✅ Deck B playing")

                elif command == "pause_a":
                    print("⏸️  Pausing Deck A...")
                    traktor.pause_deck(DeckID.A)
                    print("✅ Deck A paused")

                elif command == "pause_b":
                    print("⏸️  Pausing Deck B...")
                    traktor.pause_deck(DeckID.B)
                    print("✅ Deck B paused")

                elif command == "status":
                    print("\n📊 DECK STATUS:")
                    for deck_id in [DeckID.A, DeckID.B]:
                        state = traktor.deck_states[deck_id]
                        status = "▶️ PLAYING" if state['playing'] else "⏸️  PAUSED"
                        loaded = "✅ Loaded" if state['loaded'] else "❌ Empty"
                        print(f"  Deck {deck_id.value}: {status} | {loaded}")
                    print()

                elif command == "help" or command == "?":
                    print("Digita un comando dalla lista sopra")

                else:
                    print(f"❌ Comando sconosciuto: {command}")
                    print("Digita 'help' per lista comandi")

            except KeyboardInterrupt:
                print("\n👋 Uscita...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        traktor.disconnect()
        return True

    except Exception as e:
        logger.error(f"❌ CLI mode failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main launcher with intelligent fallback"""
    print_banner()

    # Check available GUIs
    print("🔍 Checking available interfaces...")
    available_guis = check_gui_availability()

    if not available_guis:
        print("❌ Nessuna interfaccia disponibile")
        print("Installa le dipendenze: pip install -r requirements_simple.txt")
        return 1

    print()

    # Try launching in order of preference
    if 'refactored' in available_guis:
        print("✨ Refactored GUI disponibile - usando versione ottimizzata")
        if launch_refactored_gui():
            return 0
        print("\n⚠️  Refactored GUI fallita, provo alternative...\n")

    if 'original' in available_guis:
        print("📱 Usando Original GUI")
        if launch_original_gui():
            return 0
        print("\n⚠️  Original GUI fallita, provo CLI mode...\n")

    if 'tkinter' in available_guis:
        print("📟 GUI non funzionanti, usando Command-Line mode")
        if launch_cli_mode():
            return 0

    print("\n❌ Tutte le interfacce hanno fallito")
    print("Verifica:")
    print("  1. Dipendenze installate: pip install -r requirements_simple.txt")
    print("  2. Python version: python3 --version (richiesto 3.8+)")
    print("  3. Traktor running con MIDI abilitato")

    return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
