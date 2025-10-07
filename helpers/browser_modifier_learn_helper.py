#!/usr/bin/env python3
"""
🗂️ Browser Modifier Learn Helper - Conditional Navigation Setup for Traktor
Guides setup of Modifier Conditions for bidirectional browser navigation
"""

import time
import rtmidi

class BrowserModifierLearnHelper:
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.out_ports = self.midiout.get_ports()
        self.iac_port = None

        # Browser navigation CC mappings - DISCOVERED CONFIGURATION (2025-10-06)
        self.browser_mappings = {
            'modifier_toggle': 56,     # Toggle button for M1 (0↔1) - USER VERIFIED CC56 FREE
            'tree_navigation_down': 72, # Browser tree DOWN (Button/INC with M1=0)
            'tree_navigation_up': 73,   # Browser tree UP (Button/DEC with M1=0)
            'list_navigation_up': 92,  # List UP (keeping existing)
            'list_navigation_down': 74, # List DOWN (keeping existing)
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

    def send_cc(self, cc, value=64):
        """Send MIDI CC on channel 1"""
        try:
            message = [0xB0, cc, value]  # Channel 1, CC, Value
            self.midiout.send_message(message)
            print(f"📤 Sent: CC {cc} = {value}")
            return True
        except Exception as e:
            print(f"❌ MIDI error: {e}")
            return False

    def interactive_modifier_session(self):
        """Interactive setup session for Browser Modifier Conditions"""
        print("🗂️ BROWSER MODIFIER LEARN HELPER - Interactive Session")
        print("=" * 60)
        print("📋 SETUP OVERVIEW:")
        print("   🎯 Goal: Bidirectional browser navigation using Modifier Conditions")
        print("   📝 M1 = 0 → Tree Navigation UP")
        print("   📝 M1 = 1 → Tree Navigation DOWN")
        print("   🔄 Toggle button switches M1 between 0/1")
        print("=" * 60)
        print("📋 REQUIREMENTS:")
        print("1. Open Traktor Pro 3 → Preferences → Controller Manager")
        print("2. Select your mapping (or create new 'Generic MIDI')")
        print("3. Follow the step-by-step configuration below")
        print("=" * 60)

        if not self.connect_midi():
            return

        # STEP 1: Configure Modifier Toggle
        self.configure_modifier_toggle()

        # STEP 2: Configure Conditional Tree Navigation UP
        self.configure_conditional_navigation_up()

        # STEP 3: Configure Conditional Tree Navigation DOWN
        self.configure_conditional_navigation_down()

        # STEP 4: Test the complete system
        self.test_modifier_system()

        print(f"\n🏆 BROWSER MODIFIER SYSTEM CONFIGURED!")
        print(f"📝 Remember to save your TSI file in Controller Manager")
        print(f"🎯 Test: Press toggle → Navigate UP/DOWN → Press toggle → Navigate UP/DOWN")

    def configure_modifier_toggle(self):
        """Configure the Modifier M1 toggle button"""
        print(f"\n" + "="*50)
        print(f"🔄 STEP 1: CONFIGURE MODIFIER M1 TOGGLE")
        print(f"="*50)
        print(f"📝 Controller Manager Instructions:")
        print(f"   1. Click 'Add In...'")
        print(f"   2. Select 'Modifier' → 'Modifier #1'")
        print(f"   3. Set 'Type of Controller' = 'Button'")
        print(f"   4. Set 'Interaction Mode' = 'Toggle'")
        print(f"   5. Set 'Set to Value' = '1'")
        print(f"   6. Click 'Learn' button")

        cc = self.browser_mappings['modifier_toggle']
        input(f"   ⏸️  Press ENTER when ready to send CC {cc} for MODIFIER TOGGLE...")

        success = self.send_cc(cc, 127)  # Button press

        if success:
            print(f"   ✅ CC {cc} sent for Modifier M1 Toggle")
            print(f"   📝 Verify in Controller Manager:")
            print(f"      - Assignment shows 'Modifier #1'")
            print(f"      - Type: Button, Mode: Toggle, Value: 1")
            print(f"   📊 Check Modifier State table: M1 should toggle 0↔1")

        result = input(f"   ❓ Modifier M1 toggle configured successfully? (y/n): ").lower()
        if result == 'y':
            print(f"   🎉 Modifier M1 toggle ready!")
        else:
            print(f"   ⚠️  Manual configuration needed for Modifier M1")

    def configure_conditional_navigation_up(self):
        """Configure CC72 with M1=0 condition for UP navigation"""
        print(f"\n" + "="*50)
        print(f"⬆️  STEP 2: CONFIGURE CONDITIONAL NAVIGATION UP")
        print(f"="*50)
        print(f"📝 Controller Manager Instructions:")
        print(f"   1. Click 'Add In...'")
        print(f"   2. Navigate: Browser → Tree → Select Previous")
        print(f"   3. Set 'Type of Controller' = 'Button'")
        print(f"   4. Set 'Interaction Mode' = 'Inc'")
        print(f"   5. Click 'Learn' button")
        print(f"   6. IMPORTANT: Set Modifier Conditions:")
        print(f"      • First Modifier dropdown = 'M1'")
        print(f"      • First Value dropdown = '0'")

        cc = self.browser_mappings['tree_navigation']
        input(f"   ⏸️  Press ENTER to send CC {cc} for TREE UP (M1=0)...")

        success = self.send_cc(cc, 127)  # Button value

        if success:
            print(f"   ✅ CC {cc} sent for Browser Tree UP")
            print(f"   📝 CRITICAL: Set Modifier Condition M1 = 0")
            print(f"   🔍 Verify: Assignment = 'Browser → Tree → Select Previous'")
            print(f"   🔍 Verify: Modifier Conditions shows 'M1 = 0'")

        result = input(f"   ❓ Tree UP with M1=0 condition configured? (y/n): ").lower()
        if result == 'y':
            print(f"   🎉 Conditional Tree UP ready!")
        else:
            print(f"   ⚠️  Manual configuration needed for Tree UP condition")

    def configure_conditional_navigation_down(self):
        """Configure CC72 with M1=1 condition for DOWN navigation"""
        print(f"\n" + "="*50)
        print(f"⬇️  STEP 3: CONFIGURE CONDITIONAL NAVIGATION DOWN")
        print(f"="*50)
        print(f"📝 Controller Manager Instructions:")
        print(f"   1. Click 'Add In...' again")
        print(f"   2. Navigate: Browser → Tree → Select Next")
        print(f"   3. Set 'Type of Controller' = 'Button'")
        print(f"   4. Set 'Interaction Mode' = 'Inc'")
        print(f"   5. Click 'Learn' button (SAME CC as previous!)")
        print(f"   6. IMPORTANT: Set Modifier Conditions:")
        print(f"      • First Modifier dropdown = 'M1'")
        print(f"      • First Value dropdown = '1'")

        cc = self.browser_mappings['tree_navigation']
        input(f"   ⏸️  Press ENTER to send CC {cc} for TREE DOWN (M1=1)...")

        success = self.send_cc(cc, 127)  # Button value

        if success:
            print(f"   ✅ CC {cc} sent for Browser Tree DOWN")
            print(f"   📝 CRITICAL: Set Modifier Condition M1 = 1")
            print(f"   🔍 Verify: Assignment = 'Browser → Tree → Select Next'")
            print(f"   🔍 Verify: Modifier Conditions shows 'M1 = 1'")
            print(f"   🔍 Notice: SAME CC {cc} but DIFFERENT condition!")

        result = input(f"   ❓ Tree DOWN with M1=1 condition configured? (y/n): ").lower()
        if result == 'y':
            print(f"   🎉 Conditional Tree DOWN ready!")
        else:
            print(f"   ⚠️  Manual configuration needed for Tree DOWN condition")

    def test_modifier_system(self):
        """Test the complete modifier system"""
        print(f"\n" + "="*50)
        print(f"🧪 STEP 4: SYSTEM TEST")
        print(f"="*50)
        print(f"📋 Test Sequence:")
        print(f"   1. Toggle M1 → Navigate → Toggle M1 → Navigate")
        print(f"   2. Observe different directions based on M1 state")

        input(f"   ⏸️  Position yourself on a folder (e.g., 'Chill'), then press ENTER...")

        # Test sequence
        tests = [
            ("M1 Toggle (SET to 0)", 'modifier_toggle', 127),
            ("Tree Navigation (should go UP)", 'tree_navigation', 127),
            ("M1 Toggle (SET to 1)", 'modifier_toggle', 127),
            ("Tree Navigation (should go DOWN)", 'tree_navigation', 127),
        ]

        for description, control, value in tests:
            cc = self.browser_mappings[control]
            print(f"\n🧪 Testing: {description}")
            input(f"   ⏸️  Press ENTER to send {description}...")

            success = self.send_cc(cc, value)
            if success:
                print(f"   ✅ Sent CC {cc} = {value}")
                result = input(f"   ❓ Expected behavior observed? (y/n): ").lower()
                if result != 'y':
                    print(f"   ⚠️  Issue detected with {description}")
            else:
                print(f"   ❌ Failed to send {description}")

    def get_current_mappings_summary(self):
        """Display current mappings summary"""
        print(f"\n📊 CURRENT BROWSER MODIFIER MAPPINGS:")
        print(f"-" * 40)
        for control, cc in self.browser_mappings.items():
            print(f"   {control:20}: CC {cc}")
        print(f"-" * 40)

def main():
    print("🗂️ Browser Modifier Learn Helper")
    print("Choose mode:")
    print("1. Interactive Modifier Setup Session")
    print("2. Show Current Mappings")

    choice = input("Enter choice (1/2): ").strip()

    helper = BrowserModifierLearnHelper()

    if choice == "1":
        helper.interactive_modifier_session()
    elif choice == "2":
        helper.get_current_mappings_summary()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()