#!/usr/bin/env python3
"""
Update all permission checks to allow superusers
"""

import os
import re

def update_file(filepath):
    """Update permission checks in a file to allow superusers"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Pattern 1: if not (request.user.role and request.user.role.is_management):
    pattern1 = r'if not \(request\.user\.role and request\.user\.role\.is_management\):'
    replacement1 = r'if not (request.user.is_superuser or (request.user.role and request.user.role.is_management)):'
    content, count1 = re.subn(pattern1, replacement1, content)
    if count1 > 0:
        changes.append(f"Updated {count1} is_management checks")
    
    # Pattern 2: if not request.user.role or not request.user.role.is_senior_management_team:
    pattern2 = r'if not request\.user\.role or not request\.user\.role\.is_senior_management_team:'
    replacement2 = r'if not (request.user.is_superuser or (request.user.role and request.user.role.is_senior_management_team)):'
    content, count2 = re.subn(pattern2, replacement2, content)
    if count2 > 0:
        changes.append(f"Updated {count2} 'if not role or not is_senior' checks")
    
    # Pattern 3: if not request.user.role.is_senior_management_team:
    pattern3 = r'if not request\.user\.role\.is_senior_management_team:'
    replacement3 = r'if not (request.user.is_superuser or (request.user.role and request.user.role.is_senior_management_team)):'
    content, count3 = re.subn(pattern3, replacement3, content)
    if count3 > 0:
        changes.append(f"Updated {count3} is_senior_management_team checks")
    
    # Pattern 4: if not (request.user.role and (request.user.role.can_manage_rota or request.user.role.is_management)):
    pattern4 = r'if not \(request\.user\.role and \(request\.user\.role\.can_manage_rota or request\.user\.role\.is_management\)\):'
    replacement4 = r'if not (request.user.is_superuser or (request.user.role and (request.user.role.can_manage_rota or request.user.role.is_management))):'
    content, count4 = re.subn(pattern4, replacement4, content)
    if count4 > 0:
        changes.append(f"Updated {count4} can_manage_rota checks")
    
    # Pattern 5: if not (request.user == staff or (request.user.role and request.user.role.is_management)):
    pattern5 = r'if not \(request\.user == staff or \(request\.user\.role and request\.user\.role\.is_management\)\):'
    replacement5 = r'if not (request.user.is_superuser or request.user == staff or (request.user.role and request.user.role.is_management)):'
    content, count5 = re.subn(pattern5, replacement5, content)
    if count5 > 0:
        changes.append(f"Updated {count5} user==staff checks")
    
    # Pattern 6: if not request.user.role.is_management: (without parentheses check)
    pattern6 = r'if not request\.user\.role\.is_management:'
    replacement6 = r'if not (request.user.is_superuser or (request.user.role and request.user.role.is_management)):'
    content, count6 = re.subn(pattern6, replacement6, content)
    if count6 > 0:
        changes.append(f"Updated {count6} simple is_management checks")
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True, changes
    return False, []

def main():
    print("=" * 80)
    print("🔧 UPDATING PERMISSION CHECKS TO ALLOW SUPERUSERS")
    print("=" * 80)
    print()
    
    files_to_update = [
        'scheduling/views.py',
        'scheduling/views_overtime_management.py',
        'scheduling/views_analytics.py',
        'scheduling/views_executive_summary.py',
        'scheduling/decorators.py',
        'scheduling/views_optimization.py',
    ]
    
    total_updated = 0
    
    for filepath in files_to_update:
        if os.path.exists(filepath):
            updated, changes = update_file(filepath)
            if updated:
                print(f"✅ {filepath}")
                for change in changes:
                    print(f"   - {change}")
                total_updated += 1
            else:
                print(f"⏭️  {filepath} - No changes needed")
        else:
            print(f"⚠️  {filepath} - File not found")
        print()
    
    print("=" * 80)
    print(f"✅ Updated {total_updated} file(s)")
    print()
    print("💡 All permission checks now allow:")
    print("   1. Users with appropriate roles (SM, OM, HOS, etc.)")
    print("   2. Superusers (regardless of role)")
    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
