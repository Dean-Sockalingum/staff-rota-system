"""
AI Dashboards Views
-------------------
Frontend views for AI-powered Quick Win features:
- Proactive Suggestions Dashboard
- Rota Health Scoring Dashboard
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, datetime
from scheduling.models import CareHome, Unit
from scheduling.utils_proactive_suggestions import (
    get_proactive_suggestions,
    get_high_priority_suggestions,
    get_suggestions_by_category
)
from scheduling.utils_rota_health_scoring import (
    score_rota,
    score_current_week,
    score_next_week
)


@login_required
def proactive_suggestions_dashboard(request):
    """
    Display AI-generated proactive suggestions for managers.
    
    Features:
    - 7 suggestion categories (staffing, leave, training, sickness, OT, fairness, compliance)
    - Priority filtering (high/medium/low)
    - Category filtering
    - Care home filtering
    - Look-ahead days configuration
    """
    # Get filter parameters
    care_home_id = request.GET.get('care_home')
    priority_filter = request.GET.get('priority', 'all')
    category_filter = request.GET.get('category', 'all')
    days_ahead = int(request.GET.get('days_ahead', 14))
    
    # Get care home context
    if care_home_id:
        care_home = get_object_or_404(CareHome, id=care_home_id)
    else:
        # Default to first care home or user's home
        if hasattr(request.user, 'care_home') and request.user.care_home:
            care_home = request.user.care_home
        else:
            care_home = CareHome.objects.first()
    
    # Get all suggestions
    all_suggestions = get_proactive_suggestions(
        care_home=care_home,
        days_ahead=days_ahead
    )
    
    # Apply filters
    filtered_suggestions = all_suggestions
    
    if priority_filter != 'all':
        filtered_suggestions = [
            s for s in filtered_suggestions
            if s['priority'] == priority_filter
        ]
    
    if category_filter != 'all':
        filtered_suggestions = [
            s for s in filtered_suggestions
            if s['category'] == category_filter
        ]
    
    # Count by priority
    high_count = len([s for s in all_suggestions if s['priority'] == 'high'])
    medium_count = len([s for s in all_suggestions if s['priority'] == 'medium'])
    low_count = len([s for s in all_suggestions if s['priority'] == 'low'])
    
    # Count by category
    category_counts = {}
    for suggestion in all_suggestions:
        cat = suggestion['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Available categories
    categories = [
        ('staffing', 'Staffing Levels'),
        ('leave', 'Leave Management'),
        ('training', 'Training & Compliance'),
        ('sickness', 'Sickness Patterns'),
        ('overtime_budget', 'Overtime Budget'),
        ('fairness', 'Fairness & Balance'),
        ('compliance', 'Regulatory Compliance'),
    ]
    
    context = {
        'suggestions': filtered_suggestions,
        'care_home': care_home,
        'all_care_homes': CareHome.objects.all(),
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'days_ahead': days_ahead,
        'high_count': high_count,
        'medium_count': medium_count,
        'low_count': low_count,
        'total_count': len(all_suggestions),
        'filtered_count': len(filtered_suggestions),
        'category_counts': category_counts,
        'categories': categories,
    }
    
    return render(request, 'scheduling/proactive_suggestions_dashboard.html', context)


@login_required
def rota_health_dashboard(request):
    """
    Display rota health scoring dashboard with quality metrics.
    
    Features:
    - Overall health score (0-100) with letter grade
    - 6 component scores (staffing, skill mix, fairness, cost, preferences, compliance)
    - Issues and recommendations
    - Historical trend graph
    - Week/month selector
    """
    # Get filter parameters
    care_home_id = request.GET.get('care_home')
    view_period = request.GET.get('period', 'current_week')  # current_week, next_week, custom
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Get care home context
    if care_home_id:
        care_home = get_object_or_404(CareHome, id=care_home_id)
    else:
        if hasattr(request.user, 'care_home') and request.user.care_home:
            care_home = request.user.care_home
        else:
            care_home = CareHome.objects.first()
    
    # Determine date range
    today = timezone.now().date()
    
    if view_period == 'current_week':
        # Monday to Sunday of current week
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif view_period == 'next_week':
        # Next Monday to Sunday
        start_date = today - timedelta(days=today.weekday()) + timedelta(days=7)
        end_date = start_date + timedelta(days=6)
    elif view_period == 'custom' and start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        # Default to current week
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    
    # Get rota health score
    score_data = score_rota(
        care_home=care_home,
        start_date=start_date,
        end_date=end_date
    )
    
    # Calculate historical scores (last 8 weeks for trend)
    historical_scores = []
    for weeks_ago in range(7, -1, -1):
        hist_start = start_date - timedelta(days=weeks_ago * 7)
        hist_end = hist_start + timedelta(days=6)
        hist_score = score_rota(care_home, hist_start, hist_end)
        historical_scores.append({
            'week_start': hist_start,
            'week_end': hist_end,
            'score': hist_score['overall_score'],
            'grade': hist_score['grade'],
        })
    
    # Prepare component data for chart
    components = [
        {'name': 'Staffing Levels', 'score': score_data['component_scores']['staffing_levels']},
        {'name': 'Skill Mix', 'score': score_data['component_scores']['skill_mix']},
        {'name': 'Fairness', 'score': score_data['component_scores']['fairness']},
        {'name': 'Cost Efficiency', 'score': score_data['component_scores']['cost_efficiency']},
        {'name': 'Preferences', 'score': score_data['component_scores']['preferences']},
        {'name': 'Compliance', 'score': score_data['component_scores']['compliance']},
    ]
    
    # Grade color mapping
    grade_colors = {
        'A': 'success',
        'B': 'info',
        'C': 'warning',
        'D': 'warning',
        'F': 'danger',
    }
    
    context = {
        'care_home': care_home,
        'all_care_homes': CareHome.objects.all(),
        'view_period': view_period,
        'start_date': start_date,
        'end_date': end_date,
        'overall_score': score_data['overall_score'],
        'grade': score_data['grade'],
        'grade_color': grade_colors.get(score_data['grade'], 'secondary'),
        'components': components,
        'component_scores': score_data['component_scores'],
        'issues': score_data['issues'],
        'suggestions': score_data['suggestions'],
        'historical_scores': historical_scores,
        'metadata': score_data['metadata'],
    }
    
    return render(request, 'scheduling/rota_health_dashboard.html', context)


@login_required
def rota_health_api(request):
    """
    JSON API for rota health scores (for AJAX updates).
    """
    care_home_id = request.GET.get('care_home')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if not all([care_home_id, start_date_str, end_date_str]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        care_home = CareHome.objects.get(id=care_home_id)
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except (CareHome.DoesNotExist, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    score_data = score_rota(care_home, start_date, end_date)
    
    return JsonResponse({
        'success': True,
        'score_data': score_data,
    })
