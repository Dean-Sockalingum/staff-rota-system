"""
Cost Analytics Service

Analyzes staffing costs, compares agency vs permanent expenses,
tracks overtime costs, and provides budget forecasting.
"""

from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import statistics


# Default hourly rates (can be customized per care home)
DEFAULT_PERMANENT_RATE = Decimal('15.00')  # £15/hour
DEFAULT_AGENCY_RATE = Decimal('25.00')     # £25/hour
DEFAULT_OVERTIME_MULTIPLIER = Decimal('1.5')  # 1.5x for overtime


def calculate_shift_cost(shift, hourly_rate=None):
    """
    Calculate cost for a single shift
    
    Returns: Decimal cost
    """
    # Default shift duration: 8 hours
    shift_hours = Decimal('8.0')
    
    # Get hourly rate
    if not hourly_rate:
        if hasattr(shift, 'is_agency') and shift.is_agency:
            hourly_rate = DEFAULT_AGENCY_RATE
        else:
            hourly_rate = DEFAULT_PERMANENT_RATE
    
    # Calculate base cost
    cost = hourly_rate * shift_hours
    
    # Apply overtime multiplier if applicable
    if hasattr(shift, 'is_overtime') and shift.is_overtime:
        cost = cost * DEFAULT_OVERTIME_MULTIPLIER
    
    return cost


def analyze_costs(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Analyze staffing costs for a given period
    
    Returns: Dictionary with cost analysis results
    """
    from .models import Shift
    
    # Default to last 30 days
    if not end_date:
        end_date = timezone.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Filter shifts
    shifts = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        shifts = shifts.filter(care_home=care_home)
    if unit:
        shifts = shifts.filter(unit=unit)
    
    # Initialize cost tracking
    total_cost = Decimal('0.00')
    permanent_cost = Decimal('0.00')
    agency_cost = Decimal('0.00')
    overtime_cost = Decimal('0.00')
    
    permanent_shifts = 0
    agency_shifts = 0
    overtime_shifts = 0
    
    # Daily cost breakdown
    daily_costs = {}
    
    for shift in shifts:
        # Determine shift type
        is_agency = getattr(shift, 'is_agency', False)
        is_overtime = getattr(shift, 'is_overtime', False)
        
        # Calculate shift cost
        if is_agency:
            cost = calculate_shift_cost(shift, DEFAULT_AGENCY_RATE)
            agency_cost += cost
            agency_shifts += 1
        else:
            cost = calculate_shift_cost(shift, DEFAULT_PERMANENT_RATE)
            permanent_cost += cost
            permanent_shifts += 1
        
        if is_overtime:
            # Additional overtime premium
            overtime_premium = cost * (DEFAULT_OVERTIME_MULTIPLIER - 1)
            overtime_cost += overtime_premium
            overtime_shifts += 1
        
        total_cost += cost
        
        # Track daily costs
        date_str = shift.date.strftime('%Y-%m-%d')
        if date_str not in daily_costs:
            daily_costs[date_str] = Decimal('0.00')
        daily_costs[date_str] += cost
    
    total_shifts = shifts.count()
    
    # Calculate metrics
    cost_per_shift = (total_cost / total_shifts) if total_shifts > 0 else Decimal('0.00')
    permanent_cost_per_shift = (permanent_cost / permanent_shifts) if permanent_shifts > 0 else Decimal('0.00')
    agency_cost_per_shift = (agency_cost / agency_shifts) if agency_shifts > 0 else Decimal('0.00')
    
    agency_percentage = (agency_shifts / total_shifts * 100) if total_shifts > 0 else Decimal('0.00')
    
    # Calculate cost efficiency score
    # Lower agency usage and overtime = higher efficiency
    agency_penalty = agency_percentage * Decimal('0.5')  # 0-50 points
    overtime_penalty = (overtime_shifts / total_shifts * 100 * Decimal('0.3')) if total_shifts > 0 else Decimal('0.00')  # 0-30 points
    cost_efficiency_score = max(Decimal('0.00'), Decimal('100.00') - agency_penalty - overtime_penalty)
    
    # Identify potential savings
    if agency_shifts > 0:
        # Calculate savings if agency shifts were permanent
        agency_as_permanent_cost = agency_shifts * calculate_shift_cost(shifts.first(), DEFAULT_PERMANENT_RATE)
        potential_savings = agency_cost - agency_as_permanent_cost
    else:
        potential_savings = Decimal('0.00')
    
    # Generate savings recommendations
    recommendations = []
    if agency_percentage > 30:
        recommendations.append(f"Agency usage is {agency_percentage:.1f}% - consider recruiting permanent staff")
        recommendations.append(f"Potential monthly savings: £{potential_savings:,.2f}")
    if overtime_shifts > total_shifts * 0.2:
        recommendations.append(f"Overtime shifts account for {overtime_shifts/total_shifts*100:.1f}% - review staffing levels")
    if cost_per_shift > 150:
        recommendations.append(f"Average cost per shift (£{cost_per_shift:.2f}) is high - optimize scheduling")
    
    if not recommendations:
        recommendations.append("Cost structure appears efficient - maintain current approach")
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'total_cost': total_cost,
        'permanent_staff_cost': permanent_cost,
        'agency_staff_cost': agency_cost,
        'overtime_cost': overtime_cost,
        'total_shifts': total_shifts,
        'permanent_shifts': permanent_shifts,
        'agency_shifts': agency_shifts,
        'overtime_shifts': overtime_shifts,
        'cost_per_shift': cost_per_shift,
        'permanent_cost_per_shift': permanent_cost_per_shift,
        'agency_cost_per_shift': agency_cost_per_shift,
        'agency_percentage': agency_percentage,
        'cost_efficiency_score': cost_efficiency_score,
        'cost_breakdown_data': daily_costs,
        'cost_by_category': {
            'Permanent': float(permanent_cost),
            'Agency': float(agency_cost),
            'Overtime Premium': float(overtime_cost),
        },
        'potential_savings': potential_savings,
        'savings_recommendations': '\n'.join(recommendations),
    }


def compare_agency_vs_permanent(care_home=None, unit=None, start_date=None, end_date=None):
    """
    Compare agency vs permanent staff costs
    
    Returns: Dictionary with comparison results
    """
    from .models import Shift
    
    # Default to last 30 days
    if not end_date:
        end_date = timezone.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Filter shifts
    shifts = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        shifts = shifts.filter(care_home=care_home)
    if unit:
        shifts = shifts.filter(unit=unit)
    
    # Separate agency and permanent shifts
    agency_shifts_qs = shifts.filter(is_agency=True)
    permanent_shifts_qs = shifts.exclude(is_agency=True)
    
    # Count shifts
    agency_shift_count = agency_shifts_qs.count()
    permanent_shift_count = permanent_shifts_qs.count()
    
    # Calculate costs
    agency_total_cost = agency_shift_count * calculate_shift_cost(None, DEFAULT_AGENCY_RATE)
    permanent_total_cost = permanent_shift_count * calculate_shift_cost(None, DEFAULT_PERMANENT_RATE)
    
    # Cost per shift
    agency_cost_per_shift = agency_total_cost / agency_shift_count if agency_shift_count > 0 else Decimal('0.00')
    permanent_cost_per_shift = permanent_total_cost / permanent_shift_count if permanent_shift_count > 0 else Decimal('0.00')
    
    # Hourly rates
    agency_hourly_rate = DEFAULT_AGENCY_RATE
    permanent_hourly_rate = DEFAULT_PERMANENT_RATE
    
    # Calculate differences
    cost_difference = agency_total_cost - permanent_total_cost
    total_cost = agency_total_cost + permanent_total_cost
    cost_difference_percentage = (cost_difference / total_cost * 100) if total_cost > 0 else Decimal('0.00')
    
    # Agency premium
    agency_premium = ((agency_hourly_rate - permanent_hourly_rate) / permanent_hourly_rate * 100)
    total_premium_paid = agency_total_cost - (agency_shift_count * calculate_shift_cost(None, DEFAULT_PERMANENT_RATE))
    
    # Potential savings
    if_all_permanent_cost = (agency_shift_count + permanent_shift_count) * calculate_shift_cost(None, DEFAULT_PERMANENT_RATE)
    actual_total = agency_total_cost + permanent_total_cost
    potential_monthly_savings = actual_total - if_all_permanent_cost
    
    # Generate recommendation
    if agency_shift_count > permanent_shift_count:
        priority = 'HIGH'
        recommendation = f"Agency usage is very high ({agency_shift_count} vs {permanent_shift_count} permanent). "
        recommendation += f"Recruiting {agency_shift_count // 2} permanent staff could save £{potential_monthly_savings/2:,.2f} per month."
    elif agency_premium > 50 and agency_shift_count > 10:
        priority = 'MEDIUM'
        recommendation = f"Agency premium is {agency_premium:.1f}%. Consider targeted permanent recruitment to reduce costs."
    else:
        priority = 'LOW'
        recommendation = "Agency usage is at acceptable levels. Continue monitoring."
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'agency_total_cost': agency_total_cost,
        'agency_shift_count': agency_shift_count,
        'agency_cost_per_shift': agency_cost_per_shift,
        'agency_hourly_rate': agency_hourly_rate,
        'permanent_total_cost': permanent_total_cost,
        'permanent_shift_count': permanent_shift_count,
        'permanent_cost_per_shift': permanent_cost_per_shift,
        'permanent_hourly_rate': permanent_hourly_rate,
        'cost_difference': cost_difference,
        'cost_difference_percentage': cost_difference_percentage,
        'agency_premium': agency_premium,
        'total_premium_paid': total_premium_paid,
        'if_all_permanent_cost': if_all_permanent_cost,
        'potential_monthly_savings': potential_monthly_savings,
        'recommendation': recommendation,
        'priority': priority,
    }


def forecast_budget(care_home=None, unit=None, historical_months=3, forecast_months=3, method='LINEAR'):
    """
    Forecast budget for upcoming months based on historical data
    
    Returns: Dictionary with forecast results
    """
    from .models import Shift
    
    # Calculate historical period
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=historical_months * 30)
    
    # Get historical shifts
    shifts = Shift.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    if care_home:
        shifts = shifts.filter(care_home=care_home)
    if unit:
        shifts = shifts.filter(unit=unit)
    
    # Calculate historical costs by month
    monthly_costs = {}
    for shift in shifts:
        month_key = shift.date.strftime('%Y-%m')
        cost = calculate_shift_cost(shift)
        
        if month_key not in monthly_costs:
            monthly_costs[month_key] = Decimal('0.00')
        monthly_costs[month_key] += cost
    
    if not monthly_costs:
        return {'error': 'No historical data available for forecasting'}
    
    # Historical metrics
    historical_total_cost = sum(monthly_costs.values())
    historical_average_monthly = historical_total_cost / len(monthly_costs) if monthly_costs else Decimal('0.00')
    
    # Forecast based on method
    if method == 'LINEAR':
        # Calculate trend
        values = list(monthly_costs.values())
        if len(values) > 1:
            # Simple linear trend
            x = list(range(len(values)))
            mean_x = statistics.mean(x)
            mean_y = statistics.mean([float(v) for v in values])
            
            numerator = sum((x[i] - mean_x) * (float(values[i]) - mean_y) for i in range(len(x)))
            denominator = sum((x[i] - mean_x) ** 2 for i in range(len(x)))
            
            slope = Decimal(str(numerator / denominator)) if denominator != 0 else Decimal('0.00')
            intercept = Decimal(str(mean_y)) - slope * Decimal(str(mean_x))
        else:
            slope = Decimal('0.00')
            intercept = historical_average_monthly
        
        # Forecast future months
        monthly_forecast = {}
        forecasted_total = Decimal('0.00')
        
        for i in range(forecast_months):
            future_month = end_date + timedelta(days=(i + 1) * 30)
            month_key = future_month.strftime('%Y-%m')
            
            forecast_value = intercept + slope * (len(values) + i)
            forecast_value = max(Decimal('0.00'), forecast_value)  # Ensure non-negative
            
            monthly_forecast[month_key] = float(forecast_value)
            forecasted_total += forecast_value
        
        forecasted_monthly_average = forecasted_total / forecast_months if forecast_months > 0 else Decimal('0.00')
        
        # Determine trend direction
        if slope > historical_average_monthly * Decimal('0.05'):
            trend_direction = 'INCREASING'
            trend_percentage = (slope / historical_average_monthly * 100) if historical_average_monthly > 0 else Decimal('0.00')
        elif slope < -historical_average_monthly * Decimal('0.05'):
            trend_direction = 'DECREASING'
            trend_percentage = (slope / historical_average_monthly * 100) if historical_average_monthly > 0 else Decimal('0.00')
        else:
            trend_direction = 'STABLE'
            trend_percentage = Decimal('0.00')
        
    else:  # AVERAGE method
        # Use historical average
        monthly_forecast = {}
        for i in range(forecast_months):
            future_month = end_date + timedelta(days=(i + 1) * 30)
            month_key = future_month.strftime('%Y-%m')
            monthly_forecast[month_key] = float(historical_average_monthly)
        
        forecasted_total = historical_average_monthly * forecast_months
        forecasted_monthly_average = historical_average_monthly
        trend_direction = 'STABLE'
        trend_percentage = Decimal('0.00')
    
    # Calculate confidence level
    if len(monthly_costs) >= 3:
        confidence_level = Decimal('80.00')
        margin_of_error = Decimal('15.00')
    elif len(monthly_costs) >= 2:
        confidence_level = Decimal('60.00')
        margin_of_error = Decimal('25.00')
    else:
        confidence_level = Decimal('40.00')
        margin_of_error = Decimal('35.00')
    
    # Generate recommendations
    recommendations = []
    risk_level = 'LOW'
    
    if trend_direction == 'INCREASING':
        recommendations.append(f"Costs are trending upward by {trend_percentage:.1f}%")
        recommendations.append("Review staffing efficiency and agency usage")
        risk_level = 'MEDIUM'
    elif trend_direction == 'DECREASING':
        recommendations.append(f"Costs are trending downward by {abs(trend_percentage):.1f}%")
        recommendations.append("Continue current cost management approach")
        risk_level = 'LOW'
    else:
        recommendations.append("Costs are stable - maintain current practices")
        risk_level = 'LOW'
    
    if forecasted_monthly_average > historical_average_monthly * Decimal('1.1'):
        recommendations.append(f"Forecast exceeds historical average by {((forecasted_monthly_average/historical_average_monthly - 1) * 100):.1f}%")
        risk_level = 'HIGH'
    
    return {
        'historical_start_date': start_date,
        'historical_end_date': end_date,
        'forecast_start_date': end_date + timedelta(days=1),
        'forecast_end_date': end_date + timedelta(days=forecast_months * 30),
        'forecast_months': forecast_months,
        'forecast_method': method,
        'historical_total_cost': historical_total_cost,
        'historical_average_monthly': historical_average_monthly,
        'forecasted_total_cost': forecasted_total,
        'forecasted_monthly_average': forecasted_monthly_average,
        'monthly_forecast': monthly_forecast,
        'confidence_level': confidence_level,
        'margin_of_error': margin_of_error,
        'trend_direction': trend_direction,
        'trend_percentage': trend_percentage,
        'recommendations': '\n'.join(recommendations),
        'risk_level': risk_level,
    }


def identify_cost_optimization_opportunities(care_home=None, unit=None):
    """
    Identify opportunities to optimize staffing costs
    
    Returns: List of optimization recommendation dictionaries
    """
    recommendations = []
    
    # Run cost analysis
    cost_analysis = analyze_costs(care_home, unit)
    
    # Check agency usage
    if cost_analysis['agency_percentage'] > 30:
        recommendations.append({
            'category': 'AGENCY_REDUCTION',
            'priority': 'HIGH',
            'title': 'Reduce agency staff dependency',
            'description': f"Agency staff account for {cost_analysis['agency_percentage']:.1f}% of shifts",
            'potential_savings': cost_analysis['potential_savings'],
            'action': 'Recruit permanent staff to fill regular shifts',
        })
    
    # Check overtime usage
    overtime_pct = (cost_analysis['overtime_shifts'] / cost_analysis['total_shifts'] * 100) if cost_analysis['total_shifts'] > 0 else 0
    if overtime_pct > 15:
        recommendations.append({
            'category': 'OVERTIME_REDUCTION',
            'priority': 'MEDIUM',
            'title': 'Reduce overtime dependency',
            'description': f"Overtime shifts account for {overtime_pct:.1f}% of total",
            'potential_savings': cost_analysis['overtime_cost'] * Decimal('0.5'),  # Estimate 50% reduction
            'action': 'Hire additional staff or improve scheduling efficiency',
        })
    
    # Check cost per shift
    if cost_analysis['cost_per_shift'] > 150:
        recommendations.append({
            'category': 'EFFICIENCY',
            'priority': 'MEDIUM',
            'title': 'Optimize shift costs',
            'description': f"Average cost per shift (£{cost_analysis['cost_per_shift']:.2f}) is above target",
            'potential_savings': (cost_analysis['cost_per_shift'] - Decimal('120.00')) * cost_analysis['total_shifts'],
            'action': 'Review shift allocation and staffing mix',
        })
    
    # Run agency comparison
    comparison = compare_agency_vs_permanent(care_home, unit)
    if comparison['potential_monthly_savings'] > 1000:
        recommendations.append({
            'category': 'AGENCY_TO_PERMANENT',
            'priority': 'HIGH',
            'title': 'Convert agency to permanent positions',
            'description': f"Agency premium is {comparison['agency_premium']:.1f}%",
            'potential_savings': comparison['potential_monthly_savings'],
            'action': f"Recruit permanent staff - potential monthly savings: £{comparison['potential_monthly_savings']:,.2f}",
        })
    
    # Sort by potential savings (descending)
    recommendations.sort(key=lambda x: x['potential_savings'], reverse=True)
    
    return recommendations
