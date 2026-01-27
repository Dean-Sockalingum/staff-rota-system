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
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
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
    complaint = get_object_or_404(
        Complaint.objects.select_related(
            'care_home', 'resident', 'investigating_officer', 'created_by'
        ).prefetch_related(
            'investigation_stages__assigned_to',
            'stakeholders__created_by'
        ), 
        pk=pk
    )
    
    context = {
        'complaint': complaint,
        'is_overdue': complaint.is_overdue(),
        'days_open': complaint.days_since_received(),
        'ack_within_target': complaint.acknowledgement_within_target(),
        'investigation_stages': complaint.investigation_stages.all(),
        'stakeholders': complaint.stakeholders.all(),
        'page_title': f'Complaint - {complaint.complaint_reference}',
    }
    
    return render(request, 'experience_feedback/complaint_detail.html', context)


@login_required
def complaint_create(request):
    """Create a new complaint."""
    from .forms import ComplaintForm
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.created_by = request.user
            complaint.save()
            
            messages.success(request, f'Complaint {complaint.complaint_reference} created successfully.')
            return redirect('experience_feedback:complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintForm()
    
    context = {
        'form': form,
        'page_title': 'Register New Complaint',
        'action': 'create',
    }
    
    return render(request, 'experience_feedback/complaint_form.html', context)


@login_required
def complaint_edit(request, pk):
    """Edit an existing complaint."""
    from .forms import ComplaintForm
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, f'Complaint {complaint.complaint_reference} updated successfully.')
            return redirect('experience_feedback:complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintForm(instance=complaint)
    
    context = {
        'form': form,
        'complaint': complaint,
        'page_title': f'Edit Complaint - {complaint.complaint_reference}',
        'action': 'edit',
    }
    
    return render(request, 'experience_feedback/complaint_form.html', context)


@login_required
def complaint_update_status(request, pk):
    """Update complaint status and investigation progress."""
    from .forms import ComplaintUpdateForm
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        form = ComplaintUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            updated_complaint = form.save()
            
            # Log the update notes if provided
            update_notes = form.cleaned_data.get('update_notes', '')
            if update_notes:
                # You could create an audit log entry here
                pass
            
            messages.success(request, f'Complaint {complaint.complaint_reference} status updated.')
            return redirect('experience_feedback:complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintUpdateForm(instance=complaint)
    
    context = {
        'form': form,
        'complaint': complaint,
        'page_title': f'Update Status - {complaint.complaint_reference}',
    }
    
    return render(request, 'experience_feedback/complaint_update.html', context)


@login_required
def complaint_add_stage(request, pk):
    """Add an investigation stage to a complaint."""
    from .forms import ComplaintInvestigationStageForm
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        form = ComplaintInvestigationStageForm(request.POST)
        if form.is_valid():
            stage = form.save(commit=False)
            stage.complaint = complaint
            stage.save()
            messages.success(request, f'Investigation stage "{stage.get_stage_name_display()}" added.')
            return redirect('experience_feedback:complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintInvestigationStageForm()
        # Auto-set sequence order
        max_order = complaint.investigation_stages.aggregate(models.Max('sequence_order'))['sequence_order__max'] or 0
        form.initial['sequence_order'] = max_order + 1
    
    context = {
        'form': form,
        'complaint': complaint,
        'page_title': f'Add Investigation Stage - {complaint.complaint_reference}',
    }
    
    return render(request, 'experience_feedback/complaint_stage_form.html', context)


@login_required
def complaint_add_stakeholder(request, pk):
    """Add a stakeholder to a complaint."""
    from .forms import ComplaintStakeholderForm
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        form = ComplaintStakeholderForm(request.POST)
        if form.is_valid():
            stakeholder = form.save(commit=False)
            stakeholder.complaint = complaint
            stakeholder.created_by = request.user
            stakeholder.save()
            messages.success(request, f'Stakeholder "{stakeholder.name}" added to complaint.')
            return redirect('experience_feedback:complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintStakeholderForm()
    
    context = {
        'form': form,
        'complaint': complaint,
        'page_title': f'Add Stakeholder - {complaint.complaint_reference}',
    }
    
    return render(request, 'experience_feedback/complaint_stakeholder_form.html', context)


@login_required
def complaint_delete(request, pk):
    """Delete a complaint (soft delete preferred)."""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        complaint_ref = complaint.complaint_reference
        complaint.delete()
        messages.success(request, f'Complaint {complaint_ref} has been deleted.')
        return redirect('experience_feedback:complaint_list')
    
    context = {
        'complaint': complaint,
        'page_title': f'Delete Complaint - {complaint.complaint_reference}',
    }
    
    return render(request, 'experience_feedback/complaint_confirm_delete.html', context)


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


# ============================================================================
# YOU SAID, WE DID FUNCTIONALITY
# ============================================================================

@login_required
def yswda_dashboard(request):
    """
    'You Said, We Did' dashboard showing all feedback and actions.
    Demonstrates responsiveness to resident/family feedback.
    """
    care_homes = CareHome.objects.all()
    selected_home_id = request.GET.get('care_home')
    
    if selected_home_id:
        care_home = get_object_or_404(CareHome, id=selected_home_id)
    elif care_homes.exists():
        care_home = care_homes.first()
    else:
        care_home = None
    
    # Import the model here to avoid circular import
    from .models import YouSaidWeDidAction
    
    # Filter actions by care home
    actions_qs = YouSaidWeDidAction.objects.all()
    if care_home:
        actions_qs = actions_qs.filter(care_home=care_home)
    
    # Statistics
    total_actions = actions_qs.count()
    completed_actions = actions_qs.filter(status='COMPLETED').count()
    in_progress_actions = actions_qs.filter(status='IN_PROGRESS').count()
    
    # Recent actions
    recent_actions = actions_qs.order_by('-feedback_date')[:10]
    
    # Displayable actions (for notice board)
    displayable_actions = actions_qs.filter(display_on_board=True)
    displayable_actions = [a for a in displayable_actions if a.is_displayable()]
    
    # Category breakdown
    category_counts = {}
    for action in actions_qs:
        cat = action.get_category_display()
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Sentiment breakdown
    sentiment_counts = {}
    for action in actions_qs:
        sent = action.get_sentiment_display()
        sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1
    
    context = {
        'care_homes': care_homes,
        'care_home': care_home,
        'total_actions': total_actions,
        'completed_actions': completed_actions,
        'in_progress_actions': in_progress_actions,
        'recent_actions': recent_actions,
        'displayable_actions': displayable_actions,
        'category_counts': category_counts,
        'sentiment_counts': sentiment_counts,
    }
    
    return render(request, 'experience_feedback/yswda_dashboard.html', context)


@login_required
def yswda_list(request):
    """List all You Said, We Did actions with filtering."""
    from .models import YouSaidWeDidAction
    
    actions = YouSaidWeDidAction.objects.all()
    
    # Filtering
    care_home_id = request.GET.get('care_home')
    status = request.GET.get('status')
    category = request.GET.get('category')
    
    if care_home_id:
        actions = actions.filter(care_home_id=care_home_id)
    if status:
        actions = actions.filter(status=status)
    if category:
        actions = actions.filter(category=category)
    
    context = {
        'actions': actions,
        'care_homes': CareHome.objects.all(),
    }
    
    return render(request, 'experience_feedback/yswda_list.html', context)


@login_required
def yswda_create(request):
    """Create a new You Said, We Did action."""
    from .forms import YouSaidWeDidActionForm
    from .models import YouSaidWeDidAction
    
    if request.method == 'POST':
        form = YouSaidWeDidActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.created_by = request.user
            action.save()
            messages.success(request, 'You Said, We Did action created successfully.')
            return redirect('experience_feedback:yswda_detail', pk=action.pk)
    else:
        # Pre-populate care home if provided
        initial = {}
        care_home_id = request.GET.get('care_home')
        if care_home_id:
            initial['care_home'] = care_home_id
        
        form = YouSaidWeDidActionForm(initial=initial)
    
    context = {
        'form': form,
        'action': 'create',
    }
    
    return render(request, 'experience_feedback/yswda_form.html', context)


@login_required
def yswda_detail(request, pk):
    """View details of a You Said, We Did action."""
    from .models import YouSaidWeDidAction
    
    action = get_object_or_404(YouSaidWeDidAction, pk=pk)
    
    context = {
        'action': action,
    }
    
    return render(request, 'experience_feedback/yswda_detail.html', context)


@login_required
def yswda_update(request, pk):
    """Update a You Said, We Did action."""
    from .forms import YouSaidWeDidActionForm
    from .models import YouSaidWeDidAction
    
    action = get_object_or_404(YouSaidWeDidAction, pk=pk)
    
    if request.method == 'POST':
        form = YouSaidWeDidActionForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            messages.success(request, 'You Said, We Did action updated successfully.')
            return redirect('experience_feedback:yswda_detail', pk=action.pk)
    else:
        form = YouSaidWeDidActionForm(instance=action)
    
    context = {
        'form': form,
        'action': 'update',
        'yswda': action,
    }
    
    return render(request, 'experience_feedback/yswda_form.html', context)


@login_required
def yswda_delete(request, pk):
    """Delete a You Said, We Did action."""
    from .models import YouSaidWeDidAction
    
    action = get_object_or_404(YouSaidWeDidAction, pk=pk)
    
    if request.method == 'POST':
        action.delete()
        messages.success(request, 'You Said, We Did action deleted successfully.')
        return redirect('experience_feedback:yswda_list')
    
    context = {
        'action': action,
    }
    
    return render(request, 'experience_feedback/yswda_confirm_delete.html', context)


def yswda_public_board(request, care_home_id):
    """
    Public-facing 'You Said, We Did' notice board.
    No login required - displays to residents and families.
    """
    from .models import YouSaidWeDidAction
    
    care_home = get_object_or_404(CareHome, pk=care_home_id)
    
    # Get displayable actions
    actions = YouSaidWeDidAction.objects.filter(
        care_home=care_home,
        display_on_board=True
    ).order_by('-feedback_date')
    
    # Filter to only currently displayable
    displayable_actions = [a for a in actions if a.is_displayable()]
    
    context = {
        'care_home': care_home,
        'actions': displayable_actions,
    }
    
    return render(request, 'experience_feedback/yswda_public_board.html', context)


# ============================================================================
# SURVEY DISTRIBUTION VIEWS
# ============================================================================

@login_required
def distribution_dashboard(request):
    """
    Survey distribution dashboard showing schedules, distributions, and analytics.
    """
    from .models import SurveyDistributionSchedule, SurveyDistribution
    from django.db.models import Count, Q, Avg
    from django.db.models.functions import TruncDate
    
    # Get selected care home
    care_homes = CareHome.objects.all()
    selected_home_id = request.GET.get('care_home')
    
    if selected_home_id:
        care_home = get_object_or_404(CareHome, id=selected_home_id)
    elif care_homes.exists():
        care_home = care_homes.first()
    else:
        care_home = None
    
    if not care_home:
        context = {
            'care_homes': care_homes,
            'care_home': None,
        }
        return render(request, 'experience_feedback/distribution_dashboard.html', context)
    
    # Get active schedules
    active_schedules = SurveyDistributionSchedule.objects.filter(
        care_home=care_home,
        is_active=True
    ).select_related('care_home')
    
    # Get recent distributions
    recent_distributions = SurveyDistribution.objects.filter(
        care_home=care_home
    ).select_related('resident', 'schedule').order_by('-sent_at')[:50]
    
    # Calculate statistics
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    total_sent = SurveyDistribution.objects.filter(
        care_home=care_home,
        sent_at__gte=thirty_days_ago
    ).count()
    
    total_delivered = SurveyDistribution.objects.filter(
        care_home=care_home,
        sent_at__gte=thirty_days_ago,
        delivery_status='DELIVERED'
    ).count()
    
    total_responded = SurveyDistribution.objects.filter(
        care_home=care_home,
        sent_at__gte=thirty_days_ago,
        response_received=True
    ).count()
    
    total_pending = SurveyDistribution.objects.filter(
        care_home=care_home,
        sent_at__isnull=True
    ).count()
    
    # Calculate response rate
    response_rate = (total_responded / total_sent * 100) if total_sent > 0 else 0
    delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
    
    # Get distributions needing reminders
    needs_reminders = SurveyDistribution.objects.filter(
        care_home=care_home,
        response_received=False,
        sent_at__isnull=False
    )
    distributions_needing_reminder = [d for d in needs_reminders if d.needs_reminder()]
    
    # Distribution by channel
    channel_stats = SurveyDistribution.objects.filter(
        care_home=care_home,
        sent_at__gte=thirty_days_ago
    ).values('distribution_channel').annotate(
        count=Count('id'),
        responded=Count('id', filter=Q(response_received=True))
    )
    
    # Daily distribution trend (last 14 days)
    fourteen_days_ago = timezone.now() - timedelta(days=14)
    daily_distributions = SurveyDistribution.objects.filter(
        care_home=care_home,
        sent_at__gte=fourteen_days_ago
    ).annotate(
        date=TruncDate('sent_at')
    ).values('date').annotate(
        sent=Count('id'),
        responded=Count('id', filter=Q(response_received=True))
    ).order_by('date')
    
    context = {
        'care_homes': care_homes,
        'care_home': care_home,
        'active_schedules': active_schedules,
        'recent_distributions': recent_distributions,
        'total_sent': total_sent,
        'total_delivered': total_delivered,
        'total_responded': total_responded,
        'total_pending': total_pending,
        'response_rate': round(response_rate, 1),
        'delivery_rate': round(delivery_rate, 1),
        'distributions_needing_reminder': distributions_needing_reminder,
        'channel_stats': channel_stats,
        'daily_distributions': daily_distributions,
    }
    
    return render(request, 'experience_feedback/distribution_dashboard.html', context)


@login_required
def schedule_list(request):
    """List all survey distribution schedules."""
    from .models import SurveyDistributionSchedule
    
    schedules = SurveyDistributionSchedule.objects.select_related('care_home').order_by('-created_at')
    
    context = {
        'schedules': schedules,
    }
    
    return render(request, 'experience_feedback/schedule_list.html', context)


@login_required
def schedule_create(request):
    """Create a new survey distribution schedule."""
    from .models import SurveyDistributionSchedule
    from .forms import SurveyDistributionScheduleForm
    
    if request.method == 'POST':
        form = SurveyDistributionScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.created_by = request.user
            schedule.save()
            messages.success(request, 'Survey distribution schedule created successfully.')
            return redirect('experience_feedback:schedule_list')
    else:
        form = SurveyDistributionScheduleForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'experience_feedback/schedule_form.html', context)


@login_required
def schedule_edit(request, pk):
    """Edit an existing survey distribution schedule."""
    from .models import SurveyDistributionSchedule
    from .forms import SurveyDistributionScheduleForm
    
    schedule = get_object_or_404(SurveyDistributionSchedule, pk=pk)
    
    if request.method == 'POST':
        form = SurveyDistributionScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Survey distribution schedule updated successfully.')
            return redirect('experience_feedback:schedule_list')
    else:
        form = SurveyDistributionScheduleForm(instance=schedule)
    
    context = {
        'form': form,
        'schedule': schedule,
        'action': 'Edit',
    }
    
    return render(request, 'experience_feedback/schedule_form.html', context)


@login_required
def schedule_delete(request, pk):
    """Delete a survey distribution schedule."""
    from .models import SurveyDistributionSchedule
    
    schedule = get_object_or_404(SurveyDistributionSchedule, pk=pk)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Survey distribution schedule deleted successfully.')
        return redirect('experience_feedback:schedule_list')
    
    context = {
        'schedule': schedule,
    }
    
    return render(request, 'experience_feedback/schedule_confirm_delete.html', context)


@login_required
def distribution_send(request, pk):
    """
    Send a survey distribution via email or SMS.
    """
    from .models import SurveyDistribution
    from .survey_distribution import get_email_content, get_sms_content
    from django.core.mail import send_mail
    from django.conf import settings
    
    distribution = get_object_or_404(SurveyDistribution, pk=pk)
    
    if request.method == 'POST':
        channel = request.POST.get('channel', 'EMAIL')
        
        if channel == 'EMAIL' and distribution.recipient_email:
            # Send email
            email_content = get_email_content(distribution, request)
            
            try:
                send_mail(
                    subject=email_content['subject'],
                    message=email_content['body_text'],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[distribution.recipient_email],
                    html_message=email_content['body_html'],
                    fail_silently=False,
                )
                
                distribution.distribution_channel = 'EMAIL'
                distribution.sent_at = timezone.now()
                distribution.delivery_status = 'DELIVERED'
                distribution.save()
                
                messages.success(request, f'Survey email sent to {distribution.recipient_email}')
                
            except Exception as e:
                messages.error(request, f'Failed to send email: {str(e)}')
                
        elif channel == 'SMS' and distribution.recipient_phone:
            # Send SMS
            sms_content = get_sms_content(distribution, request)
            
            # TODO: Integrate with SMS provider (Twilio, etc.)
            # For now, just mark as sent
            distribution.distribution_channel = 'SMS'
            distribution.sent_at = timezone.now()
            distribution.delivery_status = 'PENDING'
            distribution.save()
            
            messages.info(request, f'SMS would be sent to {distribution.recipient_phone}: {sms_content}')
            
        else:
            messages.error(request, f'Cannot send via {channel} - missing recipient information')
        
        return redirect('experience_feedback:distribution_dashboard')
    
    context = {
        'distribution': distribution,
    }
    
    return render(request, 'experience_feedback/distribution_send.html', context)


def survey_qr_code(request, token):
    """
    Generate and serve QR code image for a survey token.
    Public view - no login required.
    """
    from .survey_distribution import get_survey_url, generate_qr_code
    from django.http import FileResponse
    import os
    
    # Get the full survey URL
    survey_url = get_survey_url(token, request)
    
    # Generate QR code
    qr_path = generate_qr_code(survey_url)
    
    # Serve the image
    full_path = os.path.join(settings.MEDIA_ROOT, qr_path)
    
    return FileResponse(open(full_path, 'rb'), content_type='image/png')


def survey_by_token(request, token):
    """
    Public survey form accessed via unique token.
    No login required - tracks distribution response.
    """
    from .models import SurveyDistribution
    
    # Find the distribution by token
    try:
        distribution = SurveyDistribution.objects.get(survey_token=token)
    except SurveyDistribution.DoesNotExist:
        messages.error(request, 'Invalid or expired survey link.')
        return render(request, 'experience_feedback/survey_error.html')
    
    # Check if already completed
    if distribution.response_received:
        messages.info(request, 'This survey has already been completed. Thank you!')
        return render(request, 'experience_feedback/survey_already_completed.html', {
            'distribution': distribution
        })
    
    if request.method == 'POST':
        form = PublicSurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.care_home = distribution.care_home
            survey.resident = distribution.resident
            survey.survey_type = distribution.survey_type
            survey.submission_method = 'ONLINE'
            survey.save()
            
            # Update distribution
            distribution.response_received = True
            distribution.response_date = timezone.now()
            distribution.survey_response = survey
            distribution.save()
            
            messages.success(request, 'Thank you for completing the survey!')
            return redirect('experience_feedback:survey_thank_you', token=token)
    else:
        # Pre-fill some data
        initial_data = {
            'survey_date': timezone.now().date(),
        }
        form = PublicSurveyForm(initial=initial_data)
    
    context = {
        'form': form,
        'distribution': distribution,
        'care_home': distribution.care_home,
        'resident': distribution.resident,
    }
    
    return render(request, 'experience_feedback/public_survey_token.html', context)


def survey_thank_you(request, token):
    """Thank you page after survey completion."""
    from .models import SurveyDistribution
    
    try:
        distribution = SurveyDistribution.objects.get(survey_token=token)
    except SurveyDistribution.DoesNotExist:
        distribution = None
    
    context = {
        'distribution': distribution,
    }
    
    return render(request, 'experience_feedback/survey_thank_you.html', context)


# ============================================================================
# FAMILY PORTAL VIEWS
# ============================================================================

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .models import FamilyMember, FamilyMessage, FamilyPortalActivity
from .forms import FamilyMessageForm, FamilyMessageResponseForm


def family_login(request):
    """Family portal login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user has family member profile
            try:
                family_member = user.family_member_profile
                if family_member.portal_access_granted:
                    login(request, user)
                    
                    # Log activity
                    FamilyPortalActivity.objects.create(
                        family_member=family_member,
                        activity_type='LOGIN',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                    )
                    
                    messages.success(request, f'Welcome back, {family_member.first_name}!')
                    return redirect('experience_feedback:family_dashboard')
                else:
                    messages.error(request, 'Your portal access has been disabled. Please contact the care home.')
            except FamilyMember.DoesNotExist:
                messages.error(request, 'This account does not have family portal access.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'experience_feedback/family_login.html')


@login_required
def family_logout(request):
    """Family portal logout view."""
    try:
        family_member = request.user.family_member_profile
        FamilyPortalActivity.objects.create(
            family_member=family_member,
            activity_type='LOGOUT',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    except FamilyMember.DoesNotExist:
        pass
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('experience_feedback:family_login')


@login_required
def family_dashboard(request):
    """Family portal dashboard."""
    try:
        family_member = request.user.family_member_profile
    except FamilyMember.DoesNotExist:
        messages.error(request, 'Family member profile not found.')
        return redirect('experience_feedback:family_login')
    
    # Log activity
    FamilyPortalActivity.objects.create(
        family_member=family_member,
        activity_type='VIEW_DASHBOARD',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Get statistics
    total_messages = FamilyMessage.objects.filter(family_member=family_member).count()
    unanswered_messages = FamilyMessage.objects.filter(
        family_member=family_member,
        staff_responded=False
    ).count()
    
    # Get recent messages
    recent_messages = FamilyMessage.objects.filter(
        family_member=family_member
    ).order_by('-sent_date')[:5]
    
    # Get recent surveys
    recent_surveys = SatisfactionSurvey.objects.filter(
        resident=family_member.resident
    ).order_by('-survey_date')[:5]
    
    # Get pending survey distributions
    from .models import SurveyDistribution
    pending_surveys = SurveyDistribution.objects.filter(
        recipient_email=family_member.email,
        response_received=False
    ).order_by('-sent_date')[:5]
    
    context = {
        'family_member': family_member,
        'resident': family_member.resident,
        'total_messages': total_messages,
        'unanswered_messages': unanswered_messages,
        'recent_messages': recent_messages,
        'recent_surveys': recent_surveys,
        'pending_surveys': pending_surveys,
    }
    
    return render(request, 'experience_feedback/family_dashboard.html', context)


@login_required
def family_messages_list(request):
    """List all messages for family member."""
    try:
        family_member = request.user.family_member_profile
    except FamilyMember.DoesNotExist:
        messages.error(request, 'Family member profile not found.')
        return redirect('experience_feedback:family_login')
    
    # Filter messages
    messages_qs = FamilyMessage.objects.filter(family_member=family_member)
    
    status_filter = request.GET.get('status')
    if status_filter == 'unanswered':
        messages_qs = messages_qs.filter(staff_responded=False)
    elif status_filter == 'answered':
        messages_qs = messages_qs.filter(staff_responded=True)
    
    category_filter = request.GET.get('category')
    if category_filter:
        messages_qs = messages_qs.filter(category=category_filter)
    
    messages_qs = messages_qs.order_by('-sent_date')
    
    context = {
        'family_member': family_member,
        'messages': messages_qs,
        'status_filter': status_filter,
        'category_filter': category_filter,
    }
    
    return render(request, 'experience_feedback/family_messages_list.html', context)


@login_required
def family_message_detail(request, message_id):
    """View message details."""
    try:
        family_member = request.user.family_member_profile
    except FamilyMember.DoesNotExist:
        messages.error(request, 'Family member profile not found.')
        return redirect('experience_feedback:family_login')
    
    message = get_object_or_404(FamilyMessage, id=message_id, family_member=family_member)
    
    # Log activity
    FamilyPortalActivity.objects.create(
        family_member=family_member,
        activity_type='VIEW_MESSAGE',
        description=f'Viewed message: {message.subject}',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    context = {
        'family_member': family_member,
        'message': message,
    }
    
    return render(request, 'experience_feedback/family_message_detail.html', context)


@login_required
def family_message_create(request):
    """Create a new message."""
    try:
        family_member = request.user.family_member_profile
    except FamilyMember.DoesNotExist:
        messages.error(request, 'Family member profile not found.')
        return redirect('experience_feedback:family_login')
    
    if request.method == 'POST':
        form = FamilyMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.family_member = family_member
            message.resident = family_member.resident
            message.care_home = family_member.resident.current_home
            message.save()
            
            # Log activity
            FamilyPortalActivity.objects.create(
                family_member=family_member,
                activity_type='SEND_MESSAGE',
                description=f'Sent message: {message.subject}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            messages.success(request, 'Your message has been sent to the care team.')
            return redirect('experience_feedback:family_message_detail', message_id=message.id)
    else:
        form = FamilyMessageForm()
    
    context = {
        'family_member': family_member,
        'form': form,
    }
    
    return render(request, 'experience_feedback/family_message_create.html', context)


@login_required
def family_surveys_list(request):
    """List surveys for family member's resident."""
    try:
        family_member = request.user.family_member_profile
    except FamilyMember.DoesNotExist:
        messages.error(request, 'Family member profile not found.')
        return redirect('experience_feedback:family_login')
    
    # Log activity
    FamilyPortalActivity.objects.create(
        family_member=family_member,
        activity_type='VIEW_SURVEYS',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Get completed surveys
    completed_surveys = SatisfactionSurvey.objects.filter(
        resident=family_member.resident
    ).order_by('-survey_date')
    
    # Get pending survey invitations
    from .models import SurveyDistribution
    pending_surveys = SurveyDistribution.objects.filter(
        recipient_email=family_member.email,
        response_received=False
    ).order_by('-sent_date')
    
    context = {
        'family_member': family_member,
        'completed_surveys': completed_surveys,
        'pending_surveys': pending_surveys,
    }
    
    return render(request, 'experience_feedback/family_surveys_list.html', context)


# ============================================================================
# STAFF VIEWS FOR FAMILY PORTAL MANAGEMENT
# ============================================================================

@login_required
def staff_family_messages(request):
    """Staff view of family messages (requires staff permissions)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('experience_feedback:experience_dashboard')
    
    # Get all messages or filter by care home
    messages_qs = FamilyMessage.objects.all()
    
    # Filter by care home if user has assigned home
    if hasattr(request.user, 'care_home'):
        messages_qs = messages_qs.filter(care_home=request.user.care_home)
    
    # Filter options
    status_filter = request.GET.get('status')
    if status_filter == 'unanswered':
        messages_qs = messages_qs.filter(staff_responded=False)
    elif status_filter == 'answered':
        messages_qs = messages_qs.filter(staff_responded=True)
    
    priority_filter = request.GET.get('priority')
    if priority_filter:
        messages_qs = messages_qs.filter(priority=priority_filter)
    
    messages_qs = messages_qs.order_by('-sent_date')
    
    # Statistics
    total_messages = messages_qs.count()
    unanswered = messages_qs.filter(staff_responded=False).count()
    urgent = messages_qs.filter(priority='URGENT', staff_responded=False).count()
    
    context = {
        'messages': messages_qs[:50],  # Limit to 50 for performance
        'total_messages': total_messages,
        'unanswered': unanswered,
        'urgent': urgent,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    
    return render(request, 'experience_feedback/staff_family_messages.html', context)


@login_required
def staff_message_respond(request, message_id):
    """Staff respond to family message."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('experience_feedback:experience_dashboard')
    
    message = get_object_or_404(FamilyMessage, id=message_id)
    
    # Mark as read if not already
    if not message.read_by_staff:
        message.read_by_staff = True
        message.read_date = timezone.now()
        message.save()
    
    if request.method == 'POST':
        form = FamilyMessageResponseForm(request.POST, instance=message)
        if form.is_valid():
            message = form.save(commit=False)
            message.staff_responded = True
            message.responder = request.user
            message.response_date = timezone.now()
            message.save()
            
            messages.success(request, 'Response sent successfully.')
            return redirect('experience_feedback:staff_family_messages')
    else:
        form = FamilyMessageResponseForm(instance=message)
    
    context = {
        'message': message,
        'form': form,
    }
    
    return render(request, 'experience_feedback/staff_message_respond.html', context)


# ============================================================================
# ADVANCED ANALYTICS VIEWS
# ============================================================================

@login_required
def analytics_dashboard(request):
    """
    Advanced analytics dashboard for Module 3 - Experience & Feedback.
    Comprehensive metrics across all experience management features.
    """
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('experience_feedback:experience_dashboard')
    
    # Date range filter (default: last 90 days)
    from datetime import date, timedelta
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    if request.GET.get('start_date'):
        start_date = date.fromisoformat(request.GET.get('start_date'))
    if request.GET.get('end_date'):
        end_date = date.fromisoformat(request.GET.get('end_date'))
    
    # Care home filter
    care_home_id = request.GET.get('care_home')
    care_homes = CareHome.objects.all()
    selected_home = None
    if care_home_id:
        selected_home = get_object_or_404(CareHome, id=care_home_id)
    
    # ========================================================================
    # SATISFACTION SURVEY ANALYTICS
    # ========================================================================
    
    surveys_qs = SatisfactionSurvey.objects.filter(
        survey_date__gte=start_date,
        survey_date__lte=end_date
    )
    if selected_home:
        surveys_qs = surveys_qs.filter(care_home=selected_home)
    
    total_surveys = surveys_qs.count()
    avg_satisfaction = surveys_qs.aggregate(
        avg=Avg('overall_satisfaction')
    )['avg'] or 0
    avg_nps = surveys_qs.aggregate(avg=Avg('nps_score'))['avg'] or 0
    
    # Survey breakdown by type
    survey_by_type = surveys_qs.values('survey_type').annotate(
        count=Count('id'),
        avg_score=Avg('overall_satisfaction')
    ).order_by('-count')
    
    # Monthly survey trend
    from django.db.models.functions import TruncMonth
    monthly_surveys = surveys_qs.annotate(
        month=TruncMonth('survey_date')
    ).values('month').annotate(
        count=Count('id'),
        avg_satisfaction=Avg('overall_satisfaction'),
        avg_nps=Avg('nps_score')
    ).order_by('month')
    
    # ========================================================================
    # COMPLAINT ANALYTICS
    # ========================================================================
    
    complaints_qs = Complaint.objects.filter(
        received_date__gte=start_date,
        received_date__lte=end_date
    )
    if selected_home:
        complaints_qs = complaints_qs.filter(care_home=selected_home)
    
    total_complaints = complaints_qs.count()
    resolved_complaints = complaints_qs.filter(
        status__in=['RESOLVED', 'CLOSED']
    ).count()
    open_complaints = complaints_qs.exclude(
        status__in=['RESOLVED', 'CLOSED']
    ).count()
    
    # Resolution rate
    resolution_rate = (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
    
    # Average resolution time (for resolved complaints)
    resolved_with_date = complaints_qs.filter(
        status__in=['RESOLVED', 'CLOSED'],
        resolution_date__isnull=False
    )
    
    avg_resolution_days = 0
    if resolved_with_date.exists():
        resolution_times = []
        for complaint in resolved_with_date:
            days = (complaint.resolution_date - complaint.received_date).days
            resolution_times.append(days)
        avg_resolution_days = sum(resolution_times) / len(resolution_times)
    
    # Complaints by severity
    complaints_by_severity = complaints_qs.values('severity').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Complaints by category
    complaints_by_category = complaints_qs.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:5]  # Top 5 categories
    
    # ========================================================================
    # FAMILY ENGAGEMENT ANALYTICS
    # ========================================================================
    
    family_messages_qs = FamilyMessage.objects.filter(
        sent_date__gte=timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time())),
        sent_date__lte=timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.max.time()))
    )
    if selected_home:
        family_messages_qs = family_messages_qs.filter(care_home=selected_home)
    
    total_family_messages = family_messages_qs.count()
    responded_messages = family_messages_qs.filter(staff_responded=True).count()
    pending_messages = family_messages_qs.filter(staff_responded=False).count()
    
    # Response rate
    response_rate = (responded_messages / total_family_messages * 100) if total_family_messages > 0 else 0
    
    # Average response time
    avg_response_time = 0
    responded_with_dates = family_messages_qs.filter(
        staff_responded=True,
        response_date__isnull=False
    )
    if responded_with_dates.exists():
        response_times = [msg.response_time_days() for msg in responded_with_dates if msg.response_time_days() is not None]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
    
    # Messages by priority
    messages_by_priority = family_messages_qs.values('priority').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Active family members
    from .models import FamilyMember
    active_family_members = FamilyMember.objects.filter(
        portal_access_granted=True,
        messages_sent__sent_date__gte=timezone.make_aware(
            timezone.datetime.combine(start_date, timezone.datetime.min.time())
        )
    ).distinct().count()
    
    # ========================================================================
    # YOU SAID WE DID ANALYTICS
    # ========================================================================
    
    from .models import YouSaidWeDidAction
    yswda_qs = YouSaidWeDidAction.objects.filter(
        feedback_date__gte=start_date,
        feedback_date__lte=end_date
    )
    
    total_actions = yswda_qs.count()
    completed_actions = yswda_qs.filter(status='COMPLETED').count()
    in_progress_actions = yswda_qs.filter(status='IN_PROGRESS').count()
    
    # Completion rate
    completion_rate = (completed_actions / total_actions * 100) if total_actions > 0 else 0
    
    # Actions by category
    actions_by_category = yswda_qs.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # ========================================================================
    # SURVEY DISTRIBUTION ANALYTICS
    # ========================================================================
    
    from .models import SurveyDistribution
    distributions_qs = SurveyDistribution.objects.filter(
        sent_date__gte=timezone.make_aware(
            timezone.datetime.combine(start_date, timezone.datetime.min.time())
        ),
        sent_date__lte=timezone.make_aware(
            timezone.datetime.combine(end_date, timezone.datetime.max.time())
        )
    )
    if selected_home:
        distributions_qs = distributions_qs.filter(care_home=selected_home)
    
    total_distributions = distributions_qs.count()
    completed_distributions = distributions_qs.filter(response_received=True).count()
    response_rate_surveys = (completed_distributions / total_distributions * 100) if total_distributions > 0 else 0
    
    # ========================================================================
    # OVERALL EXPERIENCE SCORE
    # ========================================================================
    
    # Calculate weighted overall experience score
    # 40% Satisfaction, 30% Complaint Resolution, 20% Family Engagement, 10% Action Completion
    overall_score = (
        (avg_satisfaction / 5 * 100 * 0.40) +
        (resolution_rate * 0.30) +
        (response_rate * 0.20) +
        (completion_rate * 0.10)
    )
    
    context = {
        # Filters
        'care_homes': care_homes,
        'selected_home': selected_home,
        'start_date': start_date,
        'end_date': end_date,
        
        # Overall Metrics
        'overall_score': round(overall_score, 1),
        
        # Survey Analytics
        'total_surveys': total_surveys,
        'avg_satisfaction': round(avg_satisfaction, 2),
        'avg_nps': round(avg_nps, 1),
        'survey_by_type': survey_by_type,
        'monthly_surveys': monthly_surveys,
        
        # Complaint Analytics
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'open_complaints': open_complaints,
        'resolution_rate': round(resolution_rate, 1),
        'avg_resolution_days': round(avg_resolution_days, 1),
        'complaints_by_severity': complaints_by_severity,
        'complaints_by_category': complaints_by_category,
        
        # Family Engagement
        'total_family_messages': total_family_messages,
        'responded_messages': responded_messages,
        'pending_messages': pending_messages,
        'response_rate': round(response_rate, 1),
        'avg_response_time': round(avg_response_time, 1),
        'messages_by_priority': messages_by_priority,
        'active_family_members': active_family_members,
        
        # You Said We Did
        'total_actions': total_actions,
        'completed_actions': completed_actions,
        'in_progress_actions': in_progress_actions,
        'completion_rate': round(completion_rate, 1),
        'actions_by_category': actions_by_category,
        
        # Survey Distribution
        'total_distributions': total_distributions,
        'completed_distributions': completed_distributions,
        'response_rate_surveys': round(response_rate_surveys, 1),
    }
    
    return render(request, 'experience_feedback/analytics_dashboard.html', context)


@login_required
def analytics_export(request):
    """Export analytics data as CSV."""
    import csv
    
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this resource.')
        return redirect('experience_feedback:experience_dashboard')
    
    # Get same data as analytics dashboard
    from datetime import date, timedelta
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    if request.GET.get('start_date'):
        start_date = date.fromisoformat(request.GET.get('start_date'))
    if request.GET.get('end_date'):
        end_date = date.fromisoformat(request.GET.get('end_date'))
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="experience_analytics_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Experience & Feedback Analytics Report'])
    writer.writerow([f'Period: {start_date} to {end_date}'])
    writer.writerow([])
    
    # Survey data
    surveys = SatisfactionSurvey.objects.filter(
        survey_date__gte=start_date,
        survey_date__lte=end_date
    )
    
    writer.writerow(['SATISFACTION SURVEYS'])
    writer.writerow(['Survey Type', 'Count', 'Avg Satisfaction', 'Avg NPS'])
    for survey_type in surveys.values('survey_type').annotate(
        count=Count('id'),
        avg_sat=Avg('overall_satisfaction'),
        avg_nps=Avg('nps_score')
    ):
        writer.writerow([
            survey_type['survey_type'],
            survey_type['count'],
            round(survey_type['avg_sat'] or 0, 2),
            round(survey_type['avg_nps'] or 0, 1)
        ])
    writer.writerow([])
    
    # Complaint data
    complaints = Complaint.objects.filter(
        received_date__gte=start_date,
        received_date__lte=end_date
    )
    
    writer.writerow(['COMPLAINTS'])
    writer.writerow(['Category', 'Severity', 'Status', 'Received Date', 'Resolution Date'])
    for complaint in complaints:
        writer.writerow([
            complaint.category,
            complaint.severity,
            complaint.status,
            complaint.received_date,
            complaint.resolution_date or 'Not resolved'
        ])
    writer.writerow([])
    
    # Family messages
    writer.writerow(['FAMILY MESSAGES'])
    writer.writerow(['Subject', 'Category', 'Priority', 'Sent Date', 'Responded', 'Response Time (days)'])
    messages_qs = FamilyMessage.objects.filter(
        sent_date__gte=timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time())),
        sent_date__lte=timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.max.time()))
    )
    for msg in messages_qs:
        writer.writerow([
            msg.subject,
            msg.category,
            msg.priority,
            msg.sent_date.strftime('%Y-%m-%d'),
            'Yes' if msg.staff_responded else 'No',
            msg.response_time_days() or 'N/A'
        ])
    
    return response
