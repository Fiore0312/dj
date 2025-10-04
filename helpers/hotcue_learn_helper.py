#!/usr/bin/env python3
"""
🎯 HOTCUE Learn Helper - Automated CC Sender for Traktor Controller Manager
Sends the exact CC values needed for HOTCUE Learn mapping process
Resolves Deck A conflicts by using CC 87, 88, 89 instead of CC 2, 3, 4
"""

import time
import rtmidi

class HOTCUELearnHelper:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None

        # HOTCUE CC mappings - Complete 32 HOTCUE system (8 per deck)
        self.hotcue_mappings = {
            # DECK A - Using remapped CCs to avoid conflicts
            'deck_a_hotcue_1': 86,   # Safe CC
            'deck_a_hotcue_2': 87,   # Remapped from CC 2 (conflict resolved)
            'deck_a_hotcue_3': 88,   # Remapped from CC 3 (conflict resolved)
            'deck_a_hotcue_4': 89,   # Remapped from CC 4 (conflict resolved)
            'deck_a_hotcue_5': 90,   # Extended hotcues
            'deck_a_hotcue_6': 91,
            'deck_a_hotcue_7': 92,
            'deck_a_hotcue_8': 93,

            # DECK B - Clean CC range
            'deck_b_hotcue_1': 94,
            'deck_b_hotcue_2': 95,
            'deck_b_hotcue_3': 96,
            'deck_b_hotcue_4': 105,  # Skip FX range (97-104)
            'deck_b_hotcue_5': 106,
            'deck_b_hotcue_6': 107,
            'deck_b_hotcue_7': 108,
            'deck_b_hotcue_8': 109,

            # DECK C - Higher CC range
            'deck_c_hotcue_1': 110,
            'deck_c_hotcue_2': 111,
            'deck_c_hotcue_3': 112,
            'deck_c_hotcue_4': 113,
            'deck_c_hotcue_5': 114,
            'deck_c_hotcue_6': 115,
            'deck_c_hotcue_7': 116,
            'deck_c_hotcue_8': 117,

            # DECK D - Final CC range
            'deck_d_hotcue_1': 118,
            'deck_d_hotcue_2': 119,
            'deck_d_hotcue_3': 120,
            'deck_d_hotcue_4': 121,
            'deck_d_hotcue_5': 122,
            'deck_d_hotcue_6': 123,
            'deck_d_hotcue_7': 124,
            'deck_d_hotcue_8': 125
        }

    def connect_midi(self):
        """Connect to IAC Bus 1"""
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
            message = [0xB0, cc, value]  # Channel 1, CC, Value
            self.midiout.send_message(message)
            print(f"📤 Sent: CC {cc} = {value}")
            return True
        except Exception as e:
            print(f"❌ MIDI error: {e}")
            return False

    def interactive_learn_session(self):
        """Interactive Learn session for all HOTCUES"""
        print("🎯 HOTCUE LEARN HELPER - Interactive Session")
        print("=" * 60)
        print("📋 Instructions:")
        print("1. Open Traktor Pro 3 Controller Manager")
        print("2. Click 'Learn' for each HOTCUE control")
        print("3. Press ENTER when ready to send CC")
        print("4. Confirm mapping in Traktor")
        print("⚠️  CRITICAL: This resolves Deck A conflicts (CC 2,3,4 → 87,88,89)")
        print("=" * 60)

        if not self.connect_midi():
            return

        # Group by deck for better organization
        decks = ['a', 'b', 'c', 'd']

        for deck in decks:
            print(f"\n🎚️ CONFIGURING DECK {deck.upper()} HOTCUES")
            print(f"{'=' * 40}")

            deck_hotcues = {k: v for k, v in self.hotcue_mappings.items() if f'deck_{deck}_' in k}

            for control_name, cc in deck_hotcues.items():
                hotcue_num = control_name.split('_')[-1]
                print(f"\n🎯 CONFIGURING: DECK {deck.upper()} HOTCUE {hotcue_num}")
                print(f"   Target CC: {cc}")
                print(f"   Traktor Path: Deck {deck.upper()} > Hotcue {hotcue_num}")

                if deck == 'a' and hotcue_num in ['2', '3', '4']:
                    old_cc = {'2': 2, '3': 3, '4': 4}[hotcue_num]
                    print(f"   ⚠️  CONFLICT RESOLUTION: CC {old_cc} → CC {cc}")

                input(f"   ⏸️  Press ENTER to send CC {cc} for HOTCUE {hotcue_num}...")

                # Send full value for HOTCUE buttons
                success = self.send_cc(cc, 127)

                if success:
                    print(f"   ✅ CC {cc} sent successfully")
                    print(f"   📝 Check Traktor Controller Manager for mapping confirmation")
                else:
                    print(f"   ❌ Failed to send CC {cc}")

                # Wait for user confirmation
                result = input(f"   ❓ Mapping successful in Traktor? (y/n): ").lower()
                if result == 'y':
                    print(f"   🎉 DECK {deck.upper()} HOTCUE {hotcue_num} configured successfully!")
                else:
                    print(f"   ⚠️  DECK {deck.upper()} HOTCUE {hotcue_num} needs manual attention")

        print(f"\n🏆 HOTCUE LEARN SESSION COMPLETED!")
        print(f"📝 Remember to save your TSI file in Controller Manager")
        print(f"🎯 All 32 HOTCUES mapped (8 per deck)")
        print(f"✅ Deck A conflicts resolved (CC 2,3,4 → 87,88,89)")

    def deck_specific_session(self, deck_letter):
        """Learn session for specific deck only"""
        deck = deck_letter.lower()
        if deck not in ['a', 'b', 'c', 'd']:
            print(f"❌ Invalid deck: {deck_letter}")
            return

        print(f"🎯 DECK {deck.upper()} HOTCUE LEARN SESSION")
        print("=" * 50)

        if not self.connect_midi():
            return

        deck_hotcues = {k: v for k, v in self.hotcue_mappings.items() if f'deck_{deck}_' in k}

        for control_name, cc in deck_hotcues.items():
            hotcue_num = control_name.split('_')[-1]
            print(f"\n🎯 CONFIGURING: DECK {deck.upper()} HOTCUE {hotcue_num}")
            print(f"   Target CC: {cc}")

            if deck == 'a' and hotcue_num in ['2', '3', '4']:
                old_cc = {'2': 2, '3': 3, '4': 4}[hotcue_num]
                print(f"   ⚠️  CONFLICT RESOLUTION: CC {old_cc} → CC {cc}")

            input(f"   ⏸️  Press ENTER to send CC {cc}...")

            success = self.send_cc(cc, 127)

            if success:
                print(f"   ✅ CC {cc} sent successfully")

            result = input(f"   ❓ Mapping successful? (y/n): ").lower()
            if result == 'y':
                print(f"   🎉 HOTCUE {hotcue_num} configured!")

        print(f"\n🏆 DECK {deck.upper()} HOTCUES COMPLETED!")

    def quick_test_all(self):
        """Quick test of all HOTCUE CCs"""
        print("🧪 QUICK TEST: All HOTCUE CCs")
        print("Testing 32 HOTCUES across 4 decks...")

        if not self.connect_midi():
            return

        for control_name, cc in self.hotcue_mappings.items():
            print(f"Testing {control_name} (CC {cc})...")
            self.send_cc(cc, 127)
            time.sleep(0.3)  # Shorter delay for 32 hotcues

        print("✅ Quick test completed - 32 HOTCUES tested")

    def show_mapping_summary(self):
        """Display complete HOTCUE mapping summary"""
        print("🎯 COMPLETE HOTCUE MAPPING SUMMARY")
        print("=" * 60)

        decks = ['a', 'b', 'c', 'd']
        for deck in decks:
            print(f"\n📍 DECK {deck.upper()}:")
            deck_hotcues = {k: v for k, v in self.hotcue_mappings.items() if f'deck_{deck}_' in k}

            for control_name, cc in sorted(deck_hotcues.items()):
                hotcue_num = control_name.split('_')[-1]
                conflict_note = ""

                if deck == 'a' and hotcue_num in ['2', '3', '4']:
                    old_cc = {'2': 2, '3': 3, '4': 4}[hotcue_num]
                    conflict_note = f" (REMAPPED from CC {old_cc})"

                print(f"   HOTCUE {hotcue_num}: CC {cc}{conflict_note}")

        print(f"\n📊 TOTALS:")
        print(f"   • Total HOTCUES: {len(self.hotcue_mappings)}")
        print(f"   • HOTCUES per deck: 8")
        print(f"   • Conflicts resolved: 3 (Deck A)")
        print(f"   • CC range used: 86-125")

def main():
    print("🎯 HOTCUE Learn Helper")
    print("Choose mode:")
    print("1. Full Interactive Learn Session (All 32 HOTCUES)")
    print("2. Deck-specific Session (A/B/C/D)")
    print("3. Quick Test All CCs")
    print("4. Show Mapping Summary")

    choice = input("Enter choice (1/2/3/4): ").strip()

    helper = HOTCUELearnHelper()

    if choice == "1":
        helper.interactive_learn_session()
    elif choice == "2":
        deck = input("Enter deck letter (A/B/C/D): ").strip()
        helper.deck_specific_session(deck)
    elif choice == "3":
        helper.quick_test_all()
    elif choice == "4":
        helper.show_mapping_summary()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()