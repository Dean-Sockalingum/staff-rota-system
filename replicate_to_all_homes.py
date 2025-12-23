#!/usr/bin/env python
"""
Replicate Orchard Grove staffing patterns to Riverside, Meadowburn, and Hawthorn House.
This will use existing staff in each home and apply the same 3-week rotation patterns.
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

def get_pattern_templates():
    """Get all pattern templates from Orchard Grove implementation"""
    
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
    
    # SM patterns (Mon-Fri)
    sm_patterns = [
        {'week1': parse_days('mon tue wed thu fri'), 'week2': parse_days('mon tue wed thu fri'), 'week3': parse_days('mon tue wed thu fri')},
    ]
    
    # SCA patterns - cycle through both 24hrs and 35hrs
    sca_patterns = [
        # 24hrs patterns
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        # 35hrs patterns
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
    ] * 6  # Repeat to cover more staff
    
    # SCW patterns - cycle through both 24hrs and 35hrs
    scw_patterns = [
        # 35hrs patterns
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        # 24hrs patterns
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
    ] * 4  # Repeat to cover more staff
    
    # SCAN patterns - cycle through both 24hrs and 35hrs  
    scan_patterns = [
        # 24hrs patterns
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        # 35hrs patterns
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
    ] * 8  # Repeat to cover more staff
    
    # SCWN patterns - cycle through both 24hrs and 35hrs
    scwn_patterns = [
        # 35hrs patterns
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('thu fri sat')},
        # 24hrs patterns
        {'week1': parse_days('sun mon'), 'week2': parse_days('sun mon'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('wed thu'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('fri sat'), 'week3': parse_days('wed thu')},
    ] * 3  # Repeat to cover more staff
    
    return {
        'SSCW': sscw_patterns,
        'SSCWN': sscwn_patterns,
        'SM': sm_patterns,
        'SCA': sca_patterns,
        'SCW': scw_patterns,
        'SCAN': scan_patterns,
        'SCWN': scwn_patterns,
    }

def implement_home(care_home_name):
    """Implement 3-week rotation for a care home"""
    print(f"\n🏥 Implementing {care_home_name}")
    print("=" * 70)
    
    try:
        home = CareHome.objects.get(name=care_home_name)
    except CareHome.DoesNotExist:
        print(f"✗ {care_home_name} not found!")
        return
    
    # Get shift types
    day_senior = ShiftType.objects.get(name='DAY_SENIOR')
    night_senior = ShiftType.objects.get(name='NIGHT_SENIOR')
    day_assistant = ShiftType.objects.get(name='DAY_ASSISTANT')
    night_assistant = ShiftType.objects.get(name='NIGHT_ASSISTANT')
    admin = ShiftType.objects.get(name='ADMIN')
    
    # Get roles
    roles = {
        'SSCW': Role.objects.get(name='SSCW'),
        'SSCWN': Role.objects.get(name='SSCWN'),
        'SM': Role.objects.get(name='SM'),
        'SCW': Role.objects.get(name='SCW'),
        'SCWN': Role.objects.get(name='SCWN'),
        'SCA': Role.objects.get(name='SCA'),
        'SCAN': Role.objects.get(name='SCAN'),
    }
    
    # Get units and pattern templates
    home_units = Unit.objects.filter(care_home=home)
    patterns = get_pattern_templates()
    
    # Generate shifts for full year 2025 + 2026
    start_date = datetime(2025, 1, 1).date()
    end_date = datetime(2026, 12, 31).date()
    # Cycle must start on a Sunday to keep weeks aligned
    # Jan 1, 2025 is Wednesday, so go back to previous Sunday (Dec 29, 2024)
    cycle_start = datetime(2024, 12, 29).date()
    
    total_shifts = 0
    
    with transaction.atomic():
        # Clear existing shifts
        existing = Shift.objects.filter(unit__in=home_units).count()
        if existing > 0:
            Shift.objects.filter(unit__in=home_units).delete()
            print(f"✓ Cleared {existing} existing shifts")
        
        # Track used staff per day
        used_staff = set()
        
        # Configure role assignments
        role_configs = [
            ('SSCW', day_senior, 'DAY_0800_2000'),
            ('SSCWN', night_senior, 'NIGHT_2000_0800'),
            ('SM', admin, 'DAY_0800_2000'),
            ('SCA', day_assistant, 'DAY_0800_2000'),
            ('SCW', day_assistant, 'DAY_0800_2000'),
            ('SCAN', night_assistant, 'NIGHT_2000_0800'),
            ('SCWN', night_assistant, 'NIGHT_2000_0800'),
        ]
        
        for role_name, shift_type, shift_pattern in role_configs:
            role = roles[role_name]
            role_patterns = patterns[role_name]
            staff_list = list(User.objects.filter(
                unit__in=home_units,
                role=role,
                is_active=True
            ).order_by('sap'))
            
            category_shifts = 0
            
            for i, staff_member in enumerate(staff_list):
                pattern = role_patterns[i % len(role_patterns)]  # Cycle through patterns
                
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
    
    print(f"✓ Created {total_shifts} shifts for {care_home_name}")
    return total_shifts

def main():
    print("🔄 Replicating Orchard Grove Patterns to Other Homes")
    print("=" * 70)
    
    homes_to_implement = ['RIVERSIDE', 'MEADOWBURN', 'HAWTHORN_HOUSE']
    
    for home_name in homes_to_implement:
        implement_home(home_name)
    
    print("\n" + "=" * 70)
    print("🎉 All homes implemented successfully!")
    print("\nVerifying compliance...")
    
    # Check compliance for all homes
    from datetime import date
    test_date = date(2025, 1, 15)
    
    for home_name in ['ORCHARD_GROVE'] + homes_to_implement:
        home = CareHome.objects.get(name=home_name)
        day_shifts = Shift.objects.filter(
            unit__care_home=home,
            date=test_date,
            shift_type__name__in=['DAY_SENIOR', 'DAY_ASSISTANT', 'ADMIN']
        )
        night_shifts = Shift.objects.filter(
            unit__care_home=home,
            date=test_date,
            shift_type__name__in=['NIGHT_SENIOR', 'NIGHT_ASSISTANT']
        )
        
        day_senior = day_shifts.filter(shift_type__name__in=['DAY_SENIOR', 'ADMIN']).count()
        night_senior = night_shifts.filter(shift_type__name='NIGHT_SENIOR').count()
        
        # Get required minimums (assuming similar to OG)
        if home_name == 'VICTORIA_GARDENS':
            min_total, min_senior = 10, 1
        else:
            min_total, min_senior = 17, 2
        
        day_ok = day_shifts.count() >= min_total and day_senior >= min_senior
        night_ok = night_shifts.count() >= min_total and night_senior >= min_senior
        
        print(f"\n{home.name}:")
        print(f"  Day: {day_shifts.count()}/{min_total} total, {day_senior}/{min_senior} senior {'✓' if day_ok else '✗'}")
        print(f"  Night: {night_shifts.count()}/{min_total} total, {night_senior}/{min_senior} senior {'✓' if night_ok else '✗'}")

if __name__ == '__main__':
    main()
