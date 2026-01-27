#!/usr/bin/env python
"""Test what the dashboard context should return"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from incident_safety.models import RootCauseAnalysis, SafetyActionPlan, DutyOfCandourRecord
from django.utils import timezone

print("=== TESTING DASHBOARD CONTEXT ===\n")

# Test Total RCAs
total_rcas = RootCauseAnalysis.objects.count()
print(f"Total RCAs: {total_rcas}")

# Test Pending RCAs
pending_rcas = RootCauseAnalysis.objects.filter(
    status__in=['IN_PROGRESS', 'UNDER_REVIEW', 'REJECTED']
).count()
print(f"Pending RCAs (IN_PROGRESS, UNDER_REVIEW, REJECTED): {pending_rcas}")

# Test Total Action Plans
total_action_plans = SafetyActionPlan.objects.count()
print(f"\nTotal Action Plans: {total_action_plans}")

# Test Open Action Plans
open_action_plans = SafetyActionPlan.objects.filter(
    status__in=['IDENTIFIED', 'ASSIGNED', 'IN_PROGRESS']
).count()
print(f"Open Action Plans (IDENTIFIED, ASSIGNED, IN_PROGRESS): {open_action_plans}")

# Test Active DoC
active_doc = DutyOfCandourRecord.objects.filter(
    current_stage__in=['ASSESSMENT', 'NOTIFICATION', 'APOLOGY', 'INVESTIGATION', 'FEEDBACK']
).count()
print(f"\nActive DoC Cases (ASSESSMENT, NOTIFICATION, APOLOGY, INVESTIGATION, FEEDBACK): {active_doc}")

# Check overdue action plans
overdue_count = SafetyActionPlan.objects.filter(
    status__in=['IDENTIFIED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED'],
    target_completion_date__lt=timezone.now().date()
).count()
print(f"\nOverdue Action Plans: {overdue_count}")

print("\n=== STATS DICT ===")
stats = {
    'total_rcas': RootCauseAnalysis.objects.count(),
    'total_action_plans': SafetyActionPlan.objects.count(),
    'open_action_plans': SafetyActionPlan.objects.filter(
        status__in=['IDENTIFIED', 'ASSIGNED', 'IN_PROGRESS']
    ).count(),
    'active_doc_cases': DutyOfCandourRecord.objects.filter(
        current_stage__in=['ASSESSMENT', 'NOTIFICATION', 'APOLOGY', 'INVESTIGATION', 'FEEDBACK']
    ).count(),
}
print(stats)
