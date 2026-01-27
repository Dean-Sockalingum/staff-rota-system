#!/usr/bin/env python3
"""Add sorting to shift categories."""

with open("/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/views.py", "r") as f:
    content = f.read()

# Add sorting after day_management list creation
old_mgmt = """        day_management = [
            s for s in day_shifts
            if getattr(getattr(s.user, 'role', None), 'name', '') in ['SM', 'OM']
        ]
        # MGMT never works nightshift - empty list to avoid taking up space
        night_management = []"""

new_mgmt = """        day_management = [
            s for s in day_shifts
            if getattr(getattr(s.user, 'role', None), 'name', '') in ['SM', 'OM']
        ]
        # Sort management: SM first, then OM, alphabetically by last name
        day_management.sort(key=lambda s: (
            0 if getattr(getattr(s.user, 'role', None), 'name', '') == 'SM' else 1,
            s.user.last_name if s.user else '',
            s.user.first_name if s.user else ''
        ))
        # MGMT never works nightshift - empty list to avoid taking up space
        night_management = []"""

content = content.replace(old_mgmt, new_mgmt)

# Add sorting after day_supernumerary_duty
old_super_day = """        day_supernumerary_duty = [
            s for s in day_shifts
            if getattr(getattr(s.user, 'role', None), 'name', '') in ['SSCW'] and s not in day_management
        ]
        day_supernumerary_admin = []  # No ADMIN shift type in database
        day_supernumerary = day_supernumerary_duty + day_supernumerary_admin"""

new_super_day = """        day_supernumerary_duty = [
            s for s in day_shifts
            if getattr(getattr(s.user, 'role', None), 'name', '') in ['SSCW'] and s not in day_management
        ]
        # Sort supernumerary alphabetically by last name
        day_supernumerary_duty.sort(key=lambda s: (
            s.user.last_name if s.user else '',
            s.user.first_name if s.user else ''
        ))
        day_supernumerary_admin = []  # No ADMIN shift type in database
        day_supernumerary = day_supernumerary_duty + day_supernumerary_admin"""

content = content.replace(old_super_day, new_super_day)

# Add sorting after night_supernumerary
old_super_night = """        night_supernumerary = [
            s for s in night_shifts 
            if getattr(getattr(s.user, 'role', None), 'name', '') in ['SSCWN'] and s not in night_management
        ]"""

new_super_night = """        night_supernumerary = [
            s for s in night_shifts 
            if getattr(getattr(s.user, 'role', None), 'name', '') in ['SSCWN'] and s not in night_management
        ]
        # Sort supernumerary alphabetically by last name
        night_supernumerary.sort(key=lambda s: (
            s.user.last_name if s.user else '',
            s.user.first_name if s.user else ''
        ))"""

content = content.replace(old_super_night, new_super_night)

with open("/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/views.py", "w") as f:
    f.write(content)

print("✓ Added sorting to management and supernumerary sections")
