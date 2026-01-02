#!/usr/bin/env python3
"""
Check Care Inspectorate IDs and populate baseline CI ratings
"""

import os
import sys
import django

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models_multi_home import CareHome

def main():
    print("=" * 80)
    print("🔍 CARE INSPECTORATE REGISTRATION CHECK")
    print("=" * 80)
    print()
    
    homes = CareHome.objects.all().order_by('name')
    
    print("📋 CURRENT CARE INSPECTORATE IDs:")
    print("-" * 80)
    
    for home in homes:
        print(f"{home.get_name_display()}:")
        print(f"   Care Inspectorate ID: {home.care_inspectorate_id}")
        print(f"   Registration Number: {home.registration_number or 'Not set'}")
        print()
    
    print("=" * 80)
    print()
    print("💡 Please provide the actual Care Inspectorate service numbers (CS numbers)")
    print("   for each home so I can update them and populate baseline CI ratings.")
    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
