"""
Management command to send annual leave reminder emails to staff members.

This command sends personalized emails to staff members reminding them of their
remaining annual leave entitlement and encouraging them to book their leave.

Usage:
    python manage.py send_leave_reminders
    python manage.py send_leave_reminders --dry-run  # Preview without sending
    python manage.py send_leave_reminders --min-days 10  # Only staff with 10+ days remaining
    python manage.py send_leave_reminders --specific-staff SAP001 SAP002  # Specific staff only
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from staff_records.models import AnnualLeaveEntitlement
from scheduling.models import User
from datetime import date
from decimal import Decimal


class Command(BaseCommand):
    help = 'Send annual leave reminder emails to staff members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview emails without actually sending them',
        )
        parser.add_argument(
            '--min-days',
            type=float,
            default=0,
            help='Only send to staff with at least this many days remaining (default: 0)',
        )
        parser.add_argument(
            '--min-hours',
            type=float,
            default=0,
            help='Only send to staff with at least this many hours remaining (default: 0)',
        )
        parser.add_argument(
            '--specific-staff',
            nargs='+',
            help='Send only to specific staff members by SAP ID',
        )
        parser.add_argument(
            '--year',
            type=int,
            default=date.today().year,
            help='Leave year to check (default: current year)',
        )
        parser.add_argument(
            '--exclude-management',
            action='store_true',
            help='Exclude management staff from reminders',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        min_days = options['min_days']
        min_hours = options['min_hours']
        specific_staff = options['specific_staff']
        year = options['year']
        exclude_management = options['exclude_management']

        self.stdout.write(self.style.SUCCESS(f'\n{"="*70}'))
        self.stdout.write(self.style.SUCCESS(f'Annual Leave Reminder Email System'))
        self.stdout.write(self.style.SUCCESS(f'{"="*70}\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No emails will be sent\n'))

        # Get entitlements for the specified year
        entitlements = AnnualLeaveEntitlement.objects.filter(
            leave_year_start__year=year
        ).select_related('profile__user__role')

        # Filter by specific staff if provided
        if specific_staff:
            entitlements = entitlements.filter(profile__user__sap__in=specific_staff)
            self.stdout.write(f'Filtering to specific staff: {", ".join(specific_staff)}\n')

        # Convert to list early to allow property-based filtering
        entitlements = list(entitlements)
        total_count = len(entitlements)

        # Filter by minimum days/hours
        if min_days > 0:
            entitlements = [e for e in entitlements if e.days_remaining >= Decimal(str(min_days))]
            self.stdout.write(f'Filtering to staff with at least {min_days} days remaining\n')
            total_count = len(entitlements)
        elif min_hours > 0:
            entitlements = [e for e in entitlements if e.hours_remaining >= Decimal(str(min_hours))]
            self.stdout.write(f'Filtering to staff with at least {min_hours} hours remaining\n')
            total_count = len(entitlements)

        # Exclude management if requested
        if exclude_management:
            entitlements = [e for e in entitlements if not (e.profile.user.role and e.profile.user.role.is_management)]
            self.stdout.write('Excluding management staff\n')
            total_count = len(entitlements)

        if total_count == 0:
            self.stdout.write(self.style.WARNING('No staff members match the criteria. No emails to send.\n'))
            return

        self.stdout.write(f'Found {total_count} staff member(s) eligible for reminders\n')
        self.stdout.write(f'{"─"*70}\n')

        # Track results
        emails_sent = 0
        emails_failed = 0
        emails_skipped = 0

        # Send emails
        for entitlement in entitlements:
            user = entitlement.profile.user
            
            # Skip if no email address
            if not user.email or user.email == '':
                self.stdout.write(
                    self.style.WARNING(f'⚠️  {user.sap} - {user.full_name}: No email address - SKIPPED')
                )
                emails_skipped += 1
                continue

            # Skip if inactive
            if not user.is_active:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  {user.sap} - {user.full_name}: Inactive user - SKIPPED')
                )
                emails_skipped += 1
                continue

            # Calculate leave details
            remaining_days = float(entitlement.days_remaining)
            remaining_hours = float(entitlement.hours_remaining)
            total_days = float(entitlement.days_entitlement)
            used_days = float(entitlement.days_used)
            usage_percentage = (used_days / total_days * 100) if total_days > 0 else 0
            carryover_hours = float(entitlement.carryover_hours)
            
            # Determine urgency level
            if remaining_days < 5:
                urgency = 'HIGH'
                urgency_color = '#dc3545'  # Red
                urgency_message = 'You have very few days remaining! Please book your leave soon.'
            elif remaining_days < 10:
                urgency = 'MEDIUM'
                urgency_color = '#ffc107'  # Amber
                urgency_message = 'Please consider booking your remaining leave in the coming weeks.'
            else:
                urgency = 'LOW'
                urgency_color = '#28a745'  # Green
                urgency_message = 'You have plenty of time to plan and book your leave.'

            # Prepare email context
            context = {
                'user': user,
                'remaining_days': remaining_days,
                'remaining_hours': remaining_hours,
                'total_days': total_days,
                'used_days': used_days,
                'usage_percentage': round(usage_percentage, 1),
                'carryover_hours': carryover_hours,
                'leave_year_start': entitlement.leave_year_start,
                'leave_year_end': entitlement.leave_year_end,
                'urgency': urgency,
                'urgency_color': urgency_color,
                'urgency_message': urgency_message,
                'current_date': date.today(),
            }

            # Prepare email
            subject = f'Annual Leave Reminder - {remaining_days:.1f} days remaining'
            
            # Create plain text message
            message = f"""
Dear {user.first_name},

This is a friendly reminder about your annual leave entitlement for {year}.

LEAVE SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Entitlement:    {total_days:.1f} days ({entitlement.total_entitlement_hours:.1f} hours)
• Leave Used:           {used_days:.1f} days ({entitlement.hours_used:.1f} hours)
• Leave Remaining:      {remaining_days:.1f} days ({remaining_hours:.1f} hours)
• Usage:                {usage_percentage:.1f}%
• Carryover from last year: {carryover_hours:.1f} hours
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Leave Year Period: {entitlement.leave_year_start.strftime('%d %B %Y')} to {entitlement.leave_year_end.strftime('%d %B %Y')}

{urgency_message}

All annual leave must be used by {entitlement.leave_year_end.strftime('%d %B %Y')}.
Any unused leave may be lost if not taken before this deadline.

HOW TO REQUEST LEAVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Log into the Staff Rota System
2. Navigate to "My Leave" or "Request Leave"
3. Select your desired dates
4. Submit your request for approval

Your line manager will review and approve your request. We recommend:
• Planning your leave in advance
• Coordinating with your team
• Checking minimum staffing requirements

If you have any questions about your leave entitlement or need assistance
with the booking system, please contact your line manager or HR.

Best regards,
Staff Rota System

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated message. Please do not reply to this email.
For support, contact your line manager or HR department.
            """

            # Create HTML version (optional - more visually appealing)
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .stats-box {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
        .stat-label {{ font-weight: bold; color: #555; }}
        .stat-value {{ color: #667eea; font-weight: bold; }}
        .urgency-box {{ background: {urgency_color}; color: white; padding: 15px; margin: 20px 0; border-radius: 8px; text-align: center; font-weight: bold; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
        .highlight {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 Annual Leave Reminder</h1>
            <p>Year {year}</p>
        </div>
        <div class="content">
            <p>Dear {user.first_name},</p>
            
            <p>This is a friendly reminder about your annual leave entitlement for {year}.</p>
            
            <div class="stats-box">
                <h3>📊 Your Leave Summary</h3>
                <div class="stat-row">
                    <span class="stat-label">Total Entitlement:</span>
                    <span class="stat-value">{total_days:.1f} days ({entitlement.total_entitlement_hours:.1f} hrs)</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Leave Used:</span>
                    <span class="stat-value">{used_days:.1f} days ({entitlement.hours_used:.1f} hrs)</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Leave Remaining:</span>
                    <span class="stat-value" style="font-size: 1.2em;">{remaining_days:.1f} days ({remaining_hours:.1f} hrs)</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Usage:</span>
                    <span class="stat-value">{usage_percentage:.1f}%</span>
                </div>
                {f'<div class="stat-row"><span class="stat-label">Carryover:</span><span class="stat-value">{carryover_hours:.1f} hrs</span></div>' if carryover_hours > 0 else ''}
            </div>
            
            <div class="urgency-box">
                ⚠️ {urgency_message}
            </div>
            
            <div class="highlight">
                <strong>⏰ Important:</strong> All annual leave must be used by 
                <strong>{entitlement.leave_year_end.strftime('%d %B %Y')}</strong>. 
                Any unused leave may be lost if not taken before this deadline.
            </div>
            
            <h3>🔑 How to Request Leave</h3>
            <ol>
                <li>Log into the Staff Rota System</li>
                <li>Navigate to "My Leave" or "Request Leave"</li>
                <li>Select your desired dates</li>
                <li>Submit your request for approval</li>
            </ol>
            
            <div style="text-align: center;">
                <a href="http://localhost:8000/leave-request/" class="button">Request Leave Now</a>
            </div>
            
            <p><strong>💡 Tips:</strong></p>
            <ul>
                <li>Plan your leave in advance</li>
                <li>Coordinate with your team members</li>
                <li>Check minimum staffing requirements</li>
                <li>Consider spreading your leave throughout the year</li>
            </ul>
            
            <p>If you have any questions about your leave entitlement or need assistance with the booking system, please contact your line manager or HR.</p>
            
            <p>Best regards,<br><strong>Staff Rota System</strong></p>
            
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>For support, contact your line manager or HR department.</p>
                <p>Leave Period: {entitlement.leave_year_start.strftime('%d %b %Y')} - {entitlement.leave_year_end.strftime('%d %b %Y')}</p>
            </div>
        </div>
    </div>
</body>
</html>
            """

            # Send email
            if not dry_run:
                try:
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=message,
                        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@staffrota.com',
                        to=[user.email],
                    )
                    email.attach_alternative(html_message, "text/html")
                    email.send()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ {user.sap} - {user.full_name} ({user.email}): '
                            f'{remaining_days:.1f} days remaining - SENT'
                        )
                    )
                    emails_sent += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ {user.sap} - {user.full_name} ({user.email}): '
                            f'ERROR - {str(e)}'
                        )
                    )
                    emails_failed += 1
            else:
                # Dry run - just show what would be sent
                self.stdout.write(
                    self.style.SUCCESS(
                        f'📧 {user.sap} - {user.full_name} ({user.email}): '
                        f'{remaining_days:.1f} days remaining - WOULD SEND'
                    )
                )
                emails_sent += 1

        # Summary
        self.stdout.write(f'\n{"─"*70}')
        self.stdout.write(self.style.SUCCESS(f'\n📊 SUMMARY'))
        self.stdout.write(f'{"─"*70}')
        self.stdout.write(f'Total eligible staff:  {total_count}')
        self.stdout.write(self.style.SUCCESS(f'✅ Emails sent:        {emails_sent}'))
        if emails_failed > 0:
            self.stdout.write(self.style.ERROR(f'❌ Emails failed:      {emails_failed}'))
        if emails_skipped > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  Emails skipped:     {emails_skipped}'))
        self.stdout.write(f'{"─"*70}\n')

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\n🔍 This was a DRY RUN - no emails were actually sent.\n'
                    'Remove --dry-run to send emails for real.\n'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Email reminder campaign completed successfully!\n'
                )
            )
