"""
SMS notification service for Task 22
Handles SMS alerts for urgent notifications via Twilio
"""

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging

logger = logging.getLogger(__name__)


def send_sms_notification(phone_number, message_text):
    """
    Send SMS via Twilio
    
    Args:
        phone_number: Recipient phone in E.164 format (e.g., +447700900123)
        message_text: SMS message (max 160 chars recommended)
    
    Returns:
        tuple: (success: bool, message_sid: str or None)
    """
    if not phone_number:
        logger.warning("send_sms_notification called with no phone number")
        return False, None
    
    # Check if SMS is enabled
    if not getattr(settings, 'TWILIO_ENABLED', False):
        logger.info(f"SMS disabled - would send to {phone_number}: {message_text}")
        return False, None
    
    try:
        # Initialize Twilio client
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        # Send SMS
        message = client.messages.create(
            body=message_text[:1600],  # Twilio limit
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        logger.info(f"SMS sent to {phone_number}: {message.sid}")
        return True, message.sid
        
    except TwilioRestException as e:
        logger.error(f"Twilio error sending to {phone_number}: {e.msg}")
        return False, None
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False, None


def send_emergency_coverage_alert(staff_member, shift):
    """
    Send urgent SMS for emergency shift coverage
    
    Args:
        staff_member: User object
        shift: Shift object requiring coverage
    
    Returns:
        bool: True if sent successfully
    """
    # Check if staff has opted in to SMS
    if not staff_member.sms_notifications_enabled:
        logger.info(f"SMS disabled for {staff_member.sap}")
        return False
    
    if not staff_member.phone_number:
        logger.warning(f"No phone number for {staff_member.sap}")
        return False
    
    # Format message (keep under 160 chars)
    message = (
        f"URGENT: Emergency shift coverage needed\n"
        f"{shift.date.strftime('%a %d/%m')} {shift.start_time.strftime('%H:%M')}-{shift.end_time.strftime('%H:%M')}\n"
        f"{shift.unit.name}, {shift.care_home.name}\n"
        f"Reply to accept or login to view details"
    )
    
    success, msg_sid = send_sms_notification(staff_member.phone_number, message)
    
    if success:
        logger.info(f"Emergency coverage SMS sent to {staff_member.sap}: {msg_sid}")
    
    return success


def send_late_clockin_alert(staff_member, shift):
    """
    Send SMS alert for late clock-in
    
    Args:
        staff_member: User object
        shift: Shift object they're late for
    
    Returns:
        bool: True if sent successfully
    """
    if not staff_member.sms_notifications_enabled or not staff_member.phone_number:
        return False
    
    message = (
        f"REMINDER: Your shift started at {shift.start_time.strftime('%H:%M')}\n"
        f"{shift.unit.name}, {shift.care_home.name}\n"
        f"Please clock in or contact your manager if running late"
    )
    
    success, msg_sid = send_sms_notification(staff_member.phone_number, message)
    
    if success:
        logger.info(f"Late clock-in SMS sent to {staff_member.sap}: {msg_sid}")
    
    return success


def send_approval_required_alert(manager, item_type, item_details):
    """
    Send SMS to manager when approval is required
    
    Args:
        manager: User object (manager)
        item_type: Type of item ('leave', 'swap', 'overtime')
        item_details: Details string
    
    Returns:
        bool: True if sent successfully
    """
    if not manager.sms_notifications_enabled or not manager.phone_number:
        return False
    
    message = (
        f"ACTION REQUIRED: {item_type.upper()} approval pending\n"
        f"{item_details}\n"
        f"Login to approve/reject: {settings.SITE_URL}"
    )
    
    success, msg_sid = send_sms_notification(manager.phone_number, message)
    
    if success:
        logger.info(f"Approval required SMS sent to {manager.sap}: {msg_sid}")
    
    return success


def send_shift_cancelled_alert(staff_member, shift, reason=''):
    """
    Send SMS when a shift is cancelled
    
    Args:
        staff_member: User object
        shift: Cancelled shift object
        reason: Optional cancellation reason
    
    Returns:
        bool: True if sent successfully
    """
    if not staff_member.sms_notifications_enabled or not staff_member.phone_number:
        return False
    
    message = (
        f"CANCELLED: Your shift on {shift.date.strftime('%a %d/%m %H:%M')}\n"
        f"{shift.unit.name}\n"
        f"{f'Reason: {reason}' if reason else 'Check rota for updates'}"
    )
    
    success, msg_sid = send_sms_notification(staff_member.phone_number, message)
    
    if success:
        logger.info(f"Shift cancelled SMS sent to {staff_member.sap}: {msg_sid}")
    
    return success


def send_shift_changed_alert(staff_member, old_shift, new_shift):
    """
    Send SMS when a shift is modified
    
    Args:
        staff_member: User object
        old_shift: Original shift details
        new_shift: New shift details
    
    Returns:
        bool: True if sent successfully
    """
    if not staff_member.sms_notifications_enabled or not staff_member.phone_number:
        return False
    
    message = (
        f"SHIFT CHANGED: {new_shift.date.strftime('%a %d/%m')}\n"
        f"New time: {new_shift.start_time.strftime('%H:%M')}-{new_shift.end_time.strftime('%H:%M')}\n"
        f"{new_shift.unit.name}\n"
        f"Login to view full details"
    )
    
    success, msg_sid = send_sms_notification(staff_member.phone_number, message)
    
    if success:
        logger.info(f"Shift changed SMS sent to {staff_member.sap}: {msg_sid}")
    
    return success


def send_last_minute_shift_offer(staff_member, shift, rate_multiplier=1.5):
    """
    Send SMS for last-minute shift opportunities
    
    Args:
        staff_member: User object
        shift: Available shift object
        rate_multiplier: Pay rate multiplier (e.g., 1.5 for time-and-a-half)
    
    Returns:
        bool: True if sent successfully
    """
    if not staff_member.sms_notifications_enabled or not staff_member.phone_number:
        return False
    
    message = (
        f"LAST MINUTE SHIFT: {shift.date.strftime('%a %d/%m %H:%M')}\n"
        f"{shift.unit.name} - {rate_multiplier}x pay\n"
        f"Reply ACCEPT to claim or login to view"
    )
    
    success, msg_sid = send_sms_notification(staff_member.phone_number, message)
    
    if success:
        logger.info(f"Last minute shift SMS sent to {staff_member.sap}: {msg_sid}")
    
    return success


def send_compliance_alert(manager, alert_type, details):
    """
    Send SMS for compliance issues requiring immediate attention
    
    Args:
        manager: User object (manager)
        alert_type: Type of compliance issue
        details: Issue details
    
    Returns:
        bool: True if sent successfully
    """
    if not manager.sms_notifications_enabled or not manager.phone_number:
        return False
    
    message = (
        f"COMPLIANCE ALERT: {alert_type}\n"
        f"{details}\n"
        f"Immediate action required - login to resolve"
    )
    
    success, msg_sid = send_sms_notification(manager.phone_number, message)
    
    if success:
        logger.info(f"Compliance alert SMS sent to {manager.sap}: {msg_sid}")
    
    return success


def send_bulk_sms(recipients, message_text):
    """
    Send SMS to multiple recipients
    
    Args:
        recipients: List of User objects
        message_text: SMS message
    
    Returns:
        dict: {sent: int, failed: int, details: list}
    """
    results = {
        'sent': 0,
        'failed': 0,
        'details': []
    }
    
    for user in recipients:
        if not user.sms_notifications_enabled or not user.phone_number:
            results['failed'] += 1
            results['details'].append({
                'sap': user.sap,
                'status': 'skipped',
                'reason': 'SMS disabled or no phone number'
            })
            continue
        
        success, msg_sid = send_sms_notification(user.phone_number, message_text)
        
        if success:
            results['sent'] += 1
            results['details'].append({
                'sap': user.sap,
                'status': 'sent',
                'message_sid': msg_sid
            })
        else:
            results['failed'] += 1
            results['details'].append({
                'sap': user.sap,
                'status': 'failed'
            })
    
    logger.info(f"Bulk SMS: {results['sent']} sent, {results['failed']} failed")
    return results
