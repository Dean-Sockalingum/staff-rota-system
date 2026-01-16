"""
Management command to fix Week 3 rota data for Team A
Corrects the shift assignments based on the provided spreadsheet data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Shift, User, ShiftType
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Fix Week 3 rota data for Team A - corrects shift assignments'

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
        
        self.stdout.write(self.style.SUCCESS('\n🔧 Starting Week 3 Rota Correction...'))
        self.stdout.write('')
        
        # Define Week 3 date range: December 16-18, 2025 (Tuesday-Thursday)
        week3_start = datetime(2025, 12, 16).date()  # Tuesday
        # For 3 days: Tue, Wed, Thu
        # 35-hour staff: Tue/Wed/Thu (so days: [True, True, True])
        # 24-hour staff: Wed/Thu (so days: [False, True, True])
        staff_schedule = {
            # 35-hour staff (Tue/Wed/Thu)
            'SCW1080': {'days': [True, True, True]},
            'SCW1081': {'days': [True, True, True]},
            'SCA1084': {'days': [True, True, True]},
            'SCA1085': {'days': [True, True, True]},
            'SCA1086': {'days': [True, True, True]},
            'SCA1087': {'days': [True, True, True]},
            'SCA1088': {'days': [True, True, True]},
            'SCA1090': {'days': [True, True, True]},
            'SCA1091': {'days': [True, True, True]},
            'SCA1092': {'days': [True, True, True]},
            'SCA1093': {'days': [True, True, True]},
            'SCA1094': {'days': [True, True, True]},
            'SCA1095': {'days': [True, True, True]},
            # 24-hour staff (Wed/Thu)
            'SCW1082': {'days': [False, True, True]},
            'SCW1083': {'days': [False, True, True]},
            'SCA1096': {'days': [False, True, True]},
            'SCA1097': {'days': [False, True, True]},
            'SCA1098': {'days': [False, True, True]},
            'SCA1099': {'days': [False, True, True]},
            'SCA1100': {'days': [False, True, True]},
            'SCA1101': {'days': [False, True, True]},
            'SCA1102': {'days': [False, True, True]},
            'SCA1103': {'days': [False, True, True]},
            'SCA1104': {'days': [False, True, True]},
            'SCA1105': {'days': [False, True, True]},
            'SCA1106': {'days': [False, True, True]},
            'SCA1107': {'days': [False, True, True]},
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
                    shift_date = week3_start + timedelta(days=day_index)
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
            self.stdout.write(self.style.WARNING('Shifts that need to be ADDED:'))
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
            self.stdout.write(self.style.SUCCESS(f'✅ Team A Week 3 Rota Correction Complete!'))
            self.stdout.write(self.style.SUCCESS(f'Total changes made: {corrections_made}'))
        else:
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(self.style.SUCCESS('🔍 DRY RUN COMPLETE - No changes made'))
            if shifts_to_add or shifts_to_remove:
                self.stdout.write(self.style.WARNING(f'Run with --commit to make {len(shifts_to_add) + len(shifts_to_remove)} changes'))
        
        if errors:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(f'⚠️  {len(errors)} issue(s) require manual attention:'))
            for error in errors:
                self.stdout.write(self.style.WARNING(f'   • {error}'))
