#!/usr/bin/env python3
"""
Parse Generic MIDI TSI file and extract CC mappings
"""

import xml.etree.ElementTree as ET
import sys
from collections import defaultdict

def parse_tsi(filename):
    """Parse TSI and extract Generic MIDI mappings"""

    print(f"\n{'='*70}")
    print(f"📋 ANALYZING: {filename}")
    print(f"{'='*70}\n")

    tree = ET.parse(filename)
    root = tree.getroot()

    # Search for Generic MIDI device
    print("🔍 Searching for Generic MIDI device...\n")

    # Strategy: look for DEVI entries (Device Info)
    # TSI structure: DIOM -> DIOS -> DEVS -> DEVI (device name)

    # Let's scan all Entry elements
    all_entries = {}
    for entry in root.iter('Entry'):
        name = entry.get('Name', '')
        value = entry.get('Value', '')
        if name:
            all_entries[name] = value

    # Look for controller config
    controller_entries = {k: v for k, v in all_entries.items()
                         if 'Controller' in k or 'Midi' in k or 'Generic' in k}

    print(f"📊 Found {len(controller_entries)} controller-related entries:\n")
    for name, value in sorted(controller_entries.items())[:20]:
        print(f"  {name}")
        if len(value) < 100:
            print(f"    Value: {value}")

    # The controller mappings are in DeviceIO.Config.Controller
    # This is Base64 encoded binary data
    if 'DeviceIO.Config.Controller' in all_entries:
        controller_data = all_entries['DeviceIO.Config.Controller']
        print(f"\n✅ Found DeviceIO.Config.Controller (length: {len(controller_data)})")

        # Try to find readable strings in the data
        # TSI uses UTF-16 encoding for device names
        print("\n🔍 Searching for device names in binary data...")

        # Look for "Generic MIDI" pattern
        if 'Generic' in controller_data or 'MIDI' in controller_data:
            print("✅ Found 'Generic' or 'MIDI' in controller data!")

        # Try to extract some info
        import re

        # Search for CC patterns in the data
        # CC assignments look like: Ch X.CC YY
        cc_pattern = re.findall(r'CC\.?(\d+)', controller_data)
        if cc_pattern:
            print(f"\n📋 Found CC numbers: {sorted(set(cc_pattern))[:20]}")

        # Search for Channel patterns
        ch_pattern = re.findall(r'Ch\.?(\d+)', controller_data)
        if ch_pattern:
            print(f"📋 Found Channels: {sorted(set(ch_pattern))[:10]}")

    # Try to find mappings in a different way
    # Look for entries that contain mapping info
    print(f"\n{'─'*70}")
    print("🎛️  SEARCHING FOR MIDI ASSIGNMENTS...")
    print(f"{'─'*70}\n")

    # Search for patterns like "Assignment", "Control", etc.
    mapping_entries = {k: v for k, v in all_entries.items()
                      if any(word in k for word in ['Assignment', 'Control', 'Mapping', 'Input', 'Output'])}

    if mapping_entries:
        print(f"Found {len(mapping_entries)} mapping-related entries:\n")
        for name, value in sorted(mapping_entries.items())[:30]:
            print(f"  {name}")
            if len(value) < 200:
                print(f"    = {value[:100]}")

    print(f"\n{'='*70}")

    return all_entries

def extract_device_info(controller_data):
    """Try to extract device info from binary data"""

    print(f"\n{'='*70}")
    print("🔬 DETAILED BINARY ANALYSIS")
    print(f"{'='*70}\n")

    # TSI format uses specific markers
    # DIOM = Device Input/Output Mappings
    # DEVS = Devices
    # DEVI = Device Info

    markers = ['DIOM', 'DIOS', 'DEVS', 'DEVI', 'DDAT', 'DDIF', 'DDIV',
               'DDIC', 'DDPT', 'DDDC', 'DDCI', 'DCDT', 'DCDI', 'DCCO', 'DCCM']

    for marker in markers:
        if marker in controller_data:
            index = controller_data.index(marker)
            print(f"✅ Found marker: {marker} at position {index}")

            # Try to extract nearby data
            snippet = controller_data[index:index+200]
            # Look for readable ASCII
            readable = ''.join(c if c.isprintable() else '.' for c in snippet)
            print(f"   Context: {readable[:100]}")

    # Try to find "Generic MIDI" string
    if 'Generic' in controller_data:
        idx = controller_data.index('Generic')
        snippet = controller_data[max(0, idx-50):idx+100]
        readable = ''.join(c if c.isprintable() else '.' for c in snippet)
        print(f"\n📍 Found 'Generic' at position {idx}")
        print(f"   Context: {readable}")

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "generic_midi_mapping.tsi"

    try:
        entries = parse_tsi(filename)

        # If we found controller data, analyze it further
        if 'DeviceIO.Config.Controller' in entries:
            extract_device_info(entries['DeviceIO.Config.Controller'])

        print(f"\n{'='*70}")
        print(f"📊 SUMMARY")
        print(f"{'='*70}")
        print(f"Total entries in TSI: {len(entries)}")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
