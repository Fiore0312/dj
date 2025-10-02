#!/usr/bin/env python3
"""
Decode DCDT sections to extract CC → Command mappings
"""

import xml.etree.ElementTree as ET
import base64
import sys
import struct
from collections import defaultdict

def parse_dcdt_section(data, offset):
    """
    Parse a single DCDT section
    Returns: (cc_number, channel, command_name, value_type)
    """

    # DCDT structure (estimated):
    # 4 bytes: 'DCDT' marker
    # 4 bytes: section length
    # Variable: control data

    if data[offset:offset+4] != b'DCDT':
        return None

    # Read section length (likely big-endian 32-bit int)
    section_len = struct.unpack('>I', data[offset+4:offset+8])[0]

    section_data = data[offset+8:offset+8+section_len]

    result = {
        'offset': offset,
        'length': section_len,
        'channel': None,
        'cc': None,
        'note': None,
        'command': None,
        'raw_hex': section_data[:64].hex()  # First 64 bytes for debug
    }

    # Try to extract control type and number
    # Look for patterns in first bytes

    # Many MIDI implementations store:
    # - Message type (Note/CC/PitchBend)
    # - Channel (0-15)
    # - CC/Note number (0-127)

    # Try different offsets where this data might be
    for test_offset in [0, 4, 8, 12, 16, 20]:
        if test_offset + 4 > len(section_data):
            continue

        # Try to read as sequence of bytes
        bytes_at_offset = section_data[test_offset:test_offset+8]

        # Look for channel numbers (typically 0-5 for our case)
        for i, b in enumerate(bytes_at_offset):
            if 0 <= b <= 15:  # MIDI channel range
                result[f'possible_channel_{i}'] = b

        # Look for CC numbers (0-127)
        for i, b in enumerate(bytes_at_offset):
            if 0 <= b <= 127:
                result[f'possible_cc_{i}'] = b

    # Try to find text strings (command names)
    # Look for ASCII sequences
    text_parts = []
    current_text = bytearray()

    for byte in section_data:
        if 32 <= byte <= 126:  # Printable ASCII
            current_text.append(byte)
        else:
            if len(current_text) >= 3:
                text_parts.append(current_text.decode('ascii'))
            current_text = bytearray()

    if text_parts:
        result['text_found'] = ' | '.join(text_parts[:5])

    return result

def analyze_all_dcdt_sections(data):
    """Find and parse all DCDT sections"""

    print(f"\n{'='*70}")
    print("🔍 PARSING ALL DCDT SECTIONS")
    print(f"{'='*70}\n")

    sections = []
    offset = 0

    while True:
        pos = data.find(b'DCDT', offset)
        if pos == -1:
            break

        section = parse_dcdt_section(data, pos)
        if section:
            sections.append(section)

        offset = pos + 4

    print(f"✅ Found {len(sections)} DCDT sections\n")

    # Analyze first 50 sections in detail
    print("="*70)
    print("FIRST 50 SECTIONS (Detailed)")
    print("="*70)

    for i, sec in enumerate(sections[:50]):
        print(f"\nSection {i+1}:")
        print(f"  Offset: {sec['offset']}")
        print(f"  Length: {sec['length']} bytes")
        print(f"  Hex (first 64 bytes): {sec['raw_hex']}")

        # Show possible CC/channel values
        possible_ccs = [v for k, v in sec.items() if k.startswith('possible_cc_')]
        possible_channels = [v for k, v in sec.items() if k.startswith('possible_channel_')]

        if possible_ccs:
            print(f"  Possible CC values: {sorted(set(possible_ccs))}")
        if possible_channels:
            print(f"  Possible channels: {sorted(set(possible_channels))}")

        if 'text_found' in sec:
            print(f"  Text: {sec['text_found']}")

    # Look for patterns
    print(f"\n{'='*70}")
    print("PATTERN ANALYSIS")
    print(f"{'='*70}\n")

    # Group by section length
    lengths = defaultdict(int)
    for sec in sections:
        lengths[sec['length']] += 1

    print("Section lengths distribution:")
    for length, count in sorted(lengths.items()):
        print(f"  Length {length:4d} bytes: {count:4d} sections")

    # Look for incrementing CC patterns
    # If CC numbers are stored at consistent offset, we should see 0,1,2,3...
    print(f"\n{'='*70}")
    print("CHECKING FOR CC NUMBER SEQUENCES")
    print(f"{'='*70}\n")

    # Check each possible CC position
    for cc_field in [f'possible_cc_{i}' for i in range(8)]:
        values = [sec.get(cc_field) for sec in sections[:128] if sec.get(cc_field) is not None]

        if len(values) >= 10:
            # Check if it's sequential (0, 1, 2, 3...)
            is_sequential = all(values[i] == i for i in range(min(len(values), 128)))

            if is_sequential:
                print(f"✅ FOUND SEQUENTIAL CC PATTERN at {cc_field}!")
                print(f"   Values: {values[:20]}...")

                # This is likely the CC number position!
                # Now extract all mappings
                print(f"\n{'='*70}")
                print(f"EXTRACTING ALL CC MAPPINGS")
                print(f"{'='*70}\n")

                mappings = []
                for sec in sections:
                    cc_num = sec.get(cc_field)
                    text = sec.get('text_found', '')
                    if cc_num is not None:
                        mappings.append((cc_num, text, sec['raw_hex']))

                # Sort by CC number
                mappings.sort(key=lambda x: x[0])

                # Display all
                print("CC → Command mappings:\n")
                for cc, text, hex_data in mappings[:128]:
                    print(f"  CC {cc:3d}: {text if text else '(no text found)'}")

                # Save to file
                with open('cc_mappings_decoded.txt', 'w') as f:
                    f.write("TRAKTOR GENERIC MIDI CC MAPPINGS (Decoded)\n")
                    f.write("="*70 + "\n\n")

                    for cc, text, hex_data in mappings:
                        f.write(f"CC {cc:3d}: {text if text else '(unknown)'}\n")
                        f.write(f"  Hex: {hex_data}\n\n")

                print(f"\n💾 Saved to cc_mappings_decoded.txt")

                return mappings

    print("\n⚠️  Could not find sequential CC pattern")
    print("   Showing raw data for manual analysis...")

    return sections

def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "generic_midi_mapping.tsi"

    print(f"{'='*70}")
    print(f"📋 DECODING TSI FILE: {filename}")
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

    analyze_all_dcdt_sections(binary_data)

if __name__ == "__main__":
    main()
