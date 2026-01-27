"""
Performance Optimization & Caching Service
Task 44: Comprehensive caching layer for improved performance

Features:
- Redis caching with automatic invalidation
- Query result caching
- Template fragment caching
- Decorators for easy cache application
- Cache warming utilities
- Performance monitoring
"""

from django.core.cache import cache
from django.db.models import QuerySet
from functools import wraps
from typing import Any, Callable, Optional
import hashlib
import json
from datetime import timedelta


class CacheService:
    """
    Centralized caching service for performance optimization
    """
    
    # Cache timeout durations (in seconds)
    TIMEOUT_SHORT = 300  # 5 minutes
    TIMEOUT_MEDIUM = 900  # 15 minutes
    TIMEOUT_LONG = 3600  # 1 hour
    TIMEOUT_DAY = 86400  # 24 hours
    
    # Cache key prefixes
    PREFIX_DASHBOARD = "dashboard"
    PREFIX_STATS = "stats"
    PREFIX_SHIFT = "shift"
    PREFIX_STAFF = "staff"
    PREFIX_REPORT = "report"
    PREFIX_COMPLIANCE = "compliance"
    
    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """
        Generate a unique cache key from arguments
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Unique cache key string
        """
        # Convert args and kwargs to a string representation
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        
        # Create hash for consistent key length
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @staticmethod
    def cache_result(timeout: int = TIMEOUT_MEDIUM, key_prefix: str = ""):
        """
        Decorator to cache function results
        
        Usage:
            @CacheService.cache_result(timeout=300, key_prefix="dashboard")
            def get_dashboard_stats(home_id):
                # expensive operation
                return stats
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{func.__name__}:{CacheService.generate_cache_key(*args, **kwargs)}"
                
                # Try to get from cache
                result = cache.get(cache_key)
                
                if result is None:
                    # Cache miss - execute function
                    result = func(*args, **kwargs)
                    
                    # Store in cache
                    cache.set(cache_key, result, timeout)
                
                return result
            
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_pattern(pattern: str):
        """
        Invalidate all cache keys matching a pattern
        
        Args:
            pattern: Cache key pattern (e.g., "dashboard:*")
        """
        # Note: This requires Redis backend
        try:
            from django_redis import get_redis_connection
            conn = get_redis_connection("default")
            
            # Find all keys matching pattern
            keys = conn.keys(pattern)
            
            if keys:
                conn.delete(*keys)
                
        except Exception as e:
            # Fallback if Redis not available
            cache.clear()
    
    @staticmethod
    def warm_dashboard_cache(home_id: Optional[int] = None):
        """
        Pre-populate dashboard caches for faster load times
        
        Args:
            home_id: Specific home to warm cache for (None = all homes)
        """
        from scheduling.models import CareHome, Shift
        from django.utils import timezone
        from datetime import timedelta
        
        homes = [CareHome.objects.get(id=home_id)] if home_id else CareHome.objects.all()
        today = timezone.now().date()
        
        for home in homes:
            # Warm shift count caches
            for days_ahead in [7, 14, 30]:
                end_date = today + timedelta(days=days_ahead)
                
                cache_key = f"{CacheService.PREFIX_SHIFT}:count:{home.id}:{today}:{end_date}"
                count = Shift.objects.filter(
                    home=home,
                    date__gte=today,
                    date__lte=end_date
                ).count()
                cache.set(cache_key, count, CacheService.TIMEOUT_MEDIUM)
    
    @staticmethod
    def get_or_cache_queryset(cache_key: str, queryset_func: Callable, timeout: int = TIMEOUT_MEDIUM) -> Any:
        """
        Get result from cache or execute queryset function
        
        Args:
            cache_key: Cache key to use
            queryset_func: Function that returns queryset/data
            timeout: Cache timeout in seconds
            
        Returns:
            Cached or fresh data
        """
        result = cache.get(cache_key)
        
        if result is None:
            result = queryset_func()
            
            # Convert QuerySet to list for caching
            if isinstance(result, QuerySet):
                result = list(result)
            
            cache.set(cache_key, result, timeout)
        
        return result
    
    @staticmethod
    def invalidate_home_cache(home_id: int):
        """
        Invalidate all caches related to a specific home
        
        Args:
            home_id: ID of the care home
        """
        patterns = [
            f"{CacheService.PREFIX_DASHBOARD}:*:{home_id}:*",
            f"{CacheService.PREFIX_STATS}:*:{home_id}:*",
            f"{CacheService.PREFIX_SHIFT}:*:{home_id}:*",
            f"{CacheService.PREFIX_COMPLIANCE}:*:{home_id}:*",
        ]
        
        for pattern in patterns:
            CacheService.invalidate_pattern(pattern)
    
    @staticmethod
    def invalidate_shift_cache(shift_id: int = None, home_id: int = None, date = None):
        """
        Invalidate shift-related caches
        
        Args:
            shift_id: Specific shift ID
            home_id: Home ID for bulk invalidation
            date: Date for date-specific invalidation
        """
        if shift_id:
            CacheService.invalidate_pattern(f"{CacheService.PREFIX_SHIFT}:*:{shift_id}:*")
        
        if home_id:
            CacheService.invalidate_pattern(f"{CacheService.PREFIX_SHIFT}:*:{home_id}:*")
        
        if date:
            CacheService.invalidate_pattern(f"{CacheService.PREFIX_SHIFT}:*:{date}:*")
    
    @staticmethod
    def get_cache_stats() -> dict:
        """
        Get cache performance statistics
        
        Returns:
            Dictionary with cache stats
        """
        try:
            from django_redis import get_redis_connection
            conn = get_redis_connection("default")
            
            info = conn.info()
            
            return {
                'total_keys': conn.dbsize(),
                'used_memory': info.get('used_memory_human', 'N/A'),
                'hit_rate': info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0)),
                'connected_clients': info.get('connected_clients', 0),
                'uptime_days': info.get('uptime_in_days', 0),
            }
        except:
            return {
                'total_keys': 0,
                'used_memory': 'N/A',
                'hit_rate': 0.0,
                'connected_clients': 0,
                'uptime_days': 0,
            }


class QueryOptimizer:
    """
    Query optimization utilities to prevent N+1 queries
    """
    
    @staticmethod
    def optimize_shift_queryset(queryset: QuerySet) -> QuerySet:
        """
        Optimize shift queryset with proper select_related and prefetch_related
        
        Args:
            queryset: Base Shift queryset
            
        Returns:
            Optimized queryset
        """
        return queryset.select_related(
            'home',
            'unit',
            'staff',
            'shift_type',
            'created_by',
            'updated_by'
        ).prefetch_related(
            'notes',
            'related_shifts'
        )
    
    @staticmethod
    def optimize_staff_queryset(queryset: QuerySet) -> QuerySet:
        """
        Optimize staff queryset
        
        Args:
            queryset: Base Staff queryset
            
        Returns:
            Optimized queryset
        """
        return queryset.select_related(
            'user',
            'home',
            'primary_unit'
        ).prefetch_related(
            'qualified_units',
            'certifications',
            'leave_requests'
        )
    
    @staticmethod
    def optimize_leave_queryset(queryset: QuerySet) -> QuerySet:
        """
        Optimize leave request queryset
        
        Args:
            queryset: Base LeaveRequest queryset
            
        Returns:
            Optimized queryset
        """
        return queryset.select_related(
            'staff',
            'staff__user',
            'staff__home',
            'approved_by',
            'leave_type'
        )
    
    @staticmethod
    def batch_load_shifts(shift_ids: list) -> dict:
        """
        Batch load shifts by IDs to avoid multiple queries
        
        Args:
            shift_ids: List of shift IDs
            
        Returns:
            Dictionary mapping shift_id to shift object
        """
        from scheduling.models import Shift
        
        shifts = QueryOptimizer.optimize_shift_queryset(
            Shift.objects.filter(id__in=shift_ids)
        )
        
        return {shift.id: shift for shift in shifts}


# Convenience decorators
def cache_dashboard(timeout: int = CacheService.TIMEOUT_MEDIUM):
    """Decorator for caching dashboard data"""
    return CacheService.cache_result(timeout=timeout, key_prefix=CacheService.PREFIX_DASHBOARD)


def cache_stats(timeout: int = CacheService.TIMEOUT_LONG):
    """Decorator for caching statistics"""
    return CacheService.cache_result(timeout=timeout, key_prefix=CacheService.PREFIX_STATS)


def cache_report(timeout: int = CacheService.TIMEOUT_DAY):
    """Decorator for caching reports"""
    return CacheService.cache_result(timeout=timeout, key_prefix=CacheService.PREFIX_REPORT)
