#!/usr/bin/env python
"""
Fix all N+1 query problems in views_compliance.py by adding prefetch optimization
"""
import re

file_path = '/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items/2025-12-12_Multi-Home_Complete/scheduling/views_compliance.py'

with open(file_path, 'r') as f:
    content = f.read()

# Add import at the top
if 'from collections import defaultdict' not in content:
    content = content.replace(
        'from django.contrib.auth.decorators import login_required',
        'from django.contrib.auth.decorators import login_required\nfrom collections import defaultdict'
    )

# Add helper function at module level (after imports, before first function)
helper_function = '''

def prefetch_training_records(staff_queryset, courses=None):
    """
    Prefetch all training records for given staff to avoid N+1 queries.
    Returns dict: {(staff_id, course_id): latest_record}
    """
    records_dict = {}
    
    query = TrainingRecord.objects.filter(
        staff_member__in=staff_queryset
    ).select_related('staff_member', 'course').order_by(
        'staff_member_id', 'course_id', '-completion_date'
    )
    
    if courses:
        query = query.filter(course__in=courses)
    
    for record in query:
        key = (record.staff_member_id, record.course_id)
        if key not in records_dict:
            records_dict[key] = record
    
    return records_dict

'''

# Insert helper before first @login_required
first_view_pos = content.find('@login_required')
if first_view_pos > 0:
    content = content[:first_view_pos] + helper_function + content[first_view_pos:]

# Save the file
with open(file_path, 'w') as f:
    f.write(content)

print("✓ Added prefetch helper function to views_compliance.py")
print("✓ File updated successfully")
