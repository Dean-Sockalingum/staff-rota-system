"""
Management command to fix Team C Week 1 rota data
Corrects the shift assignments to match Team A Week 3 pattern:
- 35-hour staff work Tue/Wed/Thu
- 24-hour staff work Wed/Thu
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, User, ShiftType
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Fix Team C Week 1 rota - ensure correct Tue/Wed/Thu pattern'

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Actually make the changes (default is dry-run mode)',
        )

    def handle(self, *args, **options):
        dry_run = not options['commit']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made'))
            self.stdout.write(self.style.WARNING('Use --commit flag to actually make changes'))
        else:
            self.stdout.write(self.style.SUCCESS('✏️ COMMIT MODE - Changes will be saved'))
        
        self.stdout.write(self.style.SUCCESS('\n🔧 Starting Team C Week 1 Rota Correction...'))
        self.stdout.write('')
        
        # Define Team C Week 1 date range: December 2-4, 2025 (Tue/Wed/Thu)
        week1_start = datetime(2025, 12, 2).date()  # Tuesday
        
        # Team C Night Shift Staff with corrected schedule
        # Based on Team A pattern: SCW + first batch of SCA = 35hr, later SCA = 24hr
        # Days: [Tue, Wed, Thu]
        staff_schedule = {
            # 35-hour staff (Tue/Wed/Thu) - SCW and first batch of SCA
            'SCW1135': {'days': [True, True, True]},   # Harry Hall
            'SCW1136': {'days': [True, True, True]},   # Isabel Rivera
            'SCW1137': {'days': [True, True, True]},   # Jacob Campbell
            'SCW1138': {'days': [True, True, True]},   # Katie Mitchell
            'SCW1139': {'days': [True, True, True]},   # Leo Carter
            'SCW1140': {'days': [True, True, True]},   # Megan Roberts
            'SCA1141': {'days': [True, True, True]},   # Poppy Saeed
            'SCA1142': {'days': [True, True, True]},   # Quentin Tarant
            'SCA1143': {'days': [True, True, True]},   # Ruby Rubia
            'SCA1144': {'days': [True, True, True]},   # Sebastian Coen
            'SCA1145': {'days': [True, True, True]},   # Taylor Swifty
            'SCA1146': {'days': [True, True, True]},   # Janice Evans
            'SCA1147': {'days': [True, True, True]},   # Victor Turner
            
            # 24-hour staff (Wed/Thu only)
            'SCA1148': {'days': [False, True, True]},  # Zoe Cooper
            'SCA1149': {'days': [False, True, True]},  # Adam Phillips
            'SCA1150': {'days': [False, True, True]},  # Beth Aimes
            'SCA1151': {'days': [False, True, True]},  # Natasha Kaplinski
            'SCA1152': {'days': [False, True, True]},  # Abby Rhodes
            'SCA1153': {'days': [False, True, True]},  # David Morris
            'SCA1154': {'days': [False, True, True]},  # Emily Rogers
            'SCA1155': {'days': [False, True, True]},  # Frank Cox
            'SCA1156': {'days': [False, True, True]},  # Grace Ward
            'SCA1157': {'days': [False, True, True]},  # Henry Gray
            'SCA1158': {'days': [False, True, True]},  # Ivy Bell
            'SCA1159': {'days': [False, True, True]},  # Angela Ripton
            'SCA1160': {'days': [False, True, True]},  # Kyle Son Ji
            'SCA1161': {'days': [False, True, True]},  # Precious Richards
        }
        
        corrections_made = 0
        errors = []
        shifts_to_add = []
        shifts_to_remove = []
        correct_shifts = []
        
        # Get Night shift type
        try:
            night_shift_type = ShiftType.objects.filter(name__icontains='NIGHT').first()
            if not night_shift_type:
                self.stdout.write(self.style.ERROR('❌ NIGHT shift type not found'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error getting shift type: {e}'))
            return
        
        # First pass: identify what needs to change
        for sap_number, schedule in staff_schedule.items():
            try:
                user = User.objects.get(sap=sap_number)
                
                for day_index, should_work in enumerate(schedule['days']):
                    shift_date = week1_start + timedelta(days=day_index)
                    day_name = ['Tuesday', 'Wednesday', 'Thursday'][day_index]
                    
                    shifts = Shift.objects.filter(
                        user=user,
                        date=shift_date,
                        shift_type__name__icontains='NIGHT'
                    )
                    
                    if should_work and not shifts.exists():
                        shifts_to_add.append((user, shift_date, day_name, sap_number))
                    elif not should_work and shifts.exists():
                        for shift in shifts:
                            shifts_to_remove.append((user, shift_date, day_name, shift))
                    elif should_work and shifts.exists():
                        correct_shifts.append((user, shift_date, day_name))
                        
            except User.DoesNotExist:
                errors.append(f'User with SAP {sap_number} not found')
            except Exception as e:
                errors.append(f'Error processing {sap_number}: {str(e)}')
        
        # Display summary
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('📊 ANALYSIS RESULTS:'))
        self.stdout.write(f'  ✓ Correct shifts: {len(correct_shifts)}')
        self.stdout.write(self.style.WARNING(f'  ➕ Shifts to add: {len(shifts_to_add)}'))
        self.stdout.write(self.style.ERROR(f'  ❌ Shifts to remove: {len(shifts_to_remove)}'))
        
        if errors:
            self.stdout.write(self.style.ERROR(f'  ⚠️  Errors: {len(errors)}'))
        self.stdout.write('')
        
        if shifts_to_add:
            self.stdout.write(self.style.WARNING('Shifts that need to be ADDED (Tuesday for 35-hour staff):'))
            for user, date, day, sap in shifts_to_add[:10]:
                self.stdout.write(f'  ➕ {sap} ({user.first_name} {user.last_name}): {day} {date}')
            if len(shifts_to_add) > 10:
                self.stdout.write(f'  ... and {len(shifts_to_add) - 10} more')
            self.stdout.write('')
        
        if shifts_to_remove:
            self.stdout.write(self.style.ERROR('Shifts that need to be REMOVED:'))
            for user, date, day, _ in shifts_to_remove[:10]:
                self.stdout.write(f'  ❌ {user.sap} ({user.first_name} {user.last_name}): {day} {date}')
            if len(shifts_to_remove) > 10:
                self.stdout.write(f'  ... and {len(shifts_to_remove) - 10} more')
            self.stdout.write('')
        
        if errors:
            self.stdout.write(self.style.ERROR('Errors encountered:'))
            for error in errors:
                self.stdout.write(f'  ⚠️  {error}')
            self.stdout.write('')
        
        # Make changes if not dry run
        if not dry_run and (shifts_to_add or shifts_to_remove):
            with transaction.atomic():
                # Add missing shifts
                for user, shift_date, day_name, sap in shifts_to_add:
                    Shift.objects.create(
                        user=user,
                        date=shift_date,
                        shift_type=night_shift_type,
                        unit=user.unit,
                        status='SCHEDULED'
                    )
                    corrections_made += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Added: {sap} on {day_name} {shift_date}'))
                
                # Remove incorrect shifts
                for user, shift_date, day_name, shift in shifts_to_remove:
                    shift.delete()
                    corrections_made += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Removed: {user.sap} on {day_name} {shift_date}'))
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f'✅ Team C Week 1 Rota Correction Complete!'))
            self.stdout.write(self.style.SUCCESS(f'Total changes made: {corrections_made}'))
        else:
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(self.style.SUCCESS('🔍 DRY RUN COMPLETE - No changes made'))
            if shifts_to_add or shifts_to_remove:
                self.stdout.write(self.style.WARNING(f'Run with --commit to make {len(shifts_to_add) + len(shifts_to_remove)} changes'))
