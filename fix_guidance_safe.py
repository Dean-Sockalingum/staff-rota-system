#!/usr/bin/env python3
"""
Safe fix for staff_guidance view to dynamically load all markdown files.
This version properly handles file scanning without breaking the dashboard.
"""

import re

views_path = '/home/staff-rota-system/scheduling/views.py'

# Read the current file
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the staff_guidance function and replace the hardcoded list with dynamic loading
new_function = '''def staff_guidance(request):
    """Display operational guidance and checklists for management users."""
    import markdown

    if not (request.user.is_superuser or (request.user.role and request.user.role.is_management)):
        return redirect('staff_dashboard')

    # BASE_DIR is /path/to/rotasystems, docs is at /path/to/docs
    docs_path = Path(settings.BASE_DIR).parent / 'docs' / 'staff_guidance'
    
    # Category and icon mapping for known documents
    doc_metadata = {
        'STAFF_FAQ': {'category': 'staff', 'icon': 'fa-question-circle', 'description': 'Comprehensive FAQ covering annual leave, sickness, shifts, and training.'},
        'NEW_STARTER_GUIDE': {'category': 'staff', 'icon': 'fa-user-plus', 'description': 'Complete onboarding guide for new staff members.'},
        'ANNUAL_LEAVE_GUIDE': {'category': 'staff', 'icon': 'fa-calendar-check', 'description': 'Everything about requesting and managing annual leave.'},
        'SICKNESS_REPORTING_GUIDE': {'category': 'staff', 'icon': 'fa-notes-medical', 'description': 'Complete guide to reporting sickness and absence management.'},
        'SUPPORTING_ATTENDANCE_POLICY': {'category': 'staff', 'icon': 'fa-file-medical', 'description': 'Official attendance policy explained in staff-friendly language.'},
        'LEAVE_USAGE_TARGETS_GUIDE': {'category': 'staff', 'icon': 'fa-chart-line', 'description': 'Annual leave planning and usage targets throughout the year.'},
        'WHATS_NEW': {'category': 'system', 'icon': 'fa-star', 'description': 'Latest system features, updates, and improvements.'},
        'MANAGER_RESOURCES_INDEX': {'category': 'manager', 'icon': 'fa-users-cog', 'description': 'Complete index of all manager guidance documents.'},
        'manager_telephone_checklist': {'category': 'manager', 'icon': 'fa-phone', 'description': 'Questions to cover when speaking to staff who have called in sick.'},
        'MANAGERS_ATTENDANCE_GUIDE': {'category': 'manager', 'icon': 'fa-clipboard-check', 'description': 'Comprehensive foundational guide for absence management.'},
        'CHECKLIST_EMPLOYEE_REPORTS_ABSENT': {'category': 'manager', 'icon': 'fa-phone-square', 'description': 'Day 1 absence call checklist and documentation.'},
        'CHECKLIST_RETURN_TO_WORK': {'category': 'manager', 'icon': 'fa-clipboard-user', 'description': 'Return to work interview checklist and scenarios.'},
        'CHECKLIST_ATTENDANCE_REVIEW': {'category': 'manager', 'icon': 'fa-file-circle-check', 'description': 'Formal attendance review meeting structure.'},
        'MANAGERS_OH_REFERRAL_GUIDE': {'category': 'manager', 'icon': 'fa-stethoscope', 'description': 'Occupational Health referrals and OHIO system guide.'},
        'MANAGERS_REASONABLE_ADJUSTMENTS_GUIDE': {'category': 'manager', 'icon': 'fa-hands-helping', 'description': 'Implementing reasonable adjustments under Equality Act.'},
        'MANAGERS_DISABILITY_MH_GUIDE': {'category': 'manager', 'icon': 'fa-heart', 'description': 'Supporting staff with disabilities and mental health conditions.'},
        'MANAGERS_MENOPAUSE_GUIDE': {'category': 'manager', 'icon': 'fa-venus', 'description': 'Menopause support and workplace adjustments.'},
        'MANAGERS_ABSENCE_INTERVIEW_GUIDE': {'category': 'manager', 'icon': 'fa-comments', 'description': 'Conducting long-term absence interviews effectively.'},
        'AUTOMATED_WEEKLY_REPORTS': {'category': 'manager', 'icon': 'fa-calendar-alt', 'description': 'Guide to automated Monday management reports.'},
        'SAMPLE_ROTA_ORCHARD_GROVE': {'category': 'rota', 'icon': 'fa-calendar', 'description': 'Example 6-week rota pattern for Orchard Grove care home.'},
        'SYSTEM_FEATURE_INDEX': {'category': 'system', 'icon': 'fa-list', 'description': 'Complete index of all system features and capabilities.'},
        'SYSTEM_SOP_INDEX': {'category': 'system', 'icon': 'fa-book', 'description': 'Index of all Standard Operating Procedures.'},
        'POLICY_INTEGRATION_SUMMARY': {'category': 'system', 'icon': 'fa-file-contract', 'description': 'How organizational policies integrate with the system.'},
        'MANAGER_GUIDANCE_INTEGRATION_SUMMARY': {'category': 'manager', 'icon': 'fa-puzzle-piece', 'description': 'How manager guidance integrates across the platform.'},
        'VIDEO_PRODUCTION_PACKAGE': {'category': 'system', 'icon': 'fa-video', 'description': 'Video tutorial production guide and scripts.'},
        'SOP_SHIFT_MANAGEMENT': {'category': 'sop', 'icon': 'fa-clock', 'description': 'Standard procedures for managing shifts and rotas.'},
        'SOP_ANNUAL_LEAVE': {'category': 'sop', 'icon': 'fa-umbrella-beach', 'description': 'Annual leave approval and management procedures.'},
        'SOP_ADDITIONAL_STAFFING': {'category': 'sop', 'icon': 'fa-user-plus', 'description': 'Requesting and managing additional staffing needs.'},
        'SOP_STAFF_ONBOARDING': {'category': 'sop', 'icon': 'fa-user-graduate', 'description': 'New staff onboarding and system access procedures.'},
        'SOP_SYSTEM_MAINTENANCE': {'category': 'sop', 'icon': 'fa-tools', 'description': 'System maintenance and technical procedures.'},
        'SOP_COMPLIANCE_REPORTING': {'category': 'sop', 'icon': 'fa-file-invoice', 'description': 'Compliance reporting and audit trail procedures.'},
        'SOP_CARE_PLAN_REVIEWS': {'category': 'sop', 'icon': 'fa-file-medical-alt', 'description': 'Care plan review scheduling and tracking.'},
        'CARE_INSPECTORATE_INCIDENT_REPORT': {'category': 'care_inspectorate', 'icon': 'fa-exclamation-triangle', 'description': 'Incident reporting template for Care Inspectorate.'},
        'CARE_INSPECTORATE_INDUCTION_CHECKLIST': {'category': 'care_inspectorate', 'icon': 'fa-list-check', 'description': 'Staff induction checklist for Care Inspectorate compliance.'},
        'CARE_INSPECTORATE_SUPERVISION_RECORD': {'category': 'care_inspectorate', 'icon': 'fa-clipboard-list', 'description': 'Supervision record template for Care Inspectorate.'},
        'CARE_INSPECTORATE_TRAINING_MATRIX': {'category': 'care_inspectorate', 'icon': 'fa-graduation-cap', 'description': 'Training matrix template for Care Inspectorate compliance.'},
    }
    
    # Dynamically scan for all markdown files
    guidance_docs = []
    try:
        if docs_path.exists():
            for md_file in sorted(docs_path.glob('*.md')):
                # Get filename without extension for slug
                filename = md_file.stem
                slug = filename.lower().replace('_', '-')
                
                # Get metadata or use defaults
                meta = doc_metadata.get(filename, {})
                category = meta.get('category', 'other')
                icon = meta.get('icon', 'fa-file-alt')
                description = meta.get('description', f'Guidance document: {filename.replace("_", " ").title()}')
                
                # Create readable title from filename
                title = filename.replace('_', ' ').title()
                
                guidance_docs.append({
                    'title': title,
                    'slug': slug,
                    'description': description,
                    'file': md_file,
                    'category': category,
                    'icon': icon,
                })
    except Exception as e:
        # Fallback to ensure view doesn't break
        print(f"Error loading guidance documents: {e}")
        guidance_docs = [{
            'title': 'Error Loading Documents',
            'slug': 'error',
            'description': 'Unable to load guidance documents. Please contact support.',
            'file': None,
            'category': 'system',
            'icon': 'fa-exclamation-triangle',
        }]

    # Ensure we have at least one document
    if not guidance_docs:
        guidance_docs = [{
            'title': 'No Documents Available',
            'slug': 'no-docs',
            'description': 'No guidance documents are currently available.',
            'file': None,
            'category': 'system',
            'icon': 'fa-folder-open',
        }]

    selected_slug = request.GET.get('doc') or guidance_docs[0]['slug']
    selected_doc = next((doc for doc in guidance_docs if doc['slug'] == selected_slug), guidance_docs[0])
    
    try:
        if selected_doc['file'] and selected_doc['file'].exists():
            with selected_doc['file'].open('r', encoding='utf-8') as handle:
                raw_text = handle.read()
                # Convert markdown to HTML
                md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
                html_content = md.convert(raw_text)
                selected_doc['content'] = mark_safe(html_content)
        else:
            selected_doc['content'] = mark_safe('<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> Document file not found. Please check the repository.</div>')
    except FileNotFoundError:
        selected_doc['content'] = mark_safe('<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> Document file not found. Please check the repository.</div>')
    except Exception as e:
        selected_doc['content'] = mark_safe(f'<div class="alert alert-danger"><i class="fas fa-times-circle"></i> Error loading document: {escape(str(e))}</div>')
    
    context = {
        'guidance_docs': guidance_docs,
        'selected_doc': selected_doc,
    }

    return render(request, 'scheduling/staff_guidance.html', context)'''

# Find the start and end of the staff_guidance function
pattern = r'def staff_guidance\(request\):.*?(?=\n@login_required\s+\ndef rota_view|$)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Replace the function
    new_content = content[:match.start()] + new_function + '\n\n' + content[match.end():]
    
    # Write back
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('✅ Successfully updated staff_guidance function to dynamically load all markdown files')
    print('📁 Will now show all 36 documents from /home/docs/staff_guidance/')
else:
    print('❌ Could not find staff_guidance function')
    exit(1)
