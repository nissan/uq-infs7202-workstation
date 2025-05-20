"""
Test settings for Progress app tests.
"""
from django.test import TestCase, override_settings

# Create a comprehensive settings override that disables all authentication and permissions
test_settings = {
    'REST_FRAMEWORK': {
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PERMISSION_CLASSES': [],
    },
}

# Decorator to apply the test settings
progress_test_settings = override_settings(**test_settings)