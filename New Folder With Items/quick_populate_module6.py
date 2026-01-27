"""Quick population script for Module 6 Risk Management"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from risk_management.models import RiskCategory, RiskRegister
from scheduling.models import CareHome

User = get_user_model()

print("Module 6: Risk Management - Quick Population")
print("=" * 50)

# Get first care home and user
care_home = CareHome.objects.first()
user = User.objects.filter(is_staff=True).first()

if not care_home or not user:
    print("❌ No care homes or staff users found!")
    print("   Please create a care home and staff user first.")
    exit(1)

print(f"✓ Using Care Home: {care_home.name}")
print(f"✓ Using User: {user.get_full_name()}")
print()

# Clear existing data
print("Clearing existing risk data...")
RiskRegister.objects.all().delete()
RiskCategory.objects.all().delete()
print("✓ Cleared")
print()

# Create top-level categories
print("Creating risk categories...")
clinical = RiskCategory.objects.create(
    name='Clinical & Care Quality',
    description='Risks related to resident care and clinical practice',
    color='#dc3545',
    his_domain='Person-Centred Care',
    care_inspectorate_theme='Health and Wellbeing'
)

operational = RiskCategory.objects.create(
    name='Operational',
    description='Day-to-day operational risks',
    color='#fd7e14'
)

regulatory = RiskCategory.objects.create(
    name='Regulatory & Compliance',
    description='Compliance with Scottish care regulations',
    color='#ffc107',
    his_domain='Safe Care',
    care_inspectorate_theme='Leadership and Management'
)

# Create subcategories
medication = RiskCategory.objects.create(
    name='Medication Management',
    description='Medication administration and storage',
    parent=clinical,
    color='#dc3545',
    his_domain='Safe Care'
)

staffing = RiskCategory.objects.create(
    name='Staffing & Workforce',
    description='Staff recruitment, retention, and competency',
    parent=operational,
    color='#fd7e14',
    care_inspectorate_theme='Staff and Volunteers'
)

print(f"✓ Created {RiskCategory.objects.count()} categories")
print()

# Create sample risks
print("Creating sample risks...")

risk1 = RiskRegister.objects.create(
    title='Medication Administration Errors',
    description='Risk of incorrect medication being administered to residents',
    category=medication,
    care_home=care_home,
    affected_area='All units - medication rounds',
    inherent_likelihood=4,
    inherent_impact=5,
    current_controls='Double-checking procedures, MAR charts, e-MAR system',
    control_effectiveness=4,
    residual_likelihood=2,
    residual_impact=4,
    risk_owner=user,
    assigned_to=user,
    identified_by=user,
    identified_date=timezone.now().date() - timedelta(days=90),
    status='CONTROLLED',
    review_frequency='MONTHLY',
    next_review_date=timezone.now().date() + timedelta(days=15),
    regulatory_requirement='Care Inspectorate - Health and Wellbeing outcome'
)

risk2 = RiskRegister.objects.create(
    title='Staff Shortage - Qualified Nurses',
    description='Insufficient qualified nursing staff to meet resident needs',
    category=staffing,
    care_home=care_home,
    affected_area='Nursing units',
    inherent_likelihood=4,
    inherent_impact=4,
    current_controls='Agency staff contracts, recruitment campaigns, retention bonuses',
    control_effectiveness=3,
    residual_likelihood=3,
    residual_impact=4,
    risk_owner=user,
    assigned_to=user,
    identified_by=user,
    identified_date=timezone.now().date() - timedelta(days=60),
    status='TREATMENT',
    review_frequency='MONTHLY',
    next_review_date=timezone.now().date() + timedelta(days=20),
    regulatory_requirement='SSSC registration requirements, Care Inspectorate staffing standards',
    is_escalated=True
)

risk3 = RiskRegister.objects.create(
    title='Care Inspectorate Grade Reduction',
    description='Risk of receiving lower grades in Care Inspectorate inspection',
    category=regulatory,
    care_home=care_home,
    affected_area='All services',
    inherent_likelihood=3,
    inherent_impact=5,
    current_controls='Quality assurance framework, regular audits, staff supervision',
    control_effectiveness=4,
    residual_likelihood=2,
    residual_impact=4,
    risk_owner=user,
    assigned_to=user,
    identified_by=user,
    identified_date=timezone.now().date() - timedelta(days=150),
    status='ASSESSED',
    review_frequency='QUARTERLY',
    next_review_date=timezone.now().date() + timedelta(days=45),
    regulatory_requirement='Care Inspectorate - All Health and Social Care Standards'
)

print(f"✓ Created {RiskRegister.objects.count()} risks")
print()

print("=" * 50)
print("✅ MODULE 6 POPULATION COMPLETE!")
print(f"   • {RiskCategory.objects.count()} risk categories")
print(f"   • {RiskRegister.objects.count()} risks in register")
print()
print("Access at: http://127.0.0.1:8000/risk-management/")
print("=" * 50)
