#!/usr/bin/env python
"""
SIMPLIFIED: Add 2 OM to each standard home (1 for Victoria Gardens) and regenerate shifts.
Uses existing staff, only adds new OM staff members.
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

# Get highest SAP
max_sap = User.objects.all().order_by('-sap').first()
next_sap = int(max_sap.sap) + 1 if max_sap else 800000

# OM names pool
om_names = [
    ('Thomas', 'Anderson'), ('Sarah', 'Connor'), ('Michael', 'Jordan'),
    ('Emma', 'Watson'), ('James', 'Bond'), ('Lisa', 'Simpson'),
    ('Robert', 'Downey'), ('Jennifer', 'Lawrence'), ('William', 'Shakespeare'),
    ('Margaret', 'Thatcher')
]

def add_om_to_home(home_name, count):
    """Add Operations Managers to a home"""
    global next_sap
    
    print(f"\n  Adding {count} OM to {home_name}...")
    care_home = CareHome.objects.get(name=home_name)
    units = list(Unit.objects.filter(care_home=care_home))
    om_role = Role.objects.get(name='OM')
    
    om_staff = []
    for i in range(count):
        fname, lname = om_names[next_sap % len(om_names)]
        unit = units[i % len(units)]
        
        user = User.objects.create(
            sap=f"{next_sap:06d}",
            first_name=fname,
            last_name=lname,
            email=f"{next_sap:06d}@staff.example.com",
            password=make_password('TempPass123!'),
            role=om_role,
            unit=unit,
            home_unit=unit,
            is_staff=False,
            is_active=True,
            annual_leave_allowance=28,
            annual_leave_used=0,
            annual_leave_year_start=datetime(2026, 1, 1).date(),
            team='A'
        )
        om_staff.append(user)
        print(f"    Created OM: {user.sap} - {user.first_name} {user.last_name}")
        next_sap += 1
    
    # Create OM shifts (Mon-Fri, full year)
    admin_shift = ShiftType.objects.get(name='ADMIN')
    start_date = datetime(2026, 1, 4).date()
    end_date = datetime(2027, 1, 3).date()
    
    shifts_created = 0
    current_date = start_date
    while current_date <= end_date:
        # Mon-Fri only
        if current_date.weekday() < 5:
            for om in om_staff:
                Shift.objects.create(
                    user=om,
                    unit=om.unit,
                    shift_type=admin_shift,
                    date=current_date,
                    shift_pattern='DAY_0800_2000',
                    shift_classification='REGULAR',
                    agency_staff_name='',
                    status='CONFIRMED'
                )
                shifts_created += 1
        current_date += timedelta(days=1)
    
    print(f"    Created {shifts_created} OM shifts")
    return om_staff, shifts_created

def main():
    print("\n🏥 ADDING OPERATIONS MANAGERS TO ALL HOMES")
    print("=" * 70)
    
    with transaction.atomic():
        # Delete existing OM staff and shifts to start fresh
        print("\n  Clearing existing OM staff...")
        om_role = Role.objects.get(name='OM')
        old_om = User.objects.filter(role=om_role)
        om_count = old_om.count()
        Shift.objects.filter(user__in=old_om).delete()
        old_om.delete()
        print(f"  ✓ Removed {om_count} existing OM staff")
        
        # Add 2 OM to standard homes
        total_om_shifts = 0
        for home in ['ORCHARD_GROVE', 'RIVERSIDE', 'MEADOWBURN', 'HAWTHORN_HOUSE']:
            staff, shifts = add_om_to_home(home, 2)
            total_om_shifts += shifts
        
        # Add 1 OM to Victoria Gardens
        staff, shifts = add_om_to_home('VICTORIA_GARDENS', 1)
        total_om_shifts += shifts
    
    print("\n" + "=" * 70)
    print("🎉 Operations Managers added successfully!")
    print(f"   Total OM shifts created: {total_om_shifts}")
    print("=" * 70)
    
    # Summary
    print("\n📊 SUMMARY BY HOME:")
    for home_name in ['ORCHARD_GROVE', 'RIVERSIDE', 'MEADOWBURN', 'HAWTHORN_HOUSE', 'VICTORIA_GARDENS']:
        om_count = User.objects.filter(unit__care_home__name=home_name, role__name='OM', is_active=True).count()
        total_staff = User.objects.filter(unit__care_home__name=home_name, is_active=True).count()
        total_shifts = Shift.objects.filter(unit__care_home__name=home_name).count()
        print(f"  {home_name}: {om_count} OM, {total_staff} total staff, {total_shifts} shifts")

if __name__ == '__main__':
    main()
