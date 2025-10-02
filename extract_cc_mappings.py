#!/usr/bin/env python3
"""
Extract CC mappings from Traktor Generic MIDI TSI file
Decodes Base64 data and parses binary structure
"""

import xml.etree.ElementTree as ET
import base64
import struct
import sys
from collections import defaultdict

def decode_utf16_strings(data):
    """Extract UTF-16LE strings from binary data"""
    strings = []
    i = 0
    while i < len(data) - 1:
        # Look for UTF-16LE string patterns (even bytes are ASCII, odd bytes are 0x00)
        if data[i] != 0 and data[i+1] == 0:
            # Found potential UTF-16LE string start
            string_bytes = bytearray()
            j = i
            while j < len(data) - 1:
                if data[j] == 0 and data[j+1] == 0:
                    # Double null = end of string
                    break
                string_bytes.append(data[j])
                string_bytes.append(data[j+1])
                j += 2

            if len(string_bytes) > 4:  # At least 2 chars
                try:
                    text = string_bytes.decode('utf-16le').strip('\x00')
                    if len(text) > 2 and text.isprintable():
                        strings.append((i, text))
                except:
                    pass
            i = j + 2
        else:
            i += 1

    return strings

def find_cc_mappings(data):
    """Find CC to command mappings in binary data"""
    mappings = defaultdict(list)

    # Look for CC patterns: "Ch X.CC.YYY"
    import re

    # First, extract all strings
    strings = decode_utf16_strings(data)

    print(f"\n🔍 Found {len(strings)} readable strings in TSI data\n")

    # Group by pattern type
    cc_entries = []
    command_entries = []

    for pos, text in strings:
        if 'CC.' in text or 'Ch ' in text:
            cc_entries.append((pos, text))
        elif any(keyword in text.lower() for keyword in
                ['deck', 'play', 'cue', 'sync', 'loop', 'eq', 'volume',
                 'filter', 'load', 'hotcue', 'beatjump', 'master']):
            command_entries.append((pos, text))

    print(f"📋 CC/Channel entries: {len(cc_entries)}")
    print(f"🎛️  Command entries: {len(command_entries)}\n")

    # Show first 30 CC entries
    print("="*70)
    print("CC/CHANNEL PATTERNS")
    print("="*70)
    for pos, text in cc_entries[:30]:
        print(f"  Position {pos:6d}: {text}")

    # Show command entries
    print(f"\n{'='*70}")
    print("COMMAND PATTERNS")
    print("="*70)
    for pos, text in command_entries[:40]:
        print(f"  Position {pos:6d}: {text}")

    # Try to correlate CC numbers with commands
    # Commands usually appear shortly after CC definitions
    print(f"\n{'='*70}")
    print("CC → COMMAND CORRELATIONS (within 500 bytes)")
    print("="*70)

    correlations = []
    for cc_pos, cc_text in cc_entries:
        # Look for commands within next 500 bytes
        nearby_commands = []
        for cmd_pos, cmd_text in command_entries:
            if 0 < cmd_pos - cc_pos < 500:
                nearby_commands.append((cmd_pos - cc_pos, cmd_text))

        if nearby_commands:
            # Get closest command
            closest = min(nearby_commands, key=lambda x: x[0])
            correlations.append((cc_text, closest[1], closest[0]))

    # Sort by CC number
    def extract_cc_num(cc_text):
        match = re.search(r'CC\.(\d+)', cc_text)
        if match:
            return int(match.group(1))
        return 999

    correlations.sort(key=lambda x: extract_cc_num(x[0]))

    for cc_text, cmd_text, distance in correlations[:50]:
        print(f"\n  {cc_text}")
        print(f"    → {cmd_text} (offset: {distance} bytes)")

    return correlations

def parse_tsi_file(filename):
    """Parse TSI XML and extract controller data"""

    print(f"\n{'='*70}")
    print(f"📋 ANALYZING TSI FILE: {filename}")
    print(f"{'='*70}\n")

    tree = ET.parse(filename)
    root = tree.getroot()

    # Extract all entries
    entries = {}
    for entry in root.iter('Entry'):
        name = entry.get('Name', '')
        value = entry.get('Value', '')
        if name:
            entries[name] = value

    print(f"📊 Total entries found: {len(entries)}\n")

    # Find controller configuration
    if 'DeviceIO.Config.Controller' not in entries:
        print("❌ No controller configuration found!")
        return None

    # Decode Base64 controller data
    controller_b64 = entries['DeviceIO.Config.Controller']
    print(f"✅ Found controller data (Base64 length: {len(controller_b64)})")

    try:
        controller_binary = base64.b64decode(controller_b64)
        print(f"✅ Decoded to {len(controller_binary)} bytes\n")
        return controller_binary
    except Exception as e:
        print(f"❌ Failed to decode: {e}")
        return None

def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "generic_midi_mapping.tsi"

    # Parse TSI file
    binary_data = parse_tsi_file(filename)

    if binary_data:
        # Find CC mappings
        correlations = find_cc_mappings(binary_data)

        # Save results
        output_file = "cc_mappings_extracted.txt"
        with open(output_file, 'w') as f:
            f.write("TRAKTOR GENERIC MIDI CC MAPPINGS\n")
            f.write("="*70 + "\n\n")

            for cc_text, cmd_text, distance in correlations:
                f.write(f"{cc_text}\n")
                f.write(f"  → {cmd_text}\n")
                f.write(f"  (correlation distance: {distance} bytes)\n\n")

        print(f"\n{'='*70}")
        print(f"💾 Results saved to: {output_file}")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
