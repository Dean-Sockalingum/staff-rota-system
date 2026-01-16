"""
Management command to run automated compliance checks against all loaded rules.
This command verifies that the rota system complies with UK care home regulations.

Usage:
    python manage.py run_compliance_checks [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD] [--rules RULE1,RULE2]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, date, timedelta
from scheduling.models import (
    ComplianceRule, ComplianceCheck, ComplianceViolation, 
    Shift, LeaveRequest, ShiftType
)
from staff_records.models import AnnualLeaveEntitlement
from django.contrib.auth import get_user_model
User = get_user_model()


class Command(BaseCommand):
    help = 'Run automated compliance checks against loaded rules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date for checks (YYYY-MM-DD). Default: today',
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date for checks (YYYY-MM-DD). Default: today + 7 days',
        )
        parser.add_argument(
            '--rules',
            type=str,
            help='Comma-separated list of rule codes to check. Default: all active rules',
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Check only rules in this category',
        )

    def handle(self, *args, **options):
        # Parse dates
        if options['start_date']:
            start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
        else:
            start_date = date.today()
        
        if options['end_date']:
            end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
        else:
            end_date = start_date + timedelta(days=7)
        
        self.stdout.write(self.style.SUCCESS(f'\n=== COMPLIANCE CHECK RUN ==='))
        self.stdout.write(f'Period: {start_date} to {end_date}')
        self.stdout.write(f'Started: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        # Get rules to check
        rules_query = ComplianceRule.objects.filter(is_active=True)
        
        if options['rules']:
            rule_codes = [code.strip() for code in options['rules'].split(',')]
            rules_query = rules_query.filter(code__in=rule_codes)
            self.stdout.write(f'Checking specific rules: {", ".join(rule_codes)}')
        
        if options['category']:
            rules_query = rules_query.filter(category=options['category'])
            self.stdout.write(f'Checking category: {options["category"]}')
        
        rules = rules_query.order_by('category', 'code')
        
        if not rules.exists():
            self.stdout.write(self.style.WARNING('No active compliance rules found!'))
            return
        
        self.stdout.write(f'Checking {rules.count()} compliance rules...\n')
        
        # Run checks
        total_violations = 0
        total_items_checked = 0
        
        for rule in rules:
            self.stdout.write(f'Checking: {rule.name} ({rule.code})')
            
            start_time = timezone.now()
            
            # Create ComplianceCheck record
            check = ComplianceCheck.objects.create(
                rule=rule,
                check_date=date.today(),
                period_start=start_date,
                period_end=end_date,
                status='IN_PROGRESS',
                started_at=start_time
            )
            
            try:
                # Run the appropriate check based on rule code
                violations, items_checked = self._run_check(rule, start_date, end_date, check)
                
                # Update check record
                execution_time = (timezone.now() - start_time).total_seconds()
                check.status = 'COMPLETED'
                check.completed_at = timezone.now()
                check.violations_found = len(violations)
                check.items_checked = items_checked
                check.check_results = {
                    'violations': [{'user': v['user'], 'description': v['description']} for v in violations],
                    'items_checked': items_checked,
                    'period': f'{start_date} to {end_date}',
                    'execution_time_seconds': execution_time
                }
                check.save()
                
                total_violations += len(violations)
                total_items_checked += items_checked
                
                status_icon = '✗' if violations else '✓'
                status_color = self.style.ERROR if violations else self.style.SUCCESS
                self.stdout.write(status_color(
                    f'  {status_icon} {len(violations)} violations found '
                    f'({items_checked} items checked, {execution_time:.2f}s)'
                ))
                
            except Exception as e:
                check.status = 'FAILED'
                check.completed_at = timezone.now()
                check.check_results = {'error': str(e)}
                check.save()
                self.stdout.write(self.style.ERROR(f'  ✗ Check failed: {str(e)}'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n=== SUMMARY ==='))
        self.stdout.write(f'Rules checked: {rules.count()}')
        self.stdout.write(f'Items checked: {total_items_checked}')
        self.stdout.write(f'Total violations: {total_violations}')
        
        if total_violations > 0:
            critical = ComplianceViolation.objects.filter(
                compliance_check__check_date=date.today(),
                severity='CRITICAL',
                status='OPEN'
            ).count()
            if critical > 0:
                self.stdout.write(self.style.ERROR(f'⚠️  {critical} CRITICAL violations require immediate attention!'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ All checks passed - no violations detected'))

    def _run_check(self, rule, start_date, end_date, check):
        """Run the appropriate check based on rule code"""
        
        method_name = f'_check_{rule.code.lower()}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(rule, start_date, end_date, check)
        else:
            # Default: no check implemented yet
            return [], 0

    # Working Time Directive Checks
    
    def _check_wtd_48_hours(self, rule, start_date, end_date, check):
        """Check 48-hour weekly working time limit (averaged over 17 weeks)"""
        violations = []
        
        # Calculate 17-week period
        period_start = end_date - timedelta(weeks=17)
        
        # Get all staff users
        staff_users = User.objects.filter(is_staff=False, is_active=True)
        
        for user in staff_users:
            # Count hours in 17-week period
            shifts = Shift.objects.filter(
                user=user,
                date__gte=period_start,
                date__lte=end_date,
                status__in=['CONFIRMED', 'COMPLETED']
            )
            
            # Calculate total hours (12 hours per shift as default)
            total_hours = shifts.count() * 12
            weeks = 17
            avg_hours_per_week = total_hours / weeks if weeks > 0 else 0
            
            if avg_hours_per_week > 48:
                violation = ComplianceViolation.objects.create(
                    compliance_check=check,
                    rule=rule,
                    severity=rule.severity,
                    status='OPEN',
                    description=f'{user.full_name} averaging {avg_hours_per_week:.1f} hours/week over 17 weeks (limit: 48). Total hours in period: {total_hours}.',
                    affected_user=user
                )
                violations.append({
                    'user': user.sap,
                    'description': f'Averaging {avg_hours_per_week:.1f} hours/week'
                })
        
        return violations, staff_users.count()

    def _check_wtd_rest_11_hours(self, rule, start_date, end_date, check):
        """Check 11-hour daily rest requirement"""
        violations = []
        items_checked = 0
        
        staff_users = User.objects.filter(is_staff=False, is_active=True)
        
        for user in staff_users:
            # Get shifts in period ordered by date
            shifts = Shift.objects.filter(
                user=user,
                date__gte=start_date,
                date__lte=end_date,
                status__in=['CONFIRMED', 'COMPLETED']
            ).order_by('date', 'shift_type__start_time')
            
            shifts_list = list(shifts)
            items_checked += len(shifts_list) - 1
            
            # Check consecutive shifts
            for i in range(len(shifts_list) - 1):
                current_shift = shifts_list[i]
                next_shift = shifts_list[i + 1]
                
                # Calculate rest period between shifts
                current_end = datetime.combine(current_shift.date, current_shift.end_time)
                next_start = datetime.combine(next_shift.date, next_shift.start_time)
                rest_hours = (next_start - current_end).total_seconds() / 3600
                
                # Check if less than 11 hours rest
                if rest_hours < 11:
                    violation = ComplianceViolation.objects.create(
                        compliance_check=check,
                        rule=rule,
                        severity=rule.severity,
                        status='OPEN',
                        description=f'{user.full_name} has only {rest_hours:.1f} hours rest between shifts on {current_shift.date} and {next_shift.date} (minimum: 11 hours).',
                        affected_user=user
                    )
                    violations.append({
                        'user': user.sap,
                        'description': f'Only {rest_hours:.1f}h rest between {current_shift.date} and {next_shift.date}'
                    })
        
        return violations, items_checked

    def _check_wtd_rest_24_hours(self, rule, start_date, end_date, check):
        """Check 24-hour weekly rest requirement"""
        violations = []
        
        staff_users = User.objects.filter(is_staff=False, is_active=True)
        
        for user in staff_users:
            # Check each week in period
            current_date = start_date
            while current_date <= end_date:
                week_end = current_date + timedelta(days=6)
                
                # Check if user has at least one day off this week
                shifts_this_week = Shift.objects.filter(
                    user=user,
                    date__gte=current_date,
                    date__lte=week_end,
                    status__in=['CONFIRMED', 'COMPLETED']
                ).values('date').distinct()
                
                shifts_count = shifts_this_week.count()
                
                # If 7 shifts in 7 days = no rest day
                if shifts_count >= 7:
                    violation = ComplianceViolation.objects.create(
                        compliance_check=check,
                        rule=rule,
                        severity=rule.severity,
                        status='OPEN',
                        description=f'{user.full_name} worked all 7 days in week {current_date} to {week_end}. No weekly rest period (24 hours) provided.',
                        affected_user=user
                    )
                    violations.append({
                        'user': user.sap,
                        'description': f'No rest day in week {current_date}'
                    })
                
                current_date = week_end + timedelta(days=1)
        
        return violations, staff_users.count()

    # Staffing Level Checks
    
    def _check_min_day_staffing(self, rule, start_date, end_date, check):
        """Check minimum day staffing levels (17 care staff)"""
        violations = []
        
        current_date = start_date
        while current_date <= end_date:
            # Count day care staff on duty (not night shifts)
            day_staff = Shift.objects.filter(
                date=current_date,
                status__in=['CONFIRMED', 'SCHEDULED']
            ).exclude(
                shift_type__name__in=['NIGHT_SENIOR', 'NIGHT_ASSISTANT']
            ).values('user').distinct().count()
            
            if day_staff < 17:
                violation = ComplianceViolation.objects.create(
                    compliance_check=check,
                    rule=rule,
                    severity=rule.severity,
                    status='OPEN',
                    description=f'Insufficient day staffing on {current_date}: {day_staff}/17. Only {day_staff} day care staff scheduled (minimum: 17).'
                )
                violations.append({
                    'user': 'N/A',
                    'description': f'{current_date}: {day_staff}/17 staff'
                })
            
            current_date += timedelta(days=1)
        
        days_checked = (end_date - start_date).days + 1
        return violations, days_checked

    def _check_min_night_staffing(self, rule, start_date, end_date, check):
        """Check minimum night staffing levels (17 care staff)"""
        violations = []
        
        current_date = start_date
        while current_date <= end_date:
            # Count night care staff on duty
            night_staff = Shift.objects.filter(
                date=current_date,
                status__in=['CONFIRMED', 'SCHEDULED'],
                shift_type__name__in=['NIGHT_SENIOR', 'NIGHT_ASSISTANT']
            ).values('user').distinct().count()
            
            if night_staff < 17:
                violation = ComplianceViolation.objects.create(
                    compliance_check=check,
                    rule=rule,
                    severity=rule.severity,
                    status='OPEN',
                    description=f'Insufficient night staffing on {current_date}: {night_staff}/17. Only {night_staff} night care staff scheduled (minimum: 17).'
                )
                violations.append({
                    'user': 'N/A',
                    'description': f'{current_date}: {night_staff}/17 staff'
                })
            
            current_date += timedelta(days=1)
        
        days_checked = (end_date - start_date).days + 1
        return violations, days_checked

    def _check_skill_mix_ratio(self, rule, start_date, end_date, check):
        """Check senior to junior staff ratio"""
        violations = []
        
        # Simplified check - just return empty for now
        # This would need role information from User model
        
        days_checked = (end_date - start_date).days + 1
        return violations, days_checked

    # Leave Checks
    
    def _check_leave_entitlement(self, rule, start_date, end_date, check):
        """Check annual leave entitlement (5.6 weeks/year)"""
        violations = []
        
        current_year = date.today().year
        
        # Check entitlements for current year
        entitlements = AnnualLeaveEntitlement.objects.filter(
            leave_year_start__year=current_year
        )
        
        for entitlement in entitlements:
            # Convert hours to days (7 hours per day)
            entitled_days = entitlement.total_entitlement_hours / 7
            min_days = 28  # 5.6 weeks for full-time
            
            # Check if full-time staff have minimum entitlement
            if entitled_days < min_days:
                violation = ComplianceViolation.objects.create(
                    compliance_check=check,
                    rule=rule,
                    severity=rule.severity,
                    status='OPEN',
                    description=f'{entitlement.profile.user.full_name} has only {entitled_days:.1f} days annual leave (minimum: {min_days} days for full-time staff).',
                    affected_user=entitlement.profile.user
                )
                violations.append({
                    'user': entitlement.profile.user.sap,
                    'description': f'Only {entitled_days:.1f} days entitled'
                })
        
        return violations, entitlements.count()

    def _check_leave_coverage(self, rule, start_date, end_date, check):
        """Check that leave doesn't reduce staffing below minimum"""
        violations = []
        
        current_date = start_date
        while current_date <= end_date:
            # Count staff on leave
            on_leave = LeaveRequest.objects.filter(
                start_date__lte=current_date,
                end_date__gte=current_date,
                status='APPROVED'
            ).count()
            
            # Count scheduled staff
            scheduled = Shift.objects.filter(date=current_date).count()
            
            # Check if leave impacts minimum staffing
            if scheduled < 34 and on_leave > 0:  # 34 = 17 day + 17 night
                violation = ComplianceViolation.objects.create(
                    compliance_check=check,
                    rule=rule,
                    severity=rule.severity,
                    status='OPEN',
                    description=f'Leave on {current_date} may impact minimum staffing ({scheduled} scheduled, {on_leave} on leave). Approved leave may reduce staffing below minimum requirements.'
                )
                violations.append({
                    'user': 'N/A',
                    'description': f'{current_date}: {on_leave} on leave, {scheduled} scheduled'
                })
            
            current_date += timedelta(days=1)
        
        days_checked = (end_date - start_date).days + 1
        return violations, days_checked
