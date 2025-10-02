#!/usr/bin/env python3
"""
Test CC Discovery - Find which CC numbers actually work in Traktor
"""

import time
import sys
import os
import re
from traktor_control import TraktorController, MIDIChannel
from config import DJConfig

class CCDiscovery:
    def __init__(self):
        self.config = DJConfig()
        self.traktor = TraktorController(self.config)
        self.discovered_file = "cc_mapping_found.txt"
        self.discovered_ccs = self._load_discovered()

        # Connect to Traktor
        print("\n🔌 Connecting to Traktor via IAC Driver...")
        if not self.traktor.connect_with_gil_safety(output_only=True):
            print("❌ Failed to connect to Traktor MIDI")
            sys.exit(1)
        print("✅ Connected!\n")

        # Show already discovered
        if self.discovered_ccs:
            print(f"📚 Trovati {len(self.discovered_ccs)} CC già scoperti:")
            for cc in sorted(self.discovered_ccs.keys())[:10]:
                print(f"   CC {cc}: {self.discovered_ccs[cc][:50]}...")
            if len(self.discovered_ccs) > 10:
                print(f"   ... e altri {len(self.discovered_ccs) - 10}")
            print()

    def _load_discovered(self) -> dict:
        """Load previously discovered CC mappings"""
        discovered = {}
        if os.path.exists(self.discovered_file):
            with open(self.discovered_file, 'r') as f:
                for line in f:
                    # Match: "CC 20 (Ch 1): Description"
                    match = re.match(r'CC (\d+).*?: (.+)', line)
                    if match:
                        cc_num = int(match.group(1))
                        description = match.group(2).strip()
                        discovered[cc_num] = description
        return discovered

    def test_cc_range(self, start: int, end: int, channel: int = 1):
        """Test a range of CC numbers"""
        print(f"\n{'='*60}")
        print(f"🔍 TESTING CC {start}-{end} on Channel {channel}")
        print(f"{'='*60}\n")
        print("📋 Per ogni CC, osserva Traktor e dimmi cosa succede")
        print("💡 CC già scoperti verranno saltati automaticamente\n")

        results = {}
        skipped_count = 0

        for cc in range(start, end + 1):
            # Skip if already discovered
            if cc in self.discovered_ccs:
                skipped_count += 1
                print(f"⏭️  CC {cc} già scoperto: {self.discovered_ccs[cc][:40]}...")
                continue

            print(f"\n{'─'*60}")
            print(f"🎛️  Testing CC {cc} on Channel {channel}")
            print(f"{'─'*60}")

            # Send sequence and store for repeat
            def send_sequence():
                # Send CC message with value 127
                self.traktor.midi_out.send_message([
                    0xB0 + (channel - 1),  # Control Change on channel
                    cc,
                    127
                ])
                print(f"📡 Sent: CC {cc} = 127")
                time.sleep(0.5)

                # Send CC message with value 0
                self.traktor.midi_out.send_message([
                    0xB0 + (channel - 1),
                    cc,
                    0
                ])
                print(f"📡 Sent: CC {cc} = 0")
                time.sleep(0.5)

                # Send CC message with value 64 (middle)
                self.traktor.midi_out.send_message([
                    0xB0 + (channel - 1),
                    cc,
                    64
                ])
                print(f"📡 Sent: CC {cc} = 64 (middle)")
                time.sleep(1.0)

            # Send initial sequence
            send_sequence()

            # Ask user with repeat option
            while True:
                response = input(f"\n❓ Cosa ha fatto CC {cc}? (describe/r/skip/quit): ").strip()

                if response == 'quit':
                    self._save_results(results)
                    if skipped_count > 0:
                        print(f"\n⏭️  Saltati {skipped_count} CC già scoperti")
                    return

                elif response == 'r':
                    print("\n🔁 RIPETO SEQUENZA MIDI...")
                    send_sequence()
                    # Loop continues to ask again

                elif response == 'skip':
                    results[cc] = "Not mapped / No effect"
                    break

                elif response:
                    results[cc] = response
                    print(f"✅ Saved: CC {cc} = '{response}'")
                    # Save immediately to file
                    with open(self.discovered_file, "a") as f:
                        f.write(f"CC {cc} (Ch {channel}): {response}\n")
                    # Update in-memory cache
                    self.discovered_ccs[cc] = response
                    break

                else:
                    print("❌ Per favore descrivi l'effetto oppure:")
                    print("   r = ripeti sequenza 🔁")
                    print("   skip = salta ⏭️")
                    print("   quit = termina")

        self._save_results(results)
        if skipped_count > 0:
            print(f"\n⏭️  Saltati {skipped_count} CC già scoperti")

    def test_specific_cc(self, cc: int, channel: int = 1):
        """Test a specific CC number with different values"""
        print(f"\n{'='*60}")
        print(f"🔍 TESTING CC {cc} on Channel {channel}")
        print(f"{'='*60}\n")

        # Check if already discovered
        if cc in self.discovered_ccs:
            print(f"📚 CC {cc} già scoperto: {self.discovered_ccs[cc]}")
            choice = input("Vuoi testarlo comunque? (s/n): ").strip().lower()
            if choice != 's':
                return

        test_values = [0, 32, 64, 96, 127]

        def run_test():
            for value in test_values:
                print(f"\n📡 Sending CC {cc} = {value}")
                self.traktor.midi_out.send_message([
                    0xB0 + (channel - 1),
                    cc,
                    value
                ])
                time.sleep(1.5)
                input("Press ENTER for next value...")

        # Run initial test
        run_test()

        # Ask for description with repeat option
        while True:
            response = input(f"\n✏️  Describe what CC {cc} does (or 'r' to repeat): ").strip()

            if response == 'r':
                print("\n🔁 RIPETO TEST...")
                run_test()
                # Loop continues to ask again
            elif response:
                # Save to file
                with open(self.discovered_file, "a") as f:
                    f.write(f"CC {cc} (Ch {channel}): {response}\n")
                # Update in-memory cache
                self.discovered_ccs[cc] = response
                print(f"✅ Saved to {self.discovered_file}")
                break
            else:
                skip = input("Skip questo CC? (s/n): ").strip().lower()
                if skip == 's':
                    break

    def show_discovered(self):
        """Show all discovered CC mappings"""
        if not self.discovered_ccs:
            print("\n📭 Nessun CC scoperto ancora")
            print(f"   Il file {self.discovered_file} non esiste o è vuoto\n")
            return

        print(f"\n{'='*60}")
        print(f"📚 CC SCOPERTI ({len(self.discovered_ccs)} totali)")
        print(f"{'='*60}\n")

        for cc in sorted(self.discovered_ccs.keys()):
            print(f"CC {cc:3d}: {self.discovered_ccs[cc]}")

        print(f"\n{'='*60}")
        print(f"File: {self.discovered_file}\n")

    def _save_results(self, results: dict):
        """Save discovered mappings"""
        if not results:
            return

        filename = f"cc_discovery_{int(time.time())}.txt"
        with open(filename, "w") as f:
            f.write("CC DISCOVERY RESULTS\n")
            f.write("=" * 60 + "\n\n")
            for cc, description in sorted(results.items()):
                f.write(f"CC {cc}: {description}\n")

        print(f"\n✅ Results saved to: {filename}")

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║           CC DISCOVERY TOOL - Find Real Mappings           ║
╚════════════════════════════════════════════════════════════╝

Questo tool ti aiuta a scoprire quali CC numbers funzionano
davvero in Traktor.

PRIMA DI INIZIARE:
1. Apri Traktor Pro 3
2. Carica una traccia nel Deck A
3. Assicurati che IAC Driver Bus 1 sia attivo
4. Tieni Traktor visibile per vedere gli effetti

FUNZIONALITÀ:
✅ Ripeti ultimo comando con 'r' se non sei sicuro
✅ CC già scoperti vengono saltati automaticamente
✅ Salvataggio immediato in cc_mapping_found.txt

Opzioni:
  1) Test range completo (es. CC 1-127)
  2) Test range specifico (es. CC 20-40)
  3) Test singolo CC (dettagliato)
  4) Mostra CC scoperti

""")

    discoverer = CCDiscovery()

    while True:
        choice = input("Scegli opzione (1/2/3/4/quit): ").strip()

        if choice == '1':
            discoverer.test_cc_range(1, 127)
        elif choice == '2':
            start = int(input("Start CC: "))
            end = int(input("End CC: "))
            discoverer.test_cc_range(start, end)
        elif choice == '3':
            cc = int(input("CC number: "))
            discoverer.test_specific_cc(cc)
        elif choice == '4':
            discoverer.show_discovered()
        elif choice == 'quit':
            print("👋 Bye!")
            break
        else:
            print("❌ Opzione non valida")

if __name__ == "__main__":
    main()
