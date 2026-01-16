"""
Management command to generate weekly Monday morning reports for management.

This command generates a comprehensive report covering Friday-Sunday events including:
- Sickness absences
- Overtime usage
- Agency staff usage
- Hospital admissions
- Deaths
- Incidents

Designed to run every Monday morning via cron job.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import timedelta, datetime
from scheduling.models import User, Shift, IncidentReport
from staff_records.models import SicknessRecord
import json


class Command(BaseCommand):
    help = 'Generate weekly Monday morning report covering Friday-Sunday events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Generate report for specific Monday (YYYY-MM-DD). Defaults to today if Monday, otherwise next Monday.',
        )
        parser.add_argument(
            '--email',
            action='store_true',
            help='Email the report to management team',
        )
        parser.add_argument(
            '--save',
            action='store_true',
            help='Save report to database',
        )

    def handle(self, *args, **options):
        # Determine the Monday date for the report
        if options.get('date'):
            report_monday = timezone.make_aware(
                datetime.strptime(options['date'], '%Y-%m-%d')
            )
            if report_monday.weekday() != 0:  # 0 = Monday
                self.stdout.write(
                    self.style.ERROR('Specified date must be a Monday')
                )
                return
        else:
            today = timezone.now()
            if today.weekday() == 0:  # Today is Monday
                report_monday = today
            else:
                # Calculate next Monday
                days_ahead = 0 - today.weekday()  # Monday is 0
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                report_monday = today + timedelta(days=days_ahead)

        # Calculate Friday-Sunday period (3 days before Monday)
        report_sunday = report_monday - timedelta(days=1)
        report_saturday = report_monday - timedelta(days=2)
        report_friday = report_monday - timedelta(days=3)

        # Set time boundaries
        period_start = report_friday.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = report_sunday.replace(hour=23, minute=59, second=59, microsecond=999999)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*80}\n'
                f'WEEKLY MANAGEMENT REPORT - MONDAY {report_monday.strftime("%d %B %Y")}\n'
                f'Covering: Friday {report_friday.strftime("%d %b")} - '
                f'Sunday {report_sunday.strftime("%d %b %Y")}\n'
                f'{"="*80}\n'
            )
        )

        report_data = {
            'report_date': report_monday.isoformat(),
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'sickness': self._get_sickness_data(period_start, period_end),
            'overtime': self._get_overtime_data(period_start, period_end),
            'agency_staff': self._get_agency_data(period_start, period_end),
            'incidents': self._get_incidents_data(period_start, period_end),
        }

        # Display report
        self._display_report(report_data)

        # Optionally save to file
        if options.get('save'):
            filename = f"/tmp/weekly_report_{report_monday.strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Report saved to: {filename}')
            )

        # Optionally email
        if options.get('email'):
            self._email_report(report_data)

    def _get_sickness_data(self, start, end):
        """Get sickness absences during the period"""
        # Get sickness records that were active during the weekend
        # A record is active if it started on or before the period end AND
        # either hasn't ended yet OR ended on or after the period start
        sickness_records = SicknessRecord.objects.filter(
            Q(first_working_day__lte=end.date()) &
            (
                Q(actual_last_working_day__gte=start.date()) | 
                Q(actual_last_working_day__isnull=True)
            )
        ).select_related('profile__user')

        data = {
            'total_staff_off_sick': sickness_records.count(),
            'records': []
        }

        for record in sickness_records:
            # Determine the end date for display
            end_date = record.actual_last_working_day or record.estimated_return_to_work
            
            data['records'].append({
                'staff_name': record.profile.user.full_name,
                'staff_sap': record.profile.user.sap,
                'first_working_day': record.first_working_day.isoformat() if record.first_working_day else None,
                'return_date': end_date.isoformat() if end_date else 'Ongoing',
                'status': record.status,
                'reason': record.reason or 'Not specified',
                'total_days': record.total_working_days_sick,
            })

        return data

    def _get_overtime_data(self, start, end):
        """Get overtime usage during the period"""
        # In this system, overtime is calculated as shifts exceeding contracted hours
        # For the weekend report, we'll count any extra shifts worked
        # Note: This is a simplified calculation - in production you may want to
        # compare against contracted shifts_per_week
        
        # For now, we'll report on total shifts worked during the weekend
        # which can be analyzed for overtime patterns
        weekend_shifts = Shift.objects.filter(
            date__gte=start.date(),
            date__lte=end.date(),
            status__in=['SCHEDULED', 'CONFIRMED']
        ).select_related('user', 'shift_type', 'unit')

        # Group by user to find who worked multiple shifts
        shifts_by_user = {}
        for shift in weekend_shifts:
            user_id = shift.user.sap
            if user_id not in shifts_by_user:
                shifts_by_user[user_id] = {
                    'user': shift.user,
                    'shifts': []
                }
            shifts_by_user[user_id]['shifts'].append(shift)

        # Identify potential overtime (staff working more than expected)
        total_shifts = weekend_shifts.count()
        total_hours = total_shifts * 12.5  # Standard shift length
        
        overtime_candidates = []
        for user_sap, data in shifts_by_user.items():
            # If someone worked more than 2 shifts over the weekend, it might be overtime
            if len(data['shifts']) > 2:
                overtime_candidates.extend(data['shifts'])

        data = {
            'total_weekend_shifts': total_shifts,
            'estimated_hours': total_hours,
            'potential_overtime_shifts': len(overtime_candidates),
            'shifts': []
        }

        # Report on all shifts (management can review for overtime)
        for shift in weekend_shifts[:50]:  # Limit to first 50 for report
            data['shifts'].append({
                'date': shift.date.isoformat(),
                'staff_name': shift.user.full_name,
                'staff_sap': shift.user.sap,
                'shift_type': shift.shift_type.get_name_display() if shift.shift_type else 'Unknown',
                'unit': shift.unit.get_name_display() if shift.unit else 'Unknown',
                'status': shift.status,
            })

        return data

    def _get_agency_data(self, start, end):
        """Get agency staff usage during the period"""
        # Agency staff identification may vary by system
        # Option 1: Check if user has specific words in their name/role
        # Option 2: Check for specific role codes
        # For now, we'll look for users whose SAP starts with 'AGY' or contains 'AGENCY'
        
        # Get all shifts for the weekend
        all_shifts = Shift.objects.filter(
            date__gte=start.date(),
            date__lte=end.date(),
            status__in=['SCHEDULED', 'CONFIRMED']
        ).select_related('user', 'user__role', 'shift_type', 'unit')

        # Try to identify agency staff (adjust criteria as needed)
        agency_shifts = []
        for shift in all_shifts:
            # Check if this looks like an agency staff member
            is_agency = (
                shift.user.sap.startswith('AGY') or
                shift.user.sap.startswith('AGENCY') or
                (shift.user.role and 'AGENCY' in shift.user.role.name.upper())
            )
            if is_agency:
                agency_shifts.append(shift)

        total_shifts = len(agency_shifts)
        # Group by agency staff member
        agency_usage = {}
        for shift in agency_shifts:
            staff_name = shift.user.full_name
            if staff_name not in agency_usage:
                agency_usage[staff_name] = {
                    'staff_sap': shift.user.sap,
                    'shift_count': 0,
                    'shifts': []
                }
            agency_usage[staff_name]['shift_count'] += 1
            agency_usage[staff_name]['shifts'].append({
                'date': shift.date.isoformat(),
                'shift_type': shift.shift_type.get_name_display() if shift.shift_type else 'Unknown',
                'unit': shift.unit.get_name_display() if shift.unit else 'Unknown',
            })

        data = {
            'total_agency_shifts': total_shifts,
            'unique_agency_staff': len(agency_usage),
            'estimated_cost': total_shifts * 350,  # Estimated £350 per agency shift
            'staff_usage': agency_usage
        }

        return data

    def _get_incidents_data(self, start, end):
        """Get incidents during the period including hospital admissions and deaths"""
        incidents = IncidentReport.objects.filter(
            incident_date__gte=start.date(),
            incident_date__lte=end.date()
        ).select_related('reported_by').order_by('-severity', 'incident_date')

        # Categorize incidents
        hospital_admissions = incidents.filter(hospital_admission=True)
        deaths = incidents.filter(severity='DEATH')
        
        # Check Care Inspectorate notifications (need to check each incident individually)
        care_inspectorate_count = sum(
            1 for incident in incidents 
            if incident.requires_care_inspectorate_notification()
        )

        data = {
            'total_incidents': incidents.count(),
            'hospital_admissions': hospital_admissions.count(),
            'deaths': deaths.count(),
            'care_inspectorate_notifications': care_inspectorate_count,
            'incidents_by_severity': {
                'death': deaths.count(),
                'high': incidents.filter(severity__in=['MAJOR_HARM', 'MODERATE_HARM']).count(),
                'medium': incidents.filter(severity='LOW_HARM').count(),
                'low': incidents.filter(severity='NO_HARM').count(),
            },
            'incidents_by_type': {},
            'all_incidents': []
        }

        # Count by type
        for incident in incidents:
            incident_type = incident.get_incident_type_display()
            if incident_type not in data['incidents_by_type']:
                data['incidents_by_type'][incident_type] = 0
            data['incidents_by_type'][incident_type] += 1

            # Add to detailed list
            data['all_incidents'].append({
                'reference_number': incident.reference_number,
                'date': incident.incident_date.isoformat(),
                'time': incident.incident_time.strftime('%H:%M') if incident.incident_time else 'Not specified',
                'type': incident_type,
                'severity': incident.severity,
                'person_affected': incident.service_user_name or 'Not specified',
                'description': incident.description[:200] if incident.description else 'No description',
                'reported_by': incident.reported_by.full_name if incident.reported_by else 'Unknown',
                'care_inspectorate_notification': incident.requires_care_inspectorate_notification(),
                'hospital_admission': incident.hospital_admission,
            })

        return data

    def _display_report(self, data):
        """Display the report in a formatted way"""
        
        # Sickness Section
        self.stdout.write(self.style.HTTP_INFO('\n1. SICKNESS ABSENCES'))
        self.stdout.write('-' * 80)
        sickness = data['sickness']
        self.stdout.write(f'Total staff off sick during period: {sickness["total_staff_off_sick"]}')
        if sickness['records']:
            self.stdout.write('\nDetails:')
            for record in sickness['records']:
                self.stdout.write(
                    f'  • {record["staff_name"]} ({record["staff_sap"]}) - '
                    f'Status: {record["status"]} - Days sick: {record["total_days"]}'
                )
                if record['reason']:
                    self.stdout.write(f'    Reason: {record["reason"]}')
                self.stdout.write(
                    f'    Period: {record["first_working_day"]} to {record["return_date"]}'
                )
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ No sickness absences recorded'))

        # Overtime Section
        self.stdout.write(self.style.HTTP_INFO('\n2. WEEKEND SHIFT COVERAGE & OVERTIME'))
        self.stdout.write('-' * 80)
        overtime = data['overtime']
        self.stdout.write(
            f'Total weekend shifts worked: {overtime["total_weekend_shifts"]} '
            f'(~{overtime["estimated_hours"]} hours)'
        )
        if overtime['potential_overtime_shifts'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'Potential overtime shifts (staff working 3+ shifts): '
                    f'{overtime["potential_overtime_shifts"]}'
                )
            )
        if overtime['shifts']:
            self.stdout.write('\nShift details (first 50):')
            for shift in overtime['shifts'][:20]:  # Show first 20 in terminal
                self.stdout.write(
                    f'  • {shift["date"]}: {shift["staff_name"]} ({shift["staff_sap"]}) - '
                    f'{shift["shift_type"]} at {shift["unit"]} - {shift["status"]}'
                )
            if len(overtime['shifts']) > 20:
                self.stdout.write(f'  ... and {len(overtime["shifts"]) - 20} more (see full report)')
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ No weekend shifts recorded'))

        # Agency Staff Section
        self.stdout.write(self.style.HTTP_INFO('\n3. AGENCY STAFF USAGE'))
        self.stdout.write('-' * 80)
        agency = data['agency_staff']
        self.stdout.write(
            f'Total agency shifts: {agency["total_agency_shifts"]} '
            f'(Estimated cost: £{agency["estimated_cost"]:,})'
        )
        self.stdout.write(f'Unique agency staff used: {agency["unique_agency_staff"]}')
        if agency['staff_usage']:
            self.stdout.write('\nDetails:')
            for staff_name, usage in agency['staff_usage'].items():
                self.stdout.write(
                    f'  • {staff_name} ({usage["staff_sap"]}): {usage["shift_count"]} shifts'
                )
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ No agency staff usage recorded'))

        # Incidents Section
        self.stdout.write(self.style.HTTP_INFO('\n4. INCIDENTS & SERIOUS EVENTS'))
        self.stdout.write('-' * 80)
        incidents = data['incidents']
        self.stdout.write(f'Total incidents: {incidents["total_incidents"]}')
        
        if incidents['deaths'] > 0:
            self.stdout.write(
                self.style.ERROR(f'  ⚠ DEATHS: {incidents["deaths"]}')
            )
        
        if incidents['hospital_admissions'] > 0:
            self.stdout.write(
                self.style.WARNING(f'  ⚠ Hospital admissions: {incidents["hospital_admissions"]}')
            )
        
        if incidents['care_inspectorate_notifications'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'  ⚠ Care Inspectorate notifications required: '
                    f'{incidents["care_inspectorate_notifications"]}'
                )
            )

        if incidents['total_incidents'] > 0:
            self.stdout.write('\nBreakdown by severity:')
            severity = incidents['incidents_by_severity']
            if severity['death'] > 0:
                self.stdout.write(self.style.ERROR(f'  • Death: {severity["death"]}'))
            if severity['high'] > 0:
                self.stdout.write(self.style.ERROR(f'  • High: {severity["high"]}'))
            if severity['medium'] > 0:
                self.stdout.write(self.style.WARNING(f'  • Medium: {severity["medium"]}'))
            if severity['low'] > 0:
                self.stdout.write(f'  • Low: {severity["low"]}')

            self.stdout.write('\nBreakdown by type:')
            for inc_type, count in incidents['incidents_by_type'].items():
                self.stdout.write(f'  • {inc_type}: {count}')

            self.stdout.write('\nDetailed incident list:')
            for inc in incidents['all_incidents']:
                style = self.style.ERROR if inc['severity'] in ['DEATH', 'HIGH'] else self.style.WARNING
                self.stdout.write(
                    style(
                        f'  • {inc["reference_number"]} - {inc["date"]} {inc["time"]}'
                    )
                )
                self.stdout.write(f'    Type: {inc["type"]} | Severity: {inc["severity"]}')
                self.stdout.write(f'    Person affected: {inc["person_affected"]}')
                self.stdout.write(f'    Reported by: {inc["reported_by"]}')
                if inc['care_inspectorate_notification']:
                    self.stdout.write(
                        self.style.ERROR('    ⚠ Care Inspectorate notification REQUIRED')
                    )
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ No incidents recorded'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('END OF WEEKLY REPORT'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

    def _email_report(self, data):
        """Email the report to management team (placeholder for future implementation)"""
        self.stdout.write(
            self.style.WARNING(
                '\n⚠ Email functionality not yet implemented. '
                'Report data has been generated and can be saved to file.'
            )
        )
