# Using Pytest to Fix Authentication Issues in Tests

Pytest provides several powerful features that can help fix the authentication issues in our tests. This document outlines how to set up pytest and leverage its features to address our specific challenges.

## Setting Up Pytest

1. Install pytest and pytest-django:

```bash
pip install pytest pytest-django pytest-mock
```

2. Create a `pytest.ini` file at the project root:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = learnmore.test_settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    api: marks tests as API tests
    template: marks tests as template tests
    integration: marks tests as integration tests
```

3. Create or update `learnmore/test_settings.py` to override authentication settings:

```python
from learnmore.settings import *

# Disable JWT authentication for tests
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'UNAUTHENTICATED_USER': None,
}
```

## Pytest Fixtures for Authentication

Create fixtures in `conftest.py` for authentication:

```python
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()

@pytest.fixture
def user():
    """Create and return a regular user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword'
    )

@pytest.fixture
def instructor():
    """Create and return an instructor user."""
    instructor = User.objects.create_user(
        username='instructor',
        email='instructor@example.com',
        password='instructorpass'
    )
    if hasattr(instructor, 'profile'):
        instructor.profile.is_instructor = True
        instructor.profile.save()
    return instructor

@pytest.fixture
def authenticated_client(client, user):
    """Return a Django test client with a logged in user."""
    client.login(username='testuser', password='testpassword')
    return client

@pytest.fixture
def authenticated_api_client(api_client, user):
    """Return an API client with a logged in user."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client
```

## Pytest Fixtures for Test Data

Create fixtures for test data:

```python
import pytest
from courses.models import Course, Module, Quiz, Enrollment

@pytest.fixture
def course(instructor):
    """Create and return a test course."""
    return Course.objects.create(
        title='Test Course',
        slug='test-course',
        description='A test course',
        status='published',
        enrollment_type='open',
        instructor=instructor
    )

@pytest.fixture
def module(course):
    """Create and return a test module."""
    return Module.objects.create(
        title='Test Module',
        course=course,
        order=1
    )

@pytest.fixture
def quiz(module):
    """Create and return a test quiz."""
    return Quiz.objects.create(
        title='Test Quiz',
        module=module,
        description='Test quiz description'
    )

@pytest.fixture
def enrollment(user, course):
    """Create and return a test enrollment."""
    return Enrollment.objects.create(
        user=user,
        course=course,
        status='active'
    )
```

## Pytest Monkeypatching

Pytest provides powerful monkeypatching capabilities that can help bypass authentication:

```python
@pytest.fixture
def bypass_auth(monkeypatch):
    """Bypass authentication checks in views and APIs."""
    from rest_framework.permissions import IsAuthenticated
    
    # Make IsAuthenticated always return True
    def has_permission(*args, **kwargs):
        return True
    
    monkeypatch.setattr(IsAuthenticated, 'has_permission', has_permission)
    
    # For custom permissions like IsInstructorOrReadOnly
    from courses.api_views import IsInstructorOrReadOnly
    monkeypatch.setattr(IsInstructorOrReadOnly, 'has_permission', has_permission)
    monkeypatch.setattr(IsInstructorOrReadOnly, 'has_object_permission', has_permission)
```

## Example Test Using Pytest

Here's an example of how to rewrite a test using pytest:

```python
import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.template
def test_course_catalog_renders(authenticated_client, course):
    """Test course catalog page renders correctly."""
    response = authenticated_client.get(reverse('course-catalog'))
    
    assert response.status_code == 200
    assert 'courses' in response.context
    assert course in response.context['courses']

@pytest.mark.api
def test_course_catalog_api(authenticated_api_client, course):
    """Test course catalog API endpoint."""
    response = authenticated_api_client.get('/api/courses/catalog/')
    
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == course.title

@pytest.mark.integration
def test_api_and_template_consistency(authenticated_client, authenticated_api_client, course):
    """Test API and template consistency."""
    # Get template response
    template_url = reverse('course-detail', kwargs={'slug': course.slug})
    template_response = authenticated_client.get(template_url)
    
    # Get API response
    api_url = f'/api/courses/courses/{course.slug}/'
    api_response = authenticated_api_client.get(api_url)
    
    # Verify consistency
    assert template_response.status_code == 200
    assert api_response.status_code == status.HTTP_200_OK
    assert template_response.context['course'].title == api_response.data['title']
    assert template_response.context['course'].description == api_response.data['description']
```

## Using Parametrized Tests

Pytest's parameterized tests are great for testing multiple scenarios:

```python
import pytest

@pytest.mark.parametrize('status_value,is_active_expected', [
    ('published', True),
    ('draft', False),
    ('archived', False),
])
def test_course_is_active(instructor, status_value, is_active_expected):
    """Test is_active property with different status values."""
    course = Course.objects.create(
        title='Test Course',
        slug='test-course',
        status=status_value,
        instructor=instructor
    )
    assert course.is_active == is_active_expected
```

## Advanced Pytest Techniques

### Custom Markers for Authentication

You can create custom pytest markers to automatically apply authentication:

```python
import pytest

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "auth: mark test as requiring authentication")

@pytest.fixture(autouse=True)
def auto_auth(request, authenticated_client, authenticated_api_client):
    """Automatically authenticate when using the auth marker."""
    if request.node.get_closest_marker('auth'):
        # The fixture will be applied automatically
        pass
```

Then use it like this:

```python
@pytest.mark.auth
def test_protected_view():
    """This test will automatically have authenticated clients."""
    # No need to explicitly use authenticated_client
    # The client is automatically authenticated
```

### Mocking Authentication Backend

You can mock the entire authentication backend:

```python
@pytest.fixture
def mock_jwt_authentication(monkeypatch):
    """Mock JWT authentication to always authenticate as the test user."""
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from django.contrib.auth.models import AnonymousUser
    
    def get_user(self, validated_token):
        """Return the test user regardless of token."""
        user = User.objects.get(username='testuser')
        return user
    
    def authenticate(self, request):
        """Always authenticate as the test user."""
        user = User.objects.get(username='testuser')
        return (user, None)
    
    monkeypatch.setattr(JWTAuthentication, 'get_user', get_user)
    monkeypatch.setattr(JWTAuthentication, 'authenticate', authenticate)
```

## Running Tests with Pytest

```bash
# Run all tests
pytest

# Run only template tests
pytest -m template

# Run only API tests
pytest -m api

# Run only integration tests
pytest -m integration

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=courses --cov-report=term-missing
```

## Benefits of Pytest Approach

1. **Fixture Reuse**: Fixtures can be reused across multiple tests, reducing duplication
2. **Parametrized Tests**: Test multiple scenarios with a single test function
3. **Better Isolation**: Each test gets its own set of fixtures, improving isolation
4. **Powerful Mocking**: Monkeypatching and fixture mocking simplify complex scenarios
5. **Cleaner Syntax**: Assert statements are more readable than assertEqual
6. **Detailed Failures**: Pytest provides more detailed information when tests fail
7. **Plugin Ecosystem**: A rich ecosystem of plugins for features like coverage, parallel execution, etc.

## How This Addresses Our Authentication Issues

The main challenge we've been facing is that our views and APIs require JWT authentication, which our tests aren't providing. By using pytest, we can:

1. **Override Settings**: Configure test-specific settings that disable authentication requirements
2. **Provide Authentication Automatically**: Use fixtures to automatically authenticate test clients
3. **Mock Authentication Backend**: Bypass the actual authentication logic entirely
4. **Parametrize Authentication Scenarios**: Test different authentication scenarios easily

This comprehensive approach ensures that our tests work correctly without modifying our actual production code.