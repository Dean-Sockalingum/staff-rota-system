"""
Rota Health Scoring System
Provides 0-100 quality score for rota with improvement suggestions
"""

from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import logging

from scheduling.models import Shift, User, LeaveRequest, Unit, ShiftType
from scheduling.models_multi_home import CareHome
from staff_records.models import SicknessRecord
from scheduling.models_overtime import StaffOvertimePreference

logger = logging.getLogger(__name__)


class RotaHealthScorer:
    """
    Comprehensive rota quality scoring system (0-100)
    
    Scoring Factors (weighted):
    - Staffing Levels (25%): Coverage vs. required ratios
    - Skill Mix (20%): Role distribution and qualifications
    - Fairness (15%): OT distribution, shift pattern equity
    - Cost Efficiency (15%): OT vs. contracted hours usage
    - Preferences (15%): Staff working preferred shifts/homes
    - Compliance (10%): WTD, minimum staffing, breaks
    """
    
    # Scoring weights (must sum to 100)
    WEIGHTS = {
        'staffing_levels': 25,
        'skill_mix': 20,
        'fairness': 15,
        'cost_efficiency': 15,
        'preferences': 15,
        'compliance': 10
    }
    
    def __init__(self, start_date, end_date, care_home=None, unit=None):
        """
        Initialize scorer for a date range
        
        Args:
            start_date: First date to analyze
            end_date: Last date to analyze  
            care_home: Optional CareHome to filter by
            unit: Optional Unit to filter by
        """
        self.start_date = start_date
        self.end_date = end_date
        self.care_home = care_home
        self.unit = unit
        
        # Get shifts in period
        self.shifts = Shift.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        if care_home:
            self.shifts = self.shifts.filter(unit__care_home=care_home)
        if unit:
            self.shifts = self.shifts.filter(unit=unit)
        
        self.shifts = self.shifts.select_related('user', 'role', 'shift_type', 'unit')
        
        # Component scores (calculated lazily)
        self._scores = {}
        self._issues = {}
        self._suggestions = {}
    
    def get_overall_score(self):
        """Calculate weighted overall score (0-100)"""
        component_scores = self.get_all_component_scores()
        
        weighted_sum = 0
        for component, score in component_scores.items():
            weight = self.WEIGHTS[component] / 100
            weighted_sum += score * weight
        
        return round(weighted_sum, 1)
    
    def get_all_component_scores(self):
        """Get all 6 component scores"""
        return {
            'staffing_levels': self._score_staffing_levels(),
            'skill_mix': self._score_skill_mix(),
            'fairness': self._score_fairness(),
            'cost_efficiency': self._score_cost_efficiency(),
            'preferences': self._score_preferences(),
            'compliance': self._score_compliance()
        }
    
    def get_grade(self):
        """Convert score to letter grade"""
        score = self.get_overall_score()
        
        if score >= 90:
            return 'A', 'Excellent'
        elif score >= 80:
            return 'B', 'Good'
        elif score >= 70:
            return 'C', 'Satisfactory'
        elif score >= 60:
            return 'D', 'Needs Improvement'
        else:
            return 'F', 'Poor'
    
    def get_all_issues(self):
        """Get all identified issues across components"""
        # Ensure all scores calculated (populates issues)
        self.get_all_component_scores()
        
        all_issues = []
        for component, issues in self._issues.items():
            for issue in issues:
                all_issues.append({
                    'component': component,
                    'severity': issue.get('severity', 'medium'),
                    'description': issue['description'],
                    'count': issue.get('count', 0)
                })
        
        # Sort by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        all_issues.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return all_issues
    
    def get_all_suggestions(self):
        """Get improvement suggestions"""
        # Ensure all scores calculated
        self.get_all_component_scores()
        
        all_suggestions = []
        for component, suggestions in self._suggestions.items():
            all_suggestions.extend([
                {
                    'component': component,
                    'priority': s.get('priority', 'medium'),
                    'action': s['action'],
                    'impact': s.get('impact', '')
                }
                for s in suggestions
            ])
        
        return all_suggestions
    
    # Individual scoring methods
    
    def _score_staffing_levels(self):
        """Score: Adequate staffing coverage (25% weight)"""
        score = 100
        issues = []
        suggestions = []
        
        # Count days analyzed
        days_count = (self.end_date - self.start_date).days + 1
        
        # Check for uncovered shifts
        uncovered = self.shifts.filter(Q(user__isnull=True) | Q(user__is_active=False))
        uncovered_count = uncovered.count()
        
        if uncovered_count > 0:
            uncovered_pct = (uncovered_count / max(self.shifts.count(), 1)) * 100
            deduction = min(30, uncovered_pct * 1.5)  # Max 30 points off
            score -= deduction
            
            issues.append({
                'severity': 'high' if uncovered_pct > 10 else 'medium',
                'description': f'{uncovered_count} uncovered shifts ({uncovered_pct:.1f}%)',
                'count': uncovered_count
            })
            
            suggestions.append({
                'priority': 'high',
                'action': 'Use Intelligent OT Distribution to fill uncovered shifts',
                'impact': f'Could improve score by up to {deduction:.0f} points'
            })
        
        # Check staff-to-resident ratios (simplified - would use actual ratios in production)
        # For now, just check if shifts have staff
        total_shifts = self.shifts.count()
        covered_shifts = total_shifts - uncovered_count
        
        if total_shifts > 0:
            coverage_rate = (covered_shifts / total_shifts) * 100
            if coverage_rate < 95:
                issues.append({
                    'severity': 'medium',
                    'description': f'Coverage rate {coverage_rate:.1f}% below 95% target'
                })
        
        self._scores['staffing_levels'] = max(0, score)
        self._issues['staffing_levels'] = issues
        self._suggestions['staffing_levels'] = suggestions
        
        return self._scores['staffing_levels']
    
    def _score_skill_mix(self):
        """Score: Appropriate role distribution (20% weight)"""
        score = 100
        issues = []
        suggestions = []
        
        # Analyze role distribution
        role_counts = {}
        for shift in self.shifts.filter(user__isnull=False):
            role_name = shift.user.role.name if shift.user.role else 'Unknown'
            role_counts[role_name] = role_counts.get(role_name, 0) + 1
        
        total_shifts_with_staff = sum(role_counts.values())
        
        if total_shifts_with_staff > 0:
            # Check for appropriate supervisory coverage (SSCW/SSCWN)
            supervisory_roles = ['SSCW', 'SSCWN', 'SM', 'OM']
            supervisory_count = sum(role_counts.get(role, 0) for role in supervisory_roles)
            supervisory_pct = (supervisory_count / total_shifts_with_staff) * 100
            
            # Expect 15-25% supervisory coverage
            if supervisory_pct < 15:
                deduction = (15 - supervisory_pct) * 2
                score -= deduction
                issues.append({
                    'severity': 'high',
                    'description': f'Low supervisory coverage: {supervisory_pct:.1f}% (target 15-25%)',
                    'count': supervisory_count
                })
                suggestions.append({
                    'priority': 'high',
                    'action': 'Increase SSCW/supervisory shifts to ensure adequate oversight',
                    'impact': 'Improves compliance and care quality'
                })
            elif supervisory_pct > 25:
                deduction = (supervisory_pct - 25) * 1
                score -= deduction
                issues.append({
                    'severity': 'low',
                    'description': f'High supervisory coverage: {supervisory_pct:.1f}% (may be over-staffed)',
                    'count': supervisory_count
                })
                suggestions.append({
                    'priority': 'low',
                    'action': 'Review supervisory ratios to optimize costs',
                    'impact': 'Could reduce staffing costs'
                })
        
        self._scores['skill_mix'] = max(0, score)
        self._issues['skill_mix'] = issues
        self._suggestions['skill_mix'] = suggestions
        
        return self._scores['skill_mix']
    
    def _score_fairness(self):
        """Score: Equitable shift distribution (15% weight)"""
        score = 100
        issues = []
        suggestions = []
        
        # Analyze OT distribution
        ot_shifts = self.shifts.filter(is_overtime=True, user__isnull=False)
        ot_by_staff = {}
        
        for shift in ot_shifts:
            staff_id = shift.user.id
            ot_by_staff[staff_id] = ot_by_staff.get(staff_id, 0) + 1
        
        if ot_by_staff:
            # Check for concentration (one person taking too many OT)
            max_ot = max(ot_by_staff.values())
            avg_ot = sum(ot_by_staff.values()) / len(ot_by_staff)
            
            if max_ot > avg_ot * 2:  # Someone has 2x average
                deduction = 15
                score -= deduction
                issues.append({
                    'severity': 'medium',
                    'description': f'OT concentrated: Max {max_ot} shifts vs avg {avg_ot:.1f}',
                })
                suggestions.append({
                    'priority': 'medium',
                    'action': 'Distribute OT more evenly using fairness-based ranking',
                    'impact': 'Improves staff satisfaction and reduces burnout'
                })
        
        # Check shift pattern variety (simplified)
        # In production, would analyze consecutive shifts, weekends, etc.
        
        self._scores['fairness'] = max(0, score)
        self._issues['fairness'] = issues
        self._suggestions['fairness'] = suggestions
        
        return self._scores['fairness']
    
    def _score_cost_efficiency(self):
        """Score: Optimal use of contracted vs. OT hours (15% weight)"""
        score = 100
        issues = []
        suggestions = []
        
        total_shifts = self.shifts.filter(user__isnull=False).count()
        ot_shifts = self.shifts.filter(is_overtime=True).count()
        
        if total_shifts > 0:
            ot_percentage = (ot_shifts / total_shifts) * 100
            
            # Expect < 15% OT usage
            if ot_percentage > 15:
                deduction = (ot_percentage - 15) * 2
                score -= deduction
                issues.append({
                    'severity': 'high' if ot_percentage > 25 else 'medium',
                    'description': f'High OT usage: {ot_percentage:.1f}% (target <15%)',
                    'count': ot_shifts
                })
                suggestions.append({
                    'priority': 'high',
                    'action': 'Review staffing model - consider hiring to reduce OT dependency',
                    'impact': f'Could save £{(ot_shifts * 12 * 1.5):.0f}/month'  # Rough estimate
                })
        
        self._scores['cost_efficiency'] = max(0, score)
        self._issues['cost_efficiency'] = issues
        self._suggestions['cost_efficiency'] = suggestions
        
        return self._scores['cost_efficiency']
    
    def _score_preferences(self):
        """Score: Staff working preferred shifts/homes (15% weight)"""
        score = 100
        issues = []
        suggestions = []
        
        # Analyze OT preference matches
        ot_shifts = self.shifts.filter(is_overtime=True, user__isnull=False)
        preference_matches = 0
        preference_total = 0
        
        for shift in ot_shifts:
            preference_total += 1
            
            # Check if staff has preference for this shift type/home
            has_preference = StaffOvertimePreference.objects.filter(
                staff=shift.user,
                care_home=shift.unit.care_home,
                willing_to_work=True
            ).exists()
            
            if has_preference:
                preference_matches += 1
        
        if preference_total > 0:
            match_rate = (preference_matches / preference_total) * 100
            
            if match_rate < 70:
                deduction = (70 - match_rate) * 0.5
                score -= deduction
                issues.append({
                    'severity': 'medium',
                    'description': f'Low preference match: {match_rate:.1f}% (target 70%+)'
                })
                suggestions.append({
                    'priority': 'medium',
                    'action': 'Use Intelligent OT system to match preferences',
                    'impact': 'Improves staff satisfaction and acceptance rates'
                })
        
        self._scores['preferences'] = max(0, score)
        self._issues['preferences'] = issues
        self._suggestions['preferences'] = suggestions
        
        return self._scores['preferences']
    
    def _score_compliance(self):
        """Score: WTD and regulatory compliance (10% weight)"""
        score = 100
        issues = []
        suggestions = []
        
        # Check for potential WTD violations (simplified)
        # In production, would use full WTD compliance module
        
        # Check for shifts with excessive hours
        long_shifts = self.shifts.filter(
            user__isnull=False,
            duration_hours__gt=12
        )
        
        if long_shifts.exists():
            count = long_shifts.count()
            deduction = min(30, count * 5)
            score -= deduction
            issues.append({
                'severity': 'high',
                'description': f'{count} shifts over 12 hours (potential WTD risk)',
                'count': count
            })
            suggestions.append({
                'priority': 'high',
                'action': 'Review long shifts for WTD compliance',
                'impact': 'Reduces regulatory risk'
            })
        
        self._scores['compliance'] = max(0, score)
        self._issues['compliance'] = issues
        self._suggestions['compliance'] = suggestions
        
        return self._scores['compliance']


# Convenience functions

def score_rota(start_date, end_date, care_home=None, unit=None):
    """
    Quick scoring for a rota period
    
    Returns:
        dict: Full scoring report
    """
    scorer = RotaHealthScorer(start_date, end_date, care_home, unit)
    
    component_scores = scorer.get_all_component_scores()
    overall_score = scorer.get_overall_score()
    grade, grade_label = scorer.get_grade()
    
    return {
        'overall_score': overall_score,
        'grade': grade,
        'grade_label': grade_label,
        'component_scores': component_scores,
        'issues': scorer.get_all_issues(),
        'suggestions': scorer.get_all_suggestions(),
        'period': {
            'start': start_date,
            'end': end_date,
            'days': (end_date - start_date).days + 1
        }
    }


def score_current_week(care_home=None):
    """Score the current week"""
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    return score_rota(start_of_week, end_of_week, care_home)


def score_next_week(care_home=None):
    """Score next week's rota"""
    today = timezone.now().date()
    start_of_next_week = today - timedelta(days=today.weekday()) + timedelta(days=7)
    end_of_next_week = start_of_next_week + timedelta(days=6)
    
    return score_rota(start_of_next_week, end_of_next_week, care_home)
