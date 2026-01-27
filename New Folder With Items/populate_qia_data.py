"""
Populate QIA (Quality Improvement Actions) Sample Data

Creates 15 sample QIAs across all source types for testing and demonstration.
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from quality_audits.models import QualityImprovementAction, QIAUpdate, QIAReview
from scheduling.models import CareHome, CustomUser
from incident_safety.models import IncidentReport
from risk_management.models import RiskRegister

def create_sample_qias():
    """Create 15 sample QIAs"""
    
    # Get care homes and users
    try:
        care_home = CareHome.objects.first()
        if not care_home:
            print("❌ No care homes found. Please run care home setup first.")
            return
        
        # Get users for assignment
        manager = CustomUser.objects.filter(role='MANAGER').first()
        if not manager:
            manager = CustomUser.objects.filter(is_staff=True).first()
        
        if not manager:
            print("❌ No users found. Please create users first.")
            return
            
        print(f"✓ Using care home: {care_home.name}")
        print(f"✓ Using responsible person: {manager.get_full_name()}")
        
    except Exception as e:
        print(f"❌ Error getting care home/users: {e}")
        return
    
    # Clear existing QIAs
    deleted_count = QualityImprovementAction.objects.all().count()
    QualityImprovementAction.objects.all().delete()
    print(f"✓ Deleted {deleted_count} existing QIAs")
    
    # QIA data templates
    qias_data = [
        # INCIDENT-sourced QIAs (3)
        {
            'title': 'Improve Medication Administration Safety Checks',
            'action_type': 'CORRECTIVE',
            'source_type': 'INCIDENT',
            'source_reference': 'INC-2026-001',
            'priority': 'HIGH',
            'problem_description': 'Medication error occurred due to insufficient double-checking procedure during administration.',
            'root_cause': 'Current medication administration protocol lacks robust verification step. Staff not consistently using barcode scanning system.',
            'impact_analysis': 'High risk of repeated medication errors. Potential harm to residents. Risk of Care Inspectorate investigation.',
            'action_plan': '1) Implement mandatory double-check procedure with electronic verification\n2) Provide refresher training on medication safety\n3) Install additional barcode scanners in medication rooms\n4) Weekly medication safety audits for 3 months',
            'success_criteria': '100% compliance with double-check procedure. Zero medication errors for 90 days. All staff trained and competent.',
            'resources_needed': '3x barcode scanners (£1,200), training time (16 hours), audit time',
            'verification_method': 'Monthly medication audits, spot checks, electronic system reports',
            'regulatory_requirement': 'Care Inspectorate QI 1.3 - People experience safe care',
            'requires_ci_notification': True,
            'target_days': 60,
            'status': 'IMPLEMENTING',
            'percent_complete': 45,
        },
        {
            'title': 'Enhance Falls Prevention Program',
            'action_type': 'PREVENTIVE',
            'source_type': 'INCIDENT',
            'source_reference': 'INC-2026-003',
            'priority': 'HIGH',
            'problem_description': 'Increased number of resident falls in bathroom areas during evening shift.',
            'root_cause': 'Insufficient lighting in bathrooms. Walking aids not always within reach. Staff shortages during peak evening period.',
            'impact_analysis': 'Risk of serious injury to residents. Increased hospital admissions. Staff morale impact.',
            'action_plan': '1) Install motion-sensor night lights in all bathrooms\n2) Conduct falls risk assessment for all residents\n3) Increase staffing during 6-9pm period\n4) Implement hourly rounding protocol',
            'success_criteria': '50% reduction in bathroom falls within 3 months. All bathrooms have adequate lighting.',
            'resources_needed': '24x motion sensor lights (£720), 2x additional evening staff, falls assessment tools',
            'verification_method': 'Monthly falls analysis, incident reports, resident/family feedback',
            'regulatory_requirement': 'SSI Regulation 4 - Welfare and safety',
            'requires_ci_notification': False,
            'target_days': 90,
            'status': 'APPROVED',
            'percent_complete': 75,
        },
        {
            'title': 'Improve Duty of Candour Communication Process',
            'action_type': 'CORRECTIVE',
            'source_type': 'INCIDENT',
            'source_reference': 'INC-2026-002',
            'priority': 'CRITICAL',
            'problem_description': 'Delayed notification to family following significant incident. Duty of Candour timeline not met.',
            'root_cause': 'Unclear escalation process for DoC incidents. Manager not informed promptly by on-duty staff.',
            'impact_analysis': 'Breach of Duty of Candour Act 2016. Loss of family trust. Potential regulatory sanction.',
            'action_plan': '1) Create clear DoC escalation flowchart\n2) Implement 24-hour manager on-call system\n3) Provide DoC training to all staff\n4) Create DoC communication templates',
            'success_criteria': '100% DoC incidents notified within 24 hours. All staff can explain DoC process.',
            'resources_needed': 'Training time (8 hours), flowchart design, template development',
            'verification_method': 'DoC incident audits, staff competency assessment',
            'regulatory_requirement': 'Duty of Candour (Scotland) Act 2016',
            'requires_ci_notification': True,
            'target_days': 30,
            'status': 'IDENTIFIED',
            'percent_complete': 10,
        },
        
        # AUDIT-sourced QIAs (3)
        {
            'title': 'Improve Care Plan Documentation Quality',
            'action_type': 'CORRECTIVE',
            'source_type': 'AUDIT',
            'source_reference': 'AUD-2026-Q1',
            'priority': 'MEDIUM',
            'problem_description': 'Internal audit identified 30% of care plans not updated within 6-month review period.',
            'root_cause': 'Staff workload prevents timely reviews. Electronic system reminders not effective. Unclear ownership of review process.',
            'impact_analysis': 'Care plans may not reflect current needs. Risk of inappropriate care delivery.',
            'action_plan': '1) Assign named keyworker for each resident\n2) Implement weekly care plan review schedule\n3) Configure electronic alerts 2 weeks before due date\n4) Include care plan updates in supervision',
            'success_criteria': '95% of care plans reviewed on time. Zero overdue reviews older than 1 month.',
            'resources_needed': 'System configuration (4 hours), supervision time',
            'verification_method': 'Monthly care plan audit, electronic system reports',
            'regulatory_requirement': 'Care Inspectorate QI 1.1 - Assessment and care planning',
            'requires_ci_notification': False,
            'target_days': 45,
            'status': 'IMPLEMENTING',
            'percent_complete': 60,
        },
        {
            'title': 'Strengthen Infection Control Compliance',
            'action_type': 'PREVENTIVE',
            'source_type': 'AUDIT',
            'source_reference': 'AUD-2026-IPC',
            'priority': 'HIGH',
            'problem_description': 'Infection control audit showed 85% compliance (target 95%). Gaps in hand hygiene and PPE usage.',
            'root_cause': 'PPE stations not optimally located. Staff forget hand hygiene during busy periods. Lack of peer observation.',
            'impact_analysis': 'Risk of infection outbreaks. Potential resident harm. Care Inspectorate concern.',
            'action_plan': '1) Install 10 additional hand hygiene stations\n2) Implement daily infection control champion rounds\n3) Introduce peer observation program\n4) Weekly IPC huddles',
            'success_criteria': '98% compliance on next audit. Zero outbreaks for 6 months.',
            'resources_needed': '10x hand hygiene stations (£500), champion training, observation tools',
            'verification_method': 'Monthly IPC audits, peer observations, outbreak surveillance',
            'regulatory_requirement': 'Health Protection Scotland guidance, Care Inspectorate QI 1.3',
            'requires_ci_notification': False,
            'target_days': 60,
            'status': 'APPROVED',
            'percent_complete': 30,
        },
        {
            'title': 'Enhance Food Safety Record Keeping',
            'action_type': 'CORRECTIVE',
            'source_type': 'AUDIT',
            'source_reference': 'AUD-2026-ENV',
            'priority': 'MEDIUM',
            'problem_description': 'Environmental health audit found gaps in temperature recording and food traceability.',
            'root_cause': 'Paper-based system prone to omissions. Kitchen staff not trained on HACCP principles.',
            'impact_analysis': 'Risk of Environmental Health enforcement action. Food safety incidents.',
            'action_plan': '1) Implement digital temperature monitoring system\n2) Provide HACCP training to all kitchen staff\n3) Create simplified recording templates\n4) Weekly manager checks',
            'success_criteria': '100% temperature records complete. All kitchen staff HACCP certified.',
            'resources_needed': 'Digital thermometers (£300), HACCP training course (£400)',
            'verification_method': 'Weekly manager audits, Environmental Health re-inspection',
            'regulatory_requirement': 'Food Safety (Scotland) Act 2015',
            'requires_ci_notification': False,
            'target_days': 45,
            'status': 'VERIFIED',
            'percent_complete': 100,
        },
        
        # RISK-sourced QIAs (2)
        {
            'title': 'Mitigate Lone Working Risks During Night Shift',
            'action_type': 'PREVENTIVE',
            'source_type': 'RISK',
            'source_reference': 'RISK-2026-001',
            'priority': 'HIGH',
            'problem_description': 'Risk register identifies lone working as high risk during night shift in annexe building.',
            'root_cause': 'Building layout results in isolated areas. No panic alarm system in annexe.',
            'impact_analysis': 'Staff safety at risk. Delayed response to emergencies. Recruitment/retention impact.',
            'action_plan': '1) Install personal attack alarms for all night staff\n2) Implement buddy system for annexe checks\n3) Install CCTV in corridors\n4) Increase night staff by 1 FTE',
            'success_criteria': 'All lone working eliminated. Zero safety incidents. Staff feel safe (survey).',
            'resources_needed': '6x personal alarms (£300), CCTV system (£2,500), additional FTE (£26,000/year)',
            'verification_method': 'Safety incident monitoring, staff surveys, supervision discussions',
            'regulatory_requirement': 'Health and Safety at Work Act 1974',
            'requires_ci_notification': False,
            'target_days': 90,
            'status': 'IMPLEMENTING',
            'percent_complete': 40,
        },
        {
            'title': 'Address Financial Sustainability Risks',
            'action_type': 'PREVENTIVE',
            'source_type': 'RISK',
            'source_reference': 'RISK-2026-005',
            'priority': 'CRITICAL',
            'problem_description': 'Financial risk assessment shows occupancy below break-even point. Cash flow pressures.',
            'root_cause': 'Local authority funding delays. High staff turnover increases agency costs. Competition from new care home.',
            'impact_analysis': 'Service sustainability at risk. May impact quality of care. Staff uncertainty.',
            'action_plan': '1) Develop recruitment and retention strategy\n2) Negotiate improved payment terms with LA\n3) Marketing campaign for private residents\n4) Cost efficiency review\n5) Diversify into respite/day care',
            'success_criteria': 'Occupancy at 92%. Agency costs reduced by 40%. Positive cash flow.',
            'resources_needed': 'Marketing budget (£5,000), consultant support (£3,000)',
            'verification_method': 'Monthly occupancy reports, financial monitoring, staff turnover tracking',
            'regulatory_requirement': 'N/A - Business sustainability',
            'requires_ci_notification': False,
            'target_days': 180,
            'status': 'PLANNED',
            'percent_complete': 15,
        },
        
        # COMPLAINT-sourced QIAs (2)
        {
            'title': 'Improve Response Time to Call Bells',
            'action_type': 'CORRECTIVE',
            'source_type': 'COMPLAINT',
            'source_reference': 'COMP-2026-003',
            'priority': 'HIGH',
            'problem_description': 'Family complaint about delayed response to mother\'s call bell. Average response time 8 minutes.',
            'root_cause': 'Staff shortages during handover periods. Broken call bells not reported promptly. Staff not prioritizing calls.',
            'impact_analysis': 'Resident dignity and safety compromised. Family distress. Regulatory concern.',
            'action_plan': '1) Implement call bell audit system\n2) Repair/replace faulty call bells\n3) Adjust handover process to maintain floor coverage\n4) Staff training on responsiveness',
            'success_criteria': 'Average response time under 3 minutes. Zero complaints about response time.',
            'resources_needed': 'Call bell audit system (£800), repairs budget (£500)',
            'verification_method': 'Call bell system reports, resident/family surveys, observations',
            'regulatory_requirement': 'Care Inspectorate QI 1.1 - People are treated with dignity',
            'requires_ci_notification': False,
            'target_days': 30,
            'status': 'IMPLEMENTED',
            'percent_complete': 95,
        },
        {
            'title': 'Enhance Activities Program Variety',
            'action_type': 'CORRECTIVE',
            'source_type': 'COMPLAINT',
            'source_reference': 'COMP-2026-001',
            'priority': 'MEDIUM',
            'problem_description': 'Residents and families requesting more varied and meaningful activities. Current program repetitive.',
            'root_cause': 'Activities coordinator working part-time only. Limited budget. Lack of community partnerships.',
            'impact_analysis': 'Resident wellbeing and quality of life. Risk of social isolation.',
            'action_plan': '1) Increase activities coordinator to full-time\n2) Establish links with local schools, choirs, gardening clubs\n3) Introduce personalized activity planning\n4) Create "bucket list" program',
            'success_criteria': 'Activities 7 days/week. Resident participation up 50%. Positive feedback.',
            'resources_needed': 'Additional 0.5 FTE (£13,000/year), activities budget increase (£2,000/year)',
            'verification_method': 'Participation records, resident/family surveys, observation',
            'regulatory_requirement': 'Care Inspectorate QI 2.2 - Opportunities for participation',
            'requires_ci_notification': False,
            'target_days': 60,
            'status': 'APPROVED',
            'percent_complete': 50,
        },
        
        # TREND-sourced QIAs (2)
        {
            'title': 'Reduce Weight Loss Trend in Residents',
            'action_type': 'PREVENTIVE',
            'source_type': 'TREND',
            'source_reference': 'TREND-2026-NUTRITION',
            'priority': 'HIGH',
            'problem_description': 'Trend analysis shows 25% of residents experienced unintentional weight loss in Q4.',
            'root_cause': 'Insufficient nutritional screening. Meal choices not person-centered. Lack of protected mealtimes.',
            'impact_analysis': 'Malnutrition risk. Reduced immunity. Pressure ulcer risk. Quality of life impact.',
            'action_plan': '1) Implement MUST screening for all residents\n2) Dietitian review for all at-risk residents\n3) Introduce protected mealtimes\n4) Fortified food options\n5) Staff training on nutrition',
            'success_criteria': 'Weight loss trend reversed. 90% of residents maintaining healthy weight.',
            'resources_needed': 'Dietitian time (£1,500), fortified foods budget (£800/month), training',
            'verification_method': 'Monthly weight monitoring, MUST screening audits, dietitian reports',
            'regulatory_requirement': 'Care Inspectorate QI 1.3 - Health and wellbeing needs met',
            'requires_ci_notification': False,
            'target_days': 90,
            'status': 'IMPLEMENTING',
            'percent_complete': 35,
        },
        {
            'title': 'Address Staff Sickness Absence Trend',
            'action_type': 'PREVENTIVE',
            'source_type': 'TREND',
            'source_reference': 'TREND-2026-HR',
            'priority': 'MEDIUM',
            'problem_description': 'Staff sickness absence at 8% (sector average 5.2%). Trend increasing over 6 months.',
            'root_cause': 'Work-related stress. Poor workplace wellbeing support. Inadequate occupational health access.',
            'impact_analysis': 'Service continuity risk. Agency costs. Staff morale. Quality of care.',
            'action_plan': '1) Implement staff wellbeing program\n2) Provide access to occupational health\n3) Stress risk assessments\n4) Improve return-to-work process\n5) Staff survey on wellbeing',
            'success_criteria': 'Sickness absence reduced to 6% or below. Improved staff survey scores.',
            'resources_needed': 'OH service contract (£2,000/year), wellbeing activities budget (£1,500)',
            'verification_method': 'Monthly sickness monitoring, staff surveys, return-to-work interviews',
            'regulatory_requirement': 'N/A - HR best practice',
            'requires_ci_notification': False,
            'target_days': 120,
            'status': 'PLANNED',
            'percent_complete': 20,
        },
        
        # PDSA-sourced QIA (1)
        {
            'title': 'Standardize Handover Process Across All Shifts',
            'action_type': 'PREVENTIVE',
            'source_type': 'PDSA',
            'source_reference': 'PDSA-2026-COMM',
            'priority': 'MEDIUM',
            'problem_description': 'PDSA cycle testing showed structured handovers reduce information loss by 60%.',
            'root_cause': 'Handovers currently unstructured. Key information missed. No standardized format.',
            'impact_analysis': 'Information continuity. Care quality. Staff confidence.',
            'action_plan': '1) Implement SBAR handover format\n2) Create handover checklist\n3) Protected handover time (no interruptions)\n4) Train all staff on SBAR',
            'success_criteria': 'SBAR used in 100% of handovers. Zero information loss incidents.',
            'resources_needed': 'SBAR training (4 hours), handover room upgrade (£500)',
            'verification_method': 'Handover audits, staff feedback, incident analysis',
            'regulatory_requirement': 'Care Inspectorate QI 4.1 - Staff skills and knowledge',
            'requires_ci_notification': False,
            'target_days': 45,
            'status': 'VERIFIED',
            'percent_complete': 100,
        },
        
        # INSPECTION-sourced QIAs (2)
        {
            'title': 'Improve Personal Plans for Residents',
            'action_type': 'CORRECTIVE',
            'source_type': 'INSPECTION',
            'source_reference': 'CI-INSP-2025-12',
            'priority': 'CRITICAL',
            'problem_description': 'Care Inspectorate inspection found personal plans not sufficiently outcome-focused or person-centered.',
            'root_cause': 'Staff using task-focused language. Insufficient resident/family involvement in planning.',
            'impact_analysis': 'Grade 3 awarded (adequate). Must improve for next inspection. Regulatory risk.',
            'action_plan': '1) Redesign personal plan template (outcome-focused)\n2) Training on outcome-based planning\n3) Mandatory resident involvement in planning\n4) External consultant support\n5) Monthly QA audits',
            'success_criteria': 'All plans outcome-focused by June 2026. Grade 4+ on re-inspection.',
            'resources_needed': 'Consultant (£3,000), template redesign, training (12 hours)',
            'verification_method': 'Monthly quality audits, Care Inspectorate re-inspection',
            'regulatory_requirement': 'Care Inspectorate QI 1.1 - People experience compassion',
            'requires_ci_notification': True,
            'target_days': 120,
            'status': 'IMPLEMENTING',
            'percent_complete': 55,
        },
        {
            'title': 'Strengthen Leadership and Governance',
            'action_type': 'CORRECTIVE',
            'source_type': 'INSPECTION',
            'source_reference': 'CI-INSP-2025-12',
            'priority': 'HIGH',
            'problem_description': 'Inspection identified need for more robust quality assurance systems and governance.',
            'root_cause': 'QA systems in place but not systematically driving improvement. Action plans not always completed.',
            'impact_analysis': 'QI 4.3 graded as 3 (adequate). Risk of grade reduction if not improved.',
            'action_plan': '1) Implement comprehensive quality assurance framework\n2) Monthly governance meetings\n3) Improvement plan tracking system\n4) Annual quality report to stakeholders\n5) External validation visit',
            'success_criteria': 'All QA systems embedded. Evidence of improvement culture. Grade 4+ on QI 4.3.',
            'resources_needed': 'QA framework development (£2,500), tracking system',
            'verification_method': 'Governance meeting minutes, improvement tracking, Care Inspectorate feedback',
            'regulatory_requirement': 'Care Inspectorate QI 4.3 - Leadership and direction',
            'requires_ci_notification': False,
            'target_days': 90,
            'status': 'APPROVED',
            'percent_complete': 70,
        },
    ]
    
    # Create QIAs
    created_count = 0
    for qia_data in qias_data:
        try:
            # Calculate dates
            target_date = date.today() + timedelta(days=qia_data.pop('target_days'))
            
            # Extract status and percent
            status = qia_data.pop('status')
            percent = qia_data.pop('percent_complete')
            
            # Create QIA
            qia = QualityImprovementAction.objects.create(
                care_home=care_home,
                responsible_person=manager,
                identified_date=date.today() - timedelta(days=30),
                target_completion_date=target_date,
                status=status,
                percent_complete=percent,
                created_by=manager,
                **qia_data
            )
            
            # Add team members
            staff_members = CustomUser.objects.filter(is_staff=True).exclude(pk=manager.pk)[:2]
            qia.team_members.set(staff_members)
            
            # Add progress updates for in-progress QIAs
            if status in ['IMPLEMENTING', 'IMPLEMENTED', 'APPROVED']:
                QIAUpdate.objects.create(
                    qia=qia,
                    updated_by=manager,
                    status_change=f"Moved to {status}",
                    percent_complete=percent,
                    update_notes=f"Progress update: Action plan is progressing well. {percent}% complete.",
                    evidence_description="Meeting minutes, audit results, training records"
                )
            
            # Add review for verified QIAs
            if status == 'VERIFIED':
                QIAReview.objects.create(
                    qia=qia,
                    reviewer=manager,
                    is_effective=True,
                    effectiveness_rating=4,
                    effectiveness_evidence="Data shows significant improvement. Objectives met.",
                    is_sustainable=True,
                    sustainability_plan="Process changes embedded in SOPs. Staff trained and competent.",
                    lessons_learned="Structured approach and staff engagement key to success.",
                    recommend_spread=True,
                    spread_notes="Recommend adopting this approach in other care homes.",
                    approved_for_closure=False
                )
            
            created_count += 1
            print(f"✓ Created QIA: {qia.qia_reference} - {qia.title[:50]}...")
            
        except Exception as e:
            print(f"❌ Error creating QIA '{qia_data.get('title', 'Unknown')}': {e}")
    
    print(f"\n{'='*60}")
    print(f"✓ Successfully created {created_count} QIAs")
    print(f"{'='*60}")
    
    # Summary by source type
    print("\nQIA Summary by Source Type:")
    for source in ['INCIDENT', 'AUDIT', 'RISK', 'COMPLAINT', 'TREND', 'PDSA', 'INSPECTION']:
        count = QualityImprovementAction.objects.filter(source_type=source).count()
        print(f"  {source}: {count} QIAs")
    
    print("\nQIA Summary by Status:")
    for status in ['IDENTIFIED', 'PLANNED', 'APPROVED', 'IMPLEMENTING', 'IMPLEMENTED', 'VERIFIED']:
        count = QualityImprovementAction.objects.filter(status=status).count()
        print(f"  {status}: {count} QIAs")
    
    print("\nQIA Summary by Priority:")
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = QualityImprovementAction.objects.filter(priority=priority).count()
        print(f"  {priority}: {count} QIAs")
    
    print("\n✅ QIA sample data population complete!")
    print(f"Access QIA Dashboard: http://127.0.0.1:8000/quality-audits/qia/")

if __name__ == '__main__':
    create_sample_qias()
