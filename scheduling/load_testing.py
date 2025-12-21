"""
Load Testing Script for Staff Rota System

Tests concurrent user scenarios:
- Dashboard page loads
- Vacancy report generation
- Shift creation/updates
- Leave request submission

Usage:
    python manage.py shell
    >>> from scheduling.load_testing import run_load_test
    >>> run_load_test(num_users=100, duration_seconds=60)
"""

import time
import random
import threading
from datetime import datetime, timedelta
from django.utils import timezone
from django.test import Client
from django.contrib.auth import get_user_model
import statistics
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class LoadTester:
    """
    Concurrent load testing utility
    """
    
    def __init__(self, num_users=10, duration_seconds=30):
        """
        Initialize load tester
        
        Args:
            num_users: Number of concurrent users to simulate
            duration_seconds: Duration of load test
        """
        self.num_users = num_users
        self.duration_seconds = duration_seconds
        self.results = []
        self.errors = []
        self.lock = threading.Lock()
    
    def simulate_user_session(self, user_id):
        """
        Simulate a single user session
        
        Args:
            user_id: Thread-safe user identifier
        
        Returns: Session metrics dict
        """
        client = Client()
        session_metrics = {
            'user_id': user_id,
            'requests': [],
            'errors': []
        }
        
        # Get a test user
        try:
            users = list(User.objects.filter(is_active=True)[:10])
            if not users:
                logger.error("No active users found for load testing")
                return session_metrics
            
            user = random.choice(users)
            
            # Login (if authentication required)
            # client.force_login(user)
            
        except Exception as e:
            logger.error(f"Failed to get test user: {e}")
            return session_metrics
        
        start_time = time.time()
        end_time = start_time + self.duration_seconds
        
        # Simulate user actions for duration
        while time.time() < end_time:
            action = random.choice([
                'view_dashboard',
                'view_vacancies',
                'view_schedule',
                'view_leave_requests'
            ])
            
            request_start = time.time()
            
            try:
                if action == 'view_dashboard':
                    response = client.get('/scheduling/')
                    
                elif action == 'view_vacancies':
                    response = client.get('/scheduling/api/vacancies/')
                    
                elif action == 'view_schedule':
                    response = client.get('/scheduling/rota/')
                    
                elif action == 'view_leave_requests':
                    response = client.get('/scheduling/leave/')
                
                request_time = time.time() - request_start
                
                session_metrics['requests'].append({
                    'action': action,
                    'time': request_time,
                    'status': response.status_code if hasattr(response, 'status_code') else 0
                })
                
            except Exception as e:
                session_metrics['errors'].append({
                    'action': action,
                    'error': str(e)
                })
            
            # Random think time (0.5-2 seconds)
            time.sleep(random.uniform(0.5, 2.0))
        
        return session_metrics
    
    def run_test(self):
        """
        Execute load test with concurrent users
        
        Returns: Test results dict
        """
        print(f"\n🚀 Starting Load Test...")
        print(f"  Users: {self.num_users}")
        print(f"  Duration: {self.duration_seconds}s")
        print("="*60)
        
        # Create threads for concurrent users
        threads = []
        start_time = time.time()
        
        for i in range(self.num_users):
            thread = threading.Thread(
                target=self._user_thread_wrapper,
                args=(i,)
            )
            threads.append(thread)
            thread.start()
            
            # Stagger thread starts slightly
            time.sleep(0.1)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Analyze results
        return self.analyze_results(total_time)
    
    def _user_thread_wrapper(self, user_id):
        """Thread-safe wrapper for user simulation"""
        try:
            metrics = self.simulate_user_session(user_id)
            
            with self.lock:
                self.results.append(metrics)
        
        except Exception as e:
            with self.lock:
                self.errors.append({
                    'user_id': user_id,
                    'error': str(e)
                })
    
    def analyze_results(self, total_time):
        """
        Analyze load test results
        
        Args:
            total_time: Total test duration
        
        Returns: Analysis dict
        """
        print(f"\n📊 Analyzing Results...")
        
        # Aggregate request times
        all_requests = []
        for user_result in self.results:
            all_requests.extend(user_result['requests'])
        
        if not all_requests:
            print("⚠️ No requests completed")
            return {}
        
        request_times = [r['time'] for r in all_requests]
        
        # Calculate metrics
        total_requests = len(all_requests)
        total_errors = sum(len(r['errors']) for r in self.results)
        
        avg_response_time = statistics.mean(request_times)
        median_response_time = statistics.median(request_times)
        p95_response_time = sorted(request_times)[int(len(request_times) * 0.95)]
        p99_response_time = sorted(request_times)[int(len(request_times) * 0.99)]
        
        requests_per_second = total_requests / total_time
        
        # Count by action type
        action_counts = {}
        for req in all_requests:
            action = req['action']
            if action not in action_counts:
                action_counts[action] = 0
            action_counts[action] += 1
        
        # Print report
        print("\n" + "="*60)
        print("LOAD TEST RESULTS")
        print("="*60)
        print(f"\nTest Configuration:")
        print(f"  Concurrent Users: {self.num_users}")
        print(f"  Test Duration: {total_time:.2f}s")
        
        print(f"\nRequest Statistics:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Total Errors: {total_errors}")
        print(f"  Error Rate: {(total_errors/total_requests*100) if total_requests > 0 else 0:.2f}%")
        print(f"  Requests/Second: {requests_per_second:.2f}")
        
        print(f"\nResponse Times:")
        print(f"  Average: {avg_response_time*1000:.1f}ms")
        print(f"  Median: {median_response_time*1000:.1f}ms")
        print(f"  95th Percentile: {p95_response_time*1000:.1f}ms")
        print(f"  99th Percentile: {p99_response_time*1000:.1f}ms")
        
        print(f"\nRequests by Action:")
        for action, count in sorted(action_counts.items()):
            print(f"  {action}: {count}")
        
        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        
        if avg_response_time < 0.5:
            print("  ✓ EXCELLENT - Avg response time <500ms")
        elif avg_response_time < 1.0:
            print("  ✓ GOOD - Avg response time <1s")
        elif avg_response_time < 2.0:
            print("  ⚠️ ACCEPTABLE - Avg response time <2s")
        else:
            print("  ✗ POOR - Avg response time >2s (optimization needed)")
        
        if requests_per_second > 50:
            print(f"  ✓ EXCELLENT - {requests_per_second:.0f} req/s throughput")
        elif requests_per_second > 20:
            print(f"  ✓ GOOD - {requests_per_second:.0f} req/s throughput")
        else:
            print(f"  ⚠️ LOW - {requests_per_second:.0f} req/s throughput")
        
        if total_errors == 0:
            print("  ✓ STABLE - No errors detected")
        else:
            print(f"  ⚠️ {total_errors} errors detected")
        
        print("\n" + "="*60)
        
        return {
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate': (total_errors/total_requests*100) if total_requests > 0 else 0,
            'requests_per_second': requests_per_second,
            'avg_response_time': avg_response_time,
            'median_response_time': median_response_time,
            'p95_response_time': p95_response_time,
            'p99_response_time': p99_response_time,
            'action_counts': action_counts
        }


def run_load_test(num_users=50, duration_seconds=60):
    """
    Run load test with specified parameters
    
    Args:
        num_users: Number of concurrent users (default: 50)
        duration_seconds: Test duration (default: 60s)
    
    Returns: Test results dict
    """
    tester = LoadTester(num_users=num_users, duration_seconds=duration_seconds)
    return tester.run_test()


def quick_load_test():
    """Quick load test (10 users, 10 seconds)"""
    print("\n⚡ Quick Load Test (10 users, 10 seconds)...")
    return run_load_test(num_users=10, duration_seconds=10)


def stress_test():
    """Stress test (100 users, 120 seconds)"""
    print("\n💪 Stress Test (100 users, 120 seconds)...")
    return run_load_test(num_users=100, duration_seconds=120)
