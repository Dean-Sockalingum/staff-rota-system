"""
Populate standard mandatory training courses for care homes
Run with: python3 manage.py shell < populate_mandatory_training.py
"""

from scheduling.models import TrainingCourse

# Define standard mandatory training courses for Scottish care homes
mandatory_courses = [
    {
        'name': 'Fire Safety Awareness',
        'category': 'ESSENTIAL',
        'description': 'Essential fire safety training covering fire prevention, evacuation procedures, and use of fire equipment.',
        'frequency': 'ANNUAL',
        'validity_months': 12,
        'is_mandatory': True,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 2.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 2.0,
    },
    {
        'name': 'Moving & Handling',
        'category': 'ESSENTIAL',
        'description': 'Safe moving and handling techniques to prevent injury to staff and residents.',
        'frequency': 'ANNUAL',
        'validity_months': 12,
        'is_mandatory': True,
        'requires_competency_assessment': True,
        'requires_certificate': True,
        'minimum_hours': 3.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 3.0,
    },
    {
        'name': 'Adult Support & Protection',
        'category': 'ESSENTIAL',
        'description': 'Safeguarding vulnerable adults and recognizing signs of abuse or neglect.',
        'frequency': '2_YEAR',
        'validity_months': 24,
        'is_mandatory': True,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 3.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 3.0,
    },
    {
        'name': 'First Aid at Work',
        'category': 'ESSENTIAL',
        'description': 'Emergency first aid procedures and life-saving techniques.',
        'frequency': '3_YEAR',
        'validity_months': 36,
        'is_mandatory': True,
        'requires_competency_assessment': True,
        'requires_certificate': True,
        'minimum_hours': 18.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 18.0,
    },
    {
        'name': 'Infection Prevention & Control',
        'category': 'ESSENTIAL',
        'description': 'Prevention and control of infections including hand hygiene and PPE use.',
        'frequency': 'ANNUAL',
        'validity_months': 12,
        'is_mandatory': True,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 2.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 2.0,
    },
    {
        'name': 'Food Hygiene Level 2',
        'category': 'ESSENTIAL',
        'description': 'Safe food handling and hygiene practices for care settings.',
        'frequency': '3_YEAR',
        'validity_months': 36,
        'is_mandatory': True,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 6.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 6.0,
    },
    {
        'name': 'Medication Administration',
        'category': 'CLINICAL',
        'description': 'Safe administration of medications including storage, recording, and error reporting.',
        'frequency': 'ANNUAL',
        'validity_months': 12,
        'is_mandatory': True,
        'requires_competency_assessment': True,
        'requires_certificate': True,
        'minimum_hours': 4.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 4.0,
    },
    {
        'name': 'Health & Safety in the Workplace',
        'category': 'ESSENTIAL',
        'description': 'General health and safety awareness for care home environments.',
        'frequency': 'ANNUAL',
        'validity_months': 12,
        'is_mandatory': True,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 2.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 2.0,
    },
    {
        'name': 'GDPR & Data Protection',
        'category': 'ESSENTIAL',
        'description': 'Understanding GDPR requirements and maintaining confidentiality in care settings.',
        'frequency': 'ANNUAL',
        'validity_months': 12,
        'is_mandatory': True,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 1.5,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 1.5,
    },
    {
        'name': 'Dementia Awareness',
        'category': 'PERSON_CENTRED',
        'description': 'Understanding dementia and person-centred approaches to dementia care.',
        'frequency': '2_YEAR',
        'validity_months': 24,
        'is_mandatory': True,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 4.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 4.0,
    },
    {
        'name': 'Mental Health Awareness',
        'category': 'PERSON_CENTRED',
        'description': 'Recognizing and supporting mental health needs in older adults.',
        'frequency': '2_YEAR',
        'validity_months': 24,
        'is_mandatory': False,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 3.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 3.0,
    },
    {
        'name': 'Equality & Diversity',
        'category': 'PERSON_CENTRED',
        'description': 'Promoting equality, diversity, and human rights in care delivery.',
        'frequency': '2_YEAR',
        'validity_months': 24,
        'is_mandatory': True,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 2.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 2.0,
    },
    {
        'name': 'Palliative & End of Life Care',
        'category': 'CLINICAL',
        'description': 'Providing dignified and compassionate end of life care.',
        'frequency': '2_YEAR',
        'validity_months': 24,
        'is_mandatory': False,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 3.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 3.0,
    },
    {
        'name': 'Oral Health Care',
        'category': 'CLINICAL',
        'description': 'Maintaining oral hygiene and dental health for residents.',
        'frequency': '2_YEAR',
        'validity_months': 24,
        'is_mandatory': False,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 1.5,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 1.5,
    },
    {
        'name': 'Continence Care',
        'category': 'CLINICAL',
        'description': 'Managing continence issues with dignity and promoting independence.',
        'frequency': '2_YEAR',
        'validity_months': 24,
        'is_mandatory': False,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 2.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 2.0,
    },
    {
        'name': 'Nutrition & Hydration',
        'category': 'CLINICAL',
        'description': 'Supporting nutritional needs and maintaining adequate hydration.',
        'frequency': '2_YEAR',
        'validity_months': 24,
        'is_mandatory': False,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 2.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 2.0,
    },
    {
        'name': 'Pressure Area Care',
        'category': 'CLINICAL',
        'description': 'Prevention and management of pressure ulcers.',
        'frequency': 'ANNUAL',
        'validity_months': 12,
        'is_mandatory': False,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 2.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 2.0,
    },
    {
        'name': 'Diabetes Care',
        'category': 'CLINICAL',
        'description': 'Managing diabetes in care home residents including monitoring and emergency response.',
        'frequency': '2_YEAR',
        'validity_months': 24,
        'is_mandatory': False,
        'requires_competency_assessment': False,
        'requires_certificate': True,
        'minimum_hours': 2.0,
        'sssc_cpd_eligible': True,
        'sssc_cpd_hours': 2.0,
    },
]

# Create courses
created_count = 0
skipped_count = 0

print("Populating Training Courses...")
print("-" * 60)

for course_data in mandatory_courses:
    # Check if course already exists
    existing = TrainingCourse.objects.filter(name=course_data['name']).first()
    
    if existing:
        print(f"SKIPPED: {course_data['name']} (already exists)")
        skipped_count += 1
    else:
        course = TrainingCourse.objects.create(**course_data)
        status = "MANDATORY" if course.is_mandatory else "Optional"
        print(f"CREATED: {course.name} ({status}, {course.get_frequency_display()})")
        created_count += 1

print("-" * 60)
print(f"\nSummary:")
print(f"  Created: {created_count} courses")
print(f"  Skipped: {skipped_count} courses (already exist)")
print(f"  Total in database: {TrainingCourse.objects.count()} courses")
print(f"  Mandatory courses: {TrainingCourse.objects.filter(is_mandatory=True).count()}")
print("\nMandatory Training Courses:")
for course in TrainingCourse.objects.filter(is_mandatory=True).order_by('name'):
    print(f"  • {course.name} - {course.get_frequency_display()} ({course.validity_months} months)")
