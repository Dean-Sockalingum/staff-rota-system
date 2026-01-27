"""
Database Query Optimization Utilities

Optimizations:
- Query prefetching (select_related, prefetch_related)
- Index recommendations
- Slow query detection
- N+1 query prevention

Usage:
    from scheduling.query_optimizer import optimize_shift_queries
    
    # Get optimized queryset
    shifts = optimize_shift_queries(base_queryset)
"""

from django.db import connection
from django.db.models import Prefetch, Count, Q
import time
import logging

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """
    Database query optimization helper
    """
    
    @staticmethod
    def optimize_shift_queries(queryset):
        """
        Optimize Shift queryset with proper prefetching
        
        Prevents N+1 queries for:
        - user (staff member)
        - unit
        - shift_type
        - care_home (through unit)
        
        Args:
            queryset: Base Shift queryset
        
        Returns: Optimized queryset
        """
        return queryset.select_related(
            'user',
            'user__role',
            'user__unit',
            'user__unit__care_home',
            'unit',
            'unit__care_home',
            'shift_type',
            'agency_company'
        )
    
    @staticmethod
    def optimize_leave_requests(queryset):
        """
        Optimize LeaveRequest queryset
        
        Args:
            queryset: Base LeaveRequest queryset
        
        Returns: Optimized queryset
        """
        return queryset.select_related(
            'user',
            'user__role',
            'user__unit',
            'approved_by',
            'denied_by'
        )
    
    @staticmethod
    def optimize_vacancy_report(care_home=None, start_date=None, end_date=None):
        """
        Optimized query for vacancy report
        
        Args:
            care_home: CareHome instance (optional)
            start_date: Start date for report
            end_date: End date for report
        
        Returns: Optimized Shift queryset
        """
        from scheduling.models import Shift
        
        queryset = Shift.objects.filter(
            user__isnull=True,  # Vacant shifts
            date__gte=start_date,
            date__lte=end_date
        )
        
        if care_home:
            queryset = queryset.filter(unit__care_home=care_home)
        
        return queryset.select_related(
            'unit',
            'unit__care_home',
            'shift_type'
        ).order_by('date', 'shift_type__start_time')
    
    @staticmethod
    def optimize_dashboard_queries(user):
        """
        Optimized queries for dashboard page
        
        Returns: Dict with all dashboard data in minimal queries
        """
        from scheduling.models import Shift, LeaveRequest, Unit
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        # Single query for vacant shifts (next 14 days)
        vacant_shifts = Shift.objects.filter(
            user__isnull=True,
            date__gte=today,
            date__lte=today + timedelta(days=14)
        ).select_related('unit', 'shift_type', 'unit__care_home')
        
        # Filter by user's care home if not senior management
        if user.unit and user.unit.care_home and not (user.role and user.role.is_senior_management_team):
            vacant_shifts = vacant_shifts.filter(unit__care_home=user.unit.care_home)
        
        vacant_shifts = list(vacant_shifts[:50])  # Limit to 50
        
        # Single query for upcoming leave
        upcoming_leave = LeaveRequest.objects.filter(
            start_date__lte=today + timedelta(days=14),
            end_date__gte=today,
            status='APPROVED'
        ).select_related('user', 'user__unit', 'user__role')
        
        if user.unit and user.unit.care_home and not (user.role and user.role.is_senior_management_team):
            upcoming_leave = upcoming_leave.filter(user__unit__care_home=user.unit.care_home)
        
        upcoming_leave = list(upcoming_leave[:50])
        
        # Single query for recent shifts
        recent_shifts = Shift.objects.filter(
            date__gte=today - timedelta(days=7),
            date__lte=today
        ).select_related('user', 'unit', 'shift_type', 'unit__care_home')
        
        if user.unit and user.unit.care_home and not (user.role and user.role.is_senior_management_team):
            recent_shifts = recent_shifts.filter(unit__care_home=user.unit.care_home)
        
        recent_shifts = list(recent_shifts[:100])
        
        return {
            'vacant_shifts': vacant_shifts,
            'upcoming_leave': upcoming_leave,
            'recent_shifts': recent_shifts
        }
    
    @staticmethod
    def detect_n_plus_one():
        """
        Detect N+1 query issues in recent queries
        
        Returns: List of potential N+1 issues
        """
        queries = connection.queries
        
        # Group similar queries
        query_patterns = {}
        for query in queries:
            # Simplify query to pattern
            sql = query['sql']
            # Remove specific IDs
            import re
            pattern = re.sub(r'\d+', 'N', sql)
            
            if pattern not in query_patterns:
                query_patterns[pattern] = []
            query_patterns[pattern].append(query)
        
        # Find patterns that repeat many times (potential N+1)
        n_plus_one_issues = []
        for pattern, queries in query_patterns.items():
            if len(queries) > 10:  # More than 10 similar queries
                n_plus_one_issues.append({
                    'pattern': pattern[:200],  # Truncate
                    'count': len(queries),
                    'total_time': sum(float(q.get('time', 0)) for q in queries)
                })
        
        return sorted(n_plus_one_issues, key=lambda x: x['count'], reverse=True)
    
    @staticmethod
    def recommend_indexes():
        """
        Analyze queries and recommend missing indexes
        
        Returns: List of index recommendations
        """
        from scheduling.models import Shift, User, Unit, LeaveRequest
        
        recommendations = []
        
        # Check if common query patterns have indexes
        
        # Shift queries by date range
        if not Shift._meta.get_field('date').db_index:
            recommendations.append({
                'model': 'Shift',
                'field': 'date',
                'reason': 'Frequently filtered by date range'
            })
        
        # Shift queries by user (for staff schedules)
        if not Shift._meta.get_field('user').db_index:
            recommendations.append({
                'model': 'Shift',
                'field': 'user',
                'reason': 'Frequently filtered by staff member'
            })
        
        # User queries by SAP number
        if not User._meta.get_field('sap').db_index:
            recommendations.append({
                'model': 'User',
                'field': 'sap',
                'reason': 'Primary lookup field for staff'
            })
        
        # LeaveRequest queries by status
        if not LeaveRequest._meta.get_field('status').db_index:
            recommendations.append({
                'model': 'LeaveRequest',
                'field': 'status',
                'reason': 'Frequently filtered by approval status'
            })
        
        # Composite indexes
        recommendations.append({
            'model': 'Shift',
            'fields': ['unit', 'date'],
            'reason': 'Frequently queried together for unit schedules'
        })
        
        recommendations.append({
            'model': 'Shift',
            'fields': ['date', 'user'],
            'reason': 'Frequently queried together for staff schedules'
        })
        
        return recommendations
    
    @staticmethod
    def profile_query(queryset, description="Query"):
        """
        Profile a queryset execution
        
        Args:
            queryset: Django queryset to profile
            description: Description of query
        
        Returns: Dict with profiling results
        """
        # Clear previous queries
        connection.queries_log.clear()
        
        # Execute query
        start_time = time.time()
        result = list(queryset)
        elapsed = time.time() - start_time
        
        # Get query count
        query_count = len(connection.queries)
        
        logger.info(f"{description}: {elapsed:.3f}s, {query_count} queries, {len(result)} results")
        
        return {
            'description': description,
            'time_seconds': elapsed,
            'query_count': query_count,
            'result_count': len(result)
        }


def create_performance_indexes():
    """
    Generate SQL for creating recommended performance indexes
    
    Returns: List of SQL statements
    """
    sql_statements = [
        # Shift indexes
        "CREATE INDEX IF NOT EXISTS idx_shift_date ON scheduling_shift(date);",
        "CREATE INDEX IF NOT EXISTS idx_shift_user ON scheduling_shift(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_shift_unit_date ON scheduling_shift(unit_id, date);",
        "CREATE INDEX IF NOT EXISTS idx_shift_date_user ON scheduling_shift(date, user_id);",
        "CREATE INDEX IF NOT EXISTS idx_shift_vacant ON scheduling_shift(date) WHERE user_id IS NULL;",
        
        # LeaveRequest indexes
        "CREATE INDEX IF NOT EXISTS idx_leave_status ON scheduling_leaverequest(status);",
        "CREATE INDEX IF NOT EXISTS idx_leave_dates ON scheduling_leaverequest(start_date, end_date);",
        "CREATE INDEX IF NOT EXISTS idx_leave_user ON scheduling_leaverequest(user_id);",
        
        # User indexes
        "CREATE INDEX IF NOT EXISTS idx_user_sap ON scheduling_user(sap);",
        "CREATE INDEX IF NOT EXISTS idx_user_active ON scheduling_user(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_user_unit ON scheduling_user(unit_id);",
        
        # ProphetModelMetrics indexes
        "CREATE INDEX IF NOT EXISTS idx_prophet_date ON scheduling_prophet_model_metrics(forecast_date);",
        "CREATE INDEX IF NOT EXISTS idx_prophet_unit_date ON scheduling_prophet_model_metrics(unit_id, forecast_date);",
    ]
    
    return sql_statements


def apply_performance_indexes():
    """
    Apply performance indexes to database
    
    WARNING: Run during low-traffic period
    """
    from django.db import connection
    
    sql_statements = create_performance_indexes()
    
    with connection.cursor() as cursor:
        for sql in sql_statements:
            try:
                cursor.execute(sql)
                logger.info(f"Applied: {sql[:80]}...")
            except Exception as e:
                logger.error(f"Failed to apply index: {e}")
    
    logger.info(f"Applied {len(sql_statements)} performance indexes")
