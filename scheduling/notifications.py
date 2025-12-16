"""
Notification system for automated workflow
Handles SMS, email, and push notifications for staffing events
"""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)


def send_sms(phone_number, message, context=None):
    """
    Send SMS notification via Twilio
    
    Args:
        phone_number: Recipient phone number (E.164 format)
        message: Message text or template name
        context: Optional context dict for template rendering
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not phone_number:
        logger.warning("send_sms called with no phone number")
        return False
    
    try:
        # Render message from template if context provided
        if context:
            message_text = render_to_string(f'notifications/sms/{message}.txt', context)
        else:
            message_text = message
        
        # Initialize Twilio client
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        # Send SMS
        sms = client.messages.create(
            body=message_text,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        logger.info(f"SMS sent successfully to {phone_number}: {sms.sid}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False


def send_email(recipient_email, subject, message, context=None, html_template=None):
    """
    Send email notification
    
    Args:
        recipient_email: Recipient email address
        subject: Email subject line
        message: Plain text message or template name
        context: Optional context dict for template rendering
        html_template: Optional HTML template name
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not recipient_email:
        logger.warning("send_email called with no email address")
        return False
    
    try:
        # Render plain text message
        if context:
            plain_message = render_to_string(f'notifications/email/{message}.txt', context)
        else:
            plain_message = message
        
        # Render HTML message if template provided
        html_message = None
        if html_template:
            html_message = render_to_string(f'notifications/email/{html_template}.html', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Email sent successfully to {recipient_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return False


def send_push_notification(user, title, message, data=None):
    """
    Send push notification (placeholder for future implementation)
    
    Args:
        user: User object or user ID
        title: Notification title
        message: Notification message
        data: Optional data payload dict
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    # Placeholder for push notification service (Firebase, OneSignal, etc.)
    logger.info(f"Push notification queued for user {user}: {title}")
    return True


# Workflow-specific notification functions

def notify_ot_offer(staff_member, shift, batch_id, deadline):
    """Send OT offer notification to staff member"""
    context = {
        'staff_name': staff_member.full_name,
        'shift_date': shift.date,
        'shift_time': f"{shift.start_time} - {shift.end_time}",
        'unit': shift.unit.name,
        'rate': shift.calculate_ot_rate(),
        'deadline': deadline.strftime('%H:%M'),
        'batch_id': batch_id
    }
    
    # Send SMS
    sms_success = send_sms(
        staff_member.phone_number,
        'ot_offer',
        context
    )
    
    # Send email
    email_success = send_email(
        staff_member.email,
        f"Overtime Opportunity - {shift.date}",
        'ot_offer',
        context,
        html_template='ot_offer'
    )
    
    # Send push notification
    push_success = send_push_notification(
        staff_member,
        "Overtime Opportunity",
        f"OT available for {shift.date} at {shift.unit.name}",
        data={'batch_id': batch_id, 'shift_id': shift.id}
    )
    
    return sms_success or email_success or push_success


def notify_reallocation_request(staff_member, shift, from_home, to_home):
    """Send reallocation request notification"""
    context = {
        'staff_name': staff_member.full_name,
        'shift_date': shift.date,
        'shift_time': f"{shift.start_time} - {shift.end_time}",
        'from_home': from_home.name,
        'to_home': to_home.name,
        'unit': shift.unit.name
    }
    
    send_sms(staff_member.phone_number, 'reallocation_request', context)
    send_email(
        staff_member.email,
        f"Reallocation Request - {shift.date}",
        'reallocation_request',
        context,
        html_template='reallocation_request'
    )


def notify_agency_request_senior_officer(agency_request, shift):
    """Send agency request approval notification to Senior Officer"""
    context = {
        'shift_date': shift.date,
        'shift_time': f"{shift.shift_type.start_time} - {shift.shift_type.end_time}",
        'unit': shift.unit.name,
        'reason': agency_request.cover_request.absence.reason if agency_request.cover_request.absence else 'Staff absence',
        'deadline': agency_request.approval_deadline.strftime('%H:%M on %d/%m/%Y'),
        'request_id': agency_request.id,
        'approval_url': f"{settings.BASE_URL}/admin/scheduling/agencyrequest/{agency_request.id}/change/"
    }
    
    # Get Senior Officer mailbox/email
    senior_officer_email = getattr(settings, 'SENIOR_OFFICER_EMAIL', 'senior.officer@orchard-grove.co.uk')
    
    send_email(
        senior_officer_email,
        f"URGENT: Agency Request Approval Required - {shift.date}",
        'agency_approval',
        context,
        html_template='agency_approval'
    )
    
    # Also send SMS to Senior Officer mobile if configured
    senior_officer_phone = getattr(settings, 'SENIOR_OFFICER_PHONE', None)
    if senior_officer_phone:
        send_sms(
            senior_officer_phone,
            f"URGENT: Agency approval needed for {shift.date} at {shift.unit.name}. Deadline: {agency_request.approval_deadline.strftime('%H:%M')}. Check email for details."
        )


def notify_agency_auto_approved(agency_request, shift):
    """Send notification when agency request is auto-approved after timeout"""
    context = {
        'shift_date': shift.date,
        'shift_time': f"{shift.shift_type.start_time} - {shift.shift_type.end_time}",
        'unit': shift.unit.name,
        'request_id': agency_request.id,
        'timeout_reason': 'No response within 15-minute approval window'
    }
    
    # Notify Senior Officer of auto-approval
    senior_officer_email = getattr(settings, 'SENIOR_OFFICER_EMAIL', 'senior.officer@orchard-grove.co.uk')
    send_email(
        senior_officer_email,
        f"INFO: Agency Request Auto-Approved - {shift.date}",
        'agency_auto_approved',
        context,
        html_template='agency_auto_approved'
    )


def notify_long_term_cover_plan(absence, plan):
    """Send notification about long-term cover plan creation"""
    context = {
        'staff_name': absence.staff_member.full_name,
        'absence_start': absence.start_date,
        'absence_end': absence.end_date,
        'total_shifts': plan.total_shifts_affected,
        'plan_id': plan.id,
        'plan_url': f"{settings.BASE_URL}/admin/scheduling/longtermcoverplan/{plan.id}/change/"
    }
    
    # Notify Unit Manager
    # Get unit from staff member or first affected shift
    unit = absence.staff_member.unit if hasattr(absence.staff_member, 'unit') and absence.staff_member.unit else None
    if not unit and absence.affected_shifts.exists():
        unit = absence.affected_shifts.first().unit
    
    unit_manager_email = unit.manager.email if unit and hasattr(unit, 'manager') and unit.manager else None
    if unit_manager_email:
        send_email(
            unit_manager_email,
            f"Long-Term Cover Plan Generated - {absence.staff_member.full_name}",
            'long_term_plan',
            context,
            html_template='long_term_plan'
        )


def notify_cover_resolution(cover_request, resolution_method, assigned_staff=None):
    """Send notification when cover request is resolved"""
    context = {
        'shift_date': cover_request.shift.date,
        'unit': cover_request.shift.unit.name,
        'resolution_method': resolution_method,
        'assigned_staff': assigned_staff.full_name if assigned_staff else 'Agency',
        'absence_staff': cover_request.absence.staff_member.full_name
    }
    
    # Notify Unit Manager
    unit = cover_request.shift.unit
    if hasattr(unit, 'manager') and unit.manager:
        send_email(
            unit.manager.email,
            f"Shift Coverage Confirmed - {cover_request.shift.date}",
            'cover_resolved',
            context,
            html_template='cover_resolved'
        )


def notify_ot_acceptance(ot_offer, staff_member, shift):
    """Send confirmation when staff accepts OT offer"""
    context = {
        'staff_name': staff_member.full_name,
        'shift_date': shift.date,
        'shift_time': f"{shift.start_time} - {shift.end_time}",
        'unit': shift.unit.name,
        'rate': shift.calculate_ot_rate()
    }
    
    # Confirm to staff member
    send_sms(
        staff_member.phone_number,
        f"OT CONFIRMED: {shift.date} at {shift.unit.name}, {shift.start_time}-{shift.end_time}. Rate: {shift.calculate_ot_rate()}."
    )
    
    send_email(
        staff_member.email,
        f"Overtime Shift Confirmed - {shift.date}",
        'ot_accepted',
        context,
        html_template='ot_accepted'
    )


def notify_ot_declined(ot_offer, staff_member, shift):
    """Send confirmation when staff declines OT offer"""
    # Just log for now, may not need notification
    logger.info(f"OT offer declined by {staff_member.full_name} for shift {shift.id}")


def notify_wdt_compliance_warning(staff_member, violation_type, details):
    """Send WTD compliance warning"""
    context = {
        'staff_name': staff_member.full_name,
        'violation_type': violation_type,
        'details': details
    }
    
    # Notify HR/Compliance team
    hr_email = getattr(settings, 'HR_EMAIL', 'hr@orchard-grove.co.uk')
    send_email(
        hr_email,
        f"WTD Compliance Alert - {staff_member.full_name}",
        'wdt_warning',
        context,
        html_template='wdt_warning'
    )


def notify_post_shift_admin_required(shift, cover_request):
    """Send reminder for post-shift administration"""
    context = {
        'shift_date': shift.date,
        'shift_time': f"{shift.start_time} - {shift.end_time}",
        'unit': shift.unit.name,
        'staff_assigned': shift.assigned_staff.full_name if hasattr(shift, 'assigned_staff') else 'Unknown',
        'admin_url': f"{settings.BASE_URL}/admin/scheduling/postshiftadministration/add/?shift={shift.id}"
    }
    
    # Notify Unit Manager
    unit = shift.unit
    if hasattr(unit, 'manager') and unit.manager:
        send_email(
            unit.manager.email,
            f"Post-Shift Admin Required - {shift.date}",
            'post_shift_admin',
            context,
            html_template='post_shift_admin'
        )


# Batch notification functions

def send_batch_ot_offers(batch, offers_sent):
    """Send summary notification about batch OT offers"""
    logger.info(f"Batch {batch.id}: Sent {offers_sent} OT offers for shift {batch.shift.date}")


def send_escalation_summary(cover_request, steps_attempted):
    """Send summary of escalation attempts"""
    context = {
        'request_id': cover_request.id,
        'shift_date': cover_request.absence.shift.date,
        'steps_attempted': steps_attempted,
        'final_status': cover_request.status
    }
    
    senior_officer_email = getattr(settings, 'SENIOR_OFFICER_EMAIL', 'senior.officer@orchard-grove.co.uk')
    send_email(
        senior_officer_email,
        f"Cover Request Escalation Summary - {cover_request.absence.shift.date}",
        'escalation_summary',
        context,
        html_template='escalation_summary'
    )
