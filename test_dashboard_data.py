#!/usr/bin/env python3
"""
Test the Senior Dashboard view logic to see what data it's returning.
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Shift, Unit, CareHome, User
from django.utils import timezone

print("="*80)
print("SENIOR DASHBOARD DATA TEST")
print("="*80)
print()

today = datetime.now().date()
print(f"Today: {today}\n")

# Test the exact logic from the view
care_homes = CareHome.objects.all().order_by('name')

# Home-specific staffing requirements (from view)
home_staffing = {
    'HAWTHORN_HOUSE': {'day_min': 18, 'day_ideal': 41, 'night_min': 18, 'night_ideal': 41},
    'MEADOWBURN': {'day_min': 17, 'day_ideal': 41, 'night_min': 17, 'night_ideal': 41},
    'ORCHARD_GROVE': {'day_min': 17, 'day_ideal': 41, 'night_min': 17, 'night_ideal': 41},
    'RIVERSIDE': {'day_min': 17, 'day_ideal': 41, 'night_min': 17, 'night_ideal': 41},
    'VICTORIA_GARDENS': {'day_min': 10, 'day_ideal': 18, 'night_min': 10, 'night_ideal': 14},
}

staffing_today = []

for home in care_homes:
    units = Unit.objects.filter(care_home=home, is_active=True)
    
    # TODAY'S shifts for this home only
    today_shifts = Shift.objects.filter(
        date=today,
        unit__in=units,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).select_related('user', 'shift_type')
    
    # Count by shift type
    day_shifts = today_shifts.filter(shift_type__name__icontains='DAY').values('user').distinct().count()
    night_shifts = today_shifts.filter(shift_type__name__icontains='NIGHT').values('user').distinct().count()
    
    # Get home-specific requirements
    requirements = home_staffing.get(home.name, {'day_min': 17, 'day_ideal': 24, 'night_min': 17, 'night_ideal': 21})
    
    day_required = requirements['day_min']
    night_required = requirements['night_min']
    
    day_coverage = (day_shifts / day_required * 100) if day_required > 0 else 100
    night_coverage = (night_shifts / night_required * 100) if night_required > 0 else 100
    
    staffing_data = {
        'home': home.get_name_display(),
        'day_actual': day_shifts,
        'day_required': day_required,
        'day_coverage': day_coverage,
        'night_actual': night_shifts,
        'night_required': night_required,
        'night_coverage': night_coverage,
        'status': 'good' if day_coverage >= 100 and night_coverage >= 100 else 'critical',
    }
    
    staffing_today.append(staffing_data)
    
    print(f"{staffing_data['home']}:")
    print(f"  Day: {staffing_data['day_actual']}/{staffing_data['day_required']} ({staffing_data['day_coverage']:.1f}%)")
    print(f"  Night: {staffing_data['night_actual']}/{staffing_data['night_required']} ({staffing_data['night_coverage']:.1f}%)")
    print(f"  Status: {staffing_data['status']}")
    print()

print("="*80)
print("ACTIVE STAFF COUNTS")
print("="*80)
print()

for home in care_homes:
    units = Unit.objects.filter(care_home=home)
    staff_count = User.objects.filter(unit__in=units, is_active=True).count()
    print(f"{home.get_name_display()}: {staff_count} active staff")

print()
