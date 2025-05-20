"""
Custom test case for LearnMore Reborn tests.

This module provides a custom TestCase that handles authentication
for both template and API tests.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken
from test_auth_settings import AuthDisabledTestCase
from api_test_utils import APITestCaseBase

User = get_user_model()

class AuthenticatedTestCase(AuthDisabledTestCase):
    """
    A test case that sets up authenticated clients.
    
    This class provides:
    1. self.client - A Django test client with session auth
    2. self.api_client - A DRF API client with JWT auth
    3. Helper methods for authentication
    """
    
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.api_client = APIClient()
        
        # Create a test user if one doesn't exist
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a test admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True,
            is_superuser=True
        )
        
        # Create a test instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructorpass'
        )
        # Set instructor flag if profile exists
        if hasattr(self.instructor, 'profile'):
            self.instructor.profile.is_instructor = True
            self.instructor.profile.save()
    
    def login(self, user=None):
        """
        Log in with the specified user using session auth.
        
        If no user is specified, logs in with the default test user.
        This affects the regular Django test client.
        """
        if user is None:
            user = self.user
        
        # Login with the Django test client (session auth)
        self.client.login(username=user.username, password='testpassword')
    
    def login_api(self, user=None):
        """
        Log in with the specified user using JWT auth.
        
        If no user is specified, logs in with the default test user.
        This affects the API client.
        """
        if user is None:
            user = self.user
        
        # Get JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        
        # Set the Authorization header
        self.api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
        )
    
    def login_admin(self):
        """Log in as an admin user."""
        self.login(self.admin_user)
        self.login_api(self.admin_user)
    
    def login_instructor(self):
        """Log in as an instructor."""
        self.login(self.instructor)
        self.login_api(self.instructor)
        
    def logout(self):
        """Log out from both clients."""
        self.client.logout()
        self.api_client.credentials()