#!/usr/bin/env python3
"""
🔄 Update Traktor Mappings - Aggiornamento automatico traktor_control.py
Applica le correzioni CC per risolvere i conflitti identificati
"""

import re
import shutil
from datetime import datetime

class TraktorMappingUpdater:
    def __init__(self):
        self.traktor_file = 'traktor_control.py'
        self.backup_suffix = f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Mappature corrette per risolvere i conflitti
        self.corrected_mappings = {
            # Problemi risolti:
            # - deck_c_pitch: CC 42 → CC 130 (conflitto con Sync On Deck 3)
            # - deck_d_pitch: CC 43 → CC 131 (conflitto con Sync On Deck C + Load Selected Deck A)
            # - deck_d_loop_in: CC 56 → CC 132 (conflitto con Select Up/down Browser)

            'deck_c_pitch': 130,
            'deck_d_pitch': 131,
            'deck_d_loop_in': 132
        }

        # Note sui problemi risolti
        self.resolution_notes = {
            'deck_c_pitch': 'RISOLTO: CC 42 → 130 (conflitto Sync On Deck 3)',
            'deck_d_pitch': 'RISOLTO: CC 43 → 131 (CONFLITTO MULTIPLO: 2 controlli usavano CC 43)',
            'deck_d_loop_in': 'RISOLTO: CC 56 → 132 (conflitto Select Up/down Browser)'
        }

    def create_backup(self):
        """Crea backup del file traktor_control.py"""
        try:
            backup_file = f"{self.traktor_file}{self.backup_suffix}"
            shutil.copy2(self.traktor_file, backup_file)
            print(f"✅ Backup creato: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Errore creazione backup: {e}")
            return False

    def read_traktor_file(self):
        """Legge il contenuto del file traktor_control.py"""
        try:
            with open(self.traktor_file, 'r') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"❌ Errore lettura file: {e}")
            return None

    def update_midi_mappings(self, content):
        """Aggiorna le mappature MIDI nel contenuto"""
        updated_content = content

        # Pattern per trovare le mappature MIDI
        midi_map_patterns = {
            'deck_c_pitch': r"'deck_c_pitch':\s*\([^,]+,\s*(\d+)\)",
            'deck_d_pitch': r"'deck_d_pitch':\s*\([^,]+,\s*(\d+)\)",
            'deck_d_loop_in': r"'deck_d_loop_in':\s*\([^,]+,\s*(\d+)\)"
        }

        for control_name, new_cc in self.corrected_mappings.items():
            if control_name in midi_map_patterns:
                pattern = midi_map_patterns[control_name]

                # Trova il match
                match = re.search(pattern, updated_content)
                if match:
                    old_cc = match.group(1)
                    old_line = match.group(0)

                    # Crea la nuova linea con commento
                    note = self.resolution_notes[control_name]
                    new_line = old_line.replace(old_cc, str(new_cc))
                    new_line_with_comment = f"{new_line},  # {note}"

                    # Sostituisci nel contenuto
                    updated_content = updated_content.replace(old_line, new_line_with_comment)

                    print(f"✅ {control_name}: CC {old_cc} → {new_cc}")
                else:
                    print(f"⚠️ Pattern non trovato per {control_name}")

        return updated_content

    def add_resolution_comments(self, content):
        """Aggiunge commenti esplicativi per le risoluzioni"""

        # Trova la sezione MIDI_MAP e aggiungi commento di intestazione
        midi_map_comment = """
# =============================================================================
# RISOLUZIONE CONFLITTI CC - Aggiornamento del {timestamp}
# =============================================================================
# Conflitti risolti:
# - deck_c_pitch: CC 42 → 130 (conflitto con Sync On Deck 3)
# - deck_d_pitch: CC 43 → 131 (conflitto con Sync On Deck C + Load Selected Deck A)
# - deck_d_loop_in: CC 56 → 132 (conflitto con Select Up/down Browser)
# =============================================================================
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # Inserisci il commento prima di MIDI_MAP
        if 'MIDI_MAP = {' in content:
            content = content.replace('MIDI_MAP = {', f"{midi_map_comment}\nMIDI_MAP = {{")

        return content

    def write_updated_file(self, content):
        """Scrive il contenuto aggiornato nel file"""
        try:
            with open(self.traktor_file, 'w') as f:
                f.write(content)
            print(f"✅ File aggiornato: {self.traktor_file}")
            return True
        except Exception as e:
            print(f"❌ Errore scrittura file: {e}")
            return False

    def update_mappings(self):
        """Processo completo di aggiornamento mappature"""
        print("🔄 TRAKTOR MAPPINGS UPDATER")
        print("=" * 60)
        print("🎯 OBIETTIVO: Aggiornare traktor_control.py con CC corretti")
        print("📊 CONFLITTI DA RISOLVERE: 3")
        print("=" * 60)

        print(f"\n📋 MAPPATURE DA AGGIORNARE:")
        for control_name, new_cc in self.corrected_mappings.items():
            note = self.resolution_notes[control_name]
            print(f"   • {control_name}: → CC {new_cc}")
            print(f"     {note}")

        # Conferma utente
        response = input(f"\n❓ Procedere con l'aggiornamento? (y/n): ").lower().strip()
        if response != 'y':
            print("❌ Aggiornamento annullato")
            return False

        # Step 1: Backup
        print(f"\n📦 Step 1: Creazione backup...")
        if not self.create_backup():
            return False

        # Step 2: Lettura file
        print(f"\n📖 Step 2: Lettura file corrente...")
        content = self.read_traktor_file()
        if content is None:
            return False

        # Step 3: Aggiornamento mappature
        print(f"\n🔧 Step 3: Aggiornamento mappature MIDI...")
        updated_content = self.update_midi_mappings(content)

        # Step 4: Aggiunta commenti
        print(f"\n💬 Step 4: Aggiunta commenti risolutivi...")
        updated_content = self.add_resolution_comments(updated_content)

        # Step 5: Scrittura file
        print(f"\n💾 Step 5: Scrittura file aggiornato...")
        if not self.write_updated_file(updated_content):
            return False

        # Riepilogo finale
        print(f"\n🎉 AGGIORNAMENTO COMPLETATO!")
        print(f"✅ File traktor_control.py aggiornato con successo")
        print(f"📦 Backup disponibile: {self.traktor_file}{self.backup_suffix}")

        print(f"\n🚀 PROSSIMI PASSI:")
        print("   1. Verifica le modifiche nel file traktor_control.py")
        print("   2. Testa i controlli aggiornati con il CC Conflict Resolver")
        print("   3. Esporta nuova mappatura TSI da Traktor Controller Manager")

        return True

    def validate_updates(self):
        """Valida che gli aggiornamenti siano stati applicati correttamente"""
        print("🔍 VALIDAZIONE AGGIORNAMENTI")
        print("=" * 50)

        content = self.read_traktor_file()
        if content is None:
            return False

        validation_passed = True

        for control_name, expected_cc in self.corrected_mappings.items():
            # Cerca il pattern nel file
            pattern = f"'{control_name}'.*?{expected_cc}"
            if re.search(pattern, content):
                print(f"✅ {control_name}: CC {expected_cc} trovato")
            else:
                print(f"❌ {control_name}: CC {expected_cc} NON trovato")
                validation_passed = False

        if validation_passed:
            print(f"\n🎉 Validazione SUPERATA - Tutti gli aggiornamenti applicati")
        else:
            print(f"\n⚠️ Validazione FALLITA - Controllare manualmente il file")

        return validation_passed

def main():
    print("🔄 Traktor Mappings Updater")
    print("Aggiornamento automatico mappature CC")
    print("=" * 50)
    print("Opzioni:")
    print("1. Aggiorna Mappature (Risolvi Conflitti)")
    print("2. Valida Aggiornamenti")
    print("3. Esci")

    choice = input("\nInserisci scelta (1/2/3): ").strip()

    updater = TraktorMappingUpdater()

    if choice == "1":
        updater.update_mappings()
    elif choice == "2":
        updater.validate_updates()
    elif choice == "3":
        print("👋 Ciao!")
    else:
        print("❌ Scelta non valida")

if __name__ == "__main__":
    main()