#!/usr/bin/env python3
"""
Comprehensive test file fixer - Version 2
Fixes User/StaffProfile patterns in test files without breaking syntax
"""
import re
import sys

def fix_test_file(file_path):
    """Fix a single test file with careful syntax preservation"""
    print(f"\nProcessing: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Step 1: Fix User.objects.create_user() - Replace username with sap
    old_pattern = r'User\.objects\.create_user\(\s*username='
    if re.search(old_pattern, content):
        content = re.sub(
            r"User\.objects\.create_user\(\s*username='(\w+)'",
            lambda m: f"User.objects.create_user(\n            sap='{generate_sap(m.group(1))}'",
            content
        )
        content = re.sub(
            r"User\.objects\.create_user\(\s*username=\"(\w+)\"",
            lambda m: f"User.objects.create_user(\n            sap='{generate_sap(m.group(1))}'",
            content
        )
        # Add first_name and last_name after email
        content = re.sub(
            r"(User\.objects\.create_user\([^)]*email='[^']+',)",
            r"\1\n            first_name='Test',\n            last_name='User',",
            content
        )
        changes.append("Fixed User.objects.create_user() calls")
    
    # Step 2: Remove StaffProfile.objects.create() calls
    profile_pattern = r'\s+self\.\w+_profile\s*=\s*StaffProfile\.objects\.create\([^)]+\)\s*\n'
    if re.search(profile_pattern, content):
        content = re.sub(profile_pattern, '', content)
        changes.append("Removed StaffProfile.objects.create() calls")
    
    # Step 3: Update profile references
    replacements = [
        ('self.staff_profile', 'self.staff_user.staff_profile'),
        ('self.manager_profile', 'self.manager_user.staff_profile'),
        ('self.readonly_profile', 'self.readonly_user.staff_profile'),
        ('self.full_profile', 'self.full_user.staff_profile'),
    ]
    for old, new in replacements:
        if old in content and old != new:
            content = content.replace(old, new)
            changes.append(f"Updated {old} to {new}")
    
    # Step 4: Add .unit assignments after User creation (line-by-line approach)
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check for User.objects.create_user assignment
        user_match = re.match(r'(\s+)(self\.\w+)\s*=\s*User\.objects\.create_user\(', line)
        if user_match:
            indent = user_match.group(1)
            user_var = user_match.group(2)
            
            # Find closing parenthesis
            paren_depth = 1
            j = i + 1
            while j < len(lines) and paren_depth > 0:
                new_lines.append(lines[j])
                paren_depth += lines[j].count('(') - lines[j].count(')')
                if paren_depth == 0:
                    # Check if unit assignment already exists
                    has_unit = False
                    for k in range(j+1, min(j+5, len(lines))):
                        if f'{user_var}.unit' in lines[k]:
                            has_unit = True
                            break
                    
                    if not has_unit:
                        # Skip comment lines
                        k = j + 1
                        while k < len(lines) and lines[k].strip().startswith('#'):
                            new_lines.append(lines[k])
                            k += 1
                        
                        # Insert unit assignment
                        new_lines.append(f'{indent}{user_var}.unit = self.unit')
                        new_lines.append(f'{indent}{user_var}.save()')
                        new_lines.append('')
                        changes.append(f"Added .unit assignment for {user_var}")
                        i = k - 1
                    else:
                        i = j
                    break
                j += 1
            else:
                i = j - 1
        
        i += 1
    
    content = '\n'.join(new_lines)
    
    # Step 5: Fix client.login() calls
    login_patterns = [
        (r"self\.client\.login\(username='staff',\s*password='[^']+'\)", 'self.client.force_login(self.staff_user)'),
        (r"self\.client\.login\(username='manager',\s*password='[^']+'\)", 'self.client.force_login(self.manager_user)'),
        (r"self\.client\.login\(username='testuser',\s*password='[^']+'\)", 'self.client.force_login(self.user)'),
        (r"self\.client\.login\(username='readonly',\s*password='[^']+'\)", 'self.client.force_login(self.readonly_user)'),
        (r"self\.client\.login\(username='full',\s*password='[^']+'\)", 'self.client.force_login(self.full_user)'),
    ]
    for pattern, replacement in login_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes.append("Fixed client.login() calls")
    
    # Write if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  ✅ Fixed ({len(changes)} change types)")
        for change in set(changes):
            print(f"     - {change}")
        return True
    else:
        print(f"  ℹ️  No changes needed")
        return False

def generate_sap(username):
    """Generate SAP number based on username"""
    sap_map = {
        'staff': '200001',
        'manager': '200002',
        'testuser': '200003',
        'readonly': '200004',
        'full': '200005',
    }
    return sap_map.get(username, '200099')

# Fix all files
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
        import traceback
        traceback.print_exc()

print(f"\n✅ Fixed {fixed_count}/{len(test_files)} files")
print("\nVerifying syntax...")
for file_path in test_files:
    try:
        import py_compile
        py_compile.compile(file_path, doraise=True)
        print(f"  ✅ {file_path}")
    except SyntaxError as e:
        print(f"  ❌ {file_path}: {e}")
