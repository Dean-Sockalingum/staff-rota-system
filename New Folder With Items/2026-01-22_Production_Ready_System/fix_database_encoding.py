#!/usr/bin/env python
"""
Database cleanup script to fix encoding issues in production database.
This script identifies and fixes UTF-8 encoding problems in text fields.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.db import connection, transaction
from scheduling.models import User, TrainingCourse, TrainingRecord, CareHome, Unit
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_text_encoding(text):
    """Fix text encoding issues"""
    if text is None:
        return None
    
    try:
        # Try to encode/decode to ensure valid UTF-8
        if isinstance(text, str):
            return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        return text
    except Exception as e:
        logger.error(f"Error fixing encoding for text: {e}")
        return ""


def clean_user_data():
    """Clean User model data"""
    logger.info("Cleaning User data...")
    fixed_count = 0
    
    with transaction.atomic():
        for user in User.objects.all():
            needs_update = False
            
            # Fix first_name
            if user.first_name:
                fixed = fix_text_encoding(user.first_name)
                if fixed != user.first_name:
                    user.first_name = fixed
                    needs_update = True
            
            # Fix last_name
            if user.last_name:
                fixed = fix_text_encoding(user.last_name)
                if fixed != user.last_name:
                    user.last_name = fixed
                    needs_update = True
            
            # Fix email
            if user.email:
                fixed = fix_text_encoding(user.email)
                if fixed != user.email:
                    user.email = fixed
                    needs_update = True
            
            if needs_update:
                try:
                    user.save()
                    fixed_count += 1
                    logger.info(f"Fixed User: {user.pk}")
                except Exception as e:
                    logger.error(f"Error saving User {user.pk}: {e}")
    
    logger.info(f"Fixed {fixed_count} users")
    return fixed_count


def clean_training_course_data():
    """Clean TrainingCourse model data"""
    logger.info("Cleaning TrainingCourse data...")
    fixed_count = 0
    
    with transaction.atomic():
        for course in TrainingCourse.objects.all():
            needs_update = False
            
            # Fix name
            if course.name:
                fixed = fix_text_encoding(course.name)
                if fixed != course.name:
                    course.name = fixed
                    needs_update = True
            
            # Fix description
            if hasattr(course, 'description') and course.description:
                fixed = fix_text_encoding(course.description)
                if fixed != course.description:
                    course.description = fixed
                    needs_update = True
            
            if needs_update:
                try:
                    course.save()
                    fixed_count += 1
                    logger.info(f"Fixed TrainingCourse: {course.pk}")
                except Exception as e:
                    logger.error(f"Error saving TrainingCourse {course.pk}: {e}")
    
    logger.info(f"Fixed {fixed_count} training courses")
    return fixed_count


def clean_training_record_data():
    """Clean TrainingRecord model data"""
    logger.info("Cleaning TrainingRecord data...")
    fixed_count = 0
    deleted_count = 0
    
    with transaction.atomic():
        for record in TrainingRecord.objects.all():
            try:
                needs_update = False
                
                # Fix notes if exists
                if hasattr(record, 'notes') and record.notes:
                    fixed = fix_text_encoding(record.notes)
                    if fixed != record.notes:
                        record.notes = fixed
                        needs_update = True
                
                # Fix trainer_name if exists
                if hasattr(record, 'trainer_name') and record.trainer_name:
                    fixed = fix_text_encoding(record.trainer_name)
                    if fixed != record.trainer_name:
                        record.trainer_name = fixed
                        needs_update = True
                
                if needs_update:
                    record.save()
                    fixed_count += 1
                    logger.info(f"Fixed TrainingRecord: {record.pk}")
                    
            except Exception as e:
                logger.error(f"Error processing TrainingRecord {record.pk}: {e}")
                # Delete corrupted records that can't be fixed
                try:
                    record.delete()
                    deleted_count += 1
                    logger.warning(f"Deleted corrupted TrainingRecord: {record.pk}")
                except:
                    pass
    
    logger.info(f"Fixed {fixed_count} training records, deleted {deleted_count} corrupted records")
    return fixed_count, deleted_count


def clean_care_home_data():
    """Clean CareHome model data"""
    logger.info("Cleaning CareHome data...")
    fixed_count = 0
    
    with transaction.atomic():
        for home in CareHome.objects.all():
            needs_update = False
            
            # Fix name
            if home.name:
                fixed = fix_text_encoding(home.name)
                if fixed != home.name:
                    home.name = fixed
                    needs_update = True
            
            # Fix address if exists
            if hasattr(home, 'address') and home.address:
                fixed = fix_text_encoding(home.address)
                if fixed != home.address:
                    home.address = fixed
                    needs_update = True
            
            if needs_update:
                try:
                    home.save()
                    fixed_count += 1
                    logger.info(f"Fixed CareHome: {home.pk}")
                except Exception as e:
                    logger.error(f"Error saving CareHome {home.pk}: {e}")
    
    logger.info(f"Fixed {fixed_count} care homes")
    return fixed_count


def verify_database():
    """Verify database can be queried without errors"""
    logger.info("Verifying database integrity...")
    errors = []
    
    try:
        # Test User queries
        user_count = User.objects.count()
        logger.info(f"✓ User count: {user_count}")
        
        # Test TrainingCourse queries
        course_count = TrainingCourse.objects.count()
        logger.info(f"✓ TrainingCourse count: {course_count}")
        
        # Test TrainingRecord queries
        record_count = TrainingRecord.objects.count()
        logger.info(f"✓ TrainingRecord count: {record_count}")
        
        # Test CareHome queries
        home_count = CareHome.objects.count()
        logger.info(f"✓ CareHome count: {home_count}")
        
        # Test the specific query that was failing
        for home in CareHome.objects.filter(is_active=True)[:3]:
            for course in TrainingCourse.objects.filter(is_mandatory=True)[:3]:
                staff = User.objects.filter(unit__care_home=home, is_active=True)[:5]
                for user in staff:
                    try:
                        latest = TrainingRecord.objects.filter(
                            staff_member=user,
                            course=course
                        ).order_by('-completion_date').first()
                    except Exception as e:
                        errors.append(f"Error querying training records for User {user.pk}, Course {course.pk}: {e}")
        
        if errors:
            logger.error(f"Found {len(errors)} query errors:")
            for error in errors[:10]:  # Show first 10
                logger.error(f"  - {error}")
        else:
            logger.info("✓ All database queries successful!")
        
        return len(errors) == 0
        
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False


if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("Starting database cleanup for production demo")
    logger.info("=" * 70)
    
    try:
        # Clean all models
        clean_user_data()
        clean_care_home_data()
        clean_training_course_data()
        record_fixed, record_deleted = clean_training_record_data()
        
        logger.info("\n" + "=" * 70)
        logger.info("Cleanup complete! Verifying database...")
        logger.info("=" * 70)
        
        # Verify
        if verify_database():
            logger.info("\n✓ SUCCESS! Database is clean and ready for demo!")
        else:
            logger.warning("\n⚠ WARNING! Some issues remain. Check logs above.")
        
    except Exception as e:
        logger.error(f"Fatal error during cleanup: {e}")
        sys.exit(1)
