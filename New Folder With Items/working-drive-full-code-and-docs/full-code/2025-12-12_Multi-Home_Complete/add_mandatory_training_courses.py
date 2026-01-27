#!/usr/bin/env python3
"""
Add Mandatory Training Courses
As defined by Care Inspectorate and Glasgow City Council for care homes
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import TrainingCourse

# Mandatory training courses as defined by Care Inspectorate and Glasgow City Council
MANDATORY_COURSES = [
    # HEALTH & SAFETY (Care Inspectorate Required)
    {
        'name': 'Manual Handling',
        'category': 'HEALTH_SAFETY',
        'is_mandatory': True,
        'validity_months': 12,
        'frequency': 'ANNUAL',
        'description': 'Training on safe moving and handling techniques for residents'
    },
    {
        'name': 'Health & Safety Awareness',
        'category': 'HEALTH_SAFETY',
        'is_mandatory': True,
        'validity_months': 12,
        'frequency': 'ANNUAL',
        'description': 'Basic health and safety awareness for care home staff'
    },
    {
        'name': 'Fire Safety',
        'category': 'HEALTH_SAFETY',
        'is_mandatory': True,
        'validity_months': 12,
        'frequency': 'ANNUAL',
        'description': 'Fire safety awareness, procedures, and evacuation protocols'
    },
    {
        'name': 'First Aid',
        'category': 'HEALTH_SAFETY',
        'is_mandatory': True,
        'validity_months': 36,  # 3 years
        'frequency': 'TRIENNIAL',
        'description': 'Basic first aid and emergency response training'
    },
    {
        'name': 'Infection Prevention and Control',
        'category': 'HEALTH_SAFETY',
        'is_mandatory': True,
        'validity_months': 12,
        'frequency': 'ANNUAL',
        'description': 'IPC procedures including hand hygiene, PPE, and outbreak management'
    },
    {
        'name': 'Food Hygiene',
        'category': 'HEALTH_SAFETY',
        'is_mandatory': True,
        'validity_months': 36,  # 3 years
        'frequency': 'TRIENNIAL',
        'description': 'Food safety and hygiene in care settings'
    },
    
    # SAFEGUARDING (Care Inspectorate Required)
    {
        'name': 'Adult Support and Protection',
        'category': 'SAFEGUARDING',
        'is_mandatory': True,
        'validity_months': 12,
        'frequency': 'ANNUAL',
        'description': 'Protection of adults at risk, recognizing and reporting abuse'
    },
    {
        'name': 'Safeguarding Adults',
        'category': 'SAFEGUARDING',
        'is_mandatory': True,
        'validity_months': 12,
        'frequency': 'ANNUAL',
        'description': 'Comprehensive safeguarding awareness and procedures'
    },
    
    # CLINICAL & CARE (Care Inspectorate Required)
    {
        'name': 'Medication Management',
        'category': 'CLINICAL',
        'is_mandatory': True,
        'validity_months': 12,
        'frequency': 'ANNUAL',
        'description': 'Safe administration, storage, and recording of medications'
    },
    {
        'name': 'Dementia Awareness',
        'category': 'CLINICAL',
        'is_mandatory': True,
        'validity_months': 24,  # 2 years
        'frequency': 'BIENNIAL',
        'description': 'Understanding dementia and person-centered care approaches'
    },
    {
        'name': 'Mental Health Awareness',
        'category': 'CLINICAL',
        'is_mandatory': True,
        'validity_months': 24,  # 2 years
        'frequency': 'BIENNIAL',
        'description': 'Understanding mental health conditions in older adults'
    },
    {
        'name': 'Pressure Area Care',
        'category': 'CLINICAL',
        'is_mandatory': True,
        'validity_months': 12,
        'frequency': 'ANNUAL',
        'description': 'Prevention and management of pressure ulcers'
    },
    {
        'name': 'Nutrition and Hydration',
        'category': 'CLINICAL',
        'is_mandatory': True,
        'validity_months': 24,  # 2 years
        'frequency': 'BIENNIAL',
        'description': 'Meeting nutritional needs and monitoring hydration'
    },
    {
        'name': 'End of Life Care',
        'category': 'CLINICAL',
        'is_mandatory': True,
        'validity_months': 24,  # 2 years
        'frequency': 'BIENNIAL',
        'description': 'Palliative care approaches and supporting dignity in dying'
    },
    
    # EQUALITY & DIGNITY (Care Inspectorate Required)
    {
        'name': 'Equality and Diversity',
        'category': 'PROFESSIONAL',
        'is_mandatory': True,
        'validity_months': 24,  # 2 years
        'frequency': 'BIENNIAL',
        'description': 'Promoting equality, valuing diversity, and preventing discrimination'
    },
    {
        'name': 'Dignity and Respect',
        'category': 'PROFESSIONAL',
        'is_mandatory': True,
        'validity_months': 12,
        'frequency': 'ANNUAL',
        'description': 'Maintaining dignity and respect in all care interactions'
    },
    {
        'name': 'Human Rights in Care',
        'category': 'PROFESSIONAL',
        'is_mandatory': True,
        'validity_months': 24,  # 2 years
        'frequency': 'BIENNIAL',
        'description': 'Understanding and upholding human rights in care settings'
    },
    
    # DATA PROTECTION & GOVERNANCE (Care Inspectorate Required)
    {
        'name': 'Data Protection and Confidentiality',
        'category': 'COMPLIANCE',
        'is_mandatory': True,
        'validity_months': 12,
        'frequency': 'ANNUAL',
        'description': 'GDPR compliance, confidentiality, and information governance'
    },
    {
        'name': 'Record Keeping',
        'category': 'COMPLIANCE',
        'is_mandatory': True,
        'validity_months': 24,  # 2 years
        'frequency': 'BIENNIAL',
        'description': 'Accurate, timely, and compliant record keeping practices'
    },
    {
        'name': 'Whistleblowing',
        'category': 'COMPLIANCE',
        'is_mandatory': True,
        'validity_months': 24,  # 2 years
        'frequency': 'BIENNIAL',
        'description': 'Understanding whistleblowing procedures and protections'
    },
    
    # PROFESSIONAL DEVELOPMENT (Care Inspectorate & SSSC Required)
    {
        'name': 'Induction Training',
        'category': 'INDUCTION',
        'is_mandatory': True,
        'validity_months': 0,  # One-time only
        'frequency': 'ONE_TIME',
        'description': 'Comprehensive induction for new staff members'
    },
    {
        'name': 'Care Certificate (or SVQ equivalent)',
        'category': 'INDUCTION',
        'is_mandatory': True,
        'validity_months': 0,  # One-time qualification
        'frequency': 'ONE_TIME',
        'description': 'Foundation training for care staff (SSSC requirement)'
    },
]

def add_training_courses():
    """Add all mandatory training courses to the database"""
    print("=" * 60)
    print("ADDING MANDATORY TRAINING COURSES")
    print("Care Inspectorate & Glasgow City Council Requirements")
    print("=" * 60)
    
    added_count = 0
    updated_count = 0
    
    for course_data in MANDATORY_COURSES:
        course, created = TrainingCourse.objects.get_or_create(
            name=course_data['name'],
            defaults={
                'category': course_data['category'],
                'is_mandatory': course_data['is_mandatory'],
                'validity_months': course_data['validity_months'],
                'frequency': course_data['frequency'],
                'description': course_data['description'],
                'requires_competency_assessment': False,
                'requires_certificate': True,
                'sssc_cpd_eligible': True,
                'sssc_cpd_hours': 0
            }
        )
        
        if created:
            added_count += 1
            print(f"✓ ADDED: {course.name} ({course.category})")
        else:
            # Update existing course
            course.category = course_data['category']
            course.is_mandatory = course_data['is_mandatory']
            course.validity_months = course_data['validity_months']
            course.frequency = course_data['frequency']
            course.description = course_data['description']
            course.save()
            updated_count += 1
            print(f"✓ UPDATED: {course.name} ({course.category})")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  - Courses Added: {added_count}")
    print(f"  - Courses Updated: {updated_count}")
    print(f"  - Total Mandatory Courses: {TrainingCourse.objects.filter(is_mandatory=True).count()}")
    print("=" * 60)
    
    # Show breakdown by category
    print("\nBREAKDOWN BY CATEGORY:")
    from django.db.models import Count
    categories = TrainingCourse.objects.filter(is_mandatory=True).values('category').annotate(count=Count('id')).order_by('category')
    for cat in categories:
        print(f"  - {cat['category']}: {cat['count']} courses")
    
    print("\n✓ All mandatory training courses successfully added!")

if __name__ == '__main__':
    add_training_courses()
