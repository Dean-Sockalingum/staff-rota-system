"""
Task 51: Error Handler Views for Sentry Integration
Custom error pages with Sentry event tracking
"""

from django.shortcuts import render
from django.conf import settings
import sentry_sdk


def handler404(request, exception=None):
    """
    Custom 404 error handler
    Renders a user-friendly 404 page
    """
    # Capture 404 in Sentry with context
    with sentry_sdk.push_scope() as scope:
        scope.set_context("request", {
            "url": request.build_absolute_uri(),
            "method": request.method,
            "user_agent": request.META.get('HTTP_USER_AGENT', 'Unknown'),
        })
        scope.set_tag("error_type", "404")
        scope.set_level("info")  # 404s are informational, not errors
        
        # Only send to Sentry in production
        if not settings.DEBUG:
            sentry_sdk.capture_message(
                f"404 Not Found: {request.path}",
                level="info"
            )
    
    return render(request, '404.html', status=404)


def handler500(request):
    """
    Custom 500 error handler
    Renders a user-friendly 500 page with Sentry event ID for user feedback
    """
    # Get the Sentry event ID if available
    sentry_event_id = None
    
    # The exception should be captured automatically by Sentry middleware
    # We can get the last event ID from the SDK
    try:
        sentry_event_id = sentry_sdk.last_event_id()
    except:
        pass
    
    context = {
        'sentry_event_id': sentry_event_id,
    }
    
    return render(request, '500.html', context, status=500)


def trigger_error(request):
    """
    Test view to trigger an intentional error for Sentry testing
    Only available in DEBUG mode
    
    Usage: Navigate to /test-sentry-error/ to trigger a test error
    """
    if not settings.DEBUG:
        from django.http import Http404
        raise Http404("This page is only available in DEBUG mode")
    
    # Add some context before the error
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("test_error", "intentional")
        scope.set_context("test_info", {
            "purpose": "Testing Sentry integration",
            "triggered_by": request.user.username if request.user.is_authenticated else "Anonymous",
        })
        
        # Trigger different types of errors based on query parameter
        error_type = request.GET.get('type', 'division')
        
        if error_type == 'division':
            # Division by zero
            result = 1 / 0
        elif error_type == 'index':
            # Index error
            my_list = [1, 2, 3]
            value = my_list[10]
        elif error_type == 'key':
            # Key error
            my_dict = {'a': 1}
            value = my_dict['nonexistent_key']
        elif error_type == 'type':
            # Type error
            result = "string" + 123
        elif error_type == 'attribute':
            # Attribute error
            obj = None
            obj.some_method()
        elif error_type == 'value':
            # Value error
            int('not a number')
        else:
            # Generic exception
            raise Exception(f"Test error triggered from Sentry test view (type: {error_type})")
