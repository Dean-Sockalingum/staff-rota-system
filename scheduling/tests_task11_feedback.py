"""
Task 11: AI Assistant Feedback & Learning System - Integration Tests

Tests for:
- Feedback recording
- Preference learning
- Response personalization
- API endpoints
- Analytics calculations
- Insights generation
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from scheduling.models import Role, User
from scheduling.feedback_learning import (
    AIQueryFeedback, UserPreference,
    record_query_feedback, get_user_preferences,
    personalize_response, get_feedback_analytics,
    get_learning_insights
)

User = get_user_model()


class FeedbackRecordingTests(TestCase):
    """Test feedback recording functionality"""
    
    def setUp(self):
        """Create test user"""
        self.role = Role.objects.create(name='Carer', is_management=False)
        self.user = User.objects.create_user(
            sap='TEST001',
            password='testpass123',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            role=self.role
        )
    
    def test_record_positive_feedback(self):
        """Test recording positive feedback (rating >= 4)"""
        feedback = record_query_feedback(
            user=self.user,
            query_text="Who can work tomorrow?",
            intent="STAFF_AVAILABILITY",
            confidence=95,
            response_text="3 staff members can work tomorrow",
            response_data={'count': 3},
            rating=5,
            feedback_type="HELPFUL",
            comment="Very clear response"
        )
        
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.user, self.user)
        self.assertEqual(feedback.rating, 5)
        self.assertTrue(feedback.is_positive)
        self.assertFalse(feedback.is_negative)
        self.assertEqual(feedback.feedback_type, "HELPFUL")
    
    def test_record_negative_feedback(self):
        """Test recording negative feedback (rating <= 2)"""
        feedback = record_query_feedback(
            user=self.user,
            query_text="Show me leave balance",
            intent="LEAVE_BALANCE",
            confidence=80,
            response_text="Unable to find leave data",
            response_data={},
            rating=2,
            feedback_type="INACCURATE",
            comment="Wrong information"
        )
        
        self.assertEqual(feedback.rating, 2)
        self.assertFalse(feedback.is_positive)
        self.assertTrue(feedback.is_negative)
    
    def test_preferences_auto_created(self):
        """Test that user preferences are auto-created on first feedback"""
        # Verify no preferences exist
        self.assertFalse(UserPreference.objects.filter(user=self.user).exists())
        
        # Record feedback
        record_query_feedback(
            user=self.user,
            query_text="Test query",
            intent="TEST",
            confidence=90,
            response_text="Test response",
            response_data={},
            rating=4
        )
        
        # Verify preferences were created
        self.assertTrue(UserPreference.objects.filter(user=self.user).exists())
        prefs = UserPreference.objects.get(user=self.user)
        self.assertEqual(prefs.total_queries, 1)
        self.assertEqual(prefs.total_feedback_count, 1)


class PreferenceLearningTests(TestCase):
    """Test preference learning functionality"""
    
    def setUp(self):
        """Create test user with multiple feedback entries"""
        self.role = Role.objects.create(name='Carer', is_management=False)
        self.user = User.objects.create_user(
            sap='TEST002',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            role=self.role
        )
    
    def test_learn_detail_level_brief(self):
        """Test learning BRIEF preference from TOO_TECHNICAL feedback"""
        # Record multiple feedbacks indicating content is too technical
        for i in range(5):
            record_query_feedback(
                user=self.user,
                query_text=f"Query {i}",
                intent="TEST",
                confidence=90,
                response_text="Response",
                response_data={},
                rating=3,
                feedback_type="TOO_TECHNICAL"
            )
        
        prefs = get_user_preferences(self.user)
        self.assertEqual(prefs.preferred_detail_level, 'BRIEF')
    
    def test_learn_detail_level_detailed(self):
        """Test learning DETAILED preference from INCOMPLETE feedback"""
        # Record multiple feedbacks indicating content is incomplete
        for i in range(5):
            record_query_feedback(
                user=self.user,
                query_text=f"Query {i}",
                intent="TEST",
                confidence=90,
                response_text="Response",
                response_data={},
                rating=3,
                feedback_type="INCOMPLETE"
            )
        
        prefs = get_user_preferences(self.user)
        self.assertEqual(prefs.preferred_detail_level, 'DETAILED')
    
    def test_average_satisfaction_calculation(self):
        """Test average satisfaction rating calculation"""
        # Record feedbacks with various ratings
        ratings = [5, 4, 5, 3, 4]
        for rating in ratings:
            record_query_feedback(
                user=self.user,
                query_text="Test",
                intent="TEST",
                confidence=90,
                response_text="Response",
                response_data={},
                rating=rating
            )
        
        prefs = get_user_preferences(self.user)
        expected_avg = sum(ratings) / len(ratings)
        self.assertEqual(float(prefs.avg_satisfaction_rating), expected_avg)
    
    def test_most_common_intent_tracking(self):
        """Test tracking most common query intent"""
        # Record multiple feedbacks with same intent
        for i in range(10):
            record_query_feedback(
                user=self.user,
                query_text=f"Query {i}",
                intent="STAFF_AVAILABILITY",
                confidence=90,
                response_text="Response",
                response_data={},
                rating=4
            )
        
        # Record fewer with different intent
        for i in range(3):
            record_query_feedback(
                user=self.user,
                query_text=f"Query {i}",
                intent="LEAVE_BALANCE",
                confidence=90,
                response_text="Response",
                response_data={},
                rating=4
            )
        
        prefs = get_user_preferences(self.user)
        self.assertEqual(prefs.most_common_intent, "STAFF_AVAILABILITY")


class PersonalizationTests(TestCase):
    """Test response personalization functionality"""
    
    def setUp(self):
        """Create test user with preferences"""
        self.role = Role.objects.create(name='Carer', is_management=False)
        self.user = User.objects.create_user(
            sap='TEST003',
            password='testpass123',
            first_name='Bob',
            last_name='Jones',
            email='bob@example.com',
            role=self.role
        )
        self.prefs = UserPreference.objects.create(
            user=self.user,
            preferred_detail_level='BRIEF',
            preferred_tone='FORMAL'
        )
    
    def test_brief_personalization(self):
        """Test BRIEF detail level truncates response"""
        long_response = "\n".join([f"Line {i}" for i in range(10)])
        
        result = personalize_response(
            user=self.user,
            response_text=long_response,
            response_data={}
        )
        
        # Should be truncated to 5 lines + tip
        lines = result['response'].split('\n')
        self.assertLessEqual(len([l for l in lines if l.startswith('Line')]), 5)
        self.assertIn('Tip', result['response'])
    
    def test_formal_tone_personalization(self):
        """Test FORMAL tone replaces casual language"""
        casual_response = "💡 Tip: Great! Check this out."
        
        result = personalize_response(
            user=self.user,
            response_text=casual_response,
            response_data={}
        )
        
        # Should replace casual markers
        self.assertNotIn('💡 Tip:', result['response'])
        self.assertIn('📋 Note:', result['response'])
        self.assertNotIn('Great!', result['response'])
        self.assertIn('Confirmed', result['response'])
    
    def test_friendly_tone_personalization(self):
        """Test FRIENDLY tone adds greeting"""
        self.prefs.preferred_tone = 'FRIENDLY'
        self.prefs.save()
        
        response = "Here are 3 staff members."
        
        result = personalize_response(
            user=self.user,
            response_text=response,
            response_data={}
        )
        
        # Should add friendly greeting
        self.assertTrue(result['response'].startswith('👋'))
    
    def test_personalization_style_metadata(self):
        """Test personalization returns style metadata"""
        result = personalize_response(
            user=self.user,
            response_text="Test",
            response_data={}
        )
        
        self.assertIn('style', result)
        self.assertEqual(result['style']['detail_level'], 'BRIEF')
        self.assertEqual(result['style']['tone'], 'FORMAL')


class AnalyticsTests(TestCase):
    """Test analytics calculation functionality"""
    
    def setUp(self):
        """Create test data"""
        self.role = Role.objects.create(name='Carer', is_management=False)
        self.user1 = User.objects.create_user(
            sap='TEST004',
            password='testpass123',
            first_name='User',
            last_name='One',
            email='user1@example.com',
            role=self.role
        )
        self.user2 = User.objects.create_user(
            sap='TEST005',
            password='testpass123',
            first_name='User',
            last_name='Two',
            email='user2@example.com',
            role=self.role
        )
        
        # Create feedback data
        self._create_test_feedback()
    
    def _create_test_feedback(self):
        """Create test feedback entries"""
        # User 1: Mostly positive
        for i in range(8):
            record_query_feedback(
                user=self.user1,
                query_text=f"Query {i}",
                intent="STAFF_AVAILABILITY",
                confidence=90,
                response_text="Response",
                response_data={},
                rating=5
            )
        
        # User 1: Some negative
        for i in range(2):
            record_query_feedback(
                user=self.user1,
                query_text=f"Query {i}",
                intent="LEAVE_BALANCE",
                confidence=80,
                response_text="Response",
                response_data={},
                rating=2
            )
        
        # User 2: Mixed
        for i in range(5):
            record_query_feedback(
                user=self.user2,
                query_text=f"Query {i}",
                intent="SHIFT_SEARCH",
                confidence=85,
                response_text="Response",
                response_data={},
                rating=3
            )
    
    def test_analytics_total_counts(self):
        """Test total query and feedback counts"""
        analytics = get_feedback_analytics(days=30)
        
        self.assertEqual(analytics['total_queries'], 15)  # 10 + 5
    
    def test_analytics_average_rating(self):
        """Test average rating calculation"""
        analytics = get_feedback_analytics(user=self.user1, days=30)
        
        # User 1: 8x5 + 2x2 = 44 / 10 = 4.4
        self.assertEqual(analytics['avg_rating'], 4.4)
    
    def test_analytics_satisfaction_rate(self):
        """Test satisfaction rate calculation (rating >= 4)"""
        analytics = get_feedback_analytics(user=self.user1, days=30)
        
        # User 1: 8 out of 10 are >= 4
        self.assertEqual(analytics['satisfaction_rate'], 80.0)
    
    def test_analytics_by_intent(self):
        """Test analytics grouped by intent"""
        analytics = get_feedback_analytics(days=30)
        
        self.assertIn('STAFF_AVAILABILITY', analytics['by_intent'])
        self.assertEqual(analytics['by_intent']['STAFF_AVAILABILITY']['count'], 8)
        self.assertEqual(analytics['by_intent']['STAFF_AVAILABILITY']['avg_rating'], 5.0)
    
    def test_analytics_improvement_needed(self):
        """Test identification of low-performing intents"""
        analytics = get_feedback_analytics(days=30)
        
        # LEAVE_BALANCE has 2 ratings of 2
        improvement = analytics['improvement_needed']
        self.assertTrue(any(item['intent'] == 'LEAVE_BALANCE' for item in improvement))
    
    def test_analytics_date_filtering(self):
        """Test analytics respects date range"""
        # Create old feedback (outside date range - 91 days ago)
        old_feedback = AIQueryFeedback.objects.create(
            user=self.user1,
            query_text="Old query",
            intent_detected="TEST",
            confidence_score=90,
            response_text="Response",
            rating=5,
            created_at=timezone.now() - timedelta(days=91)
        )
        
        analytics = get_feedback_analytics(days=30)
        
        # Should not include old feedback
        self.assertEqual(analytics['total_queries'], 15)  # Not 16


class InsightsTests(TestCase):
    """Test learning insights functionality"""
    
    def setUp(self):
        """Create test data with varied performance"""
        self.role = Role.objects.create(name='Carer', is_management=False)
        self.user = User.objects.create_user(
            sap='TEST006',
            password='testpass123',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            role=self.role
        )
        
        # Create high-performing intent
        for i in range(10):
            record_query_feedback(
                user=self.user,
                query_text=f"Query {i}",
                intent="STAFF_AVAILABILITY",
                confidence=95,
                response_text="Response",
                response_data={},
                rating=5
            )
        
        # Create low-performing intent
        for i in range(10):
            record_query_feedback(
                user=self.user,
                query_text=f"Query {i}",
                intent="LEAVE_BALANCE",
                confidence=70,
                response_text="Response",
                response_data={},
                rating=2
            )
    
    def test_insights_high_performing(self):
        """Test identification of high-performing intents"""
        insights = get_learning_insights(min_feedback_count=5)
        
        high_performing = insights['high_performing_intents']
        self.assertTrue(len(high_performing) > 0)
        self.assertTrue(any(
            intent['intent'] == 'STAFF_AVAILABILITY' and intent['avg_rating'] == 5.0
            for intent in high_performing
        ))
    
    def test_insights_low_performing(self):
        """Test identification of low-performing intents"""
        insights = get_learning_insights(min_feedback_count=5)
        
        low_performing = insights['low_performing_intents']
        self.assertTrue(len(low_performing) > 0)
        self.assertTrue(any(
            intent['intent'] == 'LEAVE_BALANCE' and intent['avg_rating'] == 2.0
            for intent in low_performing
        ))
    
    def test_insights_recommendations(self):
        """Test generation of improvement recommendations"""
        insights = get_learning_insights(min_feedback_count=5)
        
        recommendations = insights['recommendations']
        self.assertTrue(len(recommendations) > 0)
        self.assertTrue(any(
            'LEAVE_BALANCE' in rec
            for rec in recommendations
        ))


class APIEndpointTests(TestCase):
    """Test API endpoint functionality"""
    
    def setUp(self):
        """Create test user and client"""
        self.client = Client()
        self.role = Role.objects.create(name='Carer', is_management=False)
        self.user = User.objects.create_user(
            sap='TEST007',
            password='testpass123',
            first_name='API',
            last_name='User',
            email='api@example.com',
            role=self.role
        )
        # Use force_login to bypass Axes backend issues in tests
        self.client.force_login(self.user)
    
    def test_submit_feedback_api(self):
        """Test POST /api/ai-assistant/feedback/"""
        data = {
            'query_text': 'Who can work tomorrow?',
            'intent_detected': 'STAFF_AVAILABILITY',
            'confidence_score': 0.95,
            'response_text': '3 staff members available',
            'response_data': {'count': 3},
            'rating': 5,
            'feedback_type': 'HELPFUL',
            'feedback_comment': 'Great response'
        }
        
        response = self.client.post(
            '/api/ai-assistant/feedback/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        result = json.loads(response.content)
        self.assertIn('feedback_id', result)
        self.assertTrue(result['preferences_updated'])
        
        # Verify feedback was created
        self.assertTrue(AIQueryFeedback.objects.filter(user=self.user).exists())
    
    def test_submit_feedback_api_missing_field(self):
        """Test API returns 400 for missing required fields"""
        data = {
            'query_text': 'Test',
            # Missing required fields
        }
        
        response = self.client.post(
            '/api/ai-assistant/feedback/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.content)
        self.assertIn('error', result)
    
    def test_submit_feedback_api_invalid_rating(self):
        """Test API validates rating range (1-5)"""
        data = {
            'query_text': 'Test',
            'intent_detected': 'TEST',
            'confidence_score': 0.9,
            'response_text': 'Response',
            'rating': 10,  # Invalid
        }
        
        response = self.client.post(
            '/api/ai-assistant/feedback/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_analytics_api(self):
        """Test GET /api/ai-assistant/analytics/"""
        # Create test feedback
        record_query_feedback(
            user=self.user,
            query_text="Test",
            intent="TEST",
            confidence=90,
            response_text="Response",
            response_data={},
            rating=5
        )
        
        response = self.client.get('/api/ai-assistant/analytics/?days=30')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertIn('total_queries', result)
        self.assertIn('avg_rating', result)
        self.assertIn('satisfaction_rate', result)
        self.assertEqual(result['period_days'], 30)
    
    def test_analytics_api_custom_period(self):
        """Test analytics API with custom date range"""
        response = self.client.get('/api/ai-assistant/analytics/?days=7')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['period_days'], 7)
    
    def test_insights_api_requires_auth(self):
        """Test insights API requires authentication"""
        self.client.logout()
        
        response = self.client.get('/api/ai-assistant/insights/')
        
        # Should redirect to login or return 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_insights_api_requires_senior_staff(self):
        """Test insights API requires Senior Staff or Admin role"""
        # Regular user (not senior)
        response = self.client.get('/api/ai-assistant/insights/')
        
        self.assertEqual(response.status_code, 403)
        result = json.loads(response.content)
        self.assertIn('error', result)
        self.assertIn('Insufficient permissions', result['error'])


class IntegrationTests(TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        """Create test environment"""
        self.client = Client()
        self.role = Role.objects.create(name='Carer', is_management=False)
        self.user = User.objects.create_user(
            sap='TEST008',
            password='testpass123',
            first_name='Integration',
            last_name='Test',
            email='integration@example.com',
            role=self.role
        )
        # Use force_login to bypass Axes backend issues in tests
        self.client.force_login(self.user)
    
    def test_full_feedback_workflow(self):
        """Test complete feedback submission and learning workflow"""
        # Step 1: Submit multiple feedbacks
        for i in range(5):
            data = {
                'query_text': f'Query {i}',
                'intent_detected': 'STAFF_AVAILABILITY',
                'confidence_score': 0.95,
                'response_text': f'Response {i}',
                'response_data': {},
                'rating': 5,
                'feedback_type': 'HELPFUL'
            }
            response = self.client.post(
                '/api/ai-assistant/feedback/',
                data=json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
        
        # Step 2: Check preferences were learned
        prefs = UserPreference.objects.get(user=self.user)
        self.assertEqual(prefs.total_queries, 5)
        self.assertEqual(float(prefs.avg_satisfaction_rating), 5.0)
        
        # Step 3: Check analytics reflect the data
        response = self.client.get('/api/ai-assistant/analytics/')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['total_queries'], 5)
        self.assertEqual(result['avg_rating'], 5.0)
        self.assertEqual(result['satisfaction_rate'], 100.0)
    
    def test_personalization_adapts_to_feedback(self):
        """Test that personalization changes based on feedback patterns"""
        # Submit feedback indicating content is too technical
        for i in range(5):
            record_query_feedback(
                user=self.user,
                query_text=f'Query {i}',
                intent='TEST',
                confidence=90,
                response_text='Response',
                response_data={},
                rating=3,
                feedback_type='TOO_TECHNICAL'
            )
        
        # Check preferences learned BRIEF preference
        prefs = get_user_preferences(self.user)
        self.assertEqual(prefs.preferred_detail_level, 'BRIEF')
        
        # Test personalization applies BRIEF style
        long_response = "\n".join([f"Line {i}" for i in range(10)])
        result = personalize_response(self.user, long_response, {})
        
        # Should be truncated
        lines = [l for l in result['response'].split('\n') if l.startswith('Line')]
        self.assertLessEqual(len(lines), 5)


# Run tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["scheduling.tests_task11_feedback"])
