"""
Generate governance-ready compliance reports in multiple formats.
These reports are formatted for regulatory submissions, audit evidence, and governance documentation.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import json
import csv
import sys
from scheduling.models_audit import ComplianceCheck, ComplianceViolation, ComplianceRule, AuditReport
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Export governance-ready compliance reports for regulatory evidence'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            default='monthly',
            choices=['weekly', 'monthly', 'quarterly', 'annual'],
            help='Report period'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='pdf-text',
            choices=['pdf-text', 'json', 'csv', 'all'],
            help='Output format (pdf-text is print-ready text format)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (without extension)'
        )
        parser.add_argument(
            '--save-db',
            action='store_true',
            help='Save report to database'
        )

    def handle(self, *args, **options):
        period = options['period']
        output_format = options['format']
        output_path = options['output']
        save_db = options['save_db']
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('GOVERNANCE COMPLIANCE REPORT - EVIDENCE EXPORT'))
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(f'\nPeriod: {period.capitalize()}')
        self.stdout.write(f'Generated: {timezone.now().strftime("%d %B %Y at %H:%M:%S")}')
        
        # Calculate date range
        end_date = date.today()
        if period == 'weekly':
            start_date = end_date - timedelta(days=7)
        elif period == 'monthly':
            start_date = end_date - timedelta(days=30)
        elif period == 'quarterly':
            start_date = end_date - timedelta(days=90)
        else:  # annual
            start_date = end_date - timedelta(days=365)
        
        self.stdout.write(f'Date Range: {start_date.strftime("%d/%m/%Y")} to {end_date.strftime("%d/%m/%Y")}\n')
        
        # Generate report data
        report_data = self._generate_governance_report(start_date, end_date)
        
        # Output in requested format(s)
        if output_format == 'all':
            if output_path:
                self._export_pdf_text(report_data, start_date, end_date, f"{output_path}.txt")
                self._export_json(report_data, start_date, end_date, f"{output_path}.json")
                self._export_csv(report_data, start_date, end_date, f"{output_path}.csv")
            else:
                self.stdout.write(self.style.ERROR('\n⚠️  --output path required when using --format all'))
        elif output_format == 'pdf-text':
            if output_path:
                self._export_pdf_text(report_data, start_date, end_date, output_path + '.txt')
            else:
                self._output_pdf_text(report_data, start_date, end_date)
        elif output_format == 'json':
            if output_path:
                self._export_json(report_data, start_date, end_date, output_path + '.json')
            else:
                self._output_json(report_data, start_date, end_date)
        else:  # csv
            if output_path:
                self._export_csv(report_data, start_date, end_date, output_path + '.csv')
            else:
                self._output_csv(report_data, start_date, end_date)
        
        # Save to database if requested
        if save_db:
            self._save_to_database(report_data, period, start_date, end_date)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Governance report export complete\n'))

    def _generate_governance_report(self, start_date, end_date):
        """Generate comprehensive governance report data"""
        
        # Get all compliance checks in period
        checks = ComplianceCheck.objects.filter(
            check_date__range=[start_date, end_date]
        ).select_related('rule')
        
        # Get all violations
        violations = ComplianceViolation.objects.filter(
            detected_at__gte=timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time())),
            detected_at__lte=timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.max.time()))
        ).select_related('rule', 'affected_user')
        
        # Calculate summary statistics
        total_checks = checks.count()
        completed_checks = checks.filter(status='COMPLETED').count()
        failed_checks = checks.filter(status='FAILED').count()
        total_items = sum(c.items_checked for c in checks if c.items_checked)
        total_violations = violations.count()
        
        # Compliance rate
        compliance_rate = ((total_items - total_violations) / total_items * 100) if total_items > 0 else 100
        
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
        for category_code, category_name in ComplianceRule.RULE_CATEGORY_CHOICES:
            count = violations.filter(rule__category=category_code).count()
            if count > 0:
                category_breakdown[category_name] = count
        
        # Violations by status
        status_breakdown = {
            'OPEN': violations.filter(status='OPEN').count(),
            'ACKNOWLEDGED': violations.filter(status='ACKNOWLEDGED').count(),
            'IN_PROGRESS': violations.filter(status='IN_PROGRESS').count(),
            'RESOLVED': violations.filter(status='RESOLVED').count(),
            'ACCEPTED_RISK': violations.filter(status='ACCEPTED_RISK').count(),
            'FALSE_POSITIVE': violations.filter(status='FALSE_POSITIVE').count(),
        }
        
        # Top violated rules
        from django.db.models import Count
        top_violations = violations.values('rule__code', 'rule__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Critical/high open violations (governance priority)
        critical_open = violations.filter(
            severity__in=['CRITICAL', 'HIGH'],
            status='OPEN'
        ).order_by('-detected_at')[:20]
        
        return {
            'period': {
                'start': start_date,
                'end': end_date,
            },
            'summary': {
                'total_checks': total_checks,
                'completed_checks': completed_checks,
                'failed_checks': failed_checks,
                'total_items_checked': total_items,
                'total_violations': total_violations,
                'open_violations': status_breakdown['OPEN'],
                'resolved_violations': status_breakdown['RESOLVED'],
                'compliance_rate': round(compliance_rate, 2),
            },
            'severity_breakdown': severity_breakdown,
            'category_breakdown': category_breakdown,
            'status_breakdown': status_breakdown,
            'top_violations': list(top_violations),
            'critical_open_violations': critical_open,
            'all_violations': violations,
        }

    def _output_pdf_text(self, data, start_date, end_date):
        """Output print-ready text format"""
        self._print_governance_report(data, start_date, end_date, sys.stdout)

    def _export_pdf_text(self, data, start_date, end_date, filepath):
        """Export to text file"""
        with open(filepath, 'w') as f:
            self._print_governance_report(data, start_date, end_date, f)
        self.stdout.write(self.style.SUCCESS(f'\n📄 Text report saved to: {filepath}'))

    def _print_governance_report(self, data, start_date, end_date, output):
        """Generate formatted governance report"""
        
        output.write('\n' + '='*80 + '\n')
        output.write('COMPLIANCE & GOVERNANCE REPORT\n')
        output.write('Care Home - Regulatory Evidence Documentation\n')
        output.write('='*80 + '\n\n')
        
        output.write(f'Report Period: {start_date.strftime("%d %B %Y")} to {end_date.strftime("%d %B %Y")}\n')
        output.write(f'Generated: {timezone.now().strftime("%d %B %Y at %H:%M:%S")}\n')
        output.write(f'Report Type: Automated Compliance Monitoring\n')
        output.write('\n' + '-'*80 + '\n\n')
        
        # Executive Summary
        output.write('EXECUTIVE SUMMARY\n')
        output.write('-'*80 + '\n\n')
        output.write(f'Overall Compliance Rate: {data["summary"]["compliance_rate"]}%\n')
        output.write(f'Total Compliance Checks: {data["summary"]["total_checks"]}\n')
        output.write(f'Items Monitored: {data["summary"]["total_items_checked"]}\n')
        output.write(f'Violations Detected: {data["summary"]["total_violations"]}\n')
        output.write(f'  - Open/Requiring Action: {data["summary"]["open_violations"]}\n')
        output.write(f'  - Resolved: {data["summary"]["resolved_violations"]}\n\n')
        
        # Severity Analysis
        output.write('VIOLATIONS BY SEVERITY\n')
        output.write('-'*80 + '\n\n')
        for severity, count in data['severity_breakdown'].items():
            marker = '🔴' if severity == 'CRITICAL' else '🟠' if severity == 'HIGH' else '🟡' if severity == 'MEDIUM' else '🟢'
            output.write(f'{marker} {severity}: {count}\n')
        output.write('\n')
        
        # Category Analysis
        output.write('VIOLATIONS BY REGULATORY CATEGORY\n')
        output.write('-'*80 + '\n\n')
        for category, count in data['category_breakdown'].items():
            output.write(f'• {category}: {count} violation(s)\n')
        output.write('\n')
        
        # Top Violated Rules
        output.write('TOP VIOLATED COMPLIANCE RULES\n')
        output.write('-'*80 + '\n\n')
        for i, rule in enumerate(data['top_violations'][:5], 1):
            output.write(f'{i}. {rule["rule__name"]} ({rule["rule__code"]})\n')
            output.write(f'   Violations: {rule["count"]}\n\n')
        
        # Critical Open Items (for governance attention)
        critical_count = data['critical_open_violations'].count()
        if critical_count > 0:
            output.write('CRITICAL/HIGH PRIORITY OPEN ITEMS REQUIRING GOVERNANCE ATTENTION\n')
            output.write('-'*80 + '\n\n')
            for violation in data['critical_open_violations'][:10]:
                output.write(f'• [{violation.severity}] {violation.rule.name}\n')
                output.write(f'  Detected: {violation.detected_at.strftime("%d/%m/%Y %H:%M")}\n')
                output.write(f'  Description: {violation.description[:200]}\n')
                if violation.affected_user:
                    output.write(f'  Affected Staff: {violation.affected_user.full_name} ({violation.affected_user.sap})\n')
                output.write('\n')
        
        # Governance Statement
        output.write('\n' + '='*80 + '\n')
        output.write('GOVERNANCE CERTIFICATION\n')
        output.write('='*80 + '\n\n')
        output.write('This report provides automated compliance monitoring evidence for:\n')
        output.write('• CQC Regulatory Requirements\n')
        output.write('• Working Time Directive (WTD) Compliance\n')
        output.write('• Staffing Level Regulations\n')
        output.write('• Health & Safety Requirements\n')
        output.write('• Data Protection (GDPR) Compliance\n\n')
        output.write('Report generated by automated compliance monitoring system.\n')
        output.write('For queries contact: Compliance Team\n\n')
        output.write('='*80 + '\n\n')

    def _output_json(self, data, start_date, end_date):
        """Output JSON format to stdout"""
        json_data = self._prepare_json_data(data, start_date, end_date)
        print(json.dumps(json_data, indent=2, default=str))

    def _export_json(self, data, start_date, end_date, filepath):
        """Export to JSON file"""
        json_data = self._prepare_json_data(data, start_date, end_date)
        with open(filepath, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        self.stdout.write(self.style.SUCCESS(f'\n📊 JSON report saved to: {filepath}'))

    def _prepare_json_data(self, data, start_date, end_date):
        """Prepare data for JSON export"""
        return {
            'report_metadata': {
                'title': 'Compliance & Governance Report',
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'generated_at': timezone.now().isoformat(),
                'report_type': 'governance_compliance',
            },
            'summary': data['summary'],
            'severity_breakdown': data['severity_breakdown'],
            'category_breakdown': data['category_breakdown'],
            'status_breakdown': data['status_breakdown'],
            'top_violated_rules': data['top_violations'],
            'critical_open_violations': [
                {
                    'id': v.id,
                    'rule': v.rule.name,
                    'rule_code': v.rule.code,
                    'severity': v.severity,
                    'detected_at': v.detected_at.isoformat(),
                    'description': v.description,
                    'status': v.status,
                    'affected_user': v.affected_user.sap if v.affected_user else None,
                }
                for v in data['critical_open_violations']
            ]
        }

    def _output_csv(self, data, start_date, end_date):
        """Output CSV format to stdout"""
        self._write_csv(data, start_date, end_date, sys.stdout)

    def _export_csv(self, data, start_date, end_date, filepath):
        """Export to CSV file"""
        with open(filepath, 'w', newline='') as f:
            self._write_csv(data, start_date, end_date, f)
        self.stdout.write(self.style.SUCCESS(f'\n📊 CSV report saved to: {filepath}'))

    def _write_csv(self, data, start_date, end_date, output):
        """Write CSV data"""
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Compliance & Governance Report'])
        writer.writerow(['Period', f'{start_date} to {end_date}'])
        writer.writerow(['Generated', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Summary
        writer.writerow(['SUMMARY'])
        for key, value in data['summary'].items():
            writer.writerow([key.replace('_', ' ').title(), value])
        writer.writerow([])
        
        # Violations detail
        writer.writerow(['VIOLATIONS DETAIL'])
        writer.writerow(['ID', 'Rule Code', 'Rule Name', 'Severity', 'Status', 'Detected', 'Staff SAP', 'Description'])
        
        for v in data['all_violations']:
            writer.writerow([
                v.id,
                v.rule.code,
                v.rule.name,
                v.severity,
                v.status,
                v.detected_at.strftime('%Y-%m-%d %H:%M'),
                v.affected_user.sap if v.affected_user else 'N/A',
                v.description[:200]
            ])

    def _save_to_database(self, data, period, start_date, end_date):
        """Save report to database"""
        
        user = User.objects.filter(is_superuser=True).first()
        
        report = AuditReport.objects.create(
            report_type='COMPLIANCE_VIOLATIONS',
            title=f'{period.capitalize()} Governance Compliance Report',
            description='Automated governance compliance report for regulatory evidence',
            period_start=start_date,
            period_end=end_date,
            generated_by=user,
            status='COMPLETED',
            report_data={
                'summary': data['summary'],
                'severity_breakdown': data['severity_breakdown'],
                'category_breakdown': data['category_breakdown'],
                'status_breakdown': data['status_breakdown'],
                'top_violations': data['top_violations'],
            },
            total_records=data['summary']['total_violations'],
        )
        
        self.stdout.write(self.style.SUCCESS(f'\n💾 Report saved to database (ID: {report.id})'))
        self.stdout.write(f'   View at: /audit/reports/{report.id}/')
