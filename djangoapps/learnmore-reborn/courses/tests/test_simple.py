import django
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient, APITestCase
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

from unittest.mock import patch, Mock
from django.test import RequestFactory

# Create a much simpler test case that directly uses the views
class SimpleTemplateTest(TestCase):
    """Test case for basic template rendering"""
    
    def setUp(self):
        # Call parent setUp first
        super().setUp()
        
        import random
        import time
        # Generate unique usernames for each test run
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create test user
        self.user = User.objects.create_user(
            username=f'testuser_simple_{unique_id}',
            email=f'test_simple_{unique_id}@example.com',
            password='testpassword'
        )
        
        # Create test instructor
        self.instructor = User.objects.create_user(
            username=f'instructor_simple_{unique_id}',
            email=f'instructor_simple_{unique_id}@example.com',
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
        # Create a direct request to the view
        from courses.views import CourseCatalogView
        
        # Create a request factory
        factory = RequestFactory()
        request = factory.get(reverse('course-catalog'))
        
        # Add user authentication attributes
        request.user = self.user
        
        # Get response
        response = CourseCatalogView.as_view()(request)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
    
    def test_course_detail_renders(self):
        """Test the course detail page renders correctly"""
        # Create a direct request to the view
        from courses.views import CourseDetailView
        
        # Create a request factory
        factory = RequestFactory()
        request = factory.get(reverse('course-detail', kwargs={'slug': self.course.slug}))
        
        # Add user authentication attributes
        request.user = self.user
        
        # Get response
        response = CourseDetailView.as_view()(request, slug=self.course.slug)
        
        # Check status code
        self.assertEqual(response.status_code, 200)


from django.test.utils import override_settings

@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
})
class SimpleAPITest(APITestCase):
    """Test case for basic API endpoints"""
    
    def setUp(self):
        # Call parent setUp first
        super().setUp()
        
        import random
        import time
        # Generate unique usernames for each test run
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create test user
        self.user = User.objects.create_user(
            username=f'testuser_api_{unique_id}',
            email=f'test_api_{unique_id}@example.com',
            password='testpassword'
        )
        
        # Create test instructor
        self.instructor = User.objects.create_user(
            username=f'instructor_api_{unique_id}',
            email=f'instructor_api_{unique_id}@example.com',
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
        
        # Set up API client - Use the built-in client from APITestCase
        self.client.enforce_csrf_checks = False
        
        # Authenticate with the user
        self.client.force_authenticate(user=self.user)
    
    def test_course_catalog_api(self):
        """Test the course catalog API returns correct data"""
        # Get the page
        response = self.client.get('/api/courses/catalog/')
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check the course is in the response - pagination might be enabled or not
        if 'results' in response.data:
            # Paginated response
            self.assertTrue('results' in response.data)
            courses = response.data['results']
        else:
            # Non-paginated response
            courses = response.data
            
        # Ensure we have at least one course (our test course)
        self.assertGreaterEqual(len(courses), 1)
        
        # Find our test course in the results
        found_course = False
        for course in courses:
            if course['slug'] == self.course.slug:
                self.assertEqual(course['title'], self.course.title)
                found_course = True
                break
                
        self.assertTrue(found_course, "Test course not found in API response")