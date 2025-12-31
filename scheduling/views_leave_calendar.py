"""
Leave Calendar Views - Task 59
Provides calendar-based visualization of leave requests for planning
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count
from datetime import datetime, timedelta
from scheduling.models import LeaveRequest, CareHome, Unit
from scheduling.permissions import has_care_home_access


@login_required
def leave_calendar_view(request):
    """
    Calendar view showing leave requests for current user
    """
    user_care_homes = request.user.care_home_access.all()
    
    context = {
        'page_title': 'My Leave Calendar',
        'care_homes': user_care_homes,
        'view_type': 'personal'
    }
    
    return render(request, 'scheduling/leave_calendar.html', context)


@login_required
def team_leave_calendar_view(request):
    """
    Calendar view showing all team leave (for managers)
    Requires FULL or READ_ONLY access
    """
    # Get user's care homes and permission level
    user_care_homes = request.user.care_home_access.all()
    permission_level = request.user.staff_profile.permission_level if hasattr(request.user, 'staff_profile') else 'NONE'
    
    if permission_level not in ['FULL', 'READ_ONLY']:
        # Redirect regular staff to personal calendar
        return leave_calendar_view(request)
    
    # Get all units across user's care homes
    units = Unit.objects.filter(care_home__in=user_care_homes).order_by('care_home__name', 'name')
    
    context = {
        'page_title': 'Team Leave Calendar',
        'care_homes': user_care_homes,
        'units': units,
        'permission_level': permission_level,
        'view_type': 'team'
    }
    
    return render(request, 'scheduling/leave_calendar.html', context)


@login_required
def leave_calendar_data_api(request):
    """
    JSON API endpoint for FullCalendar to fetch leave events
    
    Query params:
    - start: ISO date string (calendar visible start)
    - end: ISO date string (calendar visible end)
    - care_home_id: Optional filter by care home
    - unit_id: Optional filter by unit
    - view_type: 'personal' or 'team'
    """
    try:
        # Parse date range from FullCalendar
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')
        
        if not start_str or not end_str:
            return JsonResponse({'error': 'Missing start or end date'}, status=400)
        
        start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00')).date()
        end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00')).date()
        
        # Get filters
        view_type = request.GET.get('view_type', 'personal')
        care_home_id = request.GET.get('care_home_id')
        unit_id = request.GET.get('unit_id')
        
        # Base query - leave requests overlapping with calendar range
        leave_requests = LeaveRequest.objects.filter(
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
        ).select_related('user', 'user__staff_profile', 'approved_by')
        
        # Filter by view type
        if view_type == 'personal':
            # Show only current user's leave
            leave_requests = leave_requests.filter(user=request.user)
        else:
            # Team view - filter by care home access
            user_care_homes = request.user.care_home_access.all()
            leave_requests = leave_requests.filter(
                user__care_home_access__in=user_care_homes
            ).distinct()
            
            # Apply care home filter if specified
            if care_home_id:
                leave_requests = leave_requests.filter(user__care_home_access__id=care_home_id)
            
            # Apply unit filter if specified
            if unit_id:
                leave_requests = leave_requests.filter(user__staff_profile__unit__id=unit_id)
        
        # Convert to FullCalendar event format
        events = []
        for leave in leave_requests:
            # Determine event color based on status and type
            color = get_leave_color(leave.status, leave.leave_type)
            
            # Build event title
            if view_type == 'team':
                title = f"{leave.user.full_name} - {leave.get_leave_type_display()}"
            else:
                title = leave.get_leave_type_display()
            
            # Add status indicator for pending/review
            if leave.status in ['PENDING', 'MANUAL_REVIEW']:
                title = f"⏳ {title}"
            elif leave.status == 'APPROVED':
                title = f"✓ {title}"
            elif leave.status == 'DENIED':
                title = f"✗ {title}"
            
            event = {
                'id': leave.id,
                'title': title,
                'start': leave.start_date.isoformat(),
                'end': (leave.end_date + timedelta(days=1)).isoformat(),  # FullCalendar end is exclusive
                'backgroundColor': color['background'],
                'borderColor': color['border'],
                'textColor': color['text'],
                'allDay': True,
                'extendedProps': {
                    'status': leave.status,
                    'leaveType': leave.leave_type,
                    'daysRequested': leave.days_requested,
                    'userName': leave.user.full_name,
                    'userSap': leave.user.staff_profile.sap_number if hasattr(leave.user, 'staff_profile') else '',
                    'reason': leave.reason or '',
                    'isBlackout': leave.is_blackout_period,
                    'staffingRisk': leave.causes_staffing_shortfall,
                    'automated': leave.automated_decision,
                    'approvedBy': leave.approved_by.full_name if leave.approved_by else None,
                    'approvalDate': leave.approval_date.isoformat() if leave.approval_date else None,
                }
            }
            
            events.append(event)
        
        return JsonResponse(events, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_leave_color(status, leave_type):
    """
    Return color scheme based on leave status and type
    """
    # Status-based colors (takes priority)
    if status == 'APPROVED':
        if leave_type == 'ANNUAL':
            return {
                'background': '#28a745',  # Green
                'border': '#1e7e34',
                'text': '#ffffff'
            }
        elif leave_type == 'SICK':
            return {
                'background': '#fd7e14',  # Orange
                'border': '#dc6502',
                'text': '#ffffff'
            }
        elif leave_type == 'TRAINING':
            return {
                'background': '#007bff',  # Blue
                'border': '#0056b3',
                'text': '#ffffff'
            }
        else:
            return {
                'background': '#6c757d',  # Gray
                'border': '#545b62',
                'text': '#ffffff'
            }
    
    elif status == 'PENDING':
        return {
            'background': '#ffc107',  # Yellow
            'border': '#d39e00',
            'text': '#212529'
        }
    
    elif status == 'MANUAL_REVIEW':
        return {
            'background': '#ff9800',  # Amber
            'border': '#cc7a00',
            'text': '#ffffff'
        }
    
    elif status == 'DENIED':
        return {
            'background': '#dc3545',  # Red
            'border': '#bd2130',
            'text': '#ffffff'
        }
    
    elif status == 'CANCELLED':
        return {
            'background': '#6c757d',  # Gray
            'border': '#545b62',
            'text': '#ffffff'
        }
    
    # Default
    return {
        'background': '#17a2b8',  # Teal
        'border': '#117a8b',
        'text': '#ffffff'
    }


@login_required
def leave_coverage_report_api(request):
    """
    JSON API for coverage analysis on specific dates
    Returns staff availability counts by unit for date range
    """
    try:
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')
        care_home_id = request.GET.get('care_home_id')
        
        if not start_str or not end_str:
            return JsonResponse({'error': 'Missing start or end date'}, status=400)
        
        start_date = datetime.fromisoformat(start_str).date()
        end_date = datetime.fromisoformat(end_str).date()
        
        # Get all units
        units = Unit.objects.filter(care_home__id=care_home_id) if care_home_id else Unit.objects.all()
        
        coverage_data = []
        current_date = start_date
        
        while current_date <= end_date:
            date_coverage = {
                'date': current_date.isoformat(),
                'units': []
            }
            
            for unit in units:
                # Count total staff in unit
                total_staff = unit.staff_set.filter(is_active=True).count()
                
                # Count staff on leave this date
                on_leave = LeaveRequest.objects.filter(
                    user__staff_profile__unit=unit,
                    status='APPROVED',
                    start_date__lte=current_date,
                    end_date__gte=current_date
                ).count()
                
                available = total_staff - on_leave
                coverage_pct = (available / total_staff * 100) if total_staff > 0 else 100
                
                unit_data = {
                    'unit_name': unit.name,
                    'total_staff': total_staff,
                    'on_leave': on_leave,
                    'available': available,
                    'coverage_pct': round(coverage_pct, 1),
                    'is_low_coverage': coverage_pct < 75  # Flag if below 75%
                }
                
                date_coverage['units'].append(unit_data)
            
            coverage_data.append(date_coverage)
            current_date += timedelta(days=1)
        
        return JsonResponse(coverage_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
