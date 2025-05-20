"""
Custom settings module for authenticated testing.

This provides a decorator and a settings class that can be used to override
the authentication and permission settings for testing.
"""
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.conf import settings
from datetime import timedelta

# Create a comprehensive settings override that disables all authentication and permissions
test_settings_override = override_settings(
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PERMISSION_CLASSES': [],
        'UNAUTHENTICATED_USER': None,
    },
    # Disable JWT settings
    SIMPLE_JWT={
        'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
        'AUTH_HEADER_TYPES': ('Bearer',),
        'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    },
    # Remove CORS and CSRF middleware
    MIDDLEWARE=[
        m for m in settings.MIDDLEWARE if m not in [
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware'
        ]
    ],
    # Allow all CORS origins
    CORS_ALLOW_ALL_ORIGINS=True,
    CORS_ALLOW_CREDENTIALS=True,
    DEBUG=True,
)

class AuthDisabledTestCase(TestCase):
    """A TestCase that disables JWT authentication for testing."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test case with patched settings."""
        # Create patchers for REST framework settings
        cls.drf_patcher = patch('rest_framework.settings.api_settings.DEFAULT_PERMISSION_CLASSES', [])
        cls.drf_auth_patcher = patch('rest_framework.settings.api_settings.DEFAULT_AUTHENTICATION_CLASSES', [])
        
        # Start patchers
        cls.drf_patcher.start()
        cls.drf_auth_patcher.start()
        
        # Patch MIDDLEWARE to remove CORS and CSRF
        cls.middleware_patcher = patch('django.conf.settings.MIDDLEWARE', [
            m for m in settings.MIDDLEWARE if m not in [
                'corsheaders.middleware.CorsMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware'
            ]
        ])
        cls.middleware_patcher.start()
        
        super().setUpClass()
    
    @classmethod
    def tearDownClass(cls):
        """Tear down the test case and stop patchers."""
        # Stop patchers
        cls.drf_patcher.stop()
        cls.drf_auth_patcher.stop()
        cls.middleware_patcher.stop()
        
        super().tearDownClass()
        
    def setUp(self):
        """Set up test user"""
        super().setUp()
        
        # Force client to ignore CSRF
        self.client.handler.enforce_csrf_checks = False