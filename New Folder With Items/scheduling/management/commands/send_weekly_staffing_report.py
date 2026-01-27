"""
Management command to send weekly additional staffing report (Overtime & Agency)
Should be scheduled to run every Monday morning for the previous week (Sunday-Saturday)
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, date
from collections import defaultdict

from scheduling.models import Shift, User, AgencyCompany


class Command(BaseCommand):
    help = 'Send weekly additional staffing report (Overtime & Agency) to management'

    def add_arguments(self, parser):
        parser.add_argument(
            '--week-start',
            type=str,
            help='Week start date (YYYY-MM-DD). If not provided, uses previous Sunday.',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send report to. If not provided, sends to all managers.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print report without sending email',
        )

    def handle(self, *args, **options):
        # Calculate week range (Sunday to Saturday)
        if options['week_start']:
            from datetime import datetime
            week_start = datetime.strptime(options['week_start'], '%Y-%m-%d').date()
        else:
            # Default to previous week
            today = timezone.now().date()
            days_since_sunday = (today.weekday() + 1) % 7
            week_start = today - timedelta(days=days_since_sunday + 7)
        
        week_end = week_start + timedelta(days=6)
        
        self.stdout.write(f'\n{"="*70}')
        self.stdout.write(f'WEEKLY ADDITIONAL STAFFING REPORT')
        self.stdout.write(f'Week: {week_start.strftime("%d %B %Y")} - {week_end.strftime("%d %B %Y")}')
        self.stdout.write(f'{"="*70}\n')
        
        # Get all additional staffing shifts for the week
        additional_shifts = Shift.objects.filter(
            date__range=[week_start, week_end],
            shift_classification__in=['OVERTIME', 'AGENCY']
        ).select_related('user', 'unit', 'shift_type', 'agency_company').order_by('date')
        
        if not additional_shifts.exists():
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ No additional staffing used during week {week_start.strftime("%d/%m")} - {week_end.strftime("%d/%m")}'
            ))
            if not options['dry_run']:
                self._send_no_usage_email(week_start, week_end, options.get('email'))
            return
        
        # Generate report data
        report_data = self._generate_report_data(week_start, week_end, additional_shifts)
        
        # Print report to console
        self._print_report(report_data)
        
        # Send email
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n⚠ DRY RUN - Email not sent'))
        else:
            self._send_email_report(report_data, options.get('email'))
            self.stdout.write(self.style.SUCCESS('\n✓ Weekly staffing report sent successfully!'))
    
    def _generate_report_data(self, week_start, week_end, shifts):
        """Generate structured report data"""
        
        daily_breakdown = {}
        overtime_totals = {'hours': 0, 'shifts': 0, 'staff': set()}
        agency_totals_by_company = defaultdict(lambda: {'hours': 0, 'cost': 0, 'shifts': 0, 'days': set()})
        
        # Initialize daily breakdown
        current_day = week_start
        while current_day <= week_end:
            daily_breakdown[current_day] = {
                'overtime': [],
                'agency': defaultdict(list),
                'overtime_hours': 0,
                'agency_hours': 0,
                'agency_cost': 0
            }
            current_day += timedelta(days=1)
        
        # Process shifts
        for shift in shifts:
            day_data = daily_breakdown[shift.date]
            
            if shift.shift_classification == 'OVERTIME':
                day_data['overtime'].append({
                    'staff': shift.user.full_name,
                    'sap': shift.user.sap,
                    'unit': shift.unit.get_name_display(),
                    'pattern': shift.get_shift_pattern_display(),
                    'hours': shift.duration_hours
                })
                day_data['overtime_hours'] += shift.duration_hours
                overtime_totals['hours'] += shift.duration_hours
                overtime_totals['shifts'] += 1
                overtime_totals['staff'].add(shift.user.sap)
                
            elif shift.shift_classification == 'AGENCY':
                company_name = shift.agency_company.name if shift.agency_company else 'Unknown Agency'
                shift_cost = (float(shift.agency_hourly_rate) if shift.agency_hourly_rate else 0) * shift.duration_hours
                
                day_data['agency'][company_name].append({
                    'agency_staff': shift.agency_staff_name or 'N/A',
                    'unit': shift.unit.get_name_display(),
                    'pattern': shift.get_shift_pattern_display(),
                    'hours': shift.duration_hours,
                    'rate': float(shift.agency_hourly_rate) if shift.agency_hourly_rate else 0,
                    'cost': shift_cost
                })
                day_data['agency_hours'] += shift.duration_hours
                day_data['agency_cost'] += shift_cost
                
                agency_totals_by_company[company_name]['hours'] += shift.duration_hours
                agency_totals_by_company[company_name]['cost'] += shift_cost
                agency_totals_by_company[company_name]['shifts'] += 1
                agency_totals_by_company[company_name]['days'].add(shift.date)
        
        return {
            'week_start': week_start,
            'week_end': week_end,
            'daily_breakdown': daily_breakdown,
            'overtime_totals': {
                'hours': round(overtime_totals['hours'], 2),
                'shifts': overtime_totals['shifts'],
                'unique_staff': len(overtime_totals['staff'])
            },
            'agency_totals': {
                company: {
                    'hours': round(data['hours'], 2),
                    'cost': round(data['cost'], 2),
                    'shifts': data['shifts'],
                    'days_used': len(data['days'])
                }
                for company, data in agency_totals_by_company.items()
            },
            'grand_totals': {
                'total_hours': round(
                    overtime_totals['hours'] + sum(d['hours'] for d in agency_totals_by_company.values()),
                    2
                ),
                'total_shifts': overtime_totals['shifts'] + sum(d['shifts'] for d in agency_totals_by_company.values()),
                'total_cost': round(sum(d['cost'] for d in agency_totals_by_company.values()), 2)
            }
        }
    
    def _print_report(self, data):
        """Print formatted report to console"""
        
        # Summary Section
        self.stdout.write(f'\n📊 SUMMARY')
        self.stdout.write(f'{"-"*70}')
        self.stdout.write(f'Total Additional Hours: {data["grand_totals"]["total_hours"]}')
        self.stdout.write(f'Total Additional Shifts: {data["grand_totals"]["total_shifts"]}')
        self.stdout.write(f'Total Agency Cost: £{data["grand_totals"]["total_cost"]:,.2f}')
        
        # Overtime Section
        if data['overtime_totals']['shifts'] > 0:
            self.stdout.write(f'\n⏰ OVERTIME')
            self.stdout.write(f'{"-"*70}')
            self.stdout.write(f'Total Overtime Hours: {data["overtime_totals"]["hours"]}')
            self.stdout.write(f'Total Overtime Shifts: {data["overtime_totals"]["shifts"]}')
            self.stdout.write(f'Staff Used for Overtime: {data["overtime_totals"]["unique_staff"]} people')
        
        # Agency Section
        if data['agency_totals']:
            self.stdout.write(f'\n🏢 AGENCY USAGE')
            self.stdout.write(f'{"-"*70}')
            for company, totals in data['agency_totals'].items():
                self.stdout.write(f'\n  {company}:')
                self.stdout.write(f'    - Total Hours: {totals["hours"]}')
                self.stdout.write(f'    - Total Shifts: {totals["shifts"]}')
                self.stdout.write(f'    - Days Used: {totals["days_used"]}')
                self.stdout.write(f'    - Total Cost: £{totals["cost"]:,.2f}')
        
        # Daily Breakdown
        self.stdout.write(f'\n📅 DAILY BREAKDOWN')
        self.stdout.write(f'{"-"*70}')
        for day_date, day_data in sorted(data['daily_breakdown'].items()):
            total_day_hours = day_data['overtime_hours'] + day_data['agency_hours']
            if total_day_hours > 0:
                self.stdout.write(f'\n{day_date.strftime("%A, %d %B")}:')
                self.stdout.write(f'  Overtime: {day_data["overtime_hours"]} hrs ({len(day_data["overtime"])} shifts)')
                self.stdout.write(f'  Agency: {day_data["agency_hours"]} hrs (£{day_data["agency_cost"]:,.2f})')
    
    def _send_email_report(self, data, recipient_email=None):
        """Send formatted HTML email report"""
        
        # Determine recipients
        if recipient_email:
            recipients = [recipient_email]
        else:
            # Send to all managers and operations managers
            managers = User.objects.filter(
                role__is_management=True,
                is_active=True,
                email__isnull=False
            ).exclude(email='')
            recipients = list(managers.values_list('email', flat=True))
        
        if not recipients:
            self.stdout.write(self.style.WARNING('⚠ No recipient email addresses found'))
            return
        
        subject = f'Weekly Staffing Report - {data["week_start"].strftime("%d/%m/%Y")} to {data["week_end"].strftime("%d/%m/%Y")}'
        
        # Build HTML email
        html_body = self._build_html_email(data)
        
        # Build plain text version
        text_body = self._build_text_email(data)
        
        try:
            send_mail(
                subject=subject,
                message=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                html_message=html_body,
                fail_silently=False,
            )
            self.stdout.write(f'  ✓ Sent to: {", ".join(recipients)}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error sending email: {str(e)}'))
    
    def _build_html_email(self, data):
        """Build HTML email content"""
        
        html = f'''
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #0d6efd; color: white; padding: 20px; text-align: center; }}
                .summary {{ background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #0d6efd; }}
                .section {{ margin: 20px 0; }}
                .section-title {{ font-size: 18px; font-weight: bold; color: #0d6efd; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6; }}
                th {{ background-color: #f8f9fa; font-weight: bold; }}
                .cost {{ color: #dc3545; font-weight: bold; }}
                .hours {{ color: #198754; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Weekly Additional Staffing Report</h1>
                <p>{data["week_start"].strftime("%d %B %Y")} - {data["week_end"].strftime("%d %B %Y")}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Total Additional Hours:</strong> <span class="hours">{data["grand_totals"]["total_hours"]} hours</span></p>
                <p><strong>Total Additional Shifts:</strong> {data["grand_totals"]["total_shifts"]}</p>
                <p><strong>Total Agency Cost:</strong> <span class="cost">£{data["grand_totals"]["total_cost"]:,.2f}</span></p>
            </div>
        '''
        
        # Overtime section
        if data['overtime_totals']['shifts'] > 0:
            html += f'''
            <div class="section">
                <div class="section-title">⏰ Overtime</div>
                <p><strong>Hours:</strong> {data["overtime_totals"]["hours"]}</p>
                <p><strong>Shifts:</strong> {data["overtime_totals"]["shifts"]}</p>
                <p><strong>Staff:</strong> {data["overtime_totals"]["unique_staff"]} people</p>
            </div>
            '''
        
        # Agency section
        if data['agency_totals']:
            html += '<div class="section"><div class="section-title">🏢 Agency Usage</div><table>'
            html += '<tr><th>Agency Company</th><th>Hours</th><th>Shifts</th><th>Days</th><th>Cost</th></tr>'
            for company, totals in data['agency_totals'].items():
                html += f'''
                <tr>
                    <td>{company}</td>
                    <td>{totals["hours"]}</td>
                    <td>{totals["shifts"]}</td>
                    <td>{totals["days_used"]}</td>
                    <td class="cost">£{totals["cost"]:,.2f}</td>
                </tr>
                '''
            html += '</table></div>'
        
        html += '</body></html>'
        return html
    
    def _build_text_email(self, data):
        """Build plain text email content"""
        
        text = f'''
WEEKLY ADDITIONAL STAFFING REPORT
{data["week_start"].strftime("%d %B %Y")} - {data["week_end"].strftime("%d %B %Y")}
{'='*70}

SUMMARY
-------
Total Additional Hours: {data["grand_totals"]["total_hours"]}
Total Additional Shifts: {data["grand_totals"]["total_shifts"]}
Total Agency Cost: £{data["grand_totals"]["total_cost"]:,.2f}
'''
        
        if data['overtime_totals']['shifts'] > 0:
            text += f'''
OVERTIME
--------
Hours: {data["overtime_totals"]["hours"]}
Shifts: {data["overtime_totals"]["shifts"]}
Staff: {data["overtime_totals"]["unique_staff"]} people
'''
        
        if data['agency_totals']:
            text += '\nAGENCY USAGE\n------------\n'
            for company, totals in data['agency_totals'].items():
                text += f'''
{company}:
  - Hours: {totals["hours"]}
  - Shifts: {totals["shifts"]}
  - Days: {totals["days_used"]}
  - Cost: £{totals["cost"]:,.2f}
'''
        
        return text
    
    def _send_no_usage_email(self, week_start, week_end, recipient_email=None):
        """Send email when no additional staffing was used"""
        
        if recipient_email:
            recipients = [recipient_email]
        else:
            managers = User.objects.filter(
                role__is_management=True,
                is_active=True,
                email__isnull=False
            ).exclude(email='')
            recipients = list(managers.values_list('email', flat=True))
        
        if not recipients:
            return
        
        subject = f'Weekly Staffing Report - {week_start.strftime("%d/%m/%Y")} to {week_end.strftime("%d/%m/%Y")}'
        message = f'''
No additional staffing (overtime or agency) was used during the week of {week_start.strftime("%d %B %Y")} - {week_end.strftime("%d %B %Y")}.

All shifts were covered by regular scheduled staff.
'''
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error sending email: {str(e)}'))
