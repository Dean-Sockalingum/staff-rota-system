#!/usr/bin/env python
"""
Populate realistic training data for executive board demo.
Creates training records showing current, expiring, expired, and missing training.
"""
import os
import sys
import django
from datetime import datetime, timedelta
from random import randint, choice, random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import transaction
from scheduling.models import User, TrainingCourse, TrainingRecord
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_training_records():
    """Create realistic training records for demo"""
    
    logger.info("Fetching users and courses...")
    active_users = list(User.objects.filter(is_active=True))
    courses = list(TrainingCourse.objects.all())
    mandatory_courses = [c for c in courses if c.is_mandatory]
    
    logger.info(f"Found {len(active_users)} active users")
    logger.info(f"Found {len(courses)} total courses ({len(mandatory_courses)} mandatory)")
    
    if not active_users or not courses:
        logger.error("No users or courses found!")
        return
    
    today = datetime.now().date()
    records_created = 0
    
    # Statistics for demo purposes
    stats = {
        'current': 0,
        'expiring': 0,
        'expired': 0,
        'missing': 0
    }
    
    logger.info("Creating training records...")
    
    with transaction.atomic():
        # Clear existing training records
        TrainingRecord.objects.all().delete()
        logger.info("Cleared existing training records")
        
        for user in active_users:
            # Each user should have some training records
            # Mandatory courses: 80% coverage
            # Optional courses: 40% coverage
            
            for course in mandatory_courses:
                # 80% of users have mandatory training
                if random() < 0.80:
                    # Determine status
                    status_roll = random()
                    
                    if status_roll < 0.60:
                        # 60% current (within validity period)
                        days_ago = randint(30, 300)
                        completion_date = today - timedelta(days=days_ago)
                        status = 'current'
                        stats['current'] += 1
                        
                    elif status_roll < 0.75:
                        # 15% expiring soon (within 30 days of expiry)
                        days_ago = randint(305, 335)
                        completion_date = today - timedelta(days=days_ago)
                        status = 'expiring'
                        stats['expiring'] += 1
                        
                    else:
                        # 5% expired
                        days_ago = randint(370, 700)
                        completion_date = today - timedelta(days=days_ago)
                        status = 'expired'
                        stats['expired'] += 1
                    
                    # Create the record
                    TrainingRecord.objects.create(
                        staff_member=user,
                        course=course,
                        completion_date=completion_date,
                        expiry_date=completion_date + timedelta(days=365),
                        trainer_name=choice([
                            'NHS Education Scotland',
                            'Care Inspectorate',
                            'Internal Training Team',
                            'External Provider',
                            'Online Platform'
                        ])
                    )
                    records_created += 1
                else:
                    # 20% missing mandatory training
                    stats['missing'] += 1
            
            # Optional courses - 40% coverage with varied status
            optional_courses = [c for c in courses if not c.is_mandatory]
            for course in optional_courses:
                if random() < 0.40:
                    # Similar distribution but more current (as they're optional)
                    status_roll = random()
                    
                    if status_roll < 0.75:
                        days_ago = randint(30, 250)
                        completion_date = today - timedelta(days=days_ago)
                        status = 'current'
                        stats['current'] += 1
                    elif status_roll < 0.90:
                        days_ago = randint(310, 340)
                        completion_date = today - timedelta(days=days_ago)
                        status = 'expiring'
                        stats['expiring'] += 1
                    else:
                        days_ago = randint(370, 600)
                        completion_date = today - timedelta(days=days_ago)
                        status = 'expired'
                        stats['expired'] += 1
                    
                    TrainingRecord.objects.create(
                        staff_member=user,
                        course=course,
                        completion_date=completion_date,
                        expiry_date=completion_date + timedelta(days=365),
                        trainer_name=choice([
                            'NHS Education Scotland',
                            'Care Inspectorate',
                            'Internal Training Team',
                            'External Provider'
                        ])
                    )
                    records_created += 1
            
            # Log progress every 500 users
            if (active_users.index(user) + 1) % 500 == 0:
                logger.info(f"Processed {active_users.index(user) + 1}/{len(active_users)} users...")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Training records created: {records_created}")
    logger.info(f"\nDistribution:")
    logger.info(f"  Current (valid):      {stats['current']:,}")
    logger.info(f"  Expiring soon:        {stats['expiring']:,}")
    logger.info(f"  Expired:              {stats['expired']:,}")
    logger.info(f"  Missing training:     {stats['missing']:,}")
    logger.info(f"{'='*70}\n")
    
    # Calculate compliance rate
    total_required = stats['current'] + stats['expiring'] + stats['expired'] + stats['missing']
    compliant = stats['current']
    compliance_rate = (compliant / total_required * 100) if total_required > 0 else 0
    
    logger.info(f"Overall Compliance Rate: {compliance_rate:.1f}%")
    logger.info(f"(Current certifications / Total required)")
    
    return records_created


def verify_data():
    """Verify the training data was created correctly"""
    logger.info("\nVerifying training data...")
    
    total_records = TrainingRecord.objects.count()
    logger.info(f"✓ Total training records: {total_records:,}")
    
    # Check mandatory vs optional
    mandatory_courses = TrainingCourse.objects.filter(is_mandatory=True)
    for course in mandatory_courses[:3]:
        count = TrainingRecord.objects.filter(course=course).count()
        logger.info(f"✓ {course.name}: {count:,} records")
    
    logger.info("\n✓ Data verification complete!")


if __name__ == '__main__':
    logger.info("="*70)
    logger.info("Populating Training Data for Executive Board Demo")
    logger.info("="*70)
    
    try:
        records_count = create_training_records()
        verify_data()
        
        logger.info("\n" + "="*70)
        logger.info("✓ SUCCESS! Demo data populated and ready for presentation!")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"\n✗ Error populating data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
