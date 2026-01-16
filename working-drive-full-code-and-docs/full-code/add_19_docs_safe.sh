#!/bin/bash
# Safe script to add 19 missing guidance documents to views.py

VIEWS_FILE="/home/staff-rota-system/scheduling/views.py"
BACKUP_FILE="/home/staff-rota-system/scheduling/views.py.backup_$(date +%Y%m%d_%H%M%S)"

# Backup first
cp "$VIEWS_FILE" "$BACKUP_FILE"
echo "✅ Backed up to $BACKUP_FILE"

# Add comma to line 733 (after 'icon': 'fa-calendar-alt')
sed -i "733s/'fa-calendar-alt'/'fa-calendar-alt',/" "$VIEWS_FILE"

# Now insert the 19 new documents before line 734 (the closing ])
sed -i '733a\        },\
        {\
            '"'"'title'"'"': '"'"'Leave Usage Targets Guide'"'"',\
            '"'"'slug'"'"': '"'"'leave-usage-targets-guide'"'"',\
            '"'"'description'"'"': '"'"'Annual leave planning and usage targets throughout the year.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'LEAVE_USAGE_TARGETS_GUIDE.md'"'"',\
            '"'"'category'"'"': '"'"'staff'"'"',\
            '"'"'icon'"'"': '"'"'fa-chart-line'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'What\\'"'"'s New - Latest Updates'"'"',\
            '"'"'slug'"'"': '"'"'whats-new'"'"',\
            '"'"'description'"'"': '"'"'Latest system features, updates, and improvements.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'WHATS_NEW.md'"'"',\
            '"'"'category'"'"': '"'"'system'"'"',\
            '"'"'icon'"'"': '"'"'fa-star'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'Sample Rota - Orchard Grove'"'"',\
            '"'"'slug'"'"': '"'"'sample-rota-orchard-grove'"'"',\
            '"'"'description'"'"': '"'"'Example 6-week rota pattern for Orchard Grove care home.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'SAMPLE_ROTA_ORCHARD_GROVE.md'"'"',\
            '"'"'category'"'"': '"'"'rota'"'"',\
            '"'"'icon'"'"': '"'"'fa-calendar'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'System Feature Index'"'"',\
            '"'"'slug'"'"': '"'"'system-feature-index'"'"',\
            '"'"'description'"'"': '"'"'Complete index of all system features and capabilities.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'SYSTEM_FEATURE_INDEX.md'"'"',\
            '"'"'category'"'"': '"'"'system'"'"',\
            '"'"'icon'"'"': '"'"'fa-list'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'System SOP Index'"'"',\
            '"'"'slug'"'"': '"'"'system-sop-index'"'"',\
            '"'"'description'"'"': '"'"'Index of all Standard Operating Procedures.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'SYSTEM_SOP_INDEX.md'"'"',\
            '"'"'category'"'"': '"'"'system'"'"',\
            '"'"'icon'"'"': '"'"'fa-book'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'Policy Integration Summary'"'"',\
            '"'"'slug'"'"': '"'"'policy-integration-summary'"'"',\
            '"'"'description'"'"': '"'"'How organizational policies integrate with the system.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'POLICY_INTEGRATION_SUMMARY.md'"'"',\
            '"'"'category'"'"': '"'"'system'"'"',\
            '"'"'icon'"'"': '"'"'fa-file-contract'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'Manager Guidance Integration'"'"',\
            '"'"'slug'"'"': '"'"'manager-guidance-integration-summary'"'"',\
            '"'"'description'"'"': '"'"'How manager guidance integrates across the platform.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'MANAGER_GUIDANCE_INTEGRATION_SUMMARY.md'"'"',\
            '"'"'category'"'"': '"'"'manager'"'"',\
            '"'"'icon'"'"': '"'"'fa-puzzle-piece'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'Video Production Package'"'"',\
            '"'"'slug'"'"': '"'"'video-production-package'"'"',\
            '"'"'description'"'"': '"'"'Video tutorial production guide and scripts.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'VIDEO_PRODUCTION_PACKAGE.md'"'"',\
            '"'"'category'"'"': '"'"'system'"'"',\
            '"'"'icon'"'"': '"'"'fa-video'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'SOP: Shift Management'"'"',\
            '"'"'slug'"'"': '"'"'sop-shift-management'"'"',\
            '"'"'description'"'"': '"'"'Standard procedures for managing shifts and rotas.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'SOP_SHIFT_MANAGEMENT.md'"'"',\
            '"'"'category'"'"': '"'"'sop'"'"',\
            '"'"'icon'"'"': '"'"'fa-clock'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'SOP: Annual Leave'"'"',\
            '"'"'slug'"'"': '"'"'sop-annual-leave'"'"',\
            '"'"'description'"'"': '"'"'Annual leave approval and management procedures.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'SOP_ANNUAL_LEAVE.md'"'"',\
            '"'"'category'"'"': '"'"'sop'"'"',\
            '"'"'icon'"'"': '"'"'fa-umbrella-beach'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'SOP: Additional Staffing'"'"',\
            '"'"'slug'"'"': '"'"'sop-additional-staffing'"'"',\
            '"'"'description'"'"': '"'"'Requesting and managing additional staffing needs.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'SOP_ADDITIONAL_STAFFING.md'"'"',\
            '"'"'category'"'"': '"'"'sop'"'"',\
            '"'"'icon'"'"': '"'"'fa-user-plus'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'SOP: Staff Onboarding'"'"',\
            '"'"'slug'"'"': '"'"'sop-staff-onboarding'"'"',\
            '"'"'description'"'"': '"'"'New staff onboarding and system access procedures.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'SOP_STAFF_ONBOARDING.md'"'"',\
            '"'"'category'"'"': '"'"'sop'"'"',\
            '"'"'icon'"'"': '"'"'fa-user-graduate'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'SOP: System Maintenance'"'"',\
            '"'"'slug'"'"': '"'"'sop-system-maintenance'"'"',\
            '"'"'description'"'"': '"'"'System maintenance and technical procedures.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'SOP_SYSTEM_MAINTENANCE.md'"'"',\
            '"'"'category'"'"': '"'"'sop'"'"',\
            '"'"'icon'"'"': '"'"'fa-tools'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'SOP: Compliance Reporting'"'"',\
            '"'"'slug'"'"': '"'"'sop-compliance-reporting'"'"',\
            '"'"'description'"'"': '"'"'Compliance reporting and audit trail procedures.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'SOP_COMPLIANCE_REPORTING.md'"'"',\
            '"'"'category'"'"': '"'"'sop'"'"',\
            '"'"'icon'"'"': '"'"'fa-file-invoice'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'SOP: Care Plan Reviews'"'"',\
            '"'"'slug'"'"': '"'"'sop-care-plan-reviews'"'"',\
            '"'"'description'"'"': '"'"'Care plan review scheduling and tracking.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'SOP_CARE_PLAN_REVIEWS.md'"'"',\
            '"'"'category'"'"': '"'"'sop'"'"',\
            '"'"'icon'"'"': '"'"'fa-file-medical-alt'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'Care Inspectorate: Incident Report'"'"',\
            '"'"'slug'"'"': '"'"'care-inspectorate-incident-report'"'"',\
            '"'"'description'"'"': '"'"'Incident reporting template for Care Inspectorate compliance.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'CARE_INSPECTORATE_INCIDENT_REPORT.md'"'"',\
            '"'"'category'"'"': '"'"'care_inspectorate'"'"',\
            '"'"'icon'"'"': '"'"'fa-exclamation-triangle'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'Care Inspectorate: Induction Checklist'"'"',\
            '"'"'slug'"'"': '"'"'care-inspectorate-induction-checklist'"'"',\
            '"'"'description'"'"': '"'"'Staff induction checklist for Care Inspectorate compliance.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'CARE_INSPECTORATE_INDUCTION_CHECKLIST.md'"'"',\
            '"'"'category'"'"': '"'"'care_inspectorate'"'"',\
            '"'"'icon'"'"': '"'"'fa-list-check'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'Care Inspectorate: Supervision Record'"'"',\
            '"'"'slug'"'"': '"'"'care-inspectorate-supervision-record'"'"',\
            '"'"'description'"'"': '"'"'Supervision record template for Care Inspectorate compliance.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'CARE_INSPECTORATE_SUPERVISION_RECORD.md'"'"',\
            '"'"'category'"'"': '"'"'care_inspectorate'"'"',\
            '"'"'icon'"'"': '"'"'fa-clipboard-list'"'"',\
        },\
        {\
            '"'"'title'"'"': '"'"'Care Inspectorate: Training Matrix'"'"',\
            '"'"'slug'"'"': '"'"'care-inspectorate-training-matrix'"'"',\
            '"'"'description'"'"': '"'"'Training matrix template for Care Inspectorate compliance.'"'"',\
            '"'"'file'"'"': docs_path / '"'"'CARE_INSPECTORATE_TRAINING_MATRIX.md'"'"',\
            '"'"'category'"'"': '"'"'care_inspectorate'"'"',\
            '"'"'icon'"'"': '"'"'fa-graduation-cap'"'"',\
' "$VIEWS_FILE"

echo "✅ Added 19 documents"

# Check syntax
python3 -m py_compile "$VIEWS_FILE" 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Syntax check passed"
    echo "📁 Total documents now: 36"
else
    echo "❌ Syntax error detected - restoring backup"
    cp "$BACKUP_FILE" "$VIEWS_FILE"
    exit 1
fi
