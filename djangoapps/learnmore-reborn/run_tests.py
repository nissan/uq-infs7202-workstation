#!/usr/bin/env python
"""
Test runner script for LearnMore Reborn tests with authentication disabled.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def main():
    """Run tests with authentication and permissions disabled."""
    # Set the Django settings module
    os.environ['DJANGO_SETTINGS_MODULE'] = 'learnmore.test_settings'
    
    # Setup Django
    django.setup()
    
    # Override REST framework settings
    settings.REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PERMISSION_CLASSES': [],
        'UNAUTHENTICATED_USER': None
    }
    
    # Remove CORS and CSRF middleware
    settings.MIDDLEWARE = [
        m for m in settings.MIDDLEWARE if m not in [
            'corsheaders.middleware.CorsMiddleware', 
            'django.middleware.csrf.CsrfViewMiddleware'
        ]
    ]
    
    # Configure CORS settings
    settings.CORS_ALLOW_ALL_ORIGINS = True
    settings.CORS_ALLOW_CREDENTIALS = True
    settings.CORS_ORIGIN_ALLOW_ALL = True
    
    # Disable CSRF validation
    settings.CSRF_COOKIE_SECURE = False
    settings.CSRF_COOKIE_HTTPONLY = False
    settings.SESSION_COOKIE_SECURE = False
    
    # Get the test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # Set CSRF checks to False
    from django.test.client import Client
    Client.handler.enforce_csrf_checks = False
    
    # Run tests
    failures = test_runner.run_tests(sys.argv[1:] or ['courses.tests', 'test_django_views', 'test_views'])
    
    # Exit with appropriate code
    sys.exit(bool(failures))

if __name__ == '__main__':
    main()