#!/usr/bin/env python3
"""
Replicate Orchard Grove's 3-week rotating cycle to other homes.
"""

import os
import django
import sys
from datetime import date, timedelta
from collections import defaultdict

sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, User, ShiftType
from scheduling.models_multi_home import CareHome

def extract_3_week_cycle():
    """Extract OG's 3-week cycle (Jan 11-31)."""
    print("="*80)
    print("EXTRACTING ORCHARD GROVE 3-WEEK CYCLE")
    print("="*80)
    
    og = CareHome.objects.get(name='ORCHARD_GROVE')
    cycle_start = date(2026, 1, 11)
    cycle_end = date(2026, 1, 31)  # 21 days
    
    og_shifts = Shift.objects.filter(
        unit__care_home=og,
        date__range=[cycle_start, cycle_end]
    ).select_related('user', 'user__role', 'shift_type')
    
    print(f"Date range: {cycle_start} to {cycle_end} (21 days)")
    print(f"Total OG shifts in 3-week cycle: {og_shifts.count()}")
    
    # Store pattern by day offset (0-20), role, shift type
    pattern = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    for shift in og_shifts:
        day_offset = (shift.date - cycle_start).days
        role = shift.user.role.name if shift.user and shift.user.role else 'UNKNOWN'
        shift_type_name = shift.shift_type.name
        pattern[day_offset][role][shift_type_name] += 1
    
    # Print summary
    print("\n3-Week Cycle Summary:")
    role_totals = defaultdict(int)
    for day_offset in range(21):
        day_total = 0
        for role, shift_types in pattern[day_offset].items():
            count = sum(shift_types.values())
            role_totals[role] += count
            day_total += count
        print(f"  Day {day_offset + 1}: {day_total} shifts")
    
    print("\nTotal by role over 3 weeks:")
    for role in sorted(role_totals.keys()):
        print(f"  {role}: {role_totals[role]} shifts")
    
    return pattern

def replicate_cycle(pattern, target_home_name, full_start, full_end):
    """Replicate 3-week cycle to target home for the full date range."""
    print(f"\n{'='*80}")
    print(f"REPLICATING TO {target_home_name}")
    print(f"{'='*80}")
    
    target_home = CareHome.objects.get(name=target_home_name)
    
    # Delete existing shifts
    deleted = Shift.objects.filter(
        unit__care_home=target_home,
        date__range=[full_start, full_end]
    ).delete()
    print(f"Deleted {deleted[0]} existing shifts")
    
    # Get staff pools by role
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
    
    # Iterate through full date range, repeating 3-week cycle
    current_date = full_start
    while current_date <= full_end:
        # Calculate offset within 3-week cycle (0-20)
        days_since_start = (current_date - full_start).days
        cycle_day = days_since_start % 21  # 21-day cycle
        
        if cycle_day not in pattern:
            current_date += timedelta(days=1)
            continue
        
        # Create shifts based on pattern for this cycle day
        for role, shift_types in pattern[cycle_day].items():
            if role not in staff_by_role or not staff_by_role[role]:
                continue
            
            for shift_type_name, count in shift_types.items():
                try:
                    shift_type = ShiftType.objects.get(name=shift_type_name)
                except ShiftType.DoesNotExist:
                    continue
                
                for i in range(count):
                    # Round-robin staff assignment
                    staff_index = staff_rotation[role] % len(staff_by_role[role])
                    staff = staff_by_role[role][staff_index]
                    staff_rotation[role] += 1
                    
                    shifts_to_create.append(Shift(
                        user=staff,
                        unit=staff.unit,
                        shift_type=shift_type,
                        date=current_date
                    ))
        
        current_date += timedelta(days=1)
    
    # Bulk create
    created = Shift.objects.bulk_create(shifts_to_create, batch_size=1000, ignore_conflicts=True)
    print(f"\n✅ Created {len(created)} shifts for {target_home_name}")
    
    # Summary by role
    role_counts = defaultdict(int)
    for shift in shifts_to_create:
        role_counts[shift.user.role.name] += 1
    
    print("\n--- Total Shifts by Role ---")
    for role, count in sorted(role_counts.items()):
        print(f"  {role}: {count}")
    
    return len(created)

def main():
    # Full replication period
    full_start = date(2026, 1, 11)
    full_end = date(2026, 3, 31)
    total_days = (full_end - full_start).days + 1
    
    print(f"\nFull replication period: {full_start} to {full_end} ({total_days} days)")
    print(f"Number of 3-week cycles: {total_days / 21:.1f}")
    
    # Extract 3-week cycle from OG
    pattern = extract_3_week_cycle()
    
    # Confirm
    response = input("\nProceed with replication? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled")
        return
    
    # Replicate to each home
    total_created = 0
    for home in ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']:
        count = replicate_cycle(pattern, home, full_start, full_end)
        total_created += count
    
    print(f"\n{'='*80}")
    print(f"✅ COMPLETE: Created {total_created} total shifts")
    print(f"Average per home: {total_created // 3}")
    print(f"{'='*80}")
    print("\nRestart the service: systemctl restart staffrota")

if __name__ == '__main__':
    main()
