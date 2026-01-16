"""
Management command to send automated care plan review email alerts

This command sends:
- 7-day warning emails for reviews due soon
- Due date reminders for reviews due today/tomorrow  
- Overdue escalation emails for reviews past due date

Schedule with cron:
0 9 * * * cd /path/to/rotasystems && python manage.py send_careplan_alerts

Or run manually:
python manage.py send_careplan_alerts
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from scheduling.models import CarePlanReview, User
from scheduling.models import ActivityLog


class Command(BaseCommand):
    help = 'Send automated email alerts for care plan reviews'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what emails would be sent without actually sending them'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No emails will be sent'))
        
        # Get email settings
        from_email = settings.DEFAULT_FROM_EMAIL
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        
        # Counters
        sent_count = 0
        error_count = 0
        
        # 1. SEVEN-DAY WARNING EMAILS
        seven_days_from_now = today + timedelta(days=7)
        due_soon_reviews = CarePlanReview.objects.filter(
            due_date=seven_days_from_now,
            status__in=['UPCOMING', 'DUE']
        ).select_related('resident', 'resident__unit', 'keyworker')
        
        self.stdout.write(f'\nFound {due_soon_reviews.count()} reviews due in 7 days')
        
        for review in due_soon_reviews:
            if not review.keyworker or not review.keyworker.email:
                self.stdout.write(self.style.WARNING(
                    f'  Skipping {review.resident.resident_id}: No keyworker email'
                ))
                continue
            
            subject = f'Care Plan Review Due in 7 Days - {review.resident.full_name}'
            message = self._generate_due_soon_email(review, site_url)
            recipient = [review.keyworker.email]
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS(
                    f'  Would send to {review.keyworker.email}: {subject}'
                ))
            else:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=recipient,
                        fail_silently=False
                    )
                    sent_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Sent to {review.keyworker.email}'
                    ))
                    
                    # Log the notification
                    ActivityLog.objects.create(
                        user=review.keyworker,
                        action='CAREPLAN_ALERT_SENT',
                        description=f'7-day warning sent for {review.resident.full_name}'
                    )
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(
                        f'  ✗ Failed to send to {review.keyworker.email}: {str(e)}'
                    ))
        
        # 2. DUE TODAY/TOMORROW REMINDERS
        tomorrow = today + timedelta(days=1)
        due_imminent_reviews = CarePlanReview.objects.filter(
            due_date__in=[today, tomorrow],
            status__in=['UPCOMING', 'DUE', 'IN_PROGRESS']
        ).select_related('resident', 'resident__unit', 'keyworker')
        
        self.stdout.write(f'\nFound {due_imminent_reviews.count()} reviews due today/tomorrow')
        
        for review in due_imminent_reviews:
            if not review.keyworker or not review.keyworker.email:
                continue
            
            days_until_due = (review.due_date - today).days
            urgency = 'TODAY' if days_until_due == 0 else 'TOMORROW'
            
            subject = f'URGENT: Care Plan Review Due {urgency} - {review.resident.full_name}'
            message = self._generate_urgent_email(review, site_url, urgency)
            recipient = [review.keyworker.email]
            
            # Also CC unit manager
            if review.unit_manager and review.unit_manager.email:
                recipient.append(review.unit_manager.email)
            
            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f'  Would send to {", ".join(recipient)}: {subject}'
                ))
            else:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=recipient,
                        fail_silently=False
                    )
                    sent_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Sent urgent reminder to {review.keyworker.email}'
                    ))
                    
                    ActivityLog.objects.create(
                        user=review.keyworker,
                        action='CAREPLAN_ALERT_SENT',
                        description=f'Urgent reminder sent for {review.resident.full_name} (due {urgency})'
                    )
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
        
        # 3. OVERDUE ESCALATION EMAILS
        overdue_reviews = CarePlanReview.objects.filter(
            status='OVERDUE',
            due_date__lt=today
        ).select_related('resident', 'resident__unit', 'keyworker', 'unit_manager')
        
        self.stdout.write(f'\nFound {overdue_reviews.count()} overdue reviews')
        
        # Get management team emails
        management_emails = list(
            User.objects.filter(
                is_active=True,
                role__is_management=True,
                email__isnull=False
            ).exclude(email='').values_list('email', flat=True)
        )
        
        # Group overdue reviews by unit for summary email
        overdue_by_unit = {}
        for review in overdue_reviews:
            unit_name = review.resident.unit.get_name_display()
            if unit_name not in overdue_by_unit:
                overdue_by_unit[unit_name] = []
            
            days_overdue = (today - review.due_date).days
            overdue_by_unit[unit_name].append({
                'review': review,
                'days_overdue': days_overdue
            })
            
            # Send individual email to keyworker
            if review.keyworker and review.keyworker.email:
                subject = f'OVERDUE: Care Plan Review - {review.resident.full_name} ({days_overdue} days late)'
                message = self._generate_overdue_email(review, site_url, days_overdue)
                
                if dry_run:
                    self.stdout.write(self.style.ERROR(
                        f'  Would send overdue notice to {review.keyworker.email}'
                    ))
                else:
                    try:
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=from_email,
                            recipient_list=[review.keyworker.email],
                            fail_silently=False
                        )
                        sent_count += 1
                        
                        ActivityLog.objects.create(
                            user=review.keyworker,
                            action='CAREPLAN_ALERT_SENT',
                            description=f'Overdue notice sent for {review.resident.full_name} ({days_overdue} days late)'
                        )
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
        
        # Send summary email to management
        if overdue_by_unit and management_emails:
            subject = f'Care Plan Review Overdue Summary - {today}'
            message = self._generate_management_summary(overdue_by_unit, site_url, today)
            
            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f'\nWould send management summary to {len(management_emails)} managers'
                ))
            else:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=management_emails,
                        fail_silently=False
                    )
                    sent_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'\n✓ Sent management summary to {len(management_emails)} managers'
                    ))
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'\n✗ Failed to send management summary: {str(e)}'))
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'\nEmail Alert Summary:'))
        self.stdout.write(f'  Emails sent: {sent_count}')
        self.stdout.write(f'  Errors: {error_count}')
        if dry_run:
            self.stdout.write(self.style.WARNING('  (DRY RUN - no emails actually sent)'))
        self.stdout.write('='*60 + '\n')
    
    def _generate_due_soon_email(self, review, site_url):
        """Generate email body for 7-day warning"""
        return f"""
Dear {review.keyworker.first_name},

This is a reminder that a care plan review is due in 7 days:

Resident: {review.resident.full_name} ({review.resident.resident_id})
Unit: {review.resident.unit.get_name_display()}
Due Date: {review.due_date}
Review Type: {review.get_review_type_display()}

Please ensure this review is completed on time to maintain compliance with Care Inspectorate requirements.

To complete this review, visit:
{site_url}/careplan/review/{review.id}/

If you need assistance or have any questions, please contact your unit manager.

Best regards,
Care Plan Management System
"""
    
    def _generate_urgent_email(self, review, site_url, urgency):
        """Generate email body for urgent (today/tomorrow) reminder"""
        return f"""
URGENT REMINDER

Dear {review.keyworker.first_name},

A care plan review is due {urgency}:

Resident: {review.resident.full_name} ({review.resident.resident_id})
Unit: {review.resident.unit.get_name_display()}
Due Date: {review.due_date}
Review Type: {review.get_review_type_display()}
Current Status: {review.get_status_display()}

IMMEDIATE ACTION REQUIRED

Please complete this review as soon as possible to maintain compliance.

Complete review here:
{site_url}/careplan/review/{review.id}/

If you cannot complete this review, please inform your unit manager immediately.

Best regards,
Care Plan Management System
"""
    
    def _generate_overdue_email(self, review, site_url, days_overdue):
        """Generate email body for overdue notice"""
        return f"""
OVERDUE CARE PLAN REVIEW - IMMEDIATE ACTION REQUIRED

Dear {review.keyworker.first_name},

This care plan review is now {days_overdue} day(s) OVERDUE:

Resident: {review.resident.full_name} ({review.resident.resident_id})
Unit: {review.resident.unit.get_name_display()}
Due Date: {review.due_date}
Days Overdue: {days_overdue}
Review Type: {review.get_review_type_display()}

This overdue review is a compliance violation and must be completed immediately.

Management has been notified of this overdue review.

Complete review NOW:
{site_url}/careplan/review/{review.id}/

Contact your unit manager immediately if there are any issues preventing completion.

Best regards,
Care Plan Management System
"""
    
    def _generate_management_summary(self, overdue_by_unit, site_url, today):
        """Generate management summary email for overdue reviews"""
        total_overdue = sum(len(reviews) for reviews in overdue_by_unit.values())
        
        message = f"""
CARE PLAN REVIEW - OVERDUE SUMMARY
Date: {today}
Total Overdue Reviews: {total_overdue}

OVERDUE BY UNIT:

"""
        for unit_name, reviews in sorted(overdue_by_unit.items()):
            message += f"\n{unit_name}: {len(reviews)} overdue\n"
            message += "-" * 50 + "\n"
            
            for item in sorted(reviews, key=lambda x: x['days_overdue'], reverse=True):
                review = item['review']
                days = item['days_overdue']
                message += f"  • {review.resident.full_name} ({review.resident.resident_id})\n"
                message += f"    Due: {review.due_date} ({days} days overdue)\n"
                message += f"    Keyworker: {review.keyworker.full_name if review.keyworker else 'Unassigned'}\n"
                message += f"    Status: {review.get_status_display()}\n\n"
        
        message += f"\n\nView full manager dashboard:\n{site_url}/careplan/manager-dashboard/\n"
        message += "\nPlease follow up with keyworkers to ensure these reviews are completed promptly.\n"
        message += "\nBest regards,\nCare Plan Management System"
        
        return message
