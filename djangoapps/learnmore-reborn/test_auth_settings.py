"""
Custom settings module for authenticated testing.

This provides a decorator and a settings class that can be used to override
the authentication and permission settings for testing.
"""
from unittest.mock import patch
from django.test import TestCase, override_settings

class AuthenticatedTestCase(TestCase):
    """A TestCase that disables JWT authentication for testing."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test case with patched settings."""
        # Create patchers
        cls.drf_patcher = patch('rest_framework.settings.api_settings.DEFAULT_PERMISSION_CLASSES', [])
        cls.drf_auth_patcher = patch('rest_framework.settings.api_settings.DEFAULT_AUTHENTICATION_CLASSES', [])
        
        # Start patchers
        cls.drf_patcher.start()
        cls.drf_auth_patcher.start()
        
        super().setUpClass()
    
    @classmethod
    def tearDownClass(cls):
        """Tear down the test case and stop patchers."""
        # Stop patchers
        cls.drf_patcher.stop()
        cls.drf_auth_patcher.stop()
        
        super().tearDownClass()
        
# Decorator for view test classes
test_settings_override = override_settings(
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PERMISSION_CLASSES': [],
        'UNAUTHENTICATED_USER': None,
    },
    DEBUG=True,
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]
)