#!/usr/bin/env python3
"""
🗂️ BROWSER NAVIGATION DISCOVERY HELPER
Validazione e discovery per controlli Browser Navigation - Essenziali per track selection

Funzionalità:
1. Testa CC già mappati: Navigation (49, 56, 64)
2. Scopre controlli browser avanzati
3. Test navigation tree/list/search
4. Test browser functionality workflow
5. Auto-update traktor_control.py

Status CC già mappati:
- browser_select_up_down: CC 49 (🔄 TO TEST)
- browser_tree_up_down: CC 56 (🔄 TO TEST)
- browser_expand_collapse: CC 64 (🔄 TO TEST)
- browser_load_deck_a: CC 43 ✅ CONFIRMED
- browser_load_deck_b: CC 44 ✅ CONFIRMED
- browser_load_deck_c: CC 45 ✅ CONFIRMED
- browser_load_deck_d: CC 46 ✅ CONFIRMED

CC da scoprire:
- browser_preview: CC ??
- browser_search: CC ??
- browser_favorites: CC ??
- browser_back/forward: CC ??
- playlist_up/down: CC ??

Browser workflow:
1. Tree navigation (folder structure)
2. List navigation (tracks in folder)
3. Preview track
4. Load to deck
5. Search functionality
"""

import time
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False
    print("⚠️ rtmidi non disponibile. Installa con: pip install python-rtmidi")
    sys.exit(1)

class BrowserNavDiscovery:
    """Helper per discovery e test controlli Browser Navigation"""

    def __init__(self):
        self.midi_out = None
        self.connected = False

        # Mappature esistenti da testare
        self.existing_mappings = {
            'browser_select_up_down': 49,
            'browser_tree_up_down': 56,
            'browser_expand_collapse': 64,
            'browser_load_deck_a': 43,  # CONFIRMED
            'browser_load_deck_b': 44,  # CONFIRMED
            'browser_load_deck_c': 45,  # CONFIRMED
            'browser_load_deck_d': 46   # CONFIRMED
        }

        # Controlli browser da scoprire
        self.browser_controls_to_find = [
            'browser_preview',
            'browser_search',
            'browser_favorites',
            'browser_back',
            'browser_forward',
            'playlist_up',
            'playlist_down',
            'browser_focus_tracks',
            'browser_focus_tree',
            'browser_enter',
            'browser_escape'
        ]

        # Range di ricerca
        self.search_ranges = {
            'primary_range': list(range(47, 76)),     # Vicino a load commands
            'secondary_range': list(range(1, 20)),    # Range basso
            'tertiary_range': list(range(127, 140))   # Range alto
        }

        # Risultati discovery
        self.discovery_results = {
            'tested_existing': {},
            'discovered_new': {},
            'failed_mappings': [],
            'browser_workflow_tests': {},
            'session_notes': []
        }

        # Exclude CC già usati
        self.used_ccs = {20, 21, 22, 23, 24, 25, 28, 30, 31, 60, 34, 35, 36, 50, 51, 52,
                        43, 44, 45, 46, 49, 56, 64, 80, 81, 76, 77, 78, 79, 93, 94, 95, 96,
                        97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108,
                        109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
                        121, 122, 123, 124, 125, 126}

    def connect_midi(self) -> bool:
        """Connetti a IAC Driver"""
        try:
            self.midi_out = rtmidi.MidiOut()
            output_ports = self.midi_out.get_ports()
            logger.info(f"📋 Porte MIDI disponibili: {output_ports}")

            # Cerca IAC Bus 1
            iac_port_idx = None
            for i, port in enumerate(output_ports):
                if "IAC" in port and "Bus 1" in port:
                    iac_port_idx = i
                    break

            if iac_port_idx is not None:
                self.midi_out.open_port(iac_port_idx)
                self.connected = True
                logger.info(f"✅ Connesso a: {output_ports[iac_port_idx]}")
                return True
            else:
                logger.error("❌ IAC Driver Bus 1 non trovato")
                return False

        except Exception as e:
            logger.error(f"❌ Errore connessione MIDI: {e}")
            return False

    def send_midi_cc(self, cc: int, value: int, description: str = "") -> bool:
        """Invia comando MIDI CC su canale 1"""
        if not self.connected:
            logger.error("❌ MIDI non connesso")
            return False

        try:
            # Control Change su canale 1 (0xB0)
            message = [0xB0, cc, value]
            self.midi_out.send_message(message)
            logger.info(f"📤 MIDI: CC{cc}={value} ({description})")
            return True
        except Exception as e:
            logger.error(f"❌ Errore invio MIDI CC{cc}: {e}")
            return False

    def test_browser_navigation_basic(self, control_name: str, cc: int) -> Dict[str, Any]:
        """Testa controllo navigation basico"""
        print(f"\n🗂️ TESTING BROWSER NAVIGATION: {control_name} (CC {cc})")

        response_data = {
            'control': control_name,
            'cc': cc,
            'tests': {},
            'working': False
        }

        if 'select_up_down' in control_name:
            print("   💡 Questo dovrebbe NAVIGARE SU/GIÙ nella lista tracce")
            test_instructions = [
                "Naviga UP nella lista",
                "Naviga DOWN nella lista",
                "Naviga UP di nuovo"
            ]
            test_values = [1, 127, 1]  # Up/Down values
        elif 'tree_up_down' in control_name:
            print("   💡 Questo dovrebbe NAVIGARE SU/GIÙ nell'albero folder")
            test_instructions = [
                "Naviga UP nell'albero",
                "Naviga DOWN nell'albero",
                "Naviga UP di nuovo"
            ]
            test_values = [1, 127, 1]
        elif 'expand_collapse' in control_name:
            print("   💡 Questo dovrebbe ESPANDERE/COLLASSARE folder")
            test_instructions = [
                "Espandi folder corrente",
                "Collassa folder corrente",
                "Espandi di nuovo"
            ]
            test_values = [127, 1, 127]
        else:
            print("   💡 Test generico browser navigation")
            test_instructions = ["Test funzione browser"]
            test_values = [127]

        proceed = input(f"\n   ▶️ Procedere con test {control_name}? (y/n): ").lower()
        if proceed != 'y':
            print("   ⏭️ Test saltato")
            return response_data

        working_tests = 0
        for i, (instruction, value) in enumerate(zip(test_instructions, test_values), 1):
            print(f"\n   🗂️ TEST {i}/{len(test_instructions)}: {instruction}")

            # Invia comando
            self.send_midi_cc(cc, value, f"{control_name} {instruction}")

            # Verifica risposta
            response = input(f"      Vedi {instruction.lower()}? (y/n/s=skip): ").lower()

            if response == 'y':
                working_tests += 1
                response_data['tests'][f'test_{i}'] = {'instruction': instruction, 'working': True}
                print(f"      ✅ Test {i} OK")
            elif response == 's':
                print(f"      ⏭️ Test {i} saltato")
                break
            else:
                response_data['tests'][f'test_{i}'] = {'instruction': instruction, 'working': False}
                print(f"      ❌ Test {i} fallito")

            time.sleep(0.5)

        # Determina se funziona
        response_data['working'] = working_tests >= (len(test_instructions) // 2 + 1)
        response_data['working_tests_count'] = working_tests

        if response_data['working']:
            print(f"   ✅ {control_name} BROWSER NAV CONFERMATO ({working_tests}/{len(test_instructions)} test ok)")
        else:
            print(f"   ❌ {control_name} BROWSER NAV NON FUNZIONA ({working_tests}/{len(test_instructions)} test ok)")

        return response_data

    def test_existing_browser_mappings(self) -> Dict[str, bool]:
        """Testa mappature browser esistenti"""
        print("\n🎯 === TESTING EXISTING BROWSER MAPPINGS ===")
        results = {}

        # Skip load commands (già confermati)
        navigation_controls = {k: v for k, v in self.existing_mappings.items()
                             if 'load_deck' not in k}

        for control_name, cc in navigation_controls.items():
            print(f"\n🧪 Testing {control_name} (CC {cc})")

            # Test controllo navigation
            response_data = self.test_browser_navigation_basic(control_name, cc)

            if response_data['working']:
                results[control_name] = True
                self.discovery_results['tested_existing'][control_name] = {
                    'cc': cc, 'status': 'working', 'test_time': datetime.now().isoformat(),
                    'response_data': response_data
                }
                print(f"   ✅ {control_name} CONFERMATO")
            else:
                results[control_name] = False
                self.discovery_results['failed_mappings'].append({
                    'control': control_name, 'cc': cc, 'reason': 'browser_nav_not_working',
                    'test_details': response_data
                })
                print(f"   ❌ {control_name} NON FUNZIONA")

        return results

    def test_browser_workflow_complete(self) -> Dict[str, Any]:
        """Testa workflow completo browser"""
        print("\n🗂️ === BROWSER WORKFLOW COMPLETE TEST ===")
        print("   💡 Test sequenza completa browser per caricare una traccia")

        workflow_data = {
            'workflow_steps': {},
            'working': False
        }

        workflow_steps = [
            ('focus_browser', "Browser ha focus (visibile)"),
            ('navigate_tree', "Naviga nell'albero folder"),
            ('select_folder', "Seleziona/espandi folder"),
            ('navigate_tracks', "Naviga nella lista tracce"),
            ('preview_track', "Preview traccia (se possibile)"),
            ('load_track', "Carica traccia su deck"),
            ('verify_load', "Verifica caricamento riuscito")
        ]

        print("   🎯 Workflow browser:")
        for i, (step_name, description) in enumerate(workflow_steps, 1):
            print(f"   {i}. {description}")

        proceed = input("\n   ▶️ Procedere con test workflow completo? (y/n): ").lower()
        if proceed != 'y':
            print("   ⏭️ Workflow test saltato")
            return workflow_data

        working_steps = 0
        for i, (step_name, description) in enumerate(workflow_steps, 1):
            print(f"\n   🗂️ STEP {i}/7: {description}")

            if step_name == 'focus_browser':
                result = input("      Browser è visibile e ha focus? (y/n): ").lower()
            elif step_name == 'navigate_tree':
                # Test tree navigation
                if 'browser_tree_up_down' in self.existing_mappings:
                    cc = self.existing_mappings['browser_tree_up_down']
                    self.send_midi_cc(cc, 127, "Tree navigation test")
                result = input("      Tree navigation funziona? (y/n/s=skip): ").lower()
            elif step_name == 'select_folder':
                # Test expand/collapse
                if 'browser_expand_collapse' in self.existing_mappings:
                    cc = self.existing_mappings['browser_expand_collapse']
                    self.send_midi_cc(cc, 127, "Folder expand test")
                result = input("      Folder expand/select funziona? (y/n/s=skip): ").lower()
            elif step_name == 'navigate_tracks':
                # Test list navigation
                if 'browser_select_up_down' in self.existing_mappings:
                    cc = self.existing_mappings['browser_select_up_down']
                    self.send_midi_cc(cc, 127, "Track list navigation test")
                result = input("      Track list navigation funziona? (y/n/s=skip): ").lower()
            elif step_name == 'preview_track':
                result = input("      Riesci a fare preview della traccia? (y/n/s=skip): ").lower()
            elif step_name == 'load_track':
                # Test load
                cc = self.existing_mappings['browser_load_deck_a']
                self.send_midi_cc(cc, 127, "Load track to deck A test")
                result = input("      Traccia caricata su deck A? (y/n/s=skip): ").lower()
            elif step_name == 'verify_load':
                result = input("      Workflow completo riuscito? (y/n): ").lower()

            if result == 'y':
                working_steps += 1
                workflow_data['workflow_steps'][step_name] = True
                print(f"      ✅ Step {step_name} OK")
            elif result == 's':
                print(f"      ⏭️ Step {step_name} saltato")
                continue
            else:
                workflow_data['workflow_steps'][step_name] = False
                print(f"      ❌ Step {step_name} fallito")

            time.sleep(0.5)

        # Determina se workflow funziona
        workflow_data['working'] = working_steps >= 4  # Almeno 4 step devono funzionare
        workflow_data['working_steps_count'] = working_steps

        if workflow_data['working']:
            print(f"   ✅ BROWSER WORKFLOW CONFERMATO ({working_steps}/7 step ok)")
        else:
            print(f"   ❌ BROWSER WORKFLOW INCOMPLETE ({working_steps}/7 step ok)")

        self.discovery_results['browser_workflow_tests']['complete_workflow'] = workflow_data
        return workflow_data

    def discover_advanced_browser_controls(self) -> Dict[str, int]:
        """Scopre controlli browser avanzati"""
        print("\n🔍 === DISCOVERING ADVANCED BROWSER CONTROLS ===")
        discovered = {}

        # Filtra CC già usati
        all_ranges = (self.search_ranges['primary_range'] +
                     self.search_ranges['secondary_range'] +
                     self.search_ranges['tertiary_range'])
        available_ccs = [cc for cc in all_ranges if cc not in self.used_ccs]

        print(f"📋 Testing CC range per advanced browser: {len(available_ccs)} CC disponibili")
        print("💡 ISTRUZIONI:")
        print("   1. Assicurati che il browser sia visibile")
        print("   2. Per ogni test, osserva cambiamenti nel browser")
        print("   3. Test include: preview, search, favorites, etc.")

        for control_type in self.browser_controls_to_find:
            print(f"\n🔎 Ricerca {control_type}")

            # Istruzioni specifiche per tipo controllo
            if 'preview' in control_type:
                instruction = "Dovrebbe fare PREVIEW della traccia selezionata"
            elif 'search' in control_type:
                instruction = "Dovrebbe aprire/attivare la SEARCH"
            elif 'favorites' in control_type:
                instruction = "Dovrebbe aprire/gestire FAVORITES"
            elif 'back' in control_type or 'forward' in control_type:
                instruction = f"Dovrebbe navigare {control_type.split('_')[1].upper()}"
            elif 'playlist' in control_type:
                instruction = f"Dovrebbe navigare playlist {control_type.split('_')[1].upper()}"
            else:
                instruction = f"Dovrebbe controllare {control_type}"

            print(f"   💡 {instruction}")

            # Test primi CC disponibili per questo controllo
            for cc in available_ccs[:8]:  # Limita a 8 test per controllo
                print(f"      🧪 Testing CC {cc} per {control_type}")

                # Test controllo
                self.send_midi_cc(cc, 127, f"{control_type} test")

                user_input = input(f"         {instruction}? (y/n/s=skip/q=quit): ").lower()

                if user_input == 'y':
                    discovered[control_type] = cc
                    self.discovery_results['discovered_new'][control_type] = {
                        'cc': cc, 'type': 'browser_advanced', 'function': control_type,
                        'discovery_time': datetime.now().isoformat()
                    }
                    print(f"         ✅ TROVATO: {control_type} = CC {cc}")
                    self.used_ccs.add(cc)  # Marca come usato
                    break  # Passa al prossimo controllo
                elif user_input == 'q':
                    print("         🚪 Uscita richiesta")
                    return discovered
                elif user_input == 's':
                    print(f"         ⏭️ CC {cc} saltato")
                    break  # Passa al prossimo controllo
                else:
                    print(f"         ❌ CC {cc} non funziona per {control_type}")

                time.sleep(0.3)

            # Se non trovato, passa al prossimo
            if control_type not in discovered:
                print(f"      ⚠️ {control_type} non trovato nei CC testati")

        return discovered

    def save_results(self) -> str:
        """Salva risultati discovery"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"browser_nav_discovery_{timestamp}.json"

        # Aggiungi note di sessione
        self.discovery_results['session_info'] = {
            'timestamp': timestamp,
            'tool': 'browser_nav_discovery.py',
            'total_tested': len(self.discovery_results['tested_existing']),
            'total_discovered': len(self.discovery_results['discovered_new']),
            'failed_count': len(self.discovery_results['failed_mappings'])
        }

        with open(filename, 'w') as f:
            json.dump(self.discovery_results, f, indent=2)

        print(f"💾 Risultati salvati in: {filename}")
        return filename

    def generate_traktor_control_update(self) -> str:
        """Genera codice per aggiornare traktor_control.py"""
        update_code = []

        # Mappature confermate esistenti
        for control, data in self.discovery_results['tested_existing'].items():
            if data['status'] == 'working':
                cc = data['cc']
                update_code.append(f"        '{control}': (MIDIChannel.AI_CONTROL.value, {cc}),  # ✅ CONFIRMED")

        # Nuove mappature scoperte
        for control, data in self.discovery_results['discovered_new'].items():
            cc = data['cc']
            function = data.get('function', 'browser')
            update_code.append(f"        '{control}': (MIDIChannel.AI_CONTROL.value, {cc}),  # ✅ DISCOVERED ({function})")

        if update_code:
            code_block = "\n".join(update_code)
            print("\n🔧 === CODICE PER AGGIORNARE traktor_control.py ===")
            print("Aggiungi/aggiorna queste righe nella sezione BROWSER CONTROLS:")
            print("-" * 60)
            print(code_block)
            print("-" * 60)

            # Salva anche su file
            with open("browser_nav_mappings_update.txt", "w") as f:
                f.write("# Browser Navigation Mappings Update for traktor_control.py\n")
                f.write("# Add/update these lines in the BROWSER CONTROLS section:\n\n")
                f.write(code_block)

            return code_block
        else:
            print("⚠️ Nessun mapping browser confermato da aggiornare")
            return ""

    def print_summary(self):
        """Stampa riassunto sessione"""
        print("\n" + "="*60)
        print("🗂️ BROWSER NAVIGATION DISCOVERY SESSION SUMMARY")
        print("="*60)

        tested = self.discovery_results['tested_existing']
        discovered = self.discovery_results['discovered_new']
        failed = self.discovery_results['failed_mappings']
        workflow_tests = self.discovery_results['browser_workflow_tests']

        print(f"✅ Mappature esistenti testate: {len(tested)}")
        for control, data in tested.items():
            status = "✅" if data['status'] == 'working' else "❌"
            working_tests = data.get('response_data', {}).get('working_tests_count', 0)
            print(f"   {status} {control}: CC {data['cc']} ({working_tests} test ok)")

        print(f"\n🔍 Nuove mappature scoperte: {len(discovered)}")
        for control, data in discovered.items():
            function = data.get('function', 'unknown')
            print(f"   ✅ {control}: CC {data['cc']} ({function})")

        print(f"\n🗂️ Test workflow browser: {len(workflow_tests)}")
        for workflow_name, workflow in workflow_tests.items():
            status = "✅" if workflow['working'] else "❌"
            working_count = workflow.get('working_steps_count', 0)
            print(f"   {status} {workflow_name}: {working_count}/7 step funzionanti")

        print(f"\n❌ Mappature fallite: {len(failed)}")
        for failure in failed:
            print(f"   ❌ {failure['control']}: CC {failure['cc']} ({failure['reason']})")

        # Status completamento browser
        basic_controls = 3  # select_up_down, tree_up_down, expand_collapse
        load_controls = 4   # load_deck_a/b/c/d
        tested_working = sum(1 for data in tested.values() if data['status'] == 'working')
        advanced_discovered = len(discovered)

        print(f"\n📈 COMPLETAMENTO BROWSER SYSTEM:")
        print(f"   Navigation basic: {tested_working}/{basic_controls} ({'✅' if tested_working == basic_controls else '🔄'})")
        print(f"   Load controls: 4/4 ✅ (existing confirmed)")
        print(f"   Advanced controls: {advanced_discovered}/{len(self.browser_controls_to_find)} ({(advanced_discovered/len(self.browser_controls_to_find)*100):.0f}%)")

    def interactive_mode(self):
        """Modalità interactive completa"""
        print("🗂️ BROWSER NAVIGATION DISCOVERY TOOL")
        print("=" * 50)
        print("Questo tool testa e scopre controlli Browser Navigation")
        print("Essenziali per selezione intelligente delle tracce!")

        if not self.connect_midi():
            print("❌ Impossibile connettere MIDI. Uscita.")
            return

        try:
            while True:
                print("\n📋 MENU BROWSER NAVIGATION DISCOVERY:")
                print("1. Test existing browser mappings")
                print("2. Test complete browser workflow")
                print("3. Discover advanced browser controls")
                print("4. Quick browser test (single CC)")
                print("5. Show current results")
                print("6. Save results & generate code")
                print("7. Auto-run all tests")
                print("q. Quit")

                choice = input("\n🎯 Scegli opzione: ").lower()

                if choice == '1':
                    self.test_existing_browser_mappings()
                elif choice == '2':
                    self.test_browser_workflow_complete()
                elif choice == '3':
                    self.discover_advanced_browser_controls()
                elif choice == '4':
                    # Quick test
                    try:
                        cc = int(input("Inserisci CC da testare: "))
                        if 0 <= cc <= 127:
                            self.send_midi_cc(cc, 127, f"Quick browser test CC {cc}")
                            result = input("Vedi cambiamento nel browser? (y/n): ").lower()
                            print(f"Risultato: {'✅ Possibile browser control' if result == 'y' else '❌ Non browser control'}")
                        else:
                            print("❌ CC deve essere 0-127")
                    except ValueError:
                        print("❌ Inserisci numero valido")

                elif choice == '5':
                    self.print_summary()
                elif choice == '6':
                    self.save_results()
                    self.generate_traktor_control_update()
                elif choice == '7':
                    print("\n🚀 AUTO-RUN: Eseguo tutti i test...")
                    self.test_existing_browser_mappings()
                    self.test_browser_workflow_complete()
                    self.discover_advanced_browser_controls()
                    self.print_summary()
                    self.save_results()
                    self.generate_traktor_control_update()
                elif choice == 'q':
                    break
                else:
                    print("❌ Opzione non valida")

        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        finally:
            if self.midi_out:
                self.midi_out.close()
            print("👋 Browser Navigation Discovery terminato")

def main():
    """Entry point"""
    discovery = BrowserNavDiscovery()
    discovery.interactive_mode()

if __name__ == "__main__":
    main()