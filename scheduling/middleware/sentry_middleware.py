"""
Task 51: Sentry Error Tracking Middleware
Enhanced error tracking with user context and breadcrumbs
"""

import sentry_sdk
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class SentryContextMiddleware(MiddlewareMixin):
    """
    Middleware to add user context and breadcrumbs to Sentry events
    Enriches error reports with useful debugging information
    """
    
    def process_request(self, request):
        """
        Add user and request context to Sentry scope
        """
        if not hasattr(settings, 'SENTRY_DSN') or not settings.SENTRY_DSN:
            return None
        
        # Set user context if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            with sentry_sdk.configure_scope() as scope:
                scope.set_user({
                    "id": request.user.sap,
                    "username": request.user.username,
                    "email": request.user.email,
                    "role": request.user.role if hasattr(request.user, 'role') else 'Unknown',
                })
                
                # Add user preferences if available
                if hasattr(request.user, 'preferences'):
                    prefs = request.user.preferences
                    scope.set_context("user_preferences", {
                        "theme": prefs.theme,
                        "language": prefs.language,
                        "timezone": prefs.timezone,
                    })
        
        # Add request context
        with sentry_sdk.configure_scope() as scope:
            scope.set_context("request", {
                "url": request.build_absolute_uri(),
                "method": request.method,
                "query_string": request.META.get('QUERY_STRING', ''),
                "user_agent": request.META.get('HTTP_USER_AGENT', 'Unknown'),
                "ip_address": self._get_client_ip(request),
                "referrer": request.META.get('HTTP_REFERER', 'Direct'),
            })
            
            # Add breadcrumb for the request
            sentry_sdk.add_breadcrumb(
                category='request',
                message=f'{request.method} {request.path}',
                level='info',
            )
        
        return None
    
    def process_response(self, request, response):
        """
        Add response breadcrumb to Sentry
        """
        if not hasattr(settings, 'SENTRY_DSN') or not settings.SENTRY_DSN:
            return response
        
        # Add breadcrumb for response
        sentry_sdk.add_breadcrumb(
            category='response',
            message=f'Response: {response.status_code}',
            level='info' if response.status_code < 400 else 'warning',
            data={
                'status_code': response.status_code,
                'content_type': response.get('Content-Type', 'unknown'),
            }
        )
        
        return response
    
    def process_exception(self, request, exception):
        """
        Capture exception in Sentry with full context
        """
        if not hasattr(settings, 'SENTRY_DSN') or not settings.SENTRY_DSN:
            return None
        
        # Add exception-specific context
        with sentry_sdk.configure_scope() as scope:
            scope.set_context("exception_info", {
                "type": type(exception).__name__,
                "message": str(exception),
                "request_path": request.path,
                "request_method": request.method,
            })
            
            # Add breadcrumb for the exception
            sentry_sdk.add_breadcrumb(
                category='exception',
                message=f'Exception occurred: {type(exception).__name__}',
                level='error',
                data={
                    'exception': str(exception),
                    'path': request.path,
                }
            )
        
        # Let Sentry middleware handle the actual capture
        return None
    
    def _get_client_ip(self, request):
        """
        Get the client's IP address from the request
        Handles proxy headers (X-Forwarded-For)
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SentryPerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to track performance metrics in Sentry
    Monitors slow requests and database queries
    """
    
    def process_request(self, request):
        """
        Start transaction for performance monitoring
        """
        if not hasattr(settings, 'SENTRY_DSN') or not settings.SENTRY_DSN:
            return None
        
        # Start a transaction for this request
        transaction = sentry_sdk.start_transaction(
            op="http.server",
            name=f"{request.method} {request.path}",
        )
        
        # Store transaction on request for later use
        request._sentry_transaction = transaction
        
        # Set transaction tags
        transaction.set_tag("http.method", request.method)
        transaction.set_tag("http.url", request.path)
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            transaction.set_tag("user.role", getattr(request.user, 'role', 'Unknown'))
        
        return None
    
    def process_response(self, request, response):
        """
        Finish transaction and record performance metrics
        """
        if not hasattr(settings, 'SENTRY_DSN') or not settings.SENTRY_DSN:
            return response
        
        # Finish the transaction if it exists
        if hasattr(request, '_sentry_transaction'):
            transaction = request._sentry_transaction
            transaction.set_http_status(response.status_code)
            transaction.set_tag("http.status_code", response.status_code)
            transaction.finish()
        
        return response
    
    def process_exception(self, request, exception):
        """
        Mark transaction as failed on exception
        """
        if not hasattr(settings, 'SENTRY_DSN') or not settings.SENTRY_DSN:
            return None
        
        # Mark transaction as failed
        if hasattr(request, '_sentry_transaction'):
            transaction = request._sentry_transaction
            transaction.set_status("internal_error")
            transaction.finish()
        
        return None
