#!/usr/bin/env python3
"""
Analyze Traktor TSI file and extract MIDI CC mappings
"""

import xml.etree.ElementTree as ET
import sys
from collections import defaultdict

def parse_tsi_file(filename):
    """Parse TSI file and extract MIDI mappings"""
    print(f"\n{'='*70}")
    print(f"📋 ANALYZING: {filename}")
    print(f"{'='*70}\n")

    tree = ET.parse(filename)
    root = tree.getroot()

    # Find all devices
    devices = []
    mappings = defaultdict(list)

    # TSI structure varies, let's find all Entry elements
    for entry in root.iter('Entry'):
        name_elem = entry.find('.//Name')
        if name_elem is not None:
            entry_name = name_elem.get('Value', '')

            # Look for MIDI-related entries
            if any(keyword in entry_name.lower() for keyword in ['midi', 'control', 'assignment']):
                devices.append(entry_name)

    # Find all mappings with CC numbers
    cc_mappings = []

    # Look for entries with ControllerType or MidiCC
    for entry in root.iter('Entry'):
        mapping_data = {}

        for child in entry.iter():
            if child.tag == 'Name' and child.get('Value'):
                key = child.get('Value', '')
                mapping_data['name'] = key

            # Look for MIDI CC values
            if 'MidiCC' in child.tag or 'CC' in child.tag:
                if child.get('Value'):
                    mapping_data['cc'] = child.get('Value')

            # Look for Channel
            if 'Channel' in child.tag:
                if child.get('Value'):
                    mapping_data['channel'] = child.get('Value')

            # Look for Assignment (Deck A, Deck B, etc)
            if 'Assignment' in child.tag:
                if child.get('Value'):
                    mapping_data['assignment'] = child.get('Value')

        if 'cc' in mapping_data and 'name' in mapping_data:
            cc_mappings.append(mapping_data)

    # Alternative approach: scan for numeric values that could be CC numbers
    print("🔍 Searching for MIDI CC patterns...\n")

    # Let's look for the actual structure
    sample_entries = []
    for i, entry in enumerate(root.iter('Entry')):
        if i < 5:  # First 5 entries to understand structure
            entry_dict = {}
            for child in entry:
                if child.tag == 'Name':
                    entry_dict['Name'] = child.get('Value', '')
                elif child.tag == 'Value':
                    entry_dict['Value'] = child.get('Value', child.text)
            if entry_dict:
                sample_entries.append(entry_dict)

    print("📊 Sample TSI Structure:")
    for entry in sample_entries[:10]:
        print(f"  {entry}")

    # Let's use a different strategy - find all Name/Value pairs
    print(f"\n{'─'*70}")
    print("🎛️  MIDI MAPPINGS FOUND:")
    print(f"{'─'*70}\n")

    name_value_pairs = {}
    current_name = None

    for elem in root.iter():
        if elem.tag == 'Name' and elem.get('Value'):
            current_name = elem.get('Value')
        elif elem.tag == 'Value' and current_name:
            value = elem.get('Value', elem.text)
            if value:
                name_value_pairs[current_name] = value
                current_name = None

    # Filter for MIDI-related entries
    midi_entries = {}
    for name, value in name_value_pairs.items():
        if any(keyword in name.lower() for keyword in
               ['midi', 'cc', 'channel', 'control', 'deck', 'play', 'cue',
                'volume', 'eq', 'loop', 'hotcue', 'crossfader', 'browser']):
            midi_entries[name] = value

    # Group by device
    print("Found MIDI Configuration Entries:\n")
    for name, value in sorted(midi_entries.items())[:50]:
        print(f"  {name:50s} = {value}")

    if len(midi_entries) > 50:
        print(f"\n  ... and {len(midi_entries) - 50} more entries")

    print(f"\n{'='*70}")
    print(f"📊 SUMMARY: Found {len(midi_entries)} MIDI-related entries")
    print(f"{'='*70}\n")

    return midi_entries

def extract_cc_numbers(filename):
    """Extract just the CC numbers and their assignments"""
    print(f"\n{'='*70}")
    print("🎯 EXTRACTING CC NUMBER ASSIGNMENTS")
    print(f"{'='*70}\n")

    tree = ET.parse(filename)
    root = tree.getroot()

    # Strategy: look for patterns in the XML
    # TSI files have Device -> Mappings -> In/Out structure

    cc_assignments = []

    # Iterate through all elements looking for CC patterns
    context = []
    for elem in root.iter():
        if elem.tag == 'Entry':
            # Start new context
            context = []

        if elem.tag == 'Name':
            name = elem.get('Value', '')
            if name:
                context.append(name)

        if elem.tag == 'Value':
            value = elem.get('Value', elem.text)
            if value and context:
                # Check if this looks like a CC assignment
                last_name = context[-1] if context else ''

                if 'Channel' in last_name and value.isdigit():
                    channel = int(value)
                elif 'MidiCC' in last_name and value.isdigit():
                    cc = int(value)
                    # Try to find what this CC is mapped to
                    if len(context) > 1:
                        assignment = {
                            'cc': cc,
                            'context': ' → '.join(context[-5:])
                        }
                        cc_assignments.append(assignment)

    # Print unique CC assignments
    seen_ccs = set()
    print("CC Number Assignments Found:\n")
    for assignment in cc_assignments:
        cc = assignment['cc']
        if cc not in seen_ccs and 0 <= cc <= 127:
            print(f"  CC {cc:3d}: {assignment['context']}")
            seen_ccs.add(cc)

    print(f"\n{'='*70}")
    print(f"📊 Found {len(seen_ccs)} unique CC numbers in use")
    print(f"{'='*70}\n")

    return cc_assignments

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "export_0210.tsi"

    try:
        # First pass - understand structure
        midi_entries = parse_tsi_file(filename)

        print("\n" + "="*70 + "\n")

        # Second pass - extract CC numbers
        cc_assignments = extract_cc_numbers(filename)

    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"❌ Error parsing XML: {e}")
        sys.exit(1)
