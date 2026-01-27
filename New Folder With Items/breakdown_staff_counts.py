#!/usr/bin/env python3
"""
Staff Count Breakdown Analysis
Shows detailed breakdown of all 1,352 staff by care home and role
"""

import os
import sys
import django
from collections import defaultdict

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db.models import Count
from scheduling.models import User, CareHome, Role

def main():
    print("=" * 80)
    print("📊 STAFF COUNT BREAKDOWN - DETAILED ANALYSIS")
    print("=" * 80)
    print()
    
    # Total counts
    total_staff = User.objects.count()
    active_staff = User.objects.filter(is_active=1).count()
    inactive_staff = User.objects.filter(is_active=0).count()
    
    print(f"🔢 OVERALL TOTALS")
    print(f"   Total Staff: {total_staff:,}")
    print(f"   ├─ Active (is_active=1): {active_staff:,}")
    print(f"   └─ Inactive (is_active=0): {inactive_staff:,}")
    print()
    print("=" * 80)
    print()
    
    # Breakdown by Care Home
    print("🏠 BREAKDOWN BY CARE HOME")
    print("-" * 80)
    
    homes = CareHome.objects.all().order_by('name')
    home_totals = []
    
    for home in homes:
        active_count = User.objects.filter(home_unit__care_home=home, is_active=1).count()
        inactive_count = User.objects.filter(home_unit__care_home=home, is_active=0).count()
        total_count = active_count + inactive_count
        home_totals.append((home.get_name_display(), active_count, inactive_count, total_count))
        
        print(f"{home.get_name_display()}:")
        print(f"   Total: {total_count:,}")
        print(f"   ├─ Active: {active_count:,}")
        print(f"   └─ Inactive: {inactive_count:,}")
        print()
    
    # Staff with no home_unit
    no_home_active = User.objects.filter(home_unit__isnull=True, is_active=1).count()
    no_home_inactive = User.objects.filter(home_unit__isnull=True, is_active=0).count()
    no_home_total = no_home_active + no_home_inactive
    
    if no_home_total > 0:
        print(f"(No Home Assigned):")
        print(f"   Total: {no_home_total:,}")
        print(f"   ├─ Active: {no_home_active:,}")
        print(f"   └─ Inactive: {no_home_inactive:,}")
        print()
    
    print("-" * 80)
    print(f"{'TOTAL':20} {total_staff:>6,}")
    print(f"{'Active':20} {active_staff:>6,}")
    print(f"{'Inactive':20} {inactive_staff:>6,}")
    print()
    print("=" * 80)
    print()
    
    # Breakdown by Role
    print("👥 BREAKDOWN BY ROLE")
    print("-" * 80)
    
    roles = Role.objects.all().order_by('name')
    role_totals = []
    
    for role in roles:
        active_count = User.objects.filter(role=role, is_active=1).count()
        inactive_count = User.objects.filter(role=role, is_active=0).count()
        total_count = active_count + inactive_count
        role_totals.append((role.name, active_count, inactive_count, total_count))
        
        print(f"{role.name}:")
        print(f"   Total: {total_count:,}")
        print(f"   ├─ Active: {active_count:,}")
        print(f"   └─ Inactive: {inactive_count:,}")
        print()
    
    # Count staff with no role
    no_role_active = User.objects.filter(role__isnull=True, is_active=1).count()
    no_role_inactive = User.objects.filter(role__isnull=True, is_active=0).count()
    no_role_total = no_role_active + no_role_inactive
    
    if no_role_total > 0:
        print(f"(No Role Assigned):")
        print(f"   Total: {no_role_total:,}")
        print(f"   ├─ Active: {no_role_active:,}")
        print(f"   └─ Inactive: {no_role_inactive:,}")
        print()
    
    print("-" * 80)
    print(f"{'TOTAL':20} {total_staff:>6,}")
    print(f"{'Active':20} {active_staff:>6,}")
    print(f"{'Inactive':20} {inactive_staff:>6,}")
    print()
    print("=" * 80)
    print()
    
    # Cross-tabulation: Staff by Home and Role
    print("📋 DETAILED MATRIX: STAFF BY HOME AND ROLE (Active Staff Only)")
    print("-" * 80)
    
    # Build matrix
    matrix = defaultdict(lambda: defaultdict(int))
    home_name_map = {}  # Maps short codes to CareHome names
    
    for staff in User.objects.filter(is_active=1).select_related('home_unit__care_home', 'role'):
        if staff.home_unit and staff.home_unit.care_home:
            home_name = staff.home_unit.care_home.name  # Store full name like 'HAWTHORN_HOUSE'
            # Extract short code (HH, MB, OG, RS, VG)
            if 'HAWTHORN' in home_name:
                home_code = 'HH'
            elif 'MEADOWBURN' in home_name:
                home_code = 'MB'
            elif 'ORCHARD' in home_name:
                home_code = 'OG'
            elif 'RIVERSIDE' in home_name:
                home_code = 'RS'
            elif 'VICTORIA' in home_name:
                home_code = 'VG'
            else:
                home_code = home_name[:4]
            home_name_map[home_code] = home_name
        else:
            home_code = 'NONE'
        role_name = staff.role.name if staff.role else 'NO_ROLE'
        matrix[home_code][role_name] += 1
    
    # Get all unique role names
    all_roles = sorted(set(role_name for home_roles in matrix.values() for role_name in home_roles.keys()))
    
    # Print header
    header = f"{'Home':8}"
    for role in all_roles:
        header += f"{role:>8}"
    header += f"{'Total':>8}"
    print(header)
    print("-" * len(header))
    
    # Print data
    home_codes = ['HH', 'MB', 'OG', 'RS', 'VG']
    for home_code in home_codes:
        if home_code in matrix:
            row = f"{home_code:8}"
            home_total = 0
            for role in all_roles:
                count = matrix[home_code].get(role, 0)
                row += f"{count:>8}"
                home_total += count
            row += f"{home_total:>8}"
            print(row)
    
    # Print totals
    print("-" * len(header))
    total_row = f"{'TOTAL':8}"
    grand_total = 0
    for role in all_roles:
        role_total = sum(matrix[home].get(role, 0) for home in home_codes if home in matrix)
        total_row += f"{role_total:>8}"
        grand_total += role_total
    total_row += f"{grand_total:>8}"
    print(total_row)
    print()
    print("=" * 80)
    print()
    
    # Summary insights
    print("💡 KEY INSIGHTS")
    print("-" * 80)
    print(f"• {inactive_staff:,} inactive staff records are included in the total count")
    print(f"• Only {active_staff:,} staff are active and available for scheduling")
    print(f"• Inactive staff are retained for historical shift data integrity")
    print()
    
    if inactive_staff > active_staff:
        print(f"⚠️  NOTE: More inactive ({inactive_staff}) than active ({active_staff}) staff")
        print(f"   This is normal if system contains historical data from previous years")
        print()
    
    print("=" * 80)

if __name__ == '__main__':
    main()
