"""
Import real-world care plan review data from CSV

Usage:
    python3 manage.py import_careplan_data careplan_data.csv
    python3 manage.py import_careplan_data careplan_data.csv --clear  # Clear existing data first
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Resident, CarePlanReview, Unit, User
from datetime import datetime, date
import csv
import sys


class Command(BaseCommand):
    help = 'Import care plan review data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--clear', action='store_true', help='Clear existing residents and reviews before import')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        clear_existing = options['clear']

        self.stdout.write("\n" + "="*70)
        self.stdout.write("CARE PLAN REVIEW DATA IMPORT")
        self.stdout.write("="*70 + "\n")

        if clear_existing:
            self.stdout.write("⚠️  Clearing existing data...")
            Resident.objects.all().delete()
            self.stdout.write(self.style.WARNING("✓ Existing data cleared\n"))

        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                stats = {
                    'residents_created': 0,
                    'residents_existing': 0,
                    'reviews_created': 0,
                    'errors': 0
                }
                
                for row in reader:
                    try:
                        self._import_row(row, stats)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"✗ Error on row: {str(e)}"))
                        stats['errors'] += 1
                        continue

                # Print summary
                self.stdout.write("\n" + "="*70)
                self.stdout.write("IMPORT SUMMARY")
                self.stdout.write("="*70)
                self.stdout.write(f"✓ Residents created: {stats['residents_created']}")
                self.stdout.write(f"⚠ Residents existing: {stats['residents_existing']}")
                self.stdout.write(f"✓ Reviews created: {stats['reviews_created']}")
                if stats['errors'] > 0:
                    self.stdout.write(self.style.ERROR(f"✗ Errors: {stats['errors']}"))
                self.stdout.write("="*70 + "\n")

                # Print statistics by unit
                self.stdout.write("\n📊 RESIDENTS BY UNIT:")
                for unit in Unit.objects.all().order_by('name'):
                    count = Resident.objects.filter(unit=unit).count()
                    if count > 0:
                        self.stdout.write(f"  • {unit.name}: {count} residents")

                self.stdout.write(f"\n📋 TOTAL: {Resident.objects.count()} residents")
                self.stdout.write(f"📝 TOTAL: {CarePlanReview.objects.count()} reviews")

                # Show compliance overview
                self.stdout.write("\n🎯 COMPLIANCE OVERVIEW:")
                total_reviews = CarePlanReview.objects.count()
                overdue = CarePlanReview.objects.filter(status='OVERDUE').count()
                due_soon = CarePlanReview.objects.filter(status='DUE').count()
                completed = CarePlanReview.objects.filter(status='COMPLETED').count()
                
                self.stdout.write(f"  ✅ Completed: {completed} ({completed*100//total_reviews if total_reviews else 0}%)")
                self.stdout.write(f"  ⚠️  Due Soon: {due_soon}")
                self.stdout.write(f"  ❌ Overdue: {overdue}")
                self.stdout.write("")

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✗ File not found: {csv_file}"))
            sys.exit(1)

    @transaction.atomic
    def _import_row(self, row, stats):
        """Import a single row of data"""
        
        # Parse data
        unit_name = row['Unit Name'].strip()
        room_number = row['Room Number'].strip()
        initials = row['Resident Initials'].strip()
        care_plan_start = self._parse_date(row['Care Plan Start Date'])
        next_review_date = self._parse_date(row['Next 6-Month Review Date'])
        review_completed = row['Review Completed'].strip().upper() == 'TRUE'
        review_overdue = row['Review Overdue'].strip().upper() == 'TRUE'
        review_notes = row['Review Notes/Summary'].strip()
        unit_manager_name = row['Unit Manager'].strip()
        keyworker_name = row['Keyworker'].strip() if row['Keyworker'].strip() else None

        # Get or create unit
        try:
            unit = Unit.objects.get(name=unit_name)
        except Unit.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"✗ Unit not found: {unit_name}"))
            stats['errors'] += 1
            return

        # Find unit manager (SSCW/SSCWN)
        unit_manager = self._find_user_by_name(unit_manager_name, unit)
        
        # Find keyworker
        keyworker = None
        if keyworker_name:
            keyworker = self._find_user_by_name(keyworker_name, unit)

        # Generate resident ID
        resident_id = f"{unit_name[:3]}{room_number:0>2}"
        
        # Create resident name from initials
        first_name = initials[0] if len(initials) > 0 else 'Unknown'
        last_name = initials[1:] if len(initials) > 1 else 'Resident'

        # Create or get resident
        resident, created = Resident.objects.get_or_create(
            resident_id=resident_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'date_of_birth': date(1945, 1, 1),  # Placeholder
                'unit': unit,
                'room_number': room_number,
                'admission_date': care_plan_start,
                'keyworker': keyworker,
                'unit_manager': unit_manager,
            }
        )

        if created:
            stats['residents_created'] += 1
            self.stdout.write(f"  ✓ Created resident: {resident_id} - {initials} (Room {room_number}, {unit_name})")
        else:
            stats['residents_existing'] += 1

        # Determine review status
        today = date.today()
        
        if review_completed:
            status = 'COMPLETED'
            completed_date = next_review_date  # Assume completed around due date
        elif review_overdue:
            status = 'OVERDUE'
            completed_date = None
        elif (next_review_date - today).days <= 7:
            status = 'DUE'
            completed_date = None
        else:
            status = 'UPCOMING'
            completed_date = None

        # Determine review type (all are 6-monthly for this data)
        review_type = 'SIX_MONTH'

        # Create review
        review = CarePlanReview.objects.create(
            resident=resident,
            review_type=review_type,
            due_date=next_review_date,
            keyworker=keyworker,
            unit_manager=unit_manager,
            status=status,
            completed_date=completed_date if review_completed else None,
            completed_by=keyworker if review_completed else None,
            manager_approved=review_completed,
            manager_approval_date=completed_date if review_completed else None,
            manager_approved_by=unit_manager if review_completed else None,
            manager_comments=review_notes if review_notes else '',
            care_needs_assessment=review_notes if review_notes else '',
        )

        stats['reviews_created'] += 1

    def _parse_date(self, date_str):
        """Parse date from various formats"""
        date_str = date_str.strip()
        
        # Try different formats
        formats = [
            '%m/%d/%Y',  # 1/10/2025
            '%Y-%m-%d',  # 2025-01-10
            '%d/%m/%Y',  # 10/01/2025
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Could not parse date: {date_str}")

    def _find_user_by_name(self, name, unit):
        """Find user by name, trying various formats"""
        if not name:
            return None
        
        # Try to parse name
        parts = name.split()
        
        if len(parts) == 2:
            # Try "First Last" format
            first_initial = parts[0][0]
            last_name = parts[1]
            
            # Search by last name and first initial
            users = User.objects.filter(
                last_name__iexact=last_name,
                first_name__istartswith=first_initial,
                unit=unit
            )
            
            if users.exists():
                return users.first()
        
        # Try searching by first and last name in full_name property
        users = User.objects.filter(unit=unit)
        for user in users:
            if user.full_name and name.lower() in user.full_name.lower():
                return user
        
        # Return first SSCW/SSCWN from unit as fallback for managers
        if 'patel' in name.lower() or 'chen' in name.lower() or 'davies' in name.lower() or \
           'white' in name.lower() or 'green' in name.lower():
            # This is a manager - find SSCW/SSCWN
            manager = User.objects.filter(
                unit=unit,
                role__name__in=['SSCW', 'SSCWN']
            ).first()
            if manager:
                return manager
        
        # Return any staff from the unit as last resort
        return User.objects.filter(unit=unit, is_active=True).first()
