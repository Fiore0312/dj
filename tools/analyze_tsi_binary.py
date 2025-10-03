#!/usr/bin/env python3
"""
Deep binary analysis of Traktor TSI format
"""

import xml.etree.ElementTree as ET
import base64
import sys
import struct

def analyze_binary_structure(data):
    """Analyze TSI binary structure markers"""

    print(f"\n{'='*70}")
    print("🔬 BINARY STRUCTURE ANALYSIS")
    print(f"{'='*70}\n")
    print(f"Total size: {len(data)} bytes\n")

    # TSI format markers (4-byte signatures)
    markers = [
        b'DIOM',  # Device Input/Output Mappings
        b'DIOS',  # Device Input/Output Settings
        b'DEVS',  # Devices
        b'DEVI',  # Device Info
        b'DDAT',  # Device Data
        b'DDIF',  # Device Definition
        b'DDIV',  # Device Version
        b'DDIC',  # Device Config
        b'DDPT',  # Device Port
        b'DDDC',  # Device Data Config
        b'DDCI',  # Device Config Info
        b'DCDT',  # Device Control Data
        b'DCDI',  # Device Control Definition
        b'DCCO',  # Device Control Config
        b'DCCM',  # Device Control Command
    ]

    marker_positions = {}
    for marker in markers:
        positions = []
        offset = 0
        while True:
            pos = data.find(marker, offset)
            if pos == -1:
                break
            positions.append(pos)
            offset = pos + 1
        if positions:
            marker_positions[marker.decode('ascii')] = positions

    print("📍 Found markers:\n")
    for marker, positions in sorted(marker_positions.items()):
        print(f"  {marker}: {len(positions)} occurrences")
        if len(positions) <= 5:
            print(f"    at: {positions}")

    # Analyze DCDT sections (Device Control Data)
    if b'DCDT' in data:
        print(f"\n{'='*70}")
        print("🎛️  ANALYZING DCDT (Control Data) SECTIONS")
        print(f"{'='*70}\n")

        dcdt_positions = marker_positions.get('DCDT', [])

        for i, pos in enumerate(dcdt_positions[:10]):  # First 10 sections
            print(f"\n--- DCDT Section {i+1} at position {pos} ---")

            # Extract section (up to next marker or 2000 bytes)
            end_pos = pos + 2000
            for next_marker in markers:
                next_pos = data.find(next_marker, pos + 4)
                if next_pos != -1 and next_pos < end_pos:
                    end_pos = next_pos

            section = data[pos:end_pos]

            # Try to find readable text
            # Method 1: Look for ASCII-printable sequences
            text_sequences = []
            current_seq = bytearray()

            for byte in section[4:]:  # Skip DCDT marker
                if 32 <= byte <= 126:  # Printable ASCII
                    current_seq.append(byte)
                else:
                    if len(current_seq) >= 4:
                        text_sequences.append(current_seq.decode('ascii'))
                    current_seq = bytearray()

            if text_sequences:
                print(f"  ASCII text found: {text_sequences[:3]}")

            # Method 2: Look for "Ch X.CC.YY" pattern in raw bytes
            section_str = section.decode('latin1')  # Use latin1 to preserve bytes
            if 'CC.' in section_str or 'Ch ' in section_str:
                # Extract the pattern
                import re
                patterns = re.findall(r'Ch \d+\.CC\.\d+', section_str)
                if patterns:
                    print(f"  ✅ Found CC pattern: {patterns[0]}")

                # Try to find associated command
                # Usually follows within 50-200 bytes
                snippet = section_str[:500]
                # Look for Traktor keywords
                keywords = ['deck', 'play', 'cue', 'sync', 'loop', 'volume',
                           'eq', 'filter', 'master', 'hotcue', 'load', 'browse']

                found_keywords = []
                for keyword in keywords:
                    if keyword in snippet.lower():
                        # Extract context
                        idx = snippet.lower().index(keyword)
                        context = snippet[max(0, idx-10):idx+30]
                        found_keywords.append(context)

                if found_keywords:
                    print(f"  Keywords nearby: {found_keywords[:2]}")

    # Try another approach: look for repeating structure
    print(f"\n{'='*70}")
    print("🔍 SEARCHING FOR CC NUMBER PATTERNS")
    print(f"{'='*70}\n")

    # CC numbers are usually stored as binary values
    # Look for sequences like: 0x00, 0x01, 0x02... (CC 0, 1, 2...)

    cc_candidates = []
    for i in range(len(data) - 1):
        # Look for byte sequences that could be CC numbers (0-127)
        if data[i] <= 127:
            # Check if there's a pattern around it
            context_before = data[max(0, i-20):i]
            context_after = data[i:min(len(data), i+20)]

            # Look for "CC" or channel markers nearby
            combined = context_before + context_after
            if b'CC' in combined or b'Ch' in combined:
                cc_candidates.append((i, data[i], combined))

    if cc_candidates:
        print(f"Found {len(cc_candidates)} potential CC number locations\n")
        print("First 20 candidates:")
        for pos, cc_val, context in cc_candidates[:20]:
            # Show context as hex
            hex_context = ' '.join(f'{b:02x}' for b in context[-10:])
            print(f"  Position {pos}: CC={cc_val:3d}  context: ...{hex_context}")

def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "generic_midi_mapping.tsi"

    print(f"{'='*70}")
    print(f"📋 LOADING TSI FILE: {filename}")
    print(f"{'='*70}")

    tree = ET.parse(filename)
    root = tree.getroot()

    entries = {}
    for entry in root.iter('Entry'):
        name = entry.get('Name', '')
        value = entry.get('Value', '')
        if name:
            entries[name] = value

    if 'DeviceIO.Config.Controller' not in entries:
        print("❌ No controller configuration found!")
        return

    controller_b64 = entries['DeviceIO.Config.Controller']
    binary_data = base64.b64decode(controller_b64)

    analyze_binary_structure(binary_data)

    # Save first 10KB for manual inspection
    with open('tsi_binary_sample.bin', 'wb') as f:
        f.write(binary_data[:10240])

    print(f"\n{'='*70}")
    print("💾 Saved first 10KB to: tsi_binary_sample.bin")
    print("   (can be inspected with hex editor)")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
