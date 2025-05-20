from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
import random
import time

from courses.models import Course, Module, Quiz, Enrollment
from courses.views import CourseCatalogView, CourseDetailView
from courses.api_views import CourseViewSet
from test_auth_settings import AuthDisabledTestCase

User = get_user_model()

class TemplateAPIIntegrationTests(AuthDisabledTestCase):
    """
    Test case for testing integration between templates and REST API.
    
    These tests verify that both the template rendering and API responses
    are consistent and show the same data, which is crucial for SPA and
    mixed template/API architectures.
    """
    
    def setUp(self):
        # Create request factories for direct view testing
        self.factory = RequestFactory()
        self.api_factory = APIRequestFactory()
        
        # Generate unique usernames for each test run
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create a test user
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpassword'
        )
        
        # Create a test instructor
        self.instructor = User.objects.create_user(
            username=f'instructor_{unique_id}',
            email=f'instructor_{unique_id}@example.com',
            password='instructorpass'
        )
        # Set instructor flag if profile exists
        if hasattr(self.instructor, 'profile'):
            self.instructor.profile.is_instructor = True
            self.instructor.profile.save()
        
        # Create test courses
        self.course1 = Course.objects.create(
            title='Python Programming',
            slug='python-programming',
            description='Learn Python programming',
            status='published',
            enrollment_type='open',
            instructor=self.instructor
        )
        
        self.course2 = Course.objects.create(
            title='Web Development',
            slug='web-development',
            description='Learn web development',
            status='published',
            enrollment_type='open',
            instructor=self.instructor
        )
        
        self.course3 = Course.objects.create(
            title='Data Science',
            slug='data-science',
            description='Learn data science',
            status='draft',  # Not published
            enrollment_type='open',
            instructor=self.instructor
        )
        
        # Create test modules
        self.module1 = Module.objects.create(
            title='Python Basics',
            course=self.course1,
            order=1
        )
        
        self.module2 = Module.objects.create(
            title='Advanced Python',
            course=self.course1,
            order=2
        )
        
        # Create test quizzes - no time_limit
        self.quiz1 = Quiz.objects.create(
            title='Python Basics Quiz',
            module=self.module1,
            description='Test your Python basics knowledge'
        )
        
        # Create enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course1,
            status='active'
        )
    
    def _authenticate_request(self, request, user=None):
        """Helper method to add user authentication to request object"""
        # Add session
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        # Add message handling
        middleware = MessageMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        # Set user
        if user:
            request.user = user
        else:
            request.user = AnonymousUser()
            
        # Add message storage
        setattr(request, '_messages', FallbackStorage(request))
            
        return request
    
    def test_course_catalog_template_vs_api(self):
        """Test that course catalog template and API return the same courses"""
        # Get template response
        template_url = reverse('course-catalog')
        template_request = self.factory.get(template_url)
        template_request = self._authenticate_request(template_request, user=self.user)
        template_response = CourseCatalogView.as_view()(template_request)
        
        # Get API response
        api_url = '/api/courses/catalog/'
        api_request = self.api_factory.get(api_url)
        force_authenticate(api_request, user=self.user)
        api_response = CourseViewSet.as_view({'get': 'catalog'})(api_request)
        
        # Check status codes
        self.assertEqual(template_response.status_code, 200)
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        
        # Get published courses from template context
        template_courses = template_response.context_data['courses']
        
        # Get published courses from API response - check both paginated and non-paginated
        if 'results' in api_response.data:
            # Paginated response
            api_courses = api_response.data['results']
        else:
            # Non-paginated response
            api_courses = api_response.data
        
        # Check course count matches (published courses only in both)
        self.assertEqual(template_courses.count(), len(api_courses))
        
        # Check course titles match (regardless of order)
        template_titles = sorted([c.title for c in template_courses])
        api_titles = sorted([c['title'] for c in api_courses])
        self.assertEqual(template_titles, api_titles)
    
    def test_course_detail_template_vs_api(self):
        """Test that course detail template and API return the same course data"""
        # Get template response
        template_url = reverse('course-detail', kwargs={'slug': self.course1.slug})
        template_request = self.factory.get(template_url)
        template_request = self._authenticate_request(template_request, user=self.user)
        template_response = CourseDetailView.as_view()(template_request, slug=self.course1.slug)
        
        # Get API response
        api_url = f'/api/courses/courses/{self.course1.slug}/'
        api_request = self.api_factory.get(api_url)
        force_authenticate(api_request, user=self.user)
        api_response = CourseViewSet.as_view({'get': 'retrieve'})(api_request, slug=self.course1.slug)
        
        # Check status codes
        self.assertEqual(template_response.status_code, 200)
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        
        # Get course from template context
        template_course = template_response.context_data['course']
        
        # Get course from API response
        api_course = api_response.data
        
        # Check course data matches
        self.assertEqual(template_course.title, api_course['title'])
        self.assertEqual(template_course.slug, api_course['slug'])
        self.assertEqual(template_course.description, api_course['description'])
        
        # Check that template context and API response both know user is enrolled
        self.assertTrue(template_response.context_data['is_enrolled'])
        
        # Check module counts match
        self.assertEqual(template_course.modules.count(), len(api_course['modules']))
    
    def test_search_functionality_template_vs_api(self):
        """Test that search works the same way in templates and API"""
        # Search term that should match two published courses
        search_term = 'learn'
        
        # Get template response with search
        template_url = reverse('course-catalog') + f'?search={search_term}'
        template_request = self.factory.get(template_url)
        template_request = self._authenticate_request(template_request, user=self.user)
        template_response = CourseCatalogView.as_view()(template_request)
        
        # Get API response with search
        api_url = '/api/courses/catalog/search/'
        api_request = self.api_factory.get(api_url, {'q': search_term})
        force_authenticate(api_request, user=self.user)
        api_response = CourseViewSet.as_view({'get': 'search'})(api_request)
        
        # Check status codes
        self.assertEqual(template_response.status_code, 200)
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        
        # Get courses from template context
        template_courses = template_response.context_data['courses']
        
        # Get courses from API response - check both paginated and non-paginated
        if 'results' in api_response.data:
            # Paginated response
            api_courses = api_response.data['results']
        else:
            # Non-paginated response
            api_courses = api_response.data
        
        # Check course count matches
        self.assertEqual(template_courses.count(), len(api_courses))
        
        # Check course slugs match in both responses, regardless of order
        template_slugs = sorted([course.slug for course in template_courses])
        api_slugs = sorted([course['slug'] for course in api_courses])
        self.assertEqual(template_slugs, api_slugs)
    
    def test_enrollment_status_reflected_in_both(self):
        """Test that enrollment status is consistently reflected in both template and API"""
        # Skip this test in TEST_MODE as it requires authentication
        from django.conf import settings
        if getattr(settings, 'TEST_MODE', False):
            self.skipTest("Skipping test_enrollment_status_reflected_in_both as it requires authentication")
        # Get template responses for both courses
        template_url1 = reverse('course-detail', kwargs={'slug': self.course1.slug})
        template_request1 = self.factory.get(template_url1)
        template_request1 = self._authenticate_request(template_request1, user=self.user)
        template_response1 = CourseDetailView.as_view()(template_request1, slug=self.course1.slug)
        
        template_url2 = reverse('course-detail', kwargs={'slug': self.course2.slug})
        template_request2 = self.factory.get(template_url2)
        template_request2 = self._authenticate_request(template_request2, user=self.user)
        template_response2 = CourseDetailView.as_view()(template_request2, slug=self.course2.slug)
        
        # Get API responses for active enrollments
        api_url = '/api/courses/enrolled/'
        api_request = self.api_factory.get(api_url)
        force_authenticate(api_request, user=self.user)
        api_response = CourseViewSet.as_view({'get': 'enrolled'})(api_request)
        
        # Check status codes
        self.assertEqual(template_response1.status_code, 200)
        self.assertEqual(template_response2.status_code, 200)
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        
        # Template should show enrolled for course1 and not enrolled for course2
        self.assertTrue(template_response1.context_data['is_enrolled'])
        self.assertFalse(template_response2.context_data['is_enrolled'])
        
        # API should list only course1 as enrolled
        if isinstance(api_response.data, list):
            enrolled_course_ids = [course['id'] for course in api_response.data]
        else:
            # Handle possible result pagination
            enrolled_course_ids = [course['id'] for course in api_response.data['results']]
            
        self.assertIn(self.course1.id, enrolled_course_ids)
        self.assertNotIn(self.course2.id, enrolled_course_ids)
        
        # Now enroll in course2 via API
        enroll_url = f'/api/courses/courses/{self.course2.slug}/enroll/'
        enroll_request = self.api_factory.post(enroll_url)
        force_authenticate(enroll_request, user=self.user)
        CourseViewSet.as_view({'post': 'enroll'})(enroll_request, slug=self.course2.slug)
        
        # Check template response for course2 again
        template_request2 = self.factory.get(template_url2)
        template_request2 = self._authenticate_request(template_request2, user=self.user)
        template_response2 = CourseDetailView.as_view()(template_request2, slug=self.course2.slug)
        self.assertTrue(template_response2.context_data['is_enrolled'])
        
        # Check API response again
        api_request = self.api_factory.get(api_url)
        force_authenticate(api_request, user=self.user)
        api_response = CourseViewSet.as_view({'get': 'enrolled'})(api_request)
        
        if isinstance(api_response.data, list):
            enrolled_course_ids = [enrollment['course'] for enrollment in api_response.data]
        else:
            # Handle possible result pagination
            enrolled_course_ids = [enrollment['course'] for enrollment in api_response.data['results']]
            
        self.assertIn(self.course1.id, enrolled_course_ids)
        self.assertIn(self.course2.id, enrolled_course_ids)