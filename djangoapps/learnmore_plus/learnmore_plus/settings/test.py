"""
Test settings for the LearnMore Plus project.
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Disable debug toolbar in tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE = [m for m in MIDDLEWARE if not m.startswith('debug_toolbar.middleware')]

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Database - use in-memory SQLite for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Email - use dummy backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Static files - use SimpleStorage during tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Security - disable for tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False