#!/usr/bin/env python3
"""Clean export data to match production schema"""
import json

print("Loading export data...")
with open('/Users/deansockalingum/Desktop/Staff_Rota_Backups/demo_export.json', 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data)} objects")

cleaned = 0
skipped = []

for obj in data:
    if obj['model'] == 'scheduling.user':
        sap = obj['pk']
        fields = obj['fields']
        
        if not sap.isdigit() or len(sap) != 6:
            print(f"  Skipping user with invalid SAP: {sap}")
            skipped.append(obj)
            continue
        
        if 'team' in fields and fields['team'] and len(fields['team']) > 1:
            fields['team'] = fields['team'][0]
            cleaned += 1
        
        fields_to_remove = ['contracted_hours_per_week', 'prefers_day_shifts', 'prefers_night_shifts', 'max_consecutive_shifts', 'min_hours_between_shifts', 'overtime_preference', 'assigned_unit', 'care_home']
        for field in fields_to_remove:
            if field in fields:
                del fields[field]

for obj in skipped:
    data.remove(obj)

print(f"Skipped {len(skipped)} invalid users")

with open('/Users/deansockalingum/Desktop/Staff_Rota_Backups/demo_export_cleaned.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✓ Saved {len(data)} objects")
