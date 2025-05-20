import django
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from courses.models import Course, Module, Quiz, Enrollment
from test_auth_settings import AuthDisabledTestCase
from api_test_utils import APITestCaseBase

# Temporarily override the REST_FRAMEWORK settings
TEST_REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

User = get_user_model()

@override_settings(REST_FRAMEWORK=TEST_REST_FRAMEWORK)
class SimpleTemplateTest(AuthDisabledTestCase):
    """Test case for basic template rendering"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructorpass'
        )
        # Setup instructor profile if it exists
        if hasattr(self.instructor, 'profile'):
            self.instructor.profile.is_instructor = True
            self.instructor.profile.save()
        
        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='A test course',
            status='published',
            enrollment_type='open',
            instructor=self.instructor
        )
    
    def test_course_catalog_renders(self):
        """Test the course catalog page renders correctly"""
        # Get the page
        response = self.client.get(reverse('course-catalog'))
        
        # Check status code and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course-catalog.html')
        
        # Check the course is in the context
        self.assertIn('courses', response.context)
        self.assertIn(self.course, response.context['courses'])
    
    def test_course_detail_renders(self):
        """Test the course detail page renders correctly"""
        # Get the page
        response = self.client.get(
            reverse('course-detail', kwargs={'slug': self.course.slug})
        )
        
        # Check status code and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course-detail.html')
        
        # Check the course is in the context
        self.assertEqual(response.context['course'], self.course)
        self.assertFalse(response.context['is_enrolled'])


@override_settings(REST_FRAMEWORK=TEST_REST_FRAMEWORK)
class SimpleAPITest(AuthDisabledTestCase):
    """Test case for basic API endpoints"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test instructor
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='instructorpass'
        )
        # Setup instructor profile if it exists
        if hasattr(self.instructor, 'profile'):
            self.instructor.profile.is_instructor = True
            self.instructor.profile.save()
        
        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='A test course',
            status='published',
            enrollment_type='open',
            instructor=self.instructor
        )
        
        # Set up API client
        self.client.handler.enforce_csrf_checks = False
        
        # Get tokens for the user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_course_catalog_api(self):
        """Test the course catalog API returns correct data"""
        # Get the page
        response = self.client.get('/api/courses/catalog/')
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check the course is in the response
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.course.title)
        self.assertEqual(response.data['results'][0]['slug'], self.course.slug)