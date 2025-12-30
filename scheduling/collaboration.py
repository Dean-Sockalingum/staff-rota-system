"""
Real-time Collaboration Service Layer
Task 36: Functions for notifications, messaging, activity tracking, and user presence
"""

from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from django.contrib.auth.models import User
from datetime import timedelta
from collections import defaultdict
import uuid

from .models import (
    Notification, Message, SystemActivity, UserPresence,
    Shift, LeaveRequest, ShiftSwapRequest, CareHome
)


# ==================== NOTIFICATION MANAGEMENT ====================

def create_notification(recipient, notification_type, title, message, priority='NORMAL',
                       related_shift=None, related_leave=None, related_swap=None,
                       related_message=None, action_url=''):
    """
    Create a new notification for a user
    
    Args:
        recipient: User object
        notification_type: Type from Notification.NOTIFICATION_TYPES
        title: Short title
        message: Detailed message
        priority: Priority level (LOW, NORMAL, HIGH, URGENT)
        related_*: Optional related objects
        action_url: Optional URL for action button
    
    Returns:
        Notification object
    """
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        related_shift=related_shift,
        related_leave_request=related_leave,
        related_swap=related_swap,
        related_message=related_message,
        action_url=action_url
    )
    
    # Also log this as system activity
    log_system_activity(
        user=None,  # System generated
        activity_type='NOTIFICATION_CREATED',
        description=f"Notification sent to {recipient.username}: {title}",
        care_home=None
    )
    
    return notification


def bulk_create_notifications(recipients, notification_type, title, message, priority='NORMAL', **kwargs):
    """
    Create notifications for multiple users at once
    
    Args:
        recipients: List of User objects
        notification_type: Type from Notification.NOTIFICATION_TYPES
        title: Short title
        message: Detailed message (can include {username} placeholder)
        priority: Priority level
        **kwargs: Additional fields (related objects, action_url)
    
    Returns:
        List of created Notification objects
    """
    notifications = []
    for recipient in recipients:
        personalized_message = message.replace('{username}', recipient.username)
        personalized_title = title.replace('{username}', recipient.username)
        
        notification = Notification(
            recipient=recipient,
            notification_type=notification_type,
            title=personalized_title,
            message=personalized_message,
            priority=priority,
            **{k: v for k, v in kwargs.items() if k in ['related_shift', 'related_leave_request', 
                                                          'related_swap', 'related_message', 'action_url']}
        )
        notifications.append(notification)
    
    return Notification.objects.bulk_create(notifications)


def get_user_notifications(user, unread_only=False, limit=50):
    """
    Get notifications for a user
    
    Args:
        user: User object
        unread_only: If True, only return unread notifications
        limit: Maximum number to return
    
    Returns:
        QuerySet of Notification objects
    """
    notifications = Notification.objects.filter(
        recipient=user,
        is_archived=False
    ).select_related('related_shift', 'related_leave_request', 'related_swap', 'related_message')
    
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    return notifications[:limit]


def mark_notifications_as_read(notification_ids):
    """
    Mark multiple notifications as read
    
    Args:
        notification_ids: List of notification IDs
    
    Returns:
        Number of notifications marked as read
    """
    count = Notification.objects.filter(
        id__in=notification_ids,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return count


def get_notification_summary(user):
    """
    Get notification summary stats for a user
    
    Returns:
        Dict with unread count, priority breakdown, type breakdown
    """
    notifications = Notification.objects.filter(recipient=user, is_archived=False)
    
    unread_count = notifications.filter(is_read=False).count()
    urgent_count = notifications.filter(priority='URGENT', is_read=False).count()
    high_count = notifications.filter(priority='HIGH', is_read=False).count()
    
    type_breakdown = notifications.filter(is_read=False).values('notification_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return {
        'total_unread': unread_count,
        'urgent': urgent_count,
        'high': high_count,
        'type_breakdown': list(type_breakdown),
        'total_notifications': notifications.count()
    }


# ==================== MESSAGING SYSTEM ====================

def send_message(sender, recipients, content, subject='', message_type='DIRECT',
                parent_message=None, related_shift=None, related_leave=None,
                care_home=None, is_important=False):
    """
    Send a message to one or more users
    
    Args:
        sender: User object (sender)
        recipients: List of User objects
        content: Message content
        subject: Optional subject
        message_type: DIRECT, GROUP, SYSTEM, ANNOUNCEMENT
        parent_message: Optional parent message for threading
        related_*: Optional related objects for context
        is_important: Mark as important
    
    Returns:
        Message object
    """
    # Generate thread_id if this is a reply
    thread_id = ''
    if parent_message:
        thread_id = parent_message.thread_id or str(parent_message.id)
    elif message_type == 'GROUP' or len(recipients) > 1:
        thread_id = str(uuid.uuid4())[:8]
    
    message = Message.objects.create(
        sender=sender,
        subject=subject,
        content=content,
        message_type=message_type,
        parent_message=parent_message,
        thread_id=thread_id,
        related_shift=related_shift,
        related_leave_request=related_leave,
        care_home=care_home,
        is_important=is_important
    )
    
    # Add recipients (M2M)
    message.recipients.add(*recipients)
    
    # Create notifications for recipients
    for recipient in recipients:
        if recipient != sender:  # Don't notify sender
            create_notification(
                recipient=recipient,
                notification_type='MESSAGE_RECEIVED',
                title=f"New message from {sender.get_full_name() or sender.username}",
                message=f"Subject: {subject}\n{content[:100]}..." if len(content) > 100 else content,
                priority='HIGH' if is_important else 'NORMAL',
                related_message=message,
                action_url=f'/messages/{message.id}/'
            )
    
    # Log activity
    log_system_activity(
        user=sender,
        activity_type='MESSAGE_SENT',
        description=f"Message sent to {len(recipients)} recipient(s): {subject or 'No subject'}",
        care_home=care_home
    )
    
    return message


def get_user_messages(user, message_type=None, unread_only=False, limit=50):
    """
    Get messages for a user (inbox)
    
    Args:
        user: User object
        message_type: Filter by type (DIRECT, GROUP, etc.)
        unread_only: Not implemented (would need MessageRead model)
        limit: Maximum number to return
    
    Returns:
        QuerySet of Message objects
    """
    messages = Message.objects.filter(
        recipients=user,
        is_archived=False
    ).select_related('sender', 'parent_message', 'care_home').prefetch_related('recipients')
    
    if message_type:
        messages = messages.filter(message_type=message_type)
    
    return messages[:limit]


def get_conversation(user1, user2, limit=50):
    """
    Get conversation between two users
    
    Args:
        user1: First User object
        user2: Second User object
        limit: Maximum number of messages
    
    Returns:
        QuerySet of Message objects ordered by created_at
    """
    messages = Message.objects.filter(
        (Q(sender=user1, recipients=user2) | Q(sender=user2, recipients=user1)),
        message_type='DIRECT'
    ).select_related('sender').order_by('created_at')
    
    return messages[:limit]


def get_thread_messages(thread_id):
    """
    Get all messages in a thread
    
    Args:
        thread_id: Thread ID
    
    Returns:
        QuerySet of Message objects
    """
    return Message.objects.filter(thread_id=thread_id).select_related(
        'sender', 'parent_message'
    ).prefetch_related('recipients').order_by('created_at')


def search_messages(user, query, limit=20):
    """
    Search user's messages
    
    Args:
        user: User object
        query: Search string
        limit: Maximum results
    
    Returns:
        QuerySet of matching messages
    """
    return Message.objects.filter(
        recipients=user,
        Q(subject__icontains=query) | Q(content__icontains=query)
    ).select_related('sender')[:limit]


# ==================== ACTIVITY LOGGING ====================

def log_system_activity(user, activity_type, description, care_home=None,
                       related_shift=None, related_user=None, related_leave=None,
                       old_value=None, new_value=None, ip_address=None, user_agent=''):
    """
    Log a system activity for audit trail
    
    Args:
        user: User who performed action (None for system)
        activity_type: Type from SystemActivity.ACTIVITY_TYPES
        description: Detailed description
        care_home: Optional related care home
        related_*: Optional related objects
        old_value: Dict of old state
        new_value: Dict of new state
        ip_address: IP address of user
        user_agent: Browser user agent
    
    Returns:
        SystemActivity object
    """
    activity = SystemActivity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        care_home=care_home,
        related_shift=related_shift,
        related_user=related_user,
        related_leave_request=related_leave,
        old_value=old_value or {},
        new_value=new_value or {},
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return activity


def get_activity_feed(care_home=None, user=None, activity_types=None, days=7, limit=100):
    """
    Get recent activity feed
    
    Args:
        care_home: Filter by care home
        user: Filter by user who performed action
        activity_types: List of activity types to include
        days: Number of days to look back
        limit: Maximum number of activities
    
    Returns:
        QuerySet of SystemActivity objects
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    
    activities = SystemActivity.objects.filter(
        created_at__gte=cutoff_date
    ).select_related('user', 'care_home', 'related_shift', 'related_user')
    
    if care_home:
        activities = activities.filter(care_home=care_home)
    
    if user:
        activities = activities.filter(user=user)
    
    if activity_types:
        activities = activities.filter(activity_type__in=activity_types)
    
    return activities[:limit]


def get_user_activity_stats(user, days=30):
    """
    Get activity statistics for a user
    
    Returns:
        Dict with activity counts by type
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    
    activities = SystemActivity.objects.filter(
        user=user,
        created_at__gte=cutoff_date
    )
    
    total_activities = activities.count()
    by_type = activities.values('activity_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent logins
    logins = activities.filter(activity_type='USER_LOGIN').count()
    
    return {
        'total_activities': total_activities,
        'by_type': list(by_type),
        'logins': logins,
        'period_days': days
    }


# ==================== USER PRESENCE ====================

def update_user_presence(user, status='ONLINE', current_page='', custom_status='',
                        status_emoji='', session_id='', device_info=''):
    """
    Update or create user presence status
    
    Args:
        user: User object
        status: ONLINE, AWAY, BUSY, OFFLINE
        current_page: Current page URL
        custom_status: Custom status message
        status_emoji: Status emoji
        session_id: Session ID
        device_info: Device/browser info
    
    Returns:
        UserPresence object
    """
    presence, created = UserPresence.objects.get_or_create(user=user)
    
    presence.status = status
    presence.current_page = current_page
    presence.custom_status = custom_status
    presence.status_emoji = status_emoji
    presence.session_id = session_id
    presence.device_info = device_info
    presence.last_activity = timezone.now()
    presence.save()
    
    return presence


def get_online_users(care_home=None, minutes=5):
    """
    Get currently online users
    
    Args:
        care_home: Optional care home filter (would need User-CareHome relation)
        minutes: Consider user online if active within this many minutes
    
    Returns:
        QuerySet of User objects with presence info
    """
    time_threshold = timezone.now() - timedelta(minutes=minutes)
    
    online_presences = UserPresence.objects.filter(
        last_seen__gte=time_threshold,
        status__in=['ONLINE', 'AWAY', 'BUSY']
    ).select_related('user')
    
    return [p.user for p in online_presences]


def get_user_presence_info(user):
    """
    Get detailed presence info for a user
    
    Returns:
        Dict with status, last_seen, is_online, custom_status
    """
    try:
        presence = UserPresence.objects.get(user=user)
        return {
            'status': presence.get_status_display(),
            'status_code': presence.status,
            'last_seen': presence.last_seen,
            'is_online': presence.is_online(),
            'custom_status': presence.custom_status,
            'status_emoji': presence.status_emoji,
            'current_page': presence.current_page,
        }
    except UserPresence.DoesNotExist:
        return {
            'status': 'Unknown',
            'status_code': 'OFFLINE',
            'last_seen': None,
            'is_online': False,
            'custom_status': '',
            'status_emoji': '',
            'current_page': '',
        }


def bulk_update_presence(user_status_pairs):
    """
    Update presence for multiple users at once
    
    Args:
        user_status_pairs: List of (user, status) tuples
    
    Returns:
        Number of presences updated
    """
    count = 0
    for user, status in user_status_pairs:
        update_user_presence(user, status)
        count += 1
    
    return count


def cleanup_stale_presence(hours=24):
    """
    Mark users as OFFLINE if they haven't been seen in X hours
    
    Args:
        hours: Hours of inactivity threshold
    
    Returns:
        Number of presences updated
    """
    cutoff_time = timezone.now() - timedelta(hours=hours)
    
    count = UserPresence.objects.filter(
        last_seen__lt=cutoff_time,
        status__in=['ONLINE', 'AWAY', 'BUSY']
    ).update(status='OFFLINE')
    
    return count


# ==================== HELPER FUNCTIONS ====================

def notify_shift_assignment(shift, assigned_user):
    """
    Helper to notify user when assigned to a shift
    """
    return create_notification(
        recipient=assigned_user,
        notification_type='SHIFT_ASSIGNED',
        title='New Shift Assigned',
        message=f'You have been assigned to a {shift.shift_type} shift on {shift.date} from {shift.start_time} to {shift.end_time}.',
        priority='HIGH',
        related_shift=shift,
        action_url=f'/shifts/{shift.id}/'
    )


def notify_leave_status(leave_request, approved, approver):
    """
    Helper to notify user about leave request status
    """
    status = 'APPROVED' if approved else 'REJECTED'
    return create_notification(
        recipient=leave_request.staff_member.user if hasattr(leave_request.staff_member, 'user') else leave_request.requested_by,
        notification_type=f'LEAVE_{status}',
        title=f'Leave Request {status.title()}',
        message=f'Your leave request from {leave_request.start_date} to {leave_request.end_date} has been {status.lower()} by {approver.get_full_name() or approver.username}.',
        priority='HIGH',
        related_leave=leave_request,
        action_url=f'/leave-requests/{leave_request.id}/'
    )


def notify_swap_request(swap_request, target_user):
    """
    Helper to notify user about shift swap request
    """
    return create_notification(
        recipient=target_user,
        notification_type='SWAP_REQUEST',
        title='Shift Swap Request',
        message=f'{swap_request.requesting_staff.user.get_full_name()} wants to swap shifts with you.',
        priority='HIGH',
        related_swap=swap_request,
        action_url=f'/shift-swaps/{swap_request.id}/'
    )
