#!/usr/bin/env python3
"""Create mandatory training courses for testing"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import TrainingCourse

# Define the 11 mandatory courses for care homes
mandatory_courses = [
    {
        'name': 'Fire Safety',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 12,
        'sssc_cpd_hours': 1.5,
        'description': 'Fire safety awareness and emergency procedures'
    },
    {
        'name': 'Moving and Handling',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 12,
        'sssc_cpd_hours': 3.0,
        'description': 'Safe moving and handling techniques for residents'
    },
    {
        'name': 'Infection Control',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 12,
        'sssc_cpd_hours': 2.0,
        'description': 'Infection prevention and control procedures'
    },
    {
        'name': 'Food Hygiene',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 36,
        'sssc_cpd_hours': 3.0,
        'description': 'Food hygiene and safety standards'
    },
    {
        'name': 'Adult Support and Protection',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 36,
        'sssc_cpd_hours': 3.0,
        'description': 'Safeguarding vulnerable adults'
    },
    {
        'name': 'First Aid',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 36,
        'sssc_cpd_hours': 6.0,
        'description': 'Emergency first aid procedures'
    },
    {
        'name': 'Health and Safety',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 12,
        'sssc_cpd_hours': 2.0,
        'description': 'Workplace health and safety procedures'
    },
    {
        'name': 'Medication Management',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 12,
        'sssc_cpd_hours': 3.0,
        'description': 'Safe administration and management of medications'
    },
    {
        'name': 'Dementia Awareness',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 36,
        'sssc_cpd_hours': 3.0,
        'description': 'Understanding and supporting people with dementia'
    },
    {
        'name': 'Mental Health Awareness',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 36,
        'sssc_cpd_hours': 2.0,
        'description': 'Mental health awareness and support'
    },
    {
        'name': 'Equality and Diversity',
        'category': 'MANDATORY',
        'is_mandatory': True,
        'validity_months': 36,
        'sssc_cpd_hours': 2.0,
        'description': 'Promoting equality and respecting diversity'
    },
]

# Optional courses
optional_courses = [
    {
        'name': 'Palliative Care',
        'category': 'CLINICAL',
        'is_mandatory': False,
        'validity_months': 36,
        'sssc_cpd_hours': 6.0,
        'description': 'End of life care and support'
    },
    {
        'name': 'Diabetes Care',
        'category': 'CLINICAL',
        'is_mandatory': False,
        'validity_months': 24,
        'sssc_cpd_hours': 3.0,
        'description': 'Managing diabetes in care settings'
    },
    {
        'name': 'Tissue Viability',
        'category': 'CLINICAL',
        'is_mandatory': False,
        'validity_months': 24,
        'sssc_cpd_hours': 3.0,
        'description': 'Pressure ulcer prevention and wound care'
    },
]

all_courses = mandatory_courses + optional_courses

print(f"Creating {len(all_courses)} training courses...")

for course_data in all_courses:
    course, created = TrainingCourse.objects.get_or_create(
        name=course_data['name'],
        defaults=course_data
    )
    if created:
        print(f"✅ Created: {course.name} ({course.category})")
    else:
        print(f"ℹ️  Already exists: {course.name}")

print(f"\n✅ Total courses in database: {TrainingCourse.objects.count()}")
print(f"   - Mandatory: {TrainingCourse.objects.filter(is_mandatory=True).count()}")
print(f"   - Optional: {TrainingCourse.objects.filter(is_mandatory=False).count()}")
