#!/usr/bin/env python3
"""
Comprehensive test fixture builder
Adds required fields for all model creations in tests
"""

import re
import os
from datetime import date, timedelta

def fix_compliance_metric_tests(filepath):
    """Add required fields to ComplianceMetric.objects.create() calls"""
    print(f"Fixing ComplianceMetric tests in {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Find all ComplianceMetric.objects.create() calls and add required fields if missing
    # Add period_start and period_end if not present
    pattern = r'(ComplianceMetric\.objects\.create\([^)]*)'
    
    def add_required_fields(match):
        create_call = match.group(1)
        
        # Check if period_start already exists
        if 'period_start' not in create_call:
            # Add before the closing paren
            create_call += f''',
            period_start=date.today() - timedelta(days=30),
            period_end=date.today()'''
        
        # Check if metric_name exists
        if 'metric_name' not in create_call and 'category=' in create_call:
            # Extract category value to generate metric_name
            category_match = re.search(r"category=['\"](\w+)['\"]", create_call)
            if category_match:
                category = category_match.group(1)
                metric_name = f"{category.replace('_', ' ').title()} Compliance"
                # Insert after category line
                create_call = create_call.replace(
                    f"category='{category}'",
                    f"category='{category}',\n            metric_name='{metric_name}'"
                ).replace(
                    f'category="{category}"',
                    f'category="{category}",\n            metric_name="{metric_name}"'
                )
        
        return create_call
    
    content = re.sub(pattern, add_required_fields, content)
    
    # Add date import if not present
    if 'from datetime import' in content and 'date' not in content.split('from datetime import')[1].split('\n')[0]:
        content = content.replace(
            'from datetime import',
            'from datetime import date,'
        )
    elif 'from datetime import' not in content and 'ComplianceMetric' in content:
        # Add import after other imports
        import_section_end = content.find('\n\nUser = get_user_model()')
        if import_section_end > 0:
            content = content[:import_section_end] + '\nfrom datetime import date, timedelta' + content[import_section_end:]
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✓ Fixed ComplianceMetric tests")
        return True
    return False

def main():
    """Fix all compliance metric test issues"""
    test_dir = '/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete/scheduling/tests'
    
    # Files with ComplianceMetric tests
    files = [
        'test_task56_compliance_widgets.py',
        'test_phase6_integration.py',
    ]
    
    fixed_count = 0
    for filename in files:
        filepath = os.path.join(test_dir, filename)
        if os.path.exists(filepath):
            if fix_compliance_metric_tests(filepath):
                fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
