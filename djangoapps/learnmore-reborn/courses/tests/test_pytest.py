"""
Example pytest-based tests for the courses app.

This file demonstrates how to use pytest with Django REST framework
to properly test both templates and API views, addressing authentication issues.
"""
import pytest
from django.urls import reverse
from rest_framework import status
import json
from test_auth_settings import AuthDisabledTestCase
from api_test_utils import APITestCaseBase
from courses.models import Course

# Mark this module as using pytest fixtures
pytestmark = pytest.mark.django_db


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


# API Tests

@pytest.mark.api
def test_course_catalog_api(authenticated_api_client, course, bypass_auth):
    """Test course catalog API endpoint."""
    # Get the response
    response = authenticated_api_client.get('/api/courses/catalog/')
    
    # Check status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check response data structure
    assert 'results' in response.data
    
    # Check course data
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == course.title
    assert response.data['results'][0]['slug'] == course.slug


@pytest.mark.api
def test_course_detail_api(authenticated_api_client, course, enrollment, bypass_auth):
    """Test course detail API endpoint."""
    # Get the response
    response = authenticated_api_client.get(f'/api/courses/courses/{course.slug}/')
    
    # Check status code
    assert response.status_code == status.HTTP_200_OK
    
    # Check course data
    assert response.data['title'] == course.title
    assert response.data['slug'] == course.slug
    assert response.data['description'] == course.description
    
    # Check modules data is included (CourseDetailSerializer should include modules)
    assert 'modules' in response.data
    assert len(response.data['modules']) == 0  # No modules in the course


@pytest.mark.api
def test_course_enrollment_api(authenticated_api_client, course, bypass_auth):
    """Test course enrollment API functionality."""
    # Enroll in the course
    response = authenticated_api_client.post(f'/api/courses/courses/{course.slug}/enroll/')
    
    # Check status code
    assert response.status_code == status.HTTP_201_CREATED
    
    # Try to enroll again - should fail
    response = authenticated_api_client.post(f'/api/courses/courses/{course.slug}/enroll/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Unenroll from the course
    response = authenticated_api_client.post(f'/api/courses/courses/{course.slug}/unenroll/')
    assert response.status_code == status.HTTP_204_NO_CONTENT


# Integration Tests

@pytest.mark.integration
def test_api_and_template_consistency(authenticated_client, authenticated_api_client, 
                                     course, enrollment, bypass_auth):
    """Test that API and template views return consistent data."""
    # Get API response
    api_url = f'/api/courses/courses/{course.slug}/'
    api_response = authenticated_api_client.get(api_url)
    
    # Get template response
    template_url = reverse('course-detail', kwargs={'slug': course.slug})
    template_response = authenticated_client.get(template_url)
    
    # Compare data
    assert api_response.status_code == status.HTTP_200_OK
    assert template_response.status_code == 200
    
    # Template response should include context with course object
    template_course = template_response.context['course']
    
    # Check core data consistency - API data vs template context data
    assert api_response.data['title'] == template_course.title
    assert api_response.data['slug'] == template_course.slug
    assert api_response.data['description'] == template_course.description


# Parametrized Tests

@pytest.mark.parametrize('enrollment_type,expected_name', [
    ('open', 'Open'),
    ('restricted', 'Restricted'),
])
def test_course_enrollment_type_display(instructor, enrollment_type, expected_name):
    """Test that course enrollment type choices work as expected."""
    course = Course.objects.create(
        title='Test Course',
        enrollment_type=enrollment_type,
        instructor=instructor
    )
    assert course.get_enrollment_type_display() == expected_name