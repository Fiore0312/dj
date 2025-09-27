#!/usr/bin/env python3
"""
🎛️ Autonomous DJ - MIDI Ports Keeper
Mantiene attive le porte MIDI virtuali per configurazione Traktor
"""

from midi.professional_midi_manager import get_midi_manager
import time
import signal
import sys

def main():
    print("🎧 Autonomous DJ - MIDI Ports Activation")
    print("=" * 50)

    # Initialize MIDI Manager
    midi = get_midi_manager()
    midi.start()

    print()
    print("🎛️ MIDI Ports are now ACTIVE and ready for Traktor!")
    print()
    print("📋 TRAKTOR CONFIGURATION STEPS:")
    print("   1. Open Traktor Pro")
    print("   2. Go to Preferences (Ctrl/Cmd + ,)")
    print("   3. Select 'Controller Manager'")
    print("   4. Click 'Add...' → 'Generic MIDI'")
    print("   5. Set Input Port: 'TraktorPy_Virtual'")
    print("   6. Set Output Port: 'TraktorPy_Virtual_In'")
    print()
    print("🔍 Available MIDI Ports:")
    print("   📥 Input for Traktor:  TraktorPy_Virtual")
    print("   📤 Output for Traktor: TraktorPy_Virtual_In")
    print()
    print("🔄 Ports will stay active until you press Ctrl+C")
    print("⚠️  Keep this terminal open during Traktor setup!")
    print()

    def signal_handler(sig, frame):
        print('\n🛑 Shutting down MIDI ports...')
        midi.stop()
        print('✅ MIDI ports closed safely')
        print('👋 Thanks for using Autonomous DJ!')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        while True:
            # Keep the ports alive
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()