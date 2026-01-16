"""
Calendar sync service for Task 23
Generates iCal (.ics) files for shift schedules
"""

from django.conf import settings
from django.utils import timezone
from icalendar import Calendar, Event, vText
from datetime import datetime, timedelta
import hashlib
import logging

logger = logging.getLogger(__name__)


def generate_shift_ical(shifts, calendar_name="My Shifts"):
    """
    Generate iCal file for shifts
    
    Args:
        shifts: QuerySet or list of Shift objects
        calendar_name: Name for the calendar
    
    Returns:
        str: iCal formatted string
    """
    cal = Calendar()
    cal.add('prodid', '-//Staff Rota System//Shift Schedule//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', calendar_name)
    cal.add('x-wr-timezone', 'Europe/London')
    cal.add('x-wr-caldesc', 'Staff shift schedule from Staff Rota System')
    
    for shift in shifts:
        event = Event()
        
        # Unique ID for the event
        uid = f"shift-{shift.id}@staffrota.system"
        event.add('uid', uid)
        
        # Shift summary (title)
        summary = f"{shift.shift_type.name if shift.shift_type else 'Shift'} - {shift.unit.name if shift.unit else ''}"
        event.add('summary', summary)
        
        # Location
        location = f"{shift.care_home.name if shift.care_home else ''}, {shift.unit.name if shift.unit else ''}"
        event.add('location', vText(location))
        
        # Start and end times
        start_datetime = datetime.combine(shift.date, shift.start_time)
        end_datetime = datetime.combine(shift.date, shift.end_time)
        
        # Handle overnight shifts
        if shift.end_time < shift.start_time:
            end_datetime += timedelta(days=1)
        
        # Make timezone-aware
        tz = timezone.get_current_timezone()
        start_datetime = tz.localize(start_datetime)
        end_datetime = tz.localize(end_datetime)
        
        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)
        
        # Description with shift details
        description = f"""Shift Details:
Type: {shift.shift_type.name if shift.shift_type else 'N/A'}
Unit: {shift.unit.name if shift.unit else 'N/A'}
Care Home: {shift.care_home.name if shift.care_home else 'N/A'}
Time: {shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M')}

View full details: {settings.SITE_URL}/scheduling/my-schedule/
"""
        event.add('description', vText(description))
        
        # Timestamps
        event.add('dtstamp', timezone.now())
        event.add('created', shift.created_at if hasattr(shift, 'created_at') else timezone.now())
        event.add('last-modified', shift.updated_at if hasattr(shift, 'updated_at') else timezone.now())
        
        # Status
        event.add('status', 'CONFIRMED')
        
        # Categories
        event.add('categories', [shift.shift_type.name if shift.shift_type else 'Shift'])
        
        # Color coding (shift type)
        if shift.shift_type:
            if 'day' in shift.shift_type.name.lower():
                event.add('color', 'blue')
            elif 'night' in shift.shift_type.name.lower():
                event.add('color', 'purple')
            elif 'late' in shift.shift_type.name.lower():
                event.add('color', 'orange')
        
        # Add reminder (1 day before shift)
        from icalendar import Alarm
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f'Reminder: {summary}')
        alarm.add('trigger', timedelta(hours=-24))
        event.add_component(alarm)
        
        cal.add_component(event)
    
    return cal.to_ical().decode('utf-8')


def generate_personal_calendar_token(user):
    """
    Generate a secure token for personal calendar subscriptions
    
    Args:
        user: User object
    
    Returns:
        str: Secure token for calendar feed
    """
    # Create unique token based on user SAP and secret
    secret = settings.SECRET_KEY
    raw_token = f"{user.sap}-{secret}-calendar"
    token = hashlib.sha256(raw_token.encode()).hexdigest()[:32]
    return token


def verify_calendar_token(sap, token):
    """
    Verify calendar subscription token
    
    Args:
        sap: User SAP number
        token: Token to verify
    
    Returns:
        bool: True if token is valid
    """
    from scheduling.models import User
    
    try:
        user = User.objects.get(sap=sap)
        expected_token = generate_personal_calendar_token(user)
        return token == expected_token
    except User.DoesNotExist:
        return False


def generate_leave_ical(leave_requests, calendar_name="My Leave"):
    """
    Generate iCal file for leave requests
    
    Args:
        leave_requests: QuerySet of LeaveRequest objects
        calendar_name: Name for the calendar
    
    Returns:
        str: iCal formatted string
    """
    cal = Calendar()
    cal.add('prodid', '-//Staff Rota System//Leave Calendar//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', calendar_name)
    cal.add('x-wr-timezone', 'Europe/London')
    
    for leave in leave_requests:
        if leave.status != 'APPROVED':
            continue
        
        event = Event()
        
        # Unique ID
        uid = f"leave-{leave.id}@staffrota.system"
        event.add('uid', uid)
        
        # Summary
        summary = f"{leave.leave_type} Leave"
        event.add('summary', summary)
        
        # All-day event
        event.add('dtstart', leave.start_date)
        event.add('dtend', leave.end_date + timedelta(days=1))  # iCal end is exclusive
        
        # Description
        description = f"""Leave Request:
Type: {leave.leave_type}
Duration: {leave.total_days} day{'s' if leave.total_days != 1 else ''}
Status: {leave.status}

{leave.notes if leave.notes else ''}
"""
        event.add('description', vText(description))
        
        # Timestamps
        event.add('dtstamp', timezone.now())
        event.add('created', leave.created_at if hasattr(leave, 'created_at') else timezone.now())
        
        # Status
        event.add('status', 'CONFIRMED')
        event.add('transp', 'TRANSPARENT')  # Show as free time
        
        # Categories
        event.add('categories', [leave.leave_type])
        
        cal.add_component(event)
    
    return cal.to_ical().decode('utf-8')


def create_single_shift_event(shift):
    """
    Create a single iCal event for a shift (for "Add to Calendar" button)
    
    Args:
        shift: Shift object
    
    Returns:
        str: iCal formatted string for single event
    """
    cal = Calendar()
    cal.add('prodid', '-//Staff Rota System//Shift//EN')
    cal.add('version', '2.0')
    cal.add('method', 'REQUEST')
    
    event = Event()
    
    uid = f"shift-{shift.id}@staffrota.system"
    event.add('uid', uid)
    
    summary = f"{shift.shift_type.name if shift.shift_type else 'Shift'} at {shift.care_home.name if shift.care_home else ''}"
    event.add('summary', summary)
    
    location = f"{shift.care_home.name if shift.care_home else ''}, {shift.unit.name if shift.unit else ''}"
    event.add('location', vText(location))
    
    # Times
    start_datetime = datetime.combine(shift.date, shift.start_time)
    end_datetime = datetime.combine(shift.date, shift.end_time)
    
    if shift.end_time < shift.start_time:
        end_datetime += timedelta(days=1)
    
    tz = timezone.get_current_timezone()
    start_datetime = tz.localize(start_datetime)
    end_datetime = tz.localize(end_datetime)
    
    event.add('dtstart', start_datetime)
    event.add('dtend', end_datetime)
    
    description = f"""Shift at {shift.care_home.name if shift.care_home else ''}
Unit: {shift.unit.name if shift.unit else ''}
Time: {shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M')}
"""
    event.add('description', vText(description))
    
    event.add('dtstamp', timezone.now())
    event.add('status', 'CONFIRMED')
    
    # Reminder
    from icalendar import Alarm
    alarm = Alarm()
    alarm.add('action', 'DISPLAY')
    alarm.add('description', f'Shift reminder: {summary}')
    alarm.add('trigger', timedelta(hours=-24))
    event.add_component(alarm)
    
    cal.add_component(event)
    
    return cal.to_ical().decode('utf-8')


def generate_google_calendar_url(shift):
    """
    Generate Google Calendar "Add Event" URL
    
    Args:
        shift: Shift object
    
    Returns:
        str: Google Calendar URL
    """
    from urllib.parse import urlencode
    
    # Format times
    start_datetime = datetime.combine(shift.date, shift.start_time)
    end_datetime = datetime.combine(shift.date, shift.end_time)
    
    if shift.end_time < shift.start_time:
        end_datetime += timedelta(days=1)
    
    # Google Calendar format: YYYYMMDDTHHMMSS
    start_str = start_datetime.strftime('%Y%m%dT%H%M%S')
    end_str = end_datetime.strftime('%Y%m%dT%H%M%S')
    
    params = {
        'action': 'TEMPLATE',
        'text': f"{shift.shift_type.name if shift.shift_type else 'Shift'} - {shift.unit.name if shift.unit else ''}",
        'dates': f"{start_str}/{end_str}",
        'details': f"Shift at {shift.care_home.name if shift.care_home else ''}\nUnit: {shift.unit.name if shift.unit else ''}",
        'location': f"{shift.care_home.name if shift.care_home else ''}, {shift.unit.name if shift.unit else ''}",
    }
    
    return f"https://calendar.google.com/calendar/render?{urlencode(params)}"


def generate_outlook_calendar_url(shift):
    """
    Generate Outlook.com "Add Event" URL
    
    Args:
        shift: Shift object
    
    Returns:
        str: Outlook calendar URL
    """
    from urllib.parse import urlencode
    
    start_datetime = datetime.combine(shift.date, shift.start_time)
    end_datetime = datetime.combine(shift.date, shift.end_time)
    
    if shift.end_time < shift.start_time:
        end_datetime += timedelta(days=1)
    
    # ISO 8601 format
    start_str = start_datetime.isoformat()
    end_str = end_datetime.isoformat()
    
    params = {
        'path': '/calendar/action/compose',
        'rru': 'addevent',
        'subject': f"{shift.shift_type.name if shift.shift_type else 'Shift'} - {shift.unit.name if shift.unit else ''}",
        'startdt': start_str,
        'enddt': end_str,
        'body': f"Shift at {shift.care_home.name if shift.care_home else ''}\nUnit: {shift.unit.name if shift.unit else ''}",
        'location': f"{shift.care_home.name if shift.care_home else ''}, {shift.unit.name if shift.unit else ''}",
    }
    
    return f"https://outlook.live.com/calendar/0/deeplink/compose?{urlencode(params)}"
