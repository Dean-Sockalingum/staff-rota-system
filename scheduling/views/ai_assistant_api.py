"""
AI Assistant API View
Provides web-based access to the AI help assistant with enhanced reporting capabilities
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta, date, datetime
import json
import sys
import os

# Import models for report generation
from scheduling.models import (
    User, Shift, LeaveRequest, IncidentReport, Unit, ShiftType
)
from staff_records.models import SicknessRecord, StaffProfile

# Import the HelpAssistant from the management command
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'management', 'commands'))
from help_assistant import HelpAssistant


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
    def interpret_query(query):
        """Interpret user query and determine what report to generate"""
        query_lower = query.lower()
        
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

Try asking about staffing, sickness, incidents, or shift coverage for instant reports!""",
                'related': ['Staffing Report', 'Sickness Report', 'Incident Report', 'Coverage Report'],
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
