#!/usr/bin/env python3
"""
Fix Admin User - Remove SM role and make it a superuser
"""

import os
import sys
import django

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User

def main():
    print("=" * 80)
    print("🔧 FIXING ADMIN USER - REMOVE SM ROLE, SET AS SUPERUSER")
    print("=" * 80)
    print()
    
    try:
        admin = User.objects.get(sap='000745')
        
        print("📋 CURRENT STATE:")
        print(f"   Name: {admin.first_name} {admin.last_name}")
        print(f"   SAP: {admin.sap}")
        print(f"   Role: {admin.role.name if admin.role else 'None'}")
        print(f"   Home Unit: {admin.home_unit.get_name_display() if admin.home_unit else 'None'}")
        print(f"   is_superuser: {admin.is_superuser}")
        print(f"   is_staff: {admin.is_staff}")
        print(f"   is_active: {admin.is_active}")
        print()
        
        # Update admin user
        print("🔄 APPLYING CHANGES...")
        admin.role = None  # Remove SM role
        admin.is_superuser = True  # Full system access
        admin.is_staff = True  # Django admin access
        admin.is_active = True  # Keep active
        admin.save()
        
        print("   ✅ Removed SM role")
        print("   ✅ Set as superuser (full system access)")
        print("   ✅ Set as staff (Django admin access)")
        print()
        
        # Verify changes
        admin.refresh_from_db()
        
        print("📋 NEW STATE:")
        print(f"   Name: {admin.first_name} {admin.last_name}")
        print(f"   SAP: {admin.sap}")
        print(f"   Role: {admin.role.name if admin.role else 'None'}")
        print(f"   Home Unit: {admin.home_unit.get_name_display() if admin.home_unit else 'None'}")
        print(f"   is_superuser: {admin.is_superuser}")
        print(f"   is_staff: {admin.is_staff}")
        print(f"   is_active: {admin.is_active}")
        print()
        
        print("=" * 80)
        print("✅ ADMIN USER UPDATED SUCCESSFULLY")
        print()
        print("💡 This account now:")
        print("   • Has NO specific role (not SM, not HOS)")
        print("   • Has SUPERUSER privileges (access to all system features)")
        print("   • Can access Django admin interface")
        print("   • Can manage all homes and all staff")
        print()
        print("=" * 80)
        
    except User.DoesNotExist:
        print("❌ Admin user (SAP: 000745) not found!")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
