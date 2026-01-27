#!/usr/bin/env python3
"""
Clone one week from Orchard Grove and repeat it for the target homes.
"""

import os
import django
import sys
from datetime import date, timedelta
from collections import defaultdict

sys.path.insert(0, '/home/staff-rota-system/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, User
from scheduling.models_multi_home import CareHome

def clone_one_week():
    """Clone the pattern from OG's first week (Jan 11-17)."""
    og = CareHome.objects.get(name='ORCHARD_GROVE')
    week_start = date(2026, 1, 11)
    week_end = date(2026, 1, 17)
    
    og_week = Shift.objects.filter(
        unit__care_home=og,
        date__range=[week_start, week_end]
    ).select_related('user', 'user__role', 'shift_type')
    
    # Group by day-of-week, role, shift_type
    pattern = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    for shift in og_week:
        day_num = (shift.date - week_start).days  # 0-6
        role = shift.user.role.name if shift.user and shift.user.role else 'UNKNOWN'
        shift_type_id = shift.shift_type.id
        pattern[day_num][role][shift_type_id] += 1
    
    print("=== Orchard Grove Week Pattern (Jan 11-17) ===")
    days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    total_per_day = []
    for day_num in range(7):
        day_total = sum(sum(counts.values()) for counts in pattern[day_num].values())
        total_per_day.append(day_total)
        print(f"{days[day_num]}: {day_total} shifts")
    
    print(f"\nWeek total: {sum(total_per_day)} shifts")
    print(f"Daily average: {sum(total_per_day)/7:.0f} shifts")
    
    return pattern

def replicate_weekly(pattern, target_home_name, start_date, end_date):
    """Replicate the weekly pattern."""
    from scheduling.models import ShiftType
    
    print(f"\nReplicating to {target_home_name}...")
    target_home = CareHome.objects.get(name=target_home_name)
    
    # Get staff pools
    staff_pools = {}
    for role in ['SM', 'OM', 'SSCW', 'SSCWN', 'SCW', 'SCA', 'SCWN', 'SCAN']:
        staff_pools[role] = list(User.objects.filter(
            unit__care_home=target_home,
            role__name=role,
            is_active=True
        ).select_related('unit'))
    
    # Rotation indices
    rotation = {role: 0 for role in staff_pools.keys()}
    
    shifts_to_create = []
    current_date = start_date
    
    while current_date <= end_date:
        # Get day of week (0 = Saturday for Jan 11, 2026)
        days_from_start = (current_date - date(2026, 1, 11)).days
        day_in_week = days_from_start % 7
        
        for role, shift_types in pattern[day_in_week].items():
            if role not in staff_pools or not staff_pools[role]:
                continue
            
            for shift_type_id, count in shift_types.items():
                shift_type = ShiftType.objects.get(id=shift_type_id)
                
                for _ in range(count):
                    staff_idx = rotation[role] % len(staff_pools[role])
                    staff = staff_pools[role][staff_idx]
                    rotation[role] += 1
                    
                    shifts_to_create.append(Shift(
                        user=staff,
                        unit=staff.unit,
                        shift_type=shift_type,
                        date=current_date
                    ))
        
        current_date += timedelta(days=1)
    
    # Bulk create
    Shift.objects.bulk_create(shifts_to_create, batch_size=1000, ignore_conflicts=True)
    
    # Summary
    role_counts = defaultdict(int)
    for shift in shifts_to_create:
        role_counts[shift.user.role.name] += 1
    
    print(f"Created {len(shifts_to_create)} shifts")
    for role in sorted(role_counts.keys()):
        print(f"  {role}: {role_counts[role]}")
    
    return len(shifts_to_create)

def main():
    pattern = clone_one_week()
    
    start = date(2026, 1, 11)
    end = date(2026, 3, 31)
    
    print(f"\nReplicating week pattern from {start} to {end}")
    
    total = 0
    for home in ['HAWTHORN_HOUSE', 'MEADOWBURN', 'RIVERSIDE']:
        count = replicate_weekly(pattern, home, start, end)
        total += count
    
    print(f"\n✅ Total shifts created: {total:,}")

if __name__ == '__main__':
    main()
