"""
Performance Benchmarking for Staff Rota System

Tests:
1. LP Solver Performance (CBC vs GLPK vs Gurobi)
2. Prophet Training Time
3. Database Query Performance
4. Dashboard Load Times
5. Concurrent User Load

Usage:
    python manage.py shell
    >>> from scheduling.performance_benchmarks import run_all_benchmarks
    >>> run_all_benchmarks()
"""

import time
import psutil
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import connection
from django.test.utils import override_settings
import logging

logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """
    Comprehensive performance benchmarking suite
    """
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.memory_start = None
    
    def start_timer(self):
        """Start timing a benchmark"""
        self.start_time = time.time()
        self.memory_start = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    def stop_timer(self, benchmark_name):
        """Stop timing and record results"""
        elapsed = time.time() - self.start_time
        memory_end = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_end - self.memory_start
        
        self.results[benchmark_name] = {
            'time_seconds': round(elapsed, 3),
            'memory_mb': round(memory_used, 2)
        }
        
        logger.info(f"{benchmark_name}: {elapsed:.3f}s, {memory_used:.2f}MB")
        return elapsed
    
    def benchmark_lp_solvers(self, care_home_name='ORCHARD_GROVE', unit_name='OG_MULBERRY'):
        """
        Benchmark different LP solvers for shift optimization
        
        Tests: CBC (default), GLPK, COIN_CMD
        
        Returns: Dict with solver performance metrics
        """
        from scheduling.models import CareHome, Unit, ShiftType, Role, User
        from scheduling.shift_optimizer import ShiftOptimizer
        from datetime import date
        
        print("\n=== LP Solver Benchmark ===")
        
        # Get test data
        try:
            care_home = CareHome.objects.get(name=care_home_name)
            unit = Unit.objects.get(name=unit_name, care_home=care_home)
        except:
            print("Error: Test care home/unit not found")
            return {}
        
        test_date = date.today()
        solver_results = {}
        
        # Test each solver
        for solver_name in ['PULP_CBC_CMD', 'GLPK_CMD', 'COIN_CMD']:
            try:
                print(f"\nTesting {solver_name}...")
                self.start_timer()
                
                optimizer = ShiftOptimizer(
                    care_home=care_home,
                    unit=unit,
                    date=test_date,
                    solver=solver_name
                )
                
                solution = optimizer.optimize()
                
                elapsed = self.stop_timer(f"LP_Solver_{solver_name}")
                
                solver_results[solver_name] = {
                    'time_seconds': elapsed,
                    'status': solution.get('status'),
                    'total_cost': solution.get('total_cost', 0),
                    'shifts_created': len(solution.get('shifts', []))
                }
                
                print(f"  ✓ Status: {solution.get('status')}")
                print(f"  ✓ Time: {elapsed:.3f}s")
                print(f"  ✓ Cost: £{solution.get('total_cost', 0):.2f}")
                
            except Exception as e:
                print(f"  ✗ {solver_name} failed: {e}")
                solver_results[solver_name] = {'error': str(e)}
        
        # Determine fastest solver
        valid_solvers = {k: v for k, v in solver_results.items() if 'error' not in v}
        if valid_solvers:
            fastest = min(valid_solvers.items(), key=lambda x: x[1]['time_seconds'])
            print(f"\n🏆 Fastest solver: {fastest[0]} ({fastest[1]['time_seconds']:.3f}s)")
        
        return solver_results
    
    def benchmark_prophet_training(self, parallel=False):
        """
        Benchmark Prophet model training time
        
        Args:
            parallel: Test parallel training across multiple units
        
        Returns: Training time metrics
        """
        from scheduling.models import Unit
        from scheduling.ml_forecasting import train_prophet_model
        import concurrent.futures
        
        print("\n=== Prophet Training Benchmark ===")
        
        units = Unit.objects.filter(is_active=True)[:5]  # Test on 5 units
        
        if not parallel:
            # Sequential training
            print(f"Sequential training for {units.count()} units...")
            self.start_timer()
            
            for unit in units:
                train_prophet_model(unit, days_history=365)
            
            elapsed = self.stop_timer("Prophet_Sequential")
            print(f"  ✓ Total time: {elapsed:.2f}s")
            print(f"  ✓ Avg per unit: {elapsed/units.count():.2f}s")
            
            return {'sequential': elapsed, 'avg_per_unit': elapsed/units.count()}
        
        else:
            # Parallel training
            print(f"Parallel training for {units.count()} units...")
            self.start_timer()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(train_prophet_model, unit, 365)
                    for unit in units
                ]
                concurrent.futures.wait(futures)
            
            elapsed = self.stop_timer("Prophet_Parallel")
            print(f"  ✓ Total time: {elapsed:.2f}s")
            print(f"  ✓ Speedup: {self.results.get('Prophet_Sequential', {}).get('time_seconds', 0) / elapsed:.2f}x")
            
            return {'parallel': elapsed, 'speedup': elapsed}
    
    def benchmark_database_queries(self):
        """
        Benchmark critical database queries
        
        Tests:
        - Dashboard vacancy report
        - Shift retrieval with/without select_related
        - Staffing coverage calculation
        
        Returns: Query performance metrics
        """
        from scheduling.models import Shift, Unit, User
        from django.db.models import Count, Prefetch
        
        print("\n=== Database Query Benchmark ===")
        
        results = {}
        
        # Test 1: Shift retrieval without optimization
        print("\nTest 1: Shift retrieval (no optimization)...")
        self.start_timer()
        
        shifts = Shift.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=7)
        )[:100]
        
        # Force evaluation
        for shift in shifts:
            _ = shift.user.first_name  # Triggers N+1 queries
            _ = shift.unit.name
            _ = shift.shift_type.name
        
        time_unoptimized = self.stop_timer("Query_Unoptimized")
        query_count_unoptimized = len(connection.queries)
        
        print(f"  ✓ Time: {time_unoptimized:.3f}s")
        print(f"  ✓ Queries: {query_count_unoptimized}")
        
        # Reset query log
        connection.queries_log.clear()
        
        # Test 2: Optimized with select_related
        print("\nTest 2: Shift retrieval (with select_related)...")
        self.start_timer()
        
        shifts = Shift.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=7)
        ).select_related('user', 'unit', 'shift_type', 'unit__care_home')[:100]
        
        for shift in shifts:
            _ = shift.user.first_name
            _ = shift.unit.name
            _ = shift.shift_type.name
        
        time_optimized = self.stop_timer("Query_Optimized")
        query_count_optimized = len(connection.queries)
        
        print(f"  ✓ Time: {time_optimized:.3f}s")
        print(f"  ✓ Queries: {query_count_optimized}")
        print(f"  ✓ Speedup: {time_unoptimized/time_optimized:.2f}x")
        print(f"  ✓ Query reduction: {query_count_unoptimized - query_count_optimized}")
        
        results['unoptimized'] = {'time': time_unoptimized, 'queries': query_count_unoptimized}
        results['optimized'] = {'time': time_optimized, 'queries': query_count_optimized}
        
        return results
    
    def benchmark_dashboard_load(self):
        """
        Benchmark dashboard page load time
        
        Simulates full dashboard data retrieval
        
        Returns: Load time metrics
        """
        from scheduling.models import Shift, Unit, User, LeaveRequest
        
        print("\n=== Dashboard Load Benchmark ===")
        
        self.start_timer()
        
        # Simulate dashboard queries
        today = timezone.now().date()
        
        # Vacancy report
        vacant_shifts = Shift.objects.filter(
            date__gte=today,
            date__lte=today + timedelta(days=14),
            user__isnull=True
        ).select_related('unit', 'shift_type').count()
        
        # Upcoming leave
        upcoming_leave = LeaveRequest.objects.filter(
            start_date__lte=today + timedelta(days=14),
            end_date__gte=today,
            status='APPROVED'
        ).select_related('user', 'user__unit').count()
        
        # Active staff
        active_staff = User.objects.filter(is_active=True).count()
        
        # Recent shifts
        recent_shifts = Shift.objects.filter(
            date__gte=today - timedelta(days=7),
            date__lte=today
        ).select_related('user', 'unit', 'shift_type')[:50]
        
        elapsed = self.stop_timer("Dashboard_Load")
        
        print(f"  ✓ Load time: {elapsed:.3f}s")
        print(f"  ✓ Vacant shifts: {vacant_shifts}")
        print(f"  ✓ Upcoming leave: {upcoming_leave}")
        print(f"  ✓ Active staff: {active_staff}")
        
        return {
            'load_time': elapsed,
            'target': 0.5,  # Target: <500ms
            'meets_target': elapsed < 0.5
        }
    
    def benchmark_concurrent_load(self, num_users=10):
        """
        Simulate concurrent user load
        
        Args:
            num_users: Number of concurrent users to simulate
        
        Returns: Concurrent load metrics
        """
        import concurrent.futures
        from scheduling.models import Shift
        
        print(f"\n=== Concurrent Load Benchmark ({num_users} users) ===")
        
        def simulate_user_session():
            """Simulate a single user session"""
            # Query shifts
            shifts = Shift.objects.filter(
                date__gte=timezone.now().date()
            ).select_related('user', 'unit')[:20]
            
            # Simulate processing
            count = shifts.count()
            time.sleep(0.1)  # Simulate client-side processing
            
            return count
        
        self.start_timer()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(simulate_user_session) for _ in range(num_users)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed = self.stop_timer(f"Concurrent_Load_{num_users}users")
        
        avg_response = elapsed / num_users
        requests_per_second = num_users / elapsed
        
        print(f"  ✓ Total time: {elapsed:.3f}s")
        print(f"  ✓ Avg response: {avg_response:.3f}s")
        print(f"  ✓ Requests/sec: {requests_per_second:.2f}")
        print(f"  ✓ Target: {num_users} users in <2s")
        print(f"  ✓ Meets target: {'✓' if elapsed < 2.0 else '✗'}")
        
        return {
            'total_time': elapsed,
            'avg_response': avg_response,
            'requests_per_second': requests_per_second,
            'meets_target': elapsed < 2.0
        }
    
    def generate_report(self):
        """
        Generate performance benchmark report
        
        Returns: Formatted report string
        """
        report = [
            "\n" + "="*60,
            "PERFORMANCE BENCHMARK REPORT",
            "="*60,
            f"Generated: {timezone.now()}",
            ""
        ]
        
        for benchmark_name, metrics in self.results.items():
            report.append(f"\n{benchmark_name}:")
            for metric, value in metrics.items():
                report.append(f"  {metric}: {value}")
        
        report.append("\n" + "="*60)
        
        return "\n".join(report)


def run_all_benchmarks():
    """
    Run complete performance benchmark suite
    
    Returns: Benchmark results dict
    """
    print("\n🚀 Starting Performance Benchmark Suite...")
    print("="*60)
    
    benchmark = PerformanceBenchmark()
    
    # 1. LP Solver Benchmark
    try:
        solver_results = benchmark.benchmark_lp_solvers()
    except Exception as e:
        print(f"LP Solver benchmark failed: {e}")
        solver_results = {}
    
    # 2. Prophet Training
    try:
        prophet_seq = benchmark.benchmark_prophet_training(parallel=False)
        prophet_par = benchmark.benchmark_prophet_training(parallel=True)
    except Exception as e:
        print(f"Prophet benchmark failed: {e}")
    
    # 3. Database Queries
    try:
        db_results = benchmark.benchmark_database_queries()
    except Exception as e:
        print(f"Database benchmark failed: {e}")
    
    # 4. Dashboard Load
    try:
        dashboard_results = benchmark.benchmark_dashboard_load()
    except Exception as e:
        print(f"Dashboard benchmark failed: {e}")
    
    # 5. Concurrent Load
    try:
        concurrent_results = benchmark.benchmark_concurrent_load(num_users=50)
    except Exception as e:
        print(f"Concurrent load benchmark failed: {e}")
    
    # Generate report
    print(benchmark.generate_report())
    
    return benchmark.results


def quick_benchmark():
    """Quick performance check (< 30 seconds)"""
    benchmark = PerformanceBenchmark()
    
    print("\n⚡ Quick Performance Check...")
    
    # Dashboard load only
    dashboard_results = benchmark.benchmark_dashboard_load()
    
    if dashboard_results['meets_target']:
        print("\n✓ Performance: GOOD (dashboard loads in <500ms)")
    else:
        print(f"\n⚠️ Performance: NEEDS OPTIMIZATION (dashboard loads in {dashboard_results['load_time']:.3f}s)")
    
    return dashboard_results
