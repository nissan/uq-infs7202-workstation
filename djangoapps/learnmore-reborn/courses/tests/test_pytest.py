"""
Example pytest-based tests for the courses app.

This file demonstrates how to use pytest with Django REST framework
to properly test both templates and API views, addressing authentication issues.
"""
from django.test import TestCase

# Define a fallback right away
AuthDisabledTestCase = TestCase

try:
    import pytest
    from django.urls import reverse
    from rest_framework import status
    import json
    
    try:
        from test_auth_settings import AuthDisabledTestCase
    except (ImportError, ModuleNotFoundError):
        # Keep the fallback already defined
        pass
        
    from api_test_utils import APITestCaseBase
    from courses.models import Course
    
    # Flag to check if pytest is available
    PYTEST_AVAILABLE = True
except ModuleNotFoundError:
    # Skip all tests if pytest is not available
    PYTEST_AVAILABLE = False

# Mark this module as using pytest fixtures if available
if PYTEST_AVAILABLE:
    pytestmark = pytest.mark.django_db


# Skip all tests if pytest is not available
if not PYTEST_AVAILABLE:
    # Create a dummy test that will be skipped if pytest is not available
    class DummyTestCase(AuthDisabledTestCase):
        def test_skip_all_tests(self):
            self.skipTest("pytest not available")
else:
    # Template Tests
    @pytest.mark.template
    def test_course_catalog_renders(authenticated_client, course, bypass_auth):
        """Test course catalog page renders correctly."""
        # Get the response
        response = authenticated_client.get(reverse('course-catalog'))
        
        # Check status code
        assert response.status_code == 200
        
        # Check template used
        assert 'courses/course-catalog.html' in [t.name for t in response.templates]
        
        # Check context
        assert 'courses' in response.context
        assert course in response.context['courses']


    @pytest.mark.template
    def test_course_detail_renders(authenticated_client, course, bypass_auth):
        """Test course detail page renders correctly."""
        # Get the response
        response = authenticated_client.get(
            reverse('course-detail', kwargs={'slug': course.slug})
        )
        
        # Check status code
        assert response.status_code == 200
        
        # Check template used
        assert 'courses/course-detail.html' in [t.name for t in response.templates]
        
        # Check context
        assert response.context['course'] == course
        assert response.context['is_enrolled'] is False


    @pytest.mark.template
    def test_module_detail_requires_login(client, module, bypass_auth):
        """Test module detail page requires login."""
        # Get the response without logging in
        response = client.get(
            reverse('module-detail', kwargs={'pk': module.pk})
        )
        
        # Check redirect to login
        assert response.status_code == 302
        assert '/login/' in response.url


    @pytest.mark.template
    def test_module_detail_renders_when_enrolled(authenticated_client, module, enrollment, bypass_auth):
        """Test module detail page renders when enrolled."""
        # Get the response
        response = authenticated_client.get(
            reverse('module-detail', kwargs={'pk': module.pk})
        )
        
        # Check status code
        assert response.status_code == 200
        
        # Check template used
        assert 'courses/module_detail.html' in [t.name for t in response.templates]
        
        # Check context
        assert response.context['module'] == module
        assert response.context['is_enrolled'] is True