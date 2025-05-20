"""
Pytest configuration and fixtures for the courses app.

This file provides fixtures for use in pytest-based tests. These fixtures set up
test data, authentication, and other test requirements.
"""
import pytest
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken
from courses.models import Course, Module, Quiz, Enrollment
from test_auth_settings import AuthDisabledTestCase
from api_test_utils import APITestCaseBase

User = get_user_model()

# Client fixtures

@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()

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

@pytest.fixture
def instructor_client(client, instructor):
    """Return a Django test client with a logged in instructor."""
    client.login(username='instructor', password='instructorpass')
    return client

@pytest.fixture
def instructor_api_client(api_client, instructor):
    """Return an API client with a logged in instructor."""
    refresh = RefreshToken.for_user(instructor)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

# User fixtures

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

# Model fixtures

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
def draft_course(instructor):
    """Create and return a draft course."""
    return Course.objects.create(
        title='Draft Course',
        slug='draft-course',
        description='A draft course',
        status='draft',
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

# Authentication bypass fixtures

@pytest.fixture
def bypass_auth(monkeypatch):
    """Bypass authentication checks in views and APIs."""
    from rest_framework.permissions import IsAuthenticated
    
    # Make IsAuthenticated always return True
    def has_permission(*args, **kwargs):
        return True
    
    monkeypatch.setattr(IsAuthenticated, 'has_permission', has_permission)
    
    # For custom permissions
    try:
        from courses.api_views import IsInstructorOrReadOnly
        monkeypatch.setattr(IsInstructorOrReadOnly, 'has_permission', has_permission)
        monkeypatch.setattr(IsInstructorOrReadOnly, 'has_object_permission', has_permission)
    except ImportError:
        pass  # Module or class not found, skip patching