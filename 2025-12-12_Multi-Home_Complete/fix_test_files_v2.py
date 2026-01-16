#!/usr/bin/env python3
"""
Comprehensive test file fixer - handles all model field corrections
"""

import re
import sys

def fix_file(filepath):
    """Fix a single test file"""
    print(f"\n{'='*60}")
    print(f"Processing: {filepath}")
    print('='*60)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # 1. Fix CareHome.objects.create()
    # Pattern: name="Test Care Home", address="123 Test St"
    old_pattern = r'name="Test Care Home",\s*address="123 Test St"'
    new_pattern = 'name="ORCHARD_GROVE",\n            bed_capacity=40,\n            location_address="123 Test St"'
    count = len(re.findall(old_pattern, content))
    if count > 0:
        content = re.sub(old_pattern, new_pattern, content)
        changes.append(f"Fixed {count} CareHome.objects.create() calls")
    
    # 2. Fix User.objects.create_user() - remove username parameter
    # Find all User.objects.create_user with username
    user_pattern = r"User\.objects\.create_user\(\s*username='testuser',\s*email='([^']+)',\s*password='([^']+)'\s*\)"
    matches = list(re.finditer(user_pattern, content))
    
    if matches:
        # Replace each match with unique SAP numbers
        for i, match in enumerate(matches, start=1):
            sap = f"20{i:04d}"  # Generates 200001, 200002, etc.
            email = match.group(1)
            password = match.group(2)
            replacement = f"""User.objects.create_user(
            sap='{sap}',
            first_name='Test',
            last_name='User',
            email='{email}',
            password='{password}'
        )"""
            content = content[:match.start()] + replacement + content[match.end():]
            # Recalculate positions for next iteration
            matches = list(re.finditer(user_pattern, content))
        changes.append(f"Fixed User.objects.create_user() to use SAP instead of username")
    
    # 3. Fix StaffProfile.objects.create()
    # Pattern: sap_number and unit fields
    profile_patterns = [
        (r"StaffProfile\.objects\.create\(\s*user=self\.user,\s*sap_number='[^']+',\s*unit=self\.unit\s*\)",
         "StaffProfile.objects.create(\n            user=self.user,\n            job_title='Care Assistant'\n        )"),
        (r"StaffProfile\.objects\.create\(\s*user=self\.user,\s*sap_number='[^']+',\s*unit=self\.unit,\s*permission_level='[^']+'\s*\)",
         "StaffProfile.objects.create(\n            user=self.user,\n            job_title='Care Assistant'\n        )"),
        (r"self\.profile = StaffProfile\.objects\.create\(\s*user=self\.user,\s*sap_number='[^']+',\s*unit=self\.unit\s*\)",
         "self.profile = StaffProfile.objects.create(\n            user=self.user,\n            job_title='Care Assistant'\n        )"),
        (r"self\.profile = StaffProfile\.objects\.create\(\s*user=self\.user,\s*sap_number='[^']+',\s*unit=self\.unit,\s*permission_level='[^']+'\s*\)",
         "self.profile = StaffProfile.objects.create(\n            user=self.user,\n            job_title='Care Assistant'\n        )"),
    ]
    
    profile_count = 0
    for pattern, replacement in profile_patterns:
        count = len(re.findall(pattern, content))
        if count > 0:
            content = re.sub(pattern, replacement, content)
            profile_count += count
    
    if profile_count > 0:
        changes.append(f"Fixed {profile_count} StaffProfile.objects.create() calls")
    
    # 4. Add user.unit = self.unit after User.objects.create_user()
    # Find User.objects.create_user blocks and add unit assignment
    user_create_pattern = r"(self\.user = User\.objects\.create_user\([^)]+\))"
    matches = re.finditer(user_create_pattern, content)
    
    for match in reversed(list(matches)):  # Reverse to maintain positions
        insert_pos = match.end()
        # Check if unit assignment already exists
        next_lines = content[insert_pos:insert_pos+100]
        if 'self.user.unit' not in next_lines:
            insertion = "\n        self.user.unit = self.unit\n        self.user.save()"
            content = content[:insert_pos] + insertion + content[insert_pos:]
    
    # 5. Fix client.login() to use force_login()
    login_pattern = r"self\.client\.login\(username='testuser', password='testpass123'\)"
    count = len(re.findall(login_pattern, content))
    if count > 0:
        content = re.sub(login_pattern, "self.client.force_login(self.user)", content)
        changes.append(f"Fixed {count} client.login() calls to use force_login()")
    
    # 6. Fix manager profiles with sap_number
    manager_pattern = r"self\.manager_profile = StaffProfile\.objects\.create\(\s*user=self\.manager,\s*sap_number='[^']+',\s*unit=self\.unit,?\s*\)"
    count = len(re.findall(manager_pattern, content))
    if count > 0:
        content = re.sub(manager_pattern, 
                        "self.manager_profile = StaffProfile.objects.create(\n            user=self.manager,\n            job_title='Care Manager'\n        )",
                        content)
        changes.append(f"Fixed {count} manager StaffProfile creations")
    
    # Save if changes were made
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print("✅ CHANGES MADE:")
        for change in changes:
            print(f"   - {change}")
        return True
    else:
        print("⚠️  No changes needed")
        return False

def main():
    files = [
        'scheduling/tests/test_task57_form_autosave.py',
        'scheduling/tests/test_task59_leave_calendar.py',
    ]
    
    total_fixed = 0
    for filepath in files:
        try:
            if fix_file(filepath):
                total_fixed += 1
        except Exception as e:
            print(f"❌ ERROR processing {filepath}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: Fixed {total_fixed}/{len(files)} files")
    print('='*60)

if __name__ == '__main__':
    main()
