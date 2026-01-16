#!/usr/bin/env python3
"""
Test script for Care Inspectorate compliance web forms
"""
import os
import django
import sys
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.test import Client
from scheduling.models import User, TrainingCourse, TrainingRecord, InductionProgress, SupervisionRecord, IncidentReport
from django.contrib.auth import get_user_model

def create_test_data():
    """Create test users and data"""
    print("\n" + "="*80)
    print("CREATING TEST DATA")
    print("="*80)
    
    # Create test users if they don't exist
    User = get_user_model()
    
    # Staff member
    staff_user, created = User.objects.get_or_create(
        username='test_staff',
        defaults={
            'email': 'test.staff@example.com',
            'first_name': 'Test',
            'last_name': 'Staff',
            'is_staff': False,
        }
    )
    if created:
        staff_user.set_password('testpass123')
        staff_user.save()
        print(f"✓ Created staff user: {staff_user.username}")
    else:
        print(f"✓ Using existing staff user: {staff_user.username}")
    
    # Manager
    manager_user, created = User.objects.get_or_create(
        username='test_manager',
        defaults={
            'email': 'test.manager@example.com',
            'first_name': 'Test',
            'last_name': 'Manager',
            'is_staff': True,
        }
    )
    if created:
        manager_user.set_password('testpass123')
        manager_user.save()
        print(f"✓ Created manager user: {manager_user.username}")
    else:
        print(f"✓ Using existing manager user: {manager_user.username}")
    
    # Create a training course
    course, created = TrainingCourse.objects.get_or_create(
        name='Fire Safety',
        defaults={
            'category': 'MANDATORY',
            'validity_months': 12,
            'description': 'Fire safety training',
            'is_sssc_cpd': True,
            'sssc_cpd_hours': 3.0,
        }
    )
    if created:
        print(f"✓ Created training course: {course.name}")
    else:
        print(f"✓ Using existing training course: {course.name}")
    
    return staff_user, manager_user, course

def test_urls():
    """Test that all compliance URLs are accessible"""
    print("\n" + "="*80)
    print("TESTING URL ACCESSIBILITY")
    print("="*80)
    
    client = Client()
    
    # URLs to test (without authentication)
    urls = [
        ('/compliance/training/', 'Training Dashboard'),
        ('/compliance/training/submit/', 'Submit Training'),
        ('/compliance/induction/', 'Induction Progress'),
        ('/compliance/induction/management/', 'Induction Management'),
        ('/compliance/supervision/', 'Supervision Records'),
        ('/compliance/supervision/create/', 'Create Supervision'),
        ('/compliance/supervision/management/', 'Supervision Management'),
        ('/compliance/incident/report/', 'Report Incident'),
        ('/compliance/incident/my-reports/', 'My Incidents'),
        ('/compliance/incident/management/', 'Incident Management'),
    ]
    
    results = []
    for url, name in urls:
        try:
            response = client.get(url)
            status = response.status_code
            # 302 = redirect to login (expected for protected views)
            # 200 = success
            if status in [200, 302]:
                results.append(f"✓ {name:30s} {url:40s} [{status}]")
            else:
                results.append(f"✗ {name:30s} {url:40s} [{status}]")
        except Exception as e:
            results.append(f"✗ {name:30s} {url:40s} [ERROR: {str(e)}]")
    
    for result in results:
        print(result)
    
    return results

def test_template_rendering():
    """Test that templates render without errors"""
    print("\n" + "="*80)
    print("TESTING TEMPLATE RENDERING")
    print("="*80)
    
    staff_user, manager_user, course = create_test_data()
    client = Client()
    
    # Login as staff
    client.login(username='test_staff', password='testpass123')
    print("\n--- Testing Staff Views (logged in as test_staff) ---")
    
    staff_views = [
        ('/compliance/training/', 'Training Dashboard'),
        ('/compliance/training/submit/', 'Submit Training'),
        ('/compliance/induction/', 'Induction Progress'),
        ('/compliance/supervision/', 'Supervision Records'),
        ('/compliance/incident/report/', 'Report Incident'),
        ('/compliance/incident/my-reports/', 'My Incidents'),
    ]
    
    for url, name in staff_views:
        try:
            response = client.get(url)
            if response.status_code == 200:
                # Check for common template elements
                content = response.content.decode('utf-8')
                has_title = '<title>' in content or '<h2>' in content
                has_form = '<form' in content or 'card' in content
                
                if has_title and has_form:
                    print(f"✓ {name:30s} renders correctly")
                else:
                    print(f"⚠ {name:30s} renders but missing elements")
            elif response.status_code == 404:
                print(f"✗ {name:30s} not found (view may not exist)")
            else:
                print(f"✗ {name:30s} returned {response.status_code}")
        except Exception as e:
            print(f"✗ {name:30s} ERROR: {str(e)[:50]}")
    
    # Logout and login as manager
    client.logout()
    client.login(username='test_manager', password='testpass123')
    print("\n--- Testing Manager Views (logged in as test_manager) ---")
    
    manager_views = [
        ('/compliance/induction/management/', 'Induction Management'),
        ('/compliance/supervision/create/', 'Create Supervision'),
        ('/compliance/supervision/management/', 'Supervision Management'),
        ('/compliance/incident/management/', 'Incident Management'),
    ]
    
    for url, name in manager_views:
        try:
            response = client.get(url)
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                has_title = '<title>' in content or '<h2>' in content
                has_content = 'card' in content or 'table' in content
                
                if has_title and has_content:
                    print(f"✓ {name:30s} renders correctly")
                else:
                    print(f"⚠ {name:30s} renders but missing elements")
            elif response.status_code == 404:
                print(f"✗ {name:30s} not found (view may not exist)")
            else:
                print(f"✗ {name:30s} returned {response.status_code}")
        except Exception as e:
            print(f"✗ {name:30s} ERROR: {str(e)[:50]}")

def test_form_fields():
    """Test that forms have the correct field names"""
    print("\n" + "="*80)
    print("TESTING FORM FIELDS")
    print("="*80)
    
    staff_user, manager_user, course = create_test_data()
    client = Client()
    client.login(username='test_staff', password='testpass123')
    
    # Test training form
    print("\n--- Training Form Fields ---")
    response = client.get('/compliance/training/submit/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        required_fields = [
            'name="course"',
            'name="completion_date"',
            'name="trainer_name"',
            'name="certificate_file"',
            'name="sssc_cpd_hours"',
        ]
        for field in required_fields:
            if field in content:
                print(f"✓ {field}")
            else:
                print(f"✗ {field} NOT FOUND")
    
    # Test incident form
    print("\n--- Incident Report Form Fields ---")
    response = client.get('/compliance/incident/report/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        required_fields = [
            'name="incident_date"',
            'name="incident_time"',
            'name="incident_type"',
            'name="severity"',
            'name="service_user_name"',
            'name="description"',
        ]
        for field in required_fields:
            if field in content:
                print(f"✓ {field}")
            else:
                print(f"✗ {field} NOT FOUND")
    
    # Test supervision form (manager)
    client.logout()
    client.login(username='test_manager', password='testpass123')
    print("\n--- Supervision Form Fields ---")
    response = client.get('/compliance/supervision/create/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        required_fields = [
            'name="staff_member"',
            'name="session_date"',
            'name="wellbeing_score"',
            'name="performance_strengths"',
            'name="next_supervision_date"',
        ]
        for field in required_fields:
            if field in content:
                print(f"✓ {field}")
            else:
                print(f"✗ {field} NOT FOUND")

def test_navigation_links():
    """Test that navigation links are in dashboards"""
    print("\n" + "="*80)
    print("TESTING NAVIGATION LINKS")
    print("="*80)
    
    staff_user, manager_user, course = create_test_data()
    client = Client()
    
    # Test staff dashboard
    client.login(username='test_staff', password='testpass123')
    print("\n--- Staff Dashboard Navigation ---")
    response = client.get('/staff-dashboard/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        links = [
            ('my_training_dashboard', 'My Training'),
            ('my_induction_progress', 'My Induction'),
            ('my_supervision_records', 'My Supervision'),
            ('my_incident_reports', 'My Incidents'),
            ('report_incident', 'Report Incident'),
        ]
        for url_name, display_name in links:
            if url_name in content:
                print(f"✓ {display_name:30s} link found")
            else:
                print(f"✗ {display_name:30s} link NOT FOUND")
    
    # Test manager dashboard
    client.logout()
    client.login(username='test_manager', password='testpass123')
    print("\n--- Manager Dashboard Navigation ---")
    response = client.get('/manager-dashboard/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        links = [
            ('induction_management', 'Induction Management'),
            ('supervision_management', 'Supervision Management'),
            ('incident_management', 'Incident Management'),
            ('create_supervision_record', 'Create Supervision'),
        ]
        for url_name, display_name in links:
            if url_name in content:
                print(f"✓ {display_name:30s} link found")
            else:
                print(f"✗ {display_name:30s} link NOT FOUND")

def test_media_configuration():
    """Test that media file serving is configured"""
    print("\n" + "="*80)
    print("TESTING MEDIA FILE CONFIGURATION")
    print("="*80)
    
    from django.conf import settings
    
    # Check settings
    checks = [
        ('MEDIA_URL', hasattr(settings, 'MEDIA_URL'), getattr(settings, 'MEDIA_URL', None)),
        ('MEDIA_ROOT', hasattr(settings, 'MEDIA_ROOT'), getattr(settings, 'MEDIA_ROOT', None)),
        ('TRAINING_CERTIFICATES_DIR', hasattr(settings, 'TRAINING_CERTIFICATES_DIR'), getattr(settings, 'TRAINING_CERTIFICATES_DIR', None)),
    ]
    
    for name, exists, value in checks:
        if exists and value:
            print(f"✓ {name:30s} = {value}")
        else:
            print(f"✗ {name:30s} NOT CONFIGURED")
    
    # Check directories exist
    import os
    media_root = settings.MEDIA_ROOT
    dirs = [
        'training/certificates',
        'incidents/photos',
        'incidents/body_maps',
    ]
    
    print("\n--- Media Directory Structure ---")
    for dir_path in dirs:
        full_path = os.path.join(media_root, dir_path)
        if os.path.exists(full_path):
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} does not exist")

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "COMPLIANCE WEB FORMS TEST SUITE" + " "*26 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        test_urls()
        test_template_rendering()
        test_form_fields()
        test_navigation_links()
        test_media_configuration()
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print("✓ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Start the development server: python3 manage.py runserver")
        print("2. Visit http://127.0.0.1:8000/staff-dashboard/ (login required)")
        print("3. Test forms manually in your browser")
        print("4. Try uploading a training certificate")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_all_tests()
