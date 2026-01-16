"""
Generate comprehensive compliance reports
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from scheduling.models import ComplianceRule, ComplianceCheck, ComplianceViolation, AuditReport
from django.db.models import Count, Q
import json


class Command(BaseCommand):
    help = 'Generate compliance reports for management'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            choices=['daily', 'weekly', 'monthly', 'quarterly', 'annual'],
            default='monthly',
            help='Report period',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['text', 'json', 'csv'],
            default='text',
            help='Output format',
        )
        parser.add_argument(
            '--save',
            action='store_true',
            help='Save report to database',
        )

    def handle(self, *args, **options):
        period = options['period']
        output_format = options['format']
        save_to_db = options['save']
        
        self.stdout.write(self.style.SUCCESS(f'\n📊 Generating Compliance Report'))
        self.stdout.write(f'Period: {period.capitalize()}')
        self.stdout.write(f'Format: {output_format.upper()}')
        self.stdout.write(f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        # Calculate date range
        end_date = date.today()
        if period == 'daily':
            start_date = end_date
        elif period == 'weekly':
            start_date = end_date - timedelta(days=7)
        elif period == 'monthly':
            start_date = end_date - timedelta(days=30)
        elif period == 'quarterly':
            start_date = end_date - timedelta(days=90)
        else:  # annual
            start_date = end_date - timedelta(days=365)
        
        # Generate report data
        report_data = self._generate_report_data(start_date, end_date)
        
        # Output in requested format
        if output_format == 'text':
            self._output_text(report_data, start_date, end_date)
        elif output_format == 'json':
            self._output_json(report_data)
        else:  # csv
            self._output_csv(report_data)
        
        # Save to database if requested
        if save_to_db:
            self._save_to_database(report_data, period, start_date, end_date)
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Report generation complete'))

    def _generate_report_data(self, start_date, end_date):
        """Generate comprehensive compliance report data"""
        
        # Get all checks in period
        checks = ComplianceCheck.objects.filter(
            check_date__gte=start_date,
            check_date__lte=end_date
        ).select_related('rule')
        
        # Get all violations in period
        violations = ComplianceViolation.objects.filter(
            detected_at__date__gte=start_date,
            detected_at__date__lte=end_date
        ).select_related('rule', 'affected_user')
        
        # Calculate statistics
        total_checks = checks.count()
        completed_checks = checks.filter(status='COMPLETED').count()
        failed_checks = checks.filter(status='FAILED').count()
        
        total_violations = violations.count()
        open_violations = violations.filter(status='OPEN').count()
        resolved_violations = violations.filter(status='RESOLVED').count()
        
        # Violations by severity
        severity_breakdown = {
            'CRITICAL': violations.filter(severity='CRITICAL').count(),
            'HIGH': violations.filter(severity='HIGH').count(),
            'MEDIUM': violations.filter(severity='MEDIUM').count(),
            'LOW': violations.filter(severity='LOW').count(),
            'INFO': violations.filter(severity='INFO').count(),
        }
        
        # Violations by category
        category_breakdown = {}
        for rule in ComplianceRule.objects.filter(is_active=True):
            count = violations.filter(rule__category=rule.category).count()
            if count > 0:
                category_breakdown[rule.get_category_display()] = count
        
        # Top violated rules
        top_violations = violations.values('rule__name', 'rule__code').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Staff with most violations
        staff_violations = violations.filter(
            affected_user__isnull=False
        ).values('affected_user__first_name', 'affected_user__last_name', 'affected_user__sap').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Compliance rate
        total_items_checked = sum(c.items_checked for c in checks)
        compliance_rate = ((total_items_checked - total_violations) / total_items_checked * 100) if total_items_checked > 0 else 100
        
        return {
            'summary': {
                'total_checks': total_checks,
                'completed_checks': completed_checks,
                'failed_checks': failed_checks,
                'total_violations': total_violations,
                'open_violations': open_violations,
                'resolved_violations': resolved_violations,
                'total_items_checked': total_items_checked,
                'compliance_rate': round(compliance_rate, 2),
            },
            'severity_breakdown': severity_breakdown,
            'category_breakdown': category_breakdown,
            'top_violations': list(top_violations),
            'staff_violations': list(staff_violations),
            'checks': checks,
            'violations': violations,
        }

    def _output_text(self, data, start_date, end_date):
        """Output report in text format"""
        
        summary = data['summary']
        
        report = f"""
{'=' * 80}
COMPLIANCE REPORT
{'=' * 80}
Period: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}
Generated: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}

EXECUTIVE SUMMARY
{'-' * 80}
Compliance Rate: {summary['compliance_rate']}%
Total Checks Performed: {summary['total_checks']}
Items Checked: {summary['total_items_checked']}
Violations Found: {summary['total_violations']}

VIOLATIONS BY SEVERITY
{'-' * 80}
🔴 Critical: {data['severity_breakdown']['CRITICAL']}
🟠 High: {data['severity_breakdown']['HIGH']}
🟡 Medium: {data['severity_breakdown']['MEDIUM']}
🟢 Low: {data['severity_breakdown']['LOW']}
ℹ️  Info: {data['severity_breakdown']['INFO']}

VIOLATIONS BY CATEGORY
{'-' * 80}
"""
        for category, count in data['category_breakdown'].items():
            report += f"{category}: {count}\n"
        
        report += f"""
VIOLATION STATUS
{'-' * 80}
Open: {summary['open_violations']}
Resolved: {summary['resolved_violations']}
Resolution Rate: {round((summary['resolved_violations'] / summary['total_violations'] * 100) if summary['total_violations'] > 0 else 0, 2)}%

TOP VIOLATED RULES
{'-' * 80}
"""
        for i, rule in enumerate(data['top_violations'][:5], 1):
            report += f"{i}. {rule['rule__name']} ({rule['rule__code']}): {rule['count']} violation(s)\n"
        
        if data['staff_violations']:
            report += f"""
STAFF WITH MOST VIOLATIONS
{'-' * 80}
"""
            for i, staff in enumerate(data['staff_violations'][:5], 1):
                staff_name = f"{staff['affected_user__first_name']} {staff['affected_user__last_name']}"
                report += f"{i}. {staff_name} ({staff['affected_user__sap']}): {staff['count']} violation(s)\n"
        
        report += f"""
{'=' * 80}
END OF REPORT
{'=' * 80}
"""
        
        self.stdout.write(report)

    def _output_json(self, data):
        """Output report in JSON format"""
        
        # Convert QuerySets to lists for JSON serialization
        json_data = {
            'summary': data['summary'],
            'severity_breakdown': data['severity_breakdown'],
            'category_breakdown': data['category_breakdown'],
            'top_violations': data['top_violations'],
            'staff_violations': data['staff_violations'],
        }
        
        self.stdout.write(json.dumps(json_data, indent=2))

    def _output_csv(self, data):
        """Output violations in CSV format"""
        import csv
        import sys
        
        writer = csv.writer(sys.stdout)
        
        # Header
        writer.writerow(['Rule Code', 'Rule Name', 'Severity', 'Status', 'Detected Date', 'Staff SAP', 'Staff Name', 'Description'])
        
        # Data rows
        for v in data['violations']:
            writer.writerow([
                v.rule.code,
                v.rule.name,
                v.severity,
                v.status,
                v.detected_at.strftime('%Y-%m-%d %H:%M'),
                v.affected_user.sap if v.affected_user else 'N/A',
                v.affected_user.full_name if v.affected_user else 'N/A',
                v.description[:100] + '...' if len(v.description) > 100 else v.description,
            ])

    def _save_to_database(self, data, period, start_date, end_date):
        """Save report to AuditReport table"""
        
        report = AuditReport.objects.create(
            report_type='COMPLIANCE_VIOLATIONS',
            title=f'{period.capitalize()} Compliance Report',
            description=f'Automated compliance report for {start_date} to {end_date}',
            period_start=start_date,
            period_end=end_date,
            status='COMPLETED',
            report_data={
                'summary': data['summary'],
                'severity_breakdown': data['severity_breakdown'],
                'category_breakdown': data['category_breakdown'],
                'top_violations': data['top_violations'],
                'staff_violations': data['staff_violations'],
            },
            total_records=data['summary']['total_violations'],
        )
        
        self.stdout.write(self.style.SUCCESS(f'\n💾 Report saved to database (ID: {report.id})'))
