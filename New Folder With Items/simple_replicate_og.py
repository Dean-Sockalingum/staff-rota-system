#!/usr/bin/env python3
"""
Simple shift replication: Count OG's shifts by role/shift_type/date, 
then create same counts for other homes using their staff pools.
"""

import os
import django
import sys
from datetime import date, timedelta
from collections import defaultdict

sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, User, Unit, ShiftType
from scheduling.models_multi_home import CareHome

def analyze_og_pattern(start_date, end_date):
    """Count OG shifts by role, shift type, and date."""
    og = CareHome.objects.get(name='ORCHARD_GROVE')
    og_shifts = Shift.objects.filter(
        unit__care_home=og,
        date__range=[start_date, end_date]
    ).select_related('user', 'user__role', 'shift_type')
    
    pattern = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    for shift in og_shifts:
        role = shift.user.role.name if shift.user and shift.user.role else 'UNKNOWN'
        shift_type_name = shift.shift_type.name
        day_of_week = shift.date.weekday()  # 0=Monday, 6=Sunday
        pattern[day_of_week][role][shift_type_name] += 1
    
    print("=== Orchard Grove Daily Pattern ===")
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day_num in range(7):
        print(f"\n{days[day_num]}:")
        for role in sorted(pattern[day_num].keys()):
            total = sum(pattern[day_num][role].values())
            print(f"  {role}: {total} shifts")
            for shift_type, count in sorted(pattern[day_num][role].items()):
                print(f"    {shift_type}: {count}")
    
    return pattern

def replicate_pattern(pattern, target_home_name, start_date, end_date):
    """Replicate OG pattern to target home."""
    print(f"\n{'='*80}")
    print(f"REPLICATING TO {target_home_name}")
    print(f"{'='*80}")
    
    target_home = CareHome.objects.get(name=target_home_name)
    target_units = list(Unit.objects.filter(care_home=target_home, is_active=True))
    
    if not target_units:
        print(f"ERROR: No units found for {target_home_name}")
        return 0
    
    # Delete existing shifts
    deleted = Shift.objects.filter(
        unit__care_home=target_home,
        date__range=[start_date, end_date]
    ).delete()
    print(f"Deleted {deleted[0]} existing shifts")
    
    # Get staff pools
    staff_by_role = {}
    for role in ['SM', 'OM', 'SSCW', 'SSCWN', 'SCW', 'SCA', 'SCWN', 'SCAN']:
        staff_by_role[role] = list(User.objects.filter(
            unit__care_home=target_home,
            role__name=role,
            is_active=True
        ).select_related('unit', 'role'))
        print(f"  {role}: {len(staff_by_role[role])} staff")
    
    shifts_to_create = []
    staff_rotation = {role: 0 for role in staff_by_role.keys()}
    
    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.weekday()
        
        if day_of_week not in pattern:
            current_date += timedelta(days=1)
            continue
        
        for role, shift_types in pattern[day_of_week].items():
            if role not in staff_by_role or not staff_by_role[role]:
                print(f"  WARNING: No {role} staff for {target_home_name}")
                continue
            
            for shift_type_name, count in shift_types.items():
                try:
                    shift_type = ShiftType.objects.get(name=shift_type_name)
                except ShiftType.DoesNotExist:
                    print(f"  WARNING: Shift type {shift_type_name} not found")
                    continue
                
                for i in range(count):
                    # Round-robin staff assignment
                    staff_index = staff_rotation[role] % len(staff_by_role[role])
                    staff = staff_by_role[role][staff_index]
                    staff_rotation[role] += 1
                    
                    # Assign to staff's own unit
                    shifts_to_create.append(Shift(
                        user=staff,
                        unit=staff.unit,
                        shift_type=shift_type,
                        date=current_date
                    ))
        
        current_date += timedelta(days=1)
    
    # Bulk create with ignore_conflicts to skip duplicates
    created = Shift.objects.bulk_create(shifts_to_create, batch_size=500, ignore_conflicts=True)
    print(f"\n✅ Created {len(created)} shifts for {target_home_name}")
    
    # Summary
    role_counts = defaultdict(int)
    for shift in shifts_to_create:
        role_counts[shift.user.role.name] += 1
    
    print("\n--- Shifts by Role ---")
    for role, count in sorted(role_counts.items()):
        print(f"  {role}: {count}")
    
    return len(created)

def main():
    start_date = date(2026, 1, 11)
    end_date = date(2026, 3, 31)
    
    print(f"Date range: {start_date} to {end_date}")
    
    # Analyze OG pattern
    pattern = analyze_og_pattern(start_date, end_date)
    
    # Replicate
    response = input("\nProceed with replication? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled")
        return
    
    total = 0
    for home in ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']:
        count = replicate_pattern(pattern, home, start_date, end_date)
        total += count
    
    print(f"\n{'='*80}")
    print(f"✅ COMPLETE: Created {total} total shifts")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
