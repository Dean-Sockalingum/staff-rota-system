#!/usr/bin/env python3
"""
Refactor Phase 6 integration tests to use current models
"""

import re

file_path = 'scheduling/tests/test_phase6_integration.py'

with open(file_path, 'r') as f:
    content = f.read()

# Fix 1: CareHome.objects.create - replace address with location_address and add bed_capacity
content = re.sub(
    r'CareHome\.objects\.create\(\s*name="Test Care Home",\s*address="([^"]+)"\s*\)',
    r"CareHome.objects.create(\n            name='ORCHARD_GROVE',\n            bed_capacity=30,\n            location_address='\1'\n        )",
    content
)

# Fix 2: Remove all StaffProfile.objects.create() and replace with User.objects.create_user()
# This is complex - let's do it more carefully with a function

def replace_staff_profile(match):
    """Replace StaffProfile.objects.create with User.objects.create_user"""
    indent = match.group(1)
    var_name = match.group(2)
    
    # Generate SAP based on variable name
    sap_map = {
        'staff_profile': '100001',
        'manager_profile': '100002',
        'profile': '100003',
        'readonly_profile': '100004',
        'full_profile': '100005',
    }
    sap = sap_map.get(var_name, '100001')
    
    # Determine role and permissions
    if 'manager' in var_name:
        role_name = 'OPERATIONS_MANAGER'
        is_management = True
        can_approve = True
    elif 'readonly' in var_name:
        role_name = 'SSCW'
        is_management = False
        can_approve = False
    elif 'full' in var_name:
        role_name = 'OPERATIONS_MANAGER'
        is_management = True
        can_approve = True
    else:
        role_name = 'SSCW'
        is_management = False
        can_approve = False
    
    # Create role first
    role_code = f"{indent}# Create role for {var_name}\n"
    role_code += f"{indent}{var_name}_role = Role.objects.get_or_create(\n"
    role_code += f"{indent}    name='{role_name}',\n"
    role_code += f"{indent}    defaults={{\n"
    role_code += f"{indent}        'is_management': {is_management},\n"
    role_code += f"{indent}        'can_approve_leave': {can_approve}\n"
    role_code += f"{indent}    }}\n"
    role_code += f"{indent})[0]\n\n"
    
    # Create user
    user_code = f"{indent}{var_name} = User.objects.create_user(\n"
    user_code += f"{indent}    sap='{sap}',\n"
    user_code += f"{indent}    password='testpass123',\n"
    user_code += f"{indent}    email='{var_name}@test.com',\n"
    user_code += f"{indent}    first_name='Test',\n"
    user_code += f"{indent}    last_name='User',\n"
    user_code += f"{indent}    role={var_name}_role\n"
    user_code += f"{indent})"
    
    return role_code + user_code

# Match StaffProfile.objects.create and replace
content = re.sub(
    r'^(\s+)(self\.\w+) = StaffProfile\.objects\.create\([^)]+\)',
    replace_staff_profile,
    content,
    flags=re.MULTILINE
)

# Fix 3: Remove LeaveType.objects.create() - leave_type is now a CharField
content = re.sub(
    r'\s+self\.leave_type = LeaveType\.objects\.create\([^)]+\)\n',
    '',
    content
)

# Fix 4: Fix LeaveRequest.objects.create() - use leave_type='ANNUAL' instead of leave_type=self.leave_type
content = re.sub(
    r'leave_type=self\.leave_type',
    r"leave_type='ANNUAL'",
    content
)

# Fix 5: Add days_requested=1 to LeaveRequest.objects.create()
# Find LeaveRequest.objects.create that don't have days_requested
def add_days_requested(match):
    create_call = match.group(0)
    if 'days_requested' not in create_call:
        # Add before the closing parenthesis
        create_call = create_call.rstrip(')\n') + ',\n            days_requested=1\n        )'
    return create_call

content = re.sub(
    r'LeaveRequest\.objects\.create\([^)]+\)',
    add_days_requested,
    content,
    flags=re.DOTALL
)

# Fix 6: Replace staff_profile references with user references in LeaveRequest
content = re.sub(r'staff_profile=self\.(\w+)', r'user=self.\1', content)
content = re.sub(r'staff_profile=profile', r'user=profile', content)

# Fix 7: Update User.objects.create_user calls to have proper format (already there but ensure SAP is 6 digits)
# This is already handled above

# Write the updated content
with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Refactored {file_path}")
print("Fixed:")
print("  - CareHome: address → location_address, added bed_capacity")  
print("  - StaffProfile → User with proper create_user()")
print("  - Removed LeaveType model references")
print("  - Fixed LeaveRequest: staff_profile → user, added days_requested")
