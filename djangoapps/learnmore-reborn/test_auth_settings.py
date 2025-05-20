"""
Custom settings module for authenticated testing.

This provides a decorator and a settings class that can be used to override
the authentication and permission settings for testing.
"""
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.conf import settings
from datetime import timedelta
from test_client import TestClient

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
        # Only stop patchers if they were successfully started
        if hasattr(cls, 'drf_patcher') and cls.drf_patcher:
            try:
                cls.drf_patcher.stop()
            except AttributeError:
                pass
                
        if hasattr(cls, 'drf_auth_patcher') and cls.drf_auth_patcher:
            try:
                cls.drf_auth_patcher.stop()
            except AttributeError:
                pass
                
        if hasattr(cls, 'middleware_patcher') and cls.middleware_patcher:
            try:
                cls.middleware_patcher.stop()
            except AttributeError:
                pass
        
        super().tearDownClass()
        
    def setUp(self):
        """Set up test user"""
        super().setUp()
        
        # Replace the default client with our custom TestClient
        self.client = TestClient()
        
        # Force Django settings into TEST_MODE
        from django.conf import settings
        settings.TEST_MODE = True
        
        # Ensure CSRF middleware is disabled
        if 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE:
            settings.MIDDLEWARE = [
                middleware for middleware in settings.MIDDLEWARE
                if middleware != 'django.middleware.csrf.CsrfViewMiddleware'
            ]
            
        # Override authentication and permission classes
        settings.REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': [],
            'DEFAULT_PERMISSION_CLASSES': [],
            'UNAUTHENTICATED_USER': None
        }
        
        # Add a flag to bypass CSRF in request
        original_get = self.client.get
        original_post = self.client.post
        
        def get_with_bypass(path, *args, **kwargs):
            response = original_get(path, *args, **kwargs)
            # Set a marker on the response to indicate it's from a test
            response._test_response = True
            return response
            
        def post_with_bypass(path, *args, **kwargs):
            response = original_post(path, *args, **kwargs)
            # Set a marker on the response to indicate it's from a test
            response._test_response = True
            return response
            
        self.client.get = get_with_bypass
        self.client.post = post_with_bypass