#!/usr/bin/env python
"""Populate demo data for production dashboard"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, ShiftType, Shift, User, Role
from datetime import datetime, date, timedelta, time as dt_time
import random

print("Starting demo data population...")

# Create care homes
print("\n1. Creating care homes...")
homes = []
for choice_value, choice_name in CareHome.HOME_CHOICES:
    home, created = CareHome.objects.get_or_create(name=choice_value)
    homes.append(home)
    if created:
        print(f"  ✓ Created: {choice_name}")
print(f"Total care homes: {len(homes)}")

# Create units
print("\n2. Creating units...")
units = []
unit_types = ['Dementia Care', 'Residential', 'Nursing']
for home in homes:
    for idx, unit_type in enumerate(unit_types, 1):
        unit_name = f"{home.get_name_display()} - {unit_type}"
        unit, created = Unit.objects.get_or_create(
            care_home=home,
            name=unit_name,
            defaults={
                'unit_type': unit_type,
                'capacity': random.randint(12, 20),
                'is_active': True
            }
        )
        units.append(unit)
        if created:
            print(f"  ✓ Created: {unit_name}")
print(f"Total units: {len(units)}")

# Create shift types
print("\n3. Creating shift types...")
shift_configs = [
    ('Early', dt_time(7, 0), dt_time(15, 0)),
    ('Late', dt_time(15, 0), dt_time(23, 0)),
    ('Night', dt_time(23, 0), dt_time(7, 0)),
]
shift_types = []
for name, start, end in shift_configs:
    st, created = ShiftType.objects.get_or_create(
        name=name,
        defaults={'start_time': start, 'end_time': end}
    )
    shift_types.append(st)
    if created:
        print(f"  ✓ Created: {name} ({start} - {end})")
print(f"Total shift types: {len(shift_types)}")

# Get user for assignments
try:
    user = User.objects.get(sap='000541')
    print(f"\nFound user: {user.get_full_name()}")
except User.DoesNotExist:
    user = None
    print("\nNo user found for assignments")

# Create shifts
print("\n4. Creating shifts...")
start_date = date.today() - timedelta(days=60)
end_date = date.today() + timedelta(days=30)
shifts_created = 0
shifts_total = 0

current_date = start_date
while current_date <= end_date:
    # Create shifts for random units each day
    daily_units = random.sample(units, k=min(10, len(units)))
    
    for unit in daily_units:
        # Each unit gets 2-3 shifts per day
        daily_shift_types = random.sample(shift_types, k=random.randint(2, 3))
        
        for st in daily_shift_types:
            shift, created = Shift.objects.get_or_create(
                unit=unit,
                shift_type=st,
                date=current_date,
                start_time=st.start_time,
                defaults={
                    'end_time': st.end_time,
                    'required_count': random.randint(2, 5),
                    'assigned_staff': user if user and random.random() < 0.6 else None,
                    'is_published': True,
                }
            )
            shifts_total += 1
            if created:
                shifts_created += 1
    
    current_date += timedelta(days=1)

print(f"  ✓ Created {shifts_created} new shifts")
print(f"Total shifts in database: {Shift.objects.count()}")
print(f"Date range: {start_date} to {end_date}")

print("\n✅ Demo data population complete!")
print(f"\nSummary:")
print(f"  - Care Homes: {CareHome.objects.count()}")
print(f"  - Units: {Unit.objects.count()}")
print(f"  - Shift Types: {ShiftType.objects.count()}")
print(f"  - Shifts: {Shift.objects.count()}")
print(f"  - Users: {User.objects.count()}")
