from django.core.management.base import BaseCommand
from scheduling.models import User, Unit, ShiftType, Shift
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Generate weekly schedules based on shift preferences and working hours'

    def add_arguments(self, parser):
        parser.add_argument(
            '--weeks',
            type=int,
            default=2,
            help='Number of weeks to generate schedules for (default: 2)'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date in YYYY-MM-DD format (default: next Monday)'
        )

    def handle(self, *args, **options):
        weeks = options['weeks']
        
        # Calculate start date (next Monday if not specified)
        if options['start_date']:
            start_date = date.fromisoformat(options['start_date'])
        else:
            today = date.today()
            days_ahead = 7 - today.weekday()  # Monday is 0
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            start_date = today + timedelta(days_ahead)
        
        self.stdout.write(f'🗓️ GENERATING {weeks} WEEK(S) OF SCHEDULES')
        self.stdout.write(f'📅 Starting from: {start_date} (Monday)')
        self.stdout.write('=' * 60)
        
        # Clear existing shifts in the date range
        end_date = start_date + timedelta(weeks=weeks)
        Shift.objects.filter(date__range=[start_date, end_date]).delete()
        
        # Get shift types
        day_shift = ShiftType.objects.get(name='DAY')
        night_shift = ShiftType.objects.get(name='NIGHT')
        
        care_units = Unit.objects.exclude(name='ADMIN')
        
        for week in range(weeks):
            week_start = start_date + timedelta(weeks=week)
            self.stdout.write(f'\\n📋 WEEK {week + 1}: {week_start}')
            self.stdout.write('-' * 40)
            
            # Generate shifts for each day of the week
            for day in range(7):  # Monday to Sunday
                current_date = week_start + timedelta(days=day)
                day_name = current_date.strftime('%A')
                
                self.stdout.write(f'\\n{day_name} {current_date}:')
                
                # For each unit, assign staff for day and night shifts
                for unit in care_units:
                    self.generate_unit_shifts(unit, current_date, day_shift, night_shift)
        
        # Generate summary
        self.generate_schedule_summary(start_date, end_date)
        
        self.stdout.write(f'\\n✅ Schedule generation complete!')
        self.stdout.write(f'📊 Generated schedules for {weeks} weeks starting {start_date}')

    def generate_unit_shifts(self, unit, shift_date, day_shift, night_shift):
        """Generate day and night shifts for a specific unit on a specific date"""
        
        # Get available staff for this unit
        unit_staff = User.objects.filter(
            unit=unit,
            is_active=True,
            role__name__in=['SCW', 'SCA', 'SSCW']
        )
        
        if unit.name == 'DEMENTIA':
            # Dementia unit: 1 SCW + 3 SCA (day), 1 SCW + 2 SCA (night)
            day_scw_needed = 1
            day_sca_needed = 3
            night_scw_needed = 1
            night_sca_needed = 2
        else:
            # Standard units: 1 SCW + 2 SCA (day), 1 SCW + 1 SCA (night)
            day_scw_needed = 1
            day_sca_needed = 2
            night_scw_needed = 1
            night_sca_needed = 1
        
        # Assign day shifts
        day_shifts = self.assign_shifts_for_period(
            unit_staff, shift_date, day_shift, 
            day_scw_needed, day_sca_needed, unit
        )
        
        # Assign night shifts
        night_shifts = self.assign_shifts_for_period(
            unit_staff, shift_date, night_shift,
            night_scw_needed, night_sca_needed, unit
        )
        
        # Print assignments
        if day_shifts or night_shifts:
            print(f'  🏢 {unit.get_name_display()}:')
            if day_shifts:
                print(f'    🌅 Day: {len(day_shifts)} staff - {[s.user.sap for s in day_shifts]}')
            if night_shifts:
                print(f'    🌙 Night: {len(night_shifts)} staff - {[s.user.sap for s in night_shifts]}')

    def assign_shifts_for_period(self, unit_staff, shift_date, shift_type, scw_needed, sca_needed, unit):
        """Assign staff to shifts based on requirements and availability"""
        
        # Filter by shift preference and role
        available_scw = unit_staff.filter(
            role__name__in=['SCW', 'SSCW'],
            shift_preference=shift_type.name
        )
        available_sca = unit_staff.filter(
            role__name='SCA',
            shift_preference=shift_type.name
        )
        
        # Check who hasn't exceeded their weekly limit
        week_start = shift_date - timedelta(days=shift_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        eligible_scw = []
        for staff in available_scw:
            current_shifts = Shift.objects.filter(
                user=staff,
                date__range=[week_start, week_end]
            ).count()
            if current_shifts < staff.shifts_per_week:
                eligible_scw.append(staff)
        
        eligible_sca = []
        for staff in available_sca:
            current_shifts = Shift.objects.filter(
                user=staff,
                date__range=[week_start, week_end]
            ).count()
            if current_shifts < staff.shifts_per_week:
                eligible_sca.append(staff)
        
        # Randomly assign available staff
        assigned_shifts = []
        
        # Assign SCW/SSCW
        scw_to_assign = min(scw_needed, len(eligible_scw))
        if scw_to_assign > 0:
            selected_scw = random.sample(eligible_scw, scw_to_assign)
            for staff in selected_scw:
                shift = Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=shift_type,
                    date=shift_date,
                    status='SCHEDULED'
                )
                assigned_shifts.append(shift)
        
        # Assign SCA
        sca_to_assign = min(sca_needed, len(eligible_sca))
        if sca_to_assign > 0:
            selected_sca = random.sample(eligible_sca, sca_to_assign)
            for staff in selected_sca:
                shift = Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=shift_type,
                    date=shift_date,
                    status='SCHEDULED'
                )
                assigned_shifts.append(shift)
        
        return assigned_shifts

    def generate_schedule_summary(self, start_date, end_date):
        """Generate a summary of the created schedules"""
        
        self.stdout.write(f'\\n📊 SCHEDULE SUMMARY')
        self.stdout.write('=' * 50)
        
        total_shifts = Shift.objects.filter(date__range=[start_date, end_date]).count()
        self.stdout.write(f'Total shifts scheduled: {total_shifts}')
        
        # Summary by role
        for role_name in ['SSCW', 'SCW', 'SCA']:
            role_shifts = Shift.objects.filter(
                date__range=[start_date, end_date],
                user__role__name=role_name
            ).count()
            self.stdout.write(f'{role_name} shifts: {role_shifts}')
        
        # Summary by shift type
        day_shifts = Shift.objects.filter(
            date__range=[start_date, end_date],
            shift_type__name='DAY'
        ).count()
        night_shifts = Shift.objects.filter(
            date__range=[start_date, end_date],
            shift_type__name='NIGHT'
        ).count()
        
        self.stdout.write(f'\\nDay shifts: {day_shifts}')
        self.stdout.write(f'Night shifts: {night_shifts}')
        
        # Check coverage
        care_units = Unit.objects.exclude(name='ADMIN')
        date_range = []
        current = start_date
        while current < end_date:
            date_range.append(current)
            current += timedelta(days=1)
        
        self.stdout.write(f'\\n🎯 COVERAGE CHECK:')
        for unit in care_units:
            unit_coverage = 0
            for shift_date in date_range:
                day_coverage = Shift.objects.filter(
                    unit=unit, date=shift_date, shift_type__name='DAY'
                ).count()
                night_coverage = Shift.objects.filter(
                    unit=unit, date=shift_date, shift_type__name='NIGHT'
                ).count()
                if day_coverage > 0 and night_coverage > 0:
                    unit_coverage += 1
            
            coverage_percent = round((unit_coverage / len(date_range)) * 100, 1)
            status = '✅' if coverage_percent >= 90 else '⚠️' if coverage_percent >= 70 else '❌'
            self.stdout.write(f'{status} {unit.get_name_display()}: {coverage_percent}% coverage')