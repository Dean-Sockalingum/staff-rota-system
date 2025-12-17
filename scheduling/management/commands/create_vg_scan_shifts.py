"""
Create Victoria Gardens SCAN NIGHT_ASSISTANT shifts using 3-week rotating patterns.

Based on image: 28 SCAN staff
- Mix of 35-hour contracts (3 nights/week)
- Mix of 24-hour contracts (2 nights/week) - CAREFUL: Tue/Wed, Wed/Thu, Fri/Sat variations
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, User, CareHome, ShiftType, Unit
from datetime import datetime, timedelta
import calendar

class Command(BaseCommand):
    help = 'Create Victoria Gardens SCAN NIGHT_ASSISTANT shifts using 3-week rotating pattern'

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
        units = list(Unit.objects.filter(care_home=vg).order_by('name'))
        
        # Weekday numbers: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
        
        # 35-hour patterns (3 nights/week)
        patterns_35hr = {
            # Tue/Wed/Thu → Sun/Mon/Tue → Thu/Fri/Sat
            'SSCWN1753': [[1,2,3], [6,0,1], [3,4,5]],  # Patience Boyd
            'SSCWN1754': [[1,2,3], [6,0,1], [3,4,5]],  # Maurice Craig
            'SSCWN1755': [[1,2,3], [6,0,1], [3,4,5]],  # Charity Dunn
            'SSCWN1756': [[1,2,3], [6,0,1], [3,4,5]],  # Leonard Fleming
            
            # Sun/Mon/Tue → Thu/Fri/Sat → Tue/Wed/Thu
            'SSCWN1758': [[6,0,1], [3,4,5], [1,2,3]],  # Kenneth Kerr
            'SSCWN1759': [[6,0,1], [3,4,5], [1,2,3]],  # Verity Maxwell
            'SSCWN1760': [[6,0,1], [3,4,5], [1,2,3]],  # Leslie Morrison
            'SSCWN1761': [[6,0,1], [3,4,5], [1,2,3]],  # Grace Muir
            
            # Tue/Wed/Thu → Sun/Mon/Tue → Thu/Fri/Sat
            'SSCWN1763': [[1,2,3], [6,0,1], [3,4,5]],  # Ruth Quinn
            
            # Sun/Mon/Tue → Thu/Fri/Sat → Tue/Wed/Thu
            'SSCWN1764': [[6,0,1], [3,4,5], [1,2,3]],  # Douglas Sutherland
            'SSCWN1765': [[6,0,1], [3,4,5], [1,2,3]],  # Esther MacDonald
            'SSCWN1766': [[6,0,1], [3,4,5], [1,2,3]],  # Ronald Stewart
        }
        
        # 24-hour patterns (2 nights/week) - CAREFUL: Different combinations!
        patterns_24hr = {
            # Tue/Wed → Sun/Mon → Fri/Sat
            'SSCWN1768': [[1,2], [6,0], [4,5]],  # Terence Robertson
            
            # Fri/Sat → Sun/Mon → Tue/Wed
            'SSCWN1769': [[4,5], [6,0], [1,2]],  # Rachel Thomson
            'SSCWN1770': [[4,5], [6,0], [1,2]],  # Geoffrey Anderson
            
            # Sun/Mon → Fri/Sat → Tue/Wed
            'SSCWN1771': [[6,0], [4,5], [1,2]],  # Leah Murray
            'SSCWN1773': [[6,0], [4,5], [1,2]],  # Sarah Ferguson
            
            # Fri/Sat → Tue/Wed → Sun/Mon
            'SSCWN1774': [[4,5], [1,2], [6,0]],  # Anthony Grant
            'SSCWN1775': [[4,5], [1,2], [6,0]],  # Rebecca Morrison
            
            # Sun/Mon → Fri/Sat → Tue/Wed
            'SSCWN1776': [[6,0], [4,5], [1,2]],  # Francis Duncan
            
            # Fri/Sat → Tue/Wed → Sun/Mon
            'SSCWN1778': [[4,5], [1,2], [6,0]],  # Clifford Graham
            'SSCWN1779': [[4,5], [1,2], [6,0]],  # Hannah Johnston
            
            # Wed/Thu → Sun/Mon → Fri/Sat
            'SSCWN1752': [[2,3], [6,0], [4,5]],  # Norman Walsh
            
            # Tue/Wed → Sun/Mon → Fri/Sat
            'SSCWN1757': [[1,2], [6,0], [4,5]],  # Honor Hart
            
            # Sun/Mon → Fri/Sat → Wed/Thu
            'SSCWN1762': [[6,0], [4,5], [2,3]],  # Gordon Paterson
            
            # Sun/Mon → Fri/Sat → Tue/Wed
            'SSCWN1777': [[6,0], [4,5], [1,2]],  # Naomi Hamilton
        }
        
        # Combine patterns (skip SSCWN1767, 1772 - vacancies)
        all_patterns = {**patterns_35hr, **patterns_24hr}
        
        # Get NIGHT_ASSISTANT shift type
        night_assistant_type = ShiftType.objects.get(name='NIGHT_ASSISTANT')
        
        stats = {
            'created': 0,
            'per_staff': {}
        }
        
        for sap in all_patterns.keys():
            stats['per_staff'][sap] = 0
        
        with transaction.atomic():
            for week_offset in range(weeks):
                week_start = start_date + timedelta(weeks=week_offset)
                week_num = week_offset % 3  # 3-week cycle
                
                self.stdout.write(f"\n=== Week {week_offset + 1} (Cycle week {week_num + 1}) ===")
                
                for day_offset in range(7):
                    current_date = week_start + timedelta(days=day_offset)
                    weekday = current_date.weekday()
                    day_name = calendar.day_name[weekday]
                    
                    daily_staff = []
                    
                    # Check each SCAN staff member for this night
                    for sap in all_patterns.keys():
                        pattern = all_patterns[sap]
                        working_nights = pattern[week_num]
                        
                        if weekday in working_nights:
                            daily_staff.append(sap)
                    
                    if not daily_staff:
                        continue
                    
                    self.stdout.write(f"{day_name} {current_date}: {len(daily_staff)} SCAN on shift")
                    
                    # Create shifts for staff working this night
                    for idx, sap in enumerate(daily_staff):
                        staff = User.objects.get(sap=sap)
                        unit = units[idx % len(units)]
                        
                        if not dry_run:
                            Shift.objects.create(
                                user=staff,
                                date=current_date,
                                shift_type=night_assistant_type,
                                unit=unit
                            )
                        
                        stats['created'] += 1
                        stats['per_staff'][sap] += 1
            
            if dry_run:
                self.stdout.write(self.style.WARNING("\n=== DRY RUN - No changes saved ==="))
                raise transaction.TransactionManagementError("Dry run")
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f"\n=== Summary ==="))
        self.stdout.write(f"Total NIGHT_ASSISTANT (SCAN) shifts created: {stats['created']}")
        self.stdout.write(f"\n35-hour contracts (3 nights/week): {len(patterns_35hr)} staff")
        self.stdout.write(f"24-hour contracts (2 nights/week): {len(patterns_24hr)} staff")
        self.stdout.write(f"Vacancies (not assigned): 2 positions (SSCWN1767, SSCWN1772)")
        
        self.stdout.write("\nShifts per staff:")
        for sap in sorted(stats['per_staff'].keys()):
            count = stats['per_staff'][sap]
            self.stdout.write(f"  {sap}: {count} shifts")
