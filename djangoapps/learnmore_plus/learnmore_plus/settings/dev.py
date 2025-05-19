"""
Development settings for the LearnMore Plus project.
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Debug Toolbar and Django Extensions
INSTALLED_APPS += ['django_extensions']  # Temporarily disabled debug_toolbar
# MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE  # Temporarily disabled
INTERNAL_IPS = ['127.0.0.1']

import sys

# Don't show debug toolbar during tests
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True if 'test' not in sys.argv else False,
    'RENDER_PANELS': False,
    'DISABLE_PANELS': {'debug_toolbar.panels.redirects.RedirectsPanel'},
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files
MEDIA_ROOT = BASE_DIR / 'media'

# Security
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False 