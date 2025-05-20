#!/usr/bin/env python
"""
Standalone test runner for the progress app tests.
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

# Run the tests
if __name__ == '__main__':
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests(['progress.tests.test_model_base'])
    sys.exit(failures)