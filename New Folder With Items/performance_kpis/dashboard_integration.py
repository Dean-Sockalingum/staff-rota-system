"""
Module 7: Integrated TQM Dashboard
Real-time KPI aggregation from all 7 modules
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import timedelta

# Import models from all 7 modules
from incident_safety.models import SafetyActionPlan, RootCauseAnalysis, IncidentTrendAnalysis
from experience_feedback.models import SatisfactionSurvey, Complaint
from quality_audits.models import PDSAProject, PDSACycle, QualityImprovementAction, QIAUpdate
from training_competency.models import TrainingCourse, CompetencyAssessment
from policies_procedures.models import Policy, PolicyAcknowledgement
from risk_management.models import RiskRegister, RiskMitigation
from scheduling.models import IncidentReport


@login_required
def integrated_dashboard(request):
    """
    Executive TQM Dashboard pulling real-time metrics from all 7 modules.
    Provides comprehensive overview of quality, safety, and compliance performance.
    """
    
    # Date ranges for calculations
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    ninety_days_ago = today - timedelta(days=90)
    this_year_start = today.replace(month=1, day=1)
    
    # ========================================
    # MODULE 2: INCIDENT & SAFETY METRICS
    # ========================================
    total_incidents = IncidentReport.objects.filter(
        date_occurred__gte=thirty_days_ago
    ).count()
    
    high_severity_incidents = IncidentReport.objects.filter(
        date_occurred__gte=thirty_days_ago,
        severity__in=['MAJOR', 'CRITICAL']
    ).count()
    
    # HSAPs (Health & Safety Action Plans)
    total_hsaps = SafetyActionPlan.objects.count()
    active_hsaps = SafetyActionPlan.objects.filter(
        status__in=['PLANNED', 'IN_PROGRESS']
    ).count()
    completed_hsaps = SafetyActionPlan.objects.filter(
        status='IMPLEMENTED'
    ).count()
    hsap_completion_rate = (completed_hsaps / total_hsaps * 100) if total_hsaps > 0 else 0
    
    # Root Cause Analysis
    total_rcas = RootCauseAnalysis.objects.count()
    approved_rcas = RootCauseAnalysis.objects.filter(status='APPROVED').count()
    rca_completion_rate = (approved_rcas / total_rcas * 100) if total_rcas > 0 else 0
    
    # Trend Analysis
    active_trends = IncidentTrendAnalysis.objects.filter(status='ACTIVE').count()
    
    # ========================================
    # MODULE 3: EXPERIENCE & FEEDBACK METRICS
    # ========================================
    total_feedback = SatisfactionSurvey.objects.filter(
        survey_date__gte=thirty_days_ago
    ).count()
    
    # Count surveys with high satisfaction (4-5 out of 5)
    positive_feedback = SatisfactionSurvey.objects.filter(
        survey_date__gte=thirty_days_ago,
        overall_satisfaction__gte=4
    ).count()
    
    complaints_count = Complaint.objects.filter(
        received_date__gte=thirty_days_ago
    ).count()
    
    # Response times
    avg_complaint_response_days = Complaint.objects.filter(
        received_date__gte=thirty_days_ago,
        response_date__isnull=False
    ).extra(
        select={'response_time': '(julianday(response_date) - julianday(received_date))'}
    ).aggregate(avg=Avg('response_time'))['avg'] or 0
    
    # Average satisfaction rating (1-5 scale)
    avg_satisfaction = SatisfactionSurvey.objects.filter(
        survey_date__gte=thirty_days_ago
    ).aggregate(avg=Avg('overall_satisfaction'))['avg'] or 0
    
    # ========================================
    # MODULE 1: QUALITY AUDITS & PDSA METRICS
    # ========================================
    total_pdsa_projects = PDSAProject.objects.count()
    active_pdsa = PDSAProject.objects.filter(status='ACTIVE').count()
    completed_pdsa = PDSAProject.objects.filter(status='COMPLETED').count()
    
    # PDSA cycles
    total_cycles = PDSACycle.objects.count()
    successful_cycles = PDSACycle.objects.filter(
        outcome='SUCCESS'
    ).count()
    pdsa_success_rate = (successful_cycles / total_cycles * 100) if total_cycles > 0 else 0
    
    # QIA (Quality Improvement Actions)
    total_qias = QualityImprovementAction.objects.count()
    active_qias = QualityImprovementAction.objects.filter(
        status__in=['IDENTIFIED', 'PLANNED', 'APPROVED', 'IMPLEMENTING', 'IMPLEMENTED']
    ).count()
    closed_qias = QualityImprovementAction.objects.filter(status='CLOSED').count()
    qia_closure_rate = (closed_qias / total_qias * 100) if total_qias > 0 else 0
    
    # Overdue QIAs
    overdue_qias = QualityImprovementAction.objects.filter(
        target_completion_date__lt=today
    ).exclude(status__in=['CLOSED', 'REJECTED']).count()
    
    # QIA by source
    qias_from_incidents = QualityImprovementAction.objects.filter(source_type='INCIDENT').count()
    qias_from_audits = QualityImprovementAction.objects.filter(source_type='AUDIT').count()
    qias_from_risks = QualityImprovementAction.objects.filter(source_type='RISK').count()
    
    # Priority breakdown
    critical_qias = QualityImprovementAction.objects.filter(priority='CRITICAL').count()
    high_priority_qias = QualityImprovementAction.objects.filter(priority='HIGH').count()
    
    # ========================================
    # MODULE 4: TRAINING & COMPETENCY METRICS
    # ========================================
    total_training_courses = TrainingCourse.objects.filter(is_active=True).count()
    mandatory_courses = TrainingCourse.objects.filter(
        is_active=True,
        is_mandatory=True
    ).count()
    
    # Competency assessments
    total_assessments = CompetencyAssessment.objects.count()
    passed_assessments = CompetencyAssessment.objects.filter(
        outcome='COMPETENT'
    ).count()
    competency_pass_rate = (passed_assessments / total_assessments * 100) if total_assessments > 0 else 0
    
    # ========================================
    # MODULE 5: POLICIES & PROCEDURES METRICS
    # ========================================
    total_policies = Policy.objects.count()
    active_policies = Policy.objects.filter(status='active').count()
    policies_needing_review = Policy.objects.filter(
        next_review_date__lte=today + timedelta(days=30)
    ).count()
    
    # Policy acknowledgements
    total_acks = PolicyAcknowledgement.objects.count()
    recent_acks = PolicyAcknowledgement.objects.filter(
        acknowledged_date__gte=thirty_days_ago
    ).count()
    
    # ========================================
    # MODULE 6: RISK MANAGEMENT METRICS
    # ========================================
    total_risks = RiskRegister.objects.count()
    critical_risks = RiskRegister.objects.filter(priority='CRITICAL').count()
    high_risks = RiskRegister.objects.filter(priority='HIGH').count()
    
    # Risk status
    controlled_risks = RiskRegister.objects.filter(status='CONTROLLED').count()
    risk_control_rate = (controlled_risks / total_risks * 100) if total_risks > 0 else 0
    
    # Mitigation effectiveness
    total_mitigations = RiskMitigation.objects.count()
    completed_mitigations = RiskMitigation.objects.filter(
        status='COMPLETED'
    ).count()
    mitigation_completion_rate = (completed_mitigations / total_mitigations * 100) if total_mitigations > 0 else 0
    
    # ========================================
    # EXECUTIVE SUMMARY CALCULATIONS
    # ========================================
    
    # Overall Safety Score (composite metric)
    # Components: low incidents, high HSAP completion, controlled risks
    safety_score = (
        (100 - min(high_severity_incidents * 10, 100)) * 0.4 +  # 40% weight
        hsap_completion_rate * 0.3 +  # 30% weight
        risk_control_rate * 0.3  # 30% weight
    )
    
    # Overall Quality Score (composite metric)
    # Components: PDSA success, competency pass rate, RCA completion, QIA closure
    quality_score = (
        pdsa_success_rate * 0.3 +
        competency_pass_rate * 0.25 +
        rca_completion_rate * 0.25 +
        qia_closure_rate * 0.2
    )
    
    # Overall Compliance Score (composite metric)
    # Components: policy status, training completion, risk management
    policies_current_pct = ((total_policies - policies_needing_review) / total_policies * 100) if total_policies > 0 else 0
    compliance_score = (
        policies_current_pct * 0.4 +
        competency_pass_rate * 0.3 +
        risk_control_rate * 0.3
    )
    
    # ========================================
    # CONTEXT DATA FOR TEMPLATE
    # ========================================
    context = {
        # Overall Scores (RAG status)
        'safety_score': round(safety_score, 1),
        'safety_rag': _get_rag_status(safety_score),
        'quality_score': round(quality_score, 1),
        'quality_rag': _get_rag_status(quality_score),
        'compliance_score': round(compliance_score, 1),
        'compliance_rag': _get_rag_status(compliance_score),
        
        # Module 2: Incident & Safety
        'total_incidents': total_incidents,
        'high_severity_incidents': high_severity_incidents,
        'total_hsaps': total_hsaps,
        'active_hsaps': active_hsaps,
        'hsap_completion_rate': round(hsap_completion_rate, 1),
        'total_rcas': total_rcas,
        'rca_completion_rate': round(rca_completion_rate, 1),
        'active_trends': active_trends,
        
        # Module 3: Experience & Feedback
        'total_feedback': total_feedback,
        'positive_feedback': positive_feedback,
        'complaints_count': complaints_count,
        'avg_complaint_response_days': round(avg_complaint_response_days, 1),
        'avg_satisfaction': round(avg_satisfaction, 1),
        
        # Module 1: Quality & PDSA
        'total_pdsa_projects': total_pdsa_projects,
        'active_pdsa': active_pdsa,
        'completed_pdsa': completed_pdsa,
        'pdsa_success_rate': round(pdsa_success_rate, 1),
        
        # Module 1: QIA (Quality Improvement Actions)
        'total_qias': total_qias,
        'active_qias': active_qias,
        'closed_qias': closed_qias,
        'qia_closure_rate': round(qia_closure_rate, 1),
        'overdue_qias': overdue_qias,
        'qias_from_incidents': qias_from_incidents,
        'qias_from_audits': qias_from_audits,
        'qias_from_risks': qias_from_risks,
        'critical_qias': critical_qias,
        'high_priority_qias': high_priority_qias,
        
        # Module 4: Training
        'total_training_courses': total_training_courses,
        'mandatory_courses': mandatory_courses,
        'competency_pass_rate': round(competency_pass_rate, 1),
        
        # Module 5: Policies
        'total_policies': total_policies,
        'active_policies': active_policies,
        'policies_needing_review': policies_needing_review,
        'recent_policy_acks': recent_acks,
        
        # Module 6: Risk Management
        'total_risks': total_risks,
        'critical_risks': critical_risks,
        'high_risks': high_risks,
        'risk_control_rate': round(risk_control_rate, 1),
        'mitigation_completion_rate': round(mitigation_completion_rate, 1),
        
        # Time period
        'period_days': 30,
        'report_date': today,
        
        # Chart data (JSON)
        'incident_trend_data': _get_incident_trend_data(thirty_days_ago, today),
        'risk_distribution_data': _get_risk_distribution_data(),
        'training_completion_data': _get_training_completion_data(),
        'pdsa_success_data': _get_pdsa_success_data(),
        'qia_closure_data': _get_qia_closure_data(),
    }
    
    return render(request, 'performance_kpis/integrated_dashboard.html', context)


def _get_rag_status(score):
    """Convert numeric score to RAG (Red/Amber/Green) status."""
    if score >= 80:
        return 'GREEN'
    elif score >= 60:
        return 'AMBER'
    else:
        return 'RED'


def _get_incident_trend_data(start_date, end_date):
    """Generate incident trend data for last 30 days."""
    import json
    from datetime import timedelta
    
    labels = []
    total_data = []
    high_severity_data = []
    
    current_date = start_date
    while current_date <= end_date:
        labels.append(current_date.strftime('%d %b'))
        
        # Count incidents for this day
        total_count = IncidentReport.objects.filter(
            date_occurred=current_date
        ).count()
        
        high_severity_count = IncidentReport.objects.filter(
            date_occurred=current_date,
            severity__in=['MAJOR', 'CRITICAL']
        ).count()
        
        total_data.append(total_count)
        high_severity_data.append(high_severity_count)
        
        current_date += timedelta(days=1)
    
    return json.dumps({
        'labels': labels,
        'total': total_data,
        'high_severity': high_severity_data
    })


def _get_risk_distribution_data():
    """Generate risk distribution by priority."""
    import json
    
    critical = RiskRegister.objects.filter(priority='CRITICAL').count()
    high = RiskRegister.objects.filter(priority='HIGH').count()
    medium = RiskRegister.objects.filter(priority='MEDIUM').count()
    low = RiskRegister.objects.filter(priority='LOW').count()
    
    return json.dumps({
        'critical': critical,
        'high': high,
        'medium': medium,
        'low': low
    })


def _get_training_completion_data():
    """Generate training completion rates for mandatory courses."""
    import json
    from training_competency.models import TrainingAttendance
    from scheduling.models import StaffMember
    
    mandatory_courses = TrainingCourse.objects.filter(
        is_active=True,
        is_mandatory=True
    )[:5]  # Top 5 mandatory courses
    
    courses = []
    completion_rates = []
    
    total_staff = StaffMember.objects.filter(is_active=True).count()
    
    for course in mandatory_courses:
        courses.append(course.course_name[:30])  # Truncate long names
        
        # Count staff who completed this course
        completed_count = TrainingAttendance.objects.filter(
            course=course,
            status='COMPLETED'
        ).values('staff_member').distinct().count()
        
        completion_rate = (completed_count / total_staff * 100) if total_staff > 0 else 0
        completion_rates.append(round(completion_rate, 1))
    
    return json.dumps({
        'courses': courses,
        'completion_rates': completion_rates
    })


def _get_pdsa_success_data():
    """Generate PDSA success rate trend for last 6 months."""
    import json
    from datetime import timedelta
    from django.db.models.functions import TruncMonth
    
    today = timezone.now().date()
    six_months_ago = today - timedelta(days=180)
    
    months = []
    success_rates = []
    
    # Get projects grouped by month
    for i in range(5, -1, -1):  # Last 6 months
        month_date = today - timedelta(days=i*30)
        month_start = month_date.replace(day=1)
        
        if i > 0:
            next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
            month_end = next_month - timedelta(days=1)
        else:
            month_end = today
        
        months.append(month_start.strftime('%b %Y'))
        
        # Count completed PDSA projects in this month
        total = PDSAProject.objects.filter(
            end_date__gte=month_start,
            end_date__lte=month_end,
            status='COMPLETED'
        ).count()
        
        successful = PDSAProject.objects.filter(
            end_date__gte=month_start,
            end_date__lte=month_end,
            status='COMPLETED',
            success_status='SUCCESS'
        ).count()
        
        success_rate = (successful / total * 100) if total > 0 else 0
        success_rates.append(round(success_rate, 1))
    
    return json.dumps({
        'months': months,
        'success_rates': success_rates
    })


def _get_qia_closure_data():
    """Generate QIA creation vs closure trend for last 6 months."""
    import json
    from datetime import timedelta
    from django.db.models.functions import TruncMonth
    
    today = timezone.now().date()
    
    months = []
    created_data = []
    closed_data = []
    
    # Get QIAs grouped by month
    for i in range(5, -1, -1):  # Last 6 months
        month_date = today - timedelta(days=i*30)
        month_start = month_date.replace(day=1)
        
        if i > 0:
            next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
            month_end = next_month - timedelta(days=1)
        else:
            month_end = today
        
        months.append(month_start.strftime('%b %Y'))
        
        # Count created QIAs
        created = QualityImprovementAction.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        
        # Count closed QIAs
        closed = QualityImprovementAction.objects.filter(
            closed_date__gte=month_start,
            closed_date__lte=month_end
        ).count()
        
        created_data.append(created)
        closed_data.append(closed)
    
    return json.dumps({
        'months': months,
        'created': created_data,
        'closed': closed_data
    })
