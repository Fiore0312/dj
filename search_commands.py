#!/usr/bin/env python3
import base64
import xml.etree.ElementTree as ET

tree = ET.parse('generic_midi_mapping.tsi')
root = tree.getroot()
entries = {e.get('Name'): e.get('Value') for e in root.iter('Entry')}
data = base64.b64decode(entries['DeviceIO.Config.Controller'])

# Search for command keywords in UTF-16BE
keywords = ['deck', 'play', 'volume', 'eq', 'cue', 'sync', 'load']

for keyword in keywords:
    keyword_utf16 = keyword.encode('utf-16be')
    pos = data.find(keyword_utf16)

    if pos != -1:
        print(f'\n✅ Found "{keyword}" at position {pos}')

        # Show context (200 bytes before and after)
        context_start = max(0, pos - 200)
        context_end = min(len(data), pos + 200)
        context = data[context_start:context_end]

        # Try to decode as UTF-16BE
        try:
            decoded = context.decode('utf-16be', errors='replace')
            # Clean up
            decoded = decoded.replace('\x00', '').replace('\uffff', '')
            print(f'Context: {repr(decoded[:200])}')
        except:
            print('Could not decode context')
    else:
        print(f'❌ "{keyword}" not found')
