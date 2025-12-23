#!/usr/bin/env python
"""
Implement Orchard Grove 3-week rotation using existing staff mapped by role.
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

from scheduling.models import CareHome, Unit, User, Shift, ShiftType, Role

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
    print("🏥 Implementing Orchard Grove 3-Week Rotation (Using Existing Staff)")
    print("=" * 70)
    
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
    
    # Get roles
    sscw_role = Role.objects.get(name='SSCW')
    sscwn_role = Role.objects.get(name='SSCWN')
    sm_role = Role.objects.get(name='SM')
    scw_role = Role.objects.get(name='SCW')
    scwn_role = Role.objects.get(name='SCWN')
    sca_role = Role.objects.get(name='SCA')
    scan_role = Role.objects.get(name='SCAN')
    
    # Get OG units and staff
    og_units = Unit.objects.filter(care_home=og)
    
    # Define pattern templates for each role
    # SSCW patterns (9 staff, 3 shifts/week, 35hrs)
    sscw_patterns = [
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
    ]
    
    # SSCWN patterns (8 staff, 3 shifts/week, 35hrs)
    sscwn_patterns = [
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
    ]
    
    # SM patterns (1 staff, Mon-Fri)
    sm_patterns = [
        {'week1': parse_days('mon tue wed thu fri'), 'week2': parse_days('mon tue wed thu fri'), 'week3': parse_days('mon tue wed thu fri')},
    ]
    
    # SCA patterns - mix of 24hrs (2 shifts/week) and 35hrs (3 shifts/week)
    # 22 staff at 24hrs, 30 staff at 35hrs
    sca_patterns_24 = [
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('mon tue'), 'week2': parse_days('sat sun'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('mon tue'), 'week2': parse_days('sat sun'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('mon tue'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('mon tue'), 'week3': parse_days('mon tue')},
    ]
    
    sca_patterns_35 = [
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
        {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')},
        {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')},
        {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('mon tue wed'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('mon tue wed'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('mon tue wed'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('mon tue wed'), 'week3': parse_days('mon tue wed')},
    ]
    
    # SCW patterns - 9 at 35hrs, 18 at 24hrs
    scw_patterns_35 = [
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
    ]
    
    scw_patterns_24 = [
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
    ]
    
    # SCAN patterns - 32 at 24hrs, 35 at 35hrs
    scan_patterns_24 = [
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('mon tue'), 'week3': parse_days('thu fri')},
    ]
    
    scan_patterns_35 = [
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
        {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')},
        {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')},
        {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')},
        {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')},
        {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('wed thu fri')},
    ]
    
    # SCWN patterns - 7 at 35hrs, 7 at 24hrs
    scwn_patterns_35 = [
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('thu fri sat')},
    ]
    
    scwn_patterns_24 = [
        {'week1': parse_days('sun mon'), 'week2': parse_days('sun mon'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('sun mon'), 'week2': parse_days('sun mon'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('fri sat'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('wed thu'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('wed thu'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('wed thu'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
    ]
    
    # Generate shifts for full year + 2026
    start_date = datetime(2025, 1, 1).date()
    end_date = datetime(2026, 12, 31).date()
    # Cycle must start on a Sunday to keep weeks aligned
    # Jan 1, 2025 is Wednesday, so go back to previous Sunday (Dec 29, 2024)
    cycle_start = datetime(2024, 12, 29).date()
    
    total_shifts = 0
    
    with transaction.atomic():
        # Clear existing OG shifts
        existing = Shift.objects.filter(unit__in=og_units).count()
        if existing > 0:
            Shift.objects.filter(unit__in=og_units).delete()
            print(f"✓ Cleared {existing} existing shifts")
        
        # Track used staff per day
        used_staff = set()
        
        # Assign patterns to staff and generate shifts
        role_configs = [
            (sscw_role, sscw_patterns, day_senior, 'DAY_0800_2000', 'SSCW'),
            (sscwn_role, sscwn_patterns, night_senior, 'NIGHT_2000_0800', 'SSCWN'),
            (sm_role, sm_patterns, admin, 'DAY_0800_2000', 'SM'),
            (sca_role, sca_patterns_24 + sca_patterns_35, day_assistant, 'DAY_0800_2000', 'SCA'),
            (scw_role, scw_patterns_35 + scw_patterns_24, day_assistant, 'DAY_0800_2000', 'SCW'),
            (scan_role, scan_patterns_24 + scan_patterns_35, night_assistant, 'NIGHT_2000_0800', 'SCAN'),
            (scwn_role, scwn_patterns_35 + scwn_patterns_24, night_assistant, 'NIGHT_2000_0800', 'SCWN'),
        ]
        
        for role, patterns, shift_type, shift_pattern, role_name in role_configs:
            staff_list = list(User.objects.filter(unit__in=og_units, role=role, is_active=True).order_by('sap'))
            category_shifts = 0
            
            for i, staff_member in enumerate(staff_list):
                if i >= len(patterns):
                    print(f"  ⚠ Warning: More {role_name} staff ({len(staff_list)}) than patterns ({len(patterns)})")
                    break
                
                pattern = patterns[i]
                
                current_date = start_date
                while current_date <= end_date:
                    if should_work(pattern, current_date, cycle_start):
                        key = (staff_member.pk, current_date, shift_type.pk)
                        if key in used_staff:
                            current_date += timedelta(days=1)
                            continue
                        
                        Shift.objects.create(
                            user=staff_member,
                            unit=staff_member.unit,
                            date=current_date,
                            shift_type=shift_type,
                            shift_pattern=shift_pattern,
                            status='CONFIRMED'
                        )
                        used_staff.add(key)
                        category_shifts += 1
                        total_shifts += 1
                    
                    current_date += timedelta(days=1)
            
            print(f"  ✓ {role_name}: {len(staff_list)} staff, {category_shifts} shifts")
    
    print("=" * 70)
    print(f"✓ Created {total_shifts} shifts for Orchard Grove")
    print(f"✓ {og.name} fully implemented with 3-week rotation")
    print("\n🎉 Orchard Grove complete!")

if __name__ == '__main__':
    main()
