#!/usr/bin/env python3
"""
Quick fix script for test_phase6_integration.py
Converts old model structure to new structure
"""

import re

# Read the file
with open('scheduling/tests/test_phase6_integration.py', 'r') as f:
    content = f.read()

# Fix CareHome creations
content = re.sub(
    r'CareHome\.objects\.create\(\s*name="Test Care Home",\s*address="123 Test St"\s*\)',
    """CareHome.objects.create(
            name='ORCHARD_GROVE',
            bed_capacity=30,
            location_address='123 Test St'
        )""",
    content
)

# Remove StaffProfile import
content = content.replace('from scheduling.models import TrainingRecord, SupervisionRecord, TrainingCourse',
                         'from scheduling.models import TrainingRecord, SupervisionRecord, TrainingCourse, Role')

# Remove LeaveType model usage - it doesn't exist
content = re.sub(
    r'# Create leave type.*?is_paid=True\s*\)',
    "# LeaveRequest uses CharField with LEAVE_TYPES choices, not a separate model",
    content,
    flags=re.DOTALL
)

#Remove StaffProfile creations and references
content = re.sub(
    r'self\.staff_profile = StaffProfile\.objects\.create\([^)]+\)',
    '# StaffProfile replaced by User model',
    content
)
content = re.sub(
    r'self\.manager_profile = StaffProfile\.objects\.create\([^)]+\)',
    '# StaffProfile replaced by User model',
    content
)
content = re.sub(
    r'self\.profile = StaffProfile\.objects\.create\([^)]+\)',
    '# StaffProfile replaced by User model',
    content
)
content = re.sub(
    r'self\.readonly_profile = StaffProfile\.objects\.create\([^)]+\)',
    '# StaffProfile replaced by User model',
    content
)
content = re.sub(
    r'self\.full_profile = StaffProfile\.objects\.create\([^)]+\)',
    '# StaffProfile replaced by User model',
    content
)
content = re.sub(
    r'profile = StaffProfile\.objects\.create\([^)]+\)',
    '# StaffProfile replaced by User model',
    content
)

# Fix User.objects.create_user calls - add SAP as first param
content = re.sub(
    r'User\.objects\.create_user\(\s*username=\'(\w+)\',\s*email=\'([^\']+)\',\s*password=\'([^\']+)\'\s*\)',
    lambda m: f"""User.objects.create_user(
            sap='123456',
            password='{m.group(3)}',
            email='{m.group(2)}',
            first_name='{m.group(1).title()}',
            last_name='User'
        )""",
    content
)

# Fix care_home_access references - this doesn't exist anymore
content = re.sub(
    r'self\.\w+_user\.care_home_access\.add\(self\.care_home\)',
    '# care_home_access removed - users are assigned via unit1/unit2',
    content
)

# Fix LeaveRequest creations - change staff_profile to user, leave_type to string
content = re.sub(
    r'LeaveRequest\.objects\.create\(\s*staff_profile=self\.(\w+)_profile,\s*leave_type=self\.leave_type,',
    lambda m: f"LeaveRequest.objects.create(\n            user=self.{m.group(1)}_user,\n            leave_type='ANNUAL',\n            days_requested=5,",
    content
)

# Fix approval references
content = re.sub(
    r'approved_by = self\.manager_profile',
    'approved_by = self.manager_user',
    content
)

# Write the file
with open('scheduling/tests/test_phase6_integration.py', 'w') as f:
    f.write(content)

print("✅ Fixed test_phase6_integration.py")
