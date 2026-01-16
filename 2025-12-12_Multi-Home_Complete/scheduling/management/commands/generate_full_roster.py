from django.core.management.base import BaseCommand
from django.utils import timezone
from scheduling.models import User, Unit, ShiftType, Shift, Role
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Generate proper 6-week rotation roster with correct shift distribution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date in YYYY-MM-DD format (default: this Monday)'
        )

    def handle(self, *args, **options):
        # Calculate start date (this Monday if not specified)
        if options['start_date']:
            start_date = date.fromisoformat(options['start_date'])
        else:
            today = date.today()
            days_back = today.weekday()  # Monday is 0
            start_date = today - timedelta(days_back)
        
        self.stdout.write(f'🗓️ GENERATING 6-WEEK ROTATION ROSTER')
        self.stdout.write(f'📅 Starting from: {start_date} (Monday)')
        self.stdout.write('=' * 60)
        
        # Clear existing shifts in the 6-week range
        end_date = start_date + timedelta(weeks=6)
        Shift.objects.filter(date__range=[start_date, end_date]).delete()
        
        # Get shift types
        shift_types = {
            'DAY_SENIOR': ShiftType.objects.get(name='DAY_SENIOR'),
            'DAY_ASSISTANT': ShiftType.objects.get(name='DAY_ASSISTANT'),
            'NIGHT_SENIOR': ShiftType.objects.get(name='NIGHT_SENIOR'),
            'NIGHT_ASSISTANT': ShiftType.objects.get(name='NIGHT_ASSISTANT'),
        }
        
        # Get all care units (excluding admin)
        care_units = list(Unit.objects.exclude(name='ADMIN').order_by('name'))
        self.stdout.write(f'🏢 Care Units: {[unit.name for unit in care_units]}')
        
        # 6-week rotation pattern for teams
        rotation_pattern = [
            # Week 1: Team A (Sun-Tue), Team B (Wed-Thu), Team C (Fri-Sat)
            ['A', 'A', 'A', 'B', 'B', 'C', 'C'],  # Week 1
            ['B', 'B', 'B', 'C', 'C', 'A', 'A'],  # Week 2
            ['C', 'C', 'C', 'A', 'A', 'B', 'B'],  # Week 3
            ['A', 'A', 'A', 'B', 'B', 'C', 'C'],  # Week 4
            ['B', 'B', 'B', 'C', 'C', 'A', 'A'],  # Week 5
            ['C', 'C', 'C', 'A', 'A', 'B', 'B'],  # Week 6
        ]
        
        total_shifts_created = 0
        
        # Generate 6 weeks of schedules
        for week in range(6):
            week_start = start_date + timedelta(weeks=week)
            week_pattern = rotation_pattern[week]
            
            self.stdout.write(f'\\n📋 WEEK {week + 1}: {week_start}')
            self.stdout.write(f'   Pattern: {week_pattern}')
            self.stdout.write('-' * 40)
            
            # Generate shifts for each day of the week
            for day in range(7):  # Monday=0 to Sunday=6
                current_date = week_start + timedelta(days=day)
                active_team = week_pattern[day]
                
                day_name = current_date.strftime('%A')
                self.stdout.write(f'\\n{day_name} {current_date} - Team {active_team}:')
                
                # For each unit, assign the active team's staff
                for unit in care_units:
                    shifts_today = self.generate_unit_shifts(
                        unit, current_date, active_team, shift_types
                    )
                    total_shifts_created += shifts_today
        
        self.stdout.write(f'\\n✅ 6-WEEK ROTATION COMPLETE!')
        self.stdout.write(f'📊 Total shifts created: {total_shifts_created}')
        self.stdout.write(f'📅 Period: {start_date} to {end_date}')
        
        # Generate summary
        self.generate_summary()

    def generate_unit_shifts(self, unit, shift_date, active_team, shift_types):
        """Generate day and night shifts for a unit on a specific date for the active team"""
        
        # Get staff from the active team for this unit
        team_staff = User.objects.filter(
            unit=unit,
            team=active_team,
            is_active=True,
            role__name__in=['SCW', 'SCA', 'SSCW']
        )
        
        if not team_staff.exists():
            print(f'  ⚠️ {unit.name}: No Team {active_team} staff available')
            return 0
        
        shifts_created = 0
        
        # Determine staffing requirements
        if unit.name == 'DEMENTIA':
            # Dementia unit: 1 SCW + 3 SCA (day), 1 SCW + 2 SCA (night)
            day_requirements = {'SCW': 1, 'SCA': 3}
            night_requirements = {'SCW': 1, 'SCA': 2}
        else:
            # Standard units: 1 SCW + 2 SCA (day), 1 SCW + 1 SCA (night)
            day_requirements = {'SCW': 1, 'SCA': 2}
            night_requirements = {'SCW': 1, 'SCA': 1}
        
        # Assign day shifts
        day_shifts = self.assign_shifts_by_preference(
            team_staff, shift_date, shift_types['DAY_SENIOR'], 
            shift_types['DAY_ASSISTANT'], day_requirements, unit
        )
        shifts_created += len(day_shifts)
        
        # Assign night shifts
        night_shifts = self.assign_shifts_by_preference(
            team_staff, shift_date, shift_types['NIGHT_SENIOR'],
            shift_types['NIGHT_ASSISTANT'], night_requirements, unit
        )
        shifts_created += len(night_shifts)
        
        # Print assignments
        staff_assigned = []
        if day_shifts:
            day_staff = [f"{s.user.sap}({s.user.role.name})" for s in day_shifts]
            staff_assigned.extend([f"Day: {', '.join(day_staff)}"])
        if night_shifts:
            night_staff = [f"{s.user.sap}({s.user.role.name})" for s in night_shifts]
            staff_assigned.extend([f"Night: {', '.join(night_staff)}"])
        
        if staff_assigned:
            print(f'  🏢 {unit.name}: {" | ".join(staff_assigned)}')
        
        return shifts_created

    def assign_shifts_by_preference(self, team_staff, shift_date, senior_shift_type, assistant_shift_type, requirements, unit):
        """Assign staff to shifts based on their role and shift preferences"""
        
        created_shifts = []
        
        # Get staff by role and shift preference
        scw_staff = team_staff.filter(role__name__in=['SCW', 'SSCW'])
        sca_staff = team_staff.filter(role__name='SCA')
        
        # Check if this is a day or night shift
        is_day = 'DAY' in senior_shift_type.name
        shift_pref = 'DAY' if is_day else 'NIGHT'
        
        # Filter by shift preference
        available_scw = scw_staff.filter(shift_preference=shift_pref)
        available_sca = sca_staff.filter(shift_preference=shift_pref)
        
        # Assign SCW/SSCW staff (senior roles)
        scw_needed = requirements.get('SCW', 0)
        if scw_needed > 0 and available_scw.exists():
            # Randomly select from available SCW staff
            selected_scw = random.sample(
                list(available_scw), 
                min(scw_needed, available_scw.count())
            )
            
            for staff in selected_scw:
                shift = Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=senior_shift_type,
                    date=shift_date,
                    status='SCHEDULED'
                )
                created_shifts.append(shift)
        
        # Assign SCA staff (assistant roles)
        sca_needed = requirements.get('SCA', 0)
        if sca_needed > 0 and available_sca.exists():
            # Randomly select from available SCA staff
            selected_sca = random.sample(
                list(available_sca),
                min(sca_needed, available_sca.count())
            )
            
            for staff in selected_sca:
                shift = Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=assistant_shift_type,
                    date=shift_date,
                    status='SCHEDULED'
                )
                created_shifts.append(shift)
        
        return created_shifts

    def generate_summary(self):
        """Generate a summary of the created schedule"""
        
        self.stdout.write(f'\\n📊 ROSTER SUMMARY')
        self.stdout.write('=' * 50)
        
        # Summary by unit
        care_units = Unit.objects.exclude(name='ADMIN')
        
        for unit in care_units:
            unit_shifts = Shift.objects.filter(unit=unit)
            day_shifts = unit_shifts.filter(shift_type__name__contains='DAY').count()
            night_shifts = unit_shifts.filter(shift_type__name__contains='NIGHT').count()
            
            self.stdout.write(f'🏢 {unit.get_name_display()}:')
            self.stdout.write(f'   Day shifts: {day_shifts}')
            self.stdout.write(f'   Night shifts: {night_shifts}')
            self.stdout.write(f'   Total: {unit_shifts.count()}')
        
        # Summary by staff
        self.stdout.write(f'\\n👥 STAFF WORKLOAD VERIFICATION:')
        sample_staff = User.objects.filter(
            is_active=True, 
            role__name__in=['SCW', 'SCA', 'SSCW']
        )[:10]
        
        for staff in sample_staff:
            total_shifts = Shift.objects.filter(user=staff).count()
            expected_per_week = staff.shifts_per_week
            expected_total = expected_per_week * 6  # 6 weeks
            
            status = '✅' if total_shifts <= expected_total else '⚠️'
            self.stdout.write(f'   {status} {staff.sap} ({staff.role.name}): {total_shifts}/{expected_total} shifts')
        
        # Name lists for generating staff
        first_names = [
            'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
            'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica'
        ]
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores'
        ]
        
        # Generate staff for rota-scheduled roles only
        roles_to_generate = [
            ('SSCW', 24),  # 3 teams per unit × 8 units
            ('SCW', 48),   # Day/night shifts × 8 units × 3 teams
            ('SCA', 78),   # Day/night shifts with enhanced dementia × 3 teams
        ]
        
        generated_staff = []
        sap_counter = {'SSW': 1, 'SCW': 1, 'SCA': 1}
        
        for role_name, count in roles_to_generate:
            try:
                role = Role.objects.get(name=role_name)
                self.stdout.write(f'Generating {count} staff for {role.get_name_display()}...')
                
                # Determine SAP prefix
                if role_name == 'SSCW':
                    prefix = 'SSW'
                else:
                    prefix = role_name
                
                for i in range(count):
                    # Generate unique name combination
                    first_name = random.choice(first_names)
                    last_name = random.choice(last_names)
                    
                    # Generate SAP number
                    sap = f"{prefix}{sap_counter[prefix]:03d}"
                    sap_counter[prefix] += 1
                    
                    # Generate unique email
                    base_email = f"{first_name.lower()}.{last_name.lower()}"
                    email = f"{base_email}@staffrota.com"
                    
                    # Handle duplicate emails
                    counter = 1
                    while User.objects.filter(email=email).exists():
                        email = f"{base_email}{counter}@staffrota.com"
                        counter += 1
                    
                    # Generate phone (optional)
                    phone = f"07{random.randint(100000000, 999999999)}" if random.choice([True, False]) else None
                    
                    # Check if staff already exists
                    if not User.objects.filter(sap=sap).exists():
                        staff = User.objects.create(
                            sap=sap,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            phone_number=phone,
                            role=role,
                            annual_leave_allowance=28,
                            is_active=True
                        )
                        staff.set_password('staff123')
                        staff.save()
                        
                        generated_staff.append(staff)
                        
            except Role.DoesNotExist:
                self.stdout.write(f'Role {role_name} does not exist, skipping...')
                        
        self.stdout.write(f'Generated {len(generated_staff)} new staff members.')
        
        # Now generate sample shifts for the next 4 weeks
        self.generate_sample_shifts()
        
        self.stdout.write(self.style.SUCCESS('Successfully generated full staff roster and sample shifts!'))
    
    def generate_sample_shifts(self):
        """Generate sample shifts for the next 4 weeks"""
        self.stdout.write('Generating sample shifts...')
        
        try:
            # Get shift types and units
            day_shift = ShiftType.objects.get(name='DAY')
            night_shift = ShiftType.objects.get(name='NIGHT')
            long_day_shift = ShiftType.objects.get(name='LONG_DAY')
            
            units = Unit.objects.all()
            
            # Get staff by role
            scw_staff = list(User.objects.filter(role__name='SCW', is_active=True))
            sca_staff = list(User.objects.filter(role__name='SCA', is_active=True))
            
            if not scw_staff or not sca_staff:
                self.stdout.write('Not enough staff to generate shifts')
                return
            
            # Generate shifts for next 4 weeks
            start_date = timezone.now().date()
            shifts_created = 0
            
            for day_offset in range(28):  # 4 weeks
                shift_date = start_date + timedelta(days=day_offset)
                
                for unit in units:
                    if unit.name == 'ADMIN':  # Skip admin unit for care shifts
                        continue
                        
                    # Determine minimum staffing for this unit
                    scw_needed = 1  # 1 SCW per unit
                    sca_needed = 2  # 2 SCA per unit (3 for dementia)
                    
                    if unit.name == 'DEMENTIA':
                        sca_needed = 3
                    
                    # Create day shifts - SCW with handover
                    if scw_staff:
                        scw = random.choice(scw_staff)
                        shift = Shift.objects.create(
                            user=scw,
                            unit=unit,
                            shift_type=long_day_shift,
                            date=shift_date,
                            status='SCHEDULED'
                        )
                        shifts_created += 1
                    
                    # SCA day shifts
                    available_sca = sca_staff.copy()
                    for i in range(min(sca_needed, len(available_sca))):
                        sca = random.choice(available_sca)
                        available_sca.remove(sca)
                        
                        shift = Shift.objects.create(
                            user=sca,
                            unit=unit,
                            shift_type=day_shift,
                            date=shift_date,
                            status='SCHEDULED'
                        )
                        shifts_created += 1
                    
                    # Create night shifts - reduced staffing (1 SCW + 1 SCA per unit)
                    if scw_staff:
                        scw = random.choice(scw_staff)
                        shift = Shift.objects.create(
                            user=scw,
                            unit=unit,
                            shift_type=night_shift,
                            date=shift_date,
                            status='SCHEDULED'
                        )
                        shifts_created += 1
                    
                    # SCA night shifts (1 per unit, except dementia which gets 2)
                    night_sca_needed = 2 if unit.name == 'DEMENTIA' else 1
                    available_sca = sca_staff.copy()
                    for i in range(min(night_sca_needed, len(available_sca))):
                        sca = random.choice(available_sca)
                        available_sca.remove(sca)
                        
                        shift = Shift.objects.create(
                            user=sca,
                            unit=unit,
                            shift_type=night_shift,
                            date=shift_date,
                            status='SCHEDULED'
                        )
                        shifts_created += 1
            
            self.stdout.write(f'Generated {shifts_created} sample shifts for 4 weeks.')
            
        except ShiftType.DoesNotExist as e:
            self.stdout.write(f'Shift type not found: {e}')
        except Exception as e:
            self.stdout.write(f'Error generating shifts: {e}')