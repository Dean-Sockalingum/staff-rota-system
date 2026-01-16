"""
Create Victoria Gardens SSCWN NIGHT_SENIOR shifts using 3-week rotating pattern.
SSCWN are supernumerary like SSCW.

Based on image pattern - 4 SCWN on 35-hour contracts (3 nights/week):
- 1 staff: Sun/Mon/Tue → Thu/Fri/Sat → Tue/Wed/Thu
- 1 staff: Tue/Wed/Thu → Sun/Mon/Tue → Thu/Fri/Sat
- 2 staff: Thu/Fri/Sat → Tue/Wed/Thu → Sun/Mon/Tue
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, User, CareHome, ShiftType, Unit
from datetime import datetime, timedelta
import calendar

class Command(BaseCommand):
    help = 'Create Victoria Gardens SSCWN shifts using 3-week rotating pattern'

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
        
        # Get SSCWN staff (4 total) - all 35-hour contracts
        scwn_staff = [
            'SSCWN1748',  # Dennis Hudson
            'SSCWN1749',  # Joy Mills
            'SSCWN1750',  # Raymond Palmer
            'SSCWN1751',  # Mercy Stone
        ]
        
        # 35-hour patterns (3 nights per week) - from image
        # Pattern cycles: Week1 → Week2 → Week3
        # Weekday numbers: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
        patterns = {
            # 1 staff: Sun/Mon/Tue → Thu/Fri/Sat → Tue/Wed/Thu
            'SSCWN1748': [[6,0,1], [3,4,5], [1,2,3]],  # Dennis Hudson
            
            # 1 staff: Tue/Wed/Thu → Sun/Mon/Tue → Thu/Fri/Sat
            'SSCWN1749': [[1,2,3], [6,0,1], [3,4,5]],  # Joy Mills
            
            # 2 staff: Thu/Fri/Sat → Tue/Wed/Thu → Sun/Mon/Tue
            'SSCWN1750': [[3,4,5], [1,2,3], [6,0,1]],  # Raymond Palmer
            'SSCWN1751': [[3,4,5], [1,2,3], [6,0,1]],  # Mercy Stone
        }
        
        # Get NIGHT_SENIOR shift type
        night_senior_type = ShiftType.objects.get(name='NIGHT_SENIOR')
        
        stats = {
            'created': 0,
            'per_staff': {}
        }
        
        for sap in scwn_staff:
            stats['per_staff'][sap] = 0
        
        with transaction.atomic():
            for week_offset in range(weeks):
                week_start = start_date + timedelta(weeks=week_offset)
                week_num = week_offset % 3  # 3-week cycle
                
                self.stdout.write(f"\n=== Week {week_offset + 1} (Cycle week {week_num + 1}) ===")
                self.stdout.write(f"Week starting: {week_start}")
                
                for day_offset in range(7):
                    current_date = week_start + timedelta(days=day_offset)
                    weekday = current_date.weekday()  # 0=Monday, 6=Sunday
                    day_name = calendar.day_name[weekday]
                    
                    daily_staff = []
                    
                    # Check each SSCWN staff member for this night
                    for sap in scwn_staff:
                        pattern = patterns[sap]
                        working_nights = pattern[week_num]
                        
                        if weekday in working_nights:
                            daily_staff.append(sap)
                    
                    if not daily_staff:
                        continue
                    
                    # Create NIGHT_SENIOR shifts for staff working this night
                    # SSCWN are supernumerary, assign to first unit
                    for sap in daily_staff:
                        staff = User.objects.get(sap=sap)
                        
                        if not dry_run:
                            Shift.objects.create(
                                user=staff,
                                date=current_date,
                                shift_type=night_senior_type,
                                unit=vg_unit
                            )
                        
                        stats['created'] += 1
                        stats['per_staff'][sap] += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  {current_date} ({day_name}): {len(daily_staff)} SSCWN - {', '.join([User.objects.get(sap=s).first_name for s in daily_staff])}"
                        )
                    )
            
            if dry_run:
                self.stdout.write(self.style.WARNING("\n=== DRY RUN - No changes saved ==="))
                raise transaction.TransactionManagementError("Dry run")
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f"\n=== Summary ==="))
        self.stdout.write(f"Total NIGHT_SENIOR (SSCWN) shifts created: {stats['created']}")
        self.stdout.write(f"\n35-hour contracts (3 nights/week):")
        for sap in scwn_staff:
            user = User.objects.get(sap=sap)
            self.stdout.write(f"  {user.first_name} {user.last_name}: {stats['per_staff'][sap]} shifts")
