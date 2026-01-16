"""
TQM Module 3: Experience & Feedback Views

Comprehensive views for resident/family experience tracking:
- Experience dashboard with satisfaction metrics
- Satisfaction survey management
- Complaints tracking with Scottish compliance
- EBCD touchpoint journey mapping
- Quality of Life assessments
- Feedback theme analysis
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q, Max, Min
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from .models import (
    SatisfactionSurvey,
    Complaint,
    EBCDTouchpoint,
    QualityOfLifeAssessment,
    FeedbackTheme,
)
from .forms import SatisfactionSurveyForm, PublicSurveyForm
from scheduling.models import CareHome
from django.http import HttpResponse
from django.template.loader import render_to_string
import uuid


@login_required
def experience_dashboard(request):
    """
    Experience & Feedback dashboard with key metrics and charts.
    """
    # Get selected care home or default to first
    care_homes = CareHome.objects.all()
    selected_home_id = request.GET.get('care_home')
    
    if selected_home_id:
        care_home = get_object_or_404(CareHome, id=selected_home_id)
    elif care_homes.exists():
        care_home = care_homes.first()
    else:
        care_home = None
    
    # Calculate date ranges
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    ninety_days_ago = today - timedelta(days=90)
    
    # Filter by care home
    surveys_qs = SatisfactionSurvey.objects.all()
    complaints_qs = Complaint.objects.all()
    touchpoints_qs = EBCDTouchpoint.objects.all()
    qol_qs = QualityOfLifeAssessment.objects.all()
    themes_qs = FeedbackTheme.objects.all()
    
    if care_home:
        surveys_qs = surveys_qs.filter(care_home=care_home)
        complaints_qs = complaints_qs.filter(care_home=care_home)
        touchpoints_qs = touchpoints_qs.filter(care_home=care_home)
        themes_qs = themes_qs.filter(care_home=care_home)
    
    # Satisfaction Survey Metrics
    recent_surveys = surveys_qs.filter(survey_date__gte=thirty_days_ago)
    total_surveys = recent_surveys.count()
    
    if total_surveys > 0:
        avg_satisfaction = sum([s.get_average_score() for s in recent_surveys]) / total_surveys
        
        # NPS calculation
        nps_surveys = recent_surveys.exclude(likelihood_recommend__isnull=True)
        if nps_surveys.exists():
            promoters = nps_surveys.filter(likelihood_recommend__gte=9).count()
            detractors = nps_surveys.filter(likelihood_recommend__lte=6).count()
            nps_total = nps_surveys.count()
            nps_score = ((promoters - detractors) / nps_total * 100) if nps_total > 0 else 0
        else:
            nps_score = None
    else:
        avg_satisfaction = None
        nps_score = None
    
    # Complaint Metrics
    open_complaints = complaints_qs.filter(
        status__in=['RECEIVED', 'ACKNOWLEDGED', 'INVESTIGATING', 'AWAITING_RESPONSE']
    ).count()
    
    overdue_complaints = sum([1 for c in complaints_qs.filter(
        status__in=['RECEIVED', 'ACKNOWLEDGED', 'INVESTIGATING', 'AWAITING_RESPONSE']
    ) if c.is_overdue()])
    
    recent_complaints = complaints_qs.filter(date_received__gte=thirty_days_ago)
    
    # QoL Metrics
    recent_qol = qol_qs.filter(assessment_date__gte=thirty_days_ago)
    if recent_qol.exists():
        avg_qol_score = recent_qol.aggregate(Avg('overall_qol_score'))['overall_qol_score__avg']
    else:
        avg_qol_score = None
    
    # Active EBCD Touchpoints
    active_touchpoints = touchpoints_qs.filter(is_active=True).count()
    
    # Active Feedback Themes
    active_themes = themes_qs.filter(is_active=True).count()
    
    context = {
        'care_homes': care_homes,
        'selected_home': care_home,
        'total_surveys': total_surveys,
        'avg_satisfaction': avg_satisfaction,
        'nps_score': nps_score,
        'open_complaints': open_complaints,
        'overdue_complaints': overdue_complaints,
        'recent_complaints_count': recent_complaints.count(),
        'avg_qol_score': avg_qol_score,
        'active_touchpoints': active_touchpoints,
        'active_themes': active_themes,
        'recent_surveys': recent_surveys.order_by('-survey_date')[:5],
        'recent_complaints': complaints_qs.order_by('-date_received')[:5],
        'page_title': 'Experience & Feedback Dashboard',
    }
    
    return render(request, 'experience_feedback/dashboard.html', context)


@login_required
def survey_list(request):
    """List all satisfaction surveys with filtering."""
    surveys = SatisfactionSurvey.objects.all().select_related('care_home', 'resident', 'created_by')
    
    # Filtering
    survey_type = request.GET.get('survey_type')
    care_home_id = request.GET.get('care_home')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if survey_type:
        surveys = surveys.filter(survey_type=survey_type)
    if care_home_id:
        surveys = surveys.filter(care_home_id=care_home_id)
    if date_from:
        surveys = surveys.filter(survey_date__gte=date_from)
    if date_to:
        surveys = surveys.filter(survey_date__lte=date_to)
    
    surveys = surveys.order_by('-survey_date')
    
    context = {
        'surveys': surveys,
        'care_homes': CareHome.objects.all(),
        'page_title': 'Satisfaction Surveys',
    }
    
    return render(request, 'experience_feedback/survey_list.html', context)


@login_required
def survey_detail(request, pk):
    """Display detailed view of a satisfaction survey."""
    survey = get_object_or_404(SatisfactionSurvey.objects.select_related('care_home', 'resident'), pk=pk)
    
    context = {
        'survey': survey,
        'avg_score': survey.get_average_score(),
        'nps_category': survey.get_nps_category(),
        'page_title': f'Survey - {survey.respondent_name or "Anonymous"}',
    }
    
    return render(request, 'experience_feedback/survey_detail.html', context)


@login_required
def complaint_list(request):
    """List all complaints with filtering."""
    complaints = Complaint.objects.all().select_related('care_home', 'resident', 'investigating_officer')
    
    # Filtering
    status = request.GET.get('status')
    severity = request.GET.get('severity')
    care_home_id = request.GET.get('care_home')
    show_overdue = request.GET.get('show_overdue')
    
    if status:
        complaints = complaints.filter(status=status)
    if severity:
        complaints = complaints.filter(severity=severity)
    if care_home_id:
        complaints = complaints.filter(care_home_id=care_home_id)
    
    # Filter overdue complaints
    if show_overdue == 'true':
        complaint_ids = [c.id for c in complaints if c.is_overdue()]
        complaints = complaints.filter(id__in=complaint_ids)
    
    complaints = complaints.order_by('-date_received')
    
    context = {
        'complaints': complaints,
        'care_homes': CareHome.objects.all(),
        'page_title': 'Complaints Management',
    }
    
    return render(request, 'experience_feedback/complaint_list.html', context)


@login_required
def complaint_detail(request, pk):
    """Display detailed view of a complaint."""
    complaint = get_object_or_404(Complaint.objects.select_related('care_home', 'resident', 'investigating_officer'), pk=pk)
    
    context = {
        'complaint': complaint,
        'is_overdue': complaint.is_overdue(),
        'days_open': complaint.days_since_received(),
        'ack_within_target': complaint.acknowledgement_within_target(),
        'page_title': f'Complaint - {complaint.complaint_reference}',
    }
    
    return render(request, 'experience_feedback/complaint_detail.html', context)


@login_required
def ebcd_touchpoint_list(request):
    """List all EBCD touchpoints."""
    touchpoints = EBCDTouchpoint.objects.all().select_related('care_home', 'created_by')
    
    # Filtering
    category = request.GET.get('category')
    care_home_id = request.GET.get('care_home')
    is_active = request.GET.get('is_active')
    
    if category:
        touchpoints = touchpoints.filter(category=category)
    if care_home_id:
        touchpoints = touchpoints.filter(care_home_id=care_home_id)
    if is_active:
        touchpoints = touchpoints.filter(is_active=(is_active == 'true'))
    
    touchpoints = touchpoints.order_by('care_home', 'category', 'sequence_order')
    
    context = {
        'touchpoints': touchpoints,
        'care_homes': CareHome.objects.all(),
        'page_title': 'EBCD Touchpoints',
    }
    
    return render(request, 'experience_feedback/ebcd_list.html', context)


@login_required
def qol_assessment_list(request):
    """List all Quality of Life assessments."""
    assessments = QualityOfLifeAssessment.objects.all().select_related('resident', 'assessed_by')
    
    # Filtering
    assessment_tool = request.GET.get('assessment_tool')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if assessment_tool:
        assessments = assessments.filter(assessment_tool=assessment_tool)
    if date_from:
        assessments = assessments.filter(assessment_date__gte=date_from)
    if date_to:
        assessments = assessments.filter(assessment_date__lte=date_to)
    
    assessments = assessments.order_by('-assessment_date')
    
    context = {
        'assessments': assessments,
        'page_title': 'Quality of Life Assessments',
    }
    
    return render(request, 'experience_feedback/qol_list.html', context)


@login_required
def feedback_theme_list(request):
    """List all feedback themes."""
    themes = FeedbackTheme.objects.all().select_related('care_home', 'assigned_to', 'created_by')
    
    # Filtering
    theme_category = request.GET.get('theme_category')
    care_home_id = request.GET.get('care_home')
    is_active = request.GET.get('is_active')
    
    if theme_category:
        themes = themes.filter(theme_category=theme_category)
    if care_home_id:
        themes = themes.filter(care_home_id=care_home_id)
    if is_active:
        themes = themes.filter(is_active=(is_active == 'true'))
    
    themes = themes.order_by('-occurrences_count', '-last_occurrence')
    
    context = {
        'themes': themes,
        'care_homes': CareHome.objects.all(),
        'page_title': 'Feedback Themes',
    }
    
    return render(request, 'experience_feedback/theme_list.html', context)


# JSON API endpoints for charts

@login_required
def satisfaction_trend_data(request):
    """API endpoint for satisfaction trend chart data."""
    care_home_id = request.GET.get('care_home')
    days = int(request.GET.get('days', 90))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    surveys = SatisfactionSurvey.objects.filter(
        survey_date__gte=start_date,
        survey_date__lte=end_date
    )
    
    if care_home_id:
        surveys = surveys.filter(care_home_id=care_home_id)
    
    # Group by week
    data_points = []
    current_date = start_date
    
    while current_date <= end_date:
        week_end = current_date + timedelta(days=7)
        week_surveys = surveys.filter(
            survey_date__gte=current_date,
            survey_date__lt=week_end
        )
        
        if week_surveys.exists():
            avg_score = sum([s.get_average_score() for s in week_surveys]) / week_surveys.count()
            data_points.append({
                'date': current_date.isoformat(),
                'avg_satisfaction': round(avg_score, 2),
                'count': week_surveys.count(),
            })
        
        current_date = week_end
    
    return JsonResponse({'data': data_points})


@login_required
def complaint_stats_data(request):
    """API endpoint for complaint statistics."""
    care_home_id = request.GET.get('care_home')
    
    complaints = Complaint.objects.all()
    
    if care_home_id:
        complaints = complaints.filter(care_home_id=care_home_id)
    
    # Status distribution
    status_counts = complaints.values('status').annotate(count=Count('id'))
    
    # Severity distribution
    severity_counts = complaints.values('severity').annotate(count=Count('id'))
    
    # Monthly complaint volume (last 6 months)
    six_months_ago = timezone.now().date() - timedelta(days=180)
    monthly_complaints = []
    
    for i in range(6):
        month_start = six_months_ago + timedelta(days=i*30)
        month_end = month_start + timedelta(days=30)
        count = complaints.filter(
            date_received__gte=month_start,
            date_received__lt=month_end
        ).count()
        
        monthly_complaints.append({
            'month': month_start.strftime('%b %Y'),
            'count': count,
        })
    
    return JsonResponse({
        'status_distribution': list(status_counts),
        'severity_distribution': list(severity_counts),
        'monthly_volume': monthly_complaints,
    })


@login_required
def nps_trend_data(request):
    """API endpoint for Net Promoter Score trend."""
    care_home_id = request.GET.get('care_home')
    days = int(request.GET.get('days', 90))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    surveys = SatisfactionSurvey.objects.filter(
        survey_date__gte=start_date,
        survey_date__lte=end_date,
        likelihood_recommend__isnull=False
    )
    
    if care_home_id:
        surveys = surveys.filter(care_home_id=care_home_id)
    
    # Group by month
    data_points = []
    current_date = start_date
    
    while current_date <= end_date:
        month_end = current_date + timedelta(days=30)
        month_surveys = surveys.filter(
            survey_date__gte=current_date,
            survey_date__lt=month_end
        )
        
        if month_surveys.exists():
            promoters = month_surveys.filter(likelihood_recommend__gte=9).count()
            detractors = month_surveys.filter(likelihood_recommend__lte=6).count()
            total = month_surveys.count()
            nps = ((promoters - detractors) / total * 100) if total > 0 else 0
            
            data_points.append({
                'month': current_date.strftime('%b %Y'),
                'nps_score': round(nps, 1),
                'promoters': promoters,
                'passives': total - promoters - detractors,
                'detractors': detractors,
            })
        
        current_date = month_end
    
    return JsonResponse({'data': data_points})


# ==================== Survey Creation & Public Access ====================

@login_required
def survey_create(request):
    """Create a new satisfaction survey (staff-initiated)."""
    survey_type = request.GET.get('type')  # Pre-select survey type from URL
    
    if request.method == 'POST':
        form = SatisfactionSurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.save()
            messages.success(request, 'Survey created successfully.')
            return redirect('experience_feedback:survey_detail', pk=survey.pk)
    else:
        form = SatisfactionSurveyForm(survey_type=survey_type)
    
    context = {
        'form': form,
        'page_title': 'Create Satisfaction Survey',
        'survey_type': survey_type,
    }
    
    return render(request, 'experience_feedback/survey_form.html', context)


@login_required
def survey_edit(request, pk):
    """Edit an existing satisfaction survey."""
    survey = get_object_or_404(SatisfactionSurvey, pk=pk)
    
    if request.method == 'POST':
        form = SatisfactionSurveyForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            messages.success(request, 'Survey updated successfully.')
            return redirect('experience_feedback:survey_detail', pk=survey.pk)
    else:
        form = SatisfactionSurveyForm(instance=survey)
    
    context = {
        'form': form,
        'survey': survey,
        'page_title': 'Edit Survey',
    }
    
    return render(request, 'experience_feedback/survey_form.html', context)


@login_required
def survey_delete(request, pk):
    """Delete a satisfaction survey."""
    survey = get_object_or_404(SatisfactionSurvey, pk=pk)
    
    if request.method == 'POST':
        survey.delete()
        messages.success(request, 'Survey deleted successfully.')
        return redirect('experience_feedback:survey_list')
    
    context = {
        'survey': survey,
        'page_title': 'Delete Survey',
    }
    
    return render(request, 'experience_feedback/survey_confirm_delete.html', context)


def public_survey(request, token):
    """
    Public survey form (no login required).
    Token should be generated and sent to respondents via email/SMS.
    """
    # For now, use token to identify care home or resident
    # In production, store tokens in database linked to specific surveys
    
    if request.method == 'POST':
        form = PublicSurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            # Set metadata from token (simplified for now)
            survey.survey_type = 'RESIDENT_ONGOING'  # Default, would be from token
            survey.save()
            
            return render(request, 'experience_feedback/public_survey_thanks.html')
    else:
        form = PublicSurveyForm()
    
    context = {
        'form': form,
        'page_title': 'Your Feedback Matters',
    }
    
    return render(request, 'experience_feedback/public_survey.html', context)


@login_required
def survey_pdf(request, pk):
    """Generate PDF version of survey (for printing or download)."""
    survey = get_object_or_404(SatisfactionSurvey, pk=pk)
    
    # Render HTML template
    html_string = render_to_string('experience_feedback/survey_pdf.html', {
        'survey': survey,
        'avg_score': survey.get_average_score(),
        'nps_category': survey.get_nps_category(),
    })
    
    # For now, return HTML (would use weasyprint/reportlab for actual PDF)
    response = HttpResponse(html_string, content_type='text/html')
    # To convert to PDF, install weasyprint and use:
    # from weasyprint import HTML
    # pdf = HTML(string=html_string).write_pdf()
    # response = HttpResponse(pdf, content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="survey_{survey.pk}.pdf"'
    
    return response


@login_required
def blank_survey_pdf(request, survey_type):
    """Generate blank printable survey template for paper distribution."""
    
    # Map survey type to friendly name
    survey_type_names = {
        'RESIDENT_ADMISSION': 'Resident - Admission Survey',
        'RESIDENT_ONGOING': 'Resident - Ongoing Care Survey',
        'RESIDENT_DISCHARGE': 'Resident - Discharge Survey',
        'FAMILY_ADMISSION': 'Family - Admission Survey',
        'FAMILY_ONGOING': 'Family - Ongoing Care Survey',
        'FAMILY_BEREAVEMENT': 'Family - Bereavement Survey',
        'STAFF_EXPERIENCE': 'Staff - Experience Survey',
        'PROFESSIONAL_PARTNERSHIP': 'Professional - Partnership Survey',
    }
    
    html_string = render_to_string('experience_feedback/blank_survey_pdf.html', {
        'survey_type': survey_type,
        'survey_type_name': survey_type_names.get(survey_type, 'Satisfaction Survey'),
    })
    
    response = HttpResponse(html_string, content_type='text/html')
    return response

