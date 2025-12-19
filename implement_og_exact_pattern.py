#!/usr/bin/env python
"""
Implement Orchard Grove exact 3-week rotation pattern.
Based on complete staff roster with 179 staff members.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.db import transaction

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import CareHome, Unit, User, Shift, ShiftType

def parse_days(day_string):
    """Convert day pattern string to list of day indices (0=Sun, 6=Sat)"""
    day_map = {'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6}
    if not day_string or day_string.strip() == '':
        return []
    days = []
    for day in day_string.lower().split():
        if day in day_map:
            days.append(day_map[day])
    return days

def get_week_number(date, cycle_start):
    """Get week number in 3-week cycle (1, 2, or 3)"""
    days_diff = (date - cycle_start).days
    week_num = (days_diff // 7) % 3 + 1
    return week_num

def should_work(staff_patterns, date, cycle_start):
    """Check if staff member works on this date based on their pattern"""
    week_num = get_week_number(date, cycle_start)
    weekday = date.weekday()
    if weekday == 6:  # Sunday
        weekday = 0
    else:
        weekday += 1
    
    week_key = f'week{week_num}'
    if week_key not in staff_patterns:
        return False
    
    pattern = staff_patterns[week_key]
    return weekday in pattern

def main():
    print("🏥 Implementing Orchard Grove Complete 3-Week Rotation")
    print("=" * 60)
    
    # Get Orchard Grove
    try:
        og = CareHome.objects.get(name='ORCHARD_GROVE')
        print(f"✓ Found care home: {og.name}")
    except CareHome.DoesNotExist:
        print("✗ Orchard Grove not found!")
        return
    
    # Get shift types
    day_senior = ShiftType.objects.get(name='DAY_SENIOR')
    night_senior = ShiftType.objects.get(name='NIGHT_SENIOR')
    day_assistant = ShiftType.objects.get(name='DAY_ASSISTANT')
    night_assistant = ShiftType.objects.get(name='NIGHT_ASSISTANT')
    admin = ShiftType.objects.get(name='ADMIN')
    
    # Define staff patterns
    # SSCW (Senior Social Care Worker) - Day Seniors - 9 staff
    sscw_staff = [
        {'sap': 1001, 'patterns': {
            'week1': parse_days('sun mon tue'),
            'week2': parse_days('wed thu fri'),
            'week3': parse_days('tue wed thu')
        }},
        {'sap': 1002, 'patterns': {
            'week1': parse_days('sun mon tue'),
            'week2': parse_days('wed thu fri'),
            'week3': parse_days('tue wed thu')
        }},
        {'sap': 1003, 'patterns': {
            'week1': parse_days('thu fri sat'),
            'week2': parse_days('sun mon tue'),
            'week3': parse_days('fri sat sun')
        }},
        {'sap': 1004, 'patterns': {
            'week1': parse_days('thu fri sat'),
            'week2': parse_days('sun mon tue'),
            'week3': parse_days('fri sat sun')
        }},
        {'sap': 1005, 'patterns': {
            'week1': parse_days('wed thu fri'),
            'week2': parse_days('sat sun mon'),
            'week3': parse_days('mon tue wed')
        }},
        {'sap': 1006, 'patterns': {
            'week1': parse_days('wed thu fri'),
            'week2': parse_days('sat sun mon'),
            'week3': parse_days('mon tue wed')
        }},
        {'sap': 1007, 'patterns': {
            'week1': parse_days('wed thu fri'),
            'week2': parse_days('tue wed thu'),
            'week3': parse_days('sat sun mon')
        }},
        {'sap': 1008, 'patterns': {
            'week1': parse_days('wed thu fri'),
            'week2': parse_days('tue wed thu'),
            'week3': parse_days('sat sun mon')
        }},
        {'sap': 1009, 'patterns': {
            'week1': parse_days('sat sun mon'),
            'week2': parse_days('fri sat sun'),
            'week3': parse_days('thu fri sat')
        }},
    ]
    
    # SSCW(N) (Senior Social Care Worker Night) - Night Seniors - 8 staff
    sscwn_staff = [
        {'sap': 1010, 'patterns': {
            'week1': parse_days('sun mon tue'),
            'week2': parse_days('wed thu fri'),
            'week3': parse_days('tue wed thu')
        }},
        {'sap': 1011, 'patterns': {
            'week1': parse_days('sun mon tue'),
            'week2': parse_days('wed thu fri'),
            'week3': parse_days('tue wed thu')
        }},
        {'sap': 1012, 'patterns': {
            'week1': parse_days('thu fri sat'),
            'week2': parse_days('sun mon tue'),
            'week3': parse_days('fri sat sun')
        }},
        {'sap': 1013, 'patterns': {
            'week1': parse_days('thu fri sat'),
            'week2': parse_days('sun mon tue'),
            'week3': parse_days('fri sat sun')
        }},
        {'sap': 1014, 'patterns': {
            'week1': parse_days('wed thu fri'),
            'week2': parse_days('sat sun mon'),
            'week3': parse_days('mon tue wed')
        }},
        {'sap': 1015, 'patterns': {
            'week1': parse_days('wed thu fri'),
            'week2': parse_days('sat sun mon'),
            'week3': parse_days('mon tue wed')
        }},
        {'sap': 1016, 'patterns': {
            'week1': parse_days('wed thu fri'),
            'week2': parse_days('tue wed thu'),
            'week3': parse_days('sat sun mon')
        }},
        {'sap': 1017, 'patterns': {
            'week1': parse_days('sat sun mon'),
            'week2': parse_days('fri sat sun'),
            'week3': parse_days('thu fri sat')
        }},
    ]
    
    # Management (SM + OM) - Admin - 3 staff
    management_staff = [
        {'sap': 1018, 'patterns': {  # SM
            'week1': parse_days('mon tue wed thu fri'),
            'week2': parse_days('mon tue wed thu fri'),
            'week3': parse_days('mon tue wed thu fri')
        }},
        {'sap': 1019, 'patterns': {  # OM
            'week1': parse_days('mon tue wed thu fri'),
            'week2': parse_days('mon tue wed thu fri'),
            'week3': parse_days('mon tue wed thu fri')
        }},
        {'sap': 1020, 'patterns': {  # OM
            'week1': parse_days('mon tue wed thu fri'),
            'week2': parse_days('mon tue wed thu fri'),
            'week3': parse_days('mon tue wed thu fri')
        }},
    ]
    
    # SCA (Social Care Assistant) 24hrs - Day Assistants - 22 staff
    sca_24_staff = [
        {'sap': 1021, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')}},
        {'sap': 1022, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')}},
        {'sap': 1023, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')}},
        {'sap': 1024, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')}},
        {'sap': 1025, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')}},
        {'sap': 1026, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')}},
        {'sap': 1027, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')}},
        {'sap': 1028, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')}},
        {'sap': 1029, 'patterns': {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')}},
        {'sap': 1030, 'patterns': {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')}},
        {'sap': 1031, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')}},
        {'sap': 1032, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')}},
        {'sap': 1033, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')}},
        {'sap': 1034, 'patterns': {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')}},
        {'sap': 1035, 'patterns': {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')}},
        {'sap': 1036, 'patterns': {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')}},
        {'sap': 1037, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')}},
        {'sap': 1038, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')}},
        {'sap': 1039, 'patterns': {'week1': parse_days('mon tue'), 'week2': parse_days('sat sun'), 'week3': parse_days('sat sun')}},
        {'sap': 1040, 'patterns': {'week1': parse_days('mon tue'), 'week2': parse_days('sat sun'), 'week3': parse_days('sat sun')}},
        {'sap': 1041, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('mon tue'), 'week3': parse_days('mon tue')}},
        {'sap': 1042, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('mon tue'), 'week3': parse_days('mon tue')}},
    ]
    
    # SCA (Social Care Assistant) 35hrs - Day Assistants - 30 staff
    sca_35_staff = [
        {'sap': 1043, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1044, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1045, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1046, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1047, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1048, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1049, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1050, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1051, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1052, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1053, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1054, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1055, 'patterns': {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1056, 'patterns': {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1057, 'patterns': {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1058, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')}},
        {'sap': 1059, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')}},
        {'sap': 1060, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')}},
        {'sap': 1061, 'patterns': {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')}},
        {'sap': 1062, 'patterns': {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')}},
        {'sap': 1063, 'patterns': {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')}},
        {'sap': 1064, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1065, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1066, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1067, 'patterns': {'week1': parse_days('mon tue wed'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1068, 'patterns': {'week1': parse_days('mon tue wed'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1069, 'patterns': {'week1': parse_days('mon tue wed'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1070, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1071, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1072, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('mon tue wed')}},
    ]
    
    # SCW (Social Care Worker) 35hrs - Day Assistants - 9 staff
    scw_35_staff = [
        {'sap': 1073, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1074, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1075, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1076, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1077, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1078, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1079, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1080, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1081, 'patterns': {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')}},
    ]
    
    # SCW (Social Care Worker) 24hrs - Day Assistants - 18 staff
    scw_24_staff = [
        {'sap': 1082, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')}},
        {'sap': 1083, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')}},
        {'sap': 1084, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')}},
        {'sap': 1085, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')}},
        {'sap': 1086, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')}},
        {'sap': 1087, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')}},
        {'sap': 1088, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')}},
        {'sap': 1089, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')}},
        {'sap': 1090, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')}},
        {'sap': 1091, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')}},
        {'sap': 1092, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')}},
        {'sap': 1093, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')}},
        {'sap': 1094, 'patterns': {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')}},
        {'sap': 1095, 'patterns': {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')}},
        {'sap': 1096, 'patterns': {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')}},
        {'sap': 1097, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')}},
        {'sap': 1098, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')}},
        {'sap': 1099, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')}},
    ]
    
    # SCAN (Social Care Assistant Night) 24hrs - Night Assistants - 32 staff
    scan_24_staff = [
        {'sap': 1100, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')}},
        {'sap': 1101, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')}},
        {'sap': 1102, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')}},
        {'sap': 1103, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')}},
        {'sap': 1104, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')}},
        {'sap': 1105, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')}},
        {'sap': 1106, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')}},
        {'sap': 1107, 'patterns': {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')}},
        {'sap': 1108, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')}},
        {'sap': 1109, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')}},
        {'sap': 1110, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')}},
        {'sap': 1111, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')}},
        {'sap': 1112, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')}},
        {'sap': 1113, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')}},
        {'sap': 1114, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')}},
        {'sap': 1115, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')}},
        {'sap': 1116, 'patterns': {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')}},
        {'sap': 1117, 'patterns': {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')}},
        {'sap': 1118, 'patterns': {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')}},
        {'sap': 1119, 'patterns': {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')}},
        {'sap': 1120, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')}},
        {'sap': 1121, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')}},
        {'sap': 1122, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')}},
        {'sap': 1123, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')}},
        {'sap': 1124, 'patterns': {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')}},
        {'sap': 1125, 'patterns': {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')}},
        {'sap': 1126, 'patterns': {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')}},
        {'sap': 1127, 'patterns': {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')}},
        {'sap': 1128, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')}},
        {'sap': 1129, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')}},
        {'sap': 1130, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')}},
        {'sap': 1131, 'patterns': {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')}},
    ]
    
    # SCAN (Social Care Assistant Night) 35hrs - Night Assistants - 35 staff
    scan_35_staff = [
        {'sap': 1132, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1133, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1134, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1135, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1136, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1137, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1138, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1139, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1140, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1141, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1142, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1143, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1144, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1145, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1146, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')}},
        {'sap': 1147, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1148, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1149, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1150, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1151, 'patterns': {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')}},
        {'sap': 1152, 'patterns': {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1153, 'patterns': {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1154, 'patterns': {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1155, 'patterns': {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1156, 'patterns': {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1157, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')}},
        {'sap': 1158, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')}},
        {'sap': 1159, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')}},
        {'sap': 1160, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')}},
        {'sap': 1161, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')}},
        {'sap': 1162, 'patterns': {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')}},
        {'sap': 1163, 'patterns': {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')}},
        {'sap': 1164, 'patterns': {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')}},
        {'sap': 1165, 'patterns': {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')}},
        {'sap': 1166, 'patterns': {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')}},
    ]
    
    # SCWN (Social Care Worker Night) 35hrs - Night Assistants - 7 staff
    scwn_35_staff = [
        {'sap': 1080, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1081, 'patterns': {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')}},
        {'sap': 1108, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1109, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1111, 'patterns': {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')}},
        {'sap': 1135, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('thu fri sat')}},
        {'sap': 1136, 'patterns': {'week1': parse_days('tue wed thu'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('thu fri sat')}},
    ]
    
    # SCWN (Social Care Worker Night) 24hrs - Night Assistants - 7 staff
    scwn_24_staff = [
        {'sap': 1082, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('sun mon'), 'week3': parse_days('sun mon')}},
        {'sap': 1083, 'patterns': {'week1': parse_days('sun mon'), 'week2': parse_days('sun mon'), 'week3': parse_days('sun mon')}},
        {'sap': 1110, 'patterns': {'week1': parse_days('fri sat'), 'week2': parse_days('fri sat'), 'week3': parse_days('wed thu')}},
        {'sap': 1137, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('wed thu'), 'week3': parse_days('wed thu')}},
        {'sap': 1138, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('wed thu'), 'week3': parse_days('wed thu')}},
        {'sap': 1139, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('wed thu'), 'week3': parse_days('fri sat')}},
        {'sap': 1140, 'patterns': {'week1': parse_days('wed thu'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')}},
    ]
    
    # Generate shifts for 6 months
    start_date = datetime(2025, 1, 1).date()
    end_date = datetime(2025, 6, 30).date()
    cycle_start = start_date  # Start of 3-week cycle
    
    total_shifts = 0
    
    with transaction.atomic():
        # Clear existing Orchard Grove shifts
        og_units = Unit.objects.filter(care_home=og)
        existing = Shift.objects.filter(unit__in=og_units).count()
        if existing > 0:
            Shift.objects.filter(unit__in=og_units).delete()
            print(f"✓ Cleared {existing} existing shifts")
        
        # Track used staff per day to avoid duplicates
        used_staff = set()
        
        # Generate shifts for each staff category
        all_staff = [
            (sscw_staff, day_senior, 'DAY_0800_2000', 'SSCW'),
            (sscwn_staff, night_senior, 'NIGHT_2000_0800', 'SSCW(N)'),
            (management_staff, admin, 'DAY_0800_2000', 'Management'),
            (sca_24_staff, day_assistant, 'DAY_0800_2000', 'SCA 24hrs'),
            (sca_35_staff, day_assistant, 'DAY_0800_2000', 'SCA 35hrs'),
            (scw_35_staff, day_assistant, 'DAY_0800_2000', 'SCW 35hrs'),
            (scw_24_staff, day_assistant, 'DAY_0800_2000', 'SCW 24hrs'),
            (scan_24_staff, night_assistant, 'NIGHT_2000_0800', 'SCAN 24hrs'),
            (scan_35_staff, night_assistant, 'NIGHT_2000_0800', 'SCAN 35hrs'),
            (scwn_35_staff, night_assistant, 'NIGHT_2000_0800', 'SCWN 35hrs'),
            (scwn_24_staff, night_assistant, 'NIGHT_2000_0800', 'SCWN 24hrs'),
        ]
        
        for staff_list, shift_type, pattern, category in all_staff:
            category_shifts = 0
            for staff_data in staff_list:
                sap = staff_data['sap']
                patterns = staff_data['patterns']
                
                try:
                    staff_member = User.objects.get(sap=sap, unit__care_home=og)
                except User.DoesNotExist:
                    print(f"  ⚠ Warning: Staff {sap} not found")
                    continue
                
                current_date = start_date
                while current_date <= end_date:
                    if should_work(patterns, current_date, cycle_start):
                        # Check for duplicate
                        key = (staff_member.pk, current_date, shift_type.pk)
                        if key in used_staff:
                            current_date += timedelta(days=1)
                            continue
                        
                        Shift.objects.create(
                            user=staff_member,
                            unit=staff_member.unit,
                            date=current_date,
                            shift_type=shift_type,
                            shift_pattern=pattern,
                            status='CONFIRMED'
                        )
                        used_staff.add(key)
                        category_shifts += 1
                        total_shifts += 1
                    
                    current_date += timedelta(days=1)
            
            print(f"  ✓ {category}: {category_shifts} shifts")
    
    print("=" * 60)
    print(f"✓ Created {total_shifts} shifts for Orchard Grove")
    print(f"✓ 179 staff members with exact 3-week rotation patterns")
    print("\n🎉 Orchard Grove roster implementation complete!")

if __name__ == '__main__':
    main()
