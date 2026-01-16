#!/usr/bin/env python3
import os
import sys
import django
from datetime import date, timedelta

# Add project directory to Python path
sys.path.insert(0, '/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete')
os.chdir('/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'care_home_project.settings')
django.setup()

from scheduling.models import Shift, ShiftType, Unit

# Check what shift type names exist
print("=== ALL SHIFT TYPES IN DATABASE ===")
shift_types = ShiftType.objects.all().order_by('name')
for st in shift_types:
    print(f"  {st.name}: {st.start_time} - {st.end_time}")

print("\n=== SAMPLE SHIFTS FOR JAN 4-10, 2026 ===")
start_date = date(2026, 1, 4)
end_date = date(2026, 1, 10)

shifts = Shift.objects.filter(
    date__range=[start_date, end_date]
).select_related('user', 'unit', 'shift_type').order_by('date', 'unit__name', 'shift_type__name')[:50]

for shift in shifts:
    unit_name = shift.unit.name if shift.unit else 'No Unit'
    shift_type_name = shift.shift_type.name if shift.shift_type else 'No Type'
    staff_name = shift.user.full_name if shift.user else 'No Staff'
    print(f"{shift.date} | {unit_name:15} | {shift_type_name:15} | {staff_name}")

print("\n=== SHIFT TYPE NAME COUNTS FOR WEEK ===")
from collections import Counter
all_shifts = Shift.objects.filter(date__range=[start_date, end_date]).select_related('shift_type')
shift_type_counts = Counter()
for shift in all_shifts:
    shift_type_counts[shift.shift_type.name if shift.shift_type else 'None'] += 1

for st_name, count in shift_type_counts.most_common():
    print(f"{st_name}: {count}")
