#!/usr/bin/env python3
"""
Extract available CC numbers per channel from Generic MIDI TSI
"""

import base64
import xml.etree.ElementTree as ET
import struct
import re
from collections import defaultdict

def main():
    tree = ET.parse('generic_midi_mapping.tsi')
    root = tree.getroot()
    entries = {e.get('Name'): e.get('Value') for e in root.iter('Entry')}
    data = base64.b64decode(entries['DeviceIO.Config.Controller'])

    print("\n" + "="*70)
    print("ANALYZING GENERIC MIDI DEVICE CONFIGURATION")
    print("="*70 + "\n")

    # Find all DCDT sections
    cc_by_channel = defaultdict(set)
    note_by_channel = defaultdict(set)
    pitchbend_channels = set()

    offset = 0
    while True:
        pos = data.find(b'DCDT', offset)
        if pos == -1:
            break

        # Read section
        section_len = struct.unpack('>I', data[pos+4:pos+8])[0]
        section = data[pos+8:pos+8+section_len]

        # Decode control ID (UTF-16BE)
        try:
            # First 4 bytes = string length, then UTF-16BE string
            str_len = struct.unpack('>I', section[0:4])[0]
            str_bytes = section[4:4+str_len*2]
            control_id = str_bytes.decode('utf-16be')

            # Parse: "ChXX.CC.YYY", "ChXX.Note.YYY", "ChXX.PitchBend"
            ch_match = re.search(r'Ch(\d+)', control_id)
            if ch_match:
                channel = int(ch_match.group(1))

                # CC
                cc_match = re.search(r'CC\.(\d+)', control_id)
                if cc_match:
                    cc_num = int(cc_match.group(1))
                    cc_by_channel[channel].add(cc_num)

                # Note
                note_match = re.search(r'Note\.(\d+)', control_id)
                if note_match:
                    note_num = int(note_match.group(1))
                    note_by_channel[channel].add(note_num)

                # PitchBend
                if 'PitchBend' in control_id:
                    pitchbend_channels.add(channel)

        except:
            pass

        offset = pos + 4

    # Display results
    print("📊 AVAILABLE MIDI CONTROLS\n")

    # CC mappings
    print("="*70)
    print("CC (Control Change) Mappings")
    print("="*70 + "\n")

    for channel in sorted(cc_by_channel.keys()):
        ccs = sorted(cc_by_channel[channel])
        print(f"Channel {channel:2d}: {len(ccs)} CCs available")

        # Show range
        if ccs:
            print(f"  Range: CC {min(ccs)} - CC {max(ccs)}")

            # Check if sequential (all 0-127)
            if ccs == list(range(128)):
                print(f"  ✅ Complete (all 128 CCs: 0-127)")
            else:
                print(f"  CCs: {ccs[:10]}... (showing first 10)")

    # Note mappings
    if note_by_channel:
        print("\n" + "="*70)
        print("Note Mappings")
        print("="*70 + "\n")

        for channel in sorted(note_by_channel.keys()):
            notes = sorted(note_by_channel[channel])
            print(f"Channel {channel:2d}: {len(notes)} Notes - Range: {min(notes)}-{max(notes)}")

    # PitchBend
    if pitchbend_channels:
        print("\n" + "="*70)
        print("PitchBend")
        print("="*70 + "\n")
        print(f"Available on channels: {sorted(pitchbend_channels)}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")

    total_ccs = sum(len(ccs) for ccs in cc_by_channel.values())
    total_notes = sum(len(notes) for notes in note_by_channel.values())

    print(f"Total CC mappings: {total_ccs}")
    print(f"Total Note mappings: {total_notes}")
    print(f"Total PitchBend channels: {len(pitchbend_channels)}")
    print(f"\nThis Generic MIDI device has {len(cc_by_channel)} channels configured.")

    # Save mapping template
    print("\n" + "="*70)
    print("GENERATING MAPPING TEMPLATE")
    print("="*70 + "\n")

    with open('generic_midi_template.txt', 'w') as f:
        f.write("TRAKTOR GENERIC MIDI - AVAILABLE CONTROLS\n")
        f.write("="*70 + "\n\n")
        f.write("This device is configured with the following MIDI controls.\n")
        f.write("Use MIDI Learn in Traktor to assign each CC to a function.\n\n")

        for channel in sorted(cc_by_channel.keys()):
            f.write(f"\n{'='*70}\n")
            f.write(f"CHANNEL {channel}\n")
            f.write(f"{'='*70}\n\n")

            ccs = sorted(cc_by_channel[channel])

            f.write(f"Available CCs: {len(ccs)}\n")
            f.write(f"Range: CC {min(ccs)} - CC {max(ccs)}\n\n")

            f.write("CC Number | Traktor Assignment (use MIDI Learn)\n")
            f.write("-" * 70 + "\n")

            for cc in ccs[:50]:  # First 50 CCs
                f.write(f"CC {cc:3d}   | (not assigned - use MIDI Learn)\n")

            if len(ccs) > 50:
                f.write(f"... and {len(ccs) - 50} more CCs\n")

    print("💾 Template saved to: generic_midi_template.txt")
    print("   Use this as reference for MIDI Learn configuration\n")

if __name__ == "__main__":
    main()
