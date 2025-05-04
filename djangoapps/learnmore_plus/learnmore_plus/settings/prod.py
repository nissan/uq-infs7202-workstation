"""
Production settings for the LearnMore Plus project.
"""
import os
import dj_database_url
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# If SECRET_KEY is not found in environment, use a default (but highly recommend setting in env)
if 'SECRET_KEY' not in os.environ:
    SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-railway-deployment')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,.railway.app,127.0.0.1').split(',')

# Database configuration using DATABASE_URL for Railway
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600
        )
    }
else:
    # Fallback to SQLite for testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Security - some settings relaxed for initial deployment
# Enable these after confirming the application works
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = bool(os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True')
SESSION_COOKIE_SECURE = bool(os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True')
CSRF_COOKIE_SECURE = bool(os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Configure middleware for WhiteNoise
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    # Add WhiteNoise middleware - ensure it's only added once
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
    ] + [m for m in MIDDLEWARE if m != 'django.middleware.security.SecurityMiddleware']

# Use WhiteNoise for static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/tmp/django-errors.log',  # Changed for Railway compatibility
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}