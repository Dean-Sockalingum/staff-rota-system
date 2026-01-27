#!/usr/bin/env python
"""
Fix Module 2 templates and create dummy test data
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
from scheduling.models import User, CareHome, IncidentReport

def fix_template_extends():
    """Fix all Module 2 templates to extend 'scheduling/base.html'"""
    templates_dir = Path(__file__).parent / 'incident_safety' / 'templates' / 'incident_safety'
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return
    
    fixed_count = 0
    for template_file in templates_dir.glob('*.html'):
        try:
            content = template_file.read_text()
            
            if "{% extends 'base.html' %}" in content:
                # Replace base.html with scheduling/base.html
                new_content = content.replace(
                    "{% extends 'base.html' %}",
                    "{% extends 'scheduling/base.html' %}"
                )
                template_file.write_text(new_content)
                print(f"✅ Fixed: {template_file.name}")
                fixed_count += 1
        except Exception as e:
            print(f"❌ Error fixing {template_file.name}: {e}")
    
    print(f"\n🎉 Fixed {fixed_count} templates")

def create_dummy_data():
    """Create test data for charts and visualizations"""
    print("\n📊 Creating dummy test data...")
    
    # Get or create care home
    care_home = CareHome.objects.first()
    if not care_home:
        print("❌ No care home found. Creating one...")
        care_home = CareHome.objects.create(
            home_id="TEST-001",
            name="Test Care Home",
            address_line1="123 Test Street",
            city="Glasgow",
            postcode="G1 1AA"
        )
    
    # Get or create user
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("❌ No active user found")
        return
    
    print(f"Using care home: {care_home.name}")
    print(f"Using user: {user.get_full_name()}")
    
    # Check if data already exists
    if IncidentReport.objects.filter(reference_number__startswith="INC-2026-").exists():
        print("\n⚠️  Test data already exists! Skipping data creation.")
        print("   (If you want to recreate, delete existing test incidents first)")
        return
    
    # Get first resident
    from scheduling.models import Resident
    resident = Resident.objects.first()
    if not resident:
        print("❌ No residents found, will create incidents without resident link")
        resident = None
    
    # Create 10 test incidents with varying data
    incidents_data = [
        {"type": "FALL_UNWITNESSED", "severity": "MAJOR_HARM"},
        {"type": "MED_ERROR_OMISSION", "severity": "MODERATE_HARM"},
        {"type": "FALL_WITNESSED", "severity": "LOW_HARM"},
        {"type": "PHYSICAL_INJURY", "severity": "MAJOR_HARM"},
        {"type": "NEAR_MISS", "severity": "NO_HARM"},
        {"type": "CHOKING", "severity": "MAJOR_HARM"},
        {"type": "FALL_BATHROOM", "severity": "MODERATE_HARM"},
        {"type": "NEAR_MISS", "severity": "NO_HARM"},
        {"type": "MED_ERROR_WRONG_DOSE", "severity": "LOW_HARM"},
        {"type": "FALL_BED", "severity": "MAJOR_HARM"},
    ]
    
    incidents = []
    for i, data in enumerate(incidents_data, 1):
        incident = IncidentReport.objects.create(
            reference_number=f"INC-2026-{i:04d}",
            incident_type=data["type"],
            severity=data["severity"],
            risk_rating="HIGH" if "MAJOR" in data["severity"] else "MODERATE",
            incident_date=date.today() - timedelta(days=i*10),
            incident_time="14:30:00",
            location="Care Home Common Area",
            description=f"Test {data['type'].lower().replace('_', ' ')} incident #{i} - This is sample data for testing charts and visualizations",
            immediate_actions=f"Staff responded immediately to incident #{i}. First aid administered and family notified.",
            reported_by=user,
            service_user_name=f"Test Resident {i}" if resident else "Unknown",
            was_witnessed=i % 2 == 0
        )
        incidents.append(incident)
        print(f"✅ Created incident: {incident}")
    
    # Create RCAs for some incidents
    rca_count = 0
    for i, incident in enumerate(incidents[:5], 1):
        rca = RootCauseAnalysis.objects.create(
            incident=incident,
            lead_investigator=user,
            analysis_method="FISHBONE" if i % 2 == 0 else "5_WHYS",
            status="IN_PROGRESS" if i % 2 == 0 else "APPROVED",
            investigation_start_date=incident.incident_date + timedelta(days=1),
            root_cause_summary=f"Root cause identified for {incident.incident_type} - System/process issue #{i}",
            lessons_learned=f"Key lessons from incident #{i} investigation",
            recommendations=f"Recommendations to prevent recurrence of incident #{i}"
        )
        rca_count += 1
        print(f"✅ Created RCA: {rca}")
    
    # Create Safety Action Plans
    action_plan_count = 0
    for i in range(1, 8):
        days_ago = i * 15
        target_date = date.today() + timedelta(days=30 - (i * 5))
        
        action_plan = SafetyActionPlan.objects.create(
            incident=incidents[i-1] if i <= len(incidents) else None,
            reference_number=f"SAP-2026-{i:03d}",
            action_type="CORRECTIVE" if i % 2 == 0 else "PREVENTIVE",
            priority="HIGH" if i <= 3 else "MEDIUM" if i <= 5 else "LOW",
            status="IN_PROGRESS" if i <= 4 else "COMPLETED",
            problem_statement=f"Safety concern #{i} identified through incident analysis",
            action_description=f"Safety action plan #{i} - Implement improved protocols to prevent recurrence",
            expected_outcome=f"Reduced incidents and improved safety measures for issue #{i}",
            action_owner=user,
            target_completion_date=target_date
        )
        action_plan_count += 1
        print(f"✅ Created Safety Action Plan: {action_plan}")
    
    # Create Duty of Candour records
    doc_count = 0
    for i in range(1, 4):
        doc = DutyOfCandourRecord.objects.create(
            incident=incidents[i-1],
            duty_of_candour_applies=True,
            harm_level="MODERATE" if i == 1 else "SEVERE",
            assessment_rationale=f"DoC assessment #{i} - Incident met criteria for duty of candour",
            assessed_by=user,
            assessment_date=incidents[i-1].incident_date,
            resident=resident,
            family_contact_name=f"Family Member {i}",
            family_contact_relationship="Next of Kin",
            family_preferred_contact_method="PHONE",
            notification_date=incidents[i-1].incident_date + timedelta(days=1),
            notification_method="Phone call followed by written confirmation",
            notification_by=user,
            apology_provided=True,
            candour_stage="COMPLETE" if i == 1 else "INVESTIGATION"
        )
        doc_count += 1
        print(f"✅ Created Duty of Candour: {doc}")
    
    # Create Trend Analysis
    trend_count = 0
    for i in range(1, 3):
        trend = IncidentTrendAnalysis.objects.create(
            care_home=care_home,
            period_type="MONTHLY" if i == 1 else "QUARTERLY",
            start_date=date.today() - timedelta(days=90),
            end_date=date.today(),
            total_incidents=len(incidents),
            trend_vs_previous_period="DECREASING" if i == 1 else "STABLE",
            percentage_change=-15.5 if i == 1 else 2.3,
            most_common_incident_type="FALL_UNWITNESSED",
            most_common_location="Common Area"
        )
        trend_count += 1
        print(f"✅ Created Trend Analysis: {trend}")
    
    print(f"\n🎉 Test Data Created:")
    print(f"   - {len(incidents)} Incidents")
    print(f"   - {rca_count} Root Cause Analyses")
    print(f"   - {action_plan_count} Safety Action Plans")
    print(f"   - {doc_count} Duty of Candour Records")
    print(f"   - {trend_count} Trend Analyses")

if __name__ == '__main__':
    print("🔧 Module 2: Fixing Templates and Creating Test Data\n")
    print("=" * 60)
    
    # Fix templates
    fix_template_extends()
    
    # Create test data
    create_dummy_data()
    
    print("\n" + "=" * 60)
    print("✅ All done! Reload your browser to see the changes.")
