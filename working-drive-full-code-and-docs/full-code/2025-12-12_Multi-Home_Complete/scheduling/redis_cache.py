"""
Redis Caching for Staff Rota System

Caches:
- Prophet forecast results (24h TTL)
- Dashboard vacancy reports (5min TTL)
- Staffing coverage calculations (15min TTL)
- User session data

Usage:
    from scheduling.redis_cache import cache_forecast, get_cached_forecast
    
    # Cache forecast
    cache_forecast(care_home, unit, forecast_date, forecast_data)
    
    # Retrieve cached forecast
    forecast = get_cached_forecast(care_home, unit, forecast_date)
"""

import json
import hashlib
from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# Cache TTL settings (in seconds)
FORECAST_TTL = 24 * 60 * 60  # 24 hours
DASHBOARD_TTL = 5 * 60        # 5 minutes
COVERAGE_TTL = 15 * 60        # 15 minutes
SESSION_TTL = 60 * 60         # 1 hour


def generate_cache_key(prefix, *args):
    """
    Generate consistent cache key from arguments
    
    Args:
        prefix: Cache key prefix (e.g., 'forecast', 'dashboard')
        *args: Variable arguments to include in key
    
    Returns: Cache key string
    """
    # Convert args to strings and hash
    key_parts = [str(arg) for arg in args]
    key_string = ":".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()[:12]
    
    return f"rota:{prefix}:{key_hash}"


def cache_forecast(care_home, unit, forecast_date, forecast_data, ttl=FORECAST_TTL):
    """
    Cache Prophet forecast results
    
    Args:
        care_home: CareHome instance or name
        unit: Unit instance or name
        forecast_date: Date of forecast
        forecast_data: Dict with forecast results
        ttl: Time to live in seconds (default: 24h)
    
    Returns: Cache key
    """
    cache_key = generate_cache_key(
        'forecast',
        getattr(care_home, 'name', care_home),
        getattr(unit, 'name', unit),
        forecast_date
    )
    
    try:
        cache.set(cache_key, forecast_data, ttl)
        logger.debug(f"Cached forecast: {cache_key}")
        return cache_key
    except Exception as e:
        logger.error(f"Failed to cache forecast: {e}")
        return None


def get_cached_forecast(care_home, unit, forecast_date):
    """
    Retrieve cached forecast
    
    Args:
        care_home: CareHome instance or name
        unit: Unit instance or name
        forecast_date: Date of forecast
    
    Returns: Forecast data dict or None if not cached
    """
    cache_key = generate_cache_key(
        'forecast',
        getattr(care_home, 'name', care_home),
        getattr(unit, 'name', unit),
        forecast_date
    )
    
    try:
        data = cache.get(cache_key)
        if data:
            logger.debug(f"Cache hit: {cache_key}")
        else:
            logger.debug(f"Cache miss: {cache_key}")
        return data
    except Exception as e:
        logger.error(f"Failed to retrieve cached forecast: {e}")
        return None


def invalidate_forecast_cache(care_home, unit, forecast_date=None):
    """
    Invalidate cached forecasts
    
    Args:
        care_home: CareHome instance or name
        unit: Unit instance or name
        forecast_date: Specific date to invalidate, or None for all
    """
    if forecast_date:
        # Invalidate specific date
        cache_key = generate_cache_key(
            'forecast',
            getattr(care_home, 'name', care_home),
            getattr(unit, 'name', unit),
            forecast_date
        )
        cache.delete(cache_key)
        logger.info(f"Invalidated forecast cache: {cache_key}")
    else:
        # Invalidate all forecasts for this unit (requires pattern matching)
        # Note: Django's default cache backend doesn't support pattern deletion
        # Consider using Redis backend for this feature
        logger.warning("Full cache invalidation requires Redis backend")


def cache_dashboard_data(user, data, ttl=DASHBOARD_TTL):
    """
    Cache dashboard data for user
    
    Args:
        user: User instance
        data: Dashboard data dict
        ttl: Time to live in seconds (default: 5min)
    
    Returns: Cache key
    """
    cache_key = generate_cache_key('dashboard', user.sap, timezone.now().date())
    
    try:
        cache.set(cache_key, data, ttl)
        logger.debug(f"Cached dashboard: {cache_key}")
        return cache_key
    except Exception as e:
        logger.error(f"Failed to cache dashboard: {e}")
        return None


def get_cached_dashboard(user):
    """
    Retrieve cached dashboard data
    
    Args:
        user: User instance
    
    Returns: Dashboard data dict or None
    """
    cache_key = generate_cache_key('dashboard', user.sap, timezone.now().date())
    
    try:
        data = cache.get(cache_key)
        if data:
            logger.debug(f"Dashboard cache hit for {user.sap}")
        return data
    except Exception as e:
        logger.error(f"Failed to retrieve cached dashboard: {e}")
        return None


def cache_vacancy_report(care_home, start_date, end_date, data, ttl=DASHBOARD_TTL):
    """
    Cache vacancy report
    
    Args:
        care_home: CareHome instance or name
        start_date: Report start date
        end_date: Report end date
        data: Vacancy data dict
        ttl: Time to live in seconds (default: 5min)
    
    Returns: Cache key
    """
    cache_key = generate_cache_key(
        'vacancy',
        getattr(care_home, 'name', care_home),
        start_date,
        end_date
    )
    
    try:
        cache.set(cache_key, data, ttl)
        logger.debug(f"Cached vacancy report: {cache_key}")
        return cache_key
    except Exception as e:
        logger.error(f"Failed to cache vacancy report: {e}")
        return None


def get_cached_vacancy_report(care_home, start_date, end_date):
    """
    Retrieve cached vacancy report
    
    Args:
        care_home: CareHome instance or name
        start_date: Report start date
        end_date: Report end date
    
    Returns: Vacancy data dict or None
    """
    cache_key = generate_cache_key(
        'vacancy',
        getattr(care_home, 'name', care_home),
        start_date,
        end_date
    )
    
    try:
        data = cache.get(cache_key)
        if data:
            logger.debug(f"Vacancy cache hit")
        return data
    except Exception as e:
        logger.error(f"Failed to retrieve cached vacancy: {e}")
        return None


def cache_staffing_coverage(unit, date, data, ttl=COVERAGE_TTL):
    """
    Cache staffing coverage calculation
    
    Args:
        unit: Unit instance or name
        date: Date of coverage
        data: Coverage data dict
        ttl: Time to live in seconds (default: 15min)
    
    Returns: Cache key
    """
    cache_key = generate_cache_key(
        'coverage',
        getattr(unit, 'name', unit),
        date
    )
    
    try:
        cache.set(cache_key, data, ttl)
        logger.debug(f"Cached coverage: {cache_key}")
        return cache_key
    except Exception as e:
        logger.error(f"Failed to cache coverage: {e}")
        return None


def get_cached_coverage(unit, date):
    """
    Retrieve cached staffing coverage
    
    Args:
        unit: Unit instance or name
        date: Date of coverage
    
    Returns: Coverage data dict or None
    """
    cache_key = generate_cache_key(
        'coverage',
        getattr(unit, 'name', unit),
        date
    )
    
    try:
        data = cache.get(cache_key)
        if data:
            logger.debug(f"Coverage cache hit")
        return data
    except Exception as e:
        logger.error(f"Failed to retrieve cached coverage: {e}")
        return None


def clear_all_cache():
    """
    Clear entire cache
    
    Use with caution in production!
    """
    try:
        cache.clear()
        logger.warning("Cleared entire cache")
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")


def get_cache_stats():
    """
    Get cache statistics (Redis backend only)
    
    Returns: Dict with cache stats or None
    """
    try:
        # This requires django-redis backend
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()
        
        return {
            'used_memory_mb': info['used_memory'] / 1024 / 1024,
            'total_keys': redis_conn.dbsize(),
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0),
            'hit_rate': info.get('keyspace_hits', 0) / (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1))
        }
    except Exception as e:
        logger.debug(f"Cache stats not available: {e}")
        return None


# Decorator for caching function results
def cached(ttl=300, key_prefix='func'):
    """
    Decorator to cache function results
    
    Usage:
        @cached(ttl=600, key_prefix='my_function')
        def my_expensive_function(arg1, arg2):
            return result
    
    Args:
        ttl: Time to live in seconds (default: 5min)
        key_prefix: Prefix for cache key
    
    Returns: Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = generate_cache_key(
                key_prefix,
                func.__name__,
                *args,
                *kwargs.values()
            )
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit: {func.__name__}")
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result: {func.__name__}")
            
            return result
        
        return wrapper
    return decorator
