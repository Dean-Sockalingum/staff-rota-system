import csv
import os
from django.core.management.base import BaseCommand
from scheduling.models import User, Unit, Shift, ShiftType, Role
from django.db import transaction
from django.utils import timezone
from datetime import timedelta, date

class Command(BaseCommand):
    help = 'Replace all SCW and SCA day/night staff with those from CSVs and create a 3-week rota.'

    def add_arguments(self, parser):
        parser.add_argument('day_excel', type=str, help='Path to the day shift Excel file (.xlsx)')
        parser.add_argument('night_excel', type=str, help='Path to the night shift Excel file (.xlsx)')
        parser.add_argument('--start-date', type=str, help='Start date for week 1 (YYYY-MM-DD)', default=None)

    def handle(self, *args, **options):
        import pandas as pd
        day_excel = options['day_excel']
        night_excel = options['night_excel']
        start_date = options['start_date']
        if start_date:
            start_date = date.fromisoformat(start_date)
        else:
            start_date = timezone.now().date()
        self.stdout.write(self.style.WARNING(f'Using start date: {start_date}'))

        # Remove all existing SCW and SCA day/night staff and their shifts
        self.stdout.write('Deleting existing SCW and SCA staff and their shifts...')
        scw_sca_roles = ['SCW', 'SCA', 'SCW(N)', 'SCA (N)', 'SCW Days', 'SCA Days']
        staff_to_remove = User.objects.filter(role__name__in=scw_sca_roles)
        Shift.objects.filter(user__in=staff_to_remove).delete()
        staff_to_remove.delete()
        # Optionally, clear orphaned shifts
        Shift.objects.filter(user__isnull=True).delete()

        # Helper to parse and import staff from an Excel file
        def import_staff(excel_path, is_night):
            df = pd.read_excel(excel_path, engine='openpyxl')
            # Normalize column names
            df.columns = [str(c).strip() for c in df.columns]
            for idx, row in df.iterrows():
                # Skip empty or non-staff rows
                if pd.isna(row.get('SAP')):
                    continue
                sap = str(row.get('SAP')).strip()
                first = str(row.get('First')).strip()
                last = str(row.get('Surname')).strip()
                role = str(row.get('TEAM')).strip() if 'TEAM' in row else str(row.get('Role', '')).strip()
                unit_name = str(row.get('Unit')).strip()
                # Get or create unit
                unit, _ = Unit.objects.get_or_create(name=unit_name)
                # Get or create user
                user, _ = User.objects.get_or_create(sap=sap, defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': f'{sap}@example.com',
                    'role_id': None,  # Set below
                    'unit': unit,
                    'home_unit': unit,
                    'is_active': True,
                })
                # Assign role
                role_obj, _ = Role.objects.get_or_create(name=role)
                user.role = role_obj
                user.unit = unit
                user.home_unit = unit
                user.save()
                # Parse 3-week pattern and create shifts
                week_start = start_date
                for week in range(1, 4):
                    for i, day in enumerate(['SUN', 'Mon', 'TUE', 'WED', 'THU', 'FRI', 'SAT']):
                        col = f'Week {week}.{day}' if f'Week {week}.{day}' in df.columns else None
                        if not col:
                            # Try alternate naming
                            for c in df.columns:
                                if c.strip().upper() == day and f'Week {week}' in c:
                                    col = c
                                    break
                        if col and str(row.get(col)).strip() == '1':
                            shift_date = week_start + timedelta(days=(week-1)*7 + i)
                            # Find shift type
                            if is_night:
                                stype_name = 'NIGHT_SENIOR' if 'SCW' in role else 'NIGHT_ASSISTANT'
                            else:
                                stype_name = 'DAY_SENIOR' if 'SCW' in role else 'DAY_ASSISTANT'
                            stype = ShiftType.objects.get(name=stype_name)
                            # Prevent duplicate shifts
                            if not Shift.objects.filter(user=user, shift_type=stype, date=shift_date).exists():
                                Shift.objects.create(user=user, unit=unit, shift_type=stype, date=shift_date, status='SCHEDULED')

        self.stdout.write('Importing day shift staff and rota...')
        import_staff(day_excel, is_night=False)
        self.stdout.write('Importing night shift staff and rota...')
        import_staff(night_excel, is_night=True)
        self.stdout.write(self.style.SUCCESS('Staff and 3-week rota imported and replaced successfully.'))
