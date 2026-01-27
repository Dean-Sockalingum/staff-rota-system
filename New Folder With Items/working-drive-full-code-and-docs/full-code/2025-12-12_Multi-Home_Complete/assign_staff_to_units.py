#!/usr/bin/env python3
"""
Assign staff to their primary units based on shift history.
Each staff member is assigned to the unit where they work most frequently.
"""

import os
import django
from collections import Counter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Shift, Unit
from django.db.models import Count

def main():
    print("\n" + "="*70)
    print("ASSIGNING STAFF TO UNITS BASED ON SHIFT PATTERNS")
    print("="*70)
    
    # Get all active staff (excluding admin)
    staff_members = User.objects.filter(is_active=True).exclude(sap='000745')
    total_staff = staff_members.count()
    
    print(f"\n📊 Processing {total_staff} staff members...")
    
    assigned = 0
    no_shifts = 0
    already_assigned = 0
    
    for staff in staff_members:
        # Get shift distribution for this staff member
        shift_units = Shift.objects.filter(
            user=staff
        ).values('unit__name', 'unit_id').annotate(
            count=Count('id')
        ).order_by('-count')
        
        if not shift_units:
            no_shifts += 1
            continue
        
        # Get the unit where they work most frequently
        primary_unit_data = shift_units[0]
        primary_unit_id = primary_unit_data['unit_id']
        shift_count = primary_unit_data['count']
        
        if primary_unit_id:
            primary_unit = Unit.objects.get(id=primary_unit_id)
            
            # Update staff member's unit and home_unit
            staff.unit = primary_unit
            staff.home_unit = primary_unit
            staff.save()
            
            assigned += 1
            
            if assigned % 100 == 0:
                print(f"  ✅ Assigned {assigned} staff to their primary units...")
    
    print("\n" + "="*70)
    print("ASSIGNMENT COMPLETE")
    print("="*70)
    
    print(f"\n📊 Summary:")
    print(f"  • Assigned to units:  {assigned:4d}")
    print(f"  • No shift history:   {no_shifts:4d}")
    print(f"  • Total processed:    {total_staff:4d}")
    
    # Show distribution by care home
    print("\n🏠 Staff Distribution by Care Home:")
    from django.db.models import Count
    home_counts = User.objects.filter(
        is_active=True
    ).exclude(
        sap='000745'
    ).values(
        'unit__care_home__name'
    ).annotate(
        count=Count('sap')
    ).order_by('-count')
    
    for item in home_counts:
        home_name = item['unit__care_home__name'] or 'No Home'
        print(f"  {home_name:20s}: {item['count']:4d} staff")
    
    # Show distribution by unit type (care vs MGMT)
    print("\n📋 Staff Distribution by Unit Type:")
    mgmt_staff = User.objects.filter(
        is_active=True,
        unit__name__icontains='MGMT'
    ).exclude(sap='000745').count()
    
    care_staff = User.objects.filter(
        is_active=True,
        unit__isnull=False
    ).exclude(
        sap='000745'
    ).exclude(
        unit__name__icontains='MGMT'
    ).count()
    
    print(f"  Care Units:    {care_staff:4d} staff")
    print(f"  MGMT Units:    {mgmt_staff:4d} staff")
    print(f"  Unassigned:    {no_shifts:4d} staff")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
