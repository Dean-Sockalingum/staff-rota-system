#!/usr/bin/env python3
"""
Comprehensive pitch demo integrity checker
Tests all critical features before HSCP/CGI presentation
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from datetime import date, timedelta
from django.urls import reverse
from django.test import Client
from scheduling.models import User, Shift, Unit
from scheduling.models_multi_home import CareHome
from staff_records.models import StaffProfile

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_test(text):
    print(f"\n✓ {text}")

def print_success(text):
    print(f"  ✅ {text}")

def print_warning(text):
    print(f"  ⚠️  {text}")

def print_error(text):
    print(f"  ❌ {text}")

def test_database():
    """Test database connectivity and data availability"""
    print_test("Test 1: Database Connectivity")
    
    try:
        care_home_count = CareHome.objects.count()
        user_count = User.objects.count()
        shift_count = Shift.objects.count()
        profile_count = StaffProfile.objects.count()
        
        print_success(f"Database accessible")
        print_success(f"  - {care_home_count} care homes")
        print_success(f"  - {user_count} users")
        print_success(f"  - {shift_count:,} shifts")
        print_success(f"  - {profile_count} staff profiles")
        return True
    except Exception as e:
        print_error(f"Database error: {e}")
        return False

def test_demo_accounts():
    """Test demo account configuration"""
    print_test("Test 2: Demo Accounts Configuration")
    
    try:
        demo_mgr = User.objects.get(sap='DEMO999')
        demo_staff = User.objects.get(sap='STAFF999')
        
        issues = []
        
        # Check DEMO999 (Management)
        if not demo_mgr.home_unit:
            issues.append('DEMO999: Missing home_unit')
        if not demo_mgr.unit:
            issues.append('DEMO999: Missing unit')
        if not demo_mgr.role:
            issues.append('DEMO999: Missing role')
        else:
            if demo_mgr.role.name not in ['SM', 'OM', 'HOS']:
                issues.append(f'DEMO999: Role is {demo_mgr.role.name}, should be management (SM/OM/HOS)')
        if not demo_mgr.is_staff:
            issues.append('DEMO999: is_staff=False (needs True for dashboards)')
        
        # Check STAFF999 (Care Worker)
        if not demo_staff.home_unit:
            issues.append('STAFF999: Missing home_unit')
        if not demo_staff.unit:
            issues.append('STAFF999: Missing unit')
        if not demo_staff.role:
            issues.append('STAFF999: Missing role')
        
        if issues:
            for issue in issues:
                print_error(issue)
            return False
        else:
            print_success(f"DEMO999: {demo_mgr.role.name} at {demo_mgr.home_unit.name} (Care Home: {demo_mgr.home_unit.care_home.name})")
            print_success(f"STAFF999: {demo_staff.role.name} at {demo_staff.home_unit.name} (Care Home: {demo_staff.home_unit.care_home.name})")
            print_success(f"Passwords: DemoHSCP2025 / StaffDemo2025")
            return True
            
    except User.DoesNotExist as e:
        print_error(f"Demo account missing: {e}")
        return False
    except Exception as e:
        print_error(f"Error checking demo accounts: {e}")
        return False

def test_shift_data():
    """Test shift data availability for demo accounts"""
    print_test("Test 3: Shift Data Availability")
    
    try:
        demo_mgr = User.objects.get(sap='DEMO999')
        
        if not demo_mgr.home_unit or not demo_mgr.home_unit.care_home:
            print_error("DEMO999 has no care home assignment")
            return False
        
        care_home = demo_mgr.home_unit.care_home
        today = date.today()
        
        # Total shifts
        total_shifts = Shift.objects.filter(unit__care_home=care_home).count()
        
        # Today's shifts
        today_shifts = Shift.objects.filter(
            unit__care_home=care_home,
            date=today
        ).count()
        
        # Next 7 days
        week_shifts = Shift.objects.filter(
            unit__care_home=care_home,
            date__gte=today,
            date__lte=today + timedelta(days=7)
        ).count()
        
        # Next 30 days
        month_shifts = Shift.objects.filter(
            unit__care_home=care_home,
            date__gte=today,
            date__lte=today + timedelta(days=30)
        ).count()
        
        if total_shifts == 0:
            print_error(f"No shifts found at {care_home.name}")
            return False
        
        print_success(f"{care_home.name} shift data:")
        print_success(f"  - {total_shifts:,} total shifts")
        print_success(f"  - {today_shifts} shifts today")
        print_success(f"  - {week_shifts} shifts next 7 days")
        print_success(f"  - {month_shifts} shifts next 30 days")
        return True
        
    except Exception as e:
        print_error(f"Error checking shifts: {e}")
        return False

def test_care_homes():
    """Test all care homes have data"""
    print_test("Test 4: Care Home Data Integrity")
    
    try:
        all_good = True
        for home in CareHome.objects.all():
            units = Unit.objects.filter(care_home=home, is_active=True).count()
            shifts = Shift.objects.filter(unit__care_home=home).count()
            staff = User.objects.filter(home_unit__care_home=home, is_active=True).count()
            
            if units == 0:
                print_warning(f"{home.name}: No active units")
                all_good = False
            elif shifts == 0:
                print_warning(f"{home.name}: No shifts")
                all_good = False
            else:
                print_success(f"{home.name}: {units} units, {shifts:,} shifts, {staff} staff")
        
        return all_good
    except Exception as e:
        print_error(f"Error checking care homes: {e}")
        return False

def test_urls():
    """Test critical URL patterns"""
    print_test("Test 5: Critical URL Patterns")
    
    critical_urls = [
        ('manager_dashboard', 'Manager Dashboard'),
        ('senior_management_dashboard', 'Senior Dashboard'),
        ('ai_assistant_page', 'AI Assistant'),
        ('staff_vacancies_report', 'Staff Vacancies Report'),
        ('training_compliance_dashboard', 'Training Compliance'),
        ('forecasting_dashboard', 'ML Forecasting'),
    ]
    
    all_good = True
    for url_name, display_name in critical_urls:
        try:
            url = reverse(url_name)
            print_success(f"{display_name}: {url}")
        except Exception as e:
            print_error(f"{display_name} ({url_name}): {str(e)[:60]}")
            all_good = False
    
    return all_good

def test_staff_profiles():
    """Test staff profile data"""
    print_test("Test 6: Staff Profile Data")
    
    try:
        total = StaffProfile.objects.count()
        active = StaffProfile.objects.filter(employment_status='ACTIVE').count()
        leavers = StaffProfile.objects.filter(employment_status='LEAVER').count()
        
        # Profiles with end dates in future (upcoming leavers)
        upcoming_leavers = StaffProfile.objects.filter(
            employment_status='LEAVER',
            end_date__gt=date.today()
        ).count()
        
        # Profiles with end dates in past (current vacancies)
        current_vacancies = StaffProfile.objects.filter(
            employment_status='LEAVER',
            end_date__lte=date.today()
        ).count()
        
        print_success(f"{total} total staff profiles")
        print_success(f"  - {active} active staff")
        print_success(f"  - {leavers} total leavers")
        print_success(f"  - {upcoming_leavers} upcoming leavers")
        print_success(f"  - {current_vacancies} current vacancies")
        
        return True
    except Exception as e:
        print_error(f"Error checking staff profiles: {e}")
        return False

def test_model_imports():
    """Test critical model imports"""
    print_test("Test 7: Model Imports")
    
    try:
        # Try importing all critical models
        from scheduling.models import (
            User, Shift, Unit, Role, LeaveRequest, 
            ShiftSwapRequest, StaffingAlert, TrainingRecord, TrainingCourse
        )
        from scheduling.models_multi_home import CareHome
        from staff_records.models import StaffProfile
        
        print_success("All critical models import successfully")
        return True
    except ImportError as e:
        print_error(f"Import error: {e}")
        return False

def test_template_issues():
    """Test for common template issues"""
    print_test("Test 8: Template Syntax Check")
    
    try:
        from django.template import Template, Context
        
        # Test template rendering
        test_template = Template('{{ test_var|title }}')
        result = test_template.render(Context({'test_var': 'hello_world'}))
        
        # Test that replace filter doesn't exist (would cause error)
        try:
            bad_template = Template('{{ test_var|replace:"_":" " }}')
            bad_template.render(Context({'test_var': 'test'}))
            print_warning("Replace filter unexpectedly worked - check Django version")
        except Exception:
            print_success("Replace filter correctly not available (as expected)")
        
        print_success("Template engine working correctly")
        return True
    except Exception as e:
        print_error(f"Template error: {e}")
        return False

def main():
    """Run all tests"""
    print_header("🎯 PITCH DEMO SYSTEM INTEGRITY CHECK")
    print("Testing system before HSCP/CGI presentation...")
    
    results = []
    
    # Run all tests
    results.append(('Database', test_database()))
    results.append(('Demo Accounts', test_demo_accounts()))
    results.append(('Shift Data', test_shift_data()))
    results.append(('Care Homes', test_care_homes()))
    results.append(('URLs', test_urls()))
    results.append(('Staff Profiles', test_staff_profiles()))
    results.append(('Model Imports', test_model_imports()))
    results.append(('Templates', test_template_issues()))
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 SYSTEM READY FOR PITCH!")
        print_header("📋 NEXT STEPS")
        print("  1. Start server: python3 manage.py runserver")
        print("  2. Login as DEMO999 / DemoHSCP2025 (management view)")
        print("  3. Test HOS Dashboard, AI Assistant, Reports")
        print("  4. Logout and login as STAFF999 / StaffDemo2025 (staff view)")
        print("  5. Test My Rota, Leave Requests, Personal Schedule")
        print("=" * 70)
        return 0
    else:
        print("\n  ⚠️  ISSUES DETECTED - REVIEW FAILURES ABOVE")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
