#!/usr/bin/env python3
"""
🔧 CC Conflict Resolver - Risoluzione automatica conflitti MIDI CC
Analizza e risolve i conflitti identificati nelle mappature Traktor

⚠️ DEPRECATION NOTICE (2025-10-04):
   Questo file è stato SOSTITUITO da tsi_mapping_validator.py

   MOTIVO: L'analisi TSI ha confermato che i "conflitti" erano teorici.
   Le mappature CC 2, 3, 4 sono funzionali grazie al deck isolation.

   UTILIZZARE INVECE:
   - tsi_mapping_validator.py (nuovo strumento di validazione)
   - tempo_adjust_learn_helper.py (aggiornato con TSI CC)

   File mantenuto per riferimento storico.
"""

import time
import rtmidi
import json
from datetime import datetime

class CCConflictResolver:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None

        # Conflitti identificati dall'utente
        self.identified_conflicts = {
            'deck_c_pitch': {
                'current_cc': 42,
                'conflicts_with': ['Sync On Deck 3'],
                'traktor_path': 'Deck C > Tempo Adjust',
                'priority': 'HIGH'
            },
            'deck_d_pitch': {
                'current_cc': 43,
                'conflicts_with': ['Sync On Deck C', 'Load Selected Deck A'],
                'traktor_path': 'Deck D > Tempo Adjust',
                'priority': 'HIGH',
                'multiple_conflicts': True,
                'conflict_count': 2
            },
            'deck_d_loop_in': {
                'current_cc': 56,
                'conflicts_with': ['Select Up/down (Browser.Tree) Global'],
                'traktor_path': 'Deck D > Loop In',
                'priority': 'MEDIUM'
            }
        }

        # CC attualmente in uso (da analisi precedenti + conflitti noti)
        self.used_ccs = {
            # FX Units (confermati)
            76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91,
            92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107,
            108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120,

            # Sync/Cue controls (confermati)
            24, 25, 26, 27, 80, 81, 82, 83,

            # Pitch controls (problematici)
            40, 41, 42, 43,

            # Loop controls
            53, 54, 55, 56, 57, 58, 121, 122, 123, 124, 125, 126,

            # Altri controlli noti
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
            28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
            44, 45, 46, 47, 48, 49, 50, 51, 52,
            59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75,
            127  # Spesso usato per controlli speciali
        }

        # Suggerimenti CC alternativi (range liberi identificati)
        self.alternative_ccs = {
            # Range 128-255 non standard ma spesso disponibili
            'high_range': list(range(128, 140)),

            # Range bassi non ancora utilizzati
            'low_available': [130, 131, 132, 133, 134, 135, 136, 137, 138, 139],

            # Range medi liberi
            'mid_available': [250, 251, 252, 253, 254, 255]
        }

        # Soluzioni proposte per ogni conflitto
        self.proposed_solutions = {
            'deck_c_pitch': {
                'new_cc': 130,
                'reason': 'CC 130 è nel range alto libero, lontano da controlli esistenti',
                'test_values': [0, 32, 64, 96, 127]  # Range pitch completo
            },
            'deck_d_pitch': {
                'new_cc': 131,
                'reason': 'CC 131 è adiacente a Deck C per consistenza, risolve DOPPIO conflitto (CC 43 usato da 2 controlli)',
                'test_values': [0, 32, 64, 96, 127],  # Range pitch completo
                'additional_note': 'ATTENZIONE: Conflitto multiplo - CC 43 condiviso da Sync On Deck C + Load Selected Deck A'
            },
            'deck_d_loop_in': {
                'new_cc': 132,
                'reason': 'CC 132 è nel range libero, separato da controlli browser',
                'test_values': [127]  # Button press
            }
        }

    def connect_midi(self):
        """Connect to IAC Bus 1"""
        print("🔍 Searching for MIDI ports...")

        for i, port in enumerate(self.out_ports):
            print(f"  [{i}] {port}")

        for i, port in enumerate(self.out_ports):
            if "IAC" in port and ("Bus 1" in port or " 1" in port):
                self.iac_port = i
                break

        if self.iac_port is None:
            print("❌ IAC Bus 1 not found!")
            return False

        try:
            self.midiout.open_port(self.iac_port)
            print(f"✅ Connected to: {self.out_ports[self.iac_port]}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def send_cc(self, cc, value=127):
        """Send MIDI CC on channel 1"""
        try:
            message = [0xB0, cc, value]
            self.midiout.send_message(message)
            return True
        except Exception as e:
            print(f"❌ MIDI error: {e}")
            return False

    def analyze_conflicts(self):
        """Analizza i conflitti identificati"""
        print("🔧 CC CONFLICT RESOLVER")
        print("=" * 70)
        print("🎯 OBIETTIVO: Risolvere conflitti CC nelle mappature Traktor")
        print("📊 CONFLITTI IDENTIFICATI: 3")
        print("🔢 CC IN CONFLITTO: 42, 43, 56")
        print("=" * 70)

        print(f"\n📋 ANALISI CONFLITTI:")

        for control_name, conflict_info in self.identified_conflicts.items():
            print(f"\n❌ {control_name.upper()}:")
            print(f"   📡 CC Attuale: {conflict_info['current_cc']}")
            print(f"   🎯 Controllo: {conflict_info['traktor_path']}")
            print(f"   ⚠️  Conflitti: {', '.join(conflict_info['conflicts_with'])}")
            print(f"   🔥 Priorità: {conflict_info['priority']}")

            # Evidenzia conflitti multipli
            if conflict_info.get('multiple_conflicts'):
                count = conflict_info.get('conflict_count', len(conflict_info['conflicts_with']))
                print(f"   🚨 CONFLITTO MULTIPLO: {count} controlli usano lo stesso CC!")

        # Mostra soluzioni proposte
        print(f"\n✅ SOLUZIONI PROPOSTE:")

        for control_name, solution in self.proposed_solutions.items():
            conflict = self.identified_conflicts[control_name]
            print(f"\n🔧 {control_name.upper()}:")
            print(f"   📡 CC Attuale: {conflict['current_cc']} → Nuovo CC: {solution['new_cc']}")
            print(f"   💡 Motivo: {solution['reason']}")

            # Nota aggiuntiva per conflitti multipli
            if 'additional_note' in solution:
                print(f"   🚨 {solution['additional_note']}")

        return True

    def resolve_single_conflict(self, control_name):
        """Risolve un singolo conflitto con Learn mode"""
        conflict = self.identified_conflicts[control_name]
        solution = self.proposed_solutions[control_name]

        print(f"\n🔧 RISOLUZIONE: {control_name.upper()}")
        print(f"   🎯 Target: {conflict['traktor_path']}")
        print(f"   📡 Nuovo CC: {solution['new_cc']}")
        print(f"   💡 Motivo: {solution['reason']}")

        # Avviso speciale per conflitti multipli
        if conflict.get('multiple_conflicts'):
            print(f"   🚨 ATTENZIONE: Questo risolve un conflitto MULTIPLO!")
            print(f"   🚨 CC {conflict['current_cc']} era usato da {conflict['conflict_count']} controlli diversi")

        print(f"\n📋 PASSI TRAKTOR:")
        print(f"   1. Apri Controller Manager")
        print(f"   2. Trova il controllo: {conflict['traktor_path']}")
        print(f"   3. Clicca 'Learn' sul controllo")
        print(f"   4. Premi ENTER qui sotto per inviare il nuovo CC")

        input(f"   ⏸️  Pronto per CC {solution['new_cc']}? Premi ENTER...")

        # Test del nuovo CC
        success_count = 0

        for value in solution['test_values']:
            print(f"   📤 Invio: CC {solution['new_cc']} = {value}")
            success = self.send_cc(solution['new_cc'], value)

            if success:
                success_count += 1
                time.sleep(0.3)

        print(f"   ✅ Test CC completati: {success_count}/{len(solution['test_values'])}")

        # Conferma utente
        while True:
            result = input(f"   ❓ Mappatura confermata in Traktor? (y/n/r=retry): ").lower().strip()

            if result == 'y':
                print(f"   🎉 {control_name} risolto con successo!")
                return True
            elif result == 'n':
                print(f"   ⚠️  {control_name} necessita configurazione manuale")
                return False
            elif result == 'r':
                print(f"   🔄 Ripeto test CC {solution['new_cc']}...")
                for value in solution['test_values']:
                    self.send_cc(solution['new_cc'], value)
                    time.sleep(0.3)
            else:
                print(f"   ⚠️  Inserisci 'y', 'n', o 'r'")

    def resolve_all_conflicts(self):
        """Risolve tutti i conflitti in sequenza"""
        print(f"\n🚀 INIZIO RISOLUZIONE CONFLITTI")

        if not self.connect_midi():
            return

        # Analisi iniziale
        self.analyze_conflicts()

        print(f"\n📋 PRE-RISOLUZIONE CHECKLIST:")
        print("✅ 1. Traktor Pro 3 è aperto")
        print("✅ 2. Controller Manager è aperto")
        print("✅ 3. La mappatura attuale è caricata")
        print("✅ 4. Tutti i deck sono visibili")

        input(f"\n⏸️  Premi ENTER per iniziare la risoluzione...")

        resolved_count = 0
        total_conflicts = len(self.identified_conflicts)

        # Risolvi conflitti in ordine di priorità
        priority_order = ['deck_c_pitch', 'deck_d_pitch', 'deck_d_loop_in']

        for control_name in priority_order:
            if control_name in self.identified_conflicts:
                print(f"\n{'='*50}")
                success = self.resolve_single_conflict(control_name)
                if success:
                    resolved_count += 1

                if control_name != priority_order[-1]:
                    input(f"\n⏭️  Premi ENTER per continuare al prossimo conflitto...")

        # Riepilogo finale
        print(f"\n🏆{'='*60}🏆")
        print("RISOLUZIONE CONFLITTI CC - RISULTATI")
        print(f"🏆{'='*60}🏆")

        success_rate = (resolved_count / total_conflicts) * 100
        print(f"\n📊 RISULTATI FINALI:")
        print(f"   Conflitti Risolti: {resolved_count}/{total_conflicts}")
        print(f"   Tasso di Successo: {success_rate:.1f}%")

        if success_rate == 100:
            status = "🎉 PERFETTO - Tutti i conflitti risolti!"
        elif success_rate >= 66:
            status = "✅ BUONO - Maggior parte dei conflitti risolti"
        else:
            status = "⚠️ PARZIALE - Alcuni conflitti richiedono attenzione manuale"

        print(f"   Status: {status}")

        # Genera mappature aggiornate
        self.generate_updated_mappings()

        print(f"\n💾 PROSSIMI PASSI:")
        print("   ✅ Esporta il file TSI aggiornato da Controller Manager")
        print("   ✅ Testa tutti i controlli per verificare il funzionamento")
        print("   ✅ Aggiorna traktor_control.py con i nuovi CC")

        return resolved_count

    def generate_updated_mappings(self):
        """Genera le mappature aggiornate per traktor_control.py"""
        print(f"\n💻 MAPPATURE AGGIORNATE PER TRAKTOR_CONTROL.PY:")
        print("=" * 60)

        print("# Aggiorna questi CC nel MIDI_MAP:")
        for control_name, solution in self.proposed_solutions.items():
            control_key = control_name
            new_cc = solution['new_cc']
            print(f"'{control_key}': (MIDIChannel.AI_CONTROL.value, {new_cc}),  # RISOLTO CONFLITTO")

        print(f"\n# Mappature complete aggiornate:")
        print("UPDATED_MIDI_MAP = {")

        # Pitch controls aggiornati
        print("    # Pitch/Tempo Adjust Controls (AGGIORNATI)")
        print("    'deck_a_pitch': (MIDIChannel.AI_CONTROL.value, 41),  # CONFERMATO")
        print("    'deck_b_pitch': (MIDIChannel.AI_CONTROL.value, 40),  # CONFERMATO")
        print(f"    'deck_c_pitch': (MIDIChannel.AI_CONTROL.value, {self.proposed_solutions['deck_c_pitch']['new_cc']}),  # RISOLTO da CC 42")
        print(f"    'deck_d_pitch': (MIDIChannel.AI_CONTROL.value, {self.proposed_solutions['deck_d_pitch']['new_cc']}),  # RISOLTO da CC 43")

        # Loop controls aggiornati
        print("    # Loop Controls (AGGIORNATI)")
        print("    'deck_d_loop_in': (MIDIChannel.AI_CONTROL.value, 132),  # RISOLTO da CC 56")
        print("}")

    def test_resolved_mappings(self):
        """Test rapido delle mappature risolte"""
        print("🧪 TEST RAPIDO MAPPATURE RISOLTE")
        print("=" * 50)

        if not self.connect_midi():
            return

        print("\n🎵 Test controlli risolti...")

        for control_name, solution in self.proposed_solutions.items():
            cc = solution['new_cc']
            test_values = solution['test_values']

            print(f"\n📤 {control_name}: CC {cc}")

            for value in test_values:
                print(f"   Valore: {value}")
                self.send_cc(cc, value)
                time.sleep(0.4)

        print(f"\n✅ Test completato - verifica le risposte in Traktor")

    def save_conflict_report(self):
        """Salva un report dei conflitti e soluzioni"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cc_conflict_report_{timestamp}.json"

        report = {
            'timestamp': timestamp,
            'conflicts_identified': self.identified_conflicts,
            'proposed_solutions': self.proposed_solutions,
            'status': 'READY_FOR_RESOLUTION'
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Report salvato: {filename}")

def main():
    print("🔧 CC Conflict Resolver")
    print("Risoluzione automatica conflitti MIDI CC Traktor")
    print("=" * 60)
    print("Opzioni disponibili:")
    print("1. Analizza e Risolvi Tutti i Conflitti")
    print("2. Test Mappature Risolte")
    print("3. Genera Report Conflitti")
    print("4. Esci")

    choice = input("\nInserisci scelta (1/2/3/4): ").strip()

    resolver = CCConflictResolver()

    if choice == "1":
        resolver.resolve_all_conflicts()
    elif choice == "2":
        resolver.test_resolved_mappings()
    elif choice == "3":
        resolver.save_conflict_report()
    elif choice == "4":
        print("👋 Ciao!")
    else:
        print("❌ Scelta non valida")

if __name__ == "__main__":
    main()