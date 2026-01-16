"""
Scheduled compliance check command - designed to run daily via cron
Runs all compliance checks and sends notifications for violations
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta
from scheduling.models import ComplianceRule, ComplianceCheck, ComplianceViolation
from scheduling.management.commands.run_compliance_checks import Command as ChecksCommand


class Command(BaseCommand):
    help = 'Run scheduled compliance checks and send notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--notify',
            action='store_true',
            help='Send email notifications for violations',
        )
        parser.add_argument(
            '--period-days',
            type=int,
            default=7,
            help='Number of days to check (default: 7)',
        )

    def handle(self, *args, **options):
        notify = options['notify']
        period_days = options['period_days']
        
        self.stdout.write(self.style.SUCCESS(f'\n🔄 Scheduled Compliance Check'))
        self.stdout.write(f'Time: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f'Period: Last {period_days} days')
        self.stdout.write(f'Notifications: {"Enabled" if notify else "Disabled"}\n')
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        
        # Run the compliance checks
        checks_command = ChecksCommand()
        checks_command.stdout = self.stdout
        checks_command.handle(start_date=start_date.strftime('%Y-%m-%d'), 
                             end_date=end_date.strftime('%Y-%m-%d'))
        
        # Get violations created today
        today_violations = ComplianceViolation.objects.filter(
            detected_at__date=date.today(),
            status='OPEN'
        ).select_related('rule', 'affected_user', 'compliance_check')
        
        if today_violations.exists():
            critical_count = today_violations.filter(severity='CRITICAL').count()
            high_count = today_violations.filter(severity='HIGH').count()
            
            self.stdout.write(self.style.WARNING(f'\n⚠️  New violations detected today:'))
            self.stdout.write(f'   Critical: {critical_count}')
            self.stdout.write(f'   High: {high_count}')
            self.stdout.write(f'   Total: {today_violations.count()}')
            
            if notify:
                self._send_violation_notifications(today_violations)
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✅ No new violations detected'))
        
        self.stdout.write(f'\n✅ Scheduled check completed')

    def _send_violation_notifications(self, violations):
        """Send email notifications for compliance violations"""
        
        # Group violations by severity
        critical = violations.filter(severity='CRITICAL')
        high = violations.filter(severity='HIGH')
        medium = violations.filter(severity='MEDIUM')
        
        if not violations.exists():
            return
        
        # Build email content
        subject = f'🚨 Compliance Violations Detected - {date.today().strftime("%d/%m/%Y")}'
        
        message_lines = [
            'Compliance Check Alert',
            '=' * 60,
            f'Date: {timezone.now().strftime("%d/%m/%Y %H:%M")}',
            f'Total Violations: {violations.count()}',
            '',
        ]
        
        if critical.exists():
            message_lines.extend([
                '🔴 CRITICAL VIOLATIONS (Immediate Action Required):',
                '-' * 60,
            ])
            for v in critical[:10]:  # Limit to first 10
                message_lines.append(f'• {v.rule.name}')
                message_lines.append(f'  {v.description[:100]}...' if len(v.description) > 100 else f'  {v.description}')
                message_lines.append('')
        
        if high.exists():
            message_lines.extend([
                '🟠 HIGH PRIORITY VIOLATIONS:',
                '-' * 60,
            ])
            for v in high[:10]:
                message_lines.append(f'• {v.rule.name}')
                message_lines.append(f'  {v.description[:100]}...' if len(v.description) > 100 else f'  {v.description}')
                message_lines.append('')
        
        if medium.exists():
            message_lines.extend([
                f'🟡 MEDIUM PRIORITY: {medium.count()} violation(s)',
                '',
            ])
        
        message_lines.extend([
            '',
            'View full details in the Compliance Dashboard:',
            f'{settings.SITE_URL}/management/compliance-dashboard/' if hasattr(settings, 'SITE_URL') else 'http://localhost:8000/management/compliance-dashboard/',
            '',
            'This is an automated notification from the Staff Rota System.',
        ])
        
        message = '\n'.join(message_lines)
        
        # Get recipient list
        recipient_list = self._get_notification_recipients()
        
        if recipient_list:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'   ✉️  Notification sent to {len(recipient_list)} recipient(s)'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ✉️  Failed to send notification: {str(e)}'))
        else:
            self.stdout.write(self.style.WARNING(f'   ⚠️  No notification recipients configured'))

    def _get_notification_recipients(self):
        """Get list of email addresses for compliance notifications"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get superusers and staff with specific permission
        recipients = User.objects.filter(
            is_active=True,
            is_superuser=True
        ).values_list('email', flat=True)
        
        return [email for email in recipients if email]
