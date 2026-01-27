"""
Email notification service for Task 21
Handles automated email notifications for shifts, leave requests, and rotas
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
import logging

logger = logging.getLogger(__name__)


def send_shift_reminder_email(shift):
    """
    Send reminder email 24 hours before a shift
    
    Args:
        shift: Shift object
    
    Returns:
        bool: True if sent successfully
    """
    try:
        staff_member = shift.staff
        
        if not staff_member.email:
            logger.warning(f"No email for staff {staff_member.sap_number}")
            return False
        
        # Build login URL
        login_url = f"{settings.SITE_URL}/scheduling/my-schedule/"
        
        context = {
            'staff_member': staff_member,
            'shift': shift,
            'login_url': login_url,
        }
        
        # Render HTML email
        html_content = render_to_string('scheduling/email/shift_reminder.html', context)
        
        # Create plain text fallback
        text_content = f"""
Hello {staff_member.first_name},

This is a reminder about your upcoming shift:

Date: {shift.date.strftime('%A, %d %B %Y')}
Time: {shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M')}
Shift Type: {shift.shift_type.name}
Unit: {shift.unit.name}
Care Home: {shift.care_home.name}

Please ensure you arrive 10-15 minutes early for handover.

View your full schedule: {login_url}

Thank you for your dedication to quality care.

Best regards,
Staff Rota System
"""
        
        # Send email
        subject = f"Shift Reminder - {shift.date.strftime('%A, %d %B %Y')}"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[staff_member.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Shift reminder sent to {staff_member.email} for shift on {shift.date}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send shift reminder: {str(e)}")
        return False


def send_leave_approved_email(leave_request, approved_by, manager_notes=''):
    """
    Send email when leave request is approved
    
    Args:
        leave_request: LeaveRequest object
        approved_by: User who approved the request
        manager_notes: Optional notes from manager
    
    Returns:
        bool: True if sent successfully
    """
    try:
        staff_member = leave_request.staff
        
        if not staff_member.email:
            logger.warning(f"No email for staff {staff_member.sap_number}")
            return False
        
        login_url = f"{settings.SITE_URL}/scheduling/leave-requests/"
        
        context = {
            'staff_member': staff_member,
            'leave_request': leave_request,
            'approved_by': approved_by,
            'manager_notes': manager_notes,
            'login_url': login_url,
        }
        
        html_content = render_to_string('scheduling/email/leave_approved.html', context)
        
        text_content = f"""
Hello {staff_member.first_name},

Good news! Your leave request has been approved.

Leave Type: {leave_request.leave_type}
Start Date: {leave_request.start_date.strftime('%A, %d %B %Y')}
End Date: {leave_request.end_date.strftime('%A, %d %B %Y')}
Total Days: {leave_request.total_days}

{f"Manager's Comments: {manager_notes}" if manager_notes else ""}

Your leave has been added to the system.

View your leave: {login_url}

Best regards,
{approved_by.get_full_name()}
{approved_by.role.name if approved_by.role else ''}
"""
        
        subject = "Leave Request Approved"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[staff_member.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Leave approved email sent to {staff_member.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send leave approved email: {str(e)}")
        return False


def send_leave_rejected_email(leave_request, rejected_by, manager_notes=''):
    """
    Send email when leave request is rejected
    
    Args:
        leave_request: LeaveRequest object
        rejected_by: User who rejected the request
        manager_notes: Reason for rejection
    
    Returns:
        bool: True if sent successfully
    """
    try:
        staff_member = leave_request.staff
        
        if not staff_member.email:
            logger.warning(f"No email for staff {staff_member.sap_number}")
            return False
        
        login_url = f"{settings.SITE_URL}/scheduling/leave-requests/"
        
        context = {
            'staff_member': staff_member,
            'leave_request': leave_request,
            'rejected_by': rejected_by,
            'manager_notes': manager_notes,
            'login_url': login_url,
        }
        
        html_content = render_to_string('scheduling/email/leave_rejected.html', context)
        
        text_content = f"""
Hello {staff_member.first_name},

Thank you for submitting your leave request. Unfortunately, we are unable to approve it at this time.

Leave Type: {leave_request.leave_type}
Start Date: {leave_request.start_date.strftime('%A, %d %B %Y')}
End Date: {leave_request.end_date.strftime('%A, %d %B %Y')}

{f"Reason: {manager_notes}" if manager_notes else ""}

Please contact your manager to discuss alternative dates.

Best regards,
{rejected_by.get_full_name()}
{rejected_by.role.name if rejected_by.role else ''}
"""
        
        subject = "Leave Request Update"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[staff_member.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Leave rejected email sent to {staff_member.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send leave rejected email: {str(e)}")
        return False


def send_shift_swap_email(staff_member, original_shift, swap_with, new_shift=None):
    """
    Send email confirmation when shift swap is processed
    
    Args:
        staff_member: User receiving the email
        original_shift: Shift being given away
        swap_with: User swapping with
        new_shift: Optional shift being received
    
    Returns:
        bool: True if sent successfully
    """
    try:
        if not staff_member.email:
            logger.warning(f"No email for staff {staff_member.sap_number}")
            return False
        
        login_url = f"{settings.SITE_URL}/scheduling/my-schedule/"
        
        context = {
            'staff_member': staff_member,
            'original_shift': original_shift,
            'swap_with': swap_with,
            'new_shift': new_shift,
            'login_url': login_url,
        }
        
        html_content = render_to_string('scheduling/email/shift_swap_confirmed.html', context)
        
        text_content = f"""
Hello {staff_member.first_name},

Your shift swap has been confirmed.

Original Shift (Given Away):
Date: {original_shift.date.strftime('%A, %d %B %Y')}
Time: {original_shift.start_time.strftime('%H:%M')} - {original_shift.end_time.strftime('%H:%M')}
Unit: {original_shift.unit.name}
Now Assigned To: {swap_with.get_full_name()}

{f'''New Shift (Received):
Date: {new_shift.date.strftime('%A, %d %B %Y')}
Time: {new_shift.start_time.strftime('%H:%M')} - {new_shift.end_time.strftime('%H:%M')}
Unit: {new_shift.unit.name}
''' if new_shift else ''}

The rota has been updated.

View your schedule: {login_url}

Best regards,
Staff Rota System
"""
        
        subject = "Shift Swap Confirmed"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[staff_member.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Shift swap email sent to {staff_member.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send shift swap email: {str(e)}")
        return False


def send_weekly_rota_email(staff_member, week_start, shifts):
    """
    Send weekly schedule email to staff member
    
    Args:
        staff_member: User object
        week_start: Date of Monday for the week
        shifts: QuerySet of shifts for the week
    
    Returns:
        bool: True if sent successfully
    """
    try:
        if not staff_member.email:
            logger.warning(f"No email for staff {staff_member.sap_number}")
            return False
        
        # Calculate total hours
        total_hours = 0
        for shift in shifts:
            shift_duration = datetime.combine(datetime.min, shift.end_time) - datetime.combine(datetime.min, shift.start_time)
            total_hours += shift_duration.total_seconds() / 3600
        
        login_url = f"{settings.SITE_URL}/scheduling/my-schedule/"
        
        # Get care home from first shift
        care_home = shifts.first().care_home if shifts.exists() else None
        
        context = {
            'staff_member': staff_member,
            'week_start': week_start,
            'shifts': shifts,
            'total_hours': round(total_hours, 1),
            'login_url': login_url,
            'care_home': care_home,
        }
        
        html_content = render_to_string('scheduling/email/weekly_rota.html', context)
        
        text_content = f"""
Hello {staff_member.first_name},

Here is your schedule for the week of {week_start.strftime('%d %B %Y')}:

"""
        
        if shifts:
            for shift in shifts:
                text_content += f"""
{shift.date.strftime('%A, %d/%m/%Y')} - {shift.shift_type.name}
  Time: {shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M')}
  Unit: {shift.unit.name}
"""
            text_content += f"\nTotal Shifts: {shifts.count()}\nTotal Hours: {round(total_hours, 1)} hours\n"
        else:
            text_content += "You have no shifts scheduled for this week.\n"
        
        text_content += f"""
View your full schedule: {login_url}

Thank you for your commitment to quality care.

Best regards,
{care_home.name if care_home else 'Management Team'}
"""
        
        subject = f"Your Weekly Schedule - Week of {week_start.strftime('%d %B %Y')}"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[staff_member.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Weekly rota email sent to {staff_member.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send weekly rota email: {str(e)}")
        return False
