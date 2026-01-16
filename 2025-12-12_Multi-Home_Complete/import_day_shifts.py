#!/usr/bin/env python3
"""
Import Day Shift Pattern - 3-Week Repeating Cycle
Clears existing shifts and imports correct pattern from spreadsheet data
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift, ShiftType, Unit
from datetime import datetime, timedelta
from django.utils import timezone

# Day shift pattern data - 3-week cycle
DAY_SHIFT_PATTERN = [
    # Week 1: TUE, FRI, SAT pattern
    {'sap': 'SCW1001', 'name': 'Alice Smith', 'unit': 'DEMENTIA', 'role': 'SCW Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCW1002', 'name': 'Bob Johnson', 'unit': 'BLUE', 'role': 'SCW Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCW1003', 'name': 'Carol Williams', 'unit': 'ORANGE', 'role': 'SCW Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCW1004', 'name': 'David Brown', 'unit': 'GREEN', 'role': 'SCW Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCW1005', 'name': 'Emily Jones', 'unit': 'VIOLET', 'role': 'SCW Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCW1006', 'name': 'Frank Garcia', 'unit': 'ROSE', 'role': 'SCW Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCW1007', 'name': 'Grace Miller', 'unit': 'GRAPE', 'role': 'SCW Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCW1008', 'name': 'Henry Davis', 'unit': 'PEACH', 'role': 'SCW Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCW1009', 'name': 'Ivy Rodriguez', 'unit': 'DEMENTIA', 'role': 'SCW Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    
    {'sap': 'SCA1010', 'name': 'Jack Martinez', 'unit': 'DEMENTIA', 'role': 'SCA Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCA1011', 'name': 'Karen Hernandez', 'unit': 'BLUE', 'role': 'SCA Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCA1012', 'name': 'Liam Lopez', 'unit': 'ORANGE', 'role': 'SCA Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCA1013', 'name': 'Mia Gonzalez', 'unit': 'GREEN', 'role': 'SCA Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCA1014', 'name': 'Noah Wilson', 'unit': 'VIOLET', 'role': 'SCA Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCA1015', 'name': 'Olivia Anderson', 'unit': 'ROSE', 'role': 'SCA Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCA1016', 'name': 'Peter Thomas', 'unit': 'GRAPE', 'role': 'SCA Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCA1017', 'name': 'Quinn Taylor', 'unit': 'PEACH', 'role': 'SCA Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCA1018', 'name': 'Rachel Moore', 'unit': 'DEMENTIA', 'role': 'SCA Days', 'week1': [3, 5, 6], 'week2': [0, 3, 4], 'week3': [1, 2, 3]},
    {'sap': 'SCA1019', 'name': 'Sam Jackson', 'unit': 'PEACH', 'role': 'SCA Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCA1020', 'name': 'Tina Martin', 'unit': 'BLUE', 'role': 'SCA Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCA1021', 'name': 'Uma Lee', 'unit': 'ORANGE', 'role': 'SCA Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCA1022', 'name': 'Victor Perez', 'unit': 'GREEN', 'role': 'SCA Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCA1023', 'name': 'Wendy Thompson', 'unit': 'VIOLET', 'role': 'SCA Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCA1024', 'name': 'Xander White', 'unit': 'ROSE', 'role': 'SCA Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    {'sap': 'SCA1025', 'name': 'Yara Harris', 'unit': 'GRAPE', 'role': 'SCA Days', 'week1': [5, 6], 'week2': [0, 4], 'week3': [1, 2]},
    
    # SUN, TUE, WED pattern
    {'sap': 'SCW1026', 'name': 'Zoe Sanchez', 'unit': 'GREEN', 'role': 'SCW Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCW1027', 'name': 'Aaron Clark', 'unit': 'VIOLET', 'role': 'SCW Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCW1028', 'name': 'Bella Ramirezz', 'unit': 'ROSE', 'role': 'SCW Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCW1029', 'name': 'Caleb Lewis', 'unit': 'GRAPE', 'role': 'SCW Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCW1030', 'name': 'Diana Robinson', 'unit': 'PEACH', 'role': 'SCW Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCW1031', 'name': 'Ethan Walker', 'unit': 'DEMENTIA', 'role': 'SCW Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCW1032', 'name': 'Fiona Young', 'unit': 'BLUE', 'role': 'SCW Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCW1033', 'name': 'George Allen', 'unit': 'ORANGE', 'role': 'SCW Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCW1034', 'name': 'Hannah King', 'unit': 'GREEN', 'role': 'SCW Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    
    {'sap': 'SCA1035', 'name': 'Isaac Wright', 'unit': 'VIOLET', 'role': 'SCA Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCA1036', 'name': 'Julia Scott', 'unit': 'ROSE', 'role': 'SCA Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCA1037', 'name': 'Kyle Torres', 'unit': 'GRAPE', 'role': 'SCA Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCA1038', 'name': 'Luna Nguyen', 'unit': 'PEACH', 'role': 'SCA Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCA1039', 'name': 'Mark Hill', 'unit': 'DEMENTIA', 'role': 'SCA Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCA1040', 'name': 'Nora Green', 'unit': 'BLUE', 'role': 'SCA Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCA1041', 'name': 'Oscar Adams', 'unit': 'GRAPE', 'role': 'SCA Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCA1042', 'name': 'Piper Baker', 'unit': 'ORANGE', 'role': 'SCA Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCA1043', 'name': 'Ryan Nelson', 'unit': 'GREEN', 'role': 'SCA Days', 'week1': [0, 3, 4], 'week2': [1, 2, 3], 'week3': [4, 5, 6]},
    {'sap': 'SCA1044', 'name': 'Sophia Hall', 'unit': 'VIOLET', 'role': 'SCA Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCA1045', 'name': 'Tyler Rivera', 'unit': 'ROSE', 'role': 'SCA Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCA1046', 'name': 'Ursula Campbell', 'unit': 'GRAPE', 'role': 'SCA Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCA1047', 'name': 'Vincent Mitchell', 'unit': 'PEACH', 'role': 'SCA Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCA1048', 'name': 'Willow Carter', 'unit': 'DEMENTIA', 'role': 'SCA Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCA1049', 'name': 'Wyatt Roberts', 'unit': 'BLUE', 'role': 'SCA Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    {'sap': 'SCA1050', 'name': 'Xenia Phillips', 'unit': 'ORANGE', 'role': 'SCA Days', 'week1': [0, 4], 'week2': [1, 2], 'week3': [5, 6]},
    
    # MON, TUE, WED pattern
    {'sap': 'SCW1051', 'name': 'Yvonne Evans', 'unit': 'GRAPE', 'role': 'SCW Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCW1052', 'name': 'Zachary Turner', 'unit': 'PEACH', 'role': 'SCW Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCW1053', 'name': 'Abigail Cooper', 'unit': 'DEMENTIA', 'role': 'SCW Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCW1054', 'name': 'Ben Morris', 'unit': 'BLUE', 'role': 'SCW Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCW1055', 'name': 'Chloe Rogers', 'unit': 'ORANGE', 'role': 'SCW Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCW1056', 'name': 'Daniel Cox', 'unit': 'GREEN', 'role': 'SCW Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCW1057', 'name': 'Ella Ward', 'unit': 'VIOLET', 'role': 'SCW Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCW1058', 'name': 'Finn Gray', 'unit': 'ROSE', 'role': 'SCW Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCW1059', 'name': 'Gemma Bell', 'unit': 'GRAPE', 'role': 'SCW Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    
    {'sap': 'SCA1060', 'name': 'Harry Coleman', 'unit': 'PEACH', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1061', 'name': 'Isabel Foster', 'unit': 'DEMENTIA', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1062', 'name': 'Jacob Bailey', 'unit': 'BLUE', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1063', 'name': 'Katie Reed', 'unit': 'ORANGE', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1064', 'name': 'Leo Kelly', 'unit': 'GREEN', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1065', 'name': 'Megan Howard', 'unit': 'VIOLET', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1066', 'name': 'Nathan Peterson', 'unit': 'ROSE', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1067', 'name': 'Poppy Cook', 'unit': 'GRAPE', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1068', 'name': 'Quentin Price', 'unit': 'PEACH', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1069', 'name': 'Ruby Barnes', 'unit': 'DEMENTIA', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1070', 'name': 'Sebastian Ross', 'unit': 'BLUE', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1071', 'name': 'Taylor Henderson', 'unit': 'ORANGE', 'role': 'SCA Days', 'week1': [1, 2, 3], 'week2': [4, 5, 6], 'week3': [0, 3, 4]},
    {'sap': 'SCA1079', 'name': 'Janice Henderson', 'unit': 'GREEN', 'role': 'SCA Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCA1072', 'name': 'Victor Watson', 'unit': 'VIOLET', 'role': 'SCA Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCA1073', 'name': 'Zoe Brooks', 'unit': 'ROSE', 'role': 'SCA Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCA1074', 'name': 'Adam Bryant', 'unit': 'GRAPE', 'role': 'SCA Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCA1075', 'name': 'Beth Griffin', 'unit': 'PEACH', 'role': 'SCA Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCA1076', 'name': 'Natasha Jones', 'unit': 'DEMENTIA', 'role': 'SCA Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCA1077', 'name': 'Abby Johnson', 'unit': 'BLUE', 'role': 'SCA Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
    {'sap': 'SCA1078', 'name': 'Kyle Oboe', 'unit': 'ORANGE', 'role': 'SCA Days', 'week1': [1, 2], 'week2': [5, 6], 'week3': [0, 4]},
]

def main():
    print("\n" + "="*70)
    print("DAY SHIFT PATTERN IMPORT - 3-WEEK REPEATING CYCLE")
    print("="*70)
    
    # Get day shift types
    try:
        scw_day_shift = ShiftType.objects.get(name='DAY_SENIOR')
        sca_day_shift = ShiftType.objects.get(name='DAY_ASSISTANT')
    except ShiftType.DoesNotExist:
        print("❌ ERROR: Day shift types not found!")
        return
    
    print(f"\n✅ Using shift types:")
    print(f"   SCW: {scw_day_shift.get_name_display()} ({scw_day_shift.start_time} - {scw_day_shift.end_time})")
    print(f"   SCA: {sca_day_shift.get_name_display()} ({sca_day_shift.start_time} - {sca_day_shift.end_time})")
    
    # Delete existing day shifts
    print(f"\n🗑️  Deleting existing day shifts...")
    deleted_count = Shift.objects.filter(shift_type__in=[scw_day_shift, sca_day_shift]).delete()[0]
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
    
    print(f"\n📊 Processing {len(DAY_SHIFT_PATTERN)} day staff members...")
    
    for staff_pattern in DAY_SHIFT_PATTERN:
        try:
            # Get user
            user = User.objects.get(sap=staff_pattern['sap'])
            stats['staff_processed'] += 1
            
            # Get unit
            unit = Unit.objects.get(name=staff_pattern['unit'])
            
            # Determine shift type based on role
            # Note: All regular SCWs and SCAs use DAY_ASSISTANT shift type
            # Only SSCWs (Senior Social Care Workers) would use DAY_SENIOR
            shift_type = sca_day_shift
            
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
            
            if stats['staff_processed'] % 10 == 0:
                print(f"   Processed: {stats['staff_processed']}/{len(DAY_SHIFT_PATTERN)} staff...")
                
        except User.DoesNotExist:
            print(f"   ⚠️  WARNING: User {staff_pattern['sap']} not found - skipping")
            stats['errors'] += 1
        except Exception as e:
            print(f"   ❌ ERROR processing {staff_pattern['sap']}: {e}")
            stats['errors'] += 1
    
    print(f"\n{'='*70}")
    print(f"IMPORT COMPLETE!")
    print(f"{'='*70}")
    print(f"✅ Staff processed: {stats['staff_processed']}/{len(DAY_SHIFT_PATTERN)}")
    print(f"✅ Shifts created: {stats['created']}")
    if stats['errors'] > 0:
        print(f"⚠️  Errors: {stats['errors']}")
    
    # Verify with Frank Garcia
    print(f"\n{'='*70}")
    print(f"VERIFICATION: Frank Garcia (SCW1006)")
    print(f"{'='*70}")
    
    try:
        frank = User.objects.get(sap='SCW1006')
        verify_start = datetime(2025, 11, 30).date()
        verify_end = datetime(2025, 12, 20).date()
        
        frank_shifts = Shift.objects.filter(
            user=frank,
            date__range=[verify_start, verify_end]
        ).order_by('date')
        
        print(f"Expected pattern: Week1=[FRI,SAT], Week2=[SUN,THU], Week3=[MON,TUE]")
        print(f"Actual shifts in Nov 30 - Dec 20:")
        
        for week_num in range(3):
            week_start = verify_start + timedelta(weeks=week_num)
            week_end = week_start + timedelta(days=6)
            week_shifts = [s for s in frank_shifts if week_start <= s.date <= week_end]
            
            print(f"\n  Week {week_num + 1} ({week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}):")
            for shift in week_shifts:
                print(f"    {shift.date.strftime('%a %b %d')}: {shift.shift_type.get_name_display()}")
        
        print(f"\n  Total: {frank_shifts.count()} shifts (Expected: 6)")
        
        if frank_shifts.count() == 6:
            print(f"\n✅ VERIFICATION PASSED!")
        else:
            print(f"\n⚠️  WARNING: Shift count mismatch!")
            
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
    
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    main()
