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

# Turn off the CSRF validation for test client
# This makes it easier to test POST requests
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'django.middleware.csrf.CsrfViewMiddleware']