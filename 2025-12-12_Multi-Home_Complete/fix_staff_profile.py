#!/usr/bin/env python3
"""
Fix StaffProfile creation in test_task59_leave_calendar.py
"""
import re

file_path = 'scheduling/tests/test_task59_leave_calendar.py'

# Read the file
with open(file_path, 'r') as f:
    content = f.read()

# Pattern to match StaffProfile.objects.create with sap_number, unit, permission_level
# We want to replace these with just job_title='Care Assistant'
pattern = r'StaffProfile\.objects\.create\(\s*user=([^,]+),\s*sap_number=\'[^\']*\',\s*unit=([^,]+),\s*permission_level=\'[^\']*\'\s*\)'

replacement = r"StaffProfile.objects.create(\n            user=\1,\n            job_title='Care Assistant'\n        )"

content = re.sub(pattern, replacement, content)

# Also need to add user.unit assignment before StaffProfile creation
# Find pattern: User.objects.create_user(...) followed by StaffProfile.objects.create
# Insert self.user.unit = self.unit; self.user.save() before StaffProfile creation

lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    
    # If we see a line with User.objects.create_user, look ahead for the closing )
    if 'User.objects.create_user(' in line:
        # Find the variable name being assigned
        var_match = re.match(r'\s*self\.(\w+)\s*=\s*User\.objects\.create_user\(', line)
        if var_match:
            user_var = var_match.group(1)
            
            # Look ahead to find the matching StaffProfile.objects.create
            j = i + 1
            while j < len(lines) and j < i + 20:  # Look ahead up to 20 lines
                if 'StaffProfile.objects.create(' in lines[j]:
                    # Check if this StaffProfile uses this user
                    if f'user=self.{user_var}' in lines[j]:
                        # Insert unit assignment before StaffProfile
                        # First, find the line after the User.objects.create_user closing
                        k = i + 1
                        while k < j and ')' not in lines[k]:
                            k += 1
                        
                        # Insert after the comment line about care_home_access
                        insert_pos = k + 1
                        while insert_pos < j and lines[insert_pos].strip().startswith('#'):
                            insert_pos += 1
                        
                        # Insert the unit assignment lines
                        indent = '        '
                        new_lines.insert(insert_pos, f'{indent}self.{user_var}.unit = self.unit')
                        new_lines.insert(insert_pos + 1, f'{indent}self.{user_var}.save()')
                        new_lines.insert(insert_pos + 2, '')
                        i += 3  # Account for inserted lines
                        break
                j += 1
    
    i += 1

content = '\n'.join(new_lines)

# Write back
with open(file_path, 'w') as f:
    f.write(content)

print("✅ Fixed StaffProfile creation patterns")
