"""
Cache Performance Monitoring Views
Task 44: Performance monitoring dashboard
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from scheduling.cache_service import CacheService
from django.core.cache import cache


@staff_member_required
def cache_stats_view(request):
    """
    Display cache performance statistics
    """
    stats = CacheService.get_cache_stats()
    
    context = {
        'stats': stats,
        'cache_backend': cache.__class__.__name__,
    }
    
    return render(request, 'scheduling/cache_stats.html', context)


@staff_member_required
def clear_cache_view(request):
    """
    Clear all application caches
    """
    if request.method == 'POST':
        pattern = request.POST.get('pattern')
        
        if pattern:
            CacheService.invalidate_pattern(pattern)
            message = f"Cleared caches matching pattern: {pattern}"
        else:
            cache.clear()
            message = "Cleared all caches"
        
        return JsonResponse({
            'status': 'success',
            'message': message,
            'stats': CacheService.get_cache_stats()
        })
    
    return JsonResponse({'status': 'error', 'message': 'POST required'})


@staff_member_required
def warm_cache_view(request):
    """
    Warm up caches manually
    """
    if request.method == 'POST':
        home_id = request.POST.get('home_id')
        
        CacheService.warm_dashboard_cache(
            home_id=int(home_id) if home_id else None
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Cache warming completed',
            'stats': CacheService.get_cache_stats()
        })
    
    return JsonResponse({'status': 'error', 'message': 'POST required'})
