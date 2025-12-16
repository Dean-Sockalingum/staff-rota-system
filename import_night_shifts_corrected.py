#!/usr/bin/env python3
"""
Import Night Shift Pattern - CORRECTED 3-Week Repeating Cycle
Based on exact spreadsheet data with verified totals:
Week 1: 27, 27, 40, 27, 27, 27, 27
Week 2: 27, 27, 27, 27, 40, 27, 27
Week 3: 27, 27, 13, 27, 41, 40, 27
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift, ShiftType, Unit
from datetime import datetime, timedelta
from django.utils import timezone

# Days: 0=SUN, 1=MON, 2=TUE, 3=WED, 4=THU, 5=FRI, 6=SAT

# Pattern Group 1: SUN/MON/TUE → THU/FRI/SAT → WED/THU/FRI (27 staff)
PATTERN_1 = [
    {'sap': 'SCW1080', 'name': 'Jack Henderson', 'unit': 'DEMENTIA', 'role': 'SCW(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCW1081', 'name': 'Karen Watson', 'unit': 'BLUE', 'role': 'SCW(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCW1082', 'name': 'Liam Brooks', 'unit': 'ORANGE', 'role': 'SCW(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCW1083', 'name': 'Mia Bryant', 'unit': 'GREEN', 'role': 'SCW(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1084', 'name': 'Olivia Jones', 'unit': 'DEMENTIA', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1085', 'name': 'Peter Johnson', 'unit': 'BLUE', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1086', 'name': 'Quinn Oboe', 'unit': 'ORANGE', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1087', 'name': 'Rachel Griffin', 'unit': 'GREEN', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1088', 'name': 'Noah Coleman', 'unit': 'VIOLET', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1090', 'name': 'Sam Foster', 'unit': 'ROSE', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1091', 'name': 'Tina Bailey', 'unit': 'GRAPE', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1092', 'name': 'Uma Reed', 'unit': 'PEACH', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1093', 'name': 'Victor Kelly', 'unit': 'DEMENTIA', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1094', 'name': 'Nora Howard', 'unit': 'BLUE', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1095', 'name': 'Nora Gotyo', 'unit': 'ORANGE', 'role': 'SCA(N)', 'week1': [0,1,2], 'week2': [4,5,6], 'week3': [3,4,5]},
    {'sap': 'SCA1096', 'name': 'Wendy Barnes', 'unit': 'DEMENTIA', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1097', 'name': 'Xander Ross', 'unit': 'BLUE', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1098', 'name': 'Yara Henderson', 'unit': 'ORANGE', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1099', 'name': 'Zoe Peterson', 'unit': 'GREEN', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1100', 'name': 'Aaron Cook', 'unit': 'VIOLET', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1101', 'name': 'Bella Price', 'unit': 'ROSE', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1102', 'name': 'Ben Nevis', 'unit': 'GRAPE', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1103', 'name': 'Chloe Earlie', 'unit': 'PEACH', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1104', 'name': 'Daniel Cohen', 'unit': 'VIOLET', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1105', 'name': 'Ella Fitzgerald', 'unit': 'ROSE', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1106', 'name': 'Finn Barr', 'unit': 'GRAPE', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
    {'sap': 'SCA1107', 'name': 'Gemma Arthur', 'unit': 'PEACH', 'role': 'SCA(N)', 'week1': [0,1], 'week2': [5,6], 'week3': [3,4]},
]

# Pattern Group 2: THU/FRI/SAT → TUE/WED/THU → SUN/MON/TUE (27 staff)
PATTERN_2 = [
    {'sap': 'SCW1108', 'name': 'Blessing Oghoa', 'unit': 'VIOLET', 'role': 'SCW(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCW1109', 'name': 'Peace Sibbald', 'unit': 'ROSE', 'role': 'SCW(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCW1110', 'name': 'JoJo McArthur', 'unit': 'GRAPE', 'role': 'SCW(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCW1111', 'name': 'Pedro Wallace', 'unit': 'PEACH', 'role': 'SCW(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1112', 'name': 'Caleb King', 'unit': 'VIOLET', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1113', 'name': 'Diana Doors', 'unit': 'ROSE', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1114', 'name': 'Ethan Hawke', 'unit': 'GRAPE', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1115', 'name': 'Fiona Bruce', 'unit': 'PEACH', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1116', 'name': 'George Harrison', 'unit': 'DEMENTIA', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1117', 'name': 'Hannah Barbera', 'unit': 'BLUE', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1118', 'name': 'Mark Lewis', 'unit': 'ORANGE', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1119', 'name': 'Isaac Robinson', 'unit': 'GREEN', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1120', 'name': 'Julia Walker', 'unit': 'DEMENTIA', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1121', 'name': 'Kyle Young', 'unit': 'BLUE', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1122', 'name': 'Luna Allen', 'unit': 'ORANGE', 'role': 'SCA(N)', 'week1': [4,5,6], 'week2': [2,3,4], 'week3': [0,1,2]},
    {'sap': 'SCA1123', 'name': 'Oscar Wright', 'unit': 'VIOLET', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1124', 'name': 'Piper Scott', 'unit': 'ROSE', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1125', 'name': 'Ryan Torres', 'unit': 'GRAPE', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1126', 'name': 'Nathan Nguyen', 'unit': 'PEACH', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1127', 'name': 'Sophia Hill', 'unit': 'DEMENTIA', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1128', 'name': 'Tyler Green', 'unit': 'BLUE', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1129', 'name': 'Ursula Adams', 'unit': 'ORANGE', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1130', 'name': 'Vincent Baker', 'unit': 'GREEN', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1131', 'name': 'Willow Nelson', 'unit': 'DEMENTIA', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1132', 'name': 'Wyatt Earp', 'unit': 'BLUE', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1133', 'name': 'Xenia Warrior', 'unit': 'ORANGE', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
    {'sap': 'SCA1134', 'name': 'Jacqui Swan', 'unit': 'GRAPE', 'role': 'SCA(N)', 'week1': [5,6], 'week2': [3,4], 'week3': [0,1]},
]

# Pattern Group 3: TUE/WED/THU → SUN/MON/TUE → THU/FRI/SAT or FRI/SAT (27 staff)
PATTERN_3 = [
    {'sap': 'SCW1135', 'name': 'Harry Hall', 'unit': 'ORANGE', 'role': 'SCW(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCW1136', 'name': 'Isabel Rivera', 'unit': 'GREEN', 'role': 'SCW(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCW1137', 'name': 'Jacob Campbell', 'unit': 'VIOLET', 'role': 'SCW(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCW1138', 'name': 'Katie Mitchell', 'unit': 'ROSE', 'role': 'SCW(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCW1139', 'name': 'Leo Carter', 'unit': 'DEMENTIA', 'role': 'SCW(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCW1140', 'name': 'Megan Roberts', 'unit': 'BLUE', 'role': 'SCW(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCA1141', 'name': 'Poppy Saeed', 'unit': 'DEMENTIA', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1142', 'name': 'Quentin Tarant', 'unit': 'BLUE', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1143', 'name': 'Ruby Rubia', 'unit': 'ORANGE', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1144', 'name': 'Sebastian Coen', 'unit': 'GREEN', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1145', 'name': 'Taylor Swifty', 'unit': 'VIOLET', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1146', 'name': 'Janice Evans', 'unit': 'ROSE', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1147', 'name': 'Victor Turner', 'unit': 'GRAPE', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1148', 'name': 'Zoe Cooper', 'unit': 'PEACH', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1149', 'name': 'Adam Phillips', 'unit': 'GRAPE', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1150', 'name': 'Beth Aimes', 'unit': 'PEACH', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1151', 'name': 'Natasha Kaplinski', 'unit': 'DEMENTIA', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1152', 'name': 'Abby Rhodes', 'unit': 'ROSE', 'role': 'SCA(N)', 'week1': [2,3,4], 'week2': [0,1,2], 'week3': [4,5,6]},
    {'sap': 'SCA1153', 'name': 'David Morris', 'unit': 'GREEN', 'role': 'SCA(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCA1154', 'name': 'Emily Rogers', 'unit': 'VIOLET', 'role': 'SCA(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCA1155', 'name': 'Frank Cox', 'unit': 'ROSE', 'role': 'SCA(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCA1156', 'name': 'Grace Ward', 'unit': 'GRAPE', 'role': 'SCA(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCA1157', 'name': 'Henry Gray', 'unit': 'PEACH', 'role': 'SCA(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCA1158', 'name': 'Ivy Bell', 'unit': 'DEMENTIA', 'role': 'SCA(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCA1159', 'name': 'Angela Ripton', 'unit': 'BLUE', 'role': 'SCA(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCA1160', 'name': 'Kyle Son Ji', 'unit': 'ORANGE', 'role': 'SCA(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
    {'sap': 'SCA1161', 'name': 'Precious Richards', 'unit': 'ROSE', 'role': 'SCA(N)', 'week1': [2,3], 'week2': [0,1], 'week3': [5,6]},
]

# Combine all patterns
NIGHT_SHIFT_PATTERN = PATTERN_1 + PATTERN_2 + PATTERN_3

def main():
    print("\n" + "="*70)
    print("NIGHT SHIFT PATTERN IMPORT - CORRECTED 3-WEEK CYCLE")
    print("="*70)
    print(f"Expected totals:")
    print(f"  Week 1: 27, 27, 40, 27, 27, 27, 27")
    print(f"  Week 2: 27, 27, 27, 27, 40, 27, 27")
    print(f"  Week 3: 27, 27, 13, 27, 41, 40, 27")
    
    # Get night shift types
    try:
        scw_night_shift = ShiftType.objects.get(name='NIGHT_SENIOR')
        sca_night_shift = ShiftType.objects.get(name='NIGHT_ASSISTANT')
    except ShiftType.DoesNotExist:
        print("❌ ERROR: Night shift types not found!")
        return
    
    print(f"\n✅ Using shift types:")
    print(f"   SCW(N): {scw_night_shift.get_name_display()} ({scw_night_shift.start_time} - {scw_night_shift.end_time})")
    print(f"   SCA(N): {sca_night_shift.get_name_display()} ({sca_night_shift.start_time} - {sca_night_shift.end_time})")
    
    # Delete existing night shifts (excluding SSCW(N) managers)
    print(f"\n🗑️  Deleting existing night shifts...")
    night_saps = [p['sap'] for p in NIGHT_SHIFT_PATTERN]
    night_users = User.objects.filter(sap__in=night_saps)
    deleted_count = Shift.objects.filter(user__in=night_users).delete()[0]
    print(f"   Deleted: {deleted_count} shifts")
    
    # Start date - Nov 30, 2025 (Sunday)
    start_date = datetime(2025, 11, 30).date()
    print(f"\n📅 Starting from: {start_date.strftime('%Y-%m-%d')} (Sunday)")
    
    # Import for 1 year (52 weeks)
    total_weeks = 52
    total_cycles = total_weeks // 3
    
    print(f"   Generating: {total_weeks} weeks ({total_cycles} complete 3-week cycles)")
    
    stats = {
        'created': 0,
        'errors': 0,
        'staff_processed': 0
    }
    
    print(f"\n📊 Processing {len(NIGHT_SHIFT_PATTERN)} night staff members...")
    
    for staff_pattern in NIGHT_SHIFT_PATTERN:
        try:
            # Get user
            user = User.objects.get(sap=staff_pattern['sap'])
            stats['staff_processed'] += 1
            
            # Get unit
            unit = Unit.objects.get(name=staff_pattern['unit'])
            
            # Determine shift type (all use NIGHT_ASSISTANT for regular night staff)
            shift_type = sca_night_shift
            
            # Generate shifts for all cycles
            for cycle in range(total_cycles + 1):
                for week_num in range(3):
                    week_key = f'week{week_num + 1}'
                    if week_key not in staff_pattern:
                        continue
                    
                    week_offset = (cycle * 3) + week_num
                    if week_offset >= total_weeks:
                        break
                        
                    week_start = start_date + timedelta(weeks=week_offset)
                    
                    # Create shifts for this week
                    for day_of_week in staff_pattern[week_key]:
                        shift_date = week_start + timedelta(days=day_of_week)
                        
                        Shift.objects.create(
                            user=user,
                            date=shift_date,
                            shift_type=shift_type,
                            unit=unit,
                            status='SCHEDULED'
                        )
                        stats['created'] += 1
            
            if stats['staff_processed'] % 10 == 0:
                print(f"   Processed: {stats['staff_processed']}/{len(NIGHT_SHIFT_PATTERN)} staff...")
                
        except User.DoesNotExist:
            print(f"   ⚠️  WARNING: User {staff_pattern['sap']} not found - skipping")
            stats['errors'] += 1
        except Exception as e:
            print(f"   ❌ ERROR processing {staff_pattern['sap']}: {e}")
            stats['errors'] += 1
    
    print(f"\n{'='*70}")
    print(f"IMPORT COMPLETE!")
    print(f"{'='*70}")
    print(f"✅ Staff processed: {stats['staff_processed']}/{len(NIGHT_SHIFT_PATTERN)}")
    print(f"✅ Shifts created: {stats['created']}")
    if stats['errors'] > 0:
        print(f"⚠️  Errors: {stats['errors']}")
    
    # Verify counts match expected totals
    print(f"\n{'='*70}")
    print(f"VERIFICATION: Checking Totals")
    print(f"{'='*70}")
    
    days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    expected = [
        [27, 27, 40, 27, 27, 27, 27],
        [27, 27, 27, 27, 40, 27, 27],
        [27, 27, 13, 27, 41, 40, 27]
    ]
    
    all_match = True
    for week in range(3):
        week_start = start_date + timedelta(weeks=week)
        print(f"\nWeek {week+1} ({week_start.strftime('%b %d')} - {(week_start + timedelta(days=6)).strftime('%b %d')}):")
        print(f"  Expected: " + " ".join(f"{days[i]:>3s}={expected[week][i]:>2d}" for i in range(7)))
        
        actual = []
        for day in range(7):
            d = week_start + timedelta(days=day)
            count = Shift.objects.filter(
                date=d,
                shift_type=sca_night_shift
            ).count()
            actual.append(count)
        
        print(f"  Actual:   " + " ".join(f"{days[i]:>3s}={actual[i]:>2d}" for i in range(7)))
        
        if actual != expected[week]:
            print(f"  ⚠️  MISMATCH!")
            all_match = False
        else:
            print(f"  ✅ MATCH!")
    
    if all_match:
        print(f"\n✅ ALL WEEKS VERIFIED - PATTERNS CORRECT!")
    else:
        print(f"\n⚠️  SOME WEEKS DON'T MATCH - CHECK PATTERNS!")
    
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    main()
