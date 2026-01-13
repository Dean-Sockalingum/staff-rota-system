"""
Staff Performance Tracking Service

Tracks attendance, punctuality, shift completion rates,
and calculates performance metrics and scores.
"""

from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal


def record_attendance(staff_member, shift, status='PRESENT', actual_start=None, actual_end=None, 
                     reason_for_absence='', documentation_provided=False):
    """Record staff attendance for a shift"""
    from .models import AttendanceRecord
    
    record, created = AttendanceRecord.objects.get_or_create(
        staff_member=staff_member,
        shift=shift,
        defaults={
            'date': shift.date,
            'shift_type': shift.shift_type,
            'status': status,
            'scheduled_start': shift.start_time if hasattr(shift, 'start_time') else timezone.now().time(),
            'scheduled_end': shift.end_time if hasattr(shift, 'end_time') else timezone.now().time(),
            'actual_start': actual_start,
            'actual_end': actual_end,
            'reason_for_absence': reason_for_absence,
            'documentation_provided': documentation_provided,
        }
    )
    
    if not created:
        record.status = status
        record.actual_start = actual_start
        record.actual_end = actual_end
        record.reason_for_absence = reason_for_absence
        record.documentation_provided = documentation_provided
        record.save()
    
    return record


def calculate_performance_metrics(staff_member, start_date=None, end_date=None):
    """Calculate performance metrics for a staff member over a period"""
    from .models import AttendanceRecord, Shift
    
    if not end_date:
        end_date = timezone.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get all shifts for this staff member in the period
    shifts = Shift.objects.filter(
        staff_member=staff_member,
        date__gte=start_date,
        date__lte=end_date
    )
    
    total_shifts = shifts.count()
    
    if total_shifts == 0:
        return {
            'total_shifts': 0,
            'shifts_attended': 0,
            'shifts_late': 0,
            'shifts_absent': 0,
            'unauthorized_absences': 0,
            'shifts_completed': 0,
            'total_minutes_late': 0,
            'attendance_rate': 100,
            'punctuality_rate': 100,
            'completion_rate': 100,
            'attendance_score': 100,
            'punctuality_score': 100,
            'completion_score': 100,
            'overall_score': 100,
        }
    
    # Get attendance records
    attendance_records = AttendanceRecord.objects.filter(
        staff_member=staff_member,
        date__gte=start_date,
        date__lte=end_date
    )
    
    # Count by status
    shifts_attended = attendance_records.filter(
        status__in=['PRESENT', 'LATE']
    ).count()
    
    shifts_late = attendance_records.filter(status='LATE').count()
    
    shifts_absent = attendance_records.filter(
        status__in=['ABSENT', 'UNAUTHORIZED']
    ).count()
    
    unauthorized_absences = attendance_records.filter(
        status='UNAUTHORIZED'
    ).count()
    
    shifts_completed = attendance_records.filter(
        shift_completed=True
    ).count()
    
    # Calculate total minutes late
    total_minutes_late = attendance_records.aggregate(
        total=Sum('minutes_late')
    )['total'] or 0
    
    # Calculate rates
    attendance_rate = (shifts_attended / total_shifts * 100) if total_shifts > 0 else 100
    
    on_time_shifts = shifts_attended - shifts_late
    punctuality_rate = (on_time_shifts / total_shifts * 100) if total_shifts > 0 else 100
    
    completion_rate = (shifts_completed / total_shifts * 100) if total_shifts > 0 else 100
    
    # Calculate scores (same as rates for simplicity)
    attendance_score = attendance_rate
    punctuality_score = punctuality_rate
    completion_score = completion_rate
    
    # Overall score (weighted average)
    overall_score = (
        attendance_score * Decimal('0.4') +
        punctuality_score * Decimal('0.3') +
        completion_score * Decimal('0.3')
    )
    
    return {
        'total_shifts': total_shifts,
        'shifts_attended': shifts_attended,
        'shifts_late': shifts_late,
        'shifts_absent': shifts_absent,
        'unauthorized_absences': unauthorized_absences,
        'shifts_completed': shifts_completed,
        'total_minutes_late': total_minutes_late,
        'average_minutes_late': (total_minutes_late / shifts_late) if shifts_late > 0 else 0,
        'attendance_rate': attendance_rate,
        'punctuality_rate': punctuality_rate,
        'completion_rate': completion_rate,
        'attendance_score': attendance_score,
        'punctuality_score': punctuality_score,
        'completion_score': completion_score,
        'overall_score': overall_score,
    }


def generate_performance_record(staff_member, start_date, end_date):
    """Generate or update a performance record for a staff member"""
    from .models import StaffPerformance
    
    metrics = calculate_performance_metrics(staff_member, start_date, end_date)
    
    # Get or create performance record
    performance, created = StaffPerformance.objects.get_or_create(
        staff_member=staff_member,
        period_start=start_date,
        period_end=end_date,
        defaults={
            'care_home': staff_member.care_home,
        }
    )
    
    # Update metrics
    performance.total_shifts = metrics['total_shifts']
    performance.shifts_attended = metrics['shifts_attended']
    performance.shifts_late = metrics['shifts_late']
    performance.shifts_absent = metrics['shifts_absent']
    performance.unauthorized_absences = metrics['unauthorized_absences']
    performance.shifts_completed = metrics['shifts_completed']
    performance.total_minutes_late = metrics['total_minutes_late']
    performance.average_minutes_late = Decimal(str(metrics['average_minutes_late']))
    
    # Calculate and save scores
    performance.calculate_scores()
    
    return performance


def get_team_performance_comparison(care_home, start_date=None, end_date=None, limit=10):
    """Get top and bottom performers in a care home"""
    from .models import StaffPerformance, User
    
    if not end_date:
        end_date = timezone.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get all staff in care home (through unit relationship)
    staff_members = User.objects.filter(unit__care_home=care_home, is_active=True)
    
    performance_data = []
    
    for staff in staff_members:
        metrics = calculate_performance_metrics(staff, start_date, end_date)
        if metrics['total_shifts'] > 0:
            performance_data.append({
                'staff_member': staff,
                'overall_score': metrics['overall_score'],
                'attendance_rate': metrics['attendance_rate'],
                'punctuality_rate': metrics['punctuality_rate'],
                'completion_rate': metrics['completion_rate'],
                'total_shifts': metrics['total_shifts'],
            })
    
    # Sort by overall score
    performance_data.sort(key=lambda x: x['overall_score'], reverse=True)
    
    return {
        'top_performers': performance_data[:limit],
        'bottom_performers': performance_data[-limit:] if len(performance_data) > limit else [],
        'average_score': sum(p['overall_score'] for p in performance_data) / len(performance_data) if performance_data else 0,
        'total_staff': len(performance_data),
    }


def identify_performance_issues(staff_member, start_date=None, end_date=None):
    """Identify performance issues and generate recommendations"""
    
    metrics = calculate_performance_metrics(staff_member, start_date, end_date)
    
    issues = []
    recommendations = []
    
    # Check attendance
    if metrics['attendance_rate'] < 80:
        issues.append({
            'category': 'ATTENDANCE',
            'severity': 'HIGH' if metrics['attendance_rate'] < 60 else 'MEDIUM',
            'description': f"Attendance rate is {metrics['attendance_rate']:.1f}% (below 80% threshold)",
            'metric_value': metrics['attendance_rate'],
        })
        recommendations.append({
            'category': 'ATTENDANCE',
            'priority': 'HIGH',
            'action': 'Schedule meeting to discuss attendance concerns',
            'details': f"Staff member has missed {metrics['shifts_absent']} out of {metrics['total_shifts']} shifts",
        })
    
    # Check unauthorized absences
    if metrics['unauthorized_absences'] > 2:
        issues.append({
            'category': 'UNAUTHORIZED_ABSENCE',
            'severity': 'CRITICAL',
            'description': f"{metrics['unauthorized_absences']} unauthorized absences",
            'metric_value': metrics['unauthorized_absences'],
        })
        recommendations.append({
            'category': 'UNAUTHORIZED_ABSENCE',
            'priority': 'CRITICAL',
            'action': 'Initiate disciplinary procedure',
            'details': 'Unauthorized absences require immediate action',
        })
    
    # Check punctuality
    if metrics['punctuality_rate'] < 85:
        issues.append({
            'category': 'PUNCTUALITY',
            'severity': 'MEDIUM',
            'description': f"Punctuality rate is {metrics['punctuality_rate']:.1f}% (below 85% threshold)",
            'metric_value': metrics['punctuality_rate'],
        })
        recommendations.append({
            'category': 'PUNCTUALITY',
            'priority': 'MEDIUM',
            'action': 'Discuss time management and shift preparation',
            'details': f"Late for {metrics['shifts_late']} shifts, average {metrics['average_minutes_late']:.0f} minutes late",
        })
    
    # Check completion rate
    if metrics['completion_rate'] < 95:
        issues.append({
            'category': 'COMPLETION',
            'severity': 'HIGH',
            'description': f"Completion rate is {metrics['completion_rate']:.1f}% (below 95% threshold)",
            'metric_value': metrics['completion_rate'],
        })
        recommendations.append({
            'category': 'COMPLETION',
            'priority': 'HIGH',
            'action': 'Review shift responsibilities and support needs',
            'details': f"Incomplete shifts: {metrics['total_shifts'] - metrics['shifts_completed']}",
        })
    
    # Overall performance
    if metrics['overall_score'] < 60:
        recommendations.append({
            'category': 'OVERALL',
            'priority': 'CRITICAL',
            'action': 'Implement performance improvement plan',
            'details': f"Overall score {metrics['overall_score']:.1f} requires formal intervention",
        })
    elif metrics['overall_score'] >= 90:
        recommendations.append({
            'category': 'RECOGNITION',
            'priority': 'LOW',
            'action': 'Recognize excellent performance',
            'details': f"Overall score {metrics['overall_score']:.1f} - consider for rewards/advancement",
        })
    
    return {
        'issues': issues,
        'recommendations': recommendations,
        'metrics': metrics,
    }


def get_attendance_calendar(staff_member, month=None, year=None):
    """Get attendance calendar data for a staff member"""
    from .models import AttendanceRecord
    
    if not month:
        month = timezone.now().month
    if not year:
        year = timezone.now().year
    
    # Get all attendance records for the month
    records = AttendanceRecord.objects.filter(
        staff_member=staff_member,
        date__year=year,
        date__month=month
    ).order_by('date')
    
    # Build calendar data
    calendar_data = {}
    for record in records:
        calendar_data[record.date.day] = {
            'status': record.status,
            'shift_type': record.shift_type,
            'minutes_late': record.minutes_late,
            'completed': record.shift_completed,
        }
    
    return {
        'month': month,
        'year': year,
        'calendar_data': calendar_data,
        'total_days': records.count(),
    }


def create_performance_review(staff_member, review_type, reviewer, 
                              quality_of_work=5, reliability=5, teamwork=5,
                              communication=5, professionalism=5,
                              achievements='', concerns='', development_goals='',
                              action_plan='', outcome='CONTINUE'):
    """Create a formal performance review"""
    from .models import PerformanceReview, StaffPerformance
    
    # Try to link to recent performance record
    recent_performance = StaffPerformance.objects.filter(
        staff_member=staff_member
    ).order_by('-period_end').first()
    
    review = PerformanceReview.objects.create(
        staff_member=staff_member,
        care_home=staff_member.care_home,
        review_type=review_type,
        review_date=timezone.now().date(),
        performance_record=recent_performance,
        quality_of_work=quality_of_work,
        reliability=reliability,
        teamwork=teamwork,
        communication=communication,
        professionalism=professionalism,
        achievements=achievements,
        concerns=concerns,
        development_goals=development_goals,
        action_plan=action_plan,
        outcome=outcome,
        reviewer=reviewer,
    )
    
    # Set next review date based on type
    if review_type == 'PROBATION':
        review.next_review_date = review.review_date + timedelta(days=30)
    elif review_type == 'QUARTERLY':
        review.next_review_date = review.review_date + timedelta(days=90)
    elif review_type == 'ANNUAL':
        review.next_review_date = review.review_date + timedelta(days=365)
    
    review.save()
    
    return review
