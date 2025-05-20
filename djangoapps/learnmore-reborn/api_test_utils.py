"""
API test utilities for LearnMore Reborn.

This module provides a base test case for API tests that automatically
disables authentication and permissions.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

class APITestCaseBase(TestCase):
    """Base test case that disables authentication and permissions for API tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        super().setUpClass()
    
    def setUp(self):
        """Set up test case with authentication disabled."""
        super().setUp()
        
        # Create an API client with CSRF checks disabled
        self.api_client = APIClient(enforce_csrf_checks=False)
        
        # Also disable CSRF checks for the Django test client
        self.client.handler.enforce_csrf_checks = False
        
        # Create a test user if needed
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
    
    def login_api(self, user=None):
        """
        Authenticate API client with the given user.
        
        This bypasses JWT token authentication.
        """
        user = user or self.user
        self.api_client.force_authenticate(user=user)
    
    def login(self, user=None):
        """Log in with the Django test client."""
        user = user or self.user
        self.client.login(username=user.username, password='testpassword')
    
    def login_instructor(self):
        """Log in as the instructor user."""
        self.login(self.instructor)
        self.login_api(self.instructor)
    
    def logout(self):
        """Log out from both clients."""
        self.client.logout()
        self.api_client.force_authenticate(user=None)