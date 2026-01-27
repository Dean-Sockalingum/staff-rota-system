"""
Create Victoria Gardens SCW DAY_ASSISTANT shifts using 3-week rotating patterns.

Based on image pattern:
- 8 SCW on 35-hour contracts (3 days/week)
- 8 SCW on 24-hour contracts (2 days/week)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, User, CareHome, ShiftType, Unit
from datetime import datetime, timedelta
import calendar

class Command(BaseCommand):
    help = 'Create Victoria Gardens SCW shifts using 3-week rotating pattern from image'

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
        
        # Get SCW staff (16 total) - assign first 8 to 35hr, last 8 to 24hr
        scw_staff = [
            'SSCWN1701', 'SSCWN1702', 'SSCWN1703', 'SSCWN1704',  # 35hr group 1
            'SSCWN1705', 'SSCWN1706', 'SSCWN1707', 'SSCWN1708',  # 35hr group 2
            'SSCWN1709', 'SSCWN1710', 'SSCWN1711', 'SSCWN1712',  # 24hr group 1
            'SSCWN1713', 'SSCWN1714', 'SSCWN1715', 'SSCWN1716',  # 24hr group 2
        ]
        
        # 35-hour patterns (3 days per week) - from image
        # Pattern cycles: Week1 → Week2 → Week3
        patterns_35hr = {
            # 4 staff: Sun/Wed/Thu → Mon/Tue/Wed → Wed/Fri/Sat
            'SSCWN1701': [[6,2,3], [0,1,2], [2,4,5]],  # Pearl Ferguson
            'SSCWN1702': [[6,2,3], [0,1,2], [2,4,5]],  # Stephen Grant
            'SSCWN1703': [[6,2,3], [0,1,2], [2,4,5]],  # Violet Morrison
            'SSCWN1704': [[6,2,3], [0,1,2], [2,4,5]],  # Mark Duncan
            
            # 2 staff: Mon/Tue/Wed → Wed/Fri/Sat → Sun/Wed/Thu
            'SSCWN1705': [[0,1,2], [2,4,5], [6,2,3]],  # Hazel Hamilton
            'SSCWN1706': [[0,1,2], [2,4,5], [6,2,3]],  # Paul Graham
            
            # 1 staff: Wed/Fri/Sat → Sun/Wed/Thu → Mon/Tue/Wed
            'SSCWN1707': [[2,4,5], [6,2,3], [0,1,2]],  # Iris Johnston
            
            # 1 staff: Mon/Tue/Wed → Tue/Fri/Sat → Sun/Wed/Thu (note: Tue not Wed in week2)
            'SSCWN1708': [[0,1,2], [1,4,5], [6,2,3]],  # Kevin Wallace
        }
        
        # 24-hour patterns (2 days per week) - from image
        patterns_24hr = {
            # 5 staff: Fri/Sat → Sun/Thu → Mon/Tue
            'SSCWN1709': [[4,5], [6,3], [0,1]],  # Marigold Fraser
            'SSCWN1710': [[4,5], [6,3], [0,1]],  # Simon Ross
            'SSCWN1711': [[4,5], [6,3], [0,1]],  # Poppy Henderson
            'SSCWN1712': [[4,5], [6,3], [0,1]],  # Colin Gibson
            
            # 1 staff: Mon/Thu → Fri/Sat → Sun/Thu
            'SSCWN1713': [[0,3], [4,5], [6,3]],  # Jasmine Burns
            
            # 2 staff: Mon/Tue → Fri/Sat → Sun/Thu
            'SSCWN1714': [[0,1], [4,5], [6,3]],  # Brian Kennedy
            'SSCWN1715': [[0,1], [4,5], [6,3]],  # Heather Russell
            
            # 1 staff: Fri/Sat → Sun/Thu → Mon/Tue (same as first 5)
            'SSCWN1716': [[4,5], [6,3], [0,1]],  # Graham Crawford
        }
        
        # Combine patterns
        all_patterns = {**patterns_35hr, **patterns_24hr}
        
        # Get DAY_ASSISTANT shift type
        day_assistant_type = ShiftType.objects.get(name='DAY_ASSISTANT')
        
        stats = {
            'created': 0,
            'per_staff': {}
        }
        
        for sap in scw_staff:
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
                    
                    # Check each SCW staff member for this day
                    for sap in scw_staff:
                        pattern = all_patterns[sap]
                        working_days = pattern[week_num]
                        
                        if weekday in working_days:
                            daily_staff.append(sap)
                    
                    if not daily_staff:
                        continue
                    
                    # Create shifts for staff working this day
                    # Distribute across units
                    for idx, sap in enumerate(daily_staff):
                        staff = User.objects.get(sap=sap)
                        unit = units[idx % len(units)]  # Rotate through units
                        
                        if not dry_run:
                            Shift.objects.create(
                                user=staff,
                                date=current_date,
                                shift_type=day_assistant_type,
                                unit=unit
                            )
                        
                        stats['created'] += 1
                        stats['per_staff'][sap] += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  {current_date} ({day_name}): {len(daily_staff)} SCW - {', '.join([User.objects.get(sap=s).first_name for s in daily_staff])}"
                        )
                    )
            
            if dry_run:
                self.stdout.write(self.style.WARNING("\n=== DRY RUN - No changes saved ==="))
                raise transaction.TransactionManagementError("Dry run")
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f"\n=== Summary ==="))
        self.stdout.write(f"Total DAY_ASSISTANT (SCW) shifts created: {stats['created']}")
        self.stdout.write(f"\n35-hour contracts (3 days/week):")
        for sap in scw_staff[:8]:
            user = User.objects.get(sap=sap)
            self.stdout.write(f"  {user.first_name} {user.last_name}: {stats['per_staff'][sap]} shifts")
        
        self.stdout.write(f"\n24-hour contracts (2 days/week):")
        for sap in scw_staff[8:]:
            user = User.objects.get(sap=sap)
            self.stdout.write(f"  {user.first_name} {user.last_name}: {stats['per_staff'][sap]} shifts")
