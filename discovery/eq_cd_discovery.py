#!/usr/bin/env python3
"""
🎛️ EQ DECK C&D DISCOVERY HELPER
Validazione e discovery per EQ deck C&D - Completamento sistema 4-deck

Funzionalità:
1. Analizza pattern EQ esistenti deck A&B
2. Scopre CC per EQ deck C&D basandosi su pattern
3. Test High/Mid/Low per ogni deck
4. Test kill/boost per EQ professionale
5. Auto-update traktor_control.py

EQ esistenti (CONFERMATI):
- deck_a_eq_high: CC 34 ✅
- deck_a_eq_mid: CC 35 ✅
- deck_a_eq_low: CC 36 ✅
- deck_b_eq_high: CC 50 ✅
- deck_b_eq_mid: CC 51 ✅
- deck_b_eq_low: CC 52 ✅

Pattern identificato:
- Deck A: CC 34-36 (range 3)
- Deck B: CC 50-52 (range 3)
- Gap: 14 CC tra A e B

Prediction per Deck C&D:
- Deck C: CC 53-55? o CC 37-39?
- Deck D: CC 56-58? o CC 66-68?

Valori EQ standard:
- 0: KILL (-∞dB)
- 64: NEUTRAL (0dB)
- 127: BOOST (+6dB)
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

class EQDiscovery:
    """Helper per discovery EQ deck C&D"""

    def __init__(self):
        self.midi_out = None
        self.connected = False

        # EQ esistenti (confermati)
        self.existing_eq = {
            'deck_a_eq_high': 34,
            'deck_a_eq_mid': 35,
            'deck_a_eq_low': 36,
            'deck_b_eq_high': 50,
            'deck_b_eq_mid': 51,
            'deck_b_eq_low': 52
        }

        # EQ types per ogni deck
        self.eq_types = ['eq_high', 'eq_mid', 'eq_low']

        # Range di ricerca basati su pattern analysis
        self.search_ranges = {
            'range_1': list(range(37, 50)),   # Tra deck A e B
            'range_2': list(range(53, 70)),   # Dopo deck B
            'range_3': list(range(27, 34)),   # Prima deck A
            'range_4': list(range(66, 80))    # Extended range
        }

        # Valori test EQ
        self.eq_test_values = {
            'kill': 0,      # -∞dB (kill)
            'low': 32,      # -3dB
            'neutral': 64,  # 0dB (flat)
            'high': 96,     # +3dB
            'boost': 127    # +6dB (max boost)
        }

        # Risultati discovery
        self.discovery_results = {
            'pattern_analysis': {},
            'tested_existing': {},
            'discovered_new': {},
            'failed_mappings': [],
            'eq_response_tests': {},
            'session_notes': []
        }

        # Exclude CC già usati
        self.used_ccs = {20, 21, 22, 23, 24, 25, 28, 30, 31, 60, 34, 35, 36, 50, 51, 52,
                        43, 44, 45, 46, 80, 81, 76, 77, 78, 79, 93, 94, 95, 96,
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

    def analyze_existing_pattern(self):
        """Analizza pattern EQ esistenti per predire C&D"""
        print("\n📊 === PATTERN ANALYSIS EQ ESISTENTI ===")

        # Raggruppa per deck
        deck_a_range = [34, 35, 36]  # High, Mid, Low
        deck_b_range = [50, 51, 52]  # High, Mid, Low

        print(f"🎛️ Deck A EQ: CC {deck_a_range[0]}-{deck_a_range[2]} (range: {deck_a_range[2] - deck_a_range[0] + 1})")
        print(f"🎛️ Deck B EQ: CC {deck_b_range[0]}-{deck_b_range[2]} (range: {deck_b_range[2] - deck_b_range[0] + 1})")

        gap = deck_b_range[0] - deck_a_range[2] - 1
        print(f"📏 Gap tra Deck A e B: {gap} CC")

        # Predizioni
        predictions = {
            'deck_c_option1': [53, 54, 55],  # Subito dopo B
            'deck_c_option2': [37, 38, 39],  # Tra A e B
            'deck_d_option1': [56, 57, 58],  # Dopo C option1
            'deck_d_option2': [66, 67, 68],  # Con gap simile
        }

        print("\n🔮 PREDIZIONI BASATE SU PATTERN:")
        for pred_name, cc_range in predictions.items():
            deck = pred_name.split('_')[1].upper()
            option = pred_name.split('_')[2]
            print(f"   {deck} {option}: CC {cc_range[0]}-{cc_range[2]} (high/mid/low)")

        self.discovery_results['pattern_analysis'] = {
            'deck_a_range': deck_a_range,
            'deck_b_range': deck_b_range,
            'gap': gap,
            'predictions': predictions
        }

        return predictions

    def test_eq_response(self, control_name: str, cc: int, eq_type: str) -> Dict[str, Any]:
        """Testa risposta EQ con diversi valori"""
        print(f"\n🎛️ TESTING EQ RESPONSE: {control_name} (CC {cc}) - {eq_type.upper()}")
        print("   💡 Ascolta come cambia il suono del deck")

        response_data = {
            'control': control_name,
            'cc': cc,
            'eq_type': eq_type,
            'tests': {},
            'working': False
        }

        test_sequence = [
            ('neutral', 64, "EQ FLAT (0dB)"),
            ('boost', 127, f"{eq_type.upper()} BOOST (+6dB)"),
            ('neutral', 64, "EQ FLAT (0dB) - reset"),
            ('kill', 0, f"{eq_type.upper()} KILL (-∞dB)"),
            ('neutral', 64, "EQ FLAT (0dB) - final reset")
        ]

        print("   🎯 Sequenza test EQ:")
        for i, (name, value, description) in enumerate(test_sequence, 1):
            print(f"   {i}. {description}")

        user_ready = input(f"\n   ▶️ Pronto per test EQ {eq_type}? (y/n): ").lower()
        if user_ready != 'y':
            print("   ⏭️ Test saltato")
            return response_data

        working_tests = 0
        for i, (test_name, value, description) in enumerate(test_sequence, 1):
            print(f"\n   🎛️ TEST {i}/5: {description}")

            # Invia comando EQ
            self.send_midi_cc(cc, value, f"{control_name} {description}")

            # Aspetta risposta utente
            if test_name == 'kill':
                response = input(f"      Audio {eq_type} ELIMINATO/MUTO? (y/n/s=skip): ").lower()
            elif test_name == 'boost':
                response = input(f"      Audio {eq_type} POTENZIATO? (y/n/s=skip): ").lower()
            else:
                response = input(f"      Audio {eq_type} normale? (y/n/s=skip): ").lower()

            if response == 'y':
                working_tests += 1
                response_data['tests'][test_name] = {'value': value, 'working': True}
                print(f"      ✅ EQ {test_name} funziona")
            elif response == 's':
                print(f"      ⏭️ Test {test_name} saltato")
                break
            else:
                response_data['tests'][test_name] = {'value': value, 'working': False}
                print(f"      ❌ EQ {test_name} non funziona")

            time.sleep(0.8)  # Pausa tra test

        # Determina se il controllo EQ funziona
        response_data['working'] = working_tests >= 3  # Almeno 3 test devono funzionare
        response_data['working_tests_count'] = working_tests

        if response_data['working']:
            print(f"   ✅ {control_name} EQ CONFERMATO ({working_tests}/5 test ok)")
        else:
            print(f"   ❌ {control_name} EQ NON FUNZIONA ({working_tests}/5 test ok)")

        return response_data

    def discover_deck_eq_complete(self, deck: str, search_ranges: List[List[int]]) -> Dict[str, int]:
        """Scopre set completo EQ per un deck (high/mid/low)"""
        print(f"\n🎛️ RICERCA EQ COMPLETO DECK {deck}")
        discovered = {}

        for range_name, cc_range in [
            ('primary', search_ranges[0]),
            ('secondary', search_ranges[1]),
            ('tertiary', search_ranges[2] if len(search_ranges) > 2 else [])
        ]:
            if not cc_range:
                continue

            print(f"\n   🔍 Test range {range_name}: {cc_range[:5]}...")  # Mostra primi 5

            # Filtra CC già usati
            available_ccs = [cc for cc in cc_range if cc not in self.used_ccs]

            if not available_ccs:
                print(f"   ⚠️ Nessun CC disponibile nel range {range_name}")
                continue

            print(f"   📋 CC disponibili: {available_ccs[:10]}...")  # Mostra primi 10

            # Cerca pattern sequenziale (3 CC consecutivi)
            for start_cc in available_ccs:
                if start_cc + 2 in available_ccs and start_cc + 1 in available_ccs:
                    # Possibile pattern trovato
                    test_ccs = [start_cc, start_cc + 1, start_cc + 2]

                    print(f"\n   🎯 Test pattern CC {test_ccs} per deck {deck}")
                    print(f"      Assumendo: {test_ccs[0]}=HIGH, {test_ccs[1]}=MID, {test_ccs[2]}=LOW")

                    # Test ogni EQ del pattern
                    pattern_working = 0
                    pattern_results = {}

                    for i, eq_type in enumerate(['high', 'mid', 'low']):
                        cc = test_ccs[i]
                        control_name = f"deck_{deck.lower()}_eq_{eq_type}"

                        print(f"\n      🧪 Test {control_name} (CC {cc})")

                        # Quick test con kill per identificare velocemente
                        self.send_midi_cc(cc, 0, f"{control_name} KILL test")
                        time.sleep(0.3)

                        result = input(f"         Audio {eq_type.upper()} eliminato per deck {deck}? (y/n/s=skip/q=quit): ").lower()

                        if result == 'y':
                            # Conferma con test completo
                            print(f"         🔄 Conferma con test completo...")
                            response_data = self.test_eq_response(control_name, cc, eq_type)

                            if response_data['working']:
                                pattern_working += 1
                                pattern_results[control_name] = cc
                                discovered[control_name] = cc

                                self.discovery_results['discovered_new'][control_name] = {
                                    'cc': cc, 'type': 'eq', 'eq_type': eq_type,
                                    'deck': deck, 'discovery_time': datetime.now().isoformat(),
                                    'response_data': response_data
                                }
                                print(f"         ✅ CONFERMATO: {control_name} = CC {cc}")
                            else:
                                print(f"         ❌ Test completo fallito per {control_name}")
                        elif result == 'q':
                            return discovered
                        elif result == 's':
                            print(f"         ⏭️ {control_name} saltato")
                            break
                        else:
                            print(f"         ❌ {control_name} non funziona")

                    # Se abbiamo trovato almeno 2 EQ del pattern, consideriamolo valido
                    if pattern_working >= 2:
                        print(f"   ✅ PATTERN VALIDO per Deck {deck}: {pattern_working}/3 EQ trovati")

                        # Marca CC come usati
                        for cc in test_ccs:
                            if cc in [discovered[ctrl] for ctrl in discovered]:
                                self.used_ccs.add(cc)

                        return discovered  # Pattern trovato, stop ricerca
                    else:
                        print(f"   ❌ Pattern non valido: solo {pattern_working}/3 EQ funzionanti")

        return discovered

    def discover_deck_cd_eq(self) -> Dict[str, int]:
        """Scopre EQ per deck C&D"""
        print("\n🔍 === DISCOVERING DECK C&D EQ CONTROLS ===")
        all_discovered = {}

        # Analizza pattern esistenti
        predictions = self.analyze_existing_pattern()

        # Prepara range di ricerca per deck C
        deck_c_ranges = [
            list(range(53, 60)),   # Dopo deck B
            list(range(37, 44)),   # Tra A e B
            list(range(27, 34))    # Prima deck A
        ]

        # Prepara range di ricerca per deck D
        deck_d_ranges = [
            list(range(56, 65)),   # Dopo potenziale deck C
            list(range(66, 73)),   # Gap simile a A-B
            list(range(40, 50))    # Altra area libera
        ]

        print("💡 ISTRUZIONI:")
        print("   1. Carica tracce sui deck C e D")
        print("   2. Metti in play i deck con audio udibile")
        print("   3. Per ogni test EQ, ascolta se il suono cambia")

        # Scopri deck C
        print(f"\n🎛️ === RICERCA EQ DECK C ===")
        deck_c_eq = self.discover_deck_eq_complete('C', deck_c_ranges)
        all_discovered.update(deck_c_eq)

        # Scopri deck D
        print(f"\n🎛️ === RICERCA EQ DECK D ===")
        deck_d_eq = self.discover_deck_eq_complete('D', deck_d_ranges)
        all_discovered.update(deck_d_eq)

        return all_discovered

    def save_results(self) -> str:
        """Salva risultati discovery"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eq_cd_discovery_{timestamp}.json"

        # Aggiungi note di sessione
        self.discovery_results['session_info'] = {
            'timestamp': timestamp,
            'tool': 'eq_cd_discovery.py',
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

        # Nuove mappature scoperte
        for control, data in self.discovery_results['discovered_new'].items():
            cc = data['cc']
            eq_type = data.get('eq_type', 'unknown')
            deck = data.get('deck', 'unknown')
            update_code.append(f"        '{control}': (MIDIChannel.AI_CONTROL.value, {cc}),  # ✅ DISCOVERED ({eq_type} deck {deck})")

        if update_code:
            code_block = "\n".join(update_code)
            print("\n🔧 === CODICE PER AGGIORNARE traktor_control.py ===")
            print("Aggiungi queste righe nella sezione EQ CONTROLS:")
            print("-" * 60)
            print(code_block)
            print("-" * 60)

            # Salva anche su file
            with open("eq_cd_mappings_update.txt", "w") as f:
                f.write("# EQ Deck C&D Mappings Update for traktor_control.py\n")
                f.write("# Add these lines in the EQ CONTROLS section:\n\n")
                f.write(code_block)

            return code_block
        else:
            print("⚠️ Nessun mapping EQ scoperto da aggiornare")
            return ""

    def print_summary(self):
        """Stampa riassunto sessione"""
        print("\n" + "="*60)
        print("🎛️ EQ DECK C&D DISCOVERY SESSION SUMMARY")
        print("="*60)

        pattern_analysis = self.discovery_results.get('pattern_analysis', {})
        discovered = self.discovery_results['discovered_new']
        failed = self.discovery_results['failed_mappings']

        print("📊 PATTERN ANALYSIS:")
        if pattern_analysis:
            predictions = pattern_analysis.get('predictions', {})
            for pred_name, cc_range in predictions.items():
                print(f"   🔮 {pred_name}: CC {cc_range[0]}-{cc_range[2]}")

        print(f"\n🔍 EQ Mappings scoperte: {len(discovered)}")

        # Raggruppa per deck
        deck_c_eq = {k: v for k, v in discovered.items() if 'deck_c' in k}
        deck_d_eq = {k: v for k, v in discovered.items() if 'deck_d' in k}

        if deck_c_eq:
            print("   🎛️ DECK C:")
            for control, data in deck_c_eq.items():
                eq_type = data.get('eq_type', 'unknown')
                working_tests = data.get('response_data', {}).get('working_tests_count', 0)
                print(f"      ✅ {control}: CC {data['cc']} ({eq_type}, {working_tests}/5 test ok)")

        if deck_d_eq:
            print("   🎛️ DECK D:")
            for control, data in deck_d_eq.items():
                eq_type = data.get('eq_type', 'unknown')
                working_tests = data.get('response_data', {}).get('working_tests_count', 0)
                print(f"      ✅ {control}: CC {data['cc']} ({eq_type}, {working_tests}/5 test ok)")

        print(f"\n❌ Mappature fallite: {len(failed)}")
        for failure in failed:
            print(f"   ❌ {failure['control']}: CC {failure['cc']} ({failure['reason']})")

        # Status completamento
        total_eq_expected = 6  # 3 per deck C + 3 per deck D
        total_found = len(discovered)
        completion_rate = (total_found / total_eq_expected) * 100

        print(f"\n📈 COMPLETAMENTO EQ SYSTEM:")
        print(f"   Deck A&B: 6/6 EQ ✅ (existing)")
        print(f"   Deck C&D: {total_found}/6 EQ ({completion_rate:.0f}%)")
        print(f"   TOTAL 4-DECK: {6 + total_found}/12 EQ ({((6 + total_found)/12)*100:.0f}%)")

    def interactive_mode(self):
        """Modalità interactive completa"""
        print("🎛️ EQ DECK C&D DISCOVERY TOOL")
        print("=" * 50)
        print("Questo tool scopre i controlli EQ per deck C&D")
        print("Completando il sistema EQ 4-deck per mixing professionale!")

        if not self.connect_midi():
            print("❌ Impossibile connettere MIDI. Uscita.")
            return

        try:
            while True:
                print("\n📋 MENU EQ C&D DISCOVERY:")
                print("1. Pattern analysis (analizza EQ esistenti)")
                print("2. Discover EQ for deck C&D - COMPLETE SEARCH")
                print("3. Quick EQ test (single CC)")
                print("4. Test EQ response (existing CC)")
                print("5. Show current results")
                print("6. Save results & generate code")
                print("7. Auto-run complete discovery")
                print("q. Quit")

                choice = input("\n🎯 Scegli opzione: ").lower()

                if choice == '1':
                    self.analyze_existing_pattern()
                elif choice == '2':
                    self.discover_deck_cd_eq()
                elif choice == '3':
                    # Quick test
                    try:
                        cc = int(input("Inserisci CC da testare per EQ: "))
                        if 0 <= cc <= 127:
                            eq_type = input("Tipo EQ (high/mid/low): ").lower()
                            if eq_type in ['high', 'mid', 'low']:
                                response_data = self.test_eq_response(f"test_cc_{cc}", cc, eq_type)
                                print(f"Risultato: {'✅ Working EQ' if response_data['working'] else '❌ Not working'}")
                            else:
                                print("❌ Tipo EQ deve essere high/mid/low")
                        else:
                            print("❌ CC deve essere 0-127")
                    except ValueError:
                        print("❌ Inserisci numero valido")

                elif choice == '4':
                    # Test existing CC
                    print("🎛️ EQ esistenti:")
                    for i, (name, cc) in enumerate(self.existing_eq.items(), 1):
                        print(f"   {i}. {name}: CC {cc}")

                    try:
                        idx = int(input("Seleziona EQ da testare (numero): ")) - 1
                        control_name = list(self.existing_eq.keys())[idx]
                        cc = self.existing_eq[control_name]
                        eq_type = control_name.split('_')[-1]  # Extract high/mid/low
                        self.test_eq_response(control_name, cc, eq_type)
                    except (ValueError, IndexError):
                        print("❌ Selezione non valida")

                elif choice == '5':
                    self.print_summary()
                elif choice == '6':
                    self.save_results()
                    self.generate_traktor_control_update()
                elif choice == '7':
                    print("\n🚀 AUTO-RUN: Ricerca completa EQ deck C&D...")
                    self.analyze_existing_pattern()
                    self.discover_deck_cd_eq()
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
            print("👋 EQ Discovery terminato")

def main():
    """Entry point"""
    discovery = EQDiscovery()
    discovery.interactive_mode()

if __name__ == "__main__":
    main()