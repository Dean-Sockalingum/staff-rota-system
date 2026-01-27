import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, CareHome
from collections import defaultdict

print("=" * 80)
print("CHECKING FOR DUPLICATE STAFF ACROSS HOMES")
print("=" * 80)

homes = CareHome.objects.all().order_by('name')

for home in homes:
    print(f"\n{home.get_name_display()} ({home.name})")
    print("-" * 80)
    
    units = home.units.all()
    staff = User.objects.filter(unit__in=units, is_active=True)
    
    # Count unique staff by SAP
    unique_staff = staff.values('sap').distinct().count()
    total_staff = staff.count()
    
    print(f"Total staff records: {total_staff}")
    print(f"Unique staff (by SAP): {unique_staff}")
    
    if total_staff > unique_staff:
        print(f"⚠️  DUPLICATES FOUND: {total_staff - unique_staff} duplicate records")
        
        # Find which staff appear in multiple units
        name_counts = defaultdict(list)
        for s in staff:
            key = f"{s.first_name} {s.last_name} ({s.sap})"
            name_counts[key].append(s.unit.name)
        
        duplicates = {k: v for k, v in name_counts.items() if len(v) > 1}
        
        if duplicates:
            print(f"\nStaff in multiple units within {home.get_name_display()}:")
            for name, units_list in sorted(duplicates.items())[:10]:
                print(f"  {name}: {len(units_list)} units - {', '.join(units_list)}")
            
            if len(duplicates) > 10:
                print(f"  ... and {len(duplicates) - 10} more")
    else:
        print("✓ No duplicates - all staff unique")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("Expected: Each home should have ~178 unique staff like Orchard Grove")
print("Orchard Grove and Victoria Gardens appear correct")
print("Hawthorn House, Meadowburn, and Riverside likely have staff in multiple units")
