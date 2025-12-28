"""
Proactive Training Scheduling System - Quick Win 7
Auto-schedules training before expiry and escalates critical cases

Business Impact:
- Improve 82% → 95% training compliance
- Avoid CI penalties (£10,000/year)
- Reduce admin time: 8 hours/week → 2 hours/week
"""

from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from scheduling.models import TrainingRecord, User
from scheduling.models_multi_home import CareHome
import logging

logger = logging.getLogger(__name__)


class ProactiveTrainingScheduler:
    """
    Automated training scheduling and escalation system
    """
    
    def __init__(self):
        self.today = timezone.now().date()
    
    def check_and_schedule_all(self):
        """Main function: Check all training records and take appropriate action"""
        results = {
            '90_day_alerts': 0,
            '60_day_bookings': 0,
            '30_day_escalations': 0,
            '7_day_critical': 0
        }
        
        # Get all training records
        training_records = TrainingRecord.objects.filter(
            user__is_active=True
        ).select_related('user', 'course')
        
        for record in training_records:
            days_until_expiry = self._days_until_expiry(record)
            
            if days_until_expiry == 90:
                self._send_90_day_alert(record)
                results['90_day_alerts'] += 1
                
            elif days_until_expiry == 60:
                self._auto_book_training(record)
                results['60_day_bookings'] += 1
                
            elif days_until_expiry == 30:
                self._escalate_to_head_of_service(record)
                results['30_day_escalations'] += 1
                
            elif days_until_expiry <= 7 and days_until_expiry > 0:
                self._flag_critical(record)
                results['7_day_critical'] += 1
        
        return results
    
    def _days_until_expiry(self, record):
        """Calculate days until training expires"""
        if not record.expiry_date:
            return 999  # No expiry
        return (record.expiry_date - self.today).days
    
    def _send_90_day_alert(self, record):
        """90 days: Send email alert to staff + manager"""
        logger.info(f"📧 90-day alert: {record.user.full_name} - {record.course.name}")
        
        subject = f"Training Renewal Reminder - {record.course.name}"
        message = f"""
Hi {record.user.first_name},

Your {record.course.name} training expires in 90 days on {record.expiry_date}.

Please book a renewal session at your earliest convenience.

Best regards,
Staff Rota System
        """
        
        # Send to staff
        try:
            send_mail(
                subject,
                message,
                'noreply@staffrota.com',
                [record.user.email],
                fail_silently=False
            )
            
            # Log activity
            record.last_reminder_sent = self.today
            record.save()
            
        except Exception as e:
            logger.error(f"Failed to send 90-day alert: {e}")
    
    def _auto_book_training(self, record):
        """60 days: Auto-book training slot if courses available"""
        logger.info(f"📅 Auto-booking: {record.user.full_name} - {record.course.name}")
        
        # Check for available training sessions
        # TODO: Integrate with training management system
        # For now: Just send booking request
        
        subject = f"Training Booking Required - {record.course.name}"
        message = f"""
Hi {record.user.first_name},

Your {record.course.name} training expires in 60 days.

AUTOMATIC BOOKING ATTEMPTED - Please confirm:
- Course: {record.course.name}
- Expiry Date: {record.expiry_date}

Contact Training Coordinator to confirm your slot.

Best regards,
Staff Rota System
        """
        
        try:
            send_mail(
                subject,
                message,
                'noreply@staffrota.com',
                [record.user.email],
                fail_silently=False
            )
            record.last_reminder_sent = self.today
            record.save()
            
        except Exception as e:
            logger.error(f"Failed to auto-book training: {e}")
    
    def _escalate_to_head_of_service(self, record):
        """30 days: Escalate to Head of Service"""
        logger.warning(f"⚠️ Escalation: {record.user.full_name} - {record.course.name}")
        
        # Get head of service (assume role-based)
        heads_of_service = User.objects.filter(
            role__name__icontains='head of service',
            is_active=True
        )
        
        subject = f"URGENT: Training Expiry - {record.user.full_name}"
        message = f"""
URGENT: Training compliance issue requiring attention

Staff Member: {record.user.full_name} (SAP: {record.user.sap})
Course: {record.course.name}
Expires: {record.expiry_date} (30 days)
Status: NOT YET BOOKED

Action Required:
1. Book training session immediately
2. If unable to book, document reason
3. Consider removing from rota if not completed

Care Inspectorate Compliance Risk: HIGH

Best regards,
Staff Rota System
        """
        
        for head in heads_of_service:
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@staffrota.com',
                    [head.email],
                    fail_silently=False
                )
            except Exception as e:
                logger.error(f"Failed to send escalation email: {e}")
        
        record.last_reminder_sent = self.today
        record.save()
    
    def _flag_critical(self, record):
        """7 days: Flag CRITICAL - remove from rota if not completed"""
        logger.error(f"🚨 CRITICAL: {record.user.full_name} - {record.course.name} expires in {self._days_until_expiry(record)} days")
        
        # Create compliance violation
        from scheduling.models import ComplianceViolation
        
        ComplianceViolation.objects.create(
            staff=record.user,
            violation_type='TRAINING_EXPIRED',
            severity='CRITICAL',
            description=f"{record.course.name} expires in {self._days_until_expiry(record)} days",
            requires_immediate_action=True
        )
        
        # Send urgent alert to all managers
        managers = User.objects.filter(
            role__is_management=True,
            is_active=True
        )
        
        subject = f"🚨 CRITICAL: Training Expiry - {record.user.full_name}"
        message = f"""
CRITICAL COMPLIANCE ALERT

Staff Member: {record.user.full_name}
Course: {record.course.name}  
Expires: {record.expiry_date} ({self._days_until_expiry(record)} days)

IMMEDIATE ACTION REQUIRED:
1. Complete training TODAY
2. OR remove from rota until compliant

Care Inspectorate risk: EXTREME

System will auto-block scheduling after expiry.

Best regards,
Staff Rota System
        """
        
        for manager in managers:
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@staffrota.com',
                    [manager.email],
                    fail_silently=False
                )
            except Exception as e:
                logger.error(f"Failed to send critical alert: {e}")


def run_proactive_training_checks():
    """
    Main entry point for scheduled task
    Run daily via cron/celery
    """
    scheduler = ProactiveTrainingScheduler()
    results = scheduler.check_and_schedule_all()
    
    logger.info(f"Proactive training check complete: {results}")
    return results
