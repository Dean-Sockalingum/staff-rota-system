"""
Management command to import Care Inspectorate reports

Usage:
    python manage.py import_ci_reports --all
    python manage.py import_ci_reports --home "Orchard Grove"
    python manage.py import_ci_reports --cs-number CS2014333831
"""

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import datetime, date
import re
import logging

from scheduling.models import Unit
from scheduling.models_improvement import CareInspectorateReport

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import Care Inspectorate reports for care homes'
    
    # CS Number mapping
    CS_NUMBERS = {
        'Meadowburn': 'CS2018371804',
        'Hawthorn House': 'CS2003001025',
        'Orchard Grove': 'CS2014333831',
        'Riverside': 'CS2014333834',
        'Victoria Gardens': 'CS2018371437',
    }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Import reports for all homes',
        )
        parser.add_argument(
            '--home',
            type=str,
            help='Import reports for specific home (e.g., "Orchard Grove")',
        )
        parser.add_argument(
            '--cs-number',
            type=str,
            help='Import reports for specific CS number (e.g., CS2014333831)',
        )
        parser.add_argument(
            '--latest-only',
            action='store_true',
            help='Only import the most recent report',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Import reports from specific year (e.g., 2024)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Care Inspectorate report import...'))
        
        # Determine which homes to process
        homes_to_process = []
        
        if options['all']:
            homes_to_process = list(self.CS_NUMBERS.items())
        elif options['home']:
            home_name = options['home']
            if home_name in self.CS_NUMBERS:
                homes_to_process = [(home_name, self.CS_NUMBERS[home_name])]
            else:
                self.stdout.write(self.style.ERROR(f"Unknown home: {home_name}"))
                self.stdout.write(f"Available homes: {', '.join(self.CS_NUMBERS.keys())}")
                return
        elif options['cs_number']:
            cs_number = options['cs_number']
            home_name = next((k for k, v in self.CS_NUMBERS.items() if v == cs_number), None)
            if home_name:
                homes_to_process = [(home_name, cs_number)]
            else:
                self.stdout.write(self.style.ERROR(f"Unknown CS number: {cs_number}"))
                return
        else:
            self.stdout.write(self.style.ERROR('Must specify --all, --home, or --cs-number'))
            return
        
        # Process each home
        total_imported = 0
        total_skipped = 0
        
        for home_name, cs_number in homes_to_process:
            self.stdout.write(f"\nProcessing {home_name} ({cs_number})...")
            
            try:
                imported, skipped = self.import_reports_for_home(
                    home_name, 
                    cs_number, 
                    latest_only=options.get('latest_only', False),
                    year=options.get('year')
                )
                total_imported += imported
                total_skipped += skipped
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {home_name}: {str(e)}"))
                logger.exception(f"Error importing reports for {home_name}")
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n{'='*50}"))
        self.stdout.write(self.style.SUCCESS(f"Import complete!"))
        self.stdout.write(self.style.SUCCESS(f"Total reports imported: {total_imported}"))
        self.stdout.write(self.style.SUCCESS(f"Total reports skipped (already exist): {total_skipped}"))
    
    def import_reports_for_home(self, home_name, cs_number, latest_only=False, year=None):
        """Import reports for a specific home"""
        
        # Get or create Unit
        try:
            unit = Unit.objects.get(name=home_name)
        except Unit.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Unit '{home_name}' not found in database. Skipping."))
            return 0, 0
        
        # Ensure CS number is set
        if not unit.care_inspectorate_cs_number:
            unit.care_inspectorate_cs_number = cs_number
            unit.save()
            self.stdout.write(f"Updated {home_name} with CS number {cs_number}")
        
        # Fetch report list from Care Inspectorate website
        reports_data = self.fetch_report_list(cs_number)
        
        if not reports_data:
            self.stdout.write(self.style.WARNING(f"No reports found for {home_name}"))
            return 0, 0
        
        # Filter by year if specified
        if year:
            reports_data = [r for r in reports_data if r['inspection_date'].year == year]
        
        # Take only latest if specified
        if latest_only and reports_data:
            reports_data = [reports_data[0]]  # Already sorted by date (newest first)
        
        self.stdout.write(f"Found {len(reports_data)} report(s) to process")
        
        imported = 0
        skipped = 0
        
        for report_data in reports_data:
            # Check if already imported
            existing = CareInspectorateReport.objects.filter(
                home=unit,
                inspection_date=report_data['inspection_date'],
                report_id=report_data['report_id']
            ).first()
            
            if existing:
                self.stdout.write(f"  Skipping {report_data['inspection_date']} (already imported)")
                skipped += 1
                continue
            
            # Fetch detailed report data
            detailed_data = self.fetch_report_details(report_data['report_id'])
            
            # Merge data
            full_data = {**report_data, **detailed_data}
            
            # Create report
            with transaction.atomic():
                report = self.create_report(unit, cs_number, full_data)
                imported += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Imported: {report.inspection_date} - {report.get_report_type_display()}"
                ))
        
        return imported, skipped
    
    def fetch_report_list(self, cs_number):
        """Fetch list of reports from Care Inspectorate website"""
        
        url = f"https://www.careinspectorate.com/index.php/care-services?detail={cs_number}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch report list for {cs_number}: {e}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find inspection reports table
        reports = []
        
        # Look for the "Inspection reports" section
        reports_section = soup.find('h2', string=re.compile(r'Inspection reports', re.I))
        if not reports_section:
            return reports
        
        # Find the table after this heading
        table = reports_section.find_next('table')
        if not table:
            return reports
        
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                # Parse date (format: "28 October 2024")
                date_str = cols[0].get_text(strip=True)
                try:
                    inspection_date = datetime.strptime(date_str, "%d %B %Y").date()
                except ValueError:
                    continue
                
                # Report type
                report_type = cols[1].get_text(strip=True)
                
                # Report ID
                report_id = cols[2].get_text(strip=True)
                
                reports.append({
                    'inspection_date': inspection_date,
                    'report_type': self.map_report_type(report_type),
                    'report_id': report_id,
                })
        
        return reports
    
    def fetch_report_details(self, report_id):
        """Fetch detailed information from specific report"""
        
        # Note: This is a simplified version. Full implementation would:
        # 1. Download the PDF report
        # 2. Extract text using PyPDF2 or pdfplumber
        # 3. Parse themes, ratings, requirements, recommendations
        
        # For now, return placeholder data
        # In production, this would parse the actual PDF
        
        return {
            'theme1_rating': None,
            'theme2_rating': None,
            'theme3_rating': None,
            'theme4_rating': None,
            'overall_rating': None,
            'requirements': [],
            'recommendations': [],
            'areas_for_improvement': [],
            'report_url': f"https://www.careinspectorate.com/index.php/inspection-reports/{report_id}",
        }
    
    def create_report(self, unit, cs_number, data):
        """Create CareInspectorateReport from fetched data"""
        
        report = CareInspectorateReport.objects.create(
            home=unit,
            cs_number=cs_number,
            report_type=data['report_type'],
            inspection_date=data['inspection_date'],
            publication_date=data.get('publication_date', data['inspection_date']),
            report_id=data['report_id'],
            
            # Quality Framework Themes
            theme1_rating=data.get('theme1_rating'),
            theme2_rating=data.get('theme2_rating'),
            theme3_rating=data.get('theme3_rating'),
            theme4_rating=data.get('theme4_rating'),
            overall_rating=data.get('overall_rating'),
            
            # Requirements and recommendations
            requirements=data.get('requirements', []),
            recommendations=data.get('recommendations', []),
            areas_for_improvement=data.get('areas_for_improvement', []),
            
            report_url=data.get('report_url', ''),
            
            created_by=None,  # System import
        )
        
        return report
    
    def map_report_type(self, report_type_text):
        """Map report type text to model choice"""
        
        text = report_type_text.lower()
        
        if 'unannounced' in text:
            return 'UNANNOUNCED'
        elif 'follow' in text or 'follow-up' in text:
            return 'FOLLOW_UP'
        elif 'complaint' in text:
            return 'COMPLAINT'
        elif 'thematic' in text:
            return 'THEMATIC'
        else:
            return 'UNANNOUNCED'  # Default
