"""
Proactive AI Suggestion Engine
Analyzes system state and generates intelligent suggestions for managers
"""

from django.utils import timezone
from django.db.models import Count, Q, Sum, Avg
from datetime import timedelta, date
import logging

from scheduling.models import (
    User, Shift, LeaveRequest, Unit, ShiftType, TrainingRecord
)
from scheduling.models_overtime import OvertimeCoverageRequest
from scheduling.models_multi_home import CareHome
from staff_records.models import SicknessRecord, StaffProfile

logger = logging.getLogger(__name__)


class ProactiveSuggestionEngine:
    """
    Generate contextual, actionable suggestions based on system analysis
    """
    
    def __init__(self, care_home=None, days_ahead=14):
        """
        Initialize suggestion engine
        
        Args:
            care_home: CareHome object to focus on (None = all homes)
            days_ahead: How many days to look forward for predictions
        """
        self.care_home = care_home
        self.days_ahead = days_ahead
        self.today = timezone.now().date()
        self.future_date = self.today + timedelta(days=days_ahead)
    
    def get_all_suggestions(self):
        """Get all proactive suggestions"""
        suggestions = []
        
        # Staffing-related suggestions
        suggestions.extend(self._uncovered_shifts_suggestions())
        suggestions.extend(self._leave_pattern_suggestions())
        suggestions.extend(self._training_expiry_suggestions())
        suggestions.extend(self._sickness_pattern_suggestions())
        
        # Operational suggestions
        suggestions.extend(self._overtime_budget_suggestions())
        suggestions.extend(self._fairness_suggestions())
        suggestions.extend(self._compliance_suggestions())
        
        # Sort by priority (high -> low)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return suggestions
    
    def _uncovered_shifts_suggestions(self):
        """Suggest action for uncovered shifts"""
        suggestions = []
        
        # Find shifts without staff in the next X days
        uncovered_query = Q(user__isnull=True) | Q(user__is_active=False)
        uncovered_shifts = Shift.objects.filter(
            uncovered_query,
            date__gte=self.today,
            date__lte=self.future_date
        )
        
        if self.care_home:
            uncovered_shifts = uncovered_shifts.filter(unit__care_home=self.care_home)
        
        uncovered_shifts = uncovered_shifts.select_related('shift_type', 'unit', 'role')
        
        # Group by urgency
        urgent = []  # Within 3 days
        soon = []    # 4-7 days
        future = []  # 8+ days
        
        for shift in uncovered_shifts:
            days_until = (shift.date - self.today).days
            shift_info = {
                'date': shift.date,
                'type': shift.shift_type.name,
                'unit': shift.unit.get_name_display(),
                'role': shift.role.get_name_display() if shift.role else 'Any',
                'shift_id': shift.id,
                'days_until': days_until
            }
            
            if days_until <= 3:
                urgent.append(shift_info)
            elif days_until <= 7:
                soon.append(shift_info)
            else:
                future.append(shift_info)
        
        # Generate suggestions based on urgency
        if urgent:
            suggestions.append({
                'priority': 'high',
                'category': 'staffing',
                'title': f'{len(urgent)} Urgent Uncovered Shifts (Next 3 Days)',
                'description': f'You have {len(urgent)} shifts without staff in the next 3 days that need immediate attention.',
                'action': 'Use Intelligent OT Distribution to contact available staff',
                'action_url': '/management/overtime/preferences/',
                'details': urgent[:5],  # Show first 5
                'icon': 'exclamation-triangle',
                'color': 'danger'
            })
        
        if soon:
            suggestions.append({
                'priority': 'medium',
                'category': 'staffing',
                'title': f'{len(soon)} Uncovered Shifts This Week',
                'description': f'{len(soon)} shifts need coverage in the next 4-7 days.',
                'action': 'Review and request OT coverage',
                'action_url': '/management/overtime/preferences/',
                'details': soon[:3],
                'icon': 'calendar-exclamation',
                'color': 'warning'
            })
        
        if future:
            suggestions.append({
                'priority': 'low',
                'category': 'staffing',
                'title': f'{len(future)} Uncovered Shifts Next 2 Weeks',
                'description': f'Plan ahead: {len(future)} shifts uncovered in days 8-{self.days_ahead}.',
                'action': 'Review staffing patterns',
                'action_url': '/management/view-rota/',
                'details': None,
                'icon': 'calendar',
                'color': 'info'
            })
        
        return suggestions
    
    def _leave_pattern_suggestions(self):
        """Suggest leave-related actions"""
        suggestions = []
        
        # Check for staff with low leave usage
        current_year_start = date(self.today.year, 1, 1)
        
        # Get all active staff
        active_staff = User.objects.filter(is_active=True, is_staff=False)
        
        # Calculate remaining leave for each staff
        low_leave_staff = []
        for staff in active_staff:
            # Get approved leave
            approved_leave = LeaveRequest.objects.filter(
                user=staff,
                status='approved',
                start_date__year=self.today.year
            ).aggregate(
                total_days=Sum('total_days')
            )['total_days'] or 0
            
            # Assume 28 days annual leave (could be from staff profile)
            annual_entitlement = 28
            remaining = annual_entitlement - approved_leave
            
            # Flag if more than 14 days remaining and less than 3 months left in year
            if remaining > 14 and self.today.month >= 10:
                low_leave_staff.append({
                    'name': staff.full_name,
                    'sap': staff.sap,
                    'remaining_days': remaining
                })
        
        if low_leave_staff:
            suggestions.append({
                'priority': 'medium',
                'category': 'leave',
                'title': f'{len(low_leave_staff)} Staff Need to Use Leave',
                'description': f'{len(low_leave_staff)} staff members have 14+ days leave remaining. Encourage bookings to avoid year-end rush.',
                'action': 'Review staff leave balances',
                'action_url': '/management/leave-requests/',
                'details': low_leave_staff[:5],
                'icon': 'umbrella-beach',
                'color': 'info'
            })
        
        # Check for pending leave requests
        pending_leave = LeaveRequest.objects.filter(
            status='pending',
            start_date__gte=self.today
        ).count()
        
        if pending_leave > 0:
            suggestions.append({
                'priority': 'medium',
                'category': 'leave',
                'title': f'{pending_leave} Pending Leave Requests',
                'description': f'{pending_leave} leave requests awaiting approval. Timely responses improve staff satisfaction.',
                'action': 'Review pending leave requests',
                'action_url': '/management/leave-requests/',
                'details': None,
                'icon': 'tasks',
                'color': 'warning'
            })
        
        return suggestions
    
    def _training_expiry_suggestions(self):
        """Suggest training renewal actions"""
        suggestions = []
        
        # Find training expiring soon (within 30 days)
        expiring_soon = TrainingRecord.objects.filter(
            expiry_date__lte=self.today + timedelta(days=30),
            expiry_date__gte=self.today
        ).select_related('staff_member')
        
        # Group by urgency
        expired = TrainingRecord.objects.filter(
            expiry_date__lt=self.today
        ).select_related('staff_member')
        
        if expired.exists():
            expired_list = [
                {
                    'name': t.staff_member.full_name,
                    'sap': t.staff_member.sap,
                    'training': t.course.name if hasattr(t, 'course') else 'Training',
                    'expired': (self.today - t.expiry_date).days
                }
                for t in expired[:10]
            ]
            
            suggestions.append({
                'priority': 'high',
                'category': 'training',
                'title': f'{expired.count()} Expired Training Records',
                'description': f'{expired.count()} training records have expired. This may impact compliance.',
                'recommendation': 'Review and renew expired training immediately',
                'action_url': '/management/training/compliance/',
                'affected_staff': [User.objects.get(sap=t.staff_member.sap) for t in expired[:5]],
            })
        
        if expiring_soon.exists():
            expiring_list = [
                {
                    'name': t.staff_member.full_name,
                    'sap': t.staff_member.sap,
                    'training': t.course.name if hasattr(t, 'course') else 'Training',
                    'days_until_expiry': (t.expiry_date - self.today).days
                }
                for t in expiring_soon[:10]
            ]
            
            suggestions.append({
                'priority': 'medium',
                'category': 'training',
                'title': f'{expiring_soon.count()} Training Records Expiring Soon',
                'description': f'{expiring_soon.count()} training records expire within 30 days. Book renewals now.',
                'recommendation': 'Schedule training renewals to maintain compliance',
                'action_url': '/management/training/compliance/',
                'affected_staff': [User.objects.get(sap=t.staff_member.sap) for t in expiring_soon[:5]],
            })
        
        return suggestions
    
    def _sickness_pattern_suggestions(self):
        """Suggest sickness-related actions"""
        suggestions = []
        
        # Find long-term sickness (14+ days)
        long_term_sick = SicknessRecord.objects.filter(
            status__in=['OPEN', 'AWAITING_FIT_NOTE'],
            total_working_days_sick__gte=14
        ).select_related('profile__user')
        
        if long_term_sick.exists():
            sick_list = [
                {
                    'name': s.profile.user.full_name,
                    'sap': s.profile.user.sap,
                    'days_sick': s.total_working_days_sick,
                    'status': s.get_status_display()
                }
                for s in long_term_sick
            ]
            
            suggestions.append({
                'priority': 'high',
                'category': 'hr',
                'title': f'{long_term_sick.count()} Long-Term Sickness Cases',
                'description': f'{long_term_sick.count()} staff off sick for 14+ days. May need occupational health referral.',
                'action': 'Review long-term sickness',
                'action_url': '/staff-records/sickness/',
                'details': sick_list,
                'icon': 'user-md',
                'color': 'warning'
            })
        
        # Check for high sickness rates (>5% of staff off sick)
        active_staff_count = User.objects.filter(is_active=True, is_staff=False).count()
        currently_sick = SicknessRecord.objects.filter(
            status__in=['OPEN', 'AWAITING_FIT_NOTE']
        ).count()
        
        if active_staff_count > 0:
            sickness_rate = (currently_sick / active_staff_count) * 100
            
            if sickness_rate > 5:
                suggestions.append({
                    'priority': 'high',
                    'category': 'hr',
                    'title': f'High Sickness Rate: {sickness_rate:.1f}%',
                    'description': f'{currently_sick} of {active_staff_count} staff currently off sick ({sickness_rate:.1f}%). Above 5% threshold.',
                    'action': 'Review sickness patterns and causes',
                    'action_url': '/staff-records/sickness/',
                    'details': None,
                    'icon': 'chart-line',
                    'color': 'danger'
                })
        
        return suggestions
    
    def _overtime_budget_suggestions(self):
        """Suggest overtime budget optimizations"""
        suggestions = []
        
        # Calculate OT usage this month
        current_month_start = self.today.replace(day=1)
        
        ot_shifts = Shift.objects.filter(
            date__gte=current_month_start,
            date__lte=self.today,
            is_overtime=True
        )
        
        if self.care_home:
            ot_shifts = ot_shifts.filter(unit__care_home=self.care_home)
        
        ot_count = ot_shifts.count()
        
        # Simple budget check (could be enhanced with actual budget model)
        if ot_count > 50:  # Threshold
            suggestions.append({
                'priority': 'medium',
                'category': 'budget',
                'title': f'High Overtime Usage This Month',
                'description': f'{ot_count} overtime shifts this month. Review patterns to optimize costs.',
                'action': 'Analyze overtime distribution',
                'action_url': '/management/overtime/preferences/',
                'details': None,
                'icon': 'pound-sign',
                'color': 'warning'
            })
        
        return suggestions
    
    def _fairness_suggestions(self):
        """Suggest fairness improvements"""
        suggestions = []
        
        # Check for staff working excessive overtime
        ot_distribution = Shift.objects.filter(
            is_overtime=True,
            date__gte=self.today - timedelta(days=30)
        ).values('user__full_name', 'user__sap').annotate(
            ot_count=Count('id')
        ).order_by('-ot_count')
        
        if ot_distribution.exists():
            top_ot = ot_distribution.first()
            if top_ot['ot_count'] > 10:  # More than 10 OT shifts in a month
                suggestions.append({
                    'priority': 'low',
                    'category': 'fairness',
                    'title': 'Overtime Distribution Imbalance',
                    'description': f"{top_ot['user__full_name']} has worked {top_ot['ot_count']} OT shifts this month. Consider spreading opportunities.",
                    'action': 'Review OT distribution fairness',
                    'action_url': '/management/overtime/preferences/',
                    'details': list(ot_distribution[:5]),
                    'icon': 'balance-scale',
                    'color': 'info'
                })
        
        return suggestions
    
    def _compliance_suggestions(self):
        """Suggest compliance-related actions"""
        suggestions = []
        
        # Check for shifts violating working time regulations (example: too many consecutive nights)
        # This would need more sophisticated logic in production
        
        return suggestions


# Convenience functions
def get_proactive_suggestions(care_home=None, days_ahead=14):
    """Get all proactive suggestions for a care home or all homes"""
    engine = ProactiveSuggestionEngine(care_home=care_home, days_ahead=days_ahead)
    return engine.get_all_suggestions()


def get_high_priority_suggestions(care_home=None):
    """Get only high-priority suggestions"""
    all_suggestions = get_proactive_suggestions(care_home=care_home)
    return [s for s in all_suggestions if s['priority'] == 'high']


def get_suggestions_by_category(category, care_home=None):
    """Get suggestions for a specific category"""
    all_suggestions = get_proactive_suggestions(care_home=care_home)
    return [s for s in all_suggestions if s['category'] == category]
