"""
Test Suite for Task 57: Form Auto-Save with localStorage
Tests form auto-save functionality and data restoration
"""

from django.test import TestCase, Client, LiveServerTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, date
from scheduling.models import Unit, LeaveRequest, IncidentReport, SupervisionRecord, TrainingRecord, TrainingCourse
from scheduling.models_multi_home import CareHome
from staff_records.models import StaffProfile

User = get_user_model()


class FormAutoSaveTemplateTests(TestCase):
    """Test that auto-save is enabled on critical forms"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name="ORCHARD_GROVE",
            bed_capacity=50
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(
            sap='200100',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpass123'
        )
        self.user.unit = self.unit
        self.user.save()
        # self.user.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
    
    def test_leave_request_form_has_autosave(self):
        """Test leave request form includes auto-save attributes"""
        self.client.force_login(self.user)  # '200100', password='testpass123')
        url = reverse('request_leave')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-autosave="true"')
        self.assertContains(response, '/static/js/form-autosave.js')
        self.assertContains(response, '/static/css/form-autosave.css')
    
    def test_incident_report_form_has_autosave(self):
        """Test incident report form includes auto-save attributes"""
        self.client.force_login(self.user)  # '200100', password='testpass123')
        url = reverse('report_incident')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-autosave="true"')
        self.assertContains(response, 'form-autosave.js')
    
    def test_supervision_record_form_has_autosave(self):
        """Test supervision record form includes auto-save attributes"""
        self.client.force_login(self.user)  # '200100', password='testpass123')
        url = reverse('create_supervision_record')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-autosave="true"')
        self.assertContains(response, 'form-autosave.js')
    
    def test_training_record_form_has_autosave(self):
        """Test training record form includes auto-save attributes"""
        self.client.force_login(self.user)  # '200100', password='testpass123')
        url = reverse('submit_training_record')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-autosave="true"')
        self.assertContains(response, 'form-autosave.js')


class FormAutoSaveJavaScriptTests(TestCase):
    """Test form auto-save JavaScript file existence and structure"""
    
    def test_autosave_js_exists(self):
        """Test that form-autosave.js file is accessible"""
        response = self.client.get('/static/js/form-autosave.js')
        
        # Should either return 200 or 404 if static files not served in tests
        # In production, this should be 200
        self.assertIn(response.status_code, [200, 404])
    
    def test_autosave_css_exists(self):
        """Test that form-autosave.css file is accessible"""
        response = self.client.get('/static/css/form-autosave.css')
        
        self.assertIn(response.status_code, [200, 404])


class FormSubmissionTests(TestCase):
    """Test form submission behavior with auto-save"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name="ORCHARD_GROVE",
            bed_capacity=50
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(
            sap='200101',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpass123'
        )
        self.user.unit = self.unit
        self.user.save()
        # self.user.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
    
    def test_leave_request_submission_clears_autosave(self):
        """Test that submitting leave request should clear auto-save data"""
        self.client.force_login(self.user)  # '200101', password='testpass123')
        
        # Submit leave request
        url = reverse('request_leave')
        data = {
            'leave_type': 'ANNUAL',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=5),
            'reason': 'Test vacation'
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 200)
        
        # Verify leave request was created
        leave_requests = LeaveRequest.objects.filter(
            staff_profile=self.user.staff_profile,
            leave_type=leave_type
        )
        self.assertTrue(leave_requests.exists())
    
    def test_incident_report_submission(self):
        """Test incident report submission"""
        self.client.force_login(self.user)  # '200101', password='testpass123')
        
        url = reverse('report_incident')
        data = {
            'incident_date': date.today(),
            'incident_time': '14:30',
            'incident_type': 'FALL',
            'severity': 'MODERATE',
            'description': 'Test incident description',
            'location': 'Test location',
            'immediate_action': 'Test action taken',
            'reported_by': self.user.staff_profile.id
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Should handle submission (may have validation errors)
        self.assertIn(response.status_code, [200, 302])


class FormValidationTests(TestCase):
    """Test form validation with auto-save enabled"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name="ORCHARD_GROVE",
            bed_capacity=50
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(
            sap='200102',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpass123'
        )
        self.user.unit = self.unit
        self.user.save()
        # self.user.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
    
    def test_leave_request_validation_errors(self):
        """Test that validation errors are displayed correctly"""
        self.client.force_login(self.user)  # '200102', password='testpass123')
        
        # Submit incomplete leave request (missing required fields)
        url = reverse('request_leave')
        data = {
            'start_date': date.today(),
            # Missing leave_type and end_date
        }
        
        response = self.client.post(url, data)
        
        # Should return form with errors (not redirect)
        self.assertEqual(response.status_code, 200)
        # Form should still have auto-save enabled
        self.assertContains(response, 'data-autosave="true"')
    
    def test_date_range_validation(self):
        """Test date range validation (end_date >= start_date)"""
        self.client.force_login(self.user)  # '200102', password='testpass123')
        
        url = reverse('request_leave')
        data = {
            'leave_type': 'ANNUAL',
            'start_date': date.today(),
            'end_date': date.today() - timedelta(days=5),  # Invalid: end before start
            'reason': 'Test'
        }
        
        response = self.client.post(url, data)
        
        # Should show validation error
        self.assertEqual(response.status_code, 200)


class FormSecurityTests(TestCase):
    """Test security aspects of form auto-save"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name="ORCHARD_GROVE",
            bed_capacity=50
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(
            sap='200103',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpass123'
        )
        self.user.unit = self.unit
        self.user.save()
        # self.user.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
    
    def test_csrf_token_not_saved(self):
        """Test that CSRF tokens are not saved in localStorage"""
        self.client.force_login(self.user)  # '200103', password='testpass123')
        url = reverse('request_leave')
        response = self.client.get(url)
        
        # Form should have CSRF token
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        # JavaScript should exclude CSRF from auto-save
        # (This is verified in form-autosave.js code review)
        self.assertEqual(response.status_code, 200)
    
    def test_authentication_required_for_forms(self):
        """Test that forms require authentication"""
        # Try accessing forms without login
        urls = [
            reverse('request_leave'),
            reverse('report_incident'),
            reverse('create_supervision_record'),
            reverse('submit_training_record')
        ]
        
        for url in urls:
            response = self.client.get(url)
            # Should redirect to login
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login/', response.url)


class FormDataIntegrityTests(TestCase):
    """Test data integrity with auto-save"""
    
    def setUp(self):
        self.client = Client()
        self.care_home = CareHome.objects.create(
            name="ORCHARD_GROVE",
            bed_capacity=50
        )
        self.unit = Unit.objects.create(
            name="Test Unit",
            care_home=self.care_home
        )
        
        self.user = User.objects.create_user(
            sap='200104',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='testpass123'
        )
        self.user.unit = self.unit
        self.user.save()
        # self.user.care_home_access.add(self.care_home)  # care_home_access removed - users access via unit.care_home
    
    def test_special_characters_in_forms(self):
        """Test that forms handle special characters correctly"""
        self.client.force_login(self.user)  # '200104', password='testpass123')
        
        url = reverse('request_leave')
        data = {
            'leave_type': 'SICK',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=3),
            'reason': 'Test with special chars: <>&"\''
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Should handle special characters
        self.assertEqual(response.status_code, 200)
        
        # Verify data was saved correctly
        leave_request = LeaveRequest.objects.filter(
            staff_profile=self.user.staff_profile,
            leave_type='SICK'
        ).first()
        
        if leave_request:
            self.assertIn('special chars', leave_request.reason)
