#!/usr/bin/env python3
"""
🎯 MIDI Learn Mode Discovery Tool
Scopre i CC corretti per comandi Traktor tramite learn mode
"""

import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    import rtmidi
except ImportError as e:
    print(f"❌ Errore import rtmidi: {e}")
    sys.exit(1)

class MIDILearnDiscovery:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None
        self.discovered_commands = {}

    def find_iac_bus(self):
        """Trova IAC Bus 1"""
        print("📤 Porte MIDI disponibili:")
        for i, port in enumerate(self.out_ports):
            print(f"  [{i}] {port}")

        for i, port in enumerate(self.out_ports):
            if "IAC" in port and ("Bus 1" in port or "1" in port):
                self.iac_port = i
                break

        if self.iac_port is None:
            print("❌ IAC Bus 1 non trovato!")
            return False

        print(f"\n🎛️ Connessione a: {self.out_ports[self.iac_port]}")
        self.midiout.open_port(self.iac_port)
        return True

    def show_learn_mode_instructions(self, target_control):
        """Mostra istruzioni per attivare learn mode"""
        print("\n" + "="*60)
        print(f"🎯 DISCOVERY TARGET: {target_control}")
        print("="*60)
        print("\n🚨 PREPARAZIONE LEARN MODE:")
        print("  1. ✅ Apri Traktor Pro 3")
        print("  2. ✅ Vai in Preferences > Controller Manager")
        print("  3. ✅ Seleziona 'AI_DJ_Complete' nella lista")
        print(f"  4. 🎯 Trova il controllo: '{target_control}'")
        print("  5. 🎯 Click sul campo Assignment del controllo")
        print("  6. 🎯 Click 'Learn' (bottone con simbolo MIDI)")
        print("  7. ⏳ Aspetta che appaia 'Learning...' nel campo")
        print("\n⚠️  IMPORTANTE: Il controllo deve essere in modalità 'Learning...'")
        print("    Prima di continuare, conferma che vedi 'Learning...'")

    def discover_cc_range(self, start_cc, end_cc, velocity=64):
        """Scopre CC in un range specifico"""
        print(f"\n📡 DISCOVERY RANGE: CC {start_cc}-{end_cc}")
        print(f"   Velocity: {velocity}")
        print(f"   Canal: 1 (0xB0)")
        print("\n🔍 Invio CC discovery...")

        for cc in range(start_cc, end_cc + 1):
            # Control Change su canale 1 (0xB0)
            msg = [0xB0, cc, velocity]
            print(f"   📤 CC {cc:3d} (0x{cc:02X}) = {velocity}")
            self.midiout.send_message(msg)
            time.sleep(0.5)  # Pausa breve tra messaggi

        print(f"\n✅ Discovery range CC {start_cc}-{end_cc} completato!")

    def test_discovered_cc(self, cc_number, description):
        """Testa un CC scoperto"""
        print(f"\n🧪 TEST CC SCOPERTO: {cc_number}")
        print(f"   Descrizione: {description}")

        # Test con valori diversi
        test_values = [0, 32, 64, 96, 127]

        for value in test_values:
            msg = [0xB0, cc_number, value]
            print(f"   📤 CC {cc_number} = {value}")
            self.midiout.send_message(msg)
            time.sleep(1)

    def discover_deck_b_volume(self):
        """Discovery per Volume Deck B (priorità 1)"""
        self.show_learn_mode_instructions("Volume Deck B")

        input("\n▶️  Premi INVIO quando il learn mode è ATTIVO per 'Volume Deck B'...")

        # Discovery range suggerito: CC 60-90
        ranges = [(60, 69), (70, 79), (80, 89)]

        for start, end in ranges:
            print(f"\n🔍 Testing range CC {start}-{end}...")
            self.discover_cc_range(start, end)

            response = input(f"\n❓ Traktor ha imparato qualche CC nel range {start}-{end}? (y/n): ").strip().lower()
            if response == 'y':
                cc_found = input("🎯 Quale CC ha imparato? (numero): ").strip()
                try:
                    cc_num = int(cc_found)
                    self.discovered_commands['deck_b_volume'] = cc_num
                    print(f"✅ SCOPERTO: deck_b_volume = CC {cc_num}")

                    # Test immediato
                    print("\n🧪 Testing CC scoperto...")
                    self.test_discovered_cc(cc_num, "Volume Deck B")

                    confirm = input("\n❓ Il volume di Deck B si muove correttamente? (y/n): ").strip().lower()
                    if confirm == 'y':
                        print("✅ CC CONFERMATO e FUNZIONANTE!")
                        return cc_num
                    else:
                        print("⚠️  CC non funziona, continuando discovery...")
                except ValueError:
                    print("⚠️  Numero CC non valido, continuando...")

        print("❌ Nessun CC trovato per deck_b_volume nel range 60-90")
        return None

    def discover_cue_buttons(self):
        """Discovery per Cue Buttons A e B"""

        # Deck A Cue
        self.show_learn_mode_instructions("Cue Deck A")
        input("\n▶️  Premi INVIO quando il learn mode è ATTIVO per 'Cue Deck A'...")

        # Range per buttons: CC 1-50
        ranges = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50)]

        for start, end in ranges:
            print(f"\n🔍 Testing range CC {start}-{end} per Cue Deck A...")
            # Per buttons usiamo velocity 127 (ON)
            self.discover_cc_range(start, end, velocity=127)

            response = input(f"\n❓ Traktor ha imparato qualche CC nel range {start}-{end}? (y/n): ").strip().lower()
            if response == 'y':
                cc_found = input("🎯 Quale CC ha imparato? (numero): ").strip()
                try:
                    cc_num = int(cc_found)
                    self.discovered_commands['deck_a_cue'] = cc_num
                    print(f"✅ SCOPERTO: deck_a_cue = CC {cc_num}")

                    # Test button
                    print("\n🧪 Testing Cue Button A...")
                    self.test_cue_button(cc_num, "Cue Deck A")
                    break
                except ValueError:
                    print("⚠️  Numero CC non valido, continuando...")

        # Deck B Cue (stesso processo)
        self.show_learn_mode_instructions("Cue Deck B")
        input("\n▶️  Premi INVIO quando il learn mode è ATTIVO per 'Cue Deck B'...")

        for start, end in ranges:
            print(f"\n🔍 Testing range CC {start}-{end} per Cue Deck B...")
            self.discover_cc_range(start, end, velocity=127)

            response = input(f"\n❓ Traktor ha imparato qualche CC nel range {start}-{end}? (y/n): ").strip().lower()
            if response == 'y':
                cc_found = input("🎯 Quale CC ha imparato? (numero): ").strip()
                try:
                    cc_num = int(cc_found)
                    self.discovered_commands['deck_b_cue'] = cc_num
                    print(f"✅ SCOPERTO: deck_b_cue = CC {cc_num}")

                    # Test button
                    print("\n🧪 Testing Cue Button B...")
                    self.test_cue_button(cc_num, "Cue Deck B")
                    break
                except ValueError:
                    print("⚠️  Numero CC non valido, continuando...")

    def test_cue_button(self, cc_number, description):
        """Test specifico per cue button"""
        print(f"\n🧪 TEST CUE BUTTON: {cc_number}")
        print(f"   Descrizione: {description}")

        # Press e release per button
        print("   📤 CUE PRESS (127)")
        self.midiout.send_message([0xB0, cc_number, 127])
        time.sleep(1)

        print("   📤 CUE RELEASE (0)")
        self.midiout.send_message([0xB0, cc_number, 0])
        time.sleep(1)

    def discover_master_volume(self):
        """Discovery per Master Volume"""
        self.show_learn_mode_instructions("Main Volume")
        input("\n▶️  Premi INVIO quando il learn mode è ATTIVO per 'Main Volume'...")

        # Range per master: CC 90-127
        ranges = [(90, 99), (100, 109), (110, 119), (120, 127)]

        for start, end in ranges:
            print(f"\n🔍 Testing range CC {start}-{end} per Master Volume...")
            self.discover_cc_range(start, end)

            response = input(f"\n❓ Traktor ha imparato qualche CC nel range {start}-{end}? (y/n): ").strip().lower()
            if response == 'y':
                cc_found = input("🎯 Quale CC ha imparato? (numero): ").strip()
                try:
                    cc_num = int(cc_found)
                    self.discovered_commands['master_volume'] = cc_num
                    print(f"✅ SCOPERTO: master_volume = CC {cc_num}")

                    # Test master volume
                    print("\n🧪 Testing Master Volume...")
                    self.test_discovered_cc(cc_num, "Master Volume")

                    confirm = input("\n❓ Il Master Volume si muove correttamente? (y/n): ").strip().lower()
                    if confirm == 'y':
                        print("✅ CC CONFERMATO e FUNZIONANTE!")
                        return cc_num
                except ValueError:
                    print("⚠️  Numero CC non valido, continuando...")

        print("❌ Nessun CC trovato per master_volume nel range 90-127")
        return None

    def show_results(self):
        """Mostra risultati discovery"""
        print("\n" + "="*60)
        print("🏆 RISULTATI MIDI LEARN DISCOVERY")
        print("="*60)

        if self.discovered_commands:
            for command, cc in self.discovered_commands.items():
                print(f"✅ {command:15} = CC {cc}")
        else:
            print("❌ Nessun comando scoperto")

        print("\n📝 Prossimi passi:")
        print("   1. Aggiorna il mapping Traktor con i CC scoperti")
        print("   2. Aggiorna traktor_control.py con i nuovi CC")
        print("   3. Re-testa il sistema completo")

    def run_full_discovery(self):
        """Esegue discovery completo"""
        print("🎯 MIDI LEARN MODE DISCOVERY")
        print("="*40)
        print("🎯 OBIETTIVO: Scoprire CC corretti per comandi problematici")
        print("="*40)

        if not self.find_iac_bus():
            return

        try:
            print("\n🚀 Iniziando discovery per comandi problematici...")

            # Priorità 1: deck_b_volume
            print("\n" + "🔴"*20)
            print("PRIORITÀ 1: DECK B VOLUME")
            print("🔴"*20)
            self.discover_deck_b_volume()

            # Priorità 2 e 3: Cue buttons
            print("\n" + "🟡"*20)
            print("PRIORITÀ 2-3: CUE BUTTONS")
            print("🟡"*20)
            self.discover_cue_buttons()

            # Priorità 4: Master volume
            print("\n" + "🟢"*20)
            print("PRIORITÀ 4: MASTER VOLUME")
            print("🟢"*20)
            self.discover_master_volume()

            # Risultati finali
            self.show_results()

        except KeyboardInterrupt:
            print("\n⏹️  Discovery interrotto dall'utente")
        except Exception as e:
            print(f"❌ Errore durante discovery: {e}")
        finally:
            self.midiout.close_port()
            print("\n🔌 Connessione MIDI chiusa")

def main():
    discovery = MIDILearnDiscovery()
    discovery.run_full_discovery()

if __name__ == "__main__":
    main()