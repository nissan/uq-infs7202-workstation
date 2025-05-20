"""
API test utilities for LearnMore Reborn.

This module provides a base test case for API tests that automatically
disables authentication and permissions.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, force_authenticate
from rest_framework.test import APIRequestFactory
from django.test.utils import override_settings
from django.conf import settings
from test_auth_settings import test_settings_override

User = get_user_model()

@test_settings_override
class APITestCaseBase(TestCase):
    """Base test case that disables authentication and permissions for API tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        super().setUpClass()
    
    def setUp(self):
        """Set up test case with authentication disabled."""
        super().setUp()
        
        # Create a standard Django client with CSRF checks disabled
        self.client = Client(enforce_csrf_checks=False)
        
        # Create an API client with CSRF checks disabled
        self.api_client = APIClient(enforce_csrf_checks=False)
        
        # Create a request factory
        self.factory = APIRequestFactory()
        
        # The client to use - we set the Django client as default but tests can use api_client too
        self.client = self.api_client
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create an instructor user
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructorpass'
        )
        # Set instructor flag if profile model exists
        if hasattr(self.instructor, 'profile'):
            self.instructor.profile.is_instructor = True
            self.instructor.profile.save()
        
        # Override settings to disable authentication and permissions for tests
        self._patch_drf_settings()
    
    def _patch_drf_settings(self):
        """Override DRF settings to disable authentication."""
        settings.REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': [],
            'DEFAULT_PERMISSION_CLASSES': [],
            'UNAUTHENTICATED_USER': None
        }
    
    def login_api(self, user=None):
        """
        Authenticate API client with the given user.
        
        This bypasses JWT token authentication.
        """
        user = user or self.user
        self.client.force_authenticate(user=user)
    
    def login(self, user=None):
        """Log in with the Django test client."""
        user = user or self.user
        self.client.force_authenticate(user=user)
    
    def login_instructor(self):
        """Log in as the instructor user."""
        self.login(self.instructor)
    
    def logout(self):
        """Log out from both clients."""
        self.client.logout()
        self.client.force_authenticate(user=None)