#!/usr/bin/env python3
"""
Extract Orchard Grove Master Staffing Model and 3-Week Shift Pattern
"""
import json
from collections import defaultdict
from datetime import datetime

print('📂 Loading complete demo export...')
with open('complete_demo_export.json', 'r') as f:
    data = json.load(f)

# Get Orchard Grove care home
homes = [d for d in data if d.get('model') == 'scheduling.carehome']
og_home = [h for h in homes if 'ORCHARD' in str(h.get('fields', {}).get('name', ''))]

if not og_home:
    print('❌ Orchard Grove not found')
    exit(1)

og_pk = og_home[0]['pk']
og_name = og_home[0].get('fields', {}).get('name')
print(f'\n✅ Found: {og_name} (pk: {og_pk})')

# Get Orchard Grove units
units = [d for d in data if d.get('model') == 'scheduling.unit']
og_units = [u for u in units if u.get('fields', {}).get('care_home') == og_pk]
og_unit_pks = [u['pk'] for u in og_units]

print(f'\n🏢 ORCHARD GROVE UNITS ({len(og_units)} units):')
for unit in sorted(og_units, key=lambda x: x.get('fields', {}).get('name', '')):
    fields = unit.get('fields', {})
    print(f'  • {fields.get("name")}: {fields.get("bed_capacity")} beds')

# Get Orchard Grove staff
users = [d for d in data if d.get('model') == 'scheduling.user']
og_staff = [u for u in users if u.get('fields', {}).get('unit') in og_unit_pks]

print(f'\n👥 ORCHARD GROVE STAFFING MODEL ({len(og_staff)} staff):')

# Get roles
roles = [d for d in data if d.get('model') == 'scheduling.role']
role_map = {r['pk']: r.get('fields', {}).get('name', f'Role {r["pk"]}') for r in roles}

# Count by role
role_counts = defaultdict(int)
role_staff = defaultdict(list)
for staff in og_staff:
    role_id = staff.get('fields', {}).get('role')
    role_counts[role_id] += 1
    role_staff[role_id].append(staff)

print('\n📊 STAFF BY ROLE:')
for role_id, count in sorted(role_counts.items()):
    role_name = role_map.get(role_id, f'Role {role_id}')
    print(f'  • {role_name} (ID: {role_id}): {count} staff')

# Get Orchard Grove shifts
shifts = [d for d in data if d.get('model') == 'scheduling.shift']
og_staff_pks = [s['pk'] for s in og_staff]
og_shifts = [s for s in shifts if s.get('fields', {}).get('user') in og_staff_pks]

print(f'\n📅 ORCHARD GROVE SHIFTS: {len(og_shifts):,} total shifts')

# Get shift types
shift_types = [d for d in data if d.get('model') == 'scheduling.shifttype']
shift_type_map = {st['pk']: st.get('fields', {}).get('name', f'Shift {st["pk"]}') for st in shift_types}

# Analyze 3-week patterns for each role
print('\n\n🔄 3-WEEK SHIFT PATTERNS BY ROLE:')
print('=' * 80)

for role_id in sorted(role_counts.keys()):
    role_name = role_map.get(role_id, f'Role {role_id}')
    staff_list = role_staff[role_id]
    
    print(f'\n\n📋 {role_name.upper()} - Sample Staff Patterns:')
    print('-' * 80)
    
    # Show patterns for first 3 staff in this role
    for staff in staff_list[:3]:
        staff_pk = staff['pk']
        staff_fields = staff.get('fields', {})
        staff_name = f"{staff_fields.get('first_name')} {staff_fields.get('last_name')}"
        
        # Get this staff's shifts
        staff_shifts = [s for s in og_shifts if s.get('fields', {}).get('user') == staff_pk]
        staff_shifts_sorted = sorted(staff_shifts, key=lambda x: x.get('fields', {}).get('date', ''))
        
        print(f'\n  {staff_pk}: {staff_name}')
        print(f'    Total shifts: {len(staff_shifts)}')
        
        if len(staff_shifts_sorted) >= 21:
            print(f'    3-Week Pattern (first 21 days):')
            
            # Group by week
            for week in range(3):
                week_start = week * 7
                week_end = week_start + 7
                week_shifts = staff_shifts_sorted[week_start:week_end]
                
                print(f'\n      Week {week + 1}:')
                for shift in week_shifts:
                    shift_fields = shift.get('fields', {})
                    shift_date = shift_fields.get('date')
                    shift_type_id = shift_fields.get('shift_type')
                    shift_type_name = shift_type_map.get(shift_type_id, f'Type {shift_type_id}')
                    
                    # Get day of week
                    date_obj = datetime.strptime(shift_date, '%Y-%m-%d')
                    day_name = date_obj.strftime('%a')
                    
                    print(f'        {day_name} {shift_date}: {shift_type_name}')

print('\n\n✅ ORCHARD GROVE MASTER PATTERN EXTRACTED!')
print('\nSummary:')
print(f'  • Care Home: {og_name}')
print(f'  • Units: {len(og_units)}')
print(f'  • Total Staff: {len(og_staff)}')
print(f'  • Total Shifts: {len(og_shifts):,}')
print(f'  • Roles: {len(role_counts)}')
print('\nThis is the master staffing model that should be replicated.')
