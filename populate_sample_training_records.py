"""
Populate sample training records for demonstration purposes
Run with: python3 manage.py shell < populate_sample_training_records.py
"""

from scheduling.models import User, TrainingCourse, TrainingRecord, CareHome
from datetime import date, timedelta
from decimal import Decimal
import random

# Get mandatory courses
mandatory_courses = list(TrainingCourse.objects.filter(is_mandatory=True))

if not mandatory_courses:
    print("ERROR: No mandatory courses found. Run populate_mandatory_training.py first.")
    exit()

print(f"Found {len(mandatory_courses)} mandatory courses")

# Get all active staff with units
staff_with_units = User.objects.filter(
    is_active=True,
    unit__isnull=False
).distinct().select_related('unit__care_home')

total_staff = staff_with_units.count()
print(f"Found {total_staff} active staff members with units assigned")

if total_staff == 0:
    print("ERROR: No staff found with unit assignments.")
    exit()

# Group staff by home
homes_staff = {}
for staff in staff_with_units:
    home_name = staff.unit.care_home.name
    if home_name not in homes_staff:
        homes_staff[home_name] = []
    homes_staff[home_name].append(staff)

print(f"\nStaff distribution across homes:")
for home_name, staff_list in homes_staff.items():
    print(f"  {home_name}: {len(staff_list)} staff")

# Create training records with varying compliance levels
created_count = 0
skipped_count = 0

print("\n" + "=" * 60)
print("Creating Sample Training Records...")
print("=" * 60)

# Define compliance patterns for each home (to show different levels)
home_compliance_targets = {
    'ORCHARD_GARDENS': 0.95,  # 95% - excellent
    'HAWTHORN_HOUSE': 0.85,   # 85% - good
    'VICTORIA_GARDENS': 0.75,  # 75% - needs attention
    'PRIMROSE_MANOR': 0.65,    # 65% - poor
    'WILLOW_GRANGE': 0.55,     # 55% - critical
}

for home_name, staff_list in homes_staff.items():
    compliance_rate = home_compliance_targets.get(home_name, 0.70)
    print(f"\n{home_name} (Target: {int(compliance_rate * 100)}% compliance)")
    print("-" * 60)
    
    for staff in staff_list:
        # Determine how many courses this staff member should have
        num_courses = int(len(mandatory_courses) * compliance_rate)
        if random.random() < (compliance_rate % 1):  # Handle fractional parts
            num_courses += 1
        
        # Randomly select which courses
        staff_courses = random.sample(mandatory_courses, min(num_courses, len(mandatory_courses)))
        
        for course in staff_courses:
            # Check if record already exists
            existing = TrainingRecord.objects.filter(
                staff_member=staff,
                course=course
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # Randomize completion dates to create varied statuses
            days_ago = random.randint(0, course.validity_months * 30)
            completion_date = date.today() - timedelta(days=days_ago)
            expiry_date = completion_date + timedelta(days=course.validity_months * 30)
            
            # Calculate status
            days_until_expiry = (expiry_date - date.today()).days
            if days_until_expiry < 0:
                status = "EXPIRED"
            elif days_until_expiry <= 30:
                status = "EXPIRING_SOON"
            else:
                status = "CURRENT"
            
            # Create the record
            record = TrainingRecord.objects.create(
                staff_member=staff,
                course=course,
                completion_date=completion_date,
                expiry_date=expiry_date,
                trainer_name=random.choice([
                    'Sarah Johnson',
                    'Michael Brown',
                    'Emma Wilson',
                    'SSSC Training',
                    'NHS Education',
                    'Care Training Scotland'
                ]),
                training_provider=random.choice([
                    'SSSC',
                    'NHS Education for Scotland',
                    'Care Training Scotland',
                    'Internal Training Team'
                ]),
                certificate_number=f"CERT-{random.randint(10000, 99999)}",
                sssc_cpd_hours_claimed=course.sssc_cpd_hours,
                notes=f"Training completed successfully. Status: {status}",
                created_by=staff  # Self-reported
            )
            
            created_count += 1
            
            # Print progress for each staff member
            if created_count % 10 == 0:
                print(f"  Created {created_count} records...")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print(f"Created: {created_count} training records")
print(f"Skipped: {skipped_count} records (already exist)")
print(f"Total records in database: {TrainingRecord.objects.count()}")

# Show compliance summary
print("\n" + "=" * 60)
print("Compliance Summary by Home")
print("=" * 60)

for home_name, staff_list in homes_staff.items():
    total_required = len(staff_list) * len(mandatory_courses)
    total_compliant = 0
    
    for staff in staff_list:
        for course in mandatory_courses:
            latest = TrainingRecord.objects.filter(
                staff_member=staff,
                course=course
            ).order_by('-completion_date').first()
            
            if latest and latest.get_status() == 'CURRENT':
                total_compliant += 1
    
    compliance_pct = (total_compliant / total_required * 100) if total_required > 0 else 0
    
    print(f"\n{home_name}:")
    print(f"  Staff: {len(staff_list)}")
    print(f"  Compliant: {total_compliant} / {total_required} required")
    print(f"  Compliance: {compliance_pct:.1f}%")

print("\n✅ Sample training records created successfully!")
print("Visit /compliance/training/management/ to view the dashboard")
