"""
Executive Summary Dashboard - Advanced analytics and forecasting
Task 46: Executive Summary Dashboard with KPI visualization, trend analysis, and forecasting
"""
from django.db.models import Count, Sum, Avg, Q, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import statistics


class ExecutiveSummaryService:
    """
    Service class for generating executive summary data with forecasting and trends
    """
    
    @staticmethod
    def get_executive_kpis(care_home=None, start_date=None, end_date=None):
        """
        Get key performance indicators for executive summary
        
        Args:
            care_home: Optional CareHome instance (None = all homes)
            start_date: Start date for period (default: 30 days ago)
            end_date: End date for period (default: today)
        
        Returns:
            dict: Executive KPIs with current period and trends
        """
        from scheduling.models import Shift, User, LeaveRequest
        from scheduling.models_multi_home import CareHome
        
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Base queryset
        shifts = Shift.objects.filter(date__range=[start_date, end_date])
        if care_home:
            shifts = shifts.filter(unit__care_home=care_home)
        
        # Total shifts
        total_shifts = shifts.count()
        
        # Staffed vs vacant
        staffed_shifts = shifts.filter(user__isnull=False).count()
        vacant_shifts = total_shifts - staffed_shifts
        fill_rate = (staffed_shifts / total_shifts * 100) if total_shifts > 0 else 0
        
        # Agency usage
        agency_shifts = shifts.filter(agency_company__isnull=False).count()
        agency_rate = (agency_shifts / total_shifts * 100) if total_shifts > 0 else 0
        
        # Staff metrics
        staff_queryset = User.objects.filter(is_active=True)
        if care_home:
            staff_queryset = staff_queryset.filter(unit__care_home=care_home)
        total_staff = staff_queryset.count()
        
        # Leave requests
        leave_requests = LeaveRequest.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        if care_home:
            leave_requests = leave_requests.filter(user__unit__care_home=care_home)
        
        pending_leave = leave_requests.filter(status='pending').count()
        approved_leave = leave_requests.filter(status='approved').count()
        
        # Budget metrics (simplified - would use actual budget system)
        regular_cost = staffed_shifts * Decimal('120')  # Average shift cost
        agency_cost = agency_shifts * Decimal('180')  # Agency premium
        total_cost = regular_cost + agency_cost
        
        # Calculate trends (compare to previous period)
        previous_start = start_date - (end_date - start_date) - timedelta(days=1)
        previous_end = start_date - timedelta(days=1)
        previous_kpis = ExecutiveSummaryService._get_period_kpis(
            care_home, previous_start, previous_end
        )
        
        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': (end_date - start_date).days + 1
            },
            'kpis': {
                'total_shifts': {
                    'value': total_shifts,
                    'trend': ExecutiveSummaryService._calculate_trend(
                        total_shifts, previous_kpis.get('total_shifts', 0)
                    )
                },
                'fill_rate': {
                    'value': round(fill_rate, 1),
                    'trend': ExecutiveSummaryService._calculate_trend(
                        fill_rate, previous_kpis.get('fill_rate', 0)
                    ),
                    'target': 95.0,
                    'status': 'success' if fill_rate >= 95 else 'warning' if fill_rate >= 90 else 'danger'
                },
                'agency_rate': {
                    'value': round(agency_rate, 1),
                    'trend': ExecutiveSummaryService._calculate_trend(
                        agency_rate, previous_kpis.get('agency_rate', 0)
                    ),
                    'target': 15.0,
                    'status': 'success' if agency_rate <= 15 else 'warning' if agency_rate <= 25 else 'danger'
                },
                'total_staff': {
                    'value': total_staff,
                    'trend': ExecutiveSummaryService._calculate_trend(
                        total_staff, previous_kpis.get('total_staff', 0)
                    )
                },
                'pending_leave': {
                    'value': pending_leave,
                    'trend': ExecutiveSummaryService._calculate_trend(
                        pending_leave, previous_kpis.get('pending_leave', 0)
                    )
                },
                'total_cost': {
                    'value': float(total_cost),
                    'trend': ExecutiveSummaryService._calculate_trend(
                        float(total_cost), previous_kpis.get('total_cost', 0)
                    ),
                    'formatted': f'£{total_cost:,.0f}'
                }
            },
            'previous_period': previous_kpis
        }
    
    @staticmethod
    def _get_period_kpis(care_home, start_date, end_date):
        """Get KPIs for a specific period (internal helper)"""
        from scheduling.models import Shift, User, LeaveRequest
        
        shifts = Shift.objects.filter(date__range=[start_date, end_date])
        if care_home:
            shifts = shifts.filter(unit__care_home=care_home)
        
        total_shifts = shifts.count()
        if total_shifts == 0:
            return {}
        
        staffed_shifts = shifts.filter(user__isnull=False).count()
        agency_shifts = shifts.filter(agency_company__isnull=False).count()
        fill_rate = (staffed_shifts / total_shifts * 100)
        agency_rate = (agency_shifts / total_shifts * 100)
        
        staff_queryset = User.objects.filter(is_active=True)
        if care_home:
            staff_queryset = staff_queryset.filter(unit__care_home=care_home)
        
        leave_requests = LeaveRequest.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
            status='pending'
        )
        if care_home:
            leave_requests = leave_requests.filter(user__unit__care_home=care_home)
        
        total_cost = staffed_shifts * Decimal('120') + agency_shifts * Decimal('180')
        
        return {
            'total_shifts': total_shifts,
            'fill_rate': fill_rate,
            'agency_rate': agency_rate,
            'total_staff': staff_queryset.count(),
            'pending_leave': leave_requests.count(),
            'total_cost': float(total_cost)
        }
    
    @staticmethod
    def _calculate_trend(current, previous):
        """Calculate trend percentage and direction"""
        if previous == 0:
            return {'change': 0, 'direction': 'neutral', 'percentage': 0}
        
        change = current - previous
        percentage = (change / previous * 100)
        
        return {
            'change': round(change, 2),
            'direction': 'up' if change > 0 else 'down' if change < 0 else 'neutral',
            'percentage': round(percentage, 1)
        }
    
    @staticmethod
    def get_trend_analysis(care_home=None, weeks=12):
        """
        Get weekly trend analysis for charts
        
        Args:
            care_home: Optional CareHome instance
            weeks: Number of weeks to analyze
        
        Returns:
            dict: Weekly trends with fill rate, agency rate, costs, day/night breakdown, and per-home data
        """
        from scheduling.models import Shift, CareHome
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(weeks=weeks)
        
        # Day shift types: DAY, EARLY, LATE, LONG_DAY
        # Night shift types: NIGHT
        
        trends = []
        current_date = start_date
        
        while current_date <= end_date:
            week_end = min(current_date + timedelta(days=6), end_date)
            
            shifts = Shift.objects.filter(
                date__range=[current_date, week_end]
            )
            if care_home:
                shifts = shifts.filter(unit__care_home=care_home)
            
            total = shifts.count()
            if total > 0:
                staffed = shifts.filter(user__isnull=False).count()
                agency = shifts.filter(agency_company__isnull=False).count()
                
                # Day shift metrics
                day_shifts = shifts.filter(shift_type__name__in=['DAY', 'EARLY', 'LATE', 'LONG_DAY'])
                day_total = day_shifts.count()
                day_staffed = day_shifts.filter(user__isnull=False).count() if day_total > 0 else 0
                day_fill_rate = round((day_staffed / day_total * 100), 1) if day_total > 0 else 0
                
                # Night shift metrics
                night_shifts = shifts.filter(shift_type__name='NIGHT')
                night_total = night_shifts.count()
                night_staffed = night_shifts.filter(user__isnull=False).count() if night_total > 0 else 0
                night_fill_rate = round((night_staffed / night_total * 100), 1) if night_total > 0 else 0
                
                # Per-home breakdown (only if not filtering by specific home)
                homes_data = []
                if not care_home:
                    for home in CareHome.objects.filter(is_active=True):
                        home_shifts = shifts.filter(unit__care_home=home)
                        home_total = home_shifts.count()
                        if home_total > 0:
                            home_staffed = home_shifts.filter(user__isnull=False).count()
                            home_day_shifts = home_shifts.filter(shift_type__name__in=['DAY', 'EARLY', 'LATE', 'LONG_DAY'])
                            home_night_shifts = home_shifts.filter(shift_type__name='NIGHT')
                            home_day_total = home_day_shifts.count()
                            home_night_total = home_night_shifts.count()
                            home_day_staffed = home_day_shifts.filter(user__isnull=False).count() if home_day_total > 0 else 0
                            home_night_staffed = home_night_shifts.filter(user__isnull=False).count() if home_night_total > 0 else 0
                            
                            homes_data.append({
                                'name': home.name,
                                'fill_rate': round((home_staffed / home_total * 100), 1),
                                'day_fill_rate': round((home_day_staffed / home_day_total * 100), 1) if home_day_total > 0 else 0,
                                'night_fill_rate': round((home_night_staffed / home_night_total * 100), 1) if home_night_total > 0 else 0,
                                'total_shifts': home_total,
                                'day_shifts': home_day_total,
                                'night_shifts': home_night_total,
                                'vacancies': home_total - home_staffed
                            })
                
                trends.append({
                    'week_start': current_date,
                    'week_end': week_end,
                    'total_shifts': total,
                    'fill_rate': round((staffed / total * 100), 1),
                    'day_fill_rate': day_fill_rate,
                    'night_fill_rate': night_fill_rate,
                    'day_shifts_total': day_total,
                    'night_shifts_total': night_total,
                    'agency_rate': round((agency / total * 100), 1),
                    'cost': float(staffed * Decimal('120') + agency * Decimal('180')),
                    'homes': homes_data
                })
            
            current_date = week_end + timedelta(days=1)
        
        return trends
    
    @staticmethod
    def generate_forecast(care_home=None, weeks_ahead=4):
        """
        Generate forecast for future weeks using simple moving average
        
        Args:
            care_home: Optional CareHome instance
            weeks_ahead: Number of weeks to forecast
        
        Returns:
            dict: Forecasted metrics
        """
        # Get historical trends
        historical = ExecutiveSummaryService.get_trend_analysis(care_home, weeks=12)
        
        if len(historical) < 4:
            return {'error': 'Insufficient historical data for forecasting'}
        
        # Calculate moving averages
        fill_rates = [week['fill_rate'] for week in historical[-8:]]
        agency_rates = [week['agency_rate'] for week in historical[-8:]]
        costs = [week['cost'] for week in historical[-8:]]
        
        avg_fill_rate = statistics.mean(fill_rates)
        avg_agency_rate = statistics.mean(agency_rates)
        avg_cost = statistics.mean(costs)
        
        # Calculate trend (linear regression simplified)
        fill_rate_trend = (fill_rates[-1] - fill_rates[0]) / len(fill_rates)
        agency_rate_trend = (agency_rates[-1] - agency_rates[0]) / len(agency_rates)
        cost_trend = (costs[-1] - costs[0]) / len(costs)
        
        # Generate forecasts
        forecasts = []
        last_date = historical[-1]['week_end']
        
        for i in range(weeks_ahead):
            week_start = last_date + timedelta(days=1 + (i * 7))
            week_end = week_start + timedelta(days=6)
            
            # Apply trend
            forecasted_fill = avg_fill_rate + (fill_rate_trend * (i + 1))
            forecasted_agency = avg_agency_rate + (agency_rate_trend * (i + 1))
            forecasted_cost = avg_cost + (cost_trend * (i + 1))
            
            # Clamp values to realistic ranges
            forecasted_fill = max(0, min(100, forecasted_fill))
            forecasted_agency = max(0, min(100, forecasted_agency))
            forecasted_cost = max(0, forecasted_cost)
            
            forecasts.append({
                'week_start': week_start,
                'week_end': week_end,
                'fill_rate': round(forecasted_fill, 1),
                'agency_rate': round(forecasted_agency, 1),
                'cost': round(forecasted_cost, 0),
                'confidence': max(0, 100 - (i * 15))  # Decreasing confidence
            })
        
        return {
            'forecasts': forecasts,
            'method': 'Moving Average with Linear Trend',
            'historical_weeks': len(historical),
            'forecast_weeks': weeks_ahead
        }
    
    @staticmethod
    def get_comparative_analysis(start_date=None, end_date=None):
        """
        Compare performance across all care homes
        
        Returns:
            list: Performance metrics for each home
        """
        from scheduling.models import CareHome
        
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        homes = CareHome.objects.filter(is_active=True)
        comparison = []
        
        for home in homes:
            kpis = ExecutiveSummaryService.get_executive_kpis(home, start_date, end_date)
            
            comparison.append({
                'home': home,
                'home_name': home.name,
                'kpis': kpis['kpis'],
                'rank_fill_rate': 0,  # Will be calculated after
                'rank_agency_rate': 0,
                'rank_cost': 0
            })
        
        # Rank homes
        comparison.sort(key=lambda x: x['kpis']['fill_rate']['value'], reverse=True)
        for i, item in enumerate(comparison):
            item['rank_fill_rate'] = i + 1
        
        comparison.sort(key=lambda x: x['kpis']['agency_rate']['value'])
        for i, item in enumerate(comparison):
            item['rank_agency_rate'] = i + 1
        
        comparison.sort(key=lambda x: x['kpis']['total_cost']['value'])
        for i, item in enumerate(comparison):
            item['rank_cost'] = i + 1
        
        # Calculate overall rank (average of ranks)
        for item in comparison:
            avg_rank = (
                item['rank_fill_rate'] +
                item['rank_agency_rate'] +
                item['rank_cost']
            ) / 3
            item['overall_rank'] = round(avg_rank, 1)
        
        # Sort by overall rank
        comparison.sort(key=lambda x: x['overall_rank'])
        
        return comparison
    
    @staticmethod
    def get_executive_insights(care_home=None):
        """
        Generate AI-powered insights and recommendations
        
        Returns:
            list: Insights with priority and actionable recommendations
        """
        kpis = ExecutiveSummaryService.get_executive_kpis(care_home)
        insights = []
        
        # Fill rate insight
        fill_rate = kpis['kpis']['fill_rate']
        if fill_rate['value'] < 90:
            insights.append({
                'type': 'critical',
                'icon': '🚨',
                'title': 'Low Fill Rate Detected',
                'message': f"Fill rate at {fill_rate['value']}% is below target (95%)",
                'recommendation': 'Increase recruitment efforts and review shift patterns',
                'priority': 1
            })
        elif fill_rate['value'] >= 98:
            insights.append({
                'type': 'success',
                'icon': '✅',
                'title': 'Excellent Staffing Coverage',
                'message': f"Fill rate at {fill_rate['value']}% exceeds target",
                'recommendation': 'Maintain current staffing strategies',
                'priority': 3
            })
        
        # Agency usage insight
        agency_rate = kpis['kpis']['agency_rate']
        if agency_rate['value'] > 25:
            insights.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': 'High Agency Dependency',
                'message': f"Agency usage at {agency_rate['value']}% is above target (15%)",
                'recommendation': 'Review permanent staff capacity and consider additional hires',
                'priority': 1
            })
        
        # Cost trend insight
        cost_trend = kpis['kpis']['total_cost']['trend']
        if cost_trend['direction'] == 'up' and cost_trend['percentage'] > 10:
            insights.append({
                'type': 'warning',
                'icon': '💰',
                'title': 'Rising Costs Detected',
                'message': f"Costs increased by {cost_trend['percentage']}% from previous period",
                'recommendation': 'Analyze cost drivers and optimize shift allocation',
                'priority': 2
            })
        
        # Pending leave insight
        pending_leave = kpis['kpis']['pending_leave']['value']
        if pending_leave > 10:
            insights.append({
                'type': 'info',
                'icon': '📋',
                'title': 'Pending Leave Requests',
                'message': f"{pending_leave} leave requests awaiting approval",
                'recommendation': 'Review and action pending leave requests promptly',
                'priority': 2
            })
        
        # Sort by priority
        insights.sort(key=lambda x: x['priority'])
        
        return insights
