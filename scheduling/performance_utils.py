"""
Performance Optimization Utilities
Provides optimized database query helpers and caching utilities
"""

from django.core.cache import cache
from django.db.models import Prefetch, Q
from functools import wraps
from typing import Any, Callable
import hashlib
import json


def cache_query(timeout: int = 300, key_prefix: str = ''):
    """
    Decorator to cache database query results
    
    Args:
        timeout: Cache timeout in seconds (default 5 minutes)
        key_prefix: Prefix for cache key (optional)
    
    Usage:
        @cache_query(timeout=600, key_prefix='shifts')
        def get_shifts_for_week(start_date, home_id):
            return Shift.objects.filter(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            
            # Add args to cache key
            for arg in args:
                if hasattr(arg, 'id'):  # Model instance
                    key_parts.append(f'{type(arg).__name__}_{arg.id}')
                else:
                    key_parts.append(str(arg))
            
            # Add kwargs to cache key
            for k, v in sorted(kwargs.items()):
                if hasattr(v, 'id'):  # Model instance
                    key_parts.append(f'{k}_{type(v).__name__}_{v.id}')
                else:
                    key_parts.append(f'{k}_{v}')
            
            cache_key = '_'.join(key_parts)
            
            # Check cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def get_optimized_shift_queryset():
    """
    Returns an optimized Shift queryset with all related data prefetched
    Reduces N+1 queries when iterating over shifts
    """
    from .models import Shift
    
    return Shift.objects.select_related(
        'user',
        'user__role',
        'user__unit',
        'user__home_unit',
        'unit',
        'shift_type',
        'assigned_by'
    )


def get_optimized_user_queryset():
    """
    Returns an optimized User queryset with all related data prefetched
    Reduces N+1 queries when displaying staff lists
    """
    from .models import User
    from staff_records.models import StaffProfile
    
    return User.objects.select_related(
        'role',
        'unit',
        'home_unit',
        'manager'
    ).prefetch_related(
        'supervised_staff'
    )


def get_shifts_with_staff(date_start, date_end, home=None, unit=None):
    """
    Optimized query for shifts with full staff details
    
    Args:
        date_start: Start date for shift range
        date_end: End date for shift range
        home: Optional CareHome to filter by
        unit: Optional Unit to filter by
    
    Returns:
        Optimized queryset with all relations prefetched
    """
    from .models import Shift
    
    queryset = get_optimized_shift_queryset().filter(
        date__gte=date_start,
        date__lte=date_end
    )
    
    if home:
        queryset = queryset.filter(unit__care_home=home)
    
    if unit:
        queryset = queryset.filter(unit=unit)
    
    return queryset.order_by('date', 'shift_type__start_time')


@cache_query(timeout=3600, key_prefix='home_data')
def get_cached_care_homes():
    """
    Returns all care homes with caching (1 hour)
    Care homes rarely change, so aggressive caching is safe
    """
    from .models_multi_home import CareHome
    
    return list(CareHome.objects.all().order_by('name'))


@cache_query(timeout=3600, key_prefix='roles')
def get_cached_roles():
    """
    Returns all roles with caching (1 hour)
    Roles rarely change, so aggressive caching is safe
    """
    from .models import Role
    
    return list(Role.objects.all().order_by('name'))


@cache_query(timeout=900, key_prefix='shift_types')
def get_cached_shift_types():
    """
    Returns all shift types with caching (15 minutes)
    Shift types occasionally change, moderate caching
    """
    from .models import ShiftType
    
    return list(ShiftType.objects.all().order_by('name'))


def invalidate_shift_cache(home_id=None, unit_id=None, date=None):
    """
    Invalidates shift-related cache keys
    Call this when shifts are created/updated/deleted
    
    Args:
        home_id: CareHome ID to invalidate
        unit_id: Unit ID to invalidate  
        date: Date to invalidate
    """
    patterns = ['shifts_*']
    
    if home_id:
        patterns.append(f'*_home_{home_id}_*')
    if unit_id:
        patterns.append(f'*_unit_{unit_id}_*')
    if date:
        patterns.append(f'*_{date}_*')
    
    # Django cache doesn't support pattern deletion in all backends
    # For production with Redis, use cache.delete_pattern()
    # For now, we'll use cache versioning approach
    cache.clear()  # Simple approach - clears all cache


def get_staff_dashboard_data(user, use_cache=True):
    """
    Optimized data retrieval for staff dashboard
    
    Args:
        user: User instance
        use_cache: Whether to use caching (default True)
    
    Returns:
        Dictionary with all dashboard data
    """
    from .models import Shift
    from datetime import date, timedelta
    
    cache_key = f'staff_dashboard_{user.id}_{date.today()}'
    
    if use_cache:
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Optimized query with select_related
    user_shifts = get_optimized_shift_queryset().filter(
        user=user,
        date__gte=week_start,
        date__lte=week_end
    ).order_by('date')
    
    data = {
        'upcoming_shifts': list(user_shifts),
        'total_hours': sum(s.shift_type.hours for s in user_shifts if s.shift_type),
        'shifts_this_week': user_shifts.count(),
    }
    
    if use_cache:
        cache.set(cache_key, data, 300)  # 5 minutes
    
    return data


def get_manager_dashboard_data(home, date_range_start, date_range_end, use_cache=True):
    """
    Optimized data retrieval for manager dashboard
    
    Args:
        home: CareHome instance
        date_range_start: Start date
        date_range_end: End date
        use_cache: Whether to use caching (default True)
    
    Returns:
        Dictionary with all dashboard data
    """
    from .models import Shift, User
    from django.db.models import Count
    
    cache_key = f'mgr_dashboard_{home.id}_{date_range_start}_{date_range_end}'
    
    if use_cache:
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
    
    # Optimized queries
    shifts = get_optimized_shift_queryset().filter(
        unit__care_home=home,
        date__gte=date_range_start,
        date__lte=date_range_end
    )
    
    staff = get_optimized_user_queryset().filter(
        home_unit__care_home=home,
        is_active=True
    )
    
    data = {
        'total_shifts': shifts.count(),
        'unfilled_shifts': shifts.filter(user__isnull=True).count(),
        'total_staff': staff.count(),
        'shifts_by_type': list(shifts.values('shift_type__name').annotate(count=Count('id'))),
    }
    
    if use_cache:
        cache.set(cache_key, data, 300)  # 5 minutes
    
    return data


class QueryOptimizer:
    """
    Context manager to monitor and log query performance
    
    Usage:
        with QueryOptimizer('manager_dashboard'):
            # Your database queries here
            shifts = Shift.objects.filter(...)
    """
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_queries = 0
        
    def __enter__(self):
        from django.db import connection
        self.start_queries = len(connection.queries)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        from django.db import connection, reset_queries
        from django.conf import settings
        
        if settings.DEBUG:
            end_queries = len(connection.queries)
            num_queries = end_queries - self.start_queries
            
            if num_queries > 10:
                print(f"⚠️  {self.operation_name}: {num_queries} queries executed")
                print("Consider using select_related() or prefetch_related()")
            elif num_queries > 5:
                print(f"ℹ️  {self.operation_name}: {num_queries} queries")
            else:
                print(f"✓ {self.operation_name}: {num_queries} queries (optimized)")
