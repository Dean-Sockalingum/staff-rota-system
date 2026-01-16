#!/usr/bin/env python3
"""Create test leave requests for testing bulk approval functionality"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.contrib.auth import get_user_model
from scheduling.models import LeaveRequest

User = get_user_model()

# Get some users (SAP is the primary key for the custom User model)
staff_users = User.objects.filter(is_superuser=False)[:5]

if not staff_users.exists():
    print("❌ No staff users found. Cannot create leave requests.")
    exit(1)

print(f"Found {staff_users.count()} staff users")

# Create 5 test leave requests
today = datetime.now().date()
leave_requests_created = 0

for i, staff in enumerate(staff_users):
    start_date = today + timedelta(days=7 + (i * 3))
    end_date = start_date + timedelta(days=2)
    
    leave_request = LeaveRequest.objects.create(
        user=staff,
        start_date=start_date,
        end_date=end_date,
        leave_type='annual',
        reason=f'Test leave request {i+1} - Holiday',
        status='PENDING',
        days_requested=(end_date - start_date).days + 1
    )
    
    leave_requests_created += 1
    print(f"✅ Created leave request for {staff.full_name}: {start_date} to {end_date}")

print(f"\n✅ Successfully created {leave_requests_created} test leave requests")
print(f"Navigate to http://localhost:8000/leave-approvals/ to test bulk approval")
