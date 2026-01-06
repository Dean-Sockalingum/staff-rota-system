"""
AI Assistant API View
Provides web-based access to the AI help assistant with enhanced reporting capabilities
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .decorators_api import api_login_required
from django.utils import timezone
from datetime import timedelta, date, datetime
import json
import sys
import os

# Import models for report generation
from scheduling.models import (
    User, Shift, LeaveRequest, IncidentReport, Unit, ShiftType, StaffingForecast
)
from scheduling.models_multi_home import CareHome
from staff_records.models import SicknessRecord, StaffProfile

# Import proactive suggestions engine
from scheduling.utils_proactive_suggestions import get_proactive_suggestions, get_high_priority_suggestions

# Import leave predictor
from scheduling.utils_leave_predictor import (
    predict_leave_approval_likelihood,
    find_better_leave_dates,
    get_optimal_leave_period
)

# Import the HelpAssistant from the management command
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'management', 'commands'))
from help_assistant import HelpAssistant


@login_required
def ai_assistant_page(request):
    """
    Main landing page for the AI Assistant interface.
    Displays the chat interface and quick access to AI features.
    """
    context = {
        'page_title': 'AI Help Assistant',
        'user': request.user,
    }
    return render(request, 'scheduling/ai_assistant_page.html', context)


def extract_dates_from_query(query):
    """
    Extract dates from natural language query.
    Supports formats like:
    - "Dec 25 to Dec 27"
    - "from 2025-01-10 to 2025-01-15"
    - "January 10-15"
    - "next week", "next Monday"
    """
    import re
    from dateutil import parser
    from datetime import timedelta
    
    today = timezone.now().date()
    dates = []
    
    # Try explicit date ranges
    date_range_patterns = [
        r'(?:from |)(\d{4}-\d{2}-\d{2}).*?(?:to |until |-).*?(\d{4}-\d{2}-\d{2})',
        r'(?:from |)([A-Za-z]+\s+\d{1,2}).*?(?:to |until |-).*?([A-Za-z]+\s+\d{1,2})',
        r'(\d{1,2}\s+[A-Za-z]+).*?(?:to |until |-).*?(\d{1,2}\s+[A-Za-z]+)',
    ]
    
    for pattern in date_range_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            try:
                start = parser.parse(match.group(1), default=today.replace(day=1))
                end = parser.parse(match.group(2), default=today.replace(day=1))
                
                # If parsed year is in the past, assume next year
                if start.date() < today:
                    start = start.replace(year=today.year + 1)
                if end.date() < today:
                    end = end.replace(year=today.year + 1)
                
                return [start.date(), end.date()]
            except:
                continue
    
    # Try relative dates
    if 'next week' in query.lower():
        # Next Monday to Friday
        days_ahead = (7 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_monday = today + timedelta(days=days_ahead)
        next_friday = next_monday + timedelta(days=4)
        return [next_monday, next_friday]
    
    if 'this week' in query.lower():
        # This Monday to Friday
        days_back = today.weekday()
        this_monday = today - timedelta(days=days_back)
        this_friday = this_monday + timedelta(days=4)
        if this_friday < today:
            # Week already passed, assume next week
            this_monday += timedelta(days=7)
            this_friday += timedelta(days=7)
        return [this_monday, this_friday]
    
    # Try single date mentions and assume 5-day duration
    single_date_patterns = [
        r'on ([A-Za-z]+\s+\d{1,2})',
        r'(\d{4}-\d{2}-\d{2})',
    ]
    
    for pattern in single_date_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            try:
                start = parser.parse(match.group(1), default=today.replace(day=1))
                if start.date() < today:
                    start = start.replace(year=today.year + 1)
                # Assume 5-day leave
                end = start + timedelta(days=4)
                return [start.date(), end.date()]
            except:
                continue
    
    return []


def format_leave_prediction_response(prediction, start_date, end_date, user):
    """Format the prediction result as a user-friendly response"""
    
    duration = (end_date - start_date).days + 1
    
    # Header with emoji based on likelihood
    if prediction['likelihood_score'] >= 85:
        emoji = "✅"
        status_text = "EXCELLENT"
    elif prediction['likelihood_score'] >= 60:
        emoji = "⚠️"
        status_text = "GOOD"
    elif prediction['likelihood_score'] >= 40:
        emoji = "⚠️"
        status_text = "MODERATE"
    else:
        emoji = "❌"
        status_text = "LOW"
    
    answer = f"{emoji} **Leave Approval Prediction**\n\n"
    answer += f"**Requested:** {start_date.strftime('%A, %B %d')} - {end_date.strftime('%A, %B %d, %Y')}\n"
    answer += f"**Duration:** {duration} days\n\n"
    answer += f"**Approval Likelihood:** {prediction['likelihood_score']}% ({status_text})\n\n"
    
    # Add factors
    if prediction['factors']:
        answer += "**Analysis:**\n"
        for factor in prediction['factors']:
            answer += f"{factor}\n"
        answer += "\n"
    
    # Add recommendations
    if prediction['recommendations']:
        answer += "**Recommendations:**\n"
        for rec in prediction['recommendations']:
            answer += f"{rec}\n"
        answer += "\n"
    
    # Add alternative dates if provided
    if prediction.get('alternative_dates') and len(prediction['alternative_dates']) > 0:
        answer += "**Better Alternative Dates:**\n"
        for alt in prediction['alternative_dates']:
            answer += f"• {alt['description']}\n"
        answer += "\n"
    
    # Add action guidance
    if prediction['can_proceed']:
        if prediction['likelihood_score'] >= 85:
            answer += "✅ **You can proceed with confidence!** Click the button below to submit your request."
        elif prediction['likelihood_score'] >= 60:
            answer += "⚠️ **Proceed with caution.** Your request will likely need manager review but has a good chance of approval."
        else:
            answer += "⚠️ **Consider alternative dates.** While you can still request these dates, approval is uncertain."
    else:
        answer += "❌ **Cannot proceed.** Please resolve the issues mentioned above before submitting a request."
    
    return answer


class ReportGenerator:
    """Generate and interpret various reports using AI"""
    
    @staticmethod
    def generate_staffing_summary():
        """Generate current staffing summary"""
        total_staff = User.objects.filter(is_staff=False, is_active=True).count()
        staff_by_role = {}
        
        for user in User.objects.filter(is_staff=False, is_active=True).select_related('role'):
            role_name = user.role.get_name_display() if user.role else 'No Role'
            staff_by_role[role_name] = staff_by_role.get(role_name, 0) + 1
        
        return {
            'total': total_staff,
            'by_role': staff_by_role,
            'summary': f"You currently have {total_staff} active staff members across {len(staff_by_role)} different roles."
        }
    
    @staticmethod
    def generate_sickness_report(days=7):
        """Generate sickness absence report"""
        today = timezone.now().date()
        start_date = today - timedelta(days=days)
        
        # Get active sickness records
        active_sickness = SicknessRecord.objects.filter(
            status__in=['OPEN', 'AWAITING_FIT_NOTE']
        ).select_related('profile__user')
        
        # Get recent sickness
        recent_sickness = SicknessRecord.objects.filter(
            first_working_day__gte=start_date
        ).select_related('profile__user')
        
        active_list = [
            {
                'name': record.profile.user.full_name,
                'sap': record.profile.user.sap,
                'days': record.total_working_days_sick,
                'status': record.get_status_display()
            }
            for record in active_sickness
        ]
        
        return {
            'currently_off_sick': active_sickness.count(),
            'recent_count': recent_sickness.count(),
            'active_cases': active_list,
            'summary': f"Currently {active_sickness.count()} staff off sick. {recent_sickness.count()} new sickness records in the last {days} days."
        }
    
    @staticmethod
    def generate_incident_report(days=7):
        """Generate incident summary report"""
        start_date = timezone.now() - timedelta(days=days)
        
        incidents = IncidentReport.objects.filter(
            created_at__gte=start_date
        ).select_related('reported_by')
        
        severity_counts = {}
        type_counts = {}
        ci_notifications = 0
        
        for incident in incidents:
            # Count by severity
            severity_counts[incident.severity] = severity_counts.get(incident.severity, 0) + 1
            
            # Count by type
            type_display = incident.get_incident_type_display()
            type_counts[type_display] = type_counts.get(type_display, 0) + 1
            
            # Check CI notification
            if incident.requires_care_inspectorate_notification():
                ci_notifications += 1
        
        critical_alert = ""
        if severity_counts.get('DEATH', 0) > 0:
            critical_alert = f"⚠️ CRITICAL: {severity_counts['DEATH']} death(s) reported. "
        elif severity_counts.get('MAJOR_HARM', 0) > 0:
            critical_alert = f"⚠️ WARNING: {severity_counts['MAJOR_HARM']} major harm incident(s). "
        
        return {
            'total_incidents': incidents.count(),
            'by_severity': severity_counts,
            'by_type': type_counts,
            'ci_notifications_required': ci_notifications,
            'summary': f"{critical_alert}{incidents.count()} total incidents in the last {days} days. {ci_notifications} require Care Inspectorate notification."
        }
    
    @staticmethod
    def generate_shift_coverage_report(date_str=None):
        """Generate shift coverage report for a specific date"""
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except:
                target_date = timezone.now().date()
        else:
            target_date = timezone.now().date()
        
        shifts = Shift.objects.filter(date=target_date).select_related('user', 'shift_type', 'unit')
        
        coverage_by_unit = {}
        coverage_by_shift = {}
        
        for shift in shifts:
            unit_name = shift.unit.get_name_display() if shift.unit else 'Unknown'
            shift_name = shift.shift_type.get_name_display() if shift.shift_type else 'Unknown'
            
            if unit_name not in coverage_by_unit:
                coverage_by_unit[unit_name] = {'day': 0, 'night': 0}
            
            if 'Night' in shift_name:
                coverage_by_unit[unit_name]['night'] += 1
            else:
                coverage_by_unit[unit_name]['day'] += 1
            
            coverage_by_shift[shift_name] = coverage_by_shift.get(shift_name, 0) + 1
        
        return {
            'date': target_date.isoformat(),
            'total_shifts': shifts.count(),
            'by_unit': coverage_by_unit,
            'by_shift_type': coverage_by_shift,
            'summary': f"On {target_date.strftime('%A, %d %B %Y')}: {shifts.count()} shifts scheduled across {len(coverage_by_unit)} units."
        }
    
    @staticmethod
    def generate_leave_summary():
        """Generate annual leave summary"""
        pending = LeaveRequest.objects.filter(status='PENDING').count()
        approved_future = LeaveRequest.objects.filter(
            status='APPROVED',
            start_date__gte=timezone.now().date()
        ).count()
        
        # Get staff with low leave balances (less than 40 hours)
        low_balance_staff = []
        try:
            from staff_records.models import AnnualLeaveEntitlement
            for ent in AnnualLeaveEntitlement.objects.select_related('profile__user'):
                if ent.hours_remaining < 40 and ent.hours_remaining > 0:
                    low_balance_staff.append({
                        'name': ent.profile.user.full_name,
                        'hours_remaining': float(ent.hours_remaining)
                    })
        except:
            pass
        
        return {
            'pending_requests': pending,
            'approved_future_leave': approved_future,
            'low_balance_count': len(low_balance_staff),
            'low_balance_staff': low_balance_staff[:5],
            'summary': f"{pending} pending leave requests. {approved_future} approved future leave bookings. {len(low_balance_staff)} staff with low leave balance."
        }
    
    @staticmethod
    def generate_staffing_forecast(days_ahead=7, care_home_name=None, unit_name=None):
        """Generate ML-based staffing forecast using Prophet predictions"""
        today = timezone.now().date()
        end_date = today + timedelta(days=days_ahead)
        
        # Build queryset
        forecasts_qs = StaffingForecast.objects.filter(
            forecast_date__gte=today,
            forecast_date__lte=end_date
        ).select_related('care_home', 'unit').order_by('forecast_date')
        
        # Apply filters
        if care_home_name:
            forecasts_qs = forecasts_qs.filter(care_home__name__icontains=care_home_name)
        
        if unit_name:
            forecasts_qs = forecasts_qs.filter(unit__name__icontains=unit_name)
        
        forecasts = list(forecasts_qs)
        
        if not forecasts:
            return {
                'summary': 'No forecast data available. Run `python3 manage.py train_prophet_models` to generate forecasts.',
                'forecasts': [],
                'high_risk_days': [],
                'avg_predicted': 0
            }
        
        # Extract forecast details
        forecast_list = []
        high_risk_days = []
        total_predicted = 0
        
        for f in forecasts:
            uncertainty_pct = (
                (float(f.confidence_upper) - float(f.confidence_lower)) / float(f.predicted_shifts)
            ) if f.predicted_shifts > 0 else 0
            
            forecast_item = {
                'date': f.forecast_date.strftime('%Y-%m-%d'),
                'care_home': f.care_home.name,
                'unit': f.unit.get_name_display(),
                'predicted_shifts': float(f.predicted_shifts),
                'ci_lower': float(f.confidence_lower),
                'ci_upper': float(f.confidence_upper),
                'uncertainty_pct': round(uncertainty_pct * 100, 1),
                'is_high_risk': uncertainty_pct > 0.5
            }
            
            forecast_list.append(forecast_item)
            total_predicted += float(f.predicted_shifts)
            
            if uncertainty_pct > 0.5:
                high_risk_days.append({
                    'date': f.forecast_date.strftime('%A, %d %b'),
                    'unit': f.unit.get_name_display(),
                    'predicted': round(float(f.predicted_shifts), 1),
                    'range': f"{round(float(f.confidence_lower), 1)}-{round(float(f.confidence_upper), 1)}"
                })
        
        avg_predicted = total_predicted / len(forecasts) if forecasts else 0
        
        return {
            'summary': f"📊 ML Forecast for next {days_ahead} days: Avg {avg_predicted:.1f} shifts/day. {len(high_risk_days)} high-uncertainty days detected.",
            'forecasts': forecast_list,
            'high_risk_days': high_risk_days,
            'avg_predicted': round(avg_predicted, 1),
            'days_ahead': days_ahead
        }
    
    @staticmethod
    def check_staffing_shortage(target_date=None, care_home_name=None):
        """Check if forecasted demand exceeds available staff"""
        if target_date is None:
            target_date = timezone.now().date()
        elif isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # Get forecasts for target date
        forecasts_qs = StaffingForecast.objects.filter(
            forecast_date=target_date
        ).select_related('care_home', 'unit')
        
        if care_home_name:
            forecasts_qs = forecasts_qs.filter(care_home__name__icontains=care_home_name)
        
        forecasts = list(forecasts_qs)
        
        if not forecasts:
            return {
                'summary': f'No ML forecast available for {target_date}. Run forecasting model first.',
                'shortages': [],
                'total_shortage': 0
            }
        
        # Get actual scheduled shifts for comparison
        scheduled_count = Shift.objects.filter(
            date=target_date,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).count()
        
        shortages = []
        total_predicted = 0
        
        for f in forecasts:
            # Get unit-specific scheduled shifts
            unit_shifts = Shift.objects.filter(
                date=target_date,
                unit=f.unit,
                status__in=['SCHEDULED', 'CONFIRMED']
            ).count()
            
            predicted = float(f.predicted_shifts)
            total_predicted += predicted
            
            # Check if shortage (use upper CI for conservative planning)
            if unit_shifts < f.confidence_upper:
                shortage = float(f.confidence_upper) - unit_shifts
                shortages.append({
                    'unit': f.unit.get_name_display(),
                    'care_home': f.care_home.name,
                    'scheduled': unit_shifts,
                    'predicted_upper': round(float(f.confidence_upper), 1),
                    'shortage': round(shortage, 1)
                })
        
        total_shortage = sum(s['shortage'] for s in shortages)
        
        if shortages:
            summary = f"⚠️ ML Prediction: Potential shortage on {target_date.strftime('%A, %d %b')} - {total_shortage:.1f} shifts short across {len(shortages)} units."
        else:
            summary = f"✅ ML Prediction: Staffing adequate for {target_date.strftime('%A, %d %b')} - {scheduled_count} scheduled vs {total_predicted:.1f} predicted."
        
        return {
            'summary': summary,
            'shortages': shortages,
            'total_shortage': round(total_shortage, 1),
            'scheduled_count': scheduled_count,
            'predicted_total': round(total_predicted, 1)
        }
    
    @staticmethod
    def interpret_query(query):
        """Interpret user query and determine what report to generate"""
        query_lower = query.lower()
        
        # ML Forecasting queries (NEW)
        if any(word in query_lower for word in ['forecast', 'predict', 'prediction', 'next week', 'upcoming demand']):
            days = 7
            if 'tomorrow' in query_lower:
                days = 1
            elif 'week' in query_lower or '7 day' in query_lower:
                days = 7
            elif 'month' in query_lower or '30 day' in query_lower:
                days = 30
            return {'type': 'ml_forecast', 'data': ReportGenerator.generate_staffing_forecast(days)}
        
        # Staffing shortage queries (NEW - ML-powered)
        if any(word in query_lower for word in ['shortage', 'short-staffed', 'short staffed', 'understaffed', 'need more staff']):
            date_str = None
            if 'tomorrow' in query_lower:
                date_str = (timezone.now().date() + timedelta(days=1)).isoformat()
            elif 'monday' in query_lower or 'tuesday' in query_lower or 'wednesday' in query_lower:
                # Simple day detection (could be enhanced)
                date_str = None
            return {'type': 'ml_shortage', 'data': ReportGenerator.check_staffing_shortage(date_str)}
        
        # Staffing queries
        if any(word in query_lower for word in ['how many staff', 'total staff', 'staff count', 'staffing levels', 
                                                  'how many active', 'how many are active', 'active staff',
                                                  'staff in hawthorn', 'staff in orchard', 'staff in meadowburn',
                                                  'staff in riverside', 'staff in victoria']):
            return {'type': 'staffing_summary', 'data': ReportGenerator.generate_staffing_summary()}
        
        # Sickness queries
        if any(word in query_lower for word in ['sickness', 'sick', 'absence', 'off sick', 'who is sick']):
            days = 7
            if 'today' in query_lower:
                days = 0
            elif 'week' in query_lower or '7 day' in query_lower:
                days = 7
            elif 'month' in query_lower or '30 day' in query_lower:
                days = 30
            return {'type': 'sickness_report', 'data': ReportGenerator.generate_sickness_report(days)}
        
        # Incident queries
        if any(word in query_lower for word in ['incident', 'accidents', 'falls', 'injury', 'injuries']):
            days = 7
            if 'today' in query_lower or 'last 24 hours' in query_lower:
                days = 1
            elif 'week' in query_lower:
                days = 7
            elif 'month' in query_lower:
                days = 30
            return {'type': 'incident_report', 'data': ReportGenerator.generate_incident_report(days)}
        
        # Shift coverage queries
        if any(word in query_lower for word in ['coverage', 'shifts today', 'who is working', 'rota today', 'schedule today']):
            # Extract date if specified
            date_str = None
            if 'tomorrow' in query_lower:
                date_str = (timezone.now().date() + timedelta(days=1)).isoformat()
            elif 'today' in query_lower or 'now' in query_lower:
                date_str = timezone.now().date().isoformat()
            return {'type': 'shift_coverage', 'data': ReportGenerator.generate_shift_coverage_report(date_str)}
        
        # Leave queries - DISABLED: Now handled by _process_leave_balance_query which is more specific
        # This generic handler was catching staff-specific leave queries before they could be processed properly
        # if any(word in query_lower for word in ['annual leave', 'holiday', 'vacation', 'leave requests', 'leave balance']):
        #     return {'type': 'leave_summary', 'data': ReportGenerator.generate_leave_summary()}
        
        # Weekly report queries
        if any(word in query_lower for word in ['weekly report', 'weekend report', 'weekly summary']):
            return {
                'type': 'weekly_report',
                'data': {
                    'summary': 'To generate the weekly report, run: `python3 manage.py generate_weekly_report --save`',
                    'info': 'The weekly report covers Friday-Sunday events including sickness, overtime, agency usage, and incidents.'
                }
            }
        
        return None


@api_login_required
@require_http_methods(["POST"])
def ai_assistant_api(request):
    """
    Enhanced AI assistant API with report generation and interpretation
    
    Expects JSON POST data:
    {
        "query": "user's question"
    }
    
    Returns:
    {
        "answer": "assistant's response",
        "related": ["topic1", "topic2"],
        "category": "category_name",
        "report_data": {...}  // Optional: structured report data
    }
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({
                'error': 'No query provided'
            }, status=400)
        
        # Initialize the assistant
        assistant = HelpAssistant()
        
        # First, check if this is a leave availability query
        import re
        leave_patterns = [
            r'can i (take|request|get|have) (leave|holiday|vacation|time off)',
            r'(leave|holiday) (availability|approval|chances)',
            r'what are my chances.*(leave|holiday|vacation)',
            r'when (can|should) i (take|request|book) (leave|holiday)',
            r'(is|are) (these |those )?dates?.*(available|good|likely)',
            r'leave (on|from|for|between)',
            r'check.*(leave|holiday|vacation)',
            r'best time.*(leave|holiday|vacation)',
            r'predict.*(leave|approval)',
        ]
        
        leave_query_match = any(re.search(pattern, query.lower()) for pattern in leave_patterns)
        
        if leave_query_match:
            # Extract dates from query
            dates_extracted = extract_dates_from_query(query)
            
            if dates_extracted and len(dates_extracted) >= 2:
                start_date, end_date = dates_extracted[0], dates_extracted[1]
                
                # Get prediction
                prediction = predict_leave_approval_likelihood(request.user, start_date, end_date)
                
                # Format response
                answer = format_leave_prediction_response(prediction, start_date, end_date, request.user)
                
                return JsonResponse({
                    'answer': answer,
                    'related': ['Request Leave', 'View Leave Balance', 'Leave Calendar'],
                    'category': 'leave_prediction',
                    'prediction_data': prediction,
                    'action_button': {
                        'text': '📝 Submit Leave Request',
                        'url': f'/request-leave/?start={start_date.isoformat()}&end={end_date.isoformat()}',
                        'visible': prediction['can_proceed']
                    }
                })
            
            elif 'best time' in query.lower() or 'when should' in query.lower():
                # Find optimal dates
                month_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)', query.lower())
                month = None
                if month_match:
                    months = ['january', 'february', 'march', 'april', 'may', 'june', 
                             'july', 'august', 'september', 'october', 'november', 'december']
                    month = months.index(month_match.group(1).lower()) + 1
                
                # Extract duration
                duration_match = re.search(r'(\d+)\s*(day|week)', query.lower())
                duration_days = 5  # default
                if duration_match:
                    num = int(duration_match.group(1))
                    if 'week' in duration_match.group(2):
                        duration_days = num * 7
                    else:
                        duration_days = num
                
                optimal = get_optimal_leave_period(request.user, month, duration_days)
                
                if optimal:
                    # Format month name for display
                    month_name = optimal['start_date'].strftime('%B')
                    
                    if optimal['available']:
                        # Less than 3 staff off - dates available
                        answer = f"**✅ Great News! Leave Available in {month_name}**\n\n"
                        answer += f"**Best dates:** {optimal['start_date'].strftime('%A, %B %d')} - {optimal['end_date'].strftime('%A, %B %d, %Y')}\n\n"
                        
                        if optimal['staff_off'] == 0:
                            answer += f"**Availability:** Excellent! No staff currently off during this period. ✅\n\n"
                        elif optimal['staff_off'] == 1:
                            answer += f"**Availability:** Very Good - Only 1 staff member off during this period. ✅\n\n"
                        else:
                            answer += f"**Availability:** Good - {optimal['staff_off']} staff members off during this period. ✅\n\n"
                        
                        answer += f"**Approval likelihood:** {optimal['score']}%\n\n"
                        
                        if optimal['available_periods'] > 1:
                            answer += f"💡 **Note:** Found {optimal['available_periods']} available periods in {month_name}. This is the best option.\n\n"
                        
                        answer += "Would you like to submit a leave request for these dates?"
                        
                        return JsonResponse({
                            'answer': answer,
                            'related': ['Request Leave', 'Check Other Dates', 'View Leave Balance'],
                            'category': 'leave_optimization',
                            'action_button': {
                                'text': '📝 Request These Dates',
                                'url': f'/request-leave/?start={optimal["start_date"].isoformat()}&end={optimal["end_date"].isoformat()}'
                            }
                        })
                    else:
                        # 3 or more staff off - busy period
                        answer = f"**⚠️ {month_name} is Quite Busy**\n\n"
                        answer += f"**Least busy dates:** {optimal['start_date'].strftime('%A, %B %d')} - {optimal['end_date'].strftime('%A, %B %d, %Y')}\n\n"
                        answer += f"**Staff already off:** {optimal['staff_off']} people during this period\n\n"
                        answer += f"**Approval likelihood:** {optimal['score']}% (Lower due to high demand)\n\n"
                        
                        if optimal['available_periods'] == 0:
                            answer += f"⚠️ **All periods in {month_name} have 3+ staff off.** This is the quietest option available.\n\n"
                        else:
                            answer += f"💡 **Recommendation:** Consider these dates or check {optimal['available_periods']} quieter periods in other months.\n\n"
                        
                        answer += "You can still request these dates, but approval may be subject to operational needs."
                        
                        return JsonResponse({
                            'answer': answer,
                            'related': ['Check Other Months', 'View Leave Calendar', 'Request Anyway'],
                            'category': 'leave_optimization',
                            'action_button': {
                                'text': '📝 Request Despite Busy Period',
                                'url': f'/request-leave/?start={optimal["start_date"].isoformat()}&end={optimal["end_date"].isoformat()}'
                            }
                        })
                else:
                    answer = "I couldn't find any future dates in the specified month. Please specify:\n"
                    answer += "• A future month (e.g., 'January', 'next month', 'March')\n"
                    answer += "• How many days? (e.g., '5 days', '1 week')\n\n"
                    answer += "Example: 'When is the best time for 5 days leave in March?'"
                    
                    return JsonResponse({
                        'answer': answer,
                        'related': ['Leave Calendar', 'Check Specific Dates'],
                        'category': 'leave_help'
                    })
            
            else:
                # No dates specified - provide guidance
                answer = "I can help you check leave availability! 📅\n\n"
                answer += "**Examples:**\n"
                answer += "• 'Can I take leave from Dec 25 to Dec 27?'\n"
                answer += "• 'Are dates Jan 10-15 good for holiday?'\n"
                answer += "• 'When is the best time for leave in March?'\n"
                answer += "• 'What are my chances for next week?'\n\n"
                answer += "I'll analyze staffing levels, your leave balance, and coverage to predict approval likelihood!"
                
                return JsonResponse({
                    'answer': answer,
                    'related': ['Leave Balance', 'Team Calendar'],
                    'category': 'leave_help'
                })
        
        # Second, check if this is a report generation query
        report_result = ReportGenerator.interpret_query(query)
        
        if report_result:
            # Generate formatted answer from report data
            report_type = report_result['type']
            report_data = report_result['data']
            
            answer = f"**{report_type.replace('_', ' ').title()}**\n\n"
            answer += report_data.get('summary', '')
            
            # Add detailed breakdown based on report type
            if report_type == 'staffing_summary':
                answer += "\n\n**Breakdown by Role:**\n"
                for role, count in report_data['by_role'].items():
                    answer += f"• {role}: {count}\n"
            
            elif report_type == 'ml_forecast':
                if report_data['high_risk_days']:
                    answer += "\n\n**⚠️ High-Uncertainty Days:**\n"
                    for day in report_data['high_risk_days'][:5]:
                        answer += f"• {day['date']} - {day['unit']}: {day['predicted']} shifts (range: {day['range']})\n"
                
                if report_data['forecasts']:
                    answer += f"\n\n**Next {min(3, len(report_data['forecasts']))} Days:**\n"
                    for fc in report_data['forecasts'][:3]:
                        risk_flag = "⚠️" if fc['is_high_risk'] else "✅"
                        answer += f"{risk_flag} {fc['date']}: {fc['predicted_shifts']:.1f} shifts ({fc['ci_lower']:.1f}-{fc['ci_upper']:.1f})\n"
            
            elif report_type == 'ml_shortage':
                if report_data['shortages']:
                    answer += "\n\n**⚠️ Predicted Shortages:**\n"
                    for s in report_data['shortages']:
                        answer += f"• {s['unit']}: {s['scheduled']} scheduled vs {s['predicted_upper']} needed (short {s['shortage']} shifts)\n"
                    answer += f"\n**Action Required:** Consider agency staff or overtime for {report_data['total_shortage']} shifts."
            
            elif report_type == 'sickness_report':
                for role, count in report_data['by_role'].items():
                    answer += f"• {role}: {count}\n"
            
            elif report_type == 'sickness_report':
                if report_data['active_cases']:
                    answer += "\n\n**Currently Off Sick:**\n"
                    for case in report_data['active_cases']:
                        answer += f"• {case['name']} ({case['sap']}) - {case['days']} days - {case['status']}\n"
            
            elif report_type == 'incident_report':
                if report_data['by_severity']:
                    answer += "\n\n**By Severity:**\n"
                    severity_labels = {
                        'DEATH': '☠️ Death',
                        'MAJOR_HARM': '🔴 Major Harm',
                        'MODERATE_HARM': '🟠 Moderate Harm',
                        'LOW_HARM': '🟡 Low Harm',
                        'NO_HARM': '🟢 No Harm'
                    }
                    for severity, count in report_data['by_severity'].items():
                        label = severity_labels.get(severity, severity)
                        answer += f"• {label}: {count}\n"
                
                if report_data['ci_notifications_required'] > 0:
                    answer += f"\n⚠️ **{report_data['ci_notifications_required']} incidents require Care Inspectorate notification**\n"
            
            elif report_type == 'shift_coverage':
                answer += "\n\n**Coverage by Unit:**\n"
                for unit, coverage in report_data['by_unit'].items():
                    answer += f"• {unit}: Day {coverage['day']} | Night {coverage['night']}\n"
            
            elif report_type == 'leave_summary':
                if report_data['low_balance_staff']:
                    answer += "\n\n**Staff with Low Leave Balance (<40 hours):**\n"
                    for staff in report_data['low_balance_staff']:
                        answer += f"• {staff['name']}: {staff['hours_remaining']:.1f} hours remaining\n"
            
            return JsonResponse({
                'answer': answer,
                'related': ['View Dashboard', 'Generate Report', 'Export Data'],
                'category': 'report',
                'report_data': report_data,
                'report_type': report_type
            })
        
        # Special handling for "show all topics"
        if 'show all topics' in query.lower() or 'list topics' in query.lower():
            topics_list = []
            for category, items in assistant.knowledge_base.items():
                category_name = category.replace('_', ' ').title()
                for key, data_item in items.items():
                    title = data_item.get('question', [''])[0].title()
                    topics_list.append(f"• {title}")
            
            answer = "**Available Help Topics:**\n\n" + "\n".join(topics_list[:20])
            if len(topics_list) > 20:
                answer += f"\n\n...and {len(topics_list) - 20} more topics!"
            
            answer += "\n\n**Quick Reports:**\n"
            answer += "• 'How many staff do we have?'\n"
            answer += "• 'Who is off sick today?'\n"
            answer += "• 'Show me recent incidents'\n"
            answer += "• 'What's the shift coverage today?'\n"
            answer += "• 'Show leave requests'\n"
            answer += "\n**Advanced Reports & Analytics:**\n"
            answer += "• 'Show OT and Agency usage' - Detailed breakdown by home and grade\n"
            answer += "• 'Show staff vacancies' - Current and upcoming leavers by home\n"
            answer += "• 'Generate annual leave report'\n"
            answer += "• 'Show leave usage targets by home'\n"
            answer += "• 'Daily additional staffing report'\n"
            answer += "• 'Weekly additional staffing analysis'\n"
            answer += "• 'Compliance and audit reports'\n"
            answer += "\n**ML-Powered Forecasts:**\n"
            answer += "• 'What's the staffing forecast for next week?'\n"
            answer += "• 'Will we be short-staffed tomorrow?'\n"
            answer += "• 'Predict staffing demand for next month'\n"
            
            return JsonResponse({
                'answer': answer,
                'related': [],
                'category': 'topics'
            })
        
        # Find the answer from knowledge base
        result = assistant.find_answer(query)
        
        if result:
            return JsonResponse({
                'answer': result['answer'],
                'related': result.get('related', []),
                'category': result.get('category', '')
            })
        else:
            # No exact match found - provide helpful suggestions
            return JsonResponse({
                'answer': """I'm not sure about that specific question. Here are some things I can help with:

**Quick Reports:**
• "How many staff do we have?"
• "Who is off sick today?"
• "Show me incidents this week"
• "What's the coverage today?"
• "Show leave requests"

**ML-Powered Forecasts (NEW!):**
• "What's the staffing forecast for next week?"
• "Will we be short-staffed tomorrow?"
• "Predict demand for next 30 days"
• "Are we understaffed on Monday?"

**Commands:**
• How to add staff
• How to generate rotas
• How to start the server
• How to manage annual leave

**Locations:**
• Where is the admin panel?
• Where is the documentation?

**Troubleshooting:**
• Database locked errors
• Import errors
• Permission denied errors

Ask about forecasts, shortages, sickness, or incidents for instant ML-powered insights!""",
                'related': ['Staffing Forecast', 'Shortage Prediction', 'Sickness Report', 'Coverage Report'],
                'category': 'help'
            })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def proactive_suggestions_api(request):
    """
    API endpoint for proactive AI suggestions
    Returns intelligent, contextual suggestions for managers
    """
    try:
        # Get optional parameters
        care_home_id = request.GET.get('care_home')
        priority_filter = request.GET.get('priority')  # high, medium, low
        category_filter = request.GET.get('category')  # staffing, leave, compliance, etc.
        days_ahead = int(request.GET.get('days_ahead', 14))
        
        # Get care home if specified
        care_home = None
        if care_home_id:
            try:
                care_home = CareHome.objects.get(id=care_home_id)
            except CareHome.DoesNotExist:
                pass
        
        # Get all suggestions
        suggestions = get_proactive_suggestions(care_home=care_home, days_ahead=days_ahead)
        
        # Apply filters
        if priority_filter:
            suggestions = [s for s in suggestions if s['priority'] == priority_filter]
        
        if category_filter:
            suggestions = [s for s in suggestions if s['category'] == category_filter]
        
        # Calculate summary statistics
        summary = {
            'total_count': len(suggestions),
            'high_priority': len([s for s in suggestions if s['priority'] == 'high']),
            'medium_priority': len([s for s in suggestions if s['priority'] == 'medium']),
            'low_priority': len([s for s in suggestions if s['priority'] == 'low']),
            'by_category': {}
        }
        
        for suggestion in suggestions:
            category = suggestion['category']
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions,
            'summary': summary
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error generating suggestions: {str(e)}'
        }, status=500)
