#!/usr/bin/env python
"""
Add RCA, Safety Action Plans, DoC, and Trend Analysis data to existing incidents
"""
import os
import django
import sys
from datetime import date, timedelta
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from incident_safety.models import (
    RootCauseAnalysis, SafetyActionPlan,
    DutyOfCandourRecord, IncidentTrendAnalysis
)
from scheduling.models import User, CareHome, IncidentReport, Resident

def create_rca_and_workflow_data():
    """Create RCA, Safety Actions, DoC, and Trend data for existing incidents"""
    print("\n📊 Creating RCA and Workflow Data...\n")
    
    # Get incidents
    incidents = list(IncidentReport.objects.filter(reference_number__startswith="INC-2026-").order_by('incident_date'))
    if not incidents:
        print("❌ No test incidents found!")
        return
    
    print(f"Found {len(incidents)} test incidents")
    
    # Get user and care home
    user = User.objects.filter(is_active=True).first()
    care_home = CareHome.objects.first()
    resident = Resident.objects.first()
    
    # 1. CREATE ROOT CAUSE ANALYSES (5 Whys and Fishbone)
    print("\n🔍 Creating Root Cause Analyses...")
    rca_count = 0
    
    # RCA 1 - Fall incident with 5 Whys
    if len(incidents) >= 1 and not hasattr(incidents[0], 'root_cause_analysis'):
        rca1 = RootCauseAnalysis.objects.create(
            incident=incidents[0],
            lead_investigator=user,
            analysis_method="5_WHYS",
            status="APPROVED",
            investigation_start_date=incidents[0].incident_date + timedelta(days=1),
            investigation_end_date=incidents[0].incident_date + timedelta(days=7),
            # 5 Whys Analysis
            why_1="Why did the resident fall? - Resident lost balance while walking to bathroom",
            why_2="Why did they lose balance? - Floor was wet from recent cleaning",
            why_3="Why was the floor wet? - Cleaning completed but wet floor signs not placed",
            why_4="Why were signs not placed? - Staff member unaware of sign location",
            why_5="Why were they unaware? - New staff, inadequate induction training on safety protocols",
            root_cause_summary="Root cause: Inadequate safety training for new staff members regarding wet floor protocols and hazard signage",
            lessons_learned="All new staff require comprehensive safety induction including location of all safety equipment and wet floor protocols",
            recommendations="1. Update induction checklist to include safety equipment location tour\n2. Implement buddy system for first 2 weeks\n3. Create visual guide showing all safety equipment locations"
        )
        rca_count += 1
        print(f"✅ Created 5 Whys RCA: {rca1.incident.reference_number}")
    
    # RCA 2 - Medication error with Fishbone
    if len(incidents) >= 2 and not hasattr(incidents[1], 'root_cause_analysis'):
        rca2 = RootCauseAnalysis.objects.create(
            incident=incidents[1],
            lead_investigator=user,
            analysis_method="FISHBONE",
            status="APPROVED",
            investigation_start_date=incidents[1].incident_date + timedelta(days=1),
            investigation_end_date=incidents[1].incident_date + timedelta(days=10),
            # Fishbone Analysis
            factor_people="Staff member working double shift, fatigue reported. Interrupted during medication round by phone call.",
            factor_environment="Poor lighting in medication room. Medication stored in similar-looking containers.",
            factor_processes="No double-check system in place. Medication administration record (MAR) chart difficult to read.",
            factor_organization="Short staffing due to sick leave. No cover arranged for busy medication rounds.",
            factor_external="Supplier changed packaging without notice, leading to similar appearance of different medications.",
            root_cause_summary="Multiple contributing factors: Staff fatigue from double shift, inadequate lighting, similar packaging, interrupted workflow, and lack of double-check system",
            lessons_learned="Medication safety requires multiple safeguards including adequate staffing, proper lighting, clear labeling, and interruption-free processes",
            recommendations="1. Implement mandatory double-check for all medications\n2. Improve medication room lighting\n3. Request suppliers use distinct packaging\n4. Establish 'do not interrupt' protocol during medication rounds\n5. Review staffing levels during peak medication times"
        )
        rca_count += 1
        print(f"✅ Created Fishbone RCA: {rca2.incident.reference_number}")
    
    # RCA 3 - Another fall with 5 Whys
    if len(incidents) >= 3 and not hasattr(incidents[2], 'root_cause_analysis'):
        rca3 = RootCauseAnalysis.objects.create(
            incident=incidents[2],
            lead_investigator=user,
            analysis_method="5_WHYS",
            status="IN_PROGRESS",
            investigation_start_date=incidents[2].incident_date + timedelta(days=1),
            why_1="Why did the resident fall? - Tripped over wheelchair footrest in common area",
            why_2="Why was footrest in common area? - Wheelchair left unattended after transfer",
            why_3="Why was it left unattended? - Staff called away urgently to another resident",
            why_4="Why wasn't it moved first? - Staff prioritized resident emergency over equipment",
            why_5="Why no system to manage equipment? - No clear protocol for equipment management during emergencies",
            root_cause_summary="Root cause: Lack of clear protocols for managing mobility equipment during emergency situations",
            lessons_learned="Need clear procedures for safe equipment positioning even during urgent situations",
            recommendations="1. Develop rapid equipment safety protocol\n2. Train all staff on quick-secure techniques\n3. Install designated parking zones for mobility aids"
        )
        rca_count += 1
        print(f"✅ Created 5 Whys RCA (In Progress): {rca3.incident.reference_number}")
    
    # RCA 4 - Injury with Fishbone AND 5 Whys (showing both methods can be documented)
    if len(incidents) >= 4 and not hasattr(incidents[3], 'root_cause_analysis'):
        rca4 = RootCauseAnalysis.objects.create(
            incident=incidents[3],
            lead_investigator=user,
            analysis_method="FISHBONE",
            status="UNDER_REVIEW",
            investigation_start_date=incidents[3].incident_date + timedelta(days=1),
            # Fishbone Analysis
            factor_people="Single staff member assisting transfer. Staff member relatively new to manual handling.",
            factor_environment="Bed height not adjusted to optimal transfer position. Limited space between bed and chair.",
            factor_processes="Risk assessment not reviewed in past 6 months. Transfer plan not updated after resident's weight gain.",
            factor_organization="Insufficient manual handling training refreshers. Equipment maintenance schedule not followed.",
            factor_external="Recommended transfer equipment temporarily out of service awaiting repair.",
            # 5 Whys Analysis (can be used alongside fishbone for deeper drill-down)
            why_1="Why did the resident fall during transfer? - Staff member lost grip during the maneuver",
            why_2="Why did the staff member lose grip? - Transfer was attempted by one person instead of two",
            why_3="Why was only one person available? - Second staff member was not assigned due to perceived low-risk assessment",
            why_4="Why was the risk assessment low? - Risk assessment had not been updated for 6 months despite resident's condition changes",
            why_5="Why wasn't the risk assessment reviewed? - No systematic trigger in place for mandatory review after resident weight/mobility changes",
            root_cause_summary="Contributing factors: Outdated risk assessment, inadequate staffing for transfer, equipment unavailability, and insufficient space. Root cause: No systematic process for triggering risk assessment reviews when resident conditions change.",
            lessons_learned="Transfer safety requires current risk assessments, appropriate equipment, adequate space, and sufficient trained staff. Systems must ensure assessments are reviewed when resident conditions change.",
            recommendations="1. Implement monthly risk assessment reviews\n2. Ensure two staff for all transfers\n3. Establish equipment maintenance priority system\n4. Create space optimization plan for resident rooms\n5. Mandatory risk reassessment triggers after weight changes >5kg or mobility status changes"
        )
        rca_count += 1
        print(f"✅ Created Fishbone RCA (Under Review): {rca4.incident.reference_number}")
    
    # 2. CREATE SAFETY ACTION PLANS
    print("\n📋 Creating Safety Action Plans...")
    sap_count = 0
    
    # Link SAPs to RCAs where they exist
    rcas = RootCauseAnalysis.objects.filter(incident__reference_number__startswith="INC-2026-")
    
    # Get next available SAP number
    existing_saps = SafetyActionPlan.objects.filter(reference_number__startswith="SAP-2026-").count()
    sap_number = existing_saps + 1
    
    for i, rca in enumerate(rcas[:4], 1):
        # Create 2 actions per RCA
        sap1 = SafetyActionPlan.objects.create(
            incident=rca.incident,
            root_cause_analysis=rca,
            reference_number=f"SAP-2026-{sap_number:03d}",
            action_type="CORRECTIVE",
            priority="HIGH" if i <= 2 else "MEDIUM",
            status="IN_PROGRESS" if i <= 2 else "COMPLETED",
            problem_statement=f"Corrective action required based on RCA findings for {rca.incident.incident_type}",
            action_description=f"Implement immediate corrective measures identified in RCA analysis for incident {rca.incident.reference_number}",
            expected_outcome="Prevent recurrence of similar incidents through targeted corrective action",
            action_owner=user,
            identified_date=rca.investigation_end_date if rca.investigation_end_date else date.today(),
            target_completion_date=date.today() + timedelta(days=30),
            actual_completion_date=date.today() - timedelta(days=5) if i > 2 else None,
            implementation_plan="Phase 1: Staff briefing\nPhase 2: Process update\nPhase 3: Monitoring"
        )
        sap_count += 1
        sap_number += 1
        
        sap2 = SafetyActionPlan.objects.create(
            incident=rca.incident,
            root_cause_analysis=rca,
            reference_number=f"SAP-2026-{sap_number:03d}",
            action_type="PREVENTIVE",
            priority="MEDIUM" if i <= 2 else "LOW",
            status="IN_PROGRESS" if i % 2 == 0 else "ASSIGNED",
            problem_statement=f"Preventive action to address systemic issues identified in RCA",
            action_description=f"Long-term preventive measures based on lessons learned from {rca.incident.reference_number}",
            expected_outcome="Systemic improvements to prevent similar incidents organization-wide",
            action_owner=user,
            identified_date=rca.investigation_end_date if rca.investigation_end_date else date.today(),
            target_completion_date=date.today() + timedelta(days=60)
        )
        sap_count += 1
        sap_number += 1
        
    print(f"✅ Created {sap_count} Safety Action Plans")
    
    # 3. CREATE DUTY OF CANDOUR RECORDS
    print("\n💬 Creating Duty of Candour Records...")
    doc_count = 0
    
    # DoC for severe incidents
    severe_incidents = [incidents[0], incidents[1], incidents[3]]  # Falls and med error
    
    for i, incident in enumerate(severe_incidents, 1):
        if not hasattr(incident, 'duty_of_candour'):
            doc = DutyOfCandourRecord.objects.create(
                incident=incident,
                duty_of_candour_applies=True,
                harm_level="MODERATE" if i % 2 == 0 else "SEVERE",
                assessment_rationale=f"Incident resulted in {'moderate' if i % 2 == 0 else 'severe'} harm requiring medical intervention. DoC applies under Duty of Candour (Scotland) Act 2016.",
                assessed_by=user,
                assessment_date=incident.incident_date,
                resident=resident,
                family_contact_name=f"Jane Smith {i}" if i == 1 else f"John Brown {i}" if i == 2 else f"Mary Wilson {i}",
                family_contact_relationship="Daughter" if i % 2 == 1 else "Son",
                family_contact_phone=f"0141 555 {1000+i}",
                family_contact_email=f"family{i}@example.com",
                family_preferred_contact_method="PHONE",
                notification_date=incident.incident_date + timedelta(hours=6),
                notification_method="Phone call followed by face-to-face meeting",
                notification_by=user,
                notification_details=f"Initial phone notification made at {incident.incident_time}. Family member arrived on-site within 2 hours. Full briefing provided by {user.get_full_name()}.",
                apology_provided=True,
                apology_date=incident.incident_date + timedelta(hours=8),
                current_stage="COMPLETE" if i == 1 else "FEEDBACK" if i == 2 else "INVESTIGATION"
            )
            doc_count += 1
            print(f"✅ Created DoC Record for {incident.reference_number}: Stage - {doc.current_stage}")
    
    # 4. CREATE TREND ANALYSES
    print("\n📈 Creating Trend Analyses...")
    trend_count = 0
    
    # Monthly trend analysis
    trend1 = IncidentTrendAnalysis.objects.create(
        care_home=care_home,
        period_type="MONTHLY",
        start_date=date.today() - timedelta(days=30),
        end_date=date.today(),
        total_incidents=len(incidents),
        incidents_by_type={
            "FALL_UNWITNESSED": 3,
            "MED_ERROR_OMISSION": 1,
            "FALL_WITNESSED": 1,
            "PHYSICAL_INJURY": 1,
            "NEAR_MISS": 2,
            "CHOKING": 1,
            "FALL_BATHROOM": 1
        },
        incidents_by_severity={
            "MAJOR_HARM": 5,
            "MODERATE_HARM": 3,
            "LOW_HARM": 2
        },
        trend_vs_previous_period="DECREASING",
        percentage_change=-15.5,
        most_common_incident_type="FALL_UNWITNESSED",
        most_common_location="Common Area",
        peak_incident_times=["14:00-16:00", "20:00-22:00"]
    )
    trend_count += 1
    print(f"✅ Created Monthly Trend Analysis: {trend1.total_incidents} incidents, {trend1.percentage_change}% change")
    
    # Quarterly trend analysis
    trend2 = IncidentTrendAnalysis.objects.create(
        care_home=care_home,
        period_type="QUARTERLY",
        start_date=date.today() - timedelta(days=90),
        end_date=date.today(),
        total_incidents=len(incidents) + 5,  # Including previous months
        incidents_by_type={
            "FALL_UNWITNESSED": 5,
            "MED_ERROR_OMISSION": 2,
            "FALL_WITNESSED": 2,
            "PHYSICAL_INJURY": 2,
            "NEAR_MISS": 3,
            "CHOKING": 1
        },
        incidents_by_severity={
            "MAJOR_HARM": 7,
            "MODERATE_HARM": 5,
            "LOW_HARM": 3
        },
        trend_vs_previous_period="STABLE",
        percentage_change=2.3,
        most_common_incident_type="FALL_UNWITNESSED",
        most_common_location="Common Area",
        peak_incident_times=["06:00-08:00", "14:00-16:00", "20:00-22:00"]
    )
    trend_count += 1
    print(f"✅ Created Quarterly Trend Analysis: {trend2.total_incidents} incidents, {trend2.percentage_change}% change")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Test Data Creation Complete!")
    print("=" * 60)
    print(f"   📊 {len(incidents)} Incident Reports")
    print(f"   🔍 {rca_count} Root Cause Analyses (5 Whys & Fishbone)")
    print(f"   📋 {sap_count} Safety Action Plans")
    print(f"   💬 {doc_count} Duty of Candour Records")
    print(f"   📈 {trend_count} Trend Analyses")
    print("=" * 60)
    print("\n✅ All buttons on Module 2 pages should now display data!")
    print("   Refresh your browser to see the results.\n")

if __name__ == '__main__':
    try:
        create_rca_and_workflow_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
