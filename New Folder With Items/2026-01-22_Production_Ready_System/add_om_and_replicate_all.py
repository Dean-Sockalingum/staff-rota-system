#!/usr/bin/env python
"""
Add Operations Managers and replicate Orchard Grove complete staffing to all homes.
- Orchard Grove: Add 2 OM
- Riverside, Meadowburn, Hawthorn House: Replicate OG pattern including 2 OM each
- Victoria Gardens: 1 OM (different smaller pattern)
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.db import transaction
from django.contrib.auth.hashers import make_password

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
    """Get all pattern templates"""
    
    # OM patterns (Mon-Fri, 35hrs)
    om_patterns = [
        {'week1': parse_days('mon tue wed thu fri'), 'week2': parse_days('mon tue wed thu fri'), 'week3': parse_days('mon tue wed thu fri')},
        {'week1': parse_days('mon tue wed thu fri'), 'week2': parse_days('mon tue wed thu fri'), 'week3': parse_days('mon tue wed thu fri')},
    ]
    
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
    
    # SCA patterns - cycle through both 24hrs and 35hrs (52 staff total)
    sca_patterns = [
        # 24hrs patterns (2 days/week)
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        {'week1': parse_days('mon tue'), 'week2': parse_days('mon tue'), 'week3': parse_days('wed thu')},
        {'week1': parse_days('sun mon'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        # 35hrs patterns (3 days/week)
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
        {'week1': parse_days('tue wed thu'), 'week2': parse_days('thu fri sat'), 'week3': parse_days('sun mon tue')},
        {'week1': parse_days('mon tue wed'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('sat sun mon')},
        {'week1': parse_days('fri sat sun'), 'week2': parse_days('tue wed thu'), 'week3': parse_days('mon tue wed')},
    ] * 4  # Repeat to cover 52 staff
    
    # SCW patterns - 27 staff
    scw_patterns = [
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
    ] * 3  # Repeat to cover 27 staff
    
    # SCAN patterns - 67 staff (24hrs and 35hrs night shifts)
    scan_patterns = [
        # 24hrs patterns
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('sat sun'), 'week2': parse_days('fri sat'), 'week3': parse_days('thu fri')},
        {'week1': parse_days('tue wed'), 'week2': parse_days('thu fri'), 'week3': parse_days('sun mon')},
        {'week1': parse_days('fri sat'), 'week2': parse_days('tue wed'), 'week3': parse_days('sat sun')},
        # 35hrs patterns
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
    ] * 7  # Repeat to cover 67 staff
    
    # SCWN patterns - 14 staff
    scwn_patterns = [
        {'week1': parse_days('sun mon'), 'week2': parse_days('wed thu'), 'week3': parse_days('tue wed')},
        {'week1': parse_days('thu fri'), 'week2': parse_days('sun mon'), 'week3': parse_days('fri sat')},
        {'week1': parse_days('wed thu'), 'week2': parse_days('sat sun'), 'week3': parse_days('mon tue')},
        {'week1': parse_days('sun mon tue'), 'week2': parse_days('wed thu fri'), 'week3': parse_days('tue wed thu')},
        {'week1': parse_days('thu fri sat'), 'week2': parse_days('sun mon tue'), 'week3': parse_days('fri sat sun')},
        {'week1': parse_days('wed thu fri'), 'week2': parse_days('sat sun mon'), 'week3': parse_days('mon tue wed')},
        {'week1': parse_days('sat sun mon'), 'week2': parse_days('fri sat sun'), 'week3': parse_days('thu fri sat')},
    ] * 2  # Repeat to cover 14 staff
    
    return {
        'OM': om_patterns,
        'SSCW': sscw_patterns,
        'SSCWN': sscwn_patterns,
        'SM': sm_patterns,
        'SCA': sca_patterns,
        'SCW': scw_patterns,
        'SCAN': scan_patterns,
        'SCWN': scwn_patterns,
    }

def create_staff_for_home(care_home, role_name, count, start_sap, start_first_name_num, pattern_templates):
    """Create staff members for a care home"""
    role = Role.objects.get(name=role_name)
    units = list(Unit.objects.filter(care_home=care_home))
    
    staff_created = []
    
    # Name pools for variety
    first_names = [
        'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
        'William', 'Barbara', 'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica',
        'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
        'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley',
        'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle',
        'Kenneth', 'Carol', 'Kevin', 'Amanda', 'Brian', 'Dorothy', 'George', 'Melissa',
        'Timothy', 'Deborah', 'Ronald', 'Stephanie', 'Edward', 'Rebecca', 'Jason', 'Sharon',
        'Jeffrey', 'Laura', 'Ryan', 'Cynthia', 'Jacob', 'Kathleen', 'Gary', 'Amy',
        'Nicholas', 'Angela', 'Eric', 'Shirley', 'Jonathan', 'Anna', 'Stephen', 'Brenda',
        'Larry', 'Pamela', 'Justin', 'Emma', 'Scott', 'Nicole', 'Brandon', 'Helen',
        'Benjamin', 'Samantha', 'Samuel', 'Katherine', 'Raymond', 'Christine', 'Patrick', 'Debra',
        'Alexander', 'Rachel', 'Jack', 'Catherine', 'Dennis', 'Carolyn', 'Jerry', 'Janet'
    ]
    
    last_names = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
        'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas',
        'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White',
        'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young',
        'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
        'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
        'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
        'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy',
        'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey',
        'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson'
    ]
    
    for i in range(count):
        sap = f"{start_sap + i:06d}"
        
        # Check if SAP already exists
        if User.objects.filter(sap=sap).exists():
            continue
        
        # Create unique name
        fname_idx = (start_first_name_num + i) % len(first_names)
        lname_idx = (start_first_name_num + i * 2) % len(last_names)
        first_name = first_names[fname_idx]
        last_name = last_names[lname_idx]
        
        # Assign to a unit (rotate through units)
        unit = units[i % len(units)]
        
        # Create user
        user = User.objects.create(
            sap=sap,
            first_name=first_name,
            last_name=last_name,
            email=f"{sap}@staff.example.com",
            password=make_password('TempPass123!'),
            role=role,
            unit=unit,
            home_unit=unit,
            is_staff=False,
            is_active=True,
            annual_leave_allowance=28,
            annual_leave_used=0,
            annual_leave_year_start=datetime(2026, 1, 1).date(),
            team='A' if i % 2 == 0 else 'B'
        )
        
        staff_created.append(user)
    
    return staff_created

def create_shifts_for_staff(care_home, staff_list, pattern_templates, shift_type, shift_pattern, cycle_start, start_date, end_date):
    """Create shifts for staff based on their patterns"""
    shifts_created = 0
    units = list(Unit.objects.filter(care_home=care_home))
    
    # Track used staff per day to avoid duplicates
    used_staff = set()
    
    current_date = start_date
    while current_date <= end_date:
        for idx, staff_member in enumerate(staff_list):
            pattern_idx = idx % len(pattern_templates)
            pattern = pattern_templates[pattern_idx]
            
            if should_work(pattern, current_date, cycle_start):
                key = (staff_member.pk, current_date, shift_type.pk)
                if key in used_staff:
                    continue
                
                # Create shift
                Shift.objects.create(
                    user=staff_member,
                    unit=staff_member.unit,
                    shift_type=shift_type,
                    date=current_date,
                    shift_pattern=shift_pattern,
                    shift_classification='REGULAR',
                    agency_staff_name='',
                    status='CONFIRMED'
                )
                used_staff.add(key)
                shifts_created += 1
        
        current_date += timedelta(days=1)
    
    return shifts_created

def implement_full_home(home_name, om_count, is_victoria=False):
    """Implement full staffing for a care home"""
    print(f"\n{'='*70}")
    print(f"🏥 {home_name}")
    print(f"{'='*70}")
    
    try:
        care_home = CareHome.objects.get(name=home_name)
    except CareHome.DoesNotExist:
        print(f"✗ Care home {home_name} not found!")
        return
    
    # Clear existing shifts in batches to avoid SQL variable limit
    total_deleted = 0
    while True:
        batch = list(Shift.objects.filter(unit__care_home=care_home).values_list('id', flat=True)[:5000])
        if not batch:
            break
        Shift.objects.filter(id__in=batch).delete()
        total_deleted += len(batch)
    print(f"  ✓ Cleared {total_deleted} existing shifts")
    
    # Get shift types
    day_senior = ShiftType.objects.get(name='DAY_SENIOR')
    night_senior = ShiftType.objects.get(name='NIGHT_SENIOR')
    day_assistant = ShiftType.objects.get(name='DAY_ASSISTANT')
    night_assistant = ShiftType.objects.get(name='NIGHT_ASSISTANT')
    admin = ShiftType.objects.get(name='ADMIN')
    
    # Date range
    cycle_start = datetime(2026, 1, 4).date()
    start_date = datetime(2026, 1, 4).date()
    end_date = datetime(2027, 1, 3).date()
    
    pattern_templates = get_pattern_templates()
    
    # Get starting SAP number
    max_sap = User.objects.all().order_by('-sap').first()
    if max_sap:
        next_sap = int(max_sap.sap) + 1
    else:
        next_sap = 1000
    
    total_shifts = 0
    
    # Victoria Gardens has different smaller staffing
    if is_victoria:
        staffing = {
            'OM': om_count,
            'SSCW': 5,  # Smaller home
            'SSCWN': 4,
            'SM': 1,
            'SCA': 30,  # Fewer staff
            'SCW': 15,
            'SCAN': 40,
            'SCWN': 8,
        }
    else:
        # Standard home staffing (same as Orchard Grove)
        staffing = {
            'OM': om_count,
            'SSCW': 9,
            'SSCWN': 8,
            'SM': 1,
            'SCA': 52,
            'SCW': 27,
            'SCAN': 67,
            'SCWN': 14,
        }
    
    # Create staff and shifts for each role
    role_shift_map = {
        'OM': (admin, 'DAY_0800_2000'),
        'SM': (admin, 'DAY_0800_2000'),
        'SSCW': (day_senior, 'DAY_0800_2000'),
        'SSCWN': (night_senior, 'NIGHT_2000_0800'),
        'SCA': (day_assistant, 'DAY_0800_2000'),
        'SCW': (day_senior, 'DAY_0800_2000'),
        'SCAN': (night_assistant, 'NIGHT_2000_0800'),
        'SCWN': (night_senior, 'NIGHT_2000_0800'),
    }
    
    start_name_num = next_sap  # Use SAP as seed for name variety
    
    for role_name, count in staffing.items():
        if count == 0:
            continue
        
        # Create staff
        staff_list = create_staff_for_home(
            care_home, 
            role_name, 
            count, 
            next_sap, 
            start_name_num,
            pattern_templates[role_name]
        )
        
        if staff_list:
            # Create shifts
            shift_type, shift_pattern = role_shift_map[role_name]
            shifts = create_shifts_for_staff(
                care_home,
                staff_list,
                pattern_templates[role_name],
                shift_type,
                shift_pattern,
                cycle_start,
                start_date,
                end_date
            )
            
            print(f"  ✓ {role_name}: {len(staff_list)} staff, {shifts} shifts")
            total_shifts += shifts
            next_sap += count
            start_name_num += count
    
    print(f"{'='*70}")
    print(f"✓ Created {total_shifts} shifts for {home_name}")
    return total_shifts

def main():
    print("\n🏥 MULTI-HOME STAFFING IMPLEMENTATION")
    print("=" * 70)
    print("Adding Operations Managers and replicating patterns to all homes")
    print("=" * 70)
    
    with transaction.atomic():
        # Implement each home
        implement_full_home('ORCHARD_GROVE', om_count=2)
        implement_full_home('RIVERSIDE', om_count=2)
        implement_full_home('MEADOWBURN', om_count=2)
        implement_full_home('HAWTHORN_HOUSE', om_count=2)
        implement_full_home('VICTORIA_GARDENS', om_count=1, is_victoria=True)
    
    print("\n" + "=" * 70)
    print("🎉 All homes fully staffed with complete 3-week rotations!")
    print("=" * 70)
    
    # Summary
    for home_name in ['ORCHARD_GROVE', 'RIVERSIDE', 'MEADOWBURN', 'HAWTHORN_HOUSE', 'VICTORIA_GARDENS']:
        total = Shift.objects.filter(unit__care_home__name=home_name).count()
        staff_count = User.objects.filter(unit__care_home__name=home_name, is_active=True).count()
        print(f"  {home_name}: {staff_count} staff, {total} shifts")

if __name__ == '__main__':
    main()
