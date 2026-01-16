#!/usr/bin/env python3
"""
Complete database setup script for all 5 care homes.
Creates units, shift types, and basic configuration.
Preserves existing admin user (SAP 000745).
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import Role, Unit, ShiftType, CareHome

def main():
    print("\n" + "="*70)
    print("🏥 COMPLETE DATABASE SETUP FOR ALL CARE HOMES")
    print("="*70 + "\n")
    
    with transaction.atomic():
        # 1. Create additional roles (already have SM, OM, SSCW, SCW from create_admin.py)
        print("📋 Setting up Roles...")
        roles_to_add = [
            {'name': 'SSCWN', 'is_management': True, 'can_approve_leave': True, 'can_manage_rota': True},
            {'name': 'SCA', 'is_management': False, 'can_approve_leave': False, 'can_manage_rota': False},
        ]
        
        for role_data in roles_to_add:
            role, created = Role.objects.get_or_create(name=role_data['name'], defaults=role_data)
            if created:
                print(f"  ✅ Created: {role.get_name_display()}")
            else:
                print(f"  ℹ️  Exists: {role.get_name_display()}")
        
        # 2. Get all care homes
        print("\n🏥 Loading Care Homes...")
        orchard_grove = CareHome.objects.get(name='ORCHARD_GROVE')
        meadowburn = CareHome.objects.get(name='MEADOWBURN')
        hawthorn_house = CareHome.objects.get(name='HAWTHORN_HOUSE')
        riverside = CareHome.objects.get(name='RIVERSIDE')
        victoria_gardens = CareHome.objects.get(name='VICTORIA_GARDENS')
        print("  ✅ All 5 care homes loaded")
        
        # 3. Create Units for each home
        print("\n🏢 Creating Units for each Care Home...")
        
        # Orchard Grove (template for large homes) - 8 units
        print("\n  📍 ORCHARD GROVE:")
        og_units = [
            {'name': 'MGMT', 'care_home': orchard_grove, 'min_day_staff': 1, 'min_night_staff': 0, 'min_weekend_staff': 1},
            {'name': 'DUTY', 'care_home': orchard_grove, 'min_day_staff': 1, 'min_night_staff': 1, 'min_weekend_staff': 1},
            {'name': 'BLUE', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'GREEN', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'ROSE', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'VIOLET', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'ORANGE', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
            {'name': 'PEACH', 'care_home': orchard_grove, 'min_day_staff': 3, 'min_night_staff': 2, 'min_weekend_staff': 3},
        ]
        
        for unit_data in og_units:
            unit, created = Unit.objects.get_or_create(
                name=unit_data['name'],
                care_home=unit_data['care_home'],
                defaults=unit_data
            )
            if created:
                print(f"    ✅ {unit.get_name_display()}")
            else:
                print(f"    ℹ️  {unit.get_name_display()} (exists)")
        
        # Meadowburn - replicate Orchard Grove model
        print("\n  📍 MEADOWBURN:")
        for unit_data in og_units:
            new_data = unit_data.copy()
            new_data['care_home'] = meadowburn
            unit, created = Unit.objects.get_or_create(
                name=new_data['name'],
                care_home=meadowburn,
                defaults=new_data
            )
            if created:
                print(f"    ✅ {unit.get_name_display()}")
        
        # Hawthorn House - replicate Orchard Grove model
        print("\n  📍 HAWTHORN HOUSE:")
        for unit_data in og_units:
            new_data = unit_data.copy()
            new_data['care_home'] = hawthorn_house
            unit, created = Unit.objects.get_or_create(
                name=new_data['name'],
                care_home=hawthorn_house,
                defaults=new_data
            )
            if created:
                print(f"    ✅ {unit.get_name_display()}")
        
        # Riverside - replicate Orchard Grove model
        print("\n  📍 RIVERSIDE:")
        for unit_data in og_units:
            new_data = unit_data.copy()
            new_data['care_home'] = riverside
            unit, created = Unit.objects.get_or_create(
                name=new_data['name'],
                care_home=riverside,
                defaults=new_data
            )
            if created:
                print(f"    ✅ {unit.get_name_display()}")
        
        # Victoria Gardens - unique smaller home model (4 units)
        print("\n  📍 VICTORIA GARDENS (Unique Model):")
        vg_units = [
            {'name': 'VG_MGMT', 'care_home': victoria_gardens, 'min_day_staff': 1, 'min_night_staff': 0, 'min_weekend_staff': 1},
            {'name': 'VG_DUTY', 'care_home': victoria_gardens, 'min_day_staff': 1, 'min_night_staff': 1, 'min_weekend_staff': 1},
            {'name': 'VG_BLUE', 'care_home': victoria_gardens, 'min_day_staff': 2, 'min_night_staff': 2, 'min_weekend_staff': 2},
            {'name': 'VG_GREEN', 'care_home': victoria_gardens, 'min_day_staff': 2, 'min_night_staff': 2, 'min_weekend_staff': 2},
        ]
        
        for unit_data in vg_units:
            unit, created = Unit.objects.get_or_create(
                name=unit_data['name'],
                care_home=unit_data['care_home'],
                defaults=unit_data
            )
            if created:
                print(f"    ✅ {unit.get_name_display()}")
        
        # 4. Create Shift Types
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
            if created:
                print(f"  ✅ {shift.get_name_display()}")
            else:
                print(f"  ℹ️  {shift.get_name_display()} (exists)")
        
        # 5. Summary
        print("\n" + "="*70)
        print("✨ DATABASE SETUP COMPLETE!")
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
        
        print(f"\n✅ Admin user preserved: SAP 000745")
        print(f"\n🌐 Server: http://127.0.0.1:8000/")
        print(f"🔐 Login: SAP 000745, password: password123")
        print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
