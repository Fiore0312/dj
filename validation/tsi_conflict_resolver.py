#!/usr/bin/env python3
"""
TSI CONFLICT RESOLVER
====================

Script intelligente per analizzare e risolvere i conflitti CC nel file TSI di Traktor Pro 3.
Basato sui problemi identificati:

CONFLITTI TROVATI:
1. Deck C Pitch: CC42 → conflitto con "Sync On Deck 3"
2. Deck D Pitch: CC43 → conflitto con "Sync On Deck C" + "Load Selected Deck A"
3. Loop In Deck D: CC56 → conflitto con "Select Up/down (Browser.Tree) Global"

OBIETTIVO:
- Trovare CC liberi per riassegnare i controlli in conflitto
- Mantenere priorità ai controlli essenziali (Sync, Browser Load)
- Suggerire mappature alternative ottimali

Author: DJ AI System
Date: 2025-10-04
"""

import os
import re
import json
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass

@dataclass
class CCConflict:
    """Rappresenta un conflitto CC con tutte le informazioni necessarie."""
    cc_number: int
    commands: List[str]
    priority_winner: str
    need_reassignment: List[str]
    suggested_new_ccs: List[int]

class TSIConflictResolver:
    """Analyzer e resolver per conflitti CC in file TSI di Traktor."""

    # Priorità dei controlli (più alto = più importante)
    CONTROL_PRIORITIES = {
        # CONTROLLI ESSENZIALI (Alta Priorità)
        'sync': 100,
        'play': 95,
        'cue': 90,
        'load_selected': 85,
        'browser_tree': 80,

        # CONTROLLI TRANSPORT (Media-Alta Priorità)
        'volume': 75,
        'crossfader': 70,
        'eq': 65,

        # CONTROLLI CREATIVI (Media Priorità)
        'pitch': 60,
        'tempo_adjust': 60,
        'loop': 55,
        'hotcue': 50,

        # CONTROLLI FX (Media-Bassa Priorità)
        'fx': 45,
        'filter': 40,

        # CONTROLLI AVANZATI (Bassa Priorità)
        'beatjump': 35,
        'browser_select': 30,
        'browser_expand': 25,
    }

    # Range CC da evitare (noti per usi specifici)
    RESERVED_CC_RANGES = [
        (0, 31),     # Controllers standard MIDI
        (32, 63),    # LSB dei controllers 0-31
        (64, 69),    # Pedali e switch standard
        (120, 127),  # Channel Mode Messages
    ]

    # CC specificamente riservati per Traktor
    TRAKTOR_RESERVED_CCS = [
        1,   # Mod Wheel (spesso usato)
        7,   # Volume (standard MIDI)
        10,  # Pan (standard MIDI)
        11,  # Expression (standard MIDI)
        64,  # Sustain Pedal
        71,  # Filter Resonance
        74,  # Filter Cutoff
    ]

    def __init__(self, tsi_file_path: str):
        """Inizializza il resolver con il path del file TSI."""
        self.tsi_file_path = tsi_file_path
        self.used_ccs: Set[int] = set()
        self.cc_mappings: Dict[int, List[str]] = defaultdict(list)
        self.conflicts: List[CCConflict] = []

    def _extract_cc_from_text(self, text: str) -> List[Tuple[int, str]]:
        """Estrae tutte le associazioni CC e comando dal testo del TSI."""
        cc_mappings = []

        # Pattern per rilevare CC assignments in formato TSI
        patterns = [
            r'<Key>ControllerType</Key>\s*<Value>7</Value>.*?<Key>ControllerValue</Key>\s*<Value>(\d+)</Value>',
            r'Control Change\s*(\d+)',
            r'CC\s*(\d+)',
            r'Controller\s*(\d+)',
        ]

        lines = text.split('\n')
        current_command = None

        for i, line in enumerate(lines):
            # Cerca nomi di comandi/controlli
            if any(keyword in line.lower() for keyword in ['deck', 'sync', 'play', 'cue', 'loop', 'pitch', 'browser', 'fx']):
                # Estrai il nome del comando dalla linea
                command_match = re.search(r'<String>([^<]+)</String>', line)
                if command_match:
                    current_command = command_match.group(1)

            # Cerca CC numbers
            for pattern in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    cc_num = int(match.group(1))
                    if current_command:
                        cc_mappings.append((cc_num, current_command))
                    else:
                        # Usa contesto dalle linee vicine
                        context_lines = lines[max(0, i-5):i+5]
                        context = ' '.join(context_lines)
                        cc_mappings.append((cc_num, f"Unknown_CC_{cc_num}"))

        return cc_mappings

    def analyze_tsi_file(self) -> bool:
        """Analizza il file TSI per estrarre mappings e identificare conflitti."""
        try:
            # Leggi il file TSI (può essere binario o XML)
            with open(self.tsi_file_path, 'rb') as f:
                content = f.read()

            # Prova a decodificare come UTF-8, fallback su latin-1
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                text_content = content.decode('latin-1', errors='ignore')

            # Estrai mappings CC
            cc_mappings = self._extract_cc_from_text(text_content)

            # Popola le strutture dati
            for cc_num, command in cc_mappings:
                self.used_ccs.add(cc_num)
                self.cc_mappings[cc_num].append(command)

            # Identifica conflitti
            self._identify_conflicts()

            return True

        except Exception as e:
            print(f"❌ Errore nell'analisi del file TSI: {e}")
            return False

    def _identify_conflicts(self):
        """Identifica tutti i conflitti CC."""
        for cc_num, commands in self.cc_mappings.items():
            if len(commands) > 1:
                # Determina il winner basato sulla priorità
                winner = max(commands, key=self._get_command_priority)
                need_reassignment = [cmd for cmd in commands if cmd != winner]

                # Trova CC disponibili per riassegnazione
                suggested_ccs = self._find_available_ccs(len(need_reassignment))

                conflict = CCConflict(
                    cc_number=cc_num,
                    commands=commands,
                    priority_winner=winner,
                    need_reassignment=need_reassignment,
                    suggested_new_ccs=suggested_ccs
                )

                self.conflicts.append(conflict)

    def _get_command_priority(self, command: str) -> int:
        """Determina la priorità di un comando."""
        command_lower = command.lower()

        for keyword, priority in self.CONTROL_PRIORITIES.items():
            if keyword in command_lower:
                return priority

        return 0  # Priorità minima per comandi sconosciuti

    def _find_available_ccs(self, count: int) -> List[int]:
        """Trova CC disponibili per riassegnazione."""
        available = []

        # Priorità 1: Range sicuro alto (70-119)
        for cc in range(70, 120):
            if self._is_cc_available(cc):
                available.append(cc)
                if len(available) >= count:
                    return available

        # Priorità 2: Range medio sicuro (34-69)
        for cc in range(34, 70):
            if self._is_cc_available(cc):
                available.append(cc)
                if len(available) >= count:
                    return available

        # Priorità 3: Range alto estremo (121-127) - da usare con cautela
        for cc in range(121, 128):
            if self._is_cc_available(cc):
                available.append(cc)
                if len(available) >= count:
                    return available

        return available

    def _is_cc_available(self, cc: int) -> bool:
        """Verifica se un CC è disponibile per l'uso."""
        # Già in uso
        if cc in self.used_ccs:
            return False

        # In range riservati
        for start, end in self.RESERVED_CC_RANGES:
            if start <= cc <= end:
                return False

        # CC specificamente riservati
        if cc in self.TRAKTOR_RESERVED_CCS:
            return False

        return True

    def generate_conflict_report(self) -> str:
        """Genera un report dettagliato dei conflitti."""
        if not self.conflicts:
            return "✅ Nessun conflitto CC trovato!"

        report = []
        report.append("🚨 TSI CONFLICT ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"File analizzato: {os.path.basename(self.tsi_file_path)}")
        report.append(f"CC totali utilizzati: {len(self.used_ccs)}")
        report.append(f"Conflitti trovati: {len(self.conflicts)}")
        report.append("")

        for i, conflict in enumerate(self.conflicts, 1):
            report.append(f"🔴 CONFLITTO #{i}: CC {conflict.cc_number}")
            report.append(f"   Comandi in conflitto: {', '.join(conflict.commands)}")
            report.append(f"   🏆 MANTIENI: {conflict.priority_winner}")

            for j, cmd in enumerate(conflict.need_reassignment):
                if j < len(conflict.suggested_new_ccs):
                    new_cc = conflict.suggested_new_ccs[j]
                    report.append(f"   🔄 SPOSTA: {cmd} → CC {new_cc}")
                else:
                    report.append(f"   ⚠️ SPOSTA: {cmd} → CC ??? (no CC disponibili)")

            report.append("")

        return "\n".join(report)

    def generate_solution_script(self) -> str:
        """Genera uno script di soluzione per i conflitti."""
        if not self.conflicts:
            return "# Nessun conflitto da risolvere!"

        script_lines = []
        script_lines.append("#!/usr/bin/env python3")
        script_lines.append('"""')
        script_lines.append("SCRIPT AUTOMATICO PER RISOLUZIONE CONFLITTI CC")
        script_lines.append("Generated by TSI Conflict Resolver")
        script_lines.append(f"File TSI: {os.path.basename(self.tsi_file_path)}")
        script_lines.append('"""')
        script_lines.append("")
        script_lines.append("# ISTRUZIONI MANUALI PER TRAKTOR PRO 3:")
        script_lines.append("# 1. Apri Traktor Pro 3")
        script_lines.append("# 2. Vai in Preferences > Controller Manager")
        script_lines.append("# 3. Seleziona il tuo controller")
        script_lines.append("# 4. Applica queste modifiche:")
        script_lines.append("")

        for i, conflict in enumerate(self.conflicts, 1):
            script_lines.append(f"# === CONFLITTO {i}: CC {conflict.cc_number} ===")
            script_lines.append(f"# MANTIENI: {conflict.priority_winner} su CC {conflict.cc_number}")

            for j, cmd in enumerate(conflict.need_reassignment):
                if j < len(conflict.suggested_new_ccs):
                    new_cc = conflict.suggested_new_ccs[j]
                    script_lines.append(f"# SPOSTA: {cmd}")
                    script_lines.append(f"#   Da CC {conflict.cc_number} a CC {new_cc}")
                    script_lines.append(f"#   1. Trova il mapping '{cmd}'")
                    script_lines.append(f"#   2. Cambia 'Control Change {conflict.cc_number}' in 'Control Change {new_cc}'")
                    script_lines.append(f"#   3. Salva e testa")
                else:
                    script_lines.append(f"# PROBLEMA: {cmd} - Nessun CC disponibile!")

            script_lines.append("")

        script_lines.append("# MAPPATURE SUGGERITE PER CONTROLLI SPECIFICI:")
        script_lines.append("")

        # Aggiungi mappature specifiche per i problemi menzionati
        script_lines.append("# === MAPPATURE PITCH/TEMPO ADJUST ===")
        script_lines.append("# NOTA: In Traktor Pro 3, 'Pitch' si chiama 'Tempo Adjust'")
        available_for_pitch = self._find_available_ccs(4)
        if len(available_for_pitch) >= 4:
            script_lines.append(f"# Deck A Tempo Adjust: CC {available_for_pitch[0]}")
            script_lines.append(f"# Deck B Tempo Adjust: CC {available_for_pitch[1]}")
            script_lines.append(f"# Deck C Tempo Adjust: CC {available_for_pitch[2]}")
            script_lines.append(f"# Deck D Tempo Adjust: CC {available_for_pitch[3]}")

        script_lines.append("")
        script_lines.append("# === MAPPATURE LOOP CONTROLS ===")
        available_for_loops = self._find_available_ccs(8)
        if len(available_for_loops) >= 8:
            script_lines.append(f"# Deck A Loop In: CC {available_for_loops[0]}")
            script_lines.append(f"# Deck A Loop Out: CC {available_for_loops[1]}")
            script_lines.append(f"# Deck B Loop In: CC {available_for_loops[2]}")
            script_lines.append(f"# Deck B Loop Out: CC {available_for_loops[3]}")
            script_lines.append(f"# Deck C Loop In: CC {available_for_loops[4]}")
            script_lines.append(f"# Deck C Loop Out: CC {available_for_loops[5]}")
            script_lines.append(f"# Deck D Loop In: CC {available_for_loops[6]}")
            script_lines.append(f"# Deck D Loop Out: CC {available_for_loops[7]}")

        return "\n".join(script_lines)

    def export_results(self, output_dir: str = "."):
        """Esporta i risultati dell'analisi."""
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")

        # Report conflitti
        report_file = os.path.join(output_dir, f"tsi_conflict_report_{timestamp}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_conflict_report())

        # Script soluzione
        solution_file = os.path.join(output_dir, f"tsi_conflict_solution_{timestamp}.py")
        with open(solution_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_solution_script())

        # JSON dati strutturati
        json_file = os.path.join(output_dir, f"tsi_conflict_data_{timestamp}.json")
        data = {
            'tsi_file': self.tsi_file_path,
            'analysis_timestamp': timestamp,
            'total_used_ccs': len(self.used_ccs),
            'used_ccs': sorted(list(self.used_ccs)),
            'conflicts_count': len(self.conflicts),
            'conflicts': [
                {
                    'cc_number': c.cc_number,
                    'commands': c.commands,
                    'priority_winner': c.priority_winner,
                    'need_reassignment': c.need_reassignment,
                    'suggested_new_ccs': c.suggested_new_ccs
                }
                for c in self.conflicts
            ],
            'available_ccs': self._find_available_ccs(50)  # Trova fino a 50 CC disponibili
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {
            'report_file': report_file,
            'solution_file': solution_file,
            'json_file': json_file
        }

def main():
    """Funzione principale per l'analisi e risoluzione conflitti TSI."""
    import argparse

    parser = argparse.ArgumentParser(description="TSI Conflict Resolver per Traktor Pro 3")
    parser.add_argument("tsi_file", help="Path al file TSI da analizzare")
    parser.add_argument("--output-dir", "-o", default=".", help="Directory per output files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Output verboso")

    args = parser.parse_args()

    if not os.path.exists(args.tsi_file):
        print(f"❌ File TSI non trovato: {args.tsi_file}")
        return 1

    print("🔍 TSI CONFLICT RESOLVER - Traktor Pro 3")
    print("=" * 50)
    print(f"📁 Analizzando: {args.tsi_file}")

    # Inizializza e analizza
    resolver = TSIConflictResolver(args.tsi_file)

    if not resolver.analyze_tsi_file():
        print("❌ Errore durante l'analisi del file TSI")
        return 1

    # Mostra risultati
    print(resolver.generate_conflict_report())

    # Esporta risultati
    print("\n📝 Esportando risultati...")
    files = resolver.export_results(args.output_dir)

    print(f"✅ Report salvato: {files['report_file']}")
    print(f"✅ Script soluzione salvato: {files['solution_file']}")
    print(f"✅ Dati JSON salvati: {files['json_file']}")

    if resolver.conflicts:
        print(f"\n🎯 AZIONI RACCOMANDATE:")
        print("1. Leggi il report dettagliato")
        print("2. Applica le modifiche suggerite in Traktor")
        print("3. Testa tutti i controlli dopo le modifiche")
        print("4. Salva il file TSI modificato")
    else:
        print("\n✅ Nessun conflitto trovato - mappatura pulita!")

    return 0

if __name__ == "__main__":
    exit(main())