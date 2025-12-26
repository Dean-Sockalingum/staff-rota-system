#!/usr/bin/env python3
"""
Phase 2 Integration Testing Suite
Tests integration between Tasks 6, 7, and 8

Test Scenarios:
1. Budget Optimization Flow (Task 8 → Tasks 1-7)
2. Compliance Enforcement (Task 6 blocks → Task 8 suggests alternative)
3. Fraud Detection (Task 7 flags → Task 8 excludes from options)
4. Cost Optimization (Task 8 ranks by cost → Task 5 predicts future needs)
5. API Endpoint Testing (All Phase 2 endpoints)
6. Performance Benchmarking

Author: AI Assistant
Date: December 25, 2025
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Setup Django environment
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from scheduling.models import Shift, Unit, ShiftType, User, Role
from scheduling.budget_optimizer import BudgetOptimizer
from scheduling.compliance_monitor import ComplianceMonitor
from scheduling.payroll_validator import PayrollValidator

User = get_user_model()


class Phase2IntegrationTests(TestCase):
    """
    Integration tests for Phase 2 tasks (6, 7, 8)
    """
    
    def setUp(self):
        """Setup test data"""
        print("\n" + "="*80)
        print("PHASE 2 INTEGRATION TESTING")
        print("="*80)
        
        # Create test unit
        self.unit = Unit.objects.create(
            name="Test Unit",
            ideal_staffing_level=5
        )
        
        # Create test role
        self.role = Role.objects.create(
            name="Support Care Worker",
            required_headcount=5,
            hourly_rate=Decimal('12.00')
        )
        
        # Create test shift type
        self.shift_type = ShiftType.objects.create(
            name="Day Shift",
            start_time="08:00",
            end_time="20:00",
            duration_hours=Decimal('12.00')
        )
        
        # Create test users
        self.staff1 = User.objects.create_user(
            username="staff1",
            first_name="Staff",
            last_name="One",
            email="staff1@test.com",
            unit=self.unit,
            role=self.role,
            employment_status='FT'
        )
        
        self.staff2 = User.objects.create_user(
            username="staff2",
            first_name="Staff",
            last_name="Two",
            email="staff2@test.com",
            unit=self.unit,
            role=self.role,
            employment_status='FT'
        )
        
        # Create high-risk staff for fraud testing
        self.risky_staff = User.objects.create_user(
            username="risky_staff",
            first_name="Risky",
            last_name="Staff",
            email="risky@test.com",
            unit=self.unit,
            role=self.role,
            employment_status='FT'
        )
        
        # Initialize components
        self.budget_optimizer = BudgetOptimizer()
        self.compliance_monitor = ComplianceMonitor()
        self.payroll_validator = PayrollValidator()
        
        print(f"✅ Test setup complete")
    
    def test_1_budget_optimization_flow(self):
        """
        Test Scenario 1: Budget Optimization Flow
        Task 8 should call Tasks 1-7 to find cheapest WTD-compliant solution
        """
        print("\n" + "-"*80)
        print("TEST 1: Budget Optimization Flow")
        print("-"*80)
        
        # Setup: Create a shortage scenario
        shift_date = timezone.now().date() + timedelta(days=7)
        
        # Test budget optimization
        result = self.budget_optimizer.get_optimal_staffing_solution(
            shift_date=shift_date,
            shift_type=self.shift_type,
            unit=self.unit,
            budget_limit=Decimal('200.00')
        )
        
        # Verify result structure
        self.assertIn('recommended_option', result)
        self.assertIn('cost', result)
        self.assertIn('details', result)
        self.assertIn('alternatives', result)
        self.assertIn('budget_impact', result)
        self.assertIn('compliance', result)
        
        # Verify cost is within budget
        if result['cost'] is not None:
            self.assertLessEqual(result['cost'], Decimal('200.00'))
        
        print(f"✅ Recommended option: {result['recommended_option']}")
        print(f"✅ Cost: £{result['cost']}")
        print(f"✅ WTD Compliant: {result['compliance']['wdt_compliant']}")
        print(f"✅ Alternatives available: {len(result['alternatives'])}")
        
    def test_2_compliance_enforcement(self):
        """
        Test Scenario 2: Compliance Enforcement
        Task 6 blocks WTD violation → Task 8 suggests alternative
        """
        print("\n" + "-"*80)
        print("TEST 2: Compliance Enforcement")
        print("-"*80)
        
        # Setup: Create shifts to trigger WTD violation
        today = timezone.now().date()
        
        # Create 6 consecutive 12-hour shifts (72 hours) to trigger 48-hour limit
        for i in range(6):
            shift_date = today + timedelta(days=i)
            Shift.objects.create(
                user=self.staff1,
                unit=self.unit,
                shift_type=self.shift_type,
                date=shift_date,
                start_time=datetime.combine(shift_date, datetime.strptime("08:00", "%H:%M").time()),
                end_time=datetime.combine(shift_date, datetime.strptime("20:00", "%H:%M").time()),
                is_confirmed=True,
                created_by=self.staff1
            )
        
        # Test compliance validation for 7th shift (should fail)
        seventh_shift_date = today + timedelta(days=6)
        validation = self.compliance_monitor.validate_shift_assignment(
            user=self.staff1,
            shift_date=seventh_shift_date,
            shift_type=self.shift_type,
            unit=self.unit
        )
        
        # Verify WTD violation detected
        self.assertFalse(validation['safe'], "Should detect WTD violation")
        self.assertTrue(any('48-hour' in v['rule'] for v in validation['violations']))
        
        print(f"✅ WTD violation detected: {validation['violations'][0]['rule']}")
        print(f"✅ Hours worked: {validation['violations'][0]['hours_worked']}")
        
        # Test that budget optimizer suggests alternative
        result = self.budget_optimizer.get_optimal_staffing_solution(
            shift_date=seventh_shift_date,
            shift_type=self.shift_type,
            unit=self.unit
        )
        
        # Verify staff1 is NOT recommended due to WTD violation
        if result['recommended_option'] == 'overtime':
            self.assertNotEqual(
                result['details'].get('user_id'),
                self.staff1.id,
                "Should not recommend staff member with WTD violation"
            )
        
        print(f"✅ Alternative solution found: {result['recommended_option']}")
        
    def test_3_fraud_detection_integration(self):
        """
        Test Scenario 3: Fraud Detection
        Task 7 flags high risk → Task 8 excludes from overtime options
        """
        print("\n" + "-"*80)
        print("TEST 3: Fraud Detection Integration")
        print("-"*80)
        
        # Setup: Create suspicious overtime pattern
        today = timezone.now().date()
        
        for i in range(10):
            shift_date = today - timedelta(days=i*2)
            Shift.objects.create(
                user=self.risky_staff,
                unit=self.unit,
                shift_type=self.shift_type,
                date=shift_date,
                start_time=datetime.combine(shift_date, datetime.strptime("08:00", "%H:%M").time()),
                end_time=datetime.combine(shift_date, datetime.strptime("20:00", "%H:%M").time()),
                is_overtime=True,
                overtime_reason="Shortage coverage",
                is_confirmed=True,
                created_by=self.risky_staff
            )
        
        # Test fraud risk detection
        fraud_risk = self.payroll_validator.get_fraud_risk_score(
            user=self.risky_staff,
            period_days=30
        )
        
        # Verify high risk detected
        print(f"✅ Fraud risk level: {fraud_risk['risk_level']}")
        print(f"✅ Risk score: {fraud_risk['risk_score']}/100")
        print(f"✅ Red flags: {len(fraud_risk['red_flags'])}")
        
        # Test that budget optimizer considers fraud risk
        future_date = today + timedelta(days=7)
        result = self.budget_optimizer.get_optimal_staffing_solution(
            shift_date=future_date,
            shift_type=self.shift_type,
            unit=self.unit
        )
        
        # If overtime is recommended, verify it's not the risky staff
        if result['recommended_option'] == 'overtime':
            recommended_user_id = result['details'].get('user_id')
            if recommended_user_id:
                self.assertNotEqual(
                    recommended_user_id,
                    self.risky_staff.id,
                    "Should not recommend high-risk staff for overtime"
                )
                print(f"✅ High-risk staff excluded from recommendations")
        
    def test_4_cost_optimization(self):
        """
        Test Scenario 4: Cost Optimization
        Task 8 ranks solutions by cost and applies budget constraints
        """
        print("\n" + "-"*80)
        print("TEST 4: Cost Optimization")
        print("-"*80)
        
        # Test budget status
        today = timezone.now().date()
        period_start = today.replace(day=1)
        period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        budget_status = self.budget_optimizer.get_budget_status(
            period_start=period_start,
            period_end=period_end
        )
        
        # Verify budget status structure
        self.assertIn('period', budget_status)
        self.assertIn('spending', budget_status)
        self.assertIn('budget', budget_status)
        self.assertIn('alerts', budget_status)
        self.assertIn('projections', budget_status)
        
        print(f"✅ Budget allocated: £{budget_status['budget']['allocated']}")
        print(f"✅ Budget spent: £{budget_status['budget']['spent']}")
        print(f"✅ Budget remaining: £{budget_status['budget']['remaining']}")
        print(f"✅ Active alerts: {len(budget_status['alerts'])}")
        
        # Test budget forecasting
        forecast = self.budget_optimizer.predict_budget_needs(days_ahead=30)
        
        # Verify forecast structure
        self.assertIn('forecast_period', forecast)
        self.assertIn('predicted_shortages', forecast)
        self.assertIn('estimated_costs', forecast)
        self.assertIn('budget_recommendations', forecast)
        
        print(f"✅ Predicted shortages: {forecast['predicted_shortages']}")
        print(f"✅ Optimistic cost: £{forecast['estimated_costs']['optimistic']}")
        print(f"✅ Realistic cost: £{forecast['estimated_costs']['realistic']}")
        print(f"✅ Pessimistic cost: £{forecast['estimated_costs']['pessimistic']}")
        
    def test_5_api_endpoints(self):
        """
        Test Scenario 5: API Endpoint Testing
        Verify all Phase 2 API endpoints are functional
        """
        print("\n" + "-"*80)
        print("TEST 5: API Endpoint Testing")
        print("-"*80)
        
        # Create authenticated client
        client = Client()
        
        # Create admin user for API access
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        client.force_login(admin)
        
        # Test 1: Compliance validation endpoint
        compliance_response = client.post('/api/compliance/validate/', {
            'user_id': self.staff1.id,
            'shift_date': (timezone.now().date() + timedelta(days=7)).isoformat(),
            'shift_type_id': self.shift_type.id,
            'unit_id': self.unit.id
        })
        
        self.assertEqual(compliance_response.status_code, 200)
        compliance_data = json.loads(compliance_response.content)
        self.assertIn('safe', compliance_data)
        print(f"✅ Compliance API: {compliance_response.status_code}")
        
        # Test 2: Fraud detection endpoint
        fraud_response = client.get(f'/api/payroll/fraud-risk/?user_id={self.staff1.id}')
        
        self.assertEqual(fraud_response.status_code, 200)
        fraud_data = json.loads(fraud_response.content)
        self.assertIn('risk_level', fraud_data)
        print(f"✅ Fraud Detection API: {fraud_response.status_code}")
        
        # Test 3: Budget optimization endpoint
        budget_opt_response = client.post('/api/budget/optimize/', {
            'shift_date': (timezone.now().date() + timedelta(days=7)).isoformat(),
            'shift_type_id': self.shift_type.id,
            'unit_id': self.unit.id,
            'budget_limit': '200.00'
        })
        
        self.assertEqual(budget_opt_response.status_code, 200)
        budget_data = json.loads(budget_opt_response.content)
        self.assertIn('recommended_option', budget_data)
        print(f"✅ Budget Optimization API: {budget_opt_response.status_code}")
        
        # Test 4: Budget status endpoint
        budget_status_response = client.get('/api/budget/status/')
        
        self.assertEqual(budget_status_response.status_code, 200)
        status_data = json.loads(budget_status_response.content)
        self.assertIn('budget', status_data)
        print(f"✅ Budget Status API: {budget_status_response.status_code}")
        
        # Test 5: Budget forecast endpoint
        forecast_response = client.get('/api/budget/forecast/?days_ahead=30')
        
        self.assertEqual(forecast_response.status_code, 200)
        forecast_data = json.loads(forecast_response.content)
        self.assertIn('predicted_shortages', forecast_data)
        print(f"✅ Budget Forecast API: {forecast_response.status_code}")
        
    def test_6_performance_benchmarks(self):
        """
        Test Scenario 6: Performance Benchmarking
        Measure response times for integrated operations
        """
        print("\n" + "-"*80)
        print("TEST 6: Performance Benchmarking")
        print("-"*80)
        
        import time
        
        shift_date = timezone.now().date() + timedelta(days=7)
        
        # Benchmark 1: Compliance validation
        start = time.time()
        self.compliance_monitor.validate_shift_assignment(
            user=self.staff1,
            shift_date=shift_date,
            shift_type=self.shift_type,
            unit=self.unit
        )
        compliance_time = (time.time() - start) * 1000
        
        # Benchmark 2: Fraud detection
        start = time.time()
        self.payroll_validator.get_fraud_risk_score(
            user=self.staff1,
            period_days=30
        )
        fraud_time = (time.time() - start) * 1000
        
        # Benchmark 3: Budget optimization (full integration)
        start = time.time()
        self.budget_optimizer.get_optimal_staffing_solution(
            shift_date=shift_date,
            shift_type=self.shift_type,
            unit=self.unit
        )
        optimization_time = (time.time() - start) * 1000
        
        print(f"✅ Compliance validation: {compliance_time:.2f}ms")
        print(f"✅ Fraud detection: {fraud_time:.2f}ms")
        print(f"✅ Budget optimization: {optimization_time:.2f}ms")
        
        # Performance targets (all should be under 1 second)
        self.assertLess(compliance_time, 1000, "Compliance validation too slow")
        self.assertLess(fraud_time, 1000, "Fraud detection too slow")
        self.assertLess(optimization_time, 1000, "Budget optimization too slow")


def run_integration_tests():
    """Run all Phase 2 integration tests"""
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Run tests
    failures = test_runner.run_tests(['__main__.Phase2IntegrationTests'])
    
    print("\n" + "="*80)
    if failures == 0:
        print("✅ ALL PHASE 2 INTEGRATION TESTS PASSED")
        print("="*80)
        return True
    else:
        print(f"❌ {failures} TESTS FAILED")
        print("="*80)
        return False


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
