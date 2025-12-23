"""
Views for shift optimization dashboard

Task 12: ML Phase 4 - Shift Optimization
Provides OM/SM interface to run optimization algorithm and review results
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Sum
from datetime import date, timedelta
import json
import logging

from .models import StaffingForecast, Shift, User, Unit
from .models_multi_home import CareHome
from .shift_optimizer import ShiftOptimizer, optimize_shifts_for_forecast

logger = logging.getLogger(__name__)


def is_operations_or_senior_manager(user):
    """Permission check: Only OM/SM can access optimization"""
    if not user.is_authenticated:
        return False
    if not user.role:
        return False
    return (user.role.name == 'OM' or 
            user.role.is_senior_management_team)


@login_required
@user_passes_test(is_operations_or_senior_manager)
def shift_optimization_dashboard(request):
    """
    Main shift optimization dashboard
    
    Features:
    - Select care home, date range
    - Run optimization algorithm
    - Preview suggested assignments
    - Cost comparison (current vs optimized)
    - Apply assignments to rota
    """
    # Get care homes (OM sees their home, SM sees all)
    if request.user.role.is_senior_management_team:
        care_homes = CareHome.objects.all().order_by('name')
    else:
        # OM sees only their assigned home
        care_homes = CareHome.objects.filter(
            units__in=Unit.objects.filter(current_staff=request.user)
        ).distinct().order_by('name')
    
    # Get selected care home (from query param or first available)
    selected_home_name = request.GET.get('care_home')
    if selected_home_name:
        care_home = CareHome.objects.filter(name=selected_home_name).first()
    else:
        care_home = care_homes.first()
    
    if not care_home:
        return render(request, 'scheduling/shift_optimization.html', {
            'error': 'No care homes available for optimization',
            'care_homes': care_homes,
        })
    
    # Date range for optimization (default: tomorrow for 7 days)
    start_date_str = request.GET.get('start_date')
    days_ahead = int(request.GET.get('days_ahead', 7))
    
    if start_date_str:
        try:
            start_date = date.fromisoformat(start_date_str)
        except ValueError:
            start_date = date.today() + timedelta(days=1)
    else:
        start_date = date.today() + timedelta(days=1)
    
    # Get forecasts for date range
    end_date = start_date + timedelta(days=days_ahead - 1)
    
    forecasts = StaffingForecast.objects.filter(
        care_home=care_home,
        forecast_date__gte=start_date,
        forecast_date__lte=end_date
    ).select_related('unit', 'care_home').order_by('forecast_date', 'unit__name')
    
    # Count existing shifts in this period
    existing_shifts = Shift.objects.filter(
        unit__care_home=care_home,
        date__gte=start_date,
        date__lte=end_date,
        status__in=['SCHEDULED', 'CONFIRMED']
    )
    
    existing_count = existing_shifts.count()
    
    # Calculate current cost (existing shifts)
    current_cost = 0
    for shift in existing_shifts:
        # Estimate cost based on shift classification
        if shift.shift_classification == 'AGENCY':
            hourly_rate = float(shift.agency_hourly_rate) if shift.agency_hourly_rate else 25.0
        elif shift.shift_classification == 'OVERTIME':
            hourly_rate = 18.0  # Avg overtime rate
        else:
            hourly_rate = 13.5  # Avg permanent staff rate
        
        current_cost += hourly_rate * shift.duration_hours
    
    # Units for this care home
    units = care_home.units.filter(is_active=True).order_by('name')
    
    # Add uncertainty percentage to each forecast
    forecast_list = []
    for forecast in forecasts[:30]:
        forecast_dict = {
            'forecast': forecast,
            'uncertainty_pct': round(
                ((float(forecast.confidence_upper) - float(forecast.confidence_lower)) / float(forecast.predicted_shifts) * 100)
                if forecast.predicted_shifts > 0 else 0
            )
        }
        forecast_list.append(forecast_dict)
    
    # Summary statistics
    summary = {
        'care_home': care_home.get_name_display(),
        'start_date': start_date,
        'end_date': end_date,
        'days_ahead': days_ahead,
        'forecast_count': forecasts.count(),
        'existing_shifts': existing_count,
        'current_cost': round(current_cost, 2),
        'units': units.count(),
    }
    
    context = {
        'care_homes': care_homes,
        'selected_home': care_home,
        'summary': summary,
        'forecasts': forecast_list,
        'units': units,
    }
    
    return render(request, 'scheduling/shift_optimization.html', context)


@login_required
@user_passes_test(is_operations_or_senior_manager)
def run_optimization(request):
    """
    AJAX endpoint to run optimization algorithm
    
    POST params:
    - care_home: Care home name
    - start_date: ISO date string
    - days_ahead: Number of days to optimize
    
    Returns:
        JSON with optimization results, cost savings, suggested assignments
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        care_home_name = data.get('care_home')
        start_date_str = data.get('start_date')
        days_ahead = int(data.get('days_ahead', 1))
        
        # Validate inputs
        if not care_home_name or not start_date_str:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        care_home = CareHome.objects.filter(name=care_home_name).first()
        if not care_home:
            return JsonResponse({'error': f'Care home {care_home_name} not found'}, status=404)
        
        start_date = date.fromisoformat(start_date_str)
        
        # Permission check: OM can only optimize their own home
        if not request.user.role.is_senior_management_team:
            if not request.user.can_access_home(care_home):
                return JsonResponse({'error': 'Unauthorized for this care home'}, status=403)
        
        # Run optimization
        logger.info(f"Running optimization for {care_home} from {start_date} ({days_ahead} days)")
        
        results = optimize_shifts_for_forecast(
            care_home=care_home,
            forecast_date=start_date,
            days_ahead=days_ahead
        )
        
        # Calculate total cost and assignments
        total_optimized_cost = sum(r.total_cost for r in results if r.success)
        total_assignments = sum(len(r.assignments) for r in results if r.success)
        
        # Get current cost for comparison
        end_date = start_date + timedelta(days=days_ahead - 1)
        existing_shifts = Shift.objects.filter(
            unit__care_home=care_home,
            date__gte=start_date,
            date__lte=end_date,
            status__in=['SCHEDULED', 'CONFIRMED']
        )
        
        current_cost = 0
        for shift in existing_shifts:
            if shift.shift_classification == 'AGENCY':
                hourly_rate = float(shift.agency_hourly_rate) if shift.agency_hourly_rate else 25.0
            elif shift.shift_classification == 'OVERTIME':
                hourly_rate = 18.0
            else:
                hourly_rate = 13.5
            current_cost += hourly_rate * shift.duration_hours
        
        cost_savings = current_cost - total_optimized_cost
        savings_percentage = (cost_savings / current_cost * 100) if current_cost > 0 else 0
        
        # Format results for JSON response
        results_data = []
        for result in results:
            if result.success:
                results_data.append({
                    'status': result.status,
                    'cost': round(result.total_cost, 2),
                    'assignments': result.assignments,
                    'metrics': result.metrics,
                })
            else:
                results_data.append({
                    'status': result.status,
                    'error': result.metrics.get('error', 'Unknown error'),
                })
        
        response_data = {
            'success': True,
            'total_cost': round(total_optimized_cost, 2),
            'current_cost': round(current_cost, 2),
            'cost_savings': round(cost_savings, 2),
            'savings_percentage': round(savings_percentage, 1),
            'total_assignments': total_assignments,
            'results': results_data,
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_operations_or_senior_manager)
def apply_optimization(request):
    """
    AJAX endpoint to apply optimization results to rota
    
    Creates Shift instances from optimization assignments
    
    POST params:
    - assignments: List of assignment dicts from optimization
    
    Returns:
        JSON with created shift count
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        assignments = data.get('assignments', [])
        
        if not assignments:
            return JsonResponse({'error': 'No assignments provided'}, status=400)
        
        created_shifts = []
        errors = []
        
        from .models import ShiftType
        
        for assignment in assignments:
            try:
                # Get unit
                unit = Unit.objects.get(name=assignment['unit'])
                
                # Get shift type
                shift_type = ShiftType.objects.get(name=assignment['shift_type'])
                
                # Get staff
                staff = User.objects.get(sap=assignment['staff_sap'])
                
                # Check if shift already exists
                existing = Shift.objects.filter(
                    user=staff,
                    unit=unit,
                    shift_type=shift_type,
                    date=assignment['date']
                ).exists()
                
                if existing:
                    errors.append(f"{staff.full_name} already has shift on {assignment['date']}")
                    continue
                
                # Create shift
                shift = Shift.objects.create(
                    user=staff,
                    unit=unit,
                    shift_type=shift_type,
                    date=assignment['date'],
                    status='SCHEDULED',
                    shift_classification='REGULAR',
                    notes=f"Auto-generated by optimizer (estimated cost: £{assignment['cost']:.2f})",
                    created_by=request.user
                )
                
                created_shifts.append(shift.id)
                logger.info(f"Created optimized shift: {shift}")
            
            except Exception as e:
                errors.append(f"Error creating shift for {assignment.get('staff_name', 'unknown')}: {str(e)}")
                logger.error(f"Shift creation error: {str(e)}", exc_info=True)
        
        return JsonResponse({
            'success': True,
            'created_count': len(created_shifts),
            'created_shift_ids': created_shifts,
            'errors': errors,
        })
    
    except Exception as e:
        logger.error(f"Apply optimization error: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_operations_or_senior_manager)
def optimization_comparison(request):
    """
    Show detailed comparison of current schedule vs optimized
    
    Visualizes:
    - Cost breakdown (permanent vs overtime vs agency)
    - Demand coverage gaps
    - Staff utilization rates
    - Fairness metrics (workload distribution)
    """
    care_home_name = request.GET.get('care_home')
    start_date_str = request.GET.get('start_date')
    
    if not care_home_name or not start_date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    care_home = CareHome.objects.filter(name=care_home_name).first()
    if not care_home:
        return JsonResponse({'error': 'Care home not found'}, status=404)
    
    start_date = date.fromisoformat(start_date_str)
    
    # Get existing shifts
    existing_shifts = Shift.objects.filter(
        unit__care_home=care_home,
        date=start_date,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).select_related('user', 'unit', 'shift_type')
    
    # Analyze current schedule
    current_analysis = {
        'total_shifts': existing_shifts.count(),
        'regular': existing_shifts.filter(shift_classification='REGULAR').count(),
        'overtime': existing_shifts.filter(shift_classification='OVERTIME').count(),
        'agency': existing_shifts.filter(shift_classification='AGENCY').count(),
        'total_cost': 0,
        'staff_count': existing_shifts.values('user').distinct().count(),
    }
    
    for shift in existing_shifts:
        if shift.shift_classification == 'AGENCY':
            hourly_rate = float(shift.agency_hourly_rate) if shift.agency_hourly_rate else 25.0
        elif shift.shift_classification == 'OVERTIME':
            hourly_rate = 18.0
        else:
            hourly_rate = 13.5
        current_analysis['total_cost'] += hourly_rate * shift.duration_hours
    
    # Get forecasts for demand comparison
    forecasts = StaffingForecast.objects.filter(
        care_home=care_home,
        forecast_date=start_date
    ).select_related('unit')
    
    demand_coverage = []
    for forecast in forecasts:
        unit_shifts = existing_shifts.filter(unit=forecast.unit).count()
        predicted = forecast.predicted_shifts
        gap = predicted - unit_shifts
        
        demand_coverage.append({
            'unit': forecast.unit.get_name_display(),
            'predicted': round(predicted, 1),
            'assigned': unit_shifts,
            'gap': round(gap, 1),
            'coverage_pct': round((unit_shifts / predicted * 100) if predicted > 0 else 100, 1),
        })
    
    context = {
        'care_home': care_home.get_name_display(),
        'date': start_date,
        'current_analysis': current_analysis,
        'demand_coverage': demand_coverage,
    }
    
    return render(request, 'scheduling/optimization_comparison.html', context)
