"""
Test settings for LearnMore project.

This file contains settings that override the main settings for testing.
"""

from .settings import *  # Import all settings from main settings file

# Override REST_FRAMEWORK settings for testing
REST_FRAMEWORK = {
    # Disable authentication during tests
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    # Allow unauthenticated access during tests
    'DEFAULT_PERMISSION_CLASSES': [],
    # Keep default pagination settings
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'UNAUTHENTICATED_USER': None,  # This is important to avoid NoneType errors
}

# Disable JWT token requirement for tests
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# Use in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable any background tasks or slow features during tests
CELERY_TASK_ALWAYS_EAGER = True

# Turn off logging during tests
import logging
logging.disable(logging.CRITICAL)

# Set DEBUG to True for testing to see more error details
DEBUG = True

# Flag to identify test mode
TEST_MODE = True

# Completely replace middleware for tests
MIDDLEWARE = [
    'test_middleware.TestCSRFMiddleware',  # Our test middleware first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # No CSRF middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configure CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True  # Legacy setting

# Configure authentication settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Disable CSRF validation for tests
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False