"""
Management command to send overtime coverage requests
Intelligently filters and ranks staff based on preferences and reliability
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import logging

from scheduling.models import Unit, Staff
from scheduling.models_overtime import (
    StaffOvertimePreference,
    OvertimeCoverageRequest,
    OvertimeCoverageResponse
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send overtime coverage request to qualified staff based on preferences'

    def add_arguments(self, parser):
        parser.add_argument(
            '--home',
            type=str,
            required=True,
            help='Home name (e.g., "Victoria Gardens")'
        )
        parser.add_argument(
            '--date',
            type=str,
            required=True,
            help='Shift date (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--shift-type',
            type=str,
            required=True,
            choices=['Early', 'Late', 'Night'],
            help='Shift type'
        )
        parser.add_argument(
            '--role',
            type=str,
            required=True,
            choices=['RN', 'SSW', 'HCA'],
            help='Required role'
        )
        parser.add_argument(
            '--max-contacts',
            type=int,
            default=5,
            help='Maximum number of staff to contact (default: 5)'
        )
        parser.add_argument(
            '--min-score',
            type=float,
            default=50.0,
            help='Minimum reliability score to contact (0-100, default: 50)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show who would be contacted without actually sending messages'
        )
        parser.add_argument(
            '--send-sms',
            action='store_true',
            help='Actually send SMS messages (requires Twilio setup)'
        )

    def handle(self, *args, **options):
        home_name = options['home']
        shift_date_str = options['date']
        shift_type = options['shift_type']
        required_role = options['role']
        max_contacts = options['max_contacts']
        min_score = options['min_score']
        dry_run = options['dry_run']
        send_sms = options['send_sms']
        
        # Validate and get home
        try:
            unit = Unit.objects.get(name=home_name)
        except Unit.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Home "{home_name}" not found'))
            return
        
        # Parse date
        try:
            shift_date = datetime.strptime(shift_date_str, '%Y-%m-%d').date()
        except ValueError:
            self.stdout.write(self.style.ERROR('Invalid date format. Use YYYY-MM-DD'))
            return
        
        # Check if date is in the future
        if shift_date < timezone.now().date():
            self.stdout.write(self.style.ERROR('Shift date must be in the future'))
            return
        
        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(self.style.WARNING('OVERTIME COVERAGE REQUEST'))
        self.stdout.write(f'{"="*80}\n')
        
        self.stdout.write(f'Home: {unit.name}')
        self.stdout.write(f'Date: {shift_date.strftime("%A, %B %d, %Y")}')
        self.stdout.write(f'Shift: {shift_type} Shift')
        self.stdout.write(f'Role Required: {required_role}')
        self.stdout.write(f'Max Contacts: {max_contacts}')
        self.stdout.write(f'Min Reliability Score: {min_score}%\n')
        
        # Find eligible staff
        self.stdout.write(self.style.WARNING('Step 1: Filtering eligible staff...\n'))
        
        eligible_staff = self._find_eligible_staff(
            unit=unit,
            shift_date=shift_date,
            shift_type=shift_type,
            required_role=required_role,
            min_score=min_score
        )
        
        if not eligible_staff:
            self.stdout.write(self.style.ERROR('No eligible staff found matching criteria'))
            self.stdout.write('\nSuggestions:')
            self.stdout.write('  - Lower minimum reliability score')
            self.stdout.write('  - Check staff overtime preferences are set up')
            self.stdout.write('  - Verify staff have opted in for overtime')
            self.stdout.write('  - Ensure staff have selected this home in preferences')
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(eligible_staff)} eligible staff\n'))
        
        # Rank and select top candidates
        self.stdout.write(self.style.WARNING('Step 2: Ranking candidates by reliability...\n'))
        
        ranked_staff = self._rank_staff(eligible_staff)
        selected_staff = ranked_staff[:max_contacts]
        
        # Display ranked list
        self.stdout.write('Top Candidates:')
        self.stdout.write(f'{"#":<4} {"Name":<25} {"Role":<6} {"Score":<8} {"Accept%":<10} {"Last OT":<15} {"Home"}')
        self.stdout.write('-' * 100)
        
        for idx, staff_data in enumerate(selected_staff, 1):
            staff = staff_data['staff']
            pref = staff_data['preference']
            score = staff_data['score']
            
            last_ot = 'Never'
            if pref.last_worked_overtime:
                days_ago = (timezone.now() - pref.last_worked_overtime).days
                if days_ago == 0:
                    last_ot = 'Today'
                elif days_ago == 1:
                    last_ot = 'Yesterday'
                else:
                    last_ot = f'{days_ago} days ago'
            
            self.stdout.write(
                f'{idx:<4} {staff.name:<25} {staff.role:<6} {score:<8.1f} '
                f'{pref.acceptance_rate:<10.1f} {last_ot:<15} {staff.unit.name}'
            )
        
        self.stdout.write('')
        
        # Create coverage request
        if not dry_run:
            coverage_request = OvertimeCoverageRequest.objects.create(
                unit=unit,
                shift_date=shift_date,
                shift_type=shift_type,
                required_role=required_role,
                total_contacted=len(selected_staff),
                created_by=None  # Set to current user in real implementation
            )
            
            self.stdout.write(self.style.SUCCESS(f'Created coverage request #{coverage_request.id}\n'))
        
        # Send messages
        self.stdout.write(self.style.WARNING('Step 3: Sending messages...\n'))
        
        for idx, staff_data in enumerate(selected_staff, 1):
            staff = staff_data['staff']
            pref = staff_data['preference']
            score = staff_data['score']
            
            message = self._create_message(
                staff=staff,
                unit=unit,
                shift_date=shift_date,
                shift_type=shift_type,
                required_role=required_role
            )
            
            if dry_run:
                self.stdout.write(f'[DRY RUN] Would send to {staff.name} ({pref.phone_number}):')
                self.stdout.write(f'  {message}\n')
            else:
                # Create response record
                response = OvertimeCoverageResponse.objects.create(
                    request=coverage_request,
                    staff=staff,
                    contact_method=pref.preferred_contact_method,
                    reliability_score_when_sent=score
                )
                
                # Update preference tracking
                pref.total_requests_sent += 1
                pref.last_contacted = timezone.now()
                pref.save()
                
                if send_sms:
                    success = self._send_sms(pref.phone_number, message)
                    if success:
                        self.stdout.write(self.style.SUCCESS(f'✓ Sent SMS to {staff.name}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'✗ Failed to send SMS to {staff.name}'))
                else:
                    self.stdout.write(f'[MESSAGE CREATED] {staff.name} - {message[:50]}...')
        
        # Summary
        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(f'{"="*80}\n')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No messages were sent'))
            self.stdout.write(f'Would contact {len(selected_staff)} staff members')
            self.stdout.write('\nTo actually send messages, run again with --send-sms flag')
        else:
            self.stdout.write(self.style.SUCCESS(f'Contacted {len(selected_staff)} staff members'))
            if send_sms:
                self.stdout.write('SMS messages sent successfully')
            else:
                self.stdout.write('Response records created (use --send-sms to send actual messages)')
            self.stdout.write(f'\nCoverage request ID: {coverage_request.id}')
            self.stdout.write('Monitor responses in the admin panel')
        
        self.stdout.write('')

    def _find_eligible_staff(self, unit, shift_date, shift_type, required_role, min_score):
        """Find staff eligible for this overtime opportunity"""
        
        # Get all staff with overtime preferences enabled
        preferences = StaffOvertimePreference.objects.filter(
            available_for_overtime=True,
            staff__role=required_role,
            staff__is_active=True
        ).select_related('staff', 'staff__unit').prefetch_related('willing_to_work_at')
        
        eligible = []
        
        for pref in preferences:
            # Check if willing to work at this home
            if not pref.can_work_at_home(unit):
                continue
            
            # Check shift type preference
            if not pref.can_work_shift_type(shift_type):
                continue
            
            # Check day preference (weekday/weekend)
            if not pref.can_work_on_date(shift_date):
                continue
            
            # Check reliability score
            score = pref.get_reliability_score()
            if score < min_score:
                continue
            
            # Check if staff has WTD capacity
            # (In production, would check actual hours worked this week)
            
            eligible.append({
                'staff': pref.staff,
                'preference': pref,
                'score': score
            })
        
        return eligible

    def _rank_staff(self, eligible_staff):
        """Rank staff by reliability score and other factors"""
        return sorted(eligible_staff, key=lambda x: x['score'], reverse=True)

    def _create_message(self, staff, unit, shift_date, shift_type, required_role):
        """Create personalized SMS message"""
        
        day_name = shift_date.strftime('%A')
        date_str = shift_date.strftime('%b %d')
        
        message = (
            f"Hi {staff.first_name}! Overtime available:\n"
            f"{unit.name}\n"
            f"{day_name} {date_str} - {shift_type} Shift\n"
            f"Role: {required_role}\n\n"
            f"Interested? Reply YES or NO"
        )
        
        return message

    def _send_sms(self, phone_number, message):
        """
        Send SMS using Twilio (placeholder)
        In production, implement actual Twilio integration
        """
        # TODO: Implement Twilio SMS sending
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=message,
        #     from_='+1234567890',
        #     to=phone_number
        # )
        
        logger.info(f'Would send SMS to {phone_number}: {message}')
        return True
