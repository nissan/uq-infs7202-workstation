from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from ..middleware import AnalyticsMiddleware
from ..models import UserActivity
from .factories import UserFactory

class AnalyticsMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = AnalyticsMiddleware(get_response=lambda r: None)
        self.user = UserFactory()
    
    def test_anonymous_user_activity(self):
        """Test that anonymous user activity is tracked"""
        request = self.factory.get('/')
        request.user = None
        request.META = {
            'HTTP_USER_AGENT': 'Mozilla/5.0',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        self.middleware(request)
        
        activity = UserActivity.objects.first()
        self.assertIsNotNone(activity)
        self.assertIsNone(activity.user)
        self.assertEqual(activity.activity_type, 'page_view')
        self.assertEqual(activity.ip_address, '127.0.0.1')
        self.assertEqual(activity.user_agent, 'Mozilla/5.0')
    
    def test_authenticated_user_activity(self):
        """Test that authenticated user activity is tracked"""
        request = self.factory.get('/')
        request.user = self.user
        request.META = {
            'HTTP_USER_AGENT': 'Mozilla/5.0',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        self.middleware(request)
        
        activity = UserActivity.objects.first()
        self.assertIsNotNone(activity)
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.activity_type, 'page_view')
        self.assertEqual(activity.ip_address, '127.0.0.1')
        self.assertEqual(activity.user_agent, 'Mozilla/5.0')
    
    def test_activity_details(self):
        """Test that activity details are properly captured"""
        request = self.factory.get('/courses/1/')
        request.user = self.user
        request.META = {
            'HTTP_USER_AGENT': 'Mozilla/5.0',
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_REFERER': 'http://example.com/'
        }
        
        self.middleware(request)
        
        activity = UserActivity.objects.first()
        self.assertIsNotNone(activity)
        self.assertEqual(activity.activity_type, 'page_view')
        self.assertIn('path', activity.details)
        self.assertEqual(activity.details['path'], '/courses/1/')
        self.assertIn('referer', activity.details)
        self.assertEqual(activity.details['referer'], 'http://example.com/')
    
    def test_activity_throttling(self):
        """Test that activity tracking is throttled for frequent requests"""
        request = self.factory.get('/')
        request.user = self.user
        request.META = {
            'HTTP_USER_AGENT': 'Mozilla/5.0',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        # Make multiple requests in quick succession
        for _ in range(5):
            self.middleware(request)
        
        # Should only have one activity record due to throttling
        self.assertEqual(UserActivity.objects.count(), 1)
    
    def test_activity_exclusion(self):
        """Test that certain paths are excluded from activity tracking"""
        # Test static file exclusion
        request = self.factory.get('/static/css/style.css')
        request.user = self.user
        request.META = {
            'HTTP_USER_AGENT': 'Mozilla/5.0',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        self.middleware(request)
        self.assertEqual(UserActivity.objects.count(), 0)
        
        # Test media file exclusion
        request = self.factory.get('/media/uploads/image.jpg')
        self.middleware(request)
        self.assertEqual(UserActivity.objects.count(), 0)
        
        # Test admin file exclusion
        request = self.factory.get('/admin/static/admin/css/base.css')
        self.middleware(request)
        self.assertEqual(UserActivity.objects.count(), 0)
    
    def test_activity_session_tracking(self):
        """Test that session information is properly tracked"""
        request = self.factory.get('/')
        request.user = self.user
        request.META = {
            'HTTP_USER_AGENT': 'Mozilla/5.0',
            'REMOTE_ADDR': '127.0.0.1'
        }
        request.session = {'sessionid': 'test-session-id'}
        
        self.middleware(request)
        
        activity = UserActivity.objects.first()
        self.assertIsNotNone(activity)
        self.assertEqual(activity.session_id, 'test-session-id')
    
    def test_activity_error_handling(self):
        """Test that middleware handles errors gracefully"""
        # Test with invalid user agent
        request = self.factory.get('/')
        request.user = self.user
        request.META = {
            'HTTP_USER_AGENT': None,
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        self.middleware(request)
        
        activity = UserActivity.objects.first()
        self.assertIsNotNone(activity)
        self.assertIsNone(activity.user_agent)
        
        # Test with invalid IP address
        request.META = {
            'HTTP_USER_AGENT': 'Mozilla/5.0',
            'REMOTE_ADDR': None
        }
        
        self.middleware(request)
        
        activity = UserActivity.objects.first()
        self.assertIsNotNone(activity)
        self.assertIsNone(activity.ip_address) 