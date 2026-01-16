#!/usr/bin/env python3
"""
Fix all test issues identified in test run
1. Remove invalid care_home_access references (doesn't exist in User model)
2. Fix SAP numbers to be 6 digits
3. Update test expectations
"""

import os
import re

def fix_care_home_access_in_file(filepath):
    """Remove or comment out care_home_access references"""
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Comment out care_home_access lines
    content = re.sub(
        r'^(\s+)(.*\.care_home_access\.add\(.*\))$',
        r'\1# \2  # care_home_access removed - users access via unit.care_home',
        content,
        flags=re.MULTILINE
    )
    
    # Comment out care_home_access.all() references
    content = re.sub(
        r'(.*\.care_home_access\.all\(\))',
        r'# \1  # care_home_access removed',
        content
    )
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✓ Fixed care_home_access references")
        return True
    return False

def fix_sap_numbers_in_file(filepath):
    """Fix SAP numbers to be 6 digits instead of 8"""
    print(f"Checking SAP numbers in {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix common SAP patterns
    # SCW1081 -> 108100
    # SCW1234 -> 123400  
    content = re.sub(r'sap=["\']SCW(\d{4})["\']', r'sap="\1" + "00"', content)
    content = re.sub(r'sap=["\']SSCW(\d{3})["\']', r'sap="\1" + "000"', content)
    
    # Fix direct 8-digit SAPs by taking last 6 digits
    content = re.sub(r'sap=["\'](\d{8})["\']', lambda m: f'sap="{m.group(1)[-6:]}"', content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✓ Fixed SAP numbers")
        return True
    return False

def main():
    """Fix all test files"""
    test_dir = '/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/scheduling/tests'
    
    files_to_fix = [
        'test_task56_compliance_widgets.py',
        'test_task57_form_autosave.py',
        'test_task59_leave_calendar.py',
        'test_phase6_integration.py',
        'test_workflow_backup.py',
        'test_workflow_clean.py',
    ]
    
    fixed_count = 0
    for filename in files_to_fix:
        filepath = os.path.join(test_dir, filename)
        if os.path.exists(filepath):
            if fix_care_home_access_in_file(filepath):
                fixed_count += 1
            if fix_sap_numbers_in_file(filepath):
                fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} files")
    print("\nNote: Tests may need additional fixes:")
    print("- Users access care homes through unit.care_home, not care_home_access")
    print("- Some tests may need to set user.unit instead")

if __name__ == '__main__':
    main()
