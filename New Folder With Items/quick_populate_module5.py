"""Quick population script for Module 5 Policies & Procedures"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from policies_procedures.models import Policy, PolicyVersion

User = get_user_model()

print("Module 5: Policies & Procedures - Quick Population")
print("=" * 50)

# Get first staff user
user = User.objects.filter(is_staff=True).first()

if not user:
    print("❌ No staff users found!")
    print("   Please create a staff user first.")
    exit(1)

print(f"✓ Using User: {user.get_full_name()}")
print()

# Clear existing data
print("Clearing existing policy data...")
PolicyVersion.objects.all().delete()
Policy.objects.all().delete()
print("✓ Cleared")
print()

# Create sample policies
print("Creating sample policies...")

policy1 = Policy.objects.create(
    title='Infection Prevention and Control Policy',
    policy_number='POL-001',
    category='infection_control',
    effective_date=timezone.now().date() - timedelta(days=180),
    next_review_date=timezone.now().date() + timedelta(days=185),
    review_frequency_months=12,
    status='active',
    version=1.0,
    summary='Comprehensive IPC policy covering hand hygiene, PPE use, isolation procedures, and outbreak management',
    keywords='IPC, infection control, hand hygiene, PPE, isolation, COVID-19',
    regulatory_framework='Care Inspectorate - Health and Wellbeing outcome, HIS IPC Standards, Scottish Government IPC guidance',
    owner=user,
    department='Clinical Services',
    is_mandatory=True
)

policy2 = Policy.objects.create(
    title='Safeguarding Adults Policy',
    policy_number='POL-002',
    category='safeguarding',
    effective_date=timezone.now().date() - timedelta(days=90),
    next_review_date=timezone.now().date() + timedelta(days=275),
    review_frequency_months=12,
    status='active',
    version=2.0,
    summary='Protection of vulnerable adults from abuse, neglect, and harm. Covers reporting procedures and multi-agency working',
    keywords='safeguarding, adult protection, abuse, neglect, reporting, MARAC',
    regulatory_framework='Adult Support and Protection (Scotland) Act 2007, Care Inspectorate safeguarding standards',
    owner=user,
    department='Safeguarding',
    is_mandatory=True
)

policy3 = Policy.objects.create(
    title='Medication Management Policy',
    policy_number='POL-003',
    category='clinical',
    effective_date=timezone.now().date() - timedelta(days=120),
    next_review_date=timezone.now().date() + timedelta(days=245),
    review_frequency_months=12,
    status='active',
    version=1.5,
    summary='Safe medication ordering, storage, administration, disposal, and error reporting procedures',
    keywords='medication, MAR, e-MAR, controlled drugs, medication errors, pharmacy',
    regulatory_framework='Care Inspectorate medication standards, HIS medication safety requirements, Nursing and Midwifery Council guidelines',
    owner=user,
    department='Clinical Services',
    is_mandatory=True
)

policy4 = Policy.objects.create(
    title='Health and Safety Policy',
    policy_number='POL-004',
    category='health_safety',
    effective_date=timezone.now().date() - timedelta(days=365),
    next_review_date=timezone.now().date() + timedelta(days=365),
    review_frequency_months=24,
    status='active',
    version=3.0,
    summary='Comprehensive H&S policy covering risk assessment, fire safety, manual handling, COSHH, and accident reporting',
    keywords='health and safety, risk assessment, fire safety, manual handling, COSHH, accidents',
    regulatory_framework='Health and Safety at Work Act 1974, Care Inspectorate quality indicators',
    owner=user,
    department='Health & Safety',
    is_mandatory=True
)

policy5 = Policy.objects.create(
    title='Staff Training and Development Policy',
    policy_number='POL-005',
    category='hr',
    effective_date=timezone.now().date() - timedelta(days=200),
    next_review_date=timezone.now().date() + timedelta(days=165),
    review_frequency_months=12,
    status='active',
    version=1.0,
    summary='Mandatory training requirements, continuing professional development, and competency assessment',
    keywords='training, CPD, competency, mandatory training, induction, SSSC',
    regulatory_framework='SSSC codes of practice, Care Inspectorate workforce standards',
    owner=user,
    department='Human Resources',
    is_mandatory=True
)

policy6 = Policy.objects.create(
    title='Falls Prevention Policy',
    policy_number='POL-006',
    category='clinical',
    effective_date=timezone.now().date() - timedelta(days=45),
    next_review_date=timezone.now().date() + timedelta(days=320),
    review_frequency_months=12,
    status='active',
    version=1.0,
    summary='Falls risk assessment, prevention strategies, post-fall management, and analysis',
    keywords='falls, falls prevention, falls risk assessment, mobility, physiotherapy',
    regulatory_framework='Care Inspectorate - Health and Wellbeing, HIS falls prevention standards',
    owner=user,
    department='Clinical Services',
    is_mandatory=True
)

# One draft policy
policy7 = Policy.objects.create(
    title='Social Media and Digital Communications Policy',
    policy_number='POL-007',
    category='it_data',
    effective_date=timezone.now().date() + timedelta(days=30),
    next_review_date=timezone.now().date() + timedelta(days=395),
    review_frequency_months=12,
    status='draft',
    version=0.5,
    summary='Guidelines for staff use of social media, protecting resident confidentiality and organizational reputation',
    keywords='social media, digital communications, confidentiality, GDPR, online presence',
    regulatory_framework='GDPR, Data Protection Act 2018, Care Inspectorate confidentiality standards',
    owner=user,
    department='IT & Communications',
    is_mandatory=False
)

print(f"✓ Created {Policy.objects.count()} policies")
print()

# Create sample versions for Policy 2 (which is v2.0)
print("Creating version history...")
PolicyVersion.objects.create(
    policy=policy2,
    version_number=1.0,
    change_summary='Initial policy creation - First version of safeguarding policy based on Adult Support and Protection (Scotland) Act 2007',
    created_by=user,
    is_current=False
)

PolicyVersion.objects.create(
    policy=policy2,
    version_number=2.0,
    change_summary='Major update following Adult Support and Protection Act amendments. Updated to reflect 2016 amendments to ASP Act. Added sections on self-directed support and updated multi-agency working procedures',
    created_by=user,
    is_current=True
)

print(f"✓ Created {PolicyVersion.objects.count()} version records")
print()

print("=" * 50)
print("✅ MODULE 5 POPULATION COMPLETE!")
print(f"   • {Policy.objects.count()} policies created")
print(f"      - {Policy.objects.filter(status='active').count()} active")
print(f"      - {Policy.objects.filter(status='draft').count()} draft")
print(f"   • {PolicyVersion.objects.count()} version records")
print()
print("Access at: http://127.0.0.1:8000/policies-procedures/")
print("=" * 50)
