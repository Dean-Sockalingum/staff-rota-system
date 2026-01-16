"""
Django signals for authentication event logging.
Automatically logs user login, logout, and failed login attempts to SystemAccessLog.
"""
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models_audit import SystemAccessLog


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login."""
    try:
        SystemAccessLog.objects.create(
            user=user,
            access_type='LOGIN',
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            session_key=request.session.session_key,
            success=True
        )
    except Exception as e:
        print(f"Login logging failed: {e}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout."""
    try:
        SystemAccessLog.objects.create(
            user=user,
            access_type='LOGOUT',
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            session_key=request.session.session_key if request.session.session_key else '',
            success=True
        )
    except Exception as e:
        print(f"Logout logging failed: {e}")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    try:
        # Extract username from credentials
        username = credentials.get('username', 'unknown')
        
        SystemAccessLog.objects.create(
            user=None,  # User not authenticated
            username_attempt=username,
            access_type='LOGIN_FAILED',
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            session_key=request.session.session_key if hasattr(request, 'session') else '',
            success=False,
            failure_reason=f'Failed login attempt for username: {username}'
        )
    except Exception as e:
        print(f"Failed login logging failed: {e}")


def _get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')  # Default for tests
    return ip if ip else '127.0.0.1'  # Ensure we always return an IP
