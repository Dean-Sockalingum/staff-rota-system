"""
Middleware for automatic audit logging of user actions and data changes.
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from threading import local
import json

from .models_audit import DataChangeLog, SystemAccessLog

# Thread-local storage for request context
_thread_locals = local()


def get_current_request():
    """Get the current request from thread-local storage."""
    return getattr(_thread_locals, 'request', None)


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to track user access and store request context for signal handlers.
    This middleware makes the current request available to Django signals so they
    can log which user made changes.
    """
    
    def process_request(self, request):
        """Store the current request in thread-local storage."""
        _thread_locals.request = request
        return None
    
    def process_response(self, request, response):
        """Clean up thread-local storage."""
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response
    
    def _get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Model change tracking via signals
# Store original values before save
_original_values = {}


@receiver(pre_save)
def store_original_values(sender, instance, **kwargs):
    """Store original model values before save for comparison."""
    # Skip audit models to avoid recursion
    if sender.__name__ in ['DataChangeLog', 'SystemAccessLog', 'ComplianceCheck', 
                           'ComplianceViolation', 'AuditReport', 'ComplianceRule']:
        return
    
    # Skip new instances (no original values)
    if instance.pk is None:
        return
    
    try:
        # Get the original instance from database
        original = sender.objects.get(pk=instance.pk)
        _original_values[instance.pk] = model_to_dict(original)
    except sender.DoesNotExist:
        pass


@receiver(post_save)
def log_model_change(sender, instance, created, **kwargs):
    """Log model changes to DataChangeLog."""
    # Skip audit models to avoid recursion
    if sender.__name__ in ['DataChangeLog', 'SystemAccessLog', 'ComplianceCheck', 
                           'ComplianceViolation', 'AuditReport', 'ComplianceRule']:
        return
    
    # Get current request
    request = get_current_request()
    if not request or not request.user.is_authenticated:
        return
    
    # Determine action
    action = 'CREATE' if created else 'UPDATE'
    
    try:
        # Get content type
        content_type = ContentType.objects.get_for_model(sender)
        
        # Prepare change data
        if created:
            # For new objects, all current values are "new"
            changes = model_to_dict(instance)
            old_values = {}
            new_values = changes
        else:
            # For updates, compare old and new values
            old_values = _original_values.get(instance.pk, {})
            new_values = model_to_dict(instance)
            
            # Find what actually changed
            changes = {}
            for field, new_value in new_values.items():
                old_value = old_values.get(field)
                if old_value != new_value:
                    changes[field] = {
                        'old': old_value,
                        'new': new_value
                    }
            
            # Skip logging if nothing changed
            if not changes:
                return
        
        # Create audit log entry
        DataChangeLog.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=str(instance.pk),
            action=action,
            field_name='multiple' if len(changes) > 1 else list(changes.keys())[0] if changes else 'unknown',
            old_value=json.dumps(old_values, cls=DjangoJSONEncoder)[:1000],
            new_value=json.dumps(new_values, cls=DjangoJSONEncoder)[:1000],
            ip_address=AuditLoggingMiddleware()._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        # Clean up stored original values
        if instance.pk in _original_values:
            del _original_values[instance.pk]
    
    except Exception as e:
        # Don't break the application if audit logging fails
        print(f"Data change logging failed: {e}")


@receiver(post_delete)
def log_model_deletion(sender, instance, **kwargs):
    """Log model deletions to DataChangeLog."""
    # Skip audit models to avoid recursion
    if sender.__name__ in ['DataChangeLog', 'SystemAccessLog', 'ComplianceCheck', 
                           'ComplianceViolation', 'AuditReport', 'ComplianceRule']:
        return
    
    # Get current request
    request = get_current_request()
    if not request or not request.user.is_authenticated:
        return
    
    try:
        # Get content type
        content_type = ContentType.objects.get_for_model(sender)
        
        # Get object representation
        old_values = model_to_dict(instance)
        
        # Create audit log entry
        DataChangeLog.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=str(instance.pk),
            action='DELETE',
            field_name='deleted',
            old_value=json.dumps(old_values, cls=DjangoJSONEncoder)[:1000],
            new_value='',
            ip_address=AuditLoggingMiddleware()._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
    
    except Exception as e:
        # Don't break the application if audit logging fails
        print(f"Deletion logging failed: {e}")
