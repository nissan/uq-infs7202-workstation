"""
Test settings for LearnMore project.

This file contains settings that override the main settings for testing.
"""

from .settings import *  # Import all settings from main settings file

# Override REST_FRAMEWORK settings for testing
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Allow unauthenticated access during tests
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    # Keep default pagination settings
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Use in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable any background tasks or slow features during tests
CELERY_TASK_ALWAYS_EAGER = True

# Turn off logging during tests
import logging
logging.disable(logging.CRITICAL)

# Set DEBUG to False for testing
DEBUG = False

# Turn off the CSRF validation for test client
# This makes it easier to test POST requests
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'django.middleware.csrf.CsrfViewMiddleware']