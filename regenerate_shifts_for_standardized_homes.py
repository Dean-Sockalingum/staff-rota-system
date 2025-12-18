#!/usr/bin/env python3
"""
Regenerate shifts for all 4 standardized homes using identical patterns.

This script will:
1. Delete all existing orphaned shifts (98,413 records with old SAP numbers)
2. Generate new shifts for Hawthorn House, Meadowburn, Orchard Grove, and Riverside
3. Apply identical shift patterns to matching staff roles across all homes
4. Create 12 months of shifts starting from today
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import User, Shift, ShiftType, Unit, CareHome

# Standard 3-week rotating shift patterns for each role
# Days: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
# Based on actual Orchard Grove patterns

SHIFT_PATTERNS = {
    # ===== SENIOR SUPPORT CARE WORKERS (Day) - 9 staff, 3 groups of 3 =====
    'SSCW_GROUP1': {
        'week1': [0, 1, 2],  # Sun, Mon, Tue
        'week2': [4, 5, 6],  # Thu, Fri, Sat
        'week3': [2, 3, 4],  # Tue, Wed, Thu
    },
    'SSCW_GROUP2': {
        'week1': [2, 3, 4],  # Tue, Wed, Thu
        'week2': [2, 3, 4],  # Tue, Wed, Thu
        'week3': [0, 1, 2],  # Sun, Mon, Tue
    },
    'SSCW_GROUP3': {
        'week1': [4, 5, 6],  # Thu, Fri, Sat
        'week2': [0, 1, 2],  # Sun, Mon, Tue
        'week3': [4, 5, 6],  # Thu, Fri, Sat
    },
    
    # ===== SENIOR SUPPORT CARE WORKERS (Night) - 8 staff, groups of 3+3+2 =====
    'SSCWN_GROUP1': {
        'week1': [1, 2, 3],  # Mon, Tue, Wed
        'week2': [4, 5, 6],  # Thu, Fri, Sat
        'week3': [2, 3, 4],  # Tue, Wed, Thu
    },
    'SSCWN_GROUP2': {
        'week1': [4, 5, 6],  # Thu, Fri, Sat
        'week2': [2, 3, 4],  # Tue, Wed, Thu
        'week3': [1, 2, 3],  # Mon, Tue, Wed
    },
    'SSCWN_GROUP3': {
        'week1': [2, 3, 4],  # Tue, Wed, Thu
        'week2': [1, 2, 3],  # Mon, Tue, Wed
        'week3': [4, 5, 6],  # Thu, Fri, Sat
    },
    
    # ===== SERVICE/OPERATIONS MANAGERS - 3 staff, fixed Mon-Fri =====
    'SM_FIXED': {
        'week1': [1, 2, 3, 4, 5],  # Mon-Fri
        'week2': [1, 2, 3, 4, 5],  # Mon-Fri
        'week3': [1, 2, 3, 4, 5],  # Mon-Fri
    },
    
    # ===== SUPPORT CARE WORKERS 35hrs (Day) - 9 staff, 3 groups of 3 =====
    'SCW35_GROUP1': {
        'week1': [3, 5, 6],  # Wed, Fri, Sat
        'week2': [0, 3, 4],  # Sun, Wed, Thu
        'week3': [1, 2, 3],  # Mon, Tue, Wed
    },
    'SCW35_GROUP2': {
        'week1': [0, 3, 4],  # Sun, Wed, Thu
        'week2': [1, 2, 3],  # Mon, Tue, Wed
        'week3': [3, 5, 6],  # Wed, Fri, Sat
    },
    'SCW35_GROUP3': {
        'week1': [1, 2, 3],  # Mon, Tue, Wed
        'week2': [3, 5, 6],  # Wed, Fri, Sat
        'week3': [0, 3, 4],  # Sun, Wed, Thu
    },
    
    # ===== SUPPORT CARE WORKERS 24hrs (Day) - 18 staff, 3 groups of 6 =====
    'SCW24_GROUP1': {
        'week1': [5, 6],     # Fri, Sat
        'week2': [0, 4],     # Sun, Thu
        'week3': [1, 2],     # Mon, Tue
    },
    'SCW24_GROUP2': {
        'week1': [0, 4],     # Sun, Thu
        'week2': [1, 2],     # Mon, Tue
        'week3': [5, 6],     # Fri, Sat
    },
    'SCW24_GROUP3': {
        'week1': [1, 2],     # Mon, Tue
        'week2': [5, 6],     # Fri, Sat
        'week3': [0, 4],     # Sun, Thu
    },
    
    # ===== SUPPORT CARE WORKERS 35hrs (Night) - 7 staff, groups of 2+3+2 =====
    'SCWN35_GROUP1': {
        'week1': [0, 1, 2],  # Sun, Mon, Tue
        'week2': [4, 5, 6],  # Thu, Fri, Sat
        'week3': [2, 3, 4],  # Tue, Wed, Thu
    },
    'SCWN35_GROUP2': {
        'week1': [4, 5, 6],  # Thu, Fri, Sat
        'week2': [2, 3, 4],  # Tue, Wed, Thu
        'week3': [0, 1, 2],  # Sun, Mon, Tue
    },
    'SCWN35_GROUP3': {
        'week1': [2, 3, 4],  # Tue, Wed, Thu
        'week2': [0, 1, 2],  # Sun, Mon, Tue
        'week3': [4, 5, 6],  # Thu, Fri, Sat
    },
    
    # ===== SUPPORT CARE WORKERS 24hrs (Night) - 7 staff, groups of 2+1+4 =====
    'SCWN24_GROUP1': {
        'week1': [0, 1],     # Sun, Mon
        'week2': [5, 6],     # Fri, Sat
        'week3': [3, 4],     # Wed, Thu
    },
    'SCWN24_GROUP2': {
        'week1': [5, 6],     # Fri, Sat
        'week2': [3, 4],     # Wed, Thu
        'week3': [0, 1],     # Sun, Mon
    },
    'SCWN24_GROUP3': {
        'week1': [3, 4],     # Wed, Thu
        'week2': [0, 1],     # Sun, Mon
        'week3': [5, 6],     # Fri, Sat
    },
    
    # ===== SUPPORT CARE ASSISTANTS 24hrs (Day) - ~32 staff, 3 groups =====
    'SCA24_GROUP1': {
        'week1': [0, 1],     # Sun, Mon
        'week2': [3, 4],     # Wed, Thu
        'week3': [3, 4],     # Wed, Thu
    },
    'SCA24_GROUP2': {
        'week1': [3, 4],     # Wed, Thu
        'week2': [0, 1],     # Sun, Mon
        'week3': [0, 1],     # Sun, Mon
    },
    'SCA24_GROUP3': {
        'week1': [2, 3],     # Tue, Wed
        'week2': [2, 3],     # Tue, Wed
        'week3': [5, 6],     # Fri, Sat
    },
    
    # ===== SUPPORT CARE ASSISTANTS 35hrs (Night) - 35 staff, groups of 11+12+12 =====
    'SCAN35_GROUP1': {
        'week1': [0, 1, 2],  # Sun, Mon, Tue
        'week2': [4, 5, 6],  # Thu, Fri, Sat
        'week3': [2, 3, 4],  # Tue, Wed, Thu
    },
    'SCAN35_GROUP2': {
        'week1': [4, 5, 6],  # Thu, Fri, Sat
        'week2': [2, 3, 4],  # Tue, Wed, Thu
        'week3': [0, 1, 2],  # Sun, Mon, Tue
    },
    'SCAN35_GROUP3': {
        'week1': [2, 3, 4],  # Tue, Wed, Thu
        'week2': [0, 1, 2],  # Sun, Mon, Tue
        'week3': [4, 5, 6],  # Thu, Fri, Sat
    },
    
    # ===== SUPPORT CARE ASSISTANTS 24hrs (Night) - ~32 staff, groups of 12+12+8 =====
    'SCAN24_GROUP1': {
        'week1': [0, 1],     # Sun, Mon
        'week2': [0, 1],     # Sun, Mon
        'week3': [0, 1],     # Sun, Mon
    },
    'SCAN24_GROUP2': {
        'week1': [4, 5],     # Thu, Fri
        'week2': [5, 6],     # Fri, Sat
        'week3': [4, 5],     # Thu, Fri
    },
    'SCAN24_GROUP3': {
        'week1': [2, 3],     # Tue, Wed
        'week2': [2, 3],     # Tue, Wed
        'week3': [5, 6],     # Fri, Sat
    },
}

# Map roles to pattern types
# Staff are assigned to groups based on SAP order (first N → Group1, next M → Group2, etc.)
ROLE_TO_PATTERN = {
    'SSCW': ['SSCW_GROUP1', 'SSCW_GROUP2', 'SSCW_GROUP3'],
    'SSCWN': ['SSCWN_GROUP1', 'SSCWN_GROUP2', 'SSCWN_GROUP3'],
    'SM': ['SM_FIXED'],
    'OM': ['SM_FIXED'],
    'HOS': ['SM_FIXED'],  # Head of Service works Mon-Fri like other management
    'SCW_35': ['SCW35_GROUP1', 'SCW35_GROUP2', 'SCW35_GROUP3'],
    'SCW_24': ['SCW24_GROUP1', 'SCW24_GROUP2', 'SCW24_GROUP3'],
    'SCWN_35': ['SCWN35_GROUP1', 'SCWN35_GROUP2', 'SCWN35_GROUP3'],
    'SCWN_24': ['SCWN24_GROUP1', 'SCWN24_GROUP2', 'SCWN24_GROUP3'],
    'SCA_24': ['SCA24_GROUP1', 'SCA24_GROUP2', 'SCA24_GROUP3'],
    'SCAN_35': ['SCAN35_GROUP1', 'SCAN35_GROUP2', 'SCAN35_GROUP3'],
    'SCAN_24': ['SCAN24_GROUP1', 'SCAN24_GROUP2', 'SCAN24_GROUP3'],
}

def get_week_number(date, start_date):
    """Get which week (1-3) in the 3-week cycle"""
    days_since_start = (date - start_date).days
    week_number = (days_since_start // 7) % 3
    return week_number + 1

def should_work_on_day(date, pattern, start_date):
    """Check if staff member should work on this date based on their pattern"""
    week_num = get_week_number(date, start_date)
    week_key = f'week{week_num}'
    # Convert Python's weekday (0=Monday) to our pattern format (0=Sunday)
    day_of_week = (date.weekday() + 1) % 7  # 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
    
    return day_of_week in pattern[week_key]

def regenerate_shifts():
    """Main function to regenerate all shifts"""
    
    print("="*80)
    print("SHIFT REGENERATION FOR STANDARDIZED HOMES")
    print("="*80)
    print()
    
    # Configuration
    target_homes = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'ORCHARD_GROVE', 'RIVERSIDE']
    start_date = datetime(2025, 12, 15).date()  # Sunday Dec 15, 2025 - start of 3-week cycle
    end_date = datetime(2026, 12, 13).date()  # 52 weeks (364 days)
    
    print(f"Target homes: {', '.join(target_homes)}")
    print(f"Shift period: {start_date} to {end_date}")
    print()
    
    # Step 1: Delete all existing shifts
    print("STEP 1: Deleting all existing shifts...")
    existing_shifts = Shift.objects.all().count()
    print(f"  Found {existing_shifts} existing shifts (all with orphaned SAP references)")
    
    if existing_shifts > 0:
        print("  Proceeding with deletion...")
        
        # Delete in batches to avoid SQLite variable limit
        print("  Deleting shifts in batches...")
        batch_size = 1000
        deleted_count = 0
        while True:
            batch = list(Shift.objects.all()[:batch_size].values_list('id', flat=True))
            if not batch:
                break
            Shift.objects.filter(id__in=batch).delete()
            deleted_count += len(batch)
            if deleted_count % 10000 == 0:
                print(f"    Deleted {deleted_count:,} shifts...")
        
        print(f"  ✓ Deleted all {existing_shifts:,} shifts")
    else:
        print("  ✓ No shifts to delete")
    print()
    
    # Step 2: Get shift types
    print("STEP 2: Loading shift types...")
    try:
        day_shift = ShiftType.objects.get(name='DAY')
        day_senior_shift = ShiftType.objects.get(name='DAY_SENIOR')
        night_assistant_shift = ShiftType.objects.get(name='NIGHT_ASSISTANT')
        night_senior_shift = ShiftType.objects.get(name='NIGHT_SENIOR')
        print(f"  ✓ Found shift types: DAY, DAY_SENIOR, NIGHT_ASSISTANT, NIGHT_SENIOR")
    except ShiftType.DoesNotExist as e:
        print(f"  ✗ ERROR: Required shift type not found: {e}")
        print("  Available shift types:")
        for st in ShiftType.objects.all():
            print(f"    - {st.name}")
        return
    print()
    
    # Step 3: Generate shifts for each home
    print("STEP 3: Generating shifts for each home...")
    print()
    
    total_shifts_created = 0
    
    for home_name in target_homes:
        try:
            home = CareHome.objects.get(name=home_name)
            units = Unit.objects.filter(care_home=home)
            
            # Get active staff
            staff_list = User.objects.filter(
                unit__in=units,
                is_active=True
            ).select_related('role', 'unit').order_by('sap')
            
            print(f"{home.get_name_display()}: {staff_list.count()} active staff")
            
            # Group staff by role
            staff_by_role = {}
            for staff in staff_list:
                role_name = staff.role.name if staff.role else 'UNKNOWN'
                if role_name not in staff_by_role:
                    staff_by_role[role_name] = []
                staff_by_role[role_name].append(staff)
            
            home_shifts_created = 0
            
            # Generate shifts for each staff member
            with transaction.atomic():
                for role_name, staff_members in staff_by_role.items():
                    # Determine role key considering hour variants
                    role_key = role_name
                    
                    # For roles with hour variants, need to check which pattern to use
                    # Based on typical staffing: first staff get 35hrs, rest get 24hrs
                    if role_name == 'SCW':
                        # 9 staff = 35hrs, rest = 24hrs
                        for idx, staff in enumerate(staff_members):
                            if idx < 9:
                                pattern_key = 'SCW_35'
                            else:
                                pattern_key = 'SCW_24'
                            
                            if pattern_key not in ROLE_TO_PATTERN:
                                continue
                                
                            available_patterns = ROLE_TO_PATTERN[pattern_key]
                            pattern_name = available_patterns[(idx if idx < 9 else idx - 9) % len(available_patterns)]
                            pattern = SHIFT_PATTERNS[pattern_name]
                            
                            shift_type = day_shift
                            is_night = False
                            
                            # Generate shifts
                            current_date = start_date
                            while current_date <= end_date:
                                if should_work_on_day(current_date, pattern, start_date):
                                    Shift.objects.create(
                                        user=staff,
                                        unit=staff.unit,
                                        shift_type=shift_type,
                                        date=current_date,
                                        status='SCHEDULED',
                                        shift_classification='REGULAR',
                                        shift_pattern='DAY_0800_2000'
                                    )
                                    home_shifts_created += 1
                                current_date += timedelta(days=1)
                        continue
                        
                    elif role_name == 'SCWN':
                        # Split between 35hrs and 24hrs
                        for idx, staff in enumerate(staff_members):
                            if idx < 7:
                                pattern_key = 'SCWN_35'
                            else:
                                pattern_key = 'SCWN_24'
                            
                            if pattern_key not in ROLE_TO_PATTERN:
                                continue
                                
                            available_patterns = ROLE_TO_PATTERN[pattern_key]
                            pattern_name = available_patterns[(idx if idx < 7 else idx - 7) % len(available_patterns)]
                            pattern = SHIFT_PATTERNS[pattern_name]
                            
                            shift_type = night_assistant_shift
                            is_night = True
                            
                            # Generate shifts
                            current_date = start_date
                            while current_date <= end_date:
                                if should_work_on_day(current_date, pattern, start_date):
                                    Shift.objects.create(
                                        user=staff,
                                        unit=staff.unit,
                                        shift_type=shift_type,
                                        date=current_date,
                                        status='SCHEDULED',
                                        shift_classification='REGULAR',
                                        shift_pattern='NIGHT_2000_0800'
                                    )
                                    home_shifts_created += 1
                                current_date += timedelta(days=1)
                        continue
                        
                    elif role_name == 'SCA':
                        # All 24hrs
                        role_key = 'SCA_24'
                    elif role_name == 'SCAN':
                        # Split between 35hrs and 24hrs
                        for idx, staff in enumerate(staff_members):
                            if idx < 35:
                                pattern_key = 'SCAN_35'
                                # SCAN 35hrs groups: 11+12+12
                                if idx < 11:
                                    pattern_idx = 0  # Group 1
                                elif idx < 23:
                                    pattern_idx = 1  # Group 2
                                else:
                                    pattern_idx = 2  # Group 3
                            else:
                                pattern_key = 'SCAN_24'
                                # SCAN 24hrs groups: 12+12+8
                                scan24_idx = idx - 35
                                if scan24_idx < 12:
                                    pattern_idx = 0  # Group 1
                                elif scan24_idx < 24:
                                    pattern_idx = 1  # Group 2
                                else:
                                    pattern_idx = 2  # Group 3
                            
                            if pattern_key not in ROLE_TO_PATTERN:
                                continue
                                
                            available_patterns = ROLE_TO_PATTERN[pattern_key]
                            pattern_name = available_patterns[pattern_idx]
                            pattern = SHIFT_PATTERNS[pattern_name]
                            
                            shift_type = night_assistant_shift
                            is_night = True
                            
                            # Generate shifts
                            current_date = start_date
                            while current_date <= end_date:
                                if should_work_on_day(current_date, pattern, start_date):
                                    Shift.objects.create(
                                        user=staff,
                                        unit=staff.unit,
                                        shift_type=shift_type,
                                        date=current_date,
                                        status='SCHEDULED',
                                        shift_classification='REGULAR',
                                        shift_pattern='NIGHT_2000_0800'
                                    )
                                    home_shifts_created += 1
                                current_date += timedelta(days=1)
                        continue
                    
                    # Standard roles with consecutive block assignment (SSCW, SSCWN, SM, OM, SCA)
                    if role_key not in ROLE_TO_PATTERN:
                        print(f"  ⚠ Skipping role {role_name} - no pattern defined")
                        continue
                    
                    # Get available patterns for this role
                    available_patterns = ROLE_TO_PATTERN[role_key]
                    
                    # Assign patterns to staff in consecutive blocks
                    # Calculate group sizes (distribute as evenly as possible)
                    total_staff = len(staff_members)
                    num_groups = len(available_patterns)
                    base_size = total_staff // num_groups
                    extra = total_staff % num_groups
                    
                    # Assign each staff member to a pattern based on consecutive blocks
                    for idx, staff in enumerate(staff_members):
                        # Determine which group this staff belongs to
                        accumulated = 0
                        pattern_idx = 0
                        for g in range(num_groups):
                            group_size = base_size + (1 if g < extra else 0)
                            if idx < accumulated + group_size:
                                pattern_idx = g
                                break
                            accumulated += group_size
                        
                        pattern_name = available_patterns[pattern_idx]
                        pattern = SHIFT_PATTERNS[pattern_name]
                        
                        # Determine shift type based on role
                        if role_name in ['SSCW', 'SM', 'OM', 'HOS']:
                            shift_type = day_senior_shift
                        elif role_name == 'SSCWN':
                            shift_type = night_senior_shift
                        elif role_name in ['SCAN', 'SCWN']:
                            shift_type = night_assistant_shift
                        else:  # SCA, SCW
                            shift_type = day_shift
                        
                        is_night = role_name in ['SCAN', 'SCWN', 'SSCWN']
                        
                        # Generate shifts for this staff member
                        current_date = start_date
                        while current_date <= end_date:
                            if should_work_on_day(current_date, pattern, start_date):
                                Shift.objects.create(
                                    user=staff,
                                    unit=staff.unit,
                                    shift_type=shift_type,
                                    date=current_date,
                                    status='SCHEDULED',
                                    shift_classification='REGULAR',
                                    shift_pattern='NIGHT_2000_0800' if is_night else 'DAY_0800_2000'
                                )
                                home_shifts_created += 1
                            
                            current_date += timedelta(days=1)
            
            total_shifts_created += home_shifts_created
            print(f"  ✓ Created {home_shifts_created:,} shifts")
            print()
            
        except CareHome.DoesNotExist:
            print(f"  ✗ {home_name} not found")
            print()
    
    print("="*80)
    print("SHIFT REGENERATION COMPLETE")
    print("="*80)
    print()
    print(f"Summary:")
    print(f"  • Old shifts deleted: {existing_shifts:,}")
    print(f"  • New shifts created: {total_shifts_created:,}")
    print(f"  • Homes updated: {len(target_homes)}")
    print(f"  • Period covered: {start_date} to {end_date}")
    print()
    print("All 4 homes now have identical shift patterns based on role.")
    print()

if __name__ == '__main__':
    regenerate_shifts()
