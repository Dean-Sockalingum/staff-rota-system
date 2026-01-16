#!/usr/bin/env python3
"""
Check Service Manager (SM) assignments across homes
Each home should have exactly 1 SM
"""

import os
import sys
import django

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, CareHome, Role

def main():
    print("=" * 80)
    print("🔍 SERVICE MANAGER (SM) ASSIGNMENT CHECK")
    print("=" * 80)
    print()
    
    # Get SM role
    try:
        sm_role = Role.objects.get(name='SM')
    except Role.DoesNotExist:
        print("❌ SM role not found!")
        return
    
    # Get all active SMs
    active_sms = User.objects.filter(role=sm_role, is_active=1).select_related('home_unit__care_home')
    total_active_sms = active_sms.count()
    
    print(f"📊 Total Active SMs: {total_active_sms} (Expected: 5 - one per home)")
    print()
    
    # Group by home
    homes = CareHome.objects.all().order_by('name')
    
    print("🏠 SM DISTRIBUTION BY CARE HOME")
    print("-" * 80)
    
    issues_found = []
    
    for home in homes:
        home_sms = active_sms.filter(home_unit__care_home=home)
        count = home_sms.count()
        
        status = "✅" if count == 1 else "⚠️" if count == 0 else "❌"
        
        print(f"{status} {home.get_name_display()}: {count} SM(s)")
        
        if count > 0:
            for sm in home_sms:
                print(f"   - {sm.first_name} {sm.last_name} (SAP: {sm.sap})")
                print(f"     Unit: {sm.home_unit.get_name_display() if sm.home_unit else 'None'}")
        
        if count == 0:
            issues_found.append(f"No SM assigned to {home.get_name_display()}")
        elif count > 1:
            issues_found.append(f"{home.get_name_display()} has {count} SMs (should be 1)")
        
        print()
    
    # Check for SMs with no home assignment
    no_home_sms = active_sms.filter(home_unit__isnull=True)
    if no_home_sms.exists():
        print("⚠️  SMs WITHOUT HOME ASSIGNMENT:")
        for sm in no_home_sms:
            print(f"   - {sm.first_name} {sm.last_name} (SAP: {sm.sap})")
        issues_found.append(f"{no_home_sms.count()} SM(s) without home assignment")
        print()
    
    # Check inactive SMs
    inactive_sms = User.objects.filter(role=sm_role, is_active=0).count()
    if inactive_sms > 0:
        print(f"ℹ️  Inactive SMs: {inactive_sms} (retained for historical data)")
        print()
    
    print("=" * 80)
    
    if issues_found:
        print("❌ ISSUES FOUND:")
        for issue in issues_found:
            print(f"   • {issue}")
        print()
        print("💡 RECOMMENDATION:")
        print("   Review the extra SM(s) and either:")
        print("   1. Reassign to a different role if they're not acting as SM")
        print("   2. Mark as inactive if they've left the position")
        print("   3. Assign to the correct home if they're in the wrong location")
    else:
        print("✅ ALL HOMES HAVE EXACTLY 1 SM - CORRECT!")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
