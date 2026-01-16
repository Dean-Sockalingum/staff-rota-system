"""
Generate care plan reviews for all residents

Usage:
    python3 manage.py generate_careplan_reviews
    python3 manage.py generate_careplan_reviews --all  # Regenerate all reviews
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from scheduling.models import Resident, CarePlanReview
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Generate care plan review schedules for all residents'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='Regenerate reviews for all residents (clears existing upcoming reviews)')

    def handle(self, *args, **options):
        regenerate_all = options['all']

        self.stdout.write("\n" + "="*70)
        self.stdout.write("CARE PLAN REVIEW SCHEDULE GENERATOR")
        self.stdout.write("="*70 + "\n")

        if regenerate_all:
            self.stdout.write("⚠️  Clearing existing UPCOMING reviews...")
            deleted = CarePlanReview.objects.filter(status='UPCOMING').delete()
            self.stdout.write(self.style.WARNING(f"✓ Deleted {deleted[0]} upcoming reviews\n"))

        stats = {
            'residents_processed': 0,
            'initial_reviews_created': 0,
            'six_month_reviews_created': 0,
            'already_scheduled': 0,
            'errors': 0
        }

        residents = Resident.objects.filter(is_active=True).select_related('unit', 'keyworker', 'unit_manager')

        for resident in residents:
            try:
                self._generate_reviews_for_resident(resident, stats)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error for {resident.resident_id}: {str(e)}"))
                stats['errors'] += 1
                continue

        # Print summary
        self.stdout.write("\n" + "="*70)
        self.stdout.write("SUMMARY")
        self.stdout.write("="*70)
        self.stdout.write(f"✓ Residents processed: {stats['residents_processed']}")
        self.stdout.write(f"✓ Initial reviews created: {stats['initial_reviews_created']}")
        self.stdout.write(f"✓ 6-month reviews created: {stats['six_month_reviews_created']}")
        self.stdout.write(f"⚠ Already scheduled: {stats['already_scheduled']}")
        if stats['errors'] > 0:
            self.stdout.write(self.style.ERROR(f"✗ Errors: {stats['errors']}"))
        self.stdout.write("="*70 + "\n")

    @transaction.atomic
    def _generate_reviews_for_resident(self, resident, stats):
        """Generate appropriate reviews for a resident"""
        stats['residents_processed'] += 1

        # Check if they already have an upcoming/due/overdue review
        existing = CarePlanReview.objects.filter(
            resident=resident,
            status__in=['UPCOMING', 'DUE', 'OVERDUE', 'IN_PROGRESS', 'PENDING_APPROVAL']
        ).exists()

        if existing:
            stats['already_scheduled'] += 1
            self.stdout.write(f"  ⚠ {resident.resident_id} - Already has pending review")
            return

        # Get last completed review
        last_completed = CarePlanReview.objects.filter(
            resident=resident,
            status='COMPLETED'
        ).order_by('-completed_date').first()

        today = date.today()

        if not last_completed:
            # New resident - check if they need initial review
            initial_due = resident.admission_date + timedelta(weeks=4)
            
            # Only create if initial review is due or overdue
            if initial_due <= today + timedelta(days=30):  # Within next 30 days or overdue
                CarePlanReview.objects.create(
                    resident=resident,
                    review_type='INITIAL',
                    due_date=initial_due,
                    keyworker=resident.keyworker,
                    unit_manager=resident.unit_manager,
                    status='UPCOMING'
                )
                stats['initial_reviews_created'] += 1
                self.stdout.write(f"  ✓ {resident.resident_id} - Initial review scheduled for {initial_due}")
            else:
                self.stdout.write(f"  • {resident.resident_id} - Initial review not yet due ({initial_due})")
        else:
            # Has completed review - schedule next 6-month review
            next_due = last_completed.completed_date + timedelta(days=183)  # ~6 months
            
            # Only create if we're within 30 days of next review or it's overdue
            if next_due <= today + timedelta(days=30):
                CarePlanReview.objects.create(
                    resident=resident,
                    review_type='SIX_MONTH',
                    due_date=next_due,
                    keyworker=resident.keyworker,
                    unit_manager=resident.unit_manager,
                    status='UPCOMING'
                )
                stats['six_month_reviews_created'] += 1
                self.stdout.write(f"  ✓ {resident.resident_id} - 6-month review scheduled for {next_due}")
            else:
                self.stdout.write(f"  • {resident.resident_id} - Next review not yet due ({next_due})")
