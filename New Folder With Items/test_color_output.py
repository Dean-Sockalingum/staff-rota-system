"""
Quick test to verify color positions are being assigned correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import Unit, CareHome

# Check Hawthorn House units
hawthorn = CareHome.objects.get(name='HAWTHORN_HOUSE')
units = Unit.objects.filter(care_home=hawthorn, is_active=True).order_by('name')

print("=== HAWTHORN HOUSE UNITS (Alphabetical Order) ===")
print("Position | Unit Name")
print("-" * 40)

all_units = sorted([u.name for u in units])
for position, full_name in enumerate(all_units, start=1):
    clean_name = full_name.split('_')[-1]
    color_position = ((position - 1) % 9) + 1
    colors = {
        1: "Purple (#9C27B0)",
        2: "Deep Purple (#673AB7)",
        3: "Indigo (#3F51B5)",
        4: "Blue (#2196F3)",
        5: "Teal (#009688)",
        6: "Green (#4CAF50)",
        7: "Orange (#FF9800)",
        8: "Deep Orange (#FF5722)",
        9: "Pink (#E91E63)"
    }
    print(f"{color_position}        | {clean_name} → {colors[color_position]}")

print("\n=== CSS CLASS EXAMPLE ===")
print(f'<div class="unit-cell unit-pos-{color_position}">Bluebell</div>')
