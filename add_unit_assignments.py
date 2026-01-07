#!/usr/bin/env python3
"""Add missing unit assignment after User creation"""

import re

file_path = 'scheduling/tests/test_task57_form_autosave.py'

with open(file_path, 'r') as f:
    content = f.read()

# After each User.objects.create_user that doesn't have unit assignment, add it
# Pattern: find User.objects.create_user followed by a closing paren and newline
# that is NOT followed by self.user.unit

pattern = r"(self\.user = User\.objects\.create_user\([^)]+\)\s*\n)(\s*# self\.user\.care_home_access)"

replacement = r"\1        self.user.unit = self.unit\n        self.user.save()\n\2"

content = re.sub(pattern, replacement, content)

with open(file_path, 'w') as f:
    f.write(content)

print("Added unit assignments")
