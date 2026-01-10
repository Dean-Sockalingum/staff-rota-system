#!/usr/bin/env python3
"""
Export shift assignments from local demo for production import
"""
import os
import django
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift

# Get shifts for next 30 days
start_date = datetime(2026, 1, 9).date()
end_date = start_date + timedelta(days=30)

shifts = Shift.objects.filter(
    date__gte=start_date,
    date__lte=end_date
).select_related('user', 'shift_type', 'unit')

shift_data = []
count = 0
for shift in shifts:
    if shift.user and len(shift.user.sap) == 6:  # Only valid 6-digit SAP numbers
        shift_data.append({
            'model': 'scheduling.shift',
            'fields': {
                'date': shift.date.isoformat(),
                'shift_type': shift.shift_type.id,
                'user': shift.user.id,
                'unit': shift.unit.id if shift.unit else None,
                'status': shift.status,
                'notes': shift.notes or '',
            }
        })
        count += 1

print(f'✅ Found {count} shifts to export')

# Save to file
output_file = '/Users/deansockalingum/Desktop/Staff_Rota_Backups/shifts_export.json'
with open(output_file, 'w') as f:
    json.dump(shift_data, f, indent=2)

print(f'✅ Shifts exported to {output_file}')
print(f'File size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB')
