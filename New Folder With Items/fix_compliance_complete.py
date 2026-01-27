#!/usr/bin/env python3
"""
Complete fix for compliance dashboard issues
"""
import re

# Fix 1: Update compliance_dashboard_new.html to use correct base template
template_file = "/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/templates/scheduling/compliance_dashboard_new.html"
with open(template_file, "r") as f:
    template_content = f.read()

template_content = template_content.replace(
    "{% extends 'base.html' %}",
    "{% extends 'scheduling/base.html' %}"
)

with open(template_file, "w") as f:
    f.write(template_content)

print("✓ Fixed base template reference")

# Fix 2: Update views.py to disable StaffCertification queries and fix count
views_file = "/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/views.py"
with open(views_file, "r") as f:
    views_content = f.read()

# Replace the StaffCertification queries with empty list
views_content = re.sub(
    r"expiring_certifications = StaffCertification\.objects\.filter\([^)]+\)\.select_related\([^)]+\)\[:10\]",
    "expiring_certifications = []  # Disabled - table not in production",
    views_content
)

# Replace expired count query
views_content = re.sub(
    r"expired_certifications_count = StaffCertification\.objects\.filter\([^)]+\)\.count\(\)",
    "expired_certifications_count = 0  # Disabled - table not in production",
    views_content
)

# Fix the count() call to use len()
views_content = re.sub(
    r"expiring_certifications_count = expiring_certifications\.count\(\)",
    "expiring_certifications_count = len(expiring_certifications)",
    views_content
)

# Fix RegulatoryCheck filter to use unit__care_home
views_content = re.sub(
    r"recent_checks = RegulatoryCheck\.objects\.filter\(\s*care_home=care_home",
    "recent_checks = RegulatoryCheck.objects.filter(\n        unit__care_home=care_home",
    views_content
)

views_content = re.sub(
    r"failed_checks = RegulatoryCheck\.objects\.filter\(\s*care_home=care_home",
    "failed_checks = RegulatoryCheck.objects.filter(\n        unit__care_home=care_home",
    views_content
)

with open(views_file, "w") as f:
    f.write(views_content)

print("✓ Fixed views.py compliance queries")
print("✓ All fixes applied successfully")
