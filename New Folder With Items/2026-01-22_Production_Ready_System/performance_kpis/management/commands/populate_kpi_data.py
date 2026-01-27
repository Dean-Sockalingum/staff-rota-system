"""
Management command to populate Performance KPI module with realistic care home data.

Creates:
- Balanced Scorecard Perspectives (4 standard perspectives)
- KPI Definitions (20+ care home specific KPIs)
- Executive Dashboards (3 different stakeholder views)
- Performance Targets (quarterly targets for each KPI)
- Benchmark Data (external benchmarks from Care Inspectorate)
- KPI Measurements (90 days of realistic data with trends)

Usage:
    python manage.py populate_kpi_data [--clear]
    
Options:
    --clear     Delete existing KPI data before populating
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import random

from performance_kpis.models import (
    BalancedScorecardPerspective,
    KPIDefinition,
    ExecutiveDashboard,
    DashboardKPI,
    PerformanceTarget,
    BenchmarkData,
    KPIMeasurement,
)
from scheduling.models import CareHome

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate Performance KPI module with realistic care home data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing KPI data before populating',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n=== Performance KPI Data Population ===\n'))

        if options['clear']:
            self.clear_data()

        # Get or create admin user for ownership
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.stdout.write(self.style.ERROR('No admin user found. Please create a superuser first.'))
            return

        # Get care homes for assignment
        care_homes = list(CareHome.objects.all())
        if not care_homes:
            self.stdout.write(self.style.WARNING('No care homes found. Creating KPIs at organization level only.'))

        # Step 1: Create Balanced Scorecard Perspectives
        self.stdout.write('\n[1/7] Creating Balanced Scorecard Perspectives...')
        perspectives = self.create_perspectives()

        # Step 2: Create KPI Definitions
        self.stdout.write('\n[2/7] Creating KPI Definitions...')
        kpis = self.create_kpis(perspectives)

        # Step 3: Create Executive Dashboards
        self.stdout.write('\n[3/7] Creating Executive Dashboards...')
        dashboards = self.create_dashboards(admin)

        # Step 4: Link KPIs to Dashboards
        self.stdout.write('\n[4/7] Linking KPIs to Dashboards...')
        self.link_kpis_to_dashboards(dashboards, kpis)

        # Step 5: Create Performance Targets
        self.stdout.write('\n[5/7] Creating Performance Targets...')
        self.create_targets(kpis)

        # Step 6: Create Benchmark Data
        self.stdout.write('\n[6/7] Creating Benchmark Data...')
        self.create_benchmarks(kpis)

        # Step 7: Create KPI Measurements (90 days)
        self.stdout.write('\n[7/7] Creating KPI Measurements (90 days)...')
        self.create_measurements(kpis, care_homes, admin)

        # Summary
        self.print_summary()

    def clear_data(self):
        """Delete existing KPI data."""
        self.stdout.write(self.style.WARNING('Clearing existing KPI data...'))
        
        KPIMeasurement.objects.all().delete()
        BenchmarkData.objects.all().delete()
        PerformanceTarget.objects.all().delete()
        DashboardKPI.objects.all().delete()
        ExecutiveDashboard.objects.all().delete()
        KPIDefinition.objects.all().delete()
        BalancedScorecardPerspective.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))

    def create_perspectives(self):
        """Create 4 standard Balanced Scorecard perspectives."""
        perspectives_data = [
            {
                'name': 'Financial Stewardship',
                'description': 'Cost efficiency, revenue optimization, and financial sustainability',
                'color_code': '#1E88E5',  # Blue
                'display_order': 1,
            },
            {
                'name': 'Resident & Family Experience',
                'description': 'Quality of care, satisfaction, and person-centered outcomes',
                'color_code': '#43A047',  # Green
                'display_order': 2,
            },
            {
                'name': 'Internal Processes',
                'description': 'Operational efficiency, safety, compliance, and quality systems',
                'color_code': '#FB8C00',  # Orange
                'display_order': 3,
            },
            {
                'name': 'Learning & Growth',
                'description': 'Staff development, innovation, and organizational capability',
                'color_code': '#8E24AA',  # Purple
                'display_order': 4,
            },
        ]

        perspectives = {}
        for data in perspectives_data:
            perspective, created = BalancedScorecardPerspective.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            perspectives[data['name']] = perspective
            status = '✓ Created' if created else '○ Exists'
            self.stdout.write(f'  {status}: {perspective.name}')

        return perspectives

    def create_kpis(self, perspectives):
        """Create comprehensive set of care home KPIs."""
        kpis_data = [
            # Financial Stewardship (8 KPIs)
            {
                'code': 'FIN-001',
                'name': 'Occupancy Rate',
                'description': 'Percentage of beds occupied',
                'category': 'FINANCIAL',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('95.0'),
                'threshold_green': Decimal('93.0'),
                'threshold_amber': Decimal('88.0'),
                'threshold_red': Decimal('85.0'),
                'reporting_frequency': 'DAILY',
                'data_source': 'Care Management System',
            },
            {
                'code': 'FIN-002',
                'name': 'Cost Per Resident Day',
                'description': 'Average daily cost per occupied bed',
                'category': 'FINANCIAL',
                'measurement_type': 'CURRENCY',
                'trend_direction': 'LOWER_BETTER',
                'target_value': Decimal('145.00'),
                'threshold_green': Decimal('150.00'),
                'threshold_amber': Decimal('160.00'),
                'threshold_red': Decimal('170.00'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Finance System',
            },
            {
                'code': 'FIN-003',
                'name': 'Agency Staff Spend',
                'description': 'Percentage of total staff costs spent on agency staff',
                'category': 'FINANCIAL',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'LOWER_BETTER',
                'target_value': Decimal('5.0'),
                'threshold_green': Decimal('8.0'),
                'threshold_amber': Decimal('12.0'),
                'threshold_red': Decimal('15.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Payroll System',
            },
            {
                'code': 'FIN-004',
                'name': 'Revenue Per Available Bed',
                'description': 'Total revenue divided by available bed days',
                'category': 'FINANCIAL',
                'measurement_type': 'CURRENCY',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('155.00'),
                'threshold_green': Decimal('150.00'),
                'threshold_amber': Decimal('145.00'),
                'threshold_red': Decimal('140.00'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Finance System',
            },
            
            # Resident & Family Experience (6 KPIs)
            {
                'code': 'RES-001',
                'name': 'Resident Satisfaction Score',
                'description': 'Overall satisfaction score from resident surveys (1-5 scale)',
                'category': 'QUALITY',
                'measurement_type': 'SCORE',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('4.5'),
                'threshold_green': Decimal('4.2'),
                'threshold_amber': Decimal('3.8'),
                'threshold_red': Decimal('3.5'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Resident Survey',
            },
            {
                'code': 'RES-002',
                'name': 'Family Satisfaction Score',
                'description': 'Overall satisfaction score from family surveys (1-5 scale)',
                'category': 'QUALITY',
                'measurement_type': 'SCORE',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('4.3'),
                'threshold_green': Decimal('4.0'),
                'threshold_amber': Decimal('3.5'),
                'threshold_red': Decimal('3.0'),
                'reporting_frequency': 'QUARTERLY',
                'data_source': 'Family Survey',
            },
            {
                'code': 'RES-003',
                'name': 'Complaint Resolution Time',
                'description': 'Average days to resolve formal complaints',
                'category': 'QUALITY',
                'measurement_type': 'DAYS',
                'trend_direction': 'LOWER_BETTER',
                'target_value': Decimal('7.0'),
                'threshold_green': Decimal('10.0'),
                'threshold_amber': Decimal('14.0'),
                'threshold_red': Decimal('21.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Complaints Log',
            },
            {
                'code': 'RES-004',
                'name': 'Activities Engagement Rate',
                'description': 'Percentage of residents participating in daily activities',
                'category': 'QUALITY',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('75.0'),
                'threshold_green': Decimal('70.0'),
                'threshold_amber': Decimal('60.0'),
                'threshold_red': Decimal('50.0'),
                'reporting_frequency': 'WEEKLY',
                'data_source': 'Activities Log',
            },
            
            # Internal Processes (8 KPIs)
            {
                'code': 'SAF-001',
                'name': 'Falls Rate (per 1000 resident days)',
                'description': 'Number of falls per 1000 resident days',
                'category': 'QUALITY',
                'measurement_type': 'RATIO',
                'trend_direction': 'LOWER_BETTER',
                'target_value': Decimal('6.5'),
                'threshold_green': Decimal('7.5'),
                'threshold_amber': Decimal('9.0'),
                'threshold_red': Decimal('11.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Incident Reporting System',
            },
            {
                'code': 'SAF-002',
                'name': 'Medication Error Rate (per 1000 doses)',
                'description': 'Medication errors per 1000 doses administered',
                'category': 'QUALITY',
                'measurement_type': 'RATIO',
                'trend_direction': 'LOWER_BETTER',
                'target_value': Decimal('2.0'),
                'threshold_green': Decimal('3.0'),
                'threshold_amber': Decimal('5.0'),
                'threshold_red': Decimal('7.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Medication Administration Records',
            },
            {
                'code': 'SAF-003',
                'name': 'Pressure Ulcer Prevalence',
                'description': 'Percentage of residents with Category 2+ pressure ulcers',
                'category': 'QUALITY',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'LOWER_BETTER',
                'target_value': Decimal('2.0'),
                'threshold_green': Decimal('3.0'),
                'threshold_amber': Decimal('5.0'),
                'threshold_red': Decimal('7.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Clinical Assessment',
            },
            {
                'code': 'SAF-004',
                'name': 'Infection Rate (per 1000 resident days)',
                'description': 'Healthcare-associated infections per 1000 resident days',
                'category': 'QUALITY',
                'measurement_type': 'RATIO',
                'trend_direction': 'LOWER_BETTER',
                'target_value': Decimal('3.5'),
                'threshold_green': Decimal('4.5'),
                'threshold_amber': Decimal('6.0'),
                'threshold_red': Decimal('8.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Infection Control Log',
            },
            {
                'code': 'COMP-001',
                'name': 'Audit Compliance Score',
                'description': 'Percentage compliance across all quality audits',
                'category': 'COMPLIANCE',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('95.0'),
                'threshold_green': Decimal('90.0'),
                'threshold_amber': Decimal('85.0'),
                'threshold_red': Decimal('80.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Quality Audit System',
            },
            {
                'code': 'COMP-002',
                'name': 'Care Plan Review Compliance',
                'description': 'Percentage of care plans reviewed within 28 days',
                'category': 'COMPLIANCE',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('100.0'),
                'threshold_green': Decimal('95.0'),
                'threshold_amber': Decimal('90.0'),
                'threshold_red': Decimal('85.0'),
                'reporting_frequency': 'WEEKLY',
                'data_source': 'Care Planning System',
            },
            
            # Learning & Growth (6 KPIs)
            {
                'code': 'HR-001',
                'name': 'Mandatory Training Compliance',
                'description': 'Percentage of staff up-to-date with all mandatory training',
                'category': 'COMPLIANCE',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('95.0'),
                'threshold_green': Decimal('90.0'),
                'threshold_amber': Decimal('85.0'),
                'threshold_red': Decimal('80.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Training Management System',
            },
            {
                'code': 'HR-002',
                'name': 'Staff Turnover Rate',
                'description': 'Annual staff turnover percentage',
                'category': 'WORKFORCE',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'LOWER_BETTER',
                'target_value': Decimal('18.0'),
                'threshold_green': Decimal('22.0'),
                'threshold_amber': Decimal('28.0'),
                'threshold_red': Decimal('35.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'HR System',
            },
            {
                'code': 'HR-003',
                'name': 'Staff Sickness Rate',
                'description': 'Percentage of contracted hours lost to sickness',
                'category': 'WORKFORCE',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'LOWER_BETTER',
                'target_value': Decimal('4.5'),
                'threshold_green': Decimal('5.5'),
                'threshold_amber': Decimal('7.0'),
                'threshold_red': Decimal('9.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Payroll System',
            },
            {
                'code': 'HR-004',
                'name': 'Staff-to-Resident Ratio',
                'description': 'Average staff-to-resident ratio during day shift',
                'category': 'WORKFORCE',
                'measurement_type': 'RATIO',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('1.5'),
                'threshold_green': Decimal('1.4'),
                'threshold_amber': Decimal('1.3'),
                'threshold_red': Decimal('1.2'),
                'reporting_frequency': 'DAILY',
                'data_source': 'Roster System',
            },
            {
                'code': 'HR-005',
                'name': 'Supervision Compliance',
                'description': 'Percentage of staff receiving monthly supervision',
                'category': 'WORKFORCE',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('95.0'),
                'threshold_green': Decimal('90.0'),
                'threshold_amber': Decimal('80.0'),
                'threshold_red': Decimal('70.0'),
                'reporting_frequency': 'MONTHLY',
                'data_source': 'Supervision Log',
            },
            {
                'code': 'HR-006',
                'name': 'SVQ Completion Rate',
                'description': 'Percentage of care staff achieving SVQ Level 2 within 12 months',
                'category': 'LEARNING',
                'measurement_type': 'PERCENTAGE',
                'trend_direction': 'HIGHER_BETTER',
                'target_value': Decimal('85.0'),
                'threshold_green': Decimal('80.0'),
                'threshold_amber': Decimal('70.0'),
                'threshold_red': Decimal('60.0'),
                'reporting_frequency': 'QUARTERLY',
                'data_source': 'Training Management System',
            },
        ]

        kpis = {}
        for data in kpis_data:
            kpi, created = KPIDefinition.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            kpis[data['code']] = kpi
            status = '✓ Created' if created else '○ Exists'
            self.stdout.write(f'  {status}: {kpi.code} - {kpi.name}')

        return kpis

    def create_dashboards(self, admin):
        """Create executive dashboards for different stakeholder groups."""
        dashboards_data = [
            {
                'name': 'Executive Overview',
                'description': 'High-level KPIs for board and executive team',
                'owner': admin,
                'is_public': True,
            },
            {
                'name': 'Clinical Quality Dashboard',
                'description': 'Clinical outcomes and safety metrics',
                'owner': admin,
                'is_public': True,
            },
            {
                'name': 'Operational Performance',
                'description': 'Financial and operational efficiency metrics',
                'owner': admin,
                'is_public': True,
            },
        ]

        dashboards = {}
        for data in dashboards_data:
            dashboard, created = ExecutiveDashboard.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            dashboards[data['name']] = dashboard
            status = '✓ Created' if created else '○ Exists'
            self.stdout.write(f'  {status}: {dashboard.name}')

        return dashboards

    def link_kpis_to_dashboards(self, dashboards, kpis):
        """Link KPIs to appropriate dashboards with chart configurations."""
        
        # Executive Overview - Key metrics from each perspective
        exec_kpis = [
            ('FIN-001', 'line', 1, True, True),  # Occupancy
            ('RES-001', 'line', 2, True, True),  # Resident Satisfaction
            ('SAF-001', 'line', 3, True, True),  # Falls Rate
            ('HR-001', 'bar', 4, True, True),    # Mandatory Training
            ('COMP-001', 'line', 5, True, True), # Audit Compliance
            ('HR-002', 'line', 6, True, True),   # Staff Turnover
        ]
        
        for code, chart_type, order, show_trend, show_target in exec_kpis:
            DashboardKPI.objects.get_or_create(
                dashboard=dashboards['Executive Overview'],
                kpi=kpis[code],
                defaults={
                    'display_order': order,
                    'chart_type': chart_type,
                    'show_trend': show_trend,
                    'show_target': show_target,
                }
            )
        
        # Clinical Quality Dashboard
        clinical_kpis = [
            ('RES-001', 'line', 1, True, True),   # Resident Satisfaction
            ('RES-002', 'line', 2, True, True),   # Family Satisfaction
            ('SAF-001', 'line', 3, True, True),   # Falls
            ('SAF-002', 'line', 4, True, True),   # Medication Errors
            ('SAF-003', 'line', 5, True, True),   # Pressure Ulcers
            ('SAF-004', 'line', 6, True, True),   # Infections
            ('RES-003', 'bar', 7, True, True),    # Complaint Resolution
            ('RES-004', 'bar', 8, True, True),    # Activities Engagement
        ]
        
        for code, chart_type, order, show_trend, show_target in clinical_kpis:
            DashboardKPI.objects.get_or_create(
                dashboard=dashboards['Clinical Quality Dashboard'],
                kpi=kpis[code],
                defaults={
                    'display_order': order,
                    'chart_type': chart_type,
                    'show_trend': show_trend,
                    'show_target': show_target,
                }
            )
        
        # Operational Performance
        ops_kpis = [
            ('FIN-001', 'line', 1, True, True),   # Occupancy
            ('FIN-002', 'line', 2, True, True),   # Cost Per Resident Day
            ('FIN-003', 'bar', 3, True, True),    # Agency Spend
            ('FIN-004', 'line', 4, True, True),   # Revenue Per Bed
            ('HR-001', 'bar', 5, True, True),     # Mandatory Training
            ('HR-002', 'line', 6, True, True),    # Staff Turnover
            ('HR-003', 'line', 7, True, True),    # Sickness Rate
            ('HR-004', 'line', 8, True, True),    # Staff Ratios
        ]
        
        for code, chart_type, order, show_trend, show_target in ops_kpis:
            DashboardKPI.objects.get_or_create(
                dashboard=dashboards['Operational Performance'],
                kpi=kpis[code],
                defaults={
                    'display_order': order,
                    'chart_type': chart_type,
                    'show_trend': show_trend,
                    'show_target': show_target,
                }
            )
        
        self.stdout.write(f'  ✓ Linked KPIs to {len(dashboards)} dashboards')

    def create_targets(self, kpis):
        """Create quarterly performance targets for each KPI."""
        today = timezone.now().date()
        
        # Q4 2025 (Oct-Dec)
        q4_2025_start = date(2025, 10, 1)
        q4_2025_end = date(2025, 12, 31)
        
        # Q1 2026 (Jan-Mar)
        q1_2026_start = date(2026, 1, 1)
        q1_2026_end = date(2026, 3, 31)
        
        # Q2 2026 (Apr-Jun)
        q2_2026_start = date(2026, 4, 1)
        q2_2026_end = date(2026, 6, 30)
        
        quarters = [
            (q4_2025_start, q4_2025_end, 'Q4 2025'),
            (q1_2026_start, q1_2026_end, 'Q1 2026'),
            (q2_2026_start, q2_2026_end, 'Q2 2026'),
        ]
        
        count = 0
        for kpi in kpis.values():
            for period_start, period_end, quarter_name in quarters:
                # Calculate stretch target based on trend direction
                if kpi.trend_direction == 'HIGHER_BETTER':
                    stretch = kpi.target_value * Decimal('1.05')
                elif kpi.trend_direction == 'LOWER_BETTER':
                    stretch = kpi.target_value * Decimal('0.95')
                else:
                    stretch = kpi.target_value
                
                PerformanceTarget.objects.get_or_create(
                    kpi=kpi,
                    period_start=period_start,
                    period_end=period_end,
                    defaults={
                        'target_value': kpi.target_value,
                        'stretch_target': stretch,
                    }
                )
                count += 1
        
        self.stdout.write(f'  ✓ Created {count} quarterly targets')

    def create_benchmarks(self, kpis):
        """Create benchmark data from Care Inspectorate and sector averages."""
        today = timezone.now().date()
        
        # Create benchmarks for last 12 months
        benchmarks_data = [
            # Financial benchmarks
            ('FIN-001', Decimal('92.5'), Decimal('88.0'), Decimal('96.0')),  # Occupancy
            ('FIN-002', Decimal('152.00'), Decimal('140.00'), Decimal('165.00')),  # Cost
            ('FIN-003', Decimal('8.5'), Decimal('5.0'), Decimal('15.0')),  # Agency
            
            # Quality benchmarks
            ('RES-001', Decimal('4.2'), Decimal('3.8'), Decimal('4.6')),  # Satisfaction
            ('RES-002', Decimal('4.0'), Decimal('3.5'), Decimal('4.5')),  # Family
            ('RES-003', Decimal('10.0'), Decimal('7.0'), Decimal('14.0')),  # Complaints
            
            # Safety benchmarks
            ('SAF-001', Decimal('7.8'), Decimal('6.0'), Decimal('10.0')),  # Falls
            ('SAF-002', Decimal('3.2'), Decimal('2.0'), Decimal('5.0')),  # Med Errors
            ('SAF-003', Decimal('3.5'), Decimal('2.0'), Decimal('6.0')),  # Pressure Ulcers
            ('SAF-004', Decimal('4.2'), Decimal('3.0'), Decimal('6.5')),  # Infections
            
            # Compliance benchmarks
            ('COMP-001', Decimal('91.0'), Decimal('85.0'), Decimal('95.0')),  # Audit
            ('COMP-002', Decimal('96.0'), Decimal('90.0'), Decimal('100.0')),  # Care Plans
            
            # HR benchmarks
            ('HR-001', Decimal('88.0'), Decimal('80.0'), Decimal('95.0')),  # Training
            ('HR-002', Decimal('24.0'), Decimal('18.0'), Decimal('30.0')),  # Turnover
            ('HR-003', Decimal('5.8'), Decimal('4.0'), Decimal('8.0')),  # Sickness
            ('HR-004', Decimal('1.4'), Decimal('1.3'), Decimal('1.6')),  # Ratios
        ]
        
        count = 0
        for code, avg, lower, upper in benchmarks_data:
            if code in kpis:
                # Create benchmark for Q4 2025
                BenchmarkData.objects.get_or_create(
                    kpi=kpis[code],
                    source_name='Care Inspectorate Scotland',
                    period_start=date(2025, 10, 1),
                    period_end=date(2025, 12, 31),
                    defaults={
                        'benchmark_type': 'NATIONAL',
                        'benchmark_value': avg,
                        'sample_size': 245,  # Scottish care homes
                        'methodology': 'National aggregate from Scottish care homes quarterly returns',
                    }
                )
                count += 1
        
        self.stdout.write(f'  ✓ Created {count} benchmark records')

    def create_measurements(self, kpis, care_homes, admin):
        """Create 90 days of realistic measurements with trends."""
        today = timezone.now().date()
        start_date = today - timedelta(days=90)
        
        # Define measurement patterns for each KPI
        patterns = {
            'FIN-001': {'base': 91.0, 'trend': 0.05, 'volatility': 1.5},  # Improving occupancy
            'FIN-002': {'base': 155.0, 'trend': -0.08, 'volatility': 3.0},  # Reducing costs
            'FIN-003': {'base': 12.0, 'trend': -0.06, 'volatility': 1.2},  # Reducing agency
            'FIN-004': {'base': 148.0, 'trend': 0.06, 'volatility': 2.5},  # Improving revenue
            
            'RES-001': {'base': 4.1, 'trend': 0.004, 'volatility': 0.15},  # Improving satisfaction
            'RES-002': {'base': 3.9, 'trend': 0.005, 'volatility': 0.20},  # Improving family
            'RES-003': {'base': 12.0, 'trend': -0.05, 'volatility': 2.0},  # Reducing resolution time
            'RES-004': {'base': 68.0, 'trend': 0.08, 'volatility': 3.0},  # Improving engagement
            
            'SAF-001': {'base': 8.2, 'trend': -0.02, 'volatility': 0.5},  # Reducing falls
            'SAF-002': {'base': 3.8, 'trend': -0.02, 'volatility': 0.3},  # Reducing med errors
            'SAF-003': {'base': 4.2, 'trend': -0.03, 'volatility': 0.4},  # Reducing pressure ulcers
            'SAF-004': {'base': 4.8, 'trend': -0.02, 'volatility': 0.4},  # Reducing infections
            
            'COMP-001': {'base': 88.0, 'trend': 0.08, 'volatility': 2.0},  # Improving audit
            'COMP-002': {'base': 92.0, 'trend': 0.09, 'volatility': 2.5},  # Improving care plans
            
            'HR-001': {'base': 86.0, 'trend': 0.10, 'volatility': 2.0},  # Improving training
            'HR-002': {'base': 26.0, 'trend': -0.08, 'volatility': 1.5},  # Reducing turnover
            'HR-003': {'base': 6.2, 'trend': -0.02, 'volatility': 0.5},  # Reducing sickness
            'HR-004': {'base': 1.35, 'trend': 0.002, 'volatility': 0.05},  # Improving ratios
            'HR-005': {'base': 85.0, 'trend': 0.08, 'volatility': 2.5},  # Improving supervision
            'HR-006': {'base': 76.0, 'trend': 0.10, 'volatility': 3.0},  # Improving SVQ
        }
        
        count = 0
        for code, kpi in kpis.items():
            if code not in patterns:
                continue
            
            pattern = patterns[code]
            
            # Determine measurement frequency
            if kpi.reporting_frequency == 'DAILY':
                interval = 1
            elif kpi.reporting_frequency == 'WEEKLY':
                interval = 7
            elif kpi.reporting_frequency == 'MONTHLY':
                interval = 30
            elif kpi.reporting_frequency == 'QUARTERLY':
                interval = 90
            else:
                interval = 30
            
            # Create measurements
            current_date = start_date
            day_count = 0
            
            while current_date <= today:
                # Calculate value with trend and random variation
                trend_factor = 1 + (pattern['trend'] * day_count / 90)
                random_factor = 1 + (random.gauss(0, pattern['volatility']) / 100)
                
                actual_value = Decimal(str(pattern['base'] * trend_factor * random_factor))
                actual_value = actual_value.quantize(Decimal('0.01'))
                
                # Create measurement
                measurement = KPIMeasurement.objects.create(
                    kpi=kpi,
                    measurement_date=current_date,
                    actual_value=actual_value,
                    target_value=kpi.target_value,
                    recorded_by=admin,
                    notes=f'Automated measurement for {kpi.code}',
                )
                
                # Optionally assign to care home (50% chance)
                if care_homes and random.random() > 0.5:
                    measurement.care_home = random.choice(care_homes)
                    measurement.save()
                
                count += 1
                current_date += timedelta(days=interval)
                day_count += interval
        
        self.stdout.write(f'  ✓ Created {count} measurements across 90 days')

    def print_summary(self):
        """Print summary of created data."""
        self.stdout.write(self.style.SUCCESS('\n=== Summary ==='))
        
        perspectives = BalancedScorecardPerspective.objects.count()
        kpis = KPIDefinition.objects.count()
        dashboards = ExecutiveDashboard.objects.count()
        dashboard_kpis = DashboardKPI.objects.count()
        targets = PerformanceTarget.objects.count()
        benchmarks = BenchmarkData.objects.count()
        measurements = KPIMeasurement.objects.count()
        
        # RAG status distribution
        green = KPIMeasurement.objects.filter(rag_status='GREEN').count()
        amber = KPIMeasurement.objects.filter(rag_status='AMBER').count()
        red = KPIMeasurement.objects.filter(rag_status='RED').count()
        
        self.stdout.write(f'  Perspectives: {perspectives}')
        self.stdout.write(f'  KPI Definitions: {kpis}')
        self.stdout.write(f'  Executive Dashboards: {dashboards}')
        self.stdout.write(f'  Dashboard-KPI Links: {dashboard_kpis}')
        self.stdout.write(f'  Performance Targets: {targets}')
        self.stdout.write(f'  Benchmark Records: {benchmarks}')
        self.stdout.write(f'  KPI Measurements: {measurements}')
        self.stdout.write(f'')
        self.stdout.write(f'  RAG Status Distribution:')
        self.stdout.write(self.style.SUCCESS(f'    GREEN: {green} ({green*100//measurements if measurements else 0}%)'))
        self.stdout.write(self.style.WARNING(f'    AMBER: {amber} ({amber*100//measurements if measurements else 0}%)'))
        self.stdout.write(self.style.ERROR(f'    RED: {red} ({red*100//measurements if measurements else 0}%)'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Performance KPI data population complete!'))
        self.stdout.write('\nAccess dashboards at: http://localhost:8001/performance-kpis/')
