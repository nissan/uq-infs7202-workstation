# Testing Setup

This document explains how to run tests with custom settings.

## Special Settings for Testing

We use a custom test settings file located at `learnmore/test_settings.py` that overrides the default settings for testing. This includes:

1. Allowing unauthenticated access during tests
2. Using an in-memory SQLite database for faster tests
3. Disabling logging and warnings
4. Skipping CSRF validation

## Running Tests with Custom Settings

To run tests with these custom settings, use:

```bash
DJANGO_SETTINGS_MODULE=learnmore.test_settings python manage.py test
```

Or use our custom test runner script:

```bash
./run_tests.sh
```

## Authentication in Tests

For tests that need authenticated users, we provide a custom `AuthenticatedTestCase` class in `courses/tests/test_case.py` that:

1. Sets up test users (regular, instructor, admin)
2. Provides login/logout helpers for Django templates and DRF APIs 
3. Handles JWT authentication for API tests

Example usage:

```python
from courses.tests.test_case import AuthenticatedTestCase

class MyTests(AuthenticatedTestCase):
    def test_something(self):
        # Log in for template tests
        self.login()
        
        # Log in for API tests
        self.login_api()
        
        # Test your view...
        response = self.client.get('/my-view/')
        self.assertEqual(response.status_code, 200)
```