"""
Cache Invalidation Middleware
Task 44: Automatic cache invalidation on data changes
"""

from django.utils.deprecation import MiddlewareMixin
from scheduling.cache_service import CacheService
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from scheduling.models import Shift, Staff, LeaveRequest, CareHome


class CacheInvalidationMiddleware(MiddlewareMixin):
    """
    Middleware to handle cache invalidation
    """
    
    def process_response(self, request, response):
        # Invalidate cache on POST/PUT/DELETE requests
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Get home_id from request if available
            home_id = request.POST.get('home') or request.GET.get('home')
            
            if home_id:
                try:
                    CacheService.invalidate_home_cache(int(home_id))
                except (ValueError, TypeError):
                    pass
        
        return response


# Signal-based cache invalidation
@receiver(post_save, sender=Shift)
@receiver(post_delete, sender=Shift)
def invalidate_shift_cache(sender, instance, **kwargs):
    """Invalidate caches when shifts are modified"""
    CacheService.invalidate_shift_cache(
        shift_id=instance.id,
        home_id=instance.home_id if instance.home_id else None,
        date=instance.date
    )
    
    # Also invalidate home cache
    if instance.home_id:
        CacheService.invalidate_home_cache(instance.home_id)


@receiver(post_save, sender=Staff)
@receiver(post_delete, sender=Staff)
def invalidate_staff_cache(sender, instance, **kwargs):
    """Invalidate caches when staff records are modified"""
    if instance.home_id:
        CacheService.invalidate_home_cache(instance.home_id)


@receiver(post_save, sender=LeaveRequest)
@receiver(post_delete, sender=LeaveRequest)
def invalidate_leave_cache(sender, instance, **kwargs):
    """Invalidate caches when leave requests are modified"""
    if hasattr(instance, 'staff') and instance.staff and instance.staff.home_id:
        CacheService.invalidate_home_cache(instance.staff.home_id)


@receiver(post_save, sender=CareHome)
def invalidate_home_metadata_cache(sender, instance, **kwargs):
    """Invalidate caches when home metadata changes"""
    CacheService.invalidate_home_cache(instance.id)
