"""
Check existing staff in production database
"""
import os
import sys
import django

sys.path.insert(0, '/home/staff-rota-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Unit, Role

print("\n" + "="*80)
print("CURRENT STAFF IN PRODUCTION DATABASE")
print("="*80 + "\n")

total_users = User.objects.count()
print(f"Total Users: {total_users}\n")

if total_users == 0:
    print("⚠️  NO USERS FOUND - Database needs to be seeded with staff\n")
else:
    print("Sample Staff (first 20):")
    print(f"{'SAP':8} | {'Name':30} | {'Unit':20} | {'Role':15}")
    print("-" * 80)
    
    users = User.objects.select_related('unit', 'role').all()[:20]
    for u in users:
        unit_name = u.unit.name if u.unit else "NO UNIT"
        role_name = u.role.name if u.role else "NO ROLE"
        full_name = f"{u.first_name} {u.last_name}"
        print(f"{u.sap:8} | {full_name:30} | {unit_name:20} | {role_name:15}")

print("\n" + "="*80)
print("UNITS IN DATABASE")
print("="*80 + "\n")

units = Unit.objects.filter(is_active=True).order_by('care_home__name', 'name')
for unit in units:
    staff_count = User.objects.filter(unit=unit, is_active=True).count()
    print(f"  {unit.care_home.name:20} | {unit.name:20} | Staff: {staff_count}")

print(f"\n✅ Check complete\n")
