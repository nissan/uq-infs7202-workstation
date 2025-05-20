"""
Authentication utilities for progress app tests.
"""
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user for testing.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class AuthClientMixin:
    """Mixin to add authentication methods to test cases."""
    
    def setUp(self):
        """Set up the test case with an API client."""
        super().setUp()
        self.api_client = APIClient()
    
    def authenticate_with_token(self, user):
        """
        Authenticate the API client with JWT tokens.
        """
        tokens = get_tokens_for_user(user)
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        return self.api_client
    
    def force_authenticate(self, user):
        """
        Force authenticate without JWT tokens.
        This is useful for tests where we want to bypass JWT authentication.
        """
        self.api_client.force_authenticate(user=user)
        return self.api_client