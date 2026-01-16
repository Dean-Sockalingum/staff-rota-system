#!/usr/bin/env python3
import os
import django
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, CareHome, Shift
from datetime import datetime, timedelta

# Get Orchard Grove staff
og_home = CareHome.objects.get(name='ORCHARD_GROVE')
og_units = Unit.objects.filter(care_home=og_home)
og_staff = User.objects.filter(
    unit__in=og_units,
    is_active=True
).select_related('role', 'unit').order_by('sap')

print("="*80)
print(f"ORCHARD GROVE SHIFT PATTERNS (178 Staff)")
print("="*80)

# Analyze shift patterns over last 3 weeks
end_date = datetime.now().date()
start_date = end_date - timedelta(days=21)

print(f"\nAnalyzing shifts from {start_date} to {end_date}")
print(f"Looking for recurring shift patterns...\n")

# Group staff by unit and role
staff_by_unit_role = defaultdict(list)
for staff in og_staff:
    key = (staff.unit.name, staff.role.name)
    staff_by_unit_role[key].append(staff)

# For each group, show the pattern
for (unit, role), staff_list in sorted(staff_by_unit_role.items()):
    print(f"\n{unit} - {role}: {len(staff_list)} staff")
    
    # Show first 5 staff in this group with their shifts
    for staff in staff_list[:5]:
        shifts = Shift.objects.filter(
            user=staff,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if shifts.exists():
            # Get days of week (0=Mon, 6=Sun)
            days_worked = set()
            for shift in shifts:
                days_worked.add(shift.date.weekday())
            
            # Convert to day names
            day_names = {
                0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu',
                4: 'Fri', 5: 'Sat', 6: 'Sun'
            }
            pattern = ', '.join(sorted([day_names[d] for d in sorted(days_worked)]))
            
            print(f"  SAP {staff.sap}: {staff.first_name} {staff.last_name:20} | {shifts.count():2} shifts | Days: {pattern}")
        else:
            print(f"  SAP {staff.sap}: {staff.first_name} {staff.last_name:20} | NO SHIFTS FOUND")

print("\n" + "="*80)
print("PATTERN SUMMARY")
print("="*80)

# Count staff with and without shifts
staff_with_shifts = 0
staff_without_shifts = 0

for staff in og_staff:
    shift_count = Shift.objects.filter(user=staff, date__gte=start_date).count()
    if shift_count > 0:
        staff_with_shifts += 1
    else:
        staff_without_shifts += 1

print(f"\nStaff with shifts in last 3 weeks: {staff_with_shifts}")
print(f"Staff without shifts: {staff_without_shifts}")
print(f"Total OG active staff: {og_staff.count()}")
