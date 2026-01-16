"""
Management command to send staffing shortage alerts to available staff
Usage: python manage.py send_staffing_alerts --date YYYY-MM-DD --unit UNIT_NAME
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta, date
from scheduling.models import (
    StaffingAlert, StaffingAlertResponse, StaffingAlertTemplate,
    User, Shift, Unit, ShiftType, StaffingRequirement
)
from django.db.models import Q
import os

# Import Twilio (optional dependency)
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


class Command(BaseCommand):
    help = 'Send staffing shortage alerts to available staff'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to check staffing for (YYYY-MM-DD), defaults to tomorrow'
        )
        parser.add_argument(
            '--unit',
            type=str,
            help='Specific unit to check (optional)'
        )
        parser.add_argument(
            '--shift-type',
            type=str,
            help='Specific shift type (optional)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending'
        )
        parser.add_argument(
            '--auto-detect',
            action='store_true',
            help='Automatically detect staffing shortages for tomorrow'
        )

    def handle(self, *args, **options):
        self.dry_run = options.get('dry_run', False)
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No alerts will be sent\n'))
        
        # Determine date
        if options.get('date'):
            try:
                check_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid date format. Use YYYY-MM-DD'))
                return
        else:
            check_date = date.today() + timedelta(days=1)  # Tomorrow
        
        self.stdout.write(f'📅 Checking staffing for: {check_date}\n')
        
        # Auto-detect shortages or use manual parameters
        if options.get('auto_detect'):
            alerts_created = self.auto_detect_shortages(check_date)
        else:
            alerts_created = self.create_manual_alert(check_date, options)
        
        # Send notifications for all pending alerts
        if alerts_created > 0:
            self.send_all_pending_alerts()
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Process complete. {alerts_created} alert(s) created.'))

    def auto_detect_shortages(self, check_date):
        """
        Automatically detect staffing shortages based on requirements
        Only sends SMS when total staff falls below minimum of 17
        """
        self.stdout.write('🔍 Auto-detecting staffing shortages...\n')
        
        # CRITICAL: Minimum safe staffing level
        MINIMUM_SAFE_STAFFING = 17
        
        alerts_created = 0
        units = Unit.objects.filter(is_active=True)
        shift_types = ShiftType.objects.all()
        
        # First, check TOTAL staffing for the day across all units
        total_day_staff = Shift.objects.filter(
            date=check_date,
            shift_type__name__icontains='DAY',
            status='SCHEDULED'
        ).count()
        
        total_night_staff = Shift.objects.filter(
            date=check_date,
            shift_type__name__icontains='NIGHT',
            status='SCHEDULED'
        ).count()
        
        day_below_minimum = total_day_staff < MINIMUM_SAFE_STAFFING
        night_below_minimum = total_night_staff < MINIMUM_SAFE_STAFFING
        
        # Log overall staffing status
        if day_below_minimum:
            self.stdout.write(
                self.style.ERROR(
                    f'  🚨 CRITICAL: DAY shift has {total_day_staff}/{MINIMUM_SAFE_STAFFING} staff (BELOW MINIMUM)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✅ DAY shift: {total_day_staff}/{MINIMUM_SAFE_STAFFING} staff'
                )
            )
        
        if night_below_minimum:
            self.stdout.write(
                self.style.ERROR(
                    f'  🚨 CRITICAL: NIGHT shift has {total_night_staff}/{MINIMUM_SAFE_STAFFING} staff (BELOW MINIMUM)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✅ NIGHT shift: {total_night_staff}/{MINIMUM_SAFE_STAFFING} staff'
                )
            )
        
        # Now check per-unit shortages
        for unit in units:
            for shift_type in shift_types:
                # Count currently scheduled staff for this unit/shift combination
                scheduled = Shift.objects.filter(
                    unit=unit,
                    date=check_date,
                    shift_type=shift_type,
                    status='SCHEDULED'
                ).count()
                
                # Use default of 4 per unit per shift
                required = 4
                shortage = required - scheduled
                
                if shortage > 0:
                    # Determine if this should trigger SMS
                    is_critical = False
                    if 'DAY' in shift_type.name.upper() and day_below_minimum:
                        is_critical = True
                    elif 'NIGHT' in shift_type.name.upper() and night_below_minimum:
                        is_critical = True
                    
                    # Create alert
                    alert = self.create_alert(
                        unit=unit,
                        shift_date=check_date,
                        shift_type=shift_type,
                        required=required,
                        current=scheduled,
                        shortage=shortage,
                        is_critical=is_critical
                    )
                    
                    if alert:
                        alerts_created += 1
                        critical_marker = '🚨 CRITICAL - SMS ALERT ' if is_critical else ''
                        self.stdout.write(
                            self.style.WARNING(
                                f'  {critical_marker}⚠️  {unit.get_name_display()} - {shift_type.get_name_display()}: '
                                f'{shortage} staff short ({scheduled}/{required})'
                            )
                        )
        
        # Summary
        if day_below_minimum or night_below_minimum:
            self.stdout.write(
                self.style.ERROR(
                    f'\n🚨 CRITICAL ALERT: Staffing below minimum of {MINIMUM_SAFE_STAFFING}. SMS alerts will be sent!'
                )
            )
        
        return alerts_created

    def create_manual_alert(self, check_date, options):
        """
        Create alert based on manual parameters
        """
        unit_name = options.get('unit')
        shift_type_name = options.get('shift_type')
        
        if not unit_name:
            self.stdout.write(self.style.ERROR('Please specify --unit or use --auto-detect'))
            return 0
        
        try:
            unit = Unit.objects.get(name=unit_name)
        except Unit.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Unit "{unit_name}" not found'))
            return 0
        
        if shift_type_name:
            try:
                shift_type = ShiftType.objects.get(name=shift_type_name)
            except ShiftType.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Shift type "{shift_type_name}" not found'))
                return 0
        else:
            # Default to day shift
            shift_type = ShiftType.objects.filter(name__contains='DAY').first()
        
        # Calculate shortage
        scheduled = Shift.objects.filter(
            unit=unit,
            date=check_date,
            shift_type=shift_type,
            status='SCHEDULED'
        ).count()
        
        required = 17  # Default minimum
        shortage = required - scheduled
        
        if shortage <= 0:
            self.stdout.write(self.style.SUCCESS(f'✅ No shortage detected. Scheduled: {scheduled}/{required}'))
            return 0
        
        alert = self.create_alert(
            unit=unit,
            shift_date=check_date,
            shift_type=shift_type,
            required=required,
            current=scheduled,
            shortage=shortage
        )
        
        return 1 if alert else 0

    def create_alert(self, unit, shift_date, shift_type, required, current, shortage, is_critical=False):
        """
        Create a staffing alert
        is_critical: True if total staffing is below minimum of 17 (triggers SMS)
        """
        if self.dry_run:
            critical_note = ' [CRITICAL - SMS WILL BE SENT]' if is_critical else ''
            self.stdout.write(f'  [DRY RUN] Would create alert for {shortage} positions{critical_note}')
            return None
        
        # Check if alert already exists
        existing = StaffingAlert.objects.filter(
            unit=unit,
            shift_date=shift_date,
            shift_type=shift_type,
            status__in=['PENDING', 'PARTIALLY_FILLED']
        ).first()
        
        if existing:
            self.stdout.write(f'  ℹ️  Alert already exists (ID: {existing.id})')
            return existing
        
        # Set priority based on criticality
        if is_critical:
            priority = 10  # Maximum priority for critical shortages
        else:
            priority = min(9, shortage * 2)  # Scale based on shortage size
        
        # Create new alert
        alert = StaffingAlert.objects.create(
            alert_type='SHORTAGE',
            unit=unit,
            shift_date=shift_date,
            shift_type=shift_type,
            required_staff=required,
            current_staff=current,
            shortage=shortage,
            expires_at=timezone.now() + timedelta(hours=12),  # 12 hour expiry
            priority=priority,
            message=f'{"🚨 CRITICAL: " if is_critical else ""}We need {shortage} additional staff for {shift_type.get_name_display()} '
                   f'on {shift_date}. Can you help?',
            # Store is_critical flag in notes for SMS decision
            notes=f'Critical shortage (below min 17): {is_critical}'
        )
        
        return alert

    def send_all_pending_alerts(self):
        """
        Send notifications for all pending alerts
        """
        pending_alerts = StaffingAlert.objects.filter(
            status__in=['PENDING', 'PARTIALLY_FILLED'],
            expires_at__gt=timezone.now()
        )
        
        self.stdout.write(f'\n📧 Sending notifications for {pending_alerts.count()} alert(s)...\n')
        
        for alert in pending_alerts:
            self.send_alert_notifications(alert)

    def send_alert_notifications(self, alert):
        """
        Send SMS and email notifications for an alert
        """
        # Find available staff
        available_staff = self.find_available_staff(alert)
        
        self.stdout.write(f'\n  Alert: {alert}')
        self.stdout.write(f'  Found {available_staff.count()} available staff members\n')
        
        emails_sent = 0
        sms_sent = 0
        
        for staff in available_staff:
            # Create response record
            response, created = StaffingAlertResponse.objects.get_or_create(
                alert=alert,
                user=staff,
                defaults={'status': 'PENDING'}
            )
            
            if not created and response.status != 'PENDING':
                continue  # Already responded
            
            # Send email
            if self.send_email_alert(alert, staff, response):
                emails_sent += 1
                response.email_sent_at = timezone.now()
                response.save()
            
            # Send SMS (if configured)
            if hasattr(staff, 'phone_number') and staff.phone_number:
                if self.send_sms_alert(alert, staff, response):
                    sms_sent += 1
                    response.sms_sent_at = timezone.now()
                    response.save()
        
        # Update alert
        if not self.dry_run:
            alert.email_sent += emails_sent
            alert.sms_sent += sms_sent
            alert.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'  ✉️  Emails sent: {emails_sent}\n'
                f'  📱 SMS sent: {sms_sent}'
            )
        )

    def find_available_staff(self, alert):
        """
        Find staff who are available and eligible for the shift
        """
        # Staff who are:
        # 1. Active
        # 2. Not already scheduled on that day
        # 3. In compatible roles
        # 4. Not on leave
        
        scheduled_users = Shift.objects.filter(
            date=alert.shift_date
        ).values_list('user_id', flat=True)
        
        on_leave = User.objects.filter(
            leave_requests__start_date__lte=alert.shift_date,
            leave_requests__end_date__gte=alert.shift_date,
            leave_requests__status='APPROVED'
        ).values_list('id', flat=True)
        
        # Get compatible roles for this shift type
        compatible_roles = alert.shift_type.get_applicable_roles_list()
        
        available = User.objects.filter(
            is_active=True,
            role__name__in=compatible_roles
        ).exclude(
            id__in=scheduled_users
        ).exclude(
            id__in=on_leave
        ).order_by('?')[:50]  # Random order, limit to 50
        
        return available

    def send_email_alert(self, alert, staff, response):
        """
        Send email notification with accept/decline links
        """
        accept_url = f"{settings.SITE_URL}/staffing/respond/{response.response_token}/accept/"
        decline_url = f"{settings.SITE_URL}/staffing/respond/{response.response_token}/decline/"
        web_url = f"{settings.SITE_URL}/staffing/alerts/"
        
        subject = f'🚨 URGENT: Staff Needed - {alert.shift_date}'
        
        message = f"""Hello {staff.first_name},

We urgently need additional staff for:

📅 Date: {alert.shift_date}
🏥 Unit: {alert.unit.get_name_display()}
⏰ Shift: {alert.shift_type.get_name_display()}
👥 Positions Available: {alert.positions_remaining}

{alert.message}

QUICK RESPONSE OPTIONS:

✅ Accept Shift (one-click):
{accept_url}

❌ Decline:
{decline_url}

Or login to view details:
{web_url}

This alert expires at: {alert.expires_at.strftime('%I:%M %p')}

Thank you for your flexibility!

Staff Rota Management System
"""
        
        if self.dry_run:
            self.stdout.write(f'    [DRY RUN] Would email {staff.email}')
            return True
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[staff.email],
                fail_silently=False,
            )
            self.stdout.write(f'    ✉️  Emailed: {staff.full_name} ({staff.email})')
            return True
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'    ❌ Email failed for {staff.email}: {str(e)}')
            )
            return False

    def send_sms_alert(self, alert, staff, response):
        """
        Send SMS notification via Twilio
        ONLY sends if alert is critical (total staff below 17)
        """
        # Check if this is a critical alert (below minimum staffing of 17)
        is_critical = alert.notes and 'Critical shortage (below min 17): True' in alert.notes
        
        if not is_critical:
            # Don't send SMS for non-critical shortages
            return False
        
        # Check if Twilio is configured
        if not TWILIO_AVAILABLE:
            if not self.dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'    ⚠️  Twilio not installed. Run: pip install twilio'
                    )
                )
            return False
        
        # Get Twilio credentials from environment
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            if not self.dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'    ⚠️  Twilio not configured. Set TWILIO_ACCOUNT_SID, '
                        f'TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env'
                    )
                )
            return False
        
        # Validate phone number
        if not staff.phone_number:
            return False
        
        # Format phone number (ensure it starts with + and country code)
        phone = staff.phone_number.strip()
        if not phone.startswith('+'):
            # Assume UK number if no country code
            phone = f'+44{phone.lstrip("0")}'
        
        # Create short URL for SMS
        accept_url = f"{settings.SITE_URL}/staffing/respond/{response.response_token}/accept/"
        
        # SMS message for CRITICAL shortage (max 160 chars for single message)
        message = (
            f"🚨 CRITICAL: Below min staff! Need you {alert.shift_date.strftime('%d/%m')} "
            f"{alert.unit.get_name_display()} {alert.shift_type.get_name_display()}. "
            f"Enhanced rates. Accept: {accept_url}"
        )
        
        # Truncate if too long
        if len(message) > 160:
            message = (
                f"🚨 CRITICAL SHORTAGE {alert.shift_date.strftime('%d/%m')} "
                f"{alert.unit.get_name_display()}. Enhanced rates. {accept_url}"
            )
        
        if self.dry_run:
            self.stdout.write(
                f'    [DRY RUN] Would SMS {phone}: {message[:50]}...'
            )
            return True
        
        try:
            # Initialize Twilio client
            client = Client(account_sid, auth_token)
            
            # Send SMS
            sms = client.messages.create(
                body=message,
                from_=from_number,
                to=phone
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'    📱 SMS sent to {staff.full_name} ({phone}) - SID: {sms.sid}'
                )
            )
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'    ❌ SMS failed for {phone}: {str(e)}'
                )
            )
            return False
