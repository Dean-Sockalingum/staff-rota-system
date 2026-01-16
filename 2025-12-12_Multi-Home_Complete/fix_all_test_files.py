#!/usr/bin/env python3
"""
Comprehensive test file fixer for all remaining test files.
Fixes:
1. User.objects.create_user(username=...) → User.objects.create_user(sap=...)
2. Remove manual StaffProfile.objects.create() calls
3. Add user.unit assignments
4. Replace client.login() with client.force_login()
5. Update references from self.profile to self.user.staff_profile
"""
import re
import sys

def fix_test_file(file_path):
    """Fix a single test file"""
    print(f"\nProcessing: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Step 1: Fix User.objects.create_user() calls
    # Replace username parameter with sap
    content = re.sub(
        r'User\.objects\.create_user\(\s*username=([\'"])(\w+)\1',
        r'User.objects.create_user(\n            sap=\1200099\1,\n            first_name=\1Test\1,\n            last_name=\1User\1',
        content
    )
    
    # Step 2: Remove StaffProfile.objects.create() and update references
    # Remove profile assignments
    content = re.sub(
        r'\s*self\.(profile|staff_profile|manager_profile)\s*=\s*StaffProfile\.objects\.create\([^)]+\)\s*\n',
        '',
        content,
        flags=re.MULTILINE
    )
    
    # Remove standalone StaffProfile.objects.create in loops
    content = re.sub(
        r'\s*StaffProfile\.objects\.create\(\s*user=[^,]+,\s*(?:sap_number=[^,]+,\s*)?(?:unit=[^,]+,?\s*)?(?:permission_level=[^,]+,?\s*)?(?:job_title=[^\n]+)?\s*\)\s*\n',
        '',
        content,
        flags=re.MULTILINE
    )
    
    # Step 3: Update references
    content = content.replace('self.staff_profile', 'self.staff_user.staff_profile')
    content = content.replace('self.manager_profile', 'self.manager_user.staff_profile')  
    content = content.replace('self.readonly_profile', 'self.readonly_user.staff_profile')
    content = content.replace('self.full_profile', 'self.full_user.staff_profile')
    content = content.replace('self.profile', 'self.user.staff_profile')
    
    # Step 4: Fix client.login() calls
    content = re.sub(
        r"self\.client\.login\(username=['\"](\w+)['\"],\s*password=['\"][^'\"]+['\"]\)",
        r'self.client.force_login(self.\1_user)',
        content
    )
    content = re.sub(
        r"self\.client\.login\(username=['\"]testuser['\"],\s*password=['\"][^'\"]+['\"]\)",
        r'self.client.force_login(self.user)',
        content
    )
    
    # Step 5: Fix indentation issues (comment followed immediately by def)
    content = re.sub(
        r'(# .*care_home.*\))(\s{0,3})(def test_)',
        r'\1\n    \n    \3',
        content
    )
    
    # Step 6: Add .unit assignments after User creation
    # This is complex, so we'll do it line by line
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this is a User.objects.create_user assignment
        user_match = re.match(r'\s*(self\.\w+)\s*=\s*User\.objects\.create_user\(', line)
        if user_match:
            user_var = user_match.group(1)
            
            # Look ahead to find the closing )
            j = i + 1
            while j < len(lines) and j < i + 15:
                if ')' in lines[j]:
                    # Found closing paren
                    # Check if there's already a .unit assignment in the next few lines
                    has_unit = False
                    for k in range(j+1, min(j+5, len(lines))):
                        if f'{user_var}.unit' in lines[k]:
                            has_unit = True
                            break
                    
                    if not has_unit:
                        # Insert unit assignment after the comment line (if present)
                        insert_pos = j + 1
                        while insert_pos < len(lines) and lines[insert_pos].strip().startswith('#'):
                            new_lines.append(lines[insert_pos])
                            insert_pos += 1
                            i += 1
                        
                        # Insert the unit assignment
                        indent = '        '
                        new_lines.append(f'{indent}{user_var}.unit = self.unit')
                        new_lines.append(f'{indent}{user_var}.save()')
                        new_lines.append('')
                    break
                j += 1
        
        i += 1
    
    content = '\n'.join(new_lines)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  ✅ Fixed")
        return True
    else:
        print(f"  ℹ️  No changes needed")
        return False

# Fix all remaining test files
test_files = [
    'scheduling/tests/test_phase6_integration.py',
    'scheduling/tests/test_shift_optimizer.py',
    'scheduling/tests/test_staffing_safeguards.py',
    'scheduling/tests/test_task55_activity_feed.py',
    'scheduling/tests/test_core.py',
]

fixed_count = 0
for file_path in test_files:
    try:
        if fix_test_file(file_path):
            fixed_count += 1
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\n✅ Fixed {fixed_count}/{len(test_files)} files")
