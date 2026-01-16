"""
Create Victoria Gardens SM/OM DAY_SENIOR shifts.
SM and OM are supernumerary and work Monday-Friday 9-5.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, User, CareHome, ShiftType, Unit
from datetime import datetime, timedelta
import calendar

class Command(BaseCommand):
    help = 'Create Victoria Gardens SM/OM shifts (Mon-Fri 9-5)'

    def add_arguments(self, parser):
        parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
        parser.add_argument('--weeks', type=int, default=7, help='Number of weeks to create')
        parser.add_argument('--dry-run', action='store_true', help='Preview without saving')

    def handle(self, *args, **options):
        start_date_str = options.get('start_date')
        weeks = options['weeks']
        dry_run = options['dry_run']

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = datetime(2025, 12, 15).date()

        # Get Victoria Gardens
        vg = CareHome.objects.get(name='VICTORIA_GARDENS')
        vg_unit = Unit.objects.filter(care_home=vg).first()
        
        # Get SM and OM staff
        sm_sap = 'SSCWN1693'  # Grace MacDonald
        om_sap = 'SSCWN1694'  # David Stewart
        
        # Get DAY_SENIOR shift type
        day_senior_type = ShiftType.objects.get(name='DAY_SENIOR')
        
        stats = {
            'created': 0,
            'sm_shifts': 0,
            'om_shifts': 0,
        }
        
        with transaction.atomic():
            for week_offset in range(weeks):
                week_start = start_date + timedelta(weeks=week_offset)
                
                self.stdout.write(f"\n=== Week {week_offset + 1} ===")
                self.stdout.write(f"Week starting: {week_start}")
                
                for day_offset in range(7):
                    current_date = week_start + timedelta(days=day_offset)
                    weekday = current_date.weekday()  # 0=Monday, 6=Sunday
                    day_name = calendar.day_name[weekday]
                    
                    # Only Monday-Friday (0-4)
                    if weekday > 4:
                        continue
                    
                    # Create shifts for both SM and OM
                    sm = User.objects.get(sap=sm_sap)
                    om = User.objects.get(sap=om_sap)
                    
                    if not dry_run:
                        # SM shift
                        Shift.objects.create(
                            user=sm,
                            date=current_date,
                            shift_type=day_senior_type,
                            unit=vg_unit
                        )
                        
                        # OM shift
                        Shift.objects.create(
                            user=om,
                            date=current_date,
                            shift_type=day_senior_type,
                            unit=vg_unit
                        )
                    
                    stats['created'] += 2
                    stats['sm_shifts'] += 1
                    stats['om_shifts'] += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  {current_date} ({day_name}): SM + OM (Grace MacDonald, David Stewart)"
                        )
                    )
            
            if dry_run:
                self.stdout.write(self.style.WARNING("\n=== DRY RUN - No changes saved ==="))
                raise transaction.TransactionManagementError("Dry run")
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f"\n=== Summary ==="))
        self.stdout.write(f"Total DAY_SENIOR shifts created: {stats['created']}")
        self.stdout.write(f"  SM (Grace MacDonald): {stats['sm_shifts']} shifts")
        self.stdout.write(f"  OM (David Stewart): {stats['om_shifts']} shifts")
