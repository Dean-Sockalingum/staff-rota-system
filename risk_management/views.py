"""
Risk Management Views

Comprehensive view layer for Scottish care home risk management.

Features:
- Risk register dashboard with 5x5 risk matrix
- CRUD operations for all risk entities
- Risk assessment workflows
- Mitigation tracking
- Review cycle management
- Chart.js visualizations (risk heat maps, trend analysis)
- CSV/PDF export functionality
- Integration with PDSA and incident modules
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
import csv

from .models import (
    RiskCategory,
    RiskRegister,
    RiskMitigation,
    RiskReview,
    RiskTreatmentPlan
)
from scheduling.models import CareHome


@login_required
def dashboard(request):
    """
    Risk management dashboard with:
    - Risk statistics by priority and status
    - 5x5 risk matrix heat map
    - Overdue reviews
    - Recent risk activity
    - Chart.js visualizations
    """
    user = request.user
    
    # Get user's care homes
    if hasattr(user, 'care_homes'):
        care_homes = user.care_homes.all()
    else:
        care_homes = CareHome.objects.all()
    
    # Filter risks by care home
    risks = RiskRegister.objects.filter(care_home__in=care_homes)
    
    # Statistics
    total_risks = risks.count()
    critical_risks = risks.filter(priority='CRITICAL').count()
    high_risks = risks.filter(priority='HIGH').count()
    medium_risks = risks.filter(priority='MEDIUM').count()
    low_risks = risks.filter(priority='LOW').count()
    
    # Status breakdown
    status_counts = risks.values('status').annotate(count=Count('id'))
    
    # Overdue reviews
    overdue_reviews = risks.filter(
        next_review_date__lt=timezone.now().date(),
        status__in=['IDENTIFIED', 'ASSESSED', 'MITIGATED', 'CONTROLLED']
    ).order_by('next_review_date')[:10]
    
    # Recent risks (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_risks = risks.filter(
        identified_date__gte=thirty_days_ago
    ).order_by('-identified_date')[:10]
    
    # Mitigation statistics
    all_mitigations = RiskMitigation.objects.filter(risk__care_home__in=care_homes)
    total_mitigations = all_mitigations.count()
    completed_mitigations = all_mitigations.filter(status='COMPLETED').count()
    overdue_mitigations = all_mitigations.filter(
        status__in=['PLANNED', 'IN_PROGRESS'],
        target_completion_date__lt=timezone.now().date()
    ).count()
    
    # Risk matrix data (5x5 grid)
    risk_matrix = {}
    for likelihood in range(1, 6):
        for impact in range(1, 6):
            count = risks.filter(
                residual_likelihood=likelihood,
                residual_impact=impact
            ).count()
            risk_matrix[f'{likelihood}_{impact}'] = count
    
    # Top risks by score
    top_risks = risks.order_by('-residual_score', 'next_review_date')[:10]
    
    # Category breakdown
    category_counts = risks.values(
        'category__name', 'category__color'
    ).annotate(count=Count('id')).order_by('-count')[:10]
    
    context = {
        'total_risks': total_risks,
        'critical_risks': critical_risks,
        'high_risks': high_risks,
        'medium_risks': medium_risks,
        'low_risks': low_risks,
        'status_counts': list(status_counts),
        'overdue_reviews': overdue_reviews,
        'recent_risks': recent_risks,
        'total_mitigations': total_mitigations,
        'completed_mitigations': completed_mitigations,
        'overdue_mitigations': overdue_mitigations,
        'risk_matrix': risk_matrix,
        'top_risks': top_risks,
        'category_counts': list(category_counts),
        'care_homes': care_homes,
    }
    
    return render(request, 'risk_management/dashboard.html', context)


@login_required
def dashboard_stats(request):
    """JSON endpoint for dashboard charts"""
    user = request.user
    
    if hasattr(user, 'care_homes'):
        care_homes = user.care_homes.all()
    else:
        care_homes = CareHome.objects.all()
    
    risks = RiskRegister.objects.filter(care_home__in=care_homes)
    
    # Priority distribution
    priority_data = {
        'CRITICAL': risks.filter(priority='CRITICAL').count(),
        'HIGH': risks.filter(priority='HIGH').count(),
        'MEDIUM': risks.filter(priority='MEDIUM').count(),
        'LOW': risks.filter(priority='LOW').count(),
    }
    
    # Status distribution
    status_data = {}
    for status_choice in RiskRegister.STATUS_CHOICES:
        status_data[status_choice[0]] = risks.filter(status=status_choice[0]).count()
    
    # Risk trend (last 12 months)
    trend_data = []
    for i in range(12, 0, -1):
        month_date = timezone.now().date() - timedelta(days=30*i)
        count = risks.filter(identified_date__month=month_date.month).count()
        trend_data.append({
            'month': month_date.strftime('%b %Y'),
            'count': count
        })
    
    # Category distribution
    category_data = list(
        risks.values('category__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    return JsonResponse({
        'priority': priority_data,
        'status': status_data,
        'trend': trend_data,
        'categories': category_data
    })


@login_required
def risk_list(request):
    """
    Risk register list view with:
    - Search and filters
    - Pagination
    - Sorting options
    - Export functionality
    """
    user = request.user
    
    if hasattr(user, 'care_homes'):
        care_homes = user.care_homes.all()
    else:
        care_homes = CareHome.objects.all()
    
    risks = RiskRegister.objects.filter(care_home__in=care_homes)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        risks = risks.filter(
            Q(risk_id__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filters
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        risks = risks.filter(priority=priority_filter)
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        risks = risks.filter(status=status_filter)
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        risks = risks.filter(category_id=category_filter)
    
    care_home_filter = request.GET.get('care_home', '')
    if care_home_filter:
        risks = risks.filter(care_home_id=care_home_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', '-residual_score')
    risks = risks.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(risks, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter dropdown
    categories = RiskCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'care_home_filter': care_home_filter,
        'sort_by': sort_by,
        'categories': categories,
        'care_homes': care_homes,
        'priority_choices': RiskRegister.STATUS_CHOICES,
        'status_choices': RiskRegister.STATUS_CHOICES,
    }
    
    return render(request, 'risk_management/risk_list.html', context)


@login_required
def risk_detail(request, pk):
    """
    Risk detail view showing:
    - Risk assessment details
    - 5x5 risk matrix position
    - Mitigations
    - Review history
    - Treatment plan (if exists)
    - Related incidents
    """
    risk = get_object_or_404(RiskRegister, pk=pk)
    
    # Check user has access to this care home
    user = request.user
    if hasattr(user, 'care_homes'):
        if risk.care_home not in user.care_homes.all():
            messages.error(request, 'You do not have access to this risk.')
            return redirect('risk_management:risk_list')
    
    # Get mitigations
    mitigations = risk.mitigations.all().order_by('-priority', 'target_completion_date')
    
    # Get reviews
    reviews = risk.reviews.all().order_by('-review_date')
    
    # Get treatment plan
    treatment_plan = None
    if hasattr(risk, 'treatment_plan'):
        treatment_plan = risk.treatment_plan
    
    # Calculate statistics
    total_mitigations = mitigations.count()
    completed_mitigations = mitigations.filter(status='COMPLETED').count()
    mitigation_completion_pct = (completed_mitigations / total_mitigations * 100) if total_mitigations > 0 else 0
    
    context = {
        'risk': risk,
        'mitigations': mitigations,
        'reviews': reviews,
        'treatment_plan': treatment_plan,
        'total_mitigations': total_mitigations,
        'completed_mitigations': completed_mitigations,
        'mitigation_completion_pct': mitigation_completion_pct,
    }
    
    return render(request, 'risk_management/risk_detail.html', context)


@login_required
def risk_create(request):
    """Create new risk"""
    user = request.user
    
    if hasattr(user, 'care_homes'):
        care_homes = user.care_homes.all()
    else:
        care_homes = CareHome.objects.all()
    
    if request.method == 'POST':
        # Process form data
        try:
            risk = RiskRegister(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                category_id=request.POST.get('category'),
                care_home_id=request.POST.get('care_home'),
                affected_area=request.POST.get('affected_area', ''),
                inherent_likelihood=int(request.POST.get('inherent_likelihood')),
                inherent_impact=int(request.POST.get('inherent_impact')),
                current_controls=request.POST.get('current_controls'),
                control_effectiveness=int(request.POST.get('control_effectiveness')),
                residual_likelihood=int(request.POST.get('residual_likelihood')),
                residual_impact=int(request.POST.get('residual_impact')),
                risk_owner=user,
                identified_by=user,
                status=request.POST.get('status', 'IDENTIFIED'),
                review_frequency=request.POST.get('review_frequency', 'MONTHLY'),
                next_review_date=request.POST.get('next_review_date'),
                regulatory_requirement=request.POST.get('regulatory_requirement', ''),
                notes=request.POST.get('notes', '')
            )
            
            # Optional target risk
            if request.POST.get('target_likelihood'):
                risk.target_likelihood = int(request.POST.get('target_likelihood'))
                risk.target_impact = int(request.POST.get('target_impact'))
            
            risk.save()
            
            messages.success(request, f'Risk "{risk.title}" created successfully.')
            return redirect('risk_management:risk_detail', pk=risk.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating risk: {str(e)}')
    
    categories = RiskCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'care_homes': care_homes,
        'categories': categories,
        'likelihood_choices': RiskRegister.LIKELIHOOD_CHOICES,
        'impact_choices': RiskRegister.IMPACT_CHOICES,
        'status_choices': RiskRegister.STATUS_CHOICES,
    }
    
    return render(request, 'risk_management/risk_form.html', context)


@login_required
def risk_edit(request, pk):
    """Edit existing risk"""
    risk = get_object_or_404(RiskRegister, pk=pk)
    
    # Check access
    user = request.user
    if hasattr(user, 'care_homes'):
        if risk.care_home not in user.care_homes.all():
            messages.error(request, 'You do not have access to this risk.')
            return redirect('risk_management:risk_list')
    
    if request.method == 'POST':
        try:
            risk.title = request.POST.get('title')
            risk.description = request.POST.get('description')
            risk.category_id = request.POST.get('category')
            risk.affected_area = request.POST.get('affected_area', '')
            risk.inherent_likelihood = int(request.POST.get('inherent_likelihood'))
            risk.inherent_impact = int(request.POST.get('inherent_impact'))
            risk.current_controls = request.POST.get('current_controls')
            risk.control_effectiveness = int(request.POST.get('control_effectiveness'))
            risk.residual_likelihood = int(request.POST.get('residual_likelihood'))
            risk.residual_impact = int(request.POST.get('residual_impact'))
            risk.status = request.POST.get('status')
            risk.review_frequency = request.POST.get('review_frequency')
            risk.next_review_date = request.POST.get('next_review_date')
            risk.regulatory_requirement = request.POST.get('regulatory_requirement', '')
            risk.notes = request.POST.get('notes', '')
            
            # Optional target risk
            if request.POST.get('target_likelihood'):
                risk.target_likelihood = int(request.POST.get('target_likelihood'))
                risk.target_impact = int(request.POST.get('target_impact'))
            else:
                risk.target_likelihood = None
                risk.target_impact = None
            
            risk.save()
            
            messages.success(request, f'Risk "{risk.title}" updated successfully.')
            return redirect('risk_management:risk_detail', pk=risk.pk)
            
        except Exception as e:
            messages.error(request, f'Error updating risk: {str(e)}')
    
    if hasattr(user, 'care_homes'):
        care_homes = user.care_homes.all()
    else:
        care_homes = CareHome.objects.all()
    
    categories = RiskCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'risk': risk,
        'care_homes': care_homes,
        'categories': categories,
        'likelihood_choices': RiskRegister.LIKELIHOOD_CHOICES,
        'impact_choices': RiskRegister.IMPACT_CHOICES,
        'status_choices': RiskRegister.STATUS_CHOICES,
        'is_edit': True,
    }
    
    return render(request, 'risk_management/risk_form.html', context)


@login_required
def risk_delete(request, pk):
    """Delete risk"""
    risk = get_object_or_404(RiskRegister, pk=pk)
    
    # Check access
    user = request.user
    if hasattr(user, 'care_homes'):
        if risk.care_home not in user.care_homes.all():
            messages.error(request, 'You do not have access to this risk.')
            return redirect('risk_management:risk_list')
    
    if request.method == 'POST':
        risk_title = risk.title
        risk.delete()
        messages.success(request, f'Risk "{risk_title}" deleted successfully.')
        return redirect('risk_management:risk_list')
    
    context = {'risk': risk}
    return render(request, 'risk_management/risk_confirm_delete.html', context)


@login_required
def mitigation_create(request, risk_pk):
    """Create mitigation for a risk"""
    risk = get_object_or_404(RiskRegister, pk=risk_pk)
    
    # Check access
    user = request.user
    if hasattr(user, 'care_homes'):
        if risk.care_home not in user.care_homes.all():
            messages.error(request, 'You do not have access to this risk.')
            return redirect('risk_management:risk_list')
    
    if request.method == 'POST':
        try:
            mitigation = RiskMitigation(
                risk=risk,
                action=request.POST.get('action'),
                description=request.POST.get('description'),
                mitigation_type=request.POST.get('mitigation_type'),
                expected_likelihood_reduction=int(request.POST.get('expected_likelihood_reduction')),
                expected_impact_reduction=int(request.POST.get('expected_impact_reduction')),
                status=request.POST.get('status', 'PLANNED'),
                priority=request.POST.get('priority', 'MEDIUM'),
                assigned_to_id=request.POST.get('assigned_to'),
                target_completion_date=request.POST.get('target_completion_date'),
                estimated_cost=request.POST.get('estimated_cost') or None,
                resources_required=request.POST.get('resources_required', ''),
                regulatory_requirement=request.POST.get('regulatory_requirement') == 'on',
                created_by=user
            )
            
            if request.POST.get('start_date'):
                mitigation.start_date = request.POST.get('start_date')
            
            mitigation.save()
            
            messages.success(request, f'Mitigation "{mitigation.action}" created successfully.')
            return redirect('risk_management:risk_detail', pk=risk.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating mitigation: {str(e)}')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'risk': risk,
        'users': users,
        'mitigation_types': RiskMitigation.TYPE_CHOICES,
        'priority_choices': RiskMitigation.PRIORITY_CHOICES,
        'status_choices': RiskMitigation.STATUS_CHOICES,
    }
    
    return render(request, 'risk_management/mitigation_form.html', context)


@login_required
def review_create(request, risk_pk):
    """Create risk review"""
    risk = get_object_or_404(RiskRegister, pk=risk_pk)
    
    # Check access
    user = request.user
    if hasattr(user, 'care_homes'):
        if risk.care_home not in user.care_homes.all():
            messages.error(request, 'You do not have access to this risk.')
            return redirect('risk_management:risk_list')
    
    if request.method == 'POST':
        try:
            review = RiskReview(
                risk=risk,
                review_date=request.POST.get('review_date', timezone.now().date()),
                reviewed_by=user,
                reassessed_likelihood=int(request.POST.get('reassessed_likelihood')),
                reassessed_impact=int(request.POST.get('reassessed_impact')),
                controls_effective=request.POST.get('controls_effective') == 'on',
                control_gaps=request.POST.get('control_gaps', ''),
                new_mitigations_required=request.POST.get('new_mitigations_required') == 'on',
                recommended_actions=request.POST.get('recommended_actions', ''),
                decision=request.POST.get('decision'),
                decision_rationale=request.POST.get('decision_rationale'),
                next_review_date=request.POST.get('next_review_date'),
                follow_up_actions=request.POST.get('follow_up_actions', ''),
                changes_in_environment=request.POST.get('changes_in_environment', ''),
                notes=request.POST.get('notes', '')
            )
            
            review.save()
            
            # Update risk's last reviewed date and next review date
            risk.last_reviewed = review.review_date
            risk.next_review_date = review.next_review_date
            
            # Update risk status based on decision
            if review.decision == 'CLOSE':
                risk.status = 'CLOSED'
            elif review.decision == 'ESCALATE':
                risk.status = 'ESCALATED'
                risk.is_escalated = True
            elif review.decision == 'ACCEPT':
                risk.status = 'ACCEPTED'
            
            # Update residual risk based on reassessment
            risk.residual_likelihood = review.reassessed_likelihood
            risk.residual_impact = review.reassessed_impact
            
            risk.save()
            
            messages.success(request, 'Risk review completed successfully.')
            return redirect('risk_management:risk_detail', pk=risk.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating review: {str(e)}')
    
    context = {
        'risk': risk,
        'likelihood_choices': RiskRegister.LIKELIHOOD_CHOICES,
        'impact_choices': RiskRegister.IMPACT_CHOICES,
        'decision_choices': RiskReview.DECISION_CHOICES,
    }
    
    return render(request, 'risk_management/review_form.html', context)


@login_required
def risk_matrix(request):
    """
    5x5 Risk Matrix visualization showing:
    - All risks positioned by likelihood and impact
    - Color-coded zones (red/amber/yellow/green)
    - Interactive hover details
    - Filter by care home, category
    """
    user = request.user
    
    if hasattr(user, 'care_homes'):
        care_homes = user.care_homes.all()
    else:
        care_homes = CareHome.objects.all()
    
    risks = RiskRegister.objects.filter(care_home__in=care_homes)
    
    # Apply filters
    care_home_filter = request.GET.get('care_home', '')
    if care_home_filter:
        risks = risks.filter(care_home_id=care_home_filter)
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        risks = risks.filter(category_id=category_filter)
    
    # Build matrix data structure
    matrix_data = {}
    for likelihood in range(1, 6):
        for impact in range(1, 6):
            key = f'{likelihood}_{impact}'
            matrix_risks = risks.filter(
                residual_likelihood=likelihood,
                residual_impact=impact
            )
            matrix_data[key] = {
                'count': matrix_risks.count(),
                'risks': list(matrix_risks.values('id', 'risk_id', 'title', 'priority'))
            }
    
    categories = RiskCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'matrix_data': matrix_data,
        'care_homes': care_homes,
        'categories': categories,
        'care_home_filter': care_home_filter,
        'category_filter': category_filter,
    }
    
    return render(request, 'risk_management/risk_matrix.html', context)


@login_required
def export_risks_csv(request):
    """Export risks to CSV"""
    user = request.user
    
    if hasattr(user, 'care_homes'):
        care_homes = user.care_homes.all()
    else:
        care_homes = CareHome.objects.all()
    
    risks = RiskRegister.objects.filter(care_home__in=care_homes).order_by('-residual_score')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="risk_register_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Risk ID', 'Title', 'Care Home', 'Category', 'Status', 'Priority',
        'Inherent Likelihood', 'Inherent Impact', 'Inherent Score',
        'Residual Likelihood', 'Residual Impact', 'Residual Score',
        'Risk Owner', 'Identified Date', 'Next Review Date',
        'Current Controls', 'Regulatory Requirement'
    ])
    
    for risk in risks:
        writer.writerow([
            risk.risk_id,
            risk.title,
            risk.care_home.name,
            risk.category.name,
            risk.get_status_display(),
            risk.priority,
            risk.inherent_likelihood,
            risk.inherent_impact,
            risk.inherent_score,
            risk.residual_likelihood,
            risk.residual_impact,
            risk.residual_score,
            f'{risk.risk_owner.first_name} {risk.risk_owner.last_name}',
            risk.identified_date,
            risk.next_review_date,
            risk.current_controls[:100],  # Truncate for CSV
            risk.regulatory_requirement[:100] if risk.regulatory_requirement else ''
        ])
    
    return response


@login_required
def reports(request):
    """
    Risk management reports dashboard:
    - Risk register summary
    - Mitigation effectiveness
    - Review compliance
    - Trend analysis
    - Export options
    """
    user = request.user
    
    if hasattr(user, 'care_homes'):
        care_homes = user.care_homes.all()
    else:
        care_homes = CareHome.objects.all()
    
    risks = RiskRegister.objects.filter(care_home__in=care_homes)
    
    # Summary statistics
    total_risks = risks.count()
    open_risks = risks.exclude(status__in=['CLOSED', 'ACCEPTED']).count()
    
    # Risk by priority
    priority_breakdown = {
        'CRITICAL': risks.filter(priority='CRITICAL').count(),
        'HIGH': risks.filter(priority='HIGH').count(),
        'MEDIUM': risks.filter(priority='MEDIUM').count(),
        'LOW': risks.filter(priority='LOW').count(),
    }
    
    # Mitigation effectiveness
    all_mitigations = RiskMitigation.objects.filter(risk__care_home__in=care_homes)
    avg_effectiveness = all_mitigations.filter(
        effectiveness_rating__isnull=False
    ).aggregate(Avg('effectiveness_rating'))['effectiveness_rating__avg'] or 0
    
    # Review compliance
    overdue_reviews = risks.filter(
        next_review_date__lt=timezone.now().date(),
        status__in=['IDENTIFIED', 'ASSESSED', 'MITIGATED', 'CONTROLLED']
    ).count()
    
    review_compliance_pct = ((total_risks - overdue_reviews) / total_risks * 100) if total_risks > 0 else 100
    
    # Category breakdown
    category_breakdown = list(
        risks.values('category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    context = {
        'total_risks': total_risks,
        'open_risks': open_risks,
        'priority_breakdown': priority_breakdown,
        'avg_effectiveness': avg_effectiveness,
        'overdue_reviews': overdue_reviews,
        'review_compliance_pct': review_compliance_pct,
        'category_breakdown': category_breakdown,
        'care_homes': care_homes,
    }
    
    return render(request, 'risk_management/reports.html', context)
