"""
Management command to generate or update sickness absence summaries with Bradford Factor calculations.

This command creates/updates SicknessAbsenceSummary records for all staff
with sickness records, calculating Bradford Factor scores and identifying
staff who have exceeded trigger thresholds.
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from staff_records.models import SicknessAbsenceSummary, StaffProfile


class Command(BaseCommand):
    help = "Generate sickness absence summaries with Bradford Factor calculations"

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            help='Year for summary (defaults to current year)'
        )
        parser.add_argument(
            '--all-years',
            action='store_true',
            help='Generate summaries for all years with sickness records'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Determine which years to process
        if options['all_years']:
            # Get all distinct years from sickness records
            from staff_records.models import SicknessRecord
            years = SicknessRecord.objects.dates('first_working_day', 'year').values_list('first_working_day__year', flat=True).distinct()
            years = sorted(set(years))
        elif options['year']:
            years = [options['year']]
        else:
            years = [date.today().year]
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Generating Sickness Absence Summaries")
        self.stdout.write(f"{'='*60}\n")
        
        total_created = 0
        total_updated = 0
        total_triggered = 0
        
        for year in years:
            self.stdout.write(f"\n{self.style.WARNING(f'Processing Year: {year}')}")
            
            # Get all staff profiles with sickness records
            profiles = StaffProfile.objects.filter(
                sickness_records__first_working_day__year=year
            ).distinct()
            
            year_created = 0
            year_updated = 0
            year_triggered = 0
            
            for profile in profiles:
                # Get or create summary
                summary, created = SicknessAbsenceSummary.objects.get_or_create(
                    profile=profile,
                    year=year
                )
                
                # Recalculate from sickness records
                summary.recalculate_from_records(year)
                
                if created:
                    year_created += 1
                    total_created += 1
                    action = "Created"
                    style = self.style.SUCCESS
                else:
                    year_updated += 1
                    total_updated += 1
                    action = "Updated"
                    style = self.style.WARNING
                
                if summary.trigger_level_reached:
                    year_triggered += 1
                    total_triggered += 1
                    trigger_marker = self.style.ERROR(" ⚠️ TRIGGERED")
                else:
                    trigger_marker = ""
                
                self.stdout.write(
                    style(
                        f"  {action}: {profile.user.full_name:30s} | "
                        f"Days: {summary.total_absence_days:3d} | "
                        f"Episodes: {summary.total_absence_instances:2d} | "
                        f"Bradford: {summary.bradford_factor_score:5d}"
                    ) + trigger_marker
                )
            
            self.stdout.write(f"\n  Year {year} Summary:")
            self.stdout.write(f"    Created:   {year_created}")
            self.stdout.write(f"    Updated:   {year_updated}")
            self.stdout.write(f"    Triggered: {year_triggered}")
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"Overall Summary:"))
        self.stdout.write(f"  Years processed:        {len(years)}")
        self.stdout.write(f"  Summaries created:      {total_created}")
        self.stdout.write(f"  Summaries updated:      {total_updated}")
        self.stdout.write(f"  Staff above threshold:  {total_triggered}")
        self.stdout.write(f"{'='*60}\n")
        
        if total_triggered > 0:
            self.stdout.write(self.style.WARNING(
                f"\n⚠️  {total_triggered} staff member(s) have exceeded the Bradford Factor threshold.\n"
                f"   These staff require formal absence review as per policy."
            ))
        
        self.stdout.write(self.style.SUCCESS("\n✅ Sickness summary generation complete!"))
