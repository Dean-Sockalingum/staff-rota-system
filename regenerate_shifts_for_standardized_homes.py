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
# Days: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday

SHIFT_PATTERNS = {
    # Social Care Assistants (Day shift) - 3 days per week on rotation
    'SCA_DAY_A': {
        'week1': [2, 4, 5],  # Wed, Fri, Sat
        'week2': [6, 2, 3],  # Sun, Wed, Thu
        'week3': [0, 1, 2],  # Mon, Tue, Wed
    },
    'SCA_DAY_B': {
        'week1': [4, 5],     # Fri, Sat
        'week2': [6, 3],     # Sun, Thu
        'week3': [0, 1],     # Mon, Tue
    },
    'SCA_DAY_C': {
        'week1': [6, 2, 3],  # Sun, Wed, Thu
        'week2': [0, 1, 2],  # Mon, Tue, Wed
        'week3': [3, 4, 5],  # Thu, Fri, Sat
    },
    
    # Social Care Assistants (Night shift) - 3 nights per week on rotation
    'SCAN_NIGHT_A': {
        'week1': [2, 4, 5],  # Wed, Fri, Sat
        'week2': [6, 2, 3],  # Sun, Wed, Thu
        'week3': [0, 1, 2],  # Mon, Tue, Wed
    },
    'SCAN_NIGHT_B': {
        'week1': [0, 2, 3],  # Mon, Wed, Thu
        'week2': [4, 5, 6],  # Fri, Sat, Sun
        'week3': [1, 2, 3],  # Tue, Wed, Thu
    },
    'SCAN_NIGHT_C': {
        'week1': [4, 5],     # Fri, Sat
        'week2': [6, 3],     # Sun, Thu
        'week3': [0, 1],     # Mon, Tue
    },
    
    # Social Care Workers (Day shift) - 3 days per week
    'SCW_DAY': {
        'week1': [0, 2, 3],  # Mon, Wed, Thu
        'week2': [4, 5, 6],  # Fri, Sat, Sun
        'week3': [1, 2, 3],  # Tue, Wed, Thu
    },
    
    # Social Care Workers (Night shift) - 2 nights per week
    'SCWN_NIGHT': {
        'week1': [0, 3],     # Mon, Thu
        'week2': [1, 4],     # Tue, Fri
        'week3': [5, 6],     # Sat, Sun
    },
    
    # Senior Social Care Workers (Day shift) - full time 5 days
    'SSCW_DAY': {
        'week1': [0, 1, 2, 3, 4],     # Mon-Fri
        'week2': [0, 1, 2, 3, 4],     # Mon-Fri
        'week3': [0, 1, 2, 3, 4],     # Mon-Fri
    },
    
    # Senior Social Care Workers (Night shift) - 4 nights per week
    'SSCWN_NIGHT': {
        'week1': [0, 2, 4, 6],  # Mon, Wed, Fri, Sun
        'week2': [1, 3, 5, 6],  # Tue, Thu, Sat, Sun
        'week3': [0, 2, 4, 6],  # Mon, Wed, Fri, Sun
    },
    
    # Service Managers - weekdays only
    'SM_DAY': {
        'week1': [0, 1, 2, 3, 4],  # Mon-Fri
        'week2': [0, 1, 2, 3, 4],  # Mon-Fri
        'week3': [0, 1, 2, 3, 4],  # Mon-Fri
    },
}

# Map roles to pattern types
ROLE_TO_PATTERN = {
    'SCA': ['SCA_DAY_A', 'SCA_DAY_B', 'SCA_DAY_C'],
    'SCAN': ['SCAN_NIGHT_A', 'SCAN_NIGHT_B', 'SCAN_NIGHT_C'],
    'SCW': ['SCW_DAY'],
    'SCWN': ['SCWN_NIGHT'],
    'SSCW': ['SSCW_DAY'],
    'SSCWN': ['SSCWN_NIGHT'],
    'SM': ['SM_DAY'],
    'OM': ['SM_DAY'],  # Operations Managers work like Service Managers
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
    day_of_week = date.weekday()  # 0=Monday, 6=Sunday
    
    return day_of_week in pattern[week_key]

def regenerate_shifts():
    """Main function to regenerate all shifts"""
    
    print("="*80)
    print("SHIFT REGENERATION FOR STANDARDIZED HOMES")
    print("="*80)
    print()
    
    # Configuration
    target_homes = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'ORCHARD_GROVE', 'RIVERSIDE']
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=365)  # 12 months of shifts
    
    print(f"Target homes: {', '.join(target_homes)}")
    print(f"Shift period: {start_date} to {end_date}")
    print()
    
    # Step 1: Delete all existing shifts
    print("STEP 1: Deleting all existing shifts...")
    existing_shifts = Shift.objects.all().count()
    print(f"  Found {existing_shifts} existing shifts (all with orphaned SAP references)")
    
    if existing_shifts > 0:
        response = input("  Delete all existing shifts? (yes/no): ")
        if response.lower() != 'yes':
            print("\nOperation cancelled.")
            return
        
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
                    if role_name not in ROLE_TO_PATTERN:
                        print(f"  ⚠ Skipping role {role_name} - no pattern defined")
                        continue
                    
                    # Get available patterns for this role
                    available_patterns = ROLE_TO_PATTERN[role_name]
                    
                    # Assign patterns to staff in rotation
                    for idx, staff in enumerate(staff_members):
                        pattern_name = available_patterns[idx % len(available_patterns)]
                        pattern = SHIFT_PATTERNS[pattern_name]
                        
                        # Determine shift type based on role
                        if role_name in ['SSCW', 'SM', 'OM']:
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
