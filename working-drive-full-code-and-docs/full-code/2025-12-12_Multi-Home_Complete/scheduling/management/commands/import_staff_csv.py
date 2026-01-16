"""
Enhanced CSV Import Command for Staff Data

This command imports complete staff records from a CSV file, including:
- Basic details (name, email, phone)
- Role and permissions
- Unit and team assignments
- Shift preferences
- Contracted hours and annual leave
- Active status

Usage:
    python3 manage.py import_staff_csv path/to/staff_file.csv

CSV Format:
    SAP,First_Name,Last_Name,Email,Phone,Role,Home_Unit,Team,Shift_Preference,Contracted_Hours,Annual_Leave_Days,Is_Active,Is_Management

Example:
    STAFF001,Jane,Smith,jane@example.com,01234567890,SSCW,BLUE,A,DAY_SENIOR,35,28,TRUE,FALSE
"""

import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import User, Role, Unit
from staff_records.models import StaffProfile, AnnualLeaveEntitlement
from datetime import date
from decimal import Decimal


class Command(BaseCommand):
    help = 'Import staff data from CSV file with full profile support'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_path',
            type=str,
            help='Path to the staff CSV file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without saving to database'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            default=True,
            help='Update existing staff records (default: True)'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        dry_run = options['dry_run']
        update_existing = options['update_existing']

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be saved\n'))

        # Statistics
        stats = {
            'created': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0
        }

        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate headers
                required_fields = [
                    'SAP', 'First_Name', 'Last_Name', 'Email', 'Role',
                    'Home_Unit', 'Team', 'Shift_Preference', 'Contracted_Hours',
                    'Annual_Leave_Days', 'Is_Active'
                ]
                
                missing_fields = [f for f in required_fields if f not in reader.fieldnames]
                if missing_fields:
                    self.stderr.write(
                        self.style.ERROR(
                            f'❌ Missing required columns: {", ".join(missing_fields)}'
                        )
                    )
                    return

                self.stdout.write(self.style.SUCCESS('✅ CSV format validated\n'))
                
                # Process each row
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        result = self._process_staff_row(row, update_existing, dry_run)
                        stats[result] += 1
                        
                        # Show progress
                        if result == 'created':
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✅ Created: {row["First_Name"]} {row["Last_Name"]} ({row["SAP"]})'
                                )
                            )
                        elif result == 'updated':
                            self.stdout.write(
                                self.style.WARNING(
                                    f'🔄 Updated: {row["First_Name"]} {row["Last_Name"]} ({row["SAP"]})'
                                )
                            )
                        elif result == 'skipped':
                            self.stdout.write(
                                f'⏭️  Skipped: {row["SAP"]} (already exists, use --update-existing to modify)'
                            )
                            
                    except Exception as e:
                        stats['errors'] += 1
                        self.stderr.write(
                            self.style.ERROR(
                                f'❌ Row {row_num} - {row.get("SAP", "UNKNOWN")}: {str(e)}'
                            )
                        )

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'❌ File not found: {csv_path}'))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Error reading CSV: {str(e)}'))
            return

        # Print summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 IMPORT SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'✅ Created:  {stats["created"]} staff')
        self.stdout.write(f'🔄 Updated:  {stats["updated"]} staff')
        self.stdout.write(f'⏭️  Skipped:  {stats["skipped"]} staff')
        self.stdout.write(f'❌ Errors:   {stats["errors"]} rows')
        self.stdout.write(f'📈 Total:    {stats["created"] + stats["updated"]} staff imported successfully')
        
        if dry_run:
            self.stdout.write('\n' + self.style.WARNING('🔍 DRY RUN - No changes were saved'))
        else:
            self.stdout.write('\n' + self.style.SUCCESS('✅ Import complete!'))

    def _process_staff_row(self, row, update_existing, dry_run):
        """Process a single staff row from CSV"""
        
        # Extract and validate data
        sap = row['SAP'].strip()
        first_name = row['First_Name'].strip()
        last_name = row['Last_Name'].strip()
        email = row['Email'].strip()
        phone = row.get('Phone', '').strip()
        role_name = row['Role'].strip()
        home_unit_name = row['Home_Unit'].strip()
        team = row['Team'].strip().upper()
        shift_pref = row['Shift_Preference'].strip()
        contracted_hours = Decimal(str(row['Contracted_Hours']))
        annual_leave_days = int(row['Annual_Leave_Days'])
        is_active = row['Is_Active'].strip().upper() in ('TRUE', '1', 'YES', 'Y')
        is_management = row.get('Is_Management', 'FALSE').strip().upper() in ('TRUE', '1', 'YES', 'Y')

        # Validate required fields
        if not sap or not first_name or not last_name or not email:
            raise ValueError('Missing required fields (SAP, First_Name, Last_Name, or Email)')

        # Get or create Role
        role, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={
                'description': f'{role_name} role',
                'is_management': is_management
            }
        )

        # Get or create Unit
        unit, _ = Unit.objects.get_or_create(
            name=home_unit_name,
            defaults={
                'description': f'{home_unit_name} unit',
                'min_day_staff': 2,
                'min_night_staff': 2
            }
        )

        # Validate team
        if team not in ('A', 'B', 'C'):
            raise ValueError(f'Invalid team: {team} (must be A, B, or C)')

        # Validate shift preference
        valid_prefs = ['DAY_SENIOR', 'DAY_ASSISTANT', 'NIGHT_SENIOR', 'NIGHT_ASSISTANT']
        if shift_pref not in valid_prefs:
            raise ValueError(f'Invalid shift preference: {shift_pref}')

        if dry_run:
            # Just check if exists
            exists = User.objects.filter(sap=sap).exists()
            return 'updated' if exists else 'created'

        # Create or update User
        user, created = User.objects.get_or_create(
            sap=sap,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone,
                'role': role,
                'home_unit': unit,
                'unit': unit,  # Current unit same as home unit initially
                'team': team,
                'shift_preference': shift_pref,
                'is_active': is_active,
                'is_staff': is_management,
                'annual_leave_allowance': annual_leave_days,
            }
        )

        if not created and update_existing:
            # Update existing user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone_number = phone
            user.role = role
            user.home_unit = unit
            user.unit = unit
            user.team = team
            user.shift_preference = shift_pref
            user.is_active = is_active
            user.is_staff = is_management
            user.annual_leave_allowance = annual_leave_days
            user.save()

        # Set default password if new user
        if created:
            user.set_password('changeme123')  # Force change on first login
            user.save()

        # Create or update StaffProfile
        profile, profile_created = StaffProfile.objects.get_or_create(
            user=user,
            defaults={
                'contracted_hours_per_week': contracted_hours,
                'employment_status': 'ACTIVE' if is_active else 'INACTIVE',
                'start_date': date.today(),
            }
        )

        if not profile_created:
            profile.contracted_hours_per_week = contracted_hours
            profile.employment_status = 'ACTIVE' if is_active else 'INACTIVE'
            profile.save()

        # Create Annual Leave Entitlement for current year
        current_year = date.today().year
        leave_year_start = date(current_year, 1, 1)
        leave_year_end = date(current_year, 12, 31)

        # Calculate total hours based on shift pattern
        # 35hr staff work 5 days @ 7hrs = 25.5 days @ 11.66hrs
        # 24hr staff work 2 shifts/week @ 12hrs = 17 days @ 12hrs
        if contracted_hours >= 30:
            # Full-time: 28 days @ ~11.66 hours = 297.5 hours (rounded)
            total_hours = Decimal('297.5')
        else:
            # Part-time: 17 days @ 12 hours = 204 hours
            total_hours = Decimal('204.0')

        entitlement, ent_created = AnnualLeaveEntitlement.objects.get_or_create(
            profile=profile,
            leave_year_start=leave_year_start,
            defaults={
                'leave_year_end': leave_year_end,
                'contracted_hours_per_week': contracted_hours,
                'total_entitlement_hours': total_hours,
                'hours_used': Decimal('0.0'),
                'hours_pending': Decimal('0.0'),
                'carryover_hours': Decimal('0.0'),
            }
        )

        if not ent_created:
            entitlement.contracted_hours_per_week = contracted_hours
            entitlement.total_entitlement_hours = total_hours
            entitlement.save()

        return 'created' if created else 'updated'
