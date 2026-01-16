#!/usr/bin/env python3
"""
Complete database initialization for all 5 care homes.
Creates units and shift types using correct database structure.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import Role, Unit, ShiftType, CareHome

def main():
    print("\n" + "="*70)
    print("🏥 INITIALIZING ALL CARE HOMES DATA")
    print("="*70 + "\n")
    
    with transaction.atomic():
        # 1. Get all care homes
        print("📍 Loading Care Homes...")
        orchard_grove = CareHome.objects.get(name='ORCHARD_GROVE')
        meadowburn = CareHome.objects.get(name='MEADOWBURN')
        hawthorn_house = CareHome.objects.get(name='HAWTHORN_HOUSE')
        riverside = CareHome.objects.get(name='RIVERSIDE')
        victoria_gardens = CareHome.objects.get(name='VICTORIA_GARDENS')
        print("  ✅ All 5 care homes loaded\n")
        
        # 2. Create Units using correct prefixed names from models.py
        print("🏢 Creating Units for each Care Home...\n")
        
        # Orchard Grove - 9 units (8 care + 1 MGMT)
        print("  📍 ORCHARD GROVE:")
        og_units = [
            {'name': 'OG_BRAMLEY', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'OG_CHERRY', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'OG_GRAPE', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'OG_ORANGE', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'OG_PEACH', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'OG_PEAR', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'OG_PLUM', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'OG_STRAWBERRY', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'OG_MGMT', 'care_home': orchard_grove, 'min_day_staff': 1, 'min_night_staff': 0, 'min_weekend_staff': 1},
        ]
        for unit_data in og_units:
            unit, created = Unit.objects.get_or_create(name=unit_data['name'], defaults=unit_data)
            print(f"    {'✅' if created else 'ℹ️ '} {unit.get_name_display()}")
        
        # Hawthorn House - 9 units (8 care + 1 MGMT)
        print("\n  📍 HAWTHORN HOUSE:")
        hh_units = [
            {'name': 'HH_BLUEBELL', 'care_home': hawthorn_house, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'HH_DAISY', 'care_home': hawthorn_house, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'HH_HEATHER', 'care_home': hawthorn_house, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'HH_IRIS', 'care_home': hawthorn_house, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'HH_PRIMROSE', 'care_home': hawthorn_house, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'HH_SNOWDROP_SRD', 'care_home': hawthorn_house, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'HH_THISTLE_SRD', 'care_home': hawthorn_house, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'HH_VIOLET', 'care_home': hawthorn_house, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'HH_MGMT', 'care_home': hawthorn_house, 'min_day_staff': 1, 'min_night_staff': 0, 'min_weekend_staff': 1},
        ]
        for unit_data in hh_units:
            unit, created = Unit.objects.get_or_create(name=unit_data['name'], defaults=unit_data)
            print(f"    {'✅' if created else 'ℹ️ '} {unit.get_name_display()}")
        
        # Meadowburn - 9 units (8 care + 1 MGMT)
        print("\n  📍 MEADOWBURN:")
        mb_units = [
            {'name': 'MB_ASTER', 'care_home': meadowburn, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'MB_BLUEBELL', 'care_home': meadowburn, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'MB_CORNFLOWER', 'care_home': meadowburn, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'MB_DAISY', 'care_home': meadowburn, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'MB_FOXGLOVE', 'care_home': meadowburn, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'MB_HONEYSUCKLE', 'care_home': meadowburn, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'MB_MARIGOLD', 'care_home': meadowburn, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'MB_POPPY_SRD', 'care_home': meadowburn, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'MB_MGMT', 'care_home': meadowburn, 'min_day_staff': 1, 'min_night_staff': 0, 'min_weekend_staff': 1},
        ]
        for unit_data in mb_units:
            unit, created = Unit.objects.get_or_create(name=unit_data['name'], defaults=unit_data)
            print(f"    {'✅' if created else 'ℹ️ '} {unit.get_name_display()}")
        
        # Riverside - 9 units (8 care + 1 MGMT)
        print("\n  📍 RIVERSIDE:")
        rs_units = [
            {'name': 'RS_DAFFODIL', 'care_home': riverside, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'RS_HEATHER', 'care_home': riverside, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'RS_JASMINE', 'care_home': riverside, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'RS_LILY', 'care_home': riverside, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'RS_LOTUS', 'care_home': riverside, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'RS_MAPLE', 'care_home': riverside, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'RS_ORCHID', 'care_home': riverside, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'RS_ROSE', 'care_home': riverside, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'RS_MGMT', 'care_home': riverside, 'min_day_staff': 1, 'min_night_staff': 0, 'min_weekend_staff': 1},
        ]
        for unit_data in rs_units:
            unit, created = Unit.objects.get_or_create(name=unit_data['name'], defaults=unit_data)
            print(f"    {'✅' if created else 'ℹ️ '} {unit.get_name_display()}")
        
        # Victoria Gardens - 6 units (5 care + 1 MGMT)
        print("\n  📍 VICTORIA GARDENS:")
        vg_units = [
            {'name': 'VG_AZALEA', 'care_home': victoria_gardens, 'min_day_staff': 2, 'min_night_staff': 2, 'min_weekend_staff': 2},
            {'name': 'VG_CROCUS', 'care_home': victoria_gardens, 'min_day_staff': 2, 'min_night_staff': 2, 'min_weekend_staff': 2},
            {'name': 'VG_LILY', 'care_home': victoria_gardens, 'min_day_staff': 2, 'min_night_staff': 2, 'min_weekend_staff': 2},
            {'name': 'VG_ROSE', 'care_home': victoria_gardens, 'min_day_staff': 2, 'min_night_staff': 2, 'min_weekend_staff': 2},
            {'name': 'VG_TULIP', 'care_home': victoria_gardens, 'min_day_staff': 2, 'min_night_staff': 2, 'min_weekend_staff': 2},
            {'name': 'VG_MGMT', 'care_home': victoria_gardens, 'min_day_staff': 1, 'min_night_staff': 0, 'min_weekend_staff': 1},
        ]
        for unit_data in vg_units:
            unit, created = Unit.objects.get_or_create(name=unit_data['name'], defaults=unit_data)
            print(f"    {'✅' if created else 'ℹ️ '} {unit.get_name_display()}")
        
        # 3. Create Shift Types
        print("\n⏰ Creating Shift Types...")
        shift_types = [
            {'name': 'LONG_DAY', 'start_time': '07:45', 'end_time': '20:15', 'color_code': '#28a745', 'duration_hours': 12.5},
            {'name': 'NIGHT', 'start_time': '19:45', 'end_time': '08:15', 'color_code': '#17a2b8', 'duration_hours': 12.5},
            {'name': 'DAY', 'start_time': '08:00', 'end_time': '20:00', 'color_code': '#fd7e14', 'duration_hours': 12.0},
            {'name': 'EARLY', 'start_time': '08:00', 'end_time': '14:00', 'color_code': '#6f42c1', 'duration_hours': 6.0},
            {'name': 'LATE', 'start_time': '14:00', 'end_time': '20:00', 'color_code': '#ffc107', 'duration_hours': 6.0},
            {'name': 'OFF', 'start_time': '00:00', 'end_time': '00:00', 'color_code': '#6c757d', 'duration_hours': 0.0},
            {'name': 'ANNUAL_LEAVE', 'start_time': '00:00', 'end_time': '00:00', 'color_code': '#20c997', 'duration_hours': 0.0},
        ]
        for shift_data in shift_types:
            shift, created = ShiftType.objects.get_or_create(name=shift_data['name'], defaults=shift_data)
            print(f"  {'✅' if created else 'ℹ️ '} {shift.get_name_display()}")
        
        # 4. Add additional roles if needed
        print("\n📋 Checking Roles...")
        roles_to_add = [
            {'name': 'SSCWN', 'is_management': True, 'can_approve_leave': True, 'can_manage_rota': True},
            {'name': 'SCA', 'is_management': False, 'can_approve_leave': False, 'can_manage_rota': False},
        ]
        for role_data in roles_to_add:
            role, created = Role.objects.get_or_create(name=role_data['name'], defaults=role_data)
            print(f"  {'✅' if created else 'ℹ️ '} {role.get_name_display()}")
        
        # 5. Summary
        print("\n" + "="*70)
        print("✨ DATABASE INITIALIZATION COMPLETE!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"  • Care Homes: {CareHome.objects.count()}")
        print(f"  • Roles: {Role.objects.count()}")
        print(f"  • Units: {Unit.objects.count()}")
        print(f"  • Shift Types: {ShiftType.objects.count()}")
        
        print(f"\n🏢 Units per Care Home:")
        for home in CareHome.objects.all():
            unit_count = Unit.objects.filter(care_home=home).count()
            print(f"  • {home.get_name_display()}: {unit_count} units")
        
        print(f"\n✅ Admin user: SAP 000745 (password: password123)")
        print(f"\n🌐 Server: http://127.0.0.1:8000/")
        print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
