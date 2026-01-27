#!/usr/bin/env python
"""
Update INC-2026-0007 (RCA #4) with 5 Whys data that ties to the fishbone analysis.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from incident_safety.models import RootCauseAnalysis

# Get RCA #4 (INC-2026-0007)
rca = RootCauseAnalysis.objects.get(pk=4)

# Update with 5 Whys that dig deeper into the fishbone factors
rca.why_1 = "Why did the resident fall during transfer? - Staff member lost grip during the maneuver"
rca.why_2 = "Why did the staff member lose grip? - Transfer was attempted by one person instead of two"
rca.why_3 = "Why was only one person available? - Second staff member was not assigned due to perceived low-risk assessment"
rca.why_4 = "Why was the risk assessment low? - Risk assessment had not been updated for 6 months despite resident's condition changes"
rca.why_5 = "Why wasn't the risk assessment reviewed? - No systematic trigger in place for mandatory review after resident weight/mobility changes"

# Update root cause and lessons
rca.root_cause_summary = "Contributing factors: Outdated risk assessment, inadequate staffing for transfer, equipment unavailability, and insufficient space. Root cause: No systematic process for triggering risk assessment reviews when resident conditions change."
rca.lessons_learned = "Transfer safety requires current risk assessments, appropriate equipment, adequate space, and sufficient trained staff. Systems must ensure assessments are reviewed when resident conditions change."
rca.recommendations = """1. Implement monthly risk assessment reviews
2. Ensure two staff for all transfers
3. Establish equipment maintenance priority system
4. Create space optimization plan for resident rooms
5. Mandatory risk reassessment triggers after weight changes >5kg or mobility status changes"""

rca.save()

print(f"✅ Updated {rca.incident.reference_number} with 5 Whys analysis")
print(f"   - Why 1: {rca.why_1}")
print(f"   - Why 2: {rca.why_2}")
print(f"   - Why 3: {rca.why_3}")
print(f"   - Why 4: {rca.why_4}")
print(f"   - Why 5: {rca.why_5}")
print(f"\n   Root Cause: {rca.root_cause_summary}")
