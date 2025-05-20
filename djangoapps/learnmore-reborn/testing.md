# Testing Fixes

Based on our investigation, there are several issues with the test suite:

1. The Django REST Framework (DRF) authentication is preventing the tests from running properly. Even though we're trying to override the settings, the middleware is still checking for authentication.

2. Some tests are expecting different behavior than what the views are actually implementing.

## Fix Strategy

1. Create a pull request with the following changes:

   - Update the test settings to properly disable DRF authentication
   - Use the test_settings_override decorator on all test classes
   - Fix test cases to match the expected behavior of the views

2. Add a special testing configuration that can be used in CI/CD pipelines.

## Key Files

- `test_auth_settings.py` - Contains settings overrides for tests
- `test_django_views.py` - Test cases for Django template views
- `test_views.py` - Alternative test approach with more explicit authentication

## Running Tests

To run tests with the correct settings, use:

```bash
# Run all tests with authentication disabled
python manage.py test --settings=learnmore.test_settings

# Run specific tests with authentication disabled
python manage.py test courses.tests --settings=learnmore.test_settings
```

## Common Test Failures

1. 401 Unauthorized - DRF authentication is still active
2. 403 Forbidden - Permissions are still being checked
3. NoneType errors - Response context is not being properly set

## Testing with Client Login vs. JWT

The tests use Django's built-in client login method, which uses session-based authentication. However, the API uses JWT token authentication. For API tests, we need to use:

```python
# JWT token authentication in tests
def login_api(self, user=None):
    """Get JWT token and set appropriate headers."""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    if user is None:
        user = self.user
        
    refresh = RefreshToken.for_user(user)
    self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
```