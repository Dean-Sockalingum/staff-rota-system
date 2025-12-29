"""
AI Assistant API View
Provides web-based access to the AI help assistant with enhanced reporting capabilities
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
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

# Import the HelpAssistant from the management command
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'management', 'commands'))
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
        if any(word in query_lower for word in ['how many staff', 'total staff', 'staff count', 'staffing levels']):
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
        
        # Leave queries
        if any(word in query_lower for word in ['annual leave', 'holiday', 'vacation', 'leave requests', 'leave balance']):
            return {'type': 'leave_summary', 'data': ReportGenerator.generate_leave_summary()}
        
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
        
        # First, check if this is a report generation query
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
            answer += "\n**Executive Dashboards (NEW!):**\n"
            answer += "• 'Show executive dashboard' - Senior leadership analytics\n"
            answer += "• 'CI performance dashboard' - Care Inspectorate ratings & quality metrics\n"
            answer += "• 'What are our latest CI ratings?' - Inspection data by care home\n"
            answer += "• 'Show operational metrics' - 6-month performance trends\n"
            answer += "• 'Quality metrics for all homes' - 4-theme quality assessment\n"
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

**Executive Dashboards (NEW!):**
• "Show executive dashboard"
• "CI performance dashboard"
• "What are our latest CI ratings?"
• "Show operational metrics"
• "Quality metrics for all homes"

**ML-Powered Forecasts:**
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

Ask about executive dashboards, CI ratings, forecasts, or operational metrics!""",
                'related': ['Executive Dashboard', 'CI Performance', 'Staffing Forecast', 'Quality Metrics'],
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
