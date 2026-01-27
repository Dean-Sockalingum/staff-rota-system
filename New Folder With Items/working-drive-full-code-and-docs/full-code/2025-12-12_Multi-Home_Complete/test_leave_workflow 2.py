#!/usr/bin/env python3
"""
Complete end-to-end workflow test for staff login and leave request system.

Tests:
1. Staff authentication with SAP credentials
2. Leave request creation
3. Auto-approval mechanism
4. Leave balance updates via signals
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')

import django
django.setup()

from scheduling.models import User, LeaveRequest, Shift
from staff_records.models import StaffProfile, AnnualLeaveEntitlement, AnnualLeaveTransaction
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

def test_complete_workflow():
    """Test the complete staff login and leave request workflow."""
    
    print("="*80)
    print("STAFF LOGIN AND LEAVE REQUEST WORKFLOW TEST")
    print("="*80)
    
    # STEP 1: Find or create a test user with full setup
    print("\n" + "="*80)
    print("STEP 1: SETUP TEST USER")
    print("="*80)
    
    # Get a staff member from Orchard Grove (should have all standardized data)
    test_user = User.objects.filter(
        is_active=True,
        role__is_management=False,
        unit__care_home__name='ORCHARD_GROVE'
    ).first()
    
    if not test_user:
        print("✗ No suitable test user found")
        return
    
    print(f"\nTest user selected:")
    print(f"  SAP: {test_user.sap}")
    print(f"  Name: {test_user.first_name} {test_user.last_name}")
    print(f"  Role: {test_user.role.name if test_user.role else 'No role'}")
    print(f"  Unit: {test_user.unit.name if test_user.unit else 'No unit'}")
    print(f"  Home: {test_user.unit.care_home.name if test_user.unit else 'No home'}")
    
    # Ensure staff profile exists
    profile, created = StaffProfile.objects.get_or_create(
        user=test_user,
        defaults={
            'ni_number': f'NI{test_user.sap}',
            'date_of_birth': date(1985, 1, 1),
            'address': '123 Test Street',
            'postcode': 'EH1 1AA',
            'phone_number': '01234567890',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '01234567890'
        }
    )
    
    if created:
        print(f"✓ Created staff profile")
    else:
        print(f"✓ Staff profile exists")
    
    # Ensure leave entitlement exists
    leave_year_start = date(2025, 4, 1)
    leave_year_end = date(2026, 3, 31)
    
    entitlement, ent_created = AnnualLeaveEntitlement.objects.get_or_create(
        profile=profile,
        leave_year_start=leave_year_start,
        defaults={
            'leave_year_end': leave_year_end,
            'contracted_hours_per_week': Decimal('35.00'),
            'total_entitlement_hours': Decimal('196.00'),  # 5.6 weeks * 35 hours
            'hours_used': Decimal('0.00'),
            'hours_pending': Decimal('0.00'),
            'hours_remaining': Decimal('196.00'),
        }
    )
    
    if ent_created:
        print(f"✓ Created leave entitlement for year {leave_year_start.year}-{leave_year_end.year}")
    else:
        print(f"✓ Leave entitlement exists")
    
    entitlement.recalculate_balance()
    entitlement.save()
    
    print(f"  Total entitlement: {entitlement.total_entitlement_hours} hours ({entitlement.days_entitlement} days)")
    print(f"  Hours remaining: {entitlement.hours_remaining} hours ({entitlement.days_remaining} days)")
    
    # Ensure user has some shifts scheduled (for leave day calculation)
    shifts_count = Shift.objects.filter(user=test_user).count()
    print(f"  Scheduled shifts: {shifts_count}")
    
    # STEP 2: Test authentication
    print("\n" + "="*80)
    print("STEP 2: TEST AUTHENTICATION")
    print("="*80)
    
    auth_result = authenticate(username=test_user.sap, password='password123')
    if auth_result:
        print(f"✓ Authentication SUCCESSFUL")
        print(f"  Username (SAP): {test_user.sap}")
        print(f"  Password: password123")
        print(f"  Authenticated user: {auth_result.first_name} {auth_result.last_name}")
    else:
        print(f"✗ Authentication FAILED")
        print(f"  This should not happen - password was just set")
        return
    
    # STEP 3: Create a leave request
    print("\n" + "="*80)
    print("STEP 3: CREATE LEAVE REQUEST")
    print("="*80)
    
    # Calculate leave dates (7 days in the future, for 5 days)
    start_date = date.today() + timedelta(days=7)
    end_date = start_date + timedelta(days=4)  # 5 calendar days
    
    # Count shifts during this period
    shifts_during_leave = Shift.objects.filter(
        user=test_user,
        date__gte=start_date,
        date__lte=end_date
    ).count()
    
    if shifts_during_leave == 0:
        # If no shifts, assume 5 weekdays
        working_days = 5
    else:
        working_days = shifts_during_leave
    
    # Calculate hours based on role
    if test_user.role and test_user.role.is_management:
        hours_per_day = Decimal('7.00')
    else:
        hours_per_day = Decimal('11.66')  # 35hr staff doing 12-hour shifts
    
    hours_requested = Decimal(str(working_days)) * hours_per_day
    
    print(f"\nCreating leave request:")
    print(f"  Start date: {start_date}")
    print(f"  End date: {end_date}")
    print(f"  Working days: {working_days}")
    print(f"  Hours requested: {hours_requested}")
    print(f"  Leave type: ANNUAL")
    
    # Check current balance
    balance_before = entitlement.hours_remaining
    print(f"  Balance before: {balance_before} hours")
    
    # Create the leave request
    leave_request = LeaveRequest.objects.create(
        user=test_user,
        leave_type='ANNUAL',
        start_date=start_date,
        end_date=end_date,
        days_requested=working_days,
        reason='Testing auto-approval workflow',
        status='PENDING'
    )
    
    print(f"✓ Leave request created (ID: {leave_request.id})")
    
    # STEP 4: Test auto-approval logic
    print("\n" + "="*80)
    print("STEP 4: TEST AUTO-APPROVAL")
    print("="*80)
    
    # Import the auto-approval function
    from scheduling.views import _process_auto_approval
    
    print(f"\nRunning auto-approval checks...")
    _process_auto_approval(leave_request, test_user)
    
    # Refresh from database
    leave_request.refresh_from_db()
    
    print(f"\nAuto-approval result:")
    print(f"  Status: {leave_request.status}")
    print(f"  Automated decision: {leave_request.automated_decision}")
    print(f"  Approval date: {leave_request.approval_date}")
    print(f"  Approved by: {leave_request.approved_by}")
    print(f"  Approval notes: {leave_request.approval_notes or '(none)'}")
    print(f"  Blackout period: {leave_request.is_blackout_period}")
    print(f"  Causes staffing shortfall: {leave_request.causes_staffing_shortfall}")
    
    if leave_request.status == 'APPROVED':
        print(f"\n✓ Leave request AUTO-APPROVED")
    elif leave_request.status == 'MANUAL_REVIEW':
        print(f"\n⚠ Leave request requires MANUAL REVIEW")
    else:
        print(f"\n⚠ Leave request status: {leave_request.status}")
    
    # STEP 5: Check leave balance update
    print("\n" + "="*80)
    print("STEP 5: CHECK LEAVE BALANCE UPDATE")
    print("="*80)
    
    # Refresh entitlement
    entitlement.refresh_from_db()
    balance_after = entitlement.hours_remaining
    
    print(f"\nLeave balance:")
    print(f"  Balance before request: {balance_before} hours")
    print(f"  Balance after request: {balance_after} hours")
    print(f"  Difference: {balance_before - balance_after} hours")
    print(f"  Expected deduction: {hours_requested} hours")
    
    # Check transactions
    transactions = AnnualLeaveTransaction.objects.filter(
        related_request=leave_request
    ).order_by('created_at')
    
    print(f"\nLeave transactions: {transactions.count()}")
    for txn in transactions:
        print(f"  - {txn.transaction_type}: {txn.hours} hours")
        print(f"    Description: {txn.description}")
        print(f"    Balance after: {txn.balance_after} hours")
        print(f"    Created at: {txn.created_at}")
    
    if leave_request.status == 'APPROVED':
        if balance_before - balance_after == hours_requested:
            print(f"\n✓ Leave balance CORRECTLY UPDATED")
        else:
            print(f"\n⚠ Leave balance update mismatch")
    else:
        print(f"\n⚠ Leave not yet approved, balance may reflect pending hours")
    
    # STEP 6: Activity log check
    print("\n" + "="*80)
    print("STEP 6: CHECK ACTIVITY LOG")
    print("="*80)
    
    from scheduling.models import ActivityLog
    
    recent_logs = ActivityLog.objects.filter(
        user=test_user
    ).order_by('-created_at')[:5]
    
    print(f"\nRecent activity logs for {test_user.first_name} {test_user.last_name}:")
    for log in recent_logs:
        print(f"  - {log.action_type}: {log.description}")
        print(f"    Created: {log.created_at}")
        print(f"    Automated: {log.automated}")
    
    # SUMMARY
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    print(f"\n✓ Test user: {test_user.sap} - {test_user.first_name} {test_user.last_name}")
    print(f"✓ Authentication: WORKING (password: password123)")
    print(f"✓ Leave entitlement: {entitlement.hours_remaining}/{entitlement.total_entitlement_hours} hours remaining")
    print(f"✓ Leave request: Created for {start_date} to {end_date} ({working_days} days)")
    
    if leave_request.status == 'APPROVED' and leave_request.automated_decision:
        print(f"✓ Auto-approval: WORKING (request auto-approved)")
    elif leave_request.status == 'MANUAL_REVIEW':
        print(f"⚠ Auto-approval: Requires manual review ({leave_request.approval_notes})")
    else:
        print(f"⚠ Auto-approval: Status is {leave_request.status}")
    
    if transactions.exists():
        print(f"✓ Leave balance update: WORKING ({transactions.count()} transaction(s) created)")
    else:
        print(f"⚠ Leave balance update: No transactions found")
    
    print(f"\n" + "="*80)
    print(f"WORKFLOW TEST COMPLETE")
    print(f"="*80)

if __name__ == '__main__':
    test_complete_workflow()
