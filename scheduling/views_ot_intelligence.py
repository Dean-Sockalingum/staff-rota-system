"""
Intelligent Overtime Distribution Dashboard Views
Provides managers with visibility into OT ranking system and fairness metrics
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta

from .decorators_api import api_login_required
from .models import Shift, User
from .models_overtime import (
    StaffOvertimePreference, 
    OvertimeCoverageRequest,
    OvertimeCoverageResponse
)
from .utils_overtime_intelligence import (
    OvertimeRanker,
    OvertimeCoverageOrchestrator,
    auto_request_ot_coverage
)


@login_required
def ot_intelligence_dashboard(request):
    """
    Main dashboard showing intelligent OT distribution system
    
    Features:
    - Live OT rankings for all staff
    - Fairness metrics (OT distribution)
    - Recent coverage requests
    - Acceptance rate leaderboard
    """
    # Get all staff with OT preferences
    ot_staff = StaffOvertimePreference.objects.filter(
        available_for_overtime=True
    ).select_related('staff').order_by('-acceptance_rate')
    
    # Calculate fairness metrics
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    ot_shifts = Shift.objects.filter(
        date__gte=thirty_days_ago,
        shift_classification='OVERTIME'
    ).values('user').annotate(
        ot_count=Count('id')
    ).order_by('-ot_count')
    
    # Create staff OT distribution map
    ot_distribution = {item['user']: item['ot_count'] for item in ot_shifts}
    
    # Calculate fairness score (0-100, higher is more fair)
    if ot_distribution:
        counts = list(ot_distribution.values())
        avg_ot = sum(counts) / len(counts)
        variance = sum((x - avg_ot) ** 2 for x in counts) / len(counts)
        std_dev = variance ** 0.5
        
        # Lower std dev = more fair distribution
        # Perfect fairness (std_dev=0) = 100, high variance = lower score
        fairness_score = max(0, 100 - (std_dev * 10))
    else:
        fairness_score = 100  # No OT yet = perfectly fair
    
    # Recent coverage requests
    recent_requests = OvertimeCoverageRequest.objects.select_related(
        'unit', 'filled_by', 'created_by'
    ).order_by('-created_at')[:20]
    
    # Top performers (highest acceptance + worked)
    top_performers = ot_staff.filter(
        total_shifts_worked__gte=3
    ).order_by('-acceptance_rate', '-total_shifts_worked')[:10]
    
    # Response time analytics
    filled_requests = OvertimeCoverageRequest.objects.filter(
        status='FILLED',
        time_to_fill_minutes__isnull=False
    )
    avg_response_time = filled_requests.aggregate(
        avg=Avg('time_to_fill_minutes')
    )['avg'] or 0
    
    context = {
        'ot_staff_count': ot_staff.count(),
        'fairness_score': round(fairness_score, 1),
        'ot_distribution': ot_distribution,
        'recent_requests': recent_requests,
        'top_performers': top_performers,
        'avg_response_time': round(avg_response_time, 1),
        'total_ot_shifts_30d': sum(ot_distribution.values()) if ot_distribution else 0,
    }
    
    return render(request, 'scheduling/ot_intelligence/dashboard.html', context)


@login_required
def ot_staff_rankings(request):
    """
    Live rankings for a hypothetical shift
    Shows how staff would be ranked for OT opportunity
    
    Query params:
    - date: Shift date (YYYY-MM-DD)
    - shift_type: DAY or NIGHT
    - care_home_id: CareHome ID
    """
    from datetime import datetime
    from .models import CareHome
    
    # Get parameters or use defaults
    shift_date_str = request.GET.get('date')
    shift_type = request.GET.get('shift_type', 'DAY').upper()
    care_home_id = request.GET.get('care_home_id')
    
    if shift_date_str:
        shift_date = datetime.strptime(shift_date_str, '%Y-%m-%d').date()
    else:
        shift_date = timezone.now().date() + timedelta(days=1)  # Tomorrow
    
    if care_home_id:
        care_home = get_object_or_404(CareHome, id=care_home_id)
    else:
        care_home = CareHome.objects.first()
    
    # Create ranker
    ranker = OvertimeRanker(
        shift_date=shift_date,
        shift_type=shift_type,
        care_home=care_home
    )
    
    # Get all ranked staff
    ranked_staff = ranker.rank_all_available_staff()
    
    # Get all care homes for selector
    care_homes = CareHome.objects.all()
    
    context = {
        'ranked_staff': ranked_staff[:20],  # Top 20
        'shift_date': shift_date,
        'shift_type': shift_type,
        'care_home': care_home,
        'care_homes': care_homes,
        'total_eligible': len(ranked_staff),
    }
    
    return render(request, 'scheduling/ot_intelligence/rankings.html', context)


@login_required
def ot_fairness_report(request):
    """
    Detailed fairness report showing OT distribution across all staff
    
    Helps managers ensure fair distribution of overtime opportunities
    """
    # Get date range (default: last 90 days)
    days = int(request.GET.get('days', 90))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Get all OT-willing staff
    ot_staff = StaffOvertimePreference.objects.filter(
        available_for_overtime=True
    ).select_related('staff', 'staff__role')
    
    # Calculate OT distribution for each staff
    staff_data = []
    for pref in ot_staff:
        ot_shifts = Shift.objects.filter(
            user=pref.staff,
            date__gte=start_date,
            shift_classification='OVERTIME'
        ).count()
        
        total_hours = ot_shifts * 8  # Assume 8 hour shifts
        
        staff_data.append({
            'staff': pref.staff,
            'ot_shifts': ot_shifts,
            'ot_hours': total_hours,
            'acceptance_rate': pref.acceptance_rate,
            'total_requests': pref.total_requests_sent,
            'last_ot_date': pref.last_worked_overtime,
        })
    
    # Sort by OT hours (highest to lowest)
    staff_data.sort(key=lambda x: x['ot_hours'], reverse=True)
    
    # Calculate statistics
    total_ot_hours = sum(s['ot_hours'] for s in staff_data)
    avg_ot_hours = total_ot_hours / len(staff_data) if staff_data else 0
    
    # Find staff who are under-utilized (below average)
    underutilized = [s for s in staff_data if s['ot_hours'] < avg_ot_hours]
    
    # Find staff who are over-utilized (above 1.5x average)
    overutilized = [s for s in staff_data if s['ot_hours'] > avg_ot_hours * 1.5]
    
    context = {
        'staff_data': staff_data,
        'days': days,
        'total_ot_hours': total_ot_hours,
        'avg_ot_hours': round(avg_ot_hours, 1),
        'underutilized': underutilized[:10],
        'overutilized': overutilized,
        'staff_count': len(staff_data),
    }
    
    return render(request, 'scheduling/ot_intelligence/fairness_report.html', context)


@api_login_required
def ot_request_coverage_api(request):
    """
    API endpoint to trigger intelligent OT coverage request
    
    POST data:
    - shift_id: ID of shift needing coverage
    - top_n: Number of staff to contact (default: 5)
    
    Returns:
    - JSON with coverage request details and contacted staff
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    import json
    data = json.loads(request.body)
    
    shift_id = data.get('shift_id')
    top_n = int(data.get('top_n', 5))
    
    if not shift_id:
        return JsonResponse({'error': 'shift_id required'}, status=400)
    
    try:
        shift = Shift.objects.get(id=shift_id)
    except Shift.DoesNotExist:
        return JsonResponse({'error': 'Shift not found'}, status=404)
    
    # Trigger intelligent OT coverage
    result = auto_request_ot_coverage(shift, top_n=top_n)
    
    # Format response
    response_data = {
        'success': True,
        'coverage_request_id': result['coverage_request'].id,
        'total_contacted': result['total_contacted'],
        'contacted_staff': [
            {
                'sap': s['staff'].sap,
                'name': s['staff'].full_name,
                'score': s['score'],
                'contact_method': s['contact_method'],
            }
            for s in result['contacted_staff']
        ]
    }
    
    return JsonResponse(response_data)


@login_required
def ot_staff_detail(request, sap):
    """
    Detailed view of individual staff member's OT history and ranking factors
    
    Args:
        sap: Staff SAP number
    """
    staff = get_object_or_404(User, sap=sap)
    
    try:
        preference = StaffOvertimePreference.objects.get(staff=staff)
    except StaffOvertimePreference.DoesNotExist:
        preference = None
    
    # Get OT history (last 6 months)
    six_months_ago = timezone.now().date() - timedelta(days=180)
    ot_shifts = Shift.objects.filter(
        user=staff,
        date__gte=six_months_ago,
        shift_classification='OVERTIME'
    ).select_related('unit', 'shift_type').order_by('-date')
    
    # Get coverage responses
    responses = OvertimeCoverageResponse.objects.filter(
        staff=staff
    ).select_related('request', 'request__unit').order_by('-responded_at')[:20]
    
    # Calculate monthly OT trends
    monthly_ot = {}
    for shift in ot_shifts:
        month_key = shift.date.strftime('%Y-%m')
        monthly_ot[month_key] = monthly_ot.get(month_key, 0) + 1
    
    context = {
        'staff': staff,
        'preference': preference,
        'ot_shifts': ot_shifts,
        'ot_shift_count': ot_shifts.count(),
        'responses': responses,
        'monthly_ot': monthly_ot,
    }
    
    return render(request, 'scheduling/ot_intelligence/staff_detail.html', context)


@api_login_required
def ot_analytics_api(request):
    """
    API endpoint for OT analytics data (for charts)
    
    Returns JSON with:
    - Acceptance rate distribution
    - Response time metrics
    - Fairness trends over time
    """
    # Acceptance rate distribution
    acceptance_buckets = {
        '0-20%': 0,
        '21-40%': 0,
        '41-60%': 0,
        '61-80%': 0,
        '81-100%': 0,
    }
    
    ot_staff = StaffOvertimePreference.objects.filter(available_for_overtime=True)
    for pref in ot_staff:
        rate = float(pref.acceptance_rate)
        if rate <= 20:
            acceptance_buckets['0-20%'] += 1
        elif rate <= 40:
            acceptance_buckets['21-40%'] += 1
        elif rate <= 60:
            acceptance_buckets['41-60%'] += 1
        elif rate <= 80:
            acceptance_buckets['61-80%'] += 1
        else:
            acceptance_buckets['81-100%'] += 1
    
    # Response time by hour of day
    requests_by_hour = {}
    filled_requests = OvertimeCoverageRequest.objects.filter(
        status='FILLED',
        time_to_fill_minutes__isnull=False
    )
    
    for req in filled_requests:
        hour = req.created_at.hour
        if hour not in requests_by_hour:
            requests_by_hour[hour] = []
        requests_by_hour[hour].append(req.time_to_fill_minutes)
    
    avg_response_by_hour = {
        hour: sum(times) / len(times)
        for hour, times in requests_by_hour.items()
    }
    
    data = {
        'acceptance_distribution': acceptance_buckets,
        'avg_response_by_hour': avg_response_by_hour,
        'total_ot_staff': ot_staff.count(),
        'avg_acceptance_rate': float(ot_staff.aggregate(Avg('acceptance_rate'))['acceptance_rate__avg'] or 0),
    }
    
    return JsonResponse(data)
