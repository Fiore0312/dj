#!/usr/bin/env python3
"""
Extract Traktor CC mappings from TSI file (UTF-16 decoded)
"""

import xml.etree.ElementTree as ET
import base64
import struct
import re
from collections import defaultdict

def decode_utf16_string(hex_bytes):
    """Decode UTF-16BE string from bytes"""
    try:
        # UTF-16BE: every character is 2 bytes (big-endian)
        # Traktor uses BIG endian!
        text = hex_bytes.decode('utf-16be').rstrip('\x00')
        # Remove any non-printable chars except spaces
        text = ''.join(c for c in text if c.isprintable() or c == ' ')
        return text if len(text) > 2 else None
    except:
        return None

def parse_dcdt_section(data, offset):
    """
    Parse DCDT section and extract:
    - Control identifier (Ch X.CC.YYY or Ch X.Note.YYY)
    - Assignment type
    - Traktor command
    """

    if data[offset:offset+4] != b'DCDT':
        return None

    # Section length
    section_len = struct.unpack('>I', data[offset+4:offset+8])[0]
    section_data = data[offset+8:offset+8+section_len]

    result = {}

    # First few bytes contain the control identifier in UTF-16LE
    # Pattern: "Ch XX.CC.YYY" or "Ch XX.Note.YYY"

    # Try to decode first part (up to 100 bytes should be enough)
    control_id = decode_utf16_string(section_data[:100])

    if control_id:
        result['control_id'] = control_id

        # Parse control type
        # Examples: "Ch 01.CC.000", "Ch 02.Note.036", "Ch 01.PitchBend"

        # Extract channel
        ch_match = re.search(r'Ch (\d+)', control_id)
        if ch_match:
            result['channel'] = int(ch_match.group(1))

        # Extract CC number
        cc_match = re.search(r'CC\.(\d+)', control_id)
        if cc_match:
            result['type'] = 'CC'
            result['number'] = int(cc_match.group(1))

        # Extract Note number
        note_match = re.search(r'Note\.(\d+)', control_id)
        if note_match:
            result['type'] = 'Note'
            result['number'] = int(note_match.group(1))

        # Check for PitchBend
        if 'PitchBend' in control_id:
            result['type'] = 'PitchBend'

    # Try to find assignment type and command name
    # These are further in the section, also UTF-16LE

    # Scan for other UTF-16 strings in the section
    # Skip first 100 bytes (control ID), scan rest
    for i in range(100, len(section_data), 2):
        # Try to decode chunk
        chunk = section_data[i:min(i+200, len(section_data))]
        text = decode_utf16_string(chunk)

        if text and len(text) > 3 and text.isprintable():
            # Look for Traktor command keywords
            keywords = ['deck', 'play', 'cue', 'sync', 'loop', 'volume',
                       'eq', 'filter', 'master', 'hotcue', 'load', 'browse',
                       'fx', 'effect', 'tempo', 'beatjump', 'crossfader',
                       'mixer', 'monitor', 'sample', 'remix']

            text_lower = text.lower()
            for keyword in keywords:
                if keyword in text_lower:
                    if 'command' not in result:
                        result['command'] = text
                    break

    return result

def extract_all_mappings(data):
    """Extract all CC mappings from TSI binary data"""

    print(f"\n{'='*70}")
    print("🎛️  EXTRACTING ALL TRAKTOR MIDI MAPPINGS")
    print(f"{'='*70}\n")

    mappings = []
    offset = 0

    while True:
        pos = data.find(b'DCDT', offset)
        if pos == -1:
            break

        mapping = parse_dcdt_section(data, pos)
        if mapping and mapping.get('control_id'):
            mappings.append(mapping)

        offset = pos + 4

    print(f"✅ Found {len(mappings)} control mappings\n")

    # Group by type
    by_type = defaultdict(list)
    for m in mappings:
        ctrl_type = m.get('type', 'Unknown')
        by_type[ctrl_type].append(m)

    print("Distribution:")
    for ctrl_type, items in sorted(by_type.items()):
        print(f"  {ctrl_type}: {len(items)} mappings")

    # Sort mappings by channel and number
    cc_mappings = sorted(
        [m for m in mappings if m.get('type') == 'CC'],
        key=lambda x: (x.get('channel', 0), x.get('number', 0))
    )

    print(f"\n{'='*70}")
    print(f"CC CONTROL MAPPINGS (Total: {len(cc_mappings)})")
    print(f"{'='*70}\n")

    # Group by channel
    by_channel = defaultdict(list)
    for m in cc_mappings:
        ch = m.get('channel', 0)
        by_channel[ch].append(m)

    for channel in sorted(by_channel.keys()):
        mappings_ch = by_channel[channel]
        print(f"\n📡 CHANNEL {channel} ({len(mappings_ch)} CC mappings)")
        print("─" * 70)

        for m in mappings_ch[:20]:  # First 20 per channel
            cc_num = m.get('number', '?')
            cmd = m.get('command', '(no command found)')
            ctrl_id = m.get('control_id', '')

            print(f"  CC {cc_num:3d}: {cmd}")
            if len(ctrl_id) < 50:
                print(f"         ID: {ctrl_id}")

        if len(mappings_ch) > 20:
            print(f"  ... and {len(mappings_ch) - 20} more")

    # Save complete mapping to file
    output_file = "traktor_cc_mappings_complete.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("TRAKTOR PRO 3 - GENERIC MIDI MAPPINGS\n")
        f.write("="*70 + "\n")
        f.write(f"Extracted from: generic_midi_mapping.tsi\n")
        f.write(f"Total mappings: {len(mappings)}\n")
        f.write("="*70 + "\n\n")

        for channel in sorted(by_channel.keys()):
            f.write(f"\n{'='*70}\n")
            f.write(f"CHANNEL {channel}\n")
            f.write(f"{'='*70}\n\n")

            for m in by_channel[channel]:
                cc_num = m.get('number', '?')
                cmd = m.get('command', '(unmapped)')
                ctrl_id = m.get('control_id', '')

                f.write(f"CC {cc_num:3d}: {cmd}\n")
                f.write(f"  Control ID: {ctrl_id}\n")

                # Include all metadata
                for key, value in m.items():
                    if key not in ['number', 'command', 'control_id', 'type', 'channel']:
                        f.write(f"  {key}: {value}\n")

                f.write("\n")

    print(f"\n{'='*70}")
    print(f"💾 Complete mappings saved to: {output_file}")
    print(f"{'='*70}\n")

    # Also create a concise Python-friendly mapping
    python_output = "traktor_cc_mapping.py"
    with open(python_output, 'w', encoding='utf-8') as f:
        f.write('"""\nTraktor Generic MIDI CC Mappings\n')
        f.write('Auto-extracted from generic_midi_mapping.tsi\n"""\n\n')

        for channel in sorted(by_channel.keys()):
            f.write(f"\n# CHANNEL {channel}\n")
            f.write(f"CHANNEL_{channel}_CC_MAP = {{\n")

            for m in by_channel[channel]:
                cc_num = m.get('number', '?')
                cmd = m.get('command', 'unmapped')

                # Clean command name for Python
                cmd_clean = cmd.replace('"', '\\"')

                f.write(f'    {cc_num}: "{cmd_clean}",\n')

            f.write("}\n")

    print(f"💾 Python mapping saved to: {python_output}\n")

    return mappings

def main():
    import sys

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

    extract_all_mappings(binary_data)

if __name__ == "__main__":
    main()
