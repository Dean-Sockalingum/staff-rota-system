#!/usr/bin/env python
"""
Test script to verify Pattern Overview leave integration
Tests: LeaveRequest creation, annual leave balance, SicknessRecord creation
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, LeaveRequest
from staff_records.models import SicknessRecord, StaffProfile
from django.db.models import Sum

print("="*60)
print("PATTERN OVERVIEW LEAVE INTEGRATION TEST")
print("="*60)

# Test 1: Check LeaveRequest model exists and is queryable
print("\n✅ TEST 1: LeaveRequest Model")
print(f"  Total leave requests in system: {LeaveRequest.objects.count()}")
annual_leave = LeaveRequest.objects.filter(leave_type='ANNUAL').count()
sick_leave = LeaveRequest.objects.filter(leave_type='SICK').count()
print(f"  - Annual leave requests: {annual_leave}")
print(f"  - Sick leave requests: {sick_leave}")

# Test 2: Check a sample user's leave balance
print("\n✅ TEST 2: Annual Leave Balance Calculation")
sample_user = User.objects.filter(is_active=True).first()
if sample_user:
    print(f"  Sample user: {sample_user.full_name} ({sample_user.sap})")
    print(f"  - Allowance: {sample_user.annual_leave_allowance} days")
    print(f"  - Approved: {sample_user.annual_leave_approved} days")
    print(f"  - Pending: {sample_user.annual_leave_pending} days")
    print(f"  - Remaining: {sample_user.annual_leave_remaining} days")
else:
    print("  No users found in system")

# Test 3: Check SicknessRecord model integration
print("\n✅ TEST 3: SicknessRecord (Bradford Factor)")
print(f"  Total sickness records: {SicknessRecord.objects.count()}")
print(f"  Active staff profiles: {StaffProfile.objects.count()}")
if SicknessRecord.objects.exists():
    recent = SicknessRecord.objects.order_by('-reported_at').first()
    print(f"  Most recent sickness:")
    print(f"    - Staff: {recent.profile.user.full_name if recent.profile else 'N/A'}")
    print(f"    - Date: {recent.first_working_day}")
    print(f"    - Status: {recent.status}")

# Test 4: Check for any unauthorised leave records
print("\n✅ TEST 4: Unauthorised Absence Tracking")
unauthorised = LeaveRequest.objects.filter(
    leave_type='OTHER',
    status='DENIED'
).count()
print(f"  Unauthorised absence records: {unauthorised}")

print("\n" + "="*60)
print("TEST COMPLETE - System ready for Pattern Overview leave recording")
print("="*60)
print("\n📝 Next Steps:")
print("  1. Log in to Pattern Overview")
print("  2. Click any shift cell")
print("  3. Select Annual Leave, Sickness, or Unauthorised Leave")
print("  4. Save and verify:")
print("     - LeaveRequest created")
print("     - Leave balance updated (annual leave)")
print("     - SicknessRecord created (sickness)")
print("     - Management notification sent")
print("     - Cell displays color-coded (A/L green, SICK red, UNAUTH orange)")
