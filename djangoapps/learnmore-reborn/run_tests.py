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
    
    # Get the test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # Run tests
    failures = test_runner.run_tests(sys.argv[1:] or ['test_django_views'])
    
    # Exit with appropriate code
    sys.exit(bool(failures))

if __name__ == '__main__':
    main()