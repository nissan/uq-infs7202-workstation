"""
Utility functions for disabling middleware during tests.

This module provides functions to disable middleware components
that might interfere with testing, such as CORS and CSRF.
"""
from django.test import override_settings
from django.conf import settings

def get_middleware_without_auth():
    """Return middleware list without authentication middleware."""
    return [
        m for m in settings.MIDDLEWARE if m not in [
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware'
        ]
    ]

def get_middleware_without_cors_csrf():
    """Return middleware list without CORS and CSRF middleware."""
    return [
        m for m in settings.MIDDLEWARE if m not in [
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware'
        ]
    ]

# Custom decorator to disable all authentication middleware
disable_auth_middleware = override_settings(
    MIDDLEWARE=get_middleware_without_auth(),
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PERMISSION_CLASSES': [],
        'UNAUTHENTICATED_USER': None,
    },
    SIMPLE_JWT={
        'ACCESS_TOKEN_LIFETIME': None,
        'REFRESH_TOKEN_LIFETIME': None,
    }
)

# Custom decorator to disable CORS and CSRF middleware
disable_cors_csrf = override_settings(
    MIDDLEWARE=get_middleware_without_cors_csrf(),
    CORS_ALLOW_ALL_ORIGINS=True,
    CORS_ALLOW_CREDENTIALS=True,
    CORS_ORIGIN_ALLOW_ALL=True,
    CSRF_COOKIE_SECURE=False,
    CSRF_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SECURE=False
)