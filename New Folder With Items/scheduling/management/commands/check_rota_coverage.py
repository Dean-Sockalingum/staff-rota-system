"""
Management command to check rota coverage and auto-generate if needed.
This can be run via cron to ensure perpetual rota coverage.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from scheduling.models import Shift


class Command(BaseCommand):
    help = 'Checks rota coverage and auto-generates future shifts if needed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold-days',
            type=int,
            default=60,
            help='Generate more shifts if coverage is less than this many days ahead (default: 60)'
        )
        parser.add_argument(
            '--generate-weeks',
            type=int,
            default=26,
            help='Number of weeks to generate when coverage is low (default: 26)'
        )

    def handle(self, *args, **options):
        threshold_days = options['threshold_days']
        generate_weeks = options['generate_weeks']

        self.stdout.write(self.style.SUCCESS(
            f'\n=== Checking Rota Coverage ===\n'
        ))

        # Find the last shift date
        last_shift = Shift.objects.order_by('-date').first()
        
        if not last_shift:
            self.stdout.write(self.style.ERROR('No shifts found in database!'))
            return

        last_date = last_shift.date
        today = timezone.now().date()
        days_ahead = (last_date - today).days

        self.stdout.write(f'Today: {today}')
        self.stdout.write(f'Last shift date: {last_date}')
        self.stdout.write(f'Coverage: {days_ahead} days ahead')
        self.stdout.write(f'Threshold: {threshold_days} days\n')

        if days_ahead < threshold_days:
            self.stdout.write(self.style.WARNING(
                f'⚠️  Coverage is below threshold! Generating {generate_weeks} weeks of future shifts...\n'
            ))
            
            # Call the generate_future_shifts command
            call_command('generate_future_shifts', weeks=generate_weeks)
            
            self.stdout.write(self.style.SUCCESS(
                '\n✓ Auto-generation complete\n'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✓ Coverage is sufficient ({days_ahead} days ahead)\n'
                f'No action needed.\n'
            ))
