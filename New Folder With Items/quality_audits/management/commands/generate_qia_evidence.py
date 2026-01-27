"""
Django management command to generate QIA evidence packs
Usage: python manage.py generate_qia_evidence [options]
"""

from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from quality_audits.evidence_pack_generator import QIAEvidencePackGenerator


class Command(BaseCommand):
    help = 'Generate QIA Evidence Pack for Care Inspectorate submissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date (YYYY-MM-DD format)',
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date (YYYY-MM-DD format)',
        )
        parser.add_argument(
            '--qi',
            type=str,
            help='Filter by Quality Indicator (e.g., 1.3)',
        )
        parser.add_argument(
            '--source',
            type=str,
            choices=['INCIDENT', 'AUDIT', 'RISK', 'COMPLAINT', 'TREND', 'PDSA', 'INSPECTION'],
            help='Filter by source type',
        )
        parser.add_argument(
            '--priority',
            type=str,
            choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            help='Filter by priority level',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='QIA_Evidence_Pack.pdf',
            help='Output filename (default: QIA_Evidence_Pack.pdf)',
        )
        parser.add_argument(
            '--last-6-months',
            action='store_true',
            help='Generate report for last 6 months',
        )
        parser.add_argument(
            '--last-year',
            action='store_true',
            help='Generate report for last year',
        )

    def handle(self, *args, **options):
        start_date = None
        end_date = None

        # Handle date shortcuts
        if options['last_6_months']:
            start_date = datetime.now() - timedelta(days=180)
            end_date = datetime.now()
            self.stdout.write("Using last 6 months date range")
        elif options['last_year']:
            start_date = datetime.now() - timedelta(days=365)
            end_date = datetime.now()
            self.stdout.write("Using last year date range")
        else:
            # Parse custom dates
            if options['start_date']:
                try:
                    start_date = datetime.strptime(options['start_date'], '%Y-%m-%d')
                    self.stdout.write(f"Start date: {start_date.strftime('%d %B %Y')}")
                except ValueError:
                    self.stdout.write(self.style.ERROR('Invalid start date format. Use YYYY-MM-DD'))
                    return

            if options['end_date']:
                try:
                    end_date = datetime.strptime(options['end_date'], '%Y-%m-%d')
                    self.stdout.write(f"End date: {end_date.strftime('%d %B %Y')}")
                except ValueError:
                    self.stdout.write(self.style.ERROR('Invalid end date format. Use YYYY-MM-DD'))
                    return

        # Display filters
        if options['qi']:
            self.stdout.write(f"Filter: Quality Indicator {options['qi']}")
        if options['source']:
            self.stdout.write(f"Filter: Source Type = {options['source']}")
        if options['priority']:
            self.stdout.write(f"Filter: Priority = {options['priority']}")

        # Generate the evidence pack
        self.stdout.write(self.style.WARNING('\nGenerating QIA Evidence Pack...'))

        try:
            generator = QIAEvidencePackGenerator(filename=options['output'])
            pdf_path = generator.generate(
                start_date=start_date,
                end_date=end_date,
                qi_filter=options['qi'],
                source_filter=options['source'],
                priority_filter=options['priority']
            )

            self.stdout.write(self.style.SUCCESS(f'\n✓ Evidence pack generated successfully!'))
            self.stdout.write(self.style.SUCCESS(f'  Location: {pdf_path}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error generating evidence pack: {str(e)}'))
            import traceback
            traceback.print_exc()
