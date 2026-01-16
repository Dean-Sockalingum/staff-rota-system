#!/usr/bin/env python3
"""
Carefully fix test_phase6_integration.py
"""
import re

file_path = 'scheduling/tests/test_phase6_integration.py'

with open(file_path, 'r') as f:
    content = f.read()

# Fix User.objects.create_user - replace username with sap
content = re.sub(
    r"User\.objects\.create_user\(\s*username='staff'",
    "User.objects.create_user(\n            sap='200001',\n            first_name='Staff',\n            last_name='User'",
    content
)
content = re.sub(
    r"User\.objects\.create_user\(\s*username='manager'",
    "User.objects.create_user(\n            sap='200002',\n            first_name='Manager',\n            last_name='User'",
    content
)
content = re.sub(
    r"User\.objects\.create_user\(\s*username='testuser'",
    "User.objects.create_user(\n            sap='200003',\n            first_name='Test',\n            last_name='User'",
    content
)
content = re.sub(
    r"User\.objects\.create_user\(\s*username='readonly'",
    "User.objects.create_user(\n            sap='200004',\n            first_name='Read',\n            last_name='Only'",
    content
)
content = re.sub(
    r"User\.objects\.create_user\(\s*username='full'",
    "User.objects.create_user(\n            sap='200005',\n            first_name='Full',\n            last_name='Access'",
    content
)

# Remove StaffProfile.objects.create() calls with old fields
content = re.sub(
    r'\s+self\.(staff_profile|manager_profile|readonly_profile|full_profile)\s*=\s*StaffProfile\.objects\.create\([^)]+\)\s*\n',
    '',
    content,
    flags=re.MULTILINE
)

# Remove profile = StaffProfile.objects.create in loops
content = re.sub(
    r'\s+profile\s*=\s*StaffProfile\.objects\.create\([^)]+\)\s*\n',
    '',
    content,
    flags=re.MULTILINE
)

# Remove lines appending to staff_profiles
content = re.sub(
    r'\s+self\.\w+\.staff_profiles\.append\([^)]+\)\s*\n',
    '',
    content
)

# Remove self.profile = StaffProfile.objects.create
content = re.sub(
    r'\s+self\.profile\s*=\s*StaffProfile\.objects\.create\([^)]+\)\s*\n',
    '',
    content,
    flags=re.MULTILINE
)

# Update profile references
content = content.replace('self.staff_profile', 'self.staff_user.staff_profile')
content = content.replace('self.manager_profile', 'self.manager_user.staff_profile')
content = content.replace('self.readonly_profile', 'self.readonly_user.staff_profile')
content = content.replace('self.full_profile', 'self.full_user.staff_profile')
content = content.replace('self.profile', 'self.user.staff_profile')

# Add .unit assignments after User creation - do manually for key ones
lines = content.split('\n')
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    
    # Check for specific User creation patterns and add unit assignment
    if re.match(r'\s+(self\.(staff_user|manager_user|user|readonly_user|full_user|manager))\s*=\s*User\.objects\.create_user\(', line):
        user_var = re.match(r'\s+(self\.\w+)', line).group(1)
        
        # Find closing paren
        j = i + 1
        paren_count = 1
        while j < len(lines) and paren_count > 0:
            new_lines.append(lines[j])
            paren_count += lines[j].count('(') - lines[j].count(')')
            j += 1
        
        # Skip comment if present
        while j < len(lines) and lines[j].strip().startswith('#'):
            new_lines.append(lines[j])
            j += 1
        
        # Add unit assignment
        indent = '        '
        new_lines.append(f'{indent}{user_var}.unit = self.unit')
        new_lines.append(f'{indent}{user_var}.save()')
        new_lines.append('')
        
        i = j - 1
    
    i += 1

content = '\n'.join(new_lines)

# Fix client.login() calls
content = re.sub(r"self\.client\.login\(username='staff',\s*password='[^']+'\)", 'self.client.force_login(self.staff_user)', content)
content = re.sub(r"self\.client\.login\(username='manager',\s*password='[^']+'\)", 'self.client.force_login(self.manager_user)', content)
content = re.sub(r"self\.client\.login\(username='testuser',\s*password='[^']+'\)", 'self.client.force_login(self.user)', content)
content = re.sub(r"self\.client\.login\(username='readonly',\s*password='[^']+'\)", 'self.client.force_login(self.readonly_user)', content)
content = re.sub(r"self\.client\.login\(username='full',\s*password='[^']+'\)", 'self.client.force_login(self.full_user)', content)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Fixed test_phase6_integration.py")

# Verify syntax
import py_compile
try:
    py_compile.compile(file_path, doraise=True)
    print("✅ Syntax valid")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
