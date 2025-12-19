"""
Implement Victoria Gardens exact 3-week rotation pattern.
Based on the provided staffing roster with specific day patterns.
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, User, CareHome, ShiftType, Unit
from django.db import transaction

# Day name mappings
DAY_MAP = {
    'sun': 6, 'mon': 0, 'tue': 1, 'wed': 2, 
    'thur': 3, 'thu': 3, 'fri': 4, 'sat': 5
}

def parse_days(day_string):
    """Convert day string like 'mon tue wed' to list of day numbers [0,1,2]"""
    days = day_string.lower().replace('(', '').replace(')', '').split()
    return [DAY_MAP[day] for day in days if day in DAY_MAP]

def get_week_number(date, start_date):
    """Calculate which week (0-2) in the 3-week rotation cycle"""
    days_since_start = (date - start_date).days
    return (days_since_start // 7) % 3

def should_work(date, pattern, start_date):
    """Check if staff should work on this date based on pattern"""
    week_num = get_week_number(date, start_date)
    day_of_week = date.weekday()
    return day_of_week in pattern[week_num]

# Define all staff patterns
PATTERNS = {
    'DAY': {
        'SM': {
            'count': 1,
            'hours': 35,
            'pattern': [
                [0,1,2,3,4],  # week1: mon-fri
                [0,1,2,3,4],  # week2: mon-fri
                [0,1,2,3,4],  # week3: mon-fri
            ],
            'role': 'SM'
        },
        'OM': {
            'count': 1,
            'hours': 35,
            'pattern': [
                [0,1,2,3,4],  # week1: mon-fri
                [0,1,2,3,4],  # week2: mon-fri
                [0,1,2,3,4],  # week3: mon-fri
            ],
            'role': 'OM'
        },
        'SSCW_A': {
            'count': 2,
            'hours': 35,
            'pattern': [
                parse_days('sun wed thur'),
                parse_days('mon tue wed'),
                parse_days('fri sat sun'),
            ],
            'role': 'SSCW'
        },
        'SSCW_B': {
            'count': 2,
            'hours': 35,
            'pattern': [
                parse_days('mon tue wed'),
                parse_days('fri sat sun'),
                parse_days('sun wed thur'),
            ],
            'role': 'SSCW'
        },
        'SSCW_C': {
            'count': 2,
            'hours': 35,
            'pattern': [
                parse_days('fri sat sun'),
                parse_days('sun wed thur'),
                parse_days('mon tue wed'),
            ],
            'role': 'SSCW'
        },
        'SCW_35_A': {
            'count': 5,
            'hours': 35,
            'pattern': [
                parse_days('sun wed thur'),
                parse_days('mon tue wed'),
                parse_days('wed fri sat'),
            ],
            'role': 'SCW'
        },
        'SCW_35_B': {
            'count': 2,
            'hours': 35,
            'pattern': [
                parse_days('sun wed thur'),
                parse_days('mon tue wed'),
                parse_days('wed fri sat'),
            ],
            'role': 'SCW'
        },
        'SCW_35_C': {
            'count': 2,
            'hours': 35,
            'pattern': [
                parse_days('mon tue wed'),
                parse_days('wed fri sat'),
                parse_days('sun wed thur'),
            ],
            'role': 'SCW'
        },
        'SCW_35_D': {
            'count': 1,
            'hours': 35,
            'pattern': [
                parse_days('wed fri sat'),
                parse_days('sun wed thur'),
                parse_days('mon tue wed'),
            ],
            'role': 'SCW'
        },
        'SCW_24_A': {
            'count': 3,
            'hours': 24,
            'pattern': [
                parse_days('mon tue'),
                parse_days('fri sat'),
                parse_days('sun thu'),
            ],
            'role': 'SCW'
        },
        'SCW_24_B': {
            'count': 2,
            'hours': 24,
            'pattern': [
                parse_days('fri sat'),
                parse_days('sun thu'),
                parse_days('mon tue'),
            ],
            'role': 'SCW'
        },
        'SCW_24_C': {
            'count': 3,
            'hours': 24,
            'pattern': [
                parse_days('mon tue'),
                parse_days('fri sat'),
                parse_days('sun thu'),
            ],
            'role': 'SCW'
        },
        'SCW_24_D': {
            'count': 2,
            'hours': 24,
            'pattern': [
                parse_days('fri sat'),
                parse_days('sun thu'),
                parse_days('mon tue'),
            ],
            'role': 'SCW'
        },
        'SCA_35_A': {
            'count': 2,
            'hours': 35,
            'pattern': [
                parse_days('sun wed thur'),
                parse_days('mon tue wed'),
                parse_days('wed fri sat'),
            ],
            'role': 'SCA'
        },
        'SCA_35_B': {
            'count': 2,
            'hours': 35,
            'pattern': [
                parse_days('mon tue wed'),
                parse_days('tue fri sat'),
                parse_days('sun wed thur'),
            ],
            'role': 'SCA'
        },
        'SCA_35_C': {
            'count': 4,
            'hours': 35,
            'pattern': [
                parse_days('wed fri sat'),
                parse_days('sun wed thur'),
                parse_days('mon tue wed'),
            ],
            'role': 'SCA'
        },
        'SCA_35_D': {
            'count': 1,
            'hours': 35,
            'pattern': [
                parse_days('sun wed thur'),
                parse_days('mon tue wed'),
                parse_days('wed fri sat'),
            ],
            'role': 'SCA'
        },
        'SCA_35_E': {
            'count': 3,
            'hours': 35,
            'pattern': [
                parse_days('mon tue wed'),
                parse_days('tue fri sat'),
                parse_days('sun wed thur'),
            ],
            'role': 'SCA'
        },
        'SCA_24_A': {
            'count': 5,
            'hours': 24,
            'pattern': [
                parse_days('mon tue'),
                parse_days('fri sat'),
                parse_days('sun thu'),
            ],
            'role': 'SCA'
        },
        'SCA_24_B': {
            'count': 2,
            'hours': 24,
            'pattern': [
                parse_days('fri sat'),
                parse_days('sun thu'),
                parse_days('mon tue'),
            ],
            'role': 'SCA'
        },
        'SCA_24_C': {
            'count': 6,
            'hours': 24,
            'pattern': [
                parse_days('sun thu'),
                parse_days('mon tue'),
                parse_days('fri sat'),
            ],
            'role': 'SCA'
        },
        'SCA_24_D': {
            'count': 1,
            'hours': 24,
            'pattern': [
                parse_days('mon tue'),
                parse_days('fri sat'),
                parse_days('sun thu'),
            ],
            'role': 'SCA'
        },
    },
    'NIGHT': {
        'SSCWN_A': {
            'count': 2,
            'hours': 35,
            'pattern': [
                parse_days('sun mon tue'),
                parse_days('thur fri sat'),
                parse_days('tue wed thur'),
            ],
            'role': 'SSCWN'
        },
        'SSCWN_B': {
            'count': 2,
            'hours': 35,
            'pattern': [
                parse_days('tue wed thur'),
                parse_days('sun mon tue'),
                parse_days('thur fri sat'),
            ],
            'role': 'SSCWN'
        },
        'SCAN_35_A': {
            'count': 5,
            'hours': 35,
            'pattern': [
                parse_days('tue wed thur'),
                parse_days('sun mon tue'),
                parse_days('thur fri sat'),
            ],
            'role': 'SCAN'
        },
        'SCAN_35_B': {
            'count': 4,
            'hours': 35,
            'pattern': [
                parse_days('sun mon tue'),
                parse_days('thur fri sat'),
                parse_days('tue wed thur'),
            ],
            'role': 'SCAN'
        },
        'SCAN_35_C': {
            'count': 1,
            'hours': 35,
            'pattern': [
                parse_days('thur fri sat'),
                parse_days('tue wed thur'),
                parse_days('sun mon tue'),
            ],
            'role': 'SCAN'
        },
        'SCAN_35_D': {
            'count': 1,
            'hours': 35,
            'pattern': [
                parse_days('sun mon tue'),
                parse_days('thur fri sat'),
                parse_days('tue wed thur'),
            ],
            'role': 'SCAN'
        },
        'SCAN_24_A': {
            'count': 3,
            'hours': 24,
            'pattern': [
                parse_days('tue wed'),
                parse_days('sun mon'),
                parse_days('fri sat'),
            ],
            'role': 'SCAN'
        },
        'SCAN_24_B': {
            'count': 6,
            'hours': 24,
            'pattern': [
                parse_days('fri sat'),
                parse_days('tue wed'),
                parse_days('sun mon'),
            ],
            'role': 'SCAN'
        },
        'SCAN_24_C': {
            'count': 6,
            'hours': 24,
            'pattern': [
                parse_days('sun mon'),
                parse_days('fri sat'),
                parse_days('tue wed'),
            ],
            'role': 'SCAN'
        },
        'SCAN_24_D': {
            'count': 2,
            'hours': 24,
            'pattern': [
                parse_days('wed thu'),
                parse_days('sun mon'),
                parse_days('fri sat'),
            ],
            'role': 'SCAN'
        },
        'SCWN_35_A': {
            'count': 2,
            'hours': 35,
            'pattern': [
                parse_days('thur fri sat'),
                parse_days('tue wed thur'),
                parse_days('sun mon tue'),
            ],
            'role': 'SCWN'
        },
        'SCWN_35_B': {
            'count': 1,
            'hours': 35,
            'pattern': [
                parse_days('sun mon tue'),
                parse_days('thur fri sat'),
                parse_days('tue wed thur'),
            ],
            'role': 'SCWN'
        },
        'SCWN_35_C': {
            'count': 1,
            'hours': 35,
            'pattern': [
                parse_days('tue wed thur'),
                parse_days('sun mon tue'),
                parse_days('thur fri sat'),
            ],
            'role': 'SCWN'
        },
        'SCWN_24_A': {
            'count': 2,
            'hours': 24,
            'pattern': [
                parse_days('fri sat'),
                parse_days('wed thu'),
                parse_days('sun mon'),
            ],
            'role': 'SCWN'
        },
        'SCWN_24_B': {
            'count': 3,
            'hours': 24,
            'pattern': [
                parse_days('wed thu'),
                parse_days('sun mon'),
                parse_days('fri sat'),
            ],
            'role': 'SCWN'
        },
        'SCWN_24_C': {
            'count': 2,
            'hours': 24,
            'pattern': [
                parse_days('sun mon'),
                parse_days('fri sat'),
                parse_days('wed thu'),
            ],
            'role': 'SCWN'
        },
    }
}

def main():
    print("\n" + "="*80)
    print("VICTORIA GARDENS - EXACT 3-WEEK ROTATION IMPLEMENTATION")
    print("="*80)
    
    # Configuration
    start_date = datetime(2025, 1, 1).date()  # Start of year
    end_date = datetime(2025, 6, 30).date()    # 6 months
    
    print(f"\nPeriod: {start_date} to {end_date}")
    print(f"Total days: {(end_date - start_date).days + 1}")
    
    # Get Victoria Gardens
    try:
        vg = CareHome.objects.get(name='VICTORIA_GARDENS')
        print(f"\n✓ Victoria Gardens loaded")
    except CareHome.DoesNotExist:
        print("\n✗ Victoria Gardens not found!")
        return
    
    # Get units
    units = list(Unit.objects.filter(care_home=vg, is_active=True).order_by('name'))
    if not units:
        print("✗ No active units found for Victoria Gardens!")
        return
    print(f"✓ {len(units)} units: {', '.join([u.get_name_display() for u in units])}")
    
    # Get staff by role
    staff_by_role = {}
    for role_name in ['SM', 'OM', 'SSCW', 'SSCWN', 'SCW', 'SCWN', 'SCA', 'SCAN']:
        staff = list(User.objects.filter(
            unit__care_home=vg,
            role__name=role_name,
            is_active=True
        ).order_by('sap'))
        staff_by_role[role_name] = staff
        print(f"✓ {len(staff)} {role_name} staff")
    
    # Get shift types
    shift_types = {
        'SM': ShiftType.objects.get(name='ADMIN'),
        'OM': ShiftType.objects.get(name='ADMIN'),
        'SSCW': ShiftType.objects.get(name='DAY_SENIOR'),
        'SCW': ShiftType.objects.get(name='DAY_SENIOR'),
        'SCA': ShiftType.objects.get(name='DAY_ASSISTANT'),
        'SSCWN': ShiftType.objects.get(name='NIGHT_SENIOR'),
        'SCWN': ShiftType.objects.get(name='NIGHT_SENIOR'),
        'SCAN': ShiftType.objects.get(name='NIGHT_ASSISTANT'),
    }
    
    with transaction.atomic():
        # Clear existing VG shifts
        deleted = Shift.objects.filter(unit__care_home=vg).delete()
        print(f"\n✓ Cleared {deleted[0]} existing shifts")
        
        shifts_created = 0
        
        # Track staff index for each pattern
        pattern_staff_index = {}
        
        # Process each day
        current_date = start_date
        while current_date <= end_date:
            day_shifts = 0
            night_shifts = 0
            
            # Track staff used on this day to avoid duplicates
            used_staff = set()
            
            # Create shifts for each pattern
            for shift_period, period_patterns in PATTERNS.items():
                for pattern_name, pattern_def in period_patterns.items():
                    role = pattern_def['role']
                    pattern = pattern_def['pattern']
                    count = pattern_def['count']
                    
                    if should_work(current_date, pattern, start_date):
                        available_staff = staff_by_role.get(role, [])
                        
                        # Initialize index for this pattern if not exists
                        if pattern_name not in pattern_staff_index:
                            pattern_staff_index[pattern_name] = 0
                        
                        # Assign staff for this pattern
                        assigned = 0
                        attempts = 0
                        while assigned < count and attempts < len(available_staff):
                            staff_idx = pattern_staff_index[pattern_name] % len(available_staff)
                            staff_member = available_staff[staff_idx]
                            shift_type = shift_types[role]
                            
                            # Check if this staff member already has a shift today
                            staff_shift_key = (staff_member.pk, current_date, shift_type.pk)
                            if staff_shift_key not in used_staff:
                                unit = units[assigned % len(units)]  # Distribute across units
                                
                                Shift.objects.create(
                                    user=staff_member,
                                    unit=unit,
                                    shift_type=shift_type,
                                    date=current_date,
                                    status='SCHEDULED',
                                    shift_pattern='DAY_0800_2000' if shift_period == 'DAY' else 'NIGHT_2000_0800'
                                )
                                shifts_created += 1
                                used_staff.add(staff_shift_key)
                                assigned += 1
                                
                                if shift_period == 'DAY':
                                    day_shifts += 1
                                else:
                                    night_shifts += 1
                            
                            pattern_staff_index[pattern_name] += 1
                            attempts += 1
            
            if shifts_created % 100 == 0:
                print(f"  {current_date}: {day_shifts} day, {night_shifts} night (total: {shifts_created})")
            
            current_date += timedelta(days=1)
        
        print(f"\n{'='*80}")
        print(f"✓ Created {shifts_created} shifts for Victoria Gardens")
        print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
