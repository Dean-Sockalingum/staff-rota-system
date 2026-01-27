import json

with open('staff_export_821.json', 'r') as f:
    data = json.load(f)

print(f'Total entries in JSON: {len(data)}')
print(f'\nChecking for unique SAP numbers:')

unique_saps = set()
sap_counts = {}
for entry in data:
    sap = entry.get('sap')
    unique_saps.add(sap)
    sap_counts[sap] = sap_counts.get(sap, 0) + 1

print(f'Unique SAP numbers: {len(unique_saps)}')
print(f'\nSAP format breakdown:')

six_digit = [s for s in unique_saps if s and s.isdigit() and len(s) == 6]
alpha_numeric = [s for s in unique_saps if s and not s.isdigit()]

print(f'  6-digit SAPs (000001-999999): {len(six_digit)}')
print(f'  Alpha-numeric SAPs (SCW1080, etc.): {len(alpha_numeric)}')

print(f'\nDuplicates:')
duplicates = [(sap, count) for sap, count in sap_counts.items() if count > 1]
if duplicates:
    print(f'  Found {len(duplicates)} duplicate SAPs')
    for sap, count in sorted(duplicates, key=lambda x: x[1], reverse=True)[:10]:
        print(f'    {sap}: appears {count} times')
else:
    print(f'  No duplicates found')

print(f'\nSample 6-digit SAPs: {sorted(six_digit)[:10]}')
print(f'Sample alpha-numeric SAPs: {sorted(alpha_numeric)[:10]}')

# Check for entries with units
with_units = [e for e in data if e.get('unit')]
without_units = [e for e in data if not e.get('unit')]
print(f'\nEntries with units assigned: {len(with_units)}')
print(f'Entries without units: {len(without_units)}')
