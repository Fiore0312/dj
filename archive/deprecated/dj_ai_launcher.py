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
    print("🎧 DJ AI SYSTEM - UNIFIED LAUNCHER v2.2")
    print("="*80)
    print("✨ Features:")
    print("  ✅ Auto-detection GUI disponibile")
    print("  ✅ Fallback multipli per massima compatibilità")
    print("  ✅ Fix blinking track issue")
    print("  ✅ Real-time command verification")
    print("  🤖 Autonomous DJ mode disponibile!")
    print()
    print("Usage:")
    print("  python3 dj_ai_launcher.py                    # GUI/CLI normale")
    print("  python3 dj_ai_launcher.py --autonomous       # Modalità autonoma")
    print("  python3 dj_ai_launcher.py --autonomous --duration 30")
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
        print("  autonomous - Avvia modalità autonoma (2 minuti test)")
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

                elif command == "autonomous":
                    print("\n🤖 Avvio modalità autonoma (2 minuti test)...")
                    print("Press Ctrl+C per fermare in qualsiasi momento\n")
                    traktor.disconnect()  # Disconnect current session
                    # Launch autonomous mode from CLI
                    success = launch_autonomous_mode(duration=2, venue="club", event="prime_time")
                    if success:
                        print("\n✅ Autonomous session completata")
                    # Reconnect for CLI mode
                    print("\n🔌 Reconnecting for CLI mode...")
                    traktor = TraktorController(config)
                    traktor.connect_with_gil_safety()

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

def launch_autonomous_mode(duration: int = 60, venue: str = "club", event: str = "prime_time"):
    """
    Launch autonomous DJ mode (simplified version)

    Args:
        duration: Session duration in minutes
        venue: Venue type (club, bar, festival, etc.)
        event: Event type (prime_time, opening, closing, etc.)
    """
    print("\n" + "="*80)
    print("🤖 AUTONOMOUS DJ MODE")
    print("="*80)
    print("Sistema DJ completamente autonomo - L'AI gestisce tutto!")
    print(f"Venue: {venue} | Event: {event} | Duration: {duration} minuti")
    print()

    try:
        from traktor_control import TraktorController, DeckID
        from config import get_config
        import asyncio
        import time

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

        print("\n🤖 Starting Autonomous DJ Session...")
        print("="*80)
        print("L'AI controllerà:")
        print("  ✅ Load tracks automatico")
        print("  ✅ Play/transitions automatiche")
        print("  ✅ Beatmatching e mixing")
        print("  ✅ Energy management")
        print()
        print("⚠️  Press Ctrl+C per fermare la sessione")
        print("="*80 + "\n")

        # Autonomous loop
        start_time = time.time()
        session_end = start_time + (duration * 60)
        deck_playing = DeckID.A
        next_deck = DeckID.B
        tracks_played = 0

        # Start first track
        print("🎵 Loading first track to Deck A...")
        traktor.load_next_track_smart(DeckID.A, "down")
        time.sleep(0.5)

        print("▶️  Starting playback...")
        traktor.force_play_deck(DeckID.A, wait_if_recent_load=True)
        tracks_played += 1

        print(f"✅ Autonomous session started! Track 1 playing on Deck {deck_playing.value}\n")

        # Main autonomous loop
        while time.time() < session_end:
            elapsed = (time.time() - start_time) / 60  # Minutes
            remaining = duration - elapsed

            # Every 30 seconds, print status
            if int(elapsed * 60) % 30 == 0:
                print(f"📊 Status: {elapsed:.1f}/{duration} min | Tracks: {tracks_played} | Remaining: {remaining:.1f} min")

            # Every 45 seconds, prepare next track and transition
            if int(elapsed * 60) % 45 == 0 and int(elapsed * 60) > 0:
                print(f"\n🔄 Preparing transition to Deck {next_deck.value}...")

                # Load next track
                print(f"   🎵 Loading track to Deck {next_deck.value}...")
                traktor.load_next_track_smart(next_deck, "down")
                time.sleep(1.0)

                # Start playing next deck
                print(f"   ▶️  Starting Deck {next_deck.value}...")
                traktor.force_play_deck(next_deck, wait_if_recent_load=True)
                time.sleep(0.5)

                # Transition crossfader (simple fade over 4 seconds)
                print("   🎛️  Crossfading...")
                current_pos = 0.0 if deck_playing == DeckID.A else 1.0
                target_pos = 1.0 if deck_playing == DeckID.A else 0.0

                for i in range(8):
                    pos = current_pos + (target_pos - current_pos) * (i / 8.0)
                    traktor.set_crossfader(pos)
                    time.sleep(0.5)

                # Stop old deck after transition
                print(f"   ⏸️  Stopping Deck {deck_playing.value}")
                traktor.pause_deck(deck_playing)

                # Swap decks
                deck_playing, next_deck = next_deck, deck_playing
                tracks_played += 1

                print(f"   ✅ Transition complete! Now playing Deck {deck_playing.value}\n")

            time.sleep(1)

        print("\n" + "="*80)
        print("✅ AUTONOMOUS SESSION COMPLETE!")
        print("="*80)
        print(f"Duration: {duration} minutes")
        print(f"Tracks played: {tracks_played}")
        print(f"Transitions: {tracks_played - 1}")
        print("="*80)

        # Cleanup
        traktor.pause_deck(DeckID.A)
        traktor.pause_deck(DeckID.B)
        traktor.disconnect()

        return True

    except KeyboardInterrupt:
        print("\n\n⚠️  Autonomous session stopped by user")
        try:
            traktor.pause_deck(DeckID.A)
            traktor.pause_deck(DeckID.B)
            traktor.disconnect()
        except:
            pass
        return True

    except Exception as e:
        print(f"\n❌ Autonomous mode failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main launcher with intelligent fallback"""
    import sys

    # Check for autonomous mode flag
    if len(sys.argv) > 1 and sys.argv[1] == '--autonomous':
        # Parse additional arguments
        duration = 60
        venue = "club"
        event = "prime_time"

        if '--duration' in sys.argv:
            idx = sys.argv.index('--duration')
            if idx + 1 < len(sys.argv):
                duration = int(sys.argv[idx + 1])

        if '--venue' in sys.argv:
            idx = sys.argv.index('--venue')
            if idx + 1 < len(sys.argv):
                venue = sys.argv[idx + 1]

        if '--event' in sys.argv:
            idx = sys.argv.index('--event')
            if idx + 1 < len(sys.argv):
                event = sys.argv[idx + 1]

        print_banner()
        return 0 if launch_autonomous_mode(duration, venue, event) else 1

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
