#!/usr/bin/env python3
"""
Import Manager Shift Pattern - 3-Week Repeating Cycle
Imports correct manager shift pattern from spreadsheet data
Note: Managers work 5 days/week (MON-FRI), 7 hours/day
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift, ShiftType, Unit
from datetime import datetime, timedelta
from django.utils import timezone

# Manager shift pattern data - 3-week cycle
# Days: 0=SUN, 1=MON, 2=TUE, 3=WED, 4=THU, 5=FRI, 6=SAT
# All managers work MON-FRI (5 days/week) consistently
MANAGER_SHIFT_PATTERN = [
    # Day Senior Social Care Workers (SSCW) - Manager level
    {'sap': 'SSCW0001', 'name': 'Joe Brogan', 'unit': 'DEMENTIA', 'role': 'SSCW', 
     'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [1, 2, 3]},
    {'sap': 'SSCW0002', 'name': 'Jack Barnes', 'unit': 'BLUE', 'role': 'SSCW', 
     'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [1, 2, 3]},
    {'sap': 'SSCW0003', 'name': 'Morag Henderson', 'unit': 'VIOLET', 'role': 'SSCW', 
     'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [1, 2, 3]},
    {'sap': 'SSCW0004', 'name': 'Diane Smith', 'unit': 'ROSE', 'role': 'SSCW', 
     'week1': [4, 5, 6], 'week2': [1, 2, 3], 'week3': [0, 1, 2]},
    {'sap': 'SSCW0005', 'name': 'Juliet Johnson', 'unit': 'GRAPE', 'role': 'SSCW', 
     'week1': [4, 5, 6], 'week2': [1, 2, 3], 'week3': [0, 1, 2]},
    {'sap': 'SSCW0006', 'name': 'Chloe Agnew', 'unit': 'PEACH', 'role': 'SSCW', 
     'week1': [4, 5, 6], 'week2': [1, 2, 3], 'week3': [0, 1, 2]},
    {'sap': 'SSCW0007', 'name': 'Agnes Spragg', 'unit': 'ORANGE', 'role': 'SSCW', 
     'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
    {'sap': 'SSCW0008', 'name': 'Margaret Thatcher', 'unit': 'GREEN', 'role': 'SSCW', 
     'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
    {'sap': 'SSCW0009', 'name': 'Jennifer Ortez', 'unit': 'DEMENTIA', 'role': 'SSCW', 
     'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
    
    # Night Senior Social Care Workers (SSCW(N)) - Manager level
    {'sap': 'SSCWN0001', 'name': 'Ian Brown', 'unit': 'DEMENTIA', 'role': 'SSCW(N)', 
     'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
    {'sap': 'SSCWN0002', 'name': 'John Dollan', 'unit': 'BLUE', 'role': 'SSCW(N)', 
     'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
    {'sap': 'SSCWN0003', 'name': 'Elaine Martinez', 'unit': 'VIOLET', 'role': 'SSCW(N)', 
     'week1': [0, 1, 2], 'week2': [4, 5, 6], 'week3': [2, 3, 4]},
    {'sap': 'SSCWN0004', 'name': 'Wendy Campbell', 'unit': 'ROSE', 'role': 'SSCW(N)', 
     'week1': [4, 5, 6], 'week2': [1, 2, 3], 'week3': [0, 1, 2]},
    {'sap': 'SSCWN0005', 'name': 'Nicole Stewart', 'unit': 'GRAPE', 'role': 'SSCW(N)', 
     'week1': [4, 5, 6], 'week2': [1, 2, 3], 'week3': [0, 1, 2]},
    {'sap': 'SSCWN0006', 'name': 'Evelyn Henderson', 'unit': 'PEACH', 'role': 'SSCW(N)', 
     'week1': [4, 5, 6], 'week2': [1, 2, 3], 'week3': [0, 1, 2]},
    {'sap': 'SSCWN0007', 'name': 'Ruth Tyler', 'unit': 'ORANGE', 'role': 'SSCW(N)', 
     'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
    {'sap': 'SSCWN0008', 'name': 'Sarah Clark', 'unit': 'GREEN', 'role': 'SSCW(N)', 
     'week1': [2, 3, 4], 'week2': [0, 1, 2], 'week3': [4, 5, 6]},
    
    # Services Manager and Operations Managers (MON-FRI only, 5 days/week)
    {'sap': 'SM0001', 'name': 'Les Dorson', 'unit': 'MGMT', 'role': 'SM', 
     'week1': [1, 2, 3, 4, 5], 'week2': [1, 2, 3, 4, 5], 'week3': [1, 2, 3, 4, 5]},
    {'sap': 'OM0002', 'name': 'Jessie Jones', 'unit': 'MGMT', 'role': 'OM', 
     'week1': [1, 2, 3, 4, 5], 'week2': [1, 2, 3, 4, 5], 'week3': [1, 2, 3, 4, 5]},
    {'sap': 'OM0001', 'name': 'Wyn Thomas', 'unit': 'MGMT', 'role': 'OM', 
     'week1': [1, 2, 3, 4, 5], 'week2': [1, 2, 3, 4, 5], 'week3': [1, 2, 3, 4, 5]},
]

def main():
    print("\n" + "="*70)
    print("MANAGER SHIFT PATTERN IMPORT - 3-WEEK REPEATING CYCLE")
    print("="*70)
    
    # Get all possible shift types for managers
    try:
        # Day SSCW managers
        sscw_day_shift = ShiftType.objects.get(name='DAY_SENIOR')
        
        # Night SSCW managers
        sscw_night_shift = ShiftType.objects.get(name='NIGHT_SENIOR')
        
        # Try to get manager shift types (SM/OM)
        try:
            manager_shift = ShiftType.objects.get(name__icontains='MANAGER')
            print(f"\n✅ Found dedicated manager shift type: {manager_shift.get_name_display()}")
        except ShiftType.DoesNotExist:
            # Use day shift for managers if no dedicated type exists
            manager_shift = sscw_day_shift
            print(f"\n⚠️  No dedicated manager shift type - using {manager_shift.get_name_display()}")
        except ShiftType.MultipleObjectsReturned:
            # Multiple manager types - use first day manager type
            manager_shift = ShiftType.objects.filter(name__icontains='MANAGER').first()
            print(f"\n✅ Using manager shift type: {manager_shift.get_name_display()}")
            
    except ShiftType.DoesNotExist as e:
        print(f"❌ ERROR: Required shift types not found: {e}")
        return
    
    print(f"\n✅ Using shift types:")
    print(f"   SSCW (Day): {sscw_day_shift.get_name_display()} ({sscw_day_shift.start_time} - {sscw_day_shift.end_time})")
    print(f"   SSCW (Night): {sscw_night_shift.get_name_display()} ({sscw_night_shift.start_time} - {sscw_night_shift.end_time})")
    print(f"   SM/OM: {manager_shift.get_name_display()} ({manager_shift.start_time} - {manager_shift.end_time})")
    
    # Delete existing manager shifts
    print(f"\n🗑️  Deleting existing manager shifts...")
    
    # Get all manager SAPs
    manager_saps = [p['sap'] for p in MANAGER_SHIFT_PATTERN]
    manager_users = User.objects.filter(sap__in=manager_saps)
    
    deleted_count = Shift.objects.filter(user__in=manager_users).delete()[0]
    print(f"   Deleted: {deleted_count} shifts")
    
    # Start date - Nov 30, 2025 (Sunday - start of week)
    start_date = datetime(2025, 11, 30).date()
    print(f"\n📅 Starting from: {start_date.strftime('%Y-%m-%d')} (Sunday)")
    
    # Import for 1 year (52 weeks = ~17.3 three-week cycles)
    total_weeks = 52
    total_cycles = total_weeks // 3
    
    print(f"   Generating: {total_weeks} weeks ({total_cycles} complete 3-week cycles)")
    
    stats = {
        'created': 0,
        'errors': 0,
        'staff_processed': 0
    }
    
    print(f"\n📊 Processing {len(MANAGER_SHIFT_PATTERN)} manager staff members...")
    
    for staff_pattern in MANAGER_SHIFT_PATTERN:
        try:
            # Get user
            user = User.objects.get(sap=staff_pattern['sap'])
            stats['staff_processed'] += 1
            
            # Get unit
            try:
                unit = Unit.objects.get(name=staff_pattern['unit'])
            except Unit.DoesNotExist:
                print(f"   ⚠️  WARNING: Unit {staff_pattern['unit']} not found for {staff_pattern['sap']}")
                unit = Unit.objects.first()  # Fallback to first unit
            
            # Determine shift type based on role
            if 'SSCW(N)' in staff_pattern['role'] or 'SSCWN' in staff_pattern['role']:
                shift_type = sscw_night_shift
            elif 'SSCW' in staff_pattern['role']:
                shift_type = sscw_day_shift
            else:  # SM or OM
                shift_type = manager_shift
            
            # Generate shifts for all cycles
            for cycle in range(total_cycles + 1):  # +1 to cover partial cycle
                for week_num in range(3):
                    week_key = f'week{week_num + 1}'
                    if week_key not in staff_pattern:
                        continue
                    
                    # Calculate week start date
                    week_offset = (cycle * 3) + week_num
                    if week_offset >= total_weeks:
                        break
                        
                    week_start = start_date + timedelta(weeks=week_offset)
                    
                    # Create shifts for this week
                    for day_of_week in staff_pattern[week_key]:
                        shift_date = week_start + timedelta(days=day_of_week)
                        
                        # Create shift
                        Shift.objects.create(
                            user=user,
                            date=shift_date,
                            shift_type=shift_type,
                            unit=unit,
                            status='SCHEDULED'
                        )
                        stats['created'] += 1
            
            if stats['staff_processed'] % 5 == 0:
                print(f"   Processed: {stats['staff_processed']}/{len(MANAGER_SHIFT_PATTERN)} staff...")
                
        except User.DoesNotExist:
            print(f"   ⚠️  WARNING: User {staff_pattern['sap']} not found - skipping")
            stats['errors'] += 1
        except Exception as e:
            print(f"   ❌ ERROR processing {staff_pattern['sap']}: {e}")
            stats['errors'] += 1
    
    print(f"\n{'='*70}")
    print(f"IMPORT COMPLETE!")
    print(f"{'='*70}")
    print(f"✅ Staff processed: {stats['staff_processed']}/{len(MANAGER_SHIFT_PATTERN)}")
    print(f"✅ Shifts created: {stats['created']}")
    if stats['errors'] > 0:
        print(f"⚠️  Errors: {stats['errors']}")
    
    # Verify with Les Dorson (Services Manager - should work MON-FRI every week)
    print(f"\n{'='*70}")
    print(f"VERIFICATION: Les Dorson (SM0001) - Services Manager")
    print(f"{'='*70}")
    
    try:
        les = User.objects.get(sap='SM0001')
        verify_start = datetime(2025, 11, 30).date()
        verify_end = datetime(2025, 12, 20).date()
        
        les_shifts = Shift.objects.filter(
            user=les,
            date__range=[verify_start, verify_end]
        ).order_by('date')
        
        print(f"Expected pattern: MON-FRI every week (5 shifts/week)")
        print(f"Actual shifts in Nov 30 - Dec 20:")
        
        for week_num in range(3):
            week_start = verify_start + timedelta(weeks=week_num)
            week_end = week_start + timedelta(days=6)
            week_shifts = [s for s in les_shifts if week_start <= s.date <= week_end]
            
            print(f"\n  Week {week_num + 1} ({week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}):")
            for shift in week_shifts:
                print(f"    {shift.date.strftime('%a %b %d')}: {shift.shift_type.get_name_display()}")
        
        print(f"\n  Total: {les_shifts.count()} shifts (Expected: 15 = 5 shifts × 3 weeks)")
        
        if les_shifts.count() == 15:
            print(f"\n✅ VERIFICATION PASSED!")
        else:
            print(f"\n⚠️  WARNING: Shift count mismatch!")
            
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
    
    # Verify with Joe Brogan (SSCW day manager)
    print(f"\n{'='*70}")
    print(f"VERIFICATION: Joe Brogan (SSCW0001) - Day Manager")
    print(f"{'='*70}")
    
    try:
        joe = User.objects.get(sap='SSCW0001')
        verify_start = datetime(2025, 11, 30).date()
        verify_end = datetime(2025, 12, 20).date()
        
        joe_shifts = Shift.objects.filter(
            user=joe,
            date__range=[verify_start, verify_end]
        ).order_by('date')
        
        print(f"Expected pattern: Week1=[SUN,MON,TUE], Week2=[THU,FRI,SAT], Week3=[MON,TUE,WED]")
        print(f"Actual shifts in Nov 30 - Dec 20:")
        
        for week_num in range(3):
            week_start = verify_start + timedelta(weeks=week_num)
            week_end = week_start + timedelta(days=6)
            week_shifts = [s for s in joe_shifts if week_start <= s.date <= week_end]
            
            print(f"\n  Week {week_num + 1} ({week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}):")
            for shift in week_shifts:
                print(f"    {shift.date.strftime('%a %b %d')}: {shift.shift_type.get_name_display()}")
        
        print(f"\n  Total: {joe_shifts.count()} shifts (Expected: 9)")
        
        if joe_shifts.count() == 9:
            print(f"\n✅ VERIFICATION PASSED!")
        else:
            print(f"\n⚠️  WARNING: Shift count mismatch!")
            
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
    
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    main()
