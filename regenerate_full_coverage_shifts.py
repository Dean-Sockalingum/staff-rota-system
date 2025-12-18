#!/usr/bin/env python3
"""
Regenerate shifts for demo with FULL DAILY COVERAGE.

All units fully staffed every day (except MGMT Mon-Fri only).
No rotation patterns - consistent staffing levels daily.
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import User, Shift, ShiftType, Unit, CareHome

def regenerate_full_coverage_shifts():
    """Generate shifts with full daily coverage for all units"""
    
    print("="*80)
    print("FULL COVERAGE SHIFT REGENERATION")
    print("="*80)
    print()
    
    # Configuration
    target_homes = ['HAWTHORN_HOUSE', 'MEADOWBURN', 'ORCHARD_GROVE', 'RIVERSIDE']
    start_date = datetime(2025, 12, 18).date()  # Today
    end_date = datetime(2026, 12, 17).date()  # 365 days
    
    print(f"Target homes: {', '.join(target_homes)}")
    print(f"Shift period: {start_date} to {end_date} (365 days)")
    print()
    
    # Step 1: Delete all existing shifts
    print("STEP 1: Deleting all existing shifts...")
    existing_count = Shift.objects.all().count()
    print(f"  Found {existing_count:,} existing shifts")
    
    if existing_count > 0:
        print("  Deleting in batches...")
        batch_size = 1000
        deleted = 0
        while True:
            batch = list(Shift.objects.all()[:batch_size].values_list('id', flat=True))
            if not batch:
                break
            Shift.objects.filter(id__in=batch).delete()
            deleted += len(batch)
            if deleted % 10000 == 0:
                print(f"    Deleted {deleted:,} shifts...")
        print(f"  ✓ Deleted {existing_count:,} shifts")
    print()
    
    # Step 2: Get shift types
    print("STEP 2: Loading shift types...")
    day_shift = ShiftType.objects.get(name='DAY')
    day_senior_shift = ShiftType.objects.get(name='DAY_SENIOR')
    night_assistant_shift = ShiftType.objects.get(name='NIGHT_ASSISTANT')
    print(f"  ✓ Loaded shift types")
    print()
    
    # Step 3: Generate shifts
    print("STEP 3: Generating full coverage shifts...")
    print()
    
    total_created = 0
    
    for home_name in target_homes:
        home = CareHome.objects.get(name=home_name)
        units = Unit.objects.filter(care_home=home)
        
        print(f"{home.get_name_display()}: {units.count()} units")
        
        # Get staff by role and unit
        # Separate MGMT staff (Mon-Fri only) from care staff (7 days)
        mgmt_unit = units.filter(name__icontains='MGMT').first()
        care_units = units.exclude(name__icontains='MGMT')
        
        # Get all active staff by unit
        home_shifts_created = 0
        
        # === DAY SHIFTS (7 days/week for care units, Mon-Fri for MGMT) ===
        
        # Process care units (7 days/week)
        for unit in care_units:
            # Get staff in this unit with day roles
            day_staff = User.objects.filter(
                unit=unit,
                is_active=True,
                role__name__in=['SSCW', 'SCW_35', 'SCW_24', 'SCA_24']
            ).order_by('sap')
            
            # Split into senior (30%) and regular (70%)
            total_day = day_staff.count()
            senior_count = max(1, total_day // 3)  # ~33% senior
            
            seniors = list(day_staff[:senior_count])
            regulars = list(day_staff[senior_count:])
            
            # Generate shifts for every day
            current_date = start_date
            while current_date <= end_date:
                # Rotate through staff to spread shifts evenly
                day_offset = (current_date - start_date).days
                
                # Each senior works ~5 days/week
                for i, staff in enumerate(seniors):
                    if (day_offset + i) % 7 < 5:  # Work 5 out of 7 days
                        Shift.objects.create(
                            user=staff,
                            date=current_date,
                            shift_type=day_senior_shift
                        )
                        home_shifts_created += 1
                
                # Each regular works ~5 days/week
                for i, staff in enumerate(regulars):
                    if (day_offset + i) % 7 < 5:  # Work 5 out of 7 days
                        Shift.objects.create(
                            user=staff,
                            date=current_date,
                            shift_type=day_shift
                        )
                        home_shifts_created += 1
                
                current_date += timedelta(days=1)
        
        # Process MGMT unit (Mon-Fri only)
        if mgmt_unit:
            mgmt_staff = User.objects.filter(
                unit=mgmt_unit,
                is_active=True,
                role__name__in=['SM', 'OM', 'HOS']
            ).order_by('sap')
            
            current_date = start_date
            while current_date <= end_date:
                # Only Monday-Friday (weekday 0-4)
                if current_date.weekday() < 5:
                    for staff in mgmt_staff:
                        Shift.objects.create(
                            user=staff,
                            date=current_date,
                            shift_type=day_shift
                        )
                        home_shifts_created += 1
                
                current_date += timedelta(days=1)
        
        # === NIGHT SHIFTS (7 days/week) ===
        for unit in care_units:
            night_staff = User.objects.filter(
                unit=unit,
                is_active=True,
                role__name__in=['SSCWN', 'SCWN_35', 'SCWN_24', 'SCAN_35', 'SCAN_24']
            ).order_by('sap')
            
            # Generate shifts for every day
            current_date = start_date
            while current_date <= end_date:
                day_offset = (current_date - start_date).days
                
                # Each night staff works ~5 days/week
                for i, staff in enumerate(night_staff):
                    if (day_offset + i) % 7 < 5:  # Work 5 out of 7 days
                        Shift.objects.create(
                            user=staff,
                            date=current_date,
                            shift_type=night_assistant_shift
                        )
                        home_shifts_created += 1
                
                current_date += timedelta(days=1)
        
        print(f"  ✓ Created {home_shifts_created:,} shifts")
        total_created += home_shifts_created
    
    print()
    print("="*80)
    print(f"✓ COMPLETE: Created {total_created:,} total shifts")
    print("="*80)
    print()
    
    # Verification
    print("VERIFICATION:")
    for home_name in target_homes:
        home = CareHome.objects.get(name=home_name)
        
        # Check today's shifts
        today_total = Shift.objects.filter(
            user__unit__care_home=home,
            date=start_date
        ).count()
        
        today_day = Shift.objects.filter(
            user__unit__care_home=home,
            date=start_date,
            shift_type__name__in=['DAY', 'DAY_SENIOR']
        ).count()
        
        today_night = Shift.objects.filter(
            user__unit__care_home=home,
            date=start_date,
            shift_type__name='NIGHT_ASSISTANT'
        ).count()
        
        print(f"{home.get_name_display()}: {today_total} shifts ({today_day} day, {today_night} night)")

if __name__ == '__main__':
    regenerate_full_coverage_shifts()
