#!/usr/bin/env python3
"""
Fix test files to use correct model field names
"""

import re

def fix_care_home_create(content):
    """Fix CareHome.objects.create() calls"""
    # Pattern: CareHome.objects.create with 'address' field
    pattern = r'CareHome\.objects\.create\(\s*name="Test Care Home",\s*address="123 Test St"\s*\)'
    replacement = 'CareHome.objects.create(\n            name="ORCHARD_GROVE",\n            bed_capacity=40,\n            location_address="123 Test St"\n        )'
    content = re.sub(pattern, replacement, content)
    
    # Also fix any remaining with just name and address
    pattern = r'name="Test Care Home",\s*\n\s*address='
    replacement = 'name="ORCHARD_GROVE",\n            bed_capacity=40,\n            location_address='
    content = re.sub(pattern, replacement, content)
    
    return content

def fix_user_create(content):
    """Fix User.objects.create_user() calls"""
    # Pattern: username parameter
    pattern = r"User\.objects\.create_user\(\s*username='testuser',\s*\n\s*email='test@example\.com',\s*\n\s*password='testpass123'\s*\)"
    
    # Find all matches and replace with incrementing SAP numbers
    matches = list(re.finditer(pattern, content))
    for i, match in enumerate(matches, start=1):
        sap = f"20000{i}"
        replacement = f"""User.objects.create_user(
            sap='{sap}',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpass123'
        )"""
        content = content[:match.start()] + replacement + content[match.end():]
    
    return content

def fix_staff_profile_create(content):
    """Fix StaffProfile.objects.create() calls"""
    # Pattern: sap_number and unit fields
    pattern = r"StaffProfile\.objects\.create\(\s*user=self\.user,\s*\n\s*sap_number='[\d]+',\s*\n\s*unit=self\.unit\s*\)"
    replacement = "StaffProfile.objects.create(\n            user=self.user,\n            job_title='Care Assistant'\n        )"
    content = re.sub(pattern, replacement, content)
    
    # Also fix with permission_level
    pattern = r"StaffProfile\.objects\.create\(\s*user=self\.user,\s*\n\s*sap_number='[\d]+',\s*\n\s*unit=self\.unit,?\s*\n\s*permission_level='[\w]+'\s*\)"
    content = re.sub(pattern, replacement, content)
    
    # Fix profile variable assignments
    pattern = r"self\.profile = StaffProfile\.objects\.create\(\s*user=self\.user,\s*\n\s*sap_number='[\d]+',\s*\n\s*unit=self\.unit\s*\)"
    replacement = "self.profile = StaffProfile.objects.create(\n            user=self.user,\n            job_title='Care Assistant'\n        )"
    content = re.sub(pattern, replacement, content)
    
    # Fix with permission_level in profile
    pattern = r"self\.profile = StaffProfile\.objects\.create\(\s*user=self\.user,\s*\n\s*sap_number='[\d]+',\s*\n\s*unit=self\.unit,?\s*\n\s*permission_level='[\w]+'\s*\)"
    content = re.sub(pattern, replacement, content)
    
    return content

def add_unit_assignment(content):
    """Add self.user.unit = self.unit after user creation"""
    # Find User.objects.create_user and add unit assignment after
    pattern = r"(self\.user = User\.objects\.create_user\([^)]+\))"
    replacement = r"\1\n        self.user.unit = self.unit\n        self.user.save()"
    content = re.sub(pattern, replacement, content)
    
    return content

def fix_login_calls(content):
    """Fix client.login() calls to use SAP instead of username"""
    content = re.sub(r"self\.client\.login\(username='testuser', password='testpass123'\)", 
                     "self.client.force_login(self.user)", content)
    return content

def main():
    files = [
        'scheduling/tests/test_task57_form_autosave.py',
        'scheduling/tests/test_task59_leave_calendar.py',
    ]
    
    for filepath in files:
        print(f"Processing {filepath}...")
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all fixes
            content = fix_care_home_create(content)
            content = fix_user_create(content)
            content = fix_staff_profile_create(content)
            content = add_unit_assignment(content)
            content = fix_login_calls(content)
            
            if content != original_content:
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"✅ Fixed {filepath}")
            else:
                print(f"⚠️  No changes needed in {filepath}")
                
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")

if __name__ == '__main__':
    main()
