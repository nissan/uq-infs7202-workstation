from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json
from courses.models import Course, Module, Quiz, Enrollment

User = get_user_model()

class TemplateAPIIntegrationTests(TestCase):
    """
    Test case for testing integration between templates and REST API.
    
    These tests verify that both the template rendering and API responses
    are consistent and show the same data, which is crucial for SPA and
    mixed template/API architectures.
    """
    
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
        # Setup instructor profile if exists
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
        
        # Setup clients
        self.client = Client()
        self.api_client = APIClient()
        
        # Create enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course1,
            status='active'
        )
    
    def test_course_catalog_template_vs_api(self):
        """Test that course catalog template and API return the same courses"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        self.api_client.force_authenticate(user=self.user)
        
        # Get template response
        template_url = reverse('course-catalog')
        template_response = self.client.get(template_url)
        
        # Get API response
        api_url = '/api/courses/catalog/'
        api_response = self.api_client.get(api_url)
        
        # Check status codes
        self.assertEqual(template_response.status_code, 200)
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        
        # Get published courses from template context
        template_courses = template_response.context['courses']
        
        # Get published courses from API response
        api_courses = api_response.data['results']
        
        # Check course count matches (published courses only in both)
        self.assertEqual(template_courses.count(), len(api_courses))
        
        # Check course titles match (regardless of order)
        template_titles = sorted([c.title for c in template_courses])
        api_titles = sorted([c['title'] for c in api_courses])
        self.assertEqual(template_titles, api_titles)
    
    def test_course_detail_template_vs_api(self):
        """Test that course detail template and API return the same course data"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        self.api_client.force_authenticate(user=self.user)
        
        # Get template response
        template_url = reverse('course-detail', kwargs={'slug': self.course1.slug})
        template_response = self.client.get(template_url)
        
        # Get API response
        api_url = f'/api/courses/courses/{self.course1.slug}/'
        api_response = self.api_client.get(api_url)
        
        # Check status codes
        self.assertEqual(template_response.status_code, 200)
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        
        # Get course from template context
        template_course = template_response.context['course']
        
        # Get course from API response
        api_course = api_response.data
        
        # Check course data matches
        self.assertEqual(template_course.title, api_course['title'])
        self.assertEqual(template_course.slug, api_course['slug'])
        self.assertEqual(template_course.description, api_course['description'])
        
        # Check that template context and API response both know user is enrolled
        self.assertTrue(template_response.context['is_enrolled'])
        
        # Check module counts match
        self.assertEqual(template_course.modules.count(), len(api_course['modules']))
    
    def test_search_functionality_template_vs_api(self):
        """Test that search works the same way in templates and API"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        self.api_client.force_authenticate(user=self.user)
        
        # Search term that should match two published courses
        search_term = 'learn'
        
        # Get template response with search
        template_url = reverse('course-catalog') + f'?search={search_term}'
        template_response = self.client.get(template_url)
        
        # Get API response with search
        api_url = '/api/courses/catalog/search/' + f'?q={search_term}'
        api_response = self.api_client.get(api_url)
        
        # Check status codes
        self.assertEqual(template_response.status_code, 200)
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        
        # Get courses from template context
        template_courses = template_response.context['courses']
        
        # Get courses from API response
        api_courses = api_response.data['results']
        
        # Both should return the published courses that match the search term
        self.assertEqual(template_courses.count(), len(api_courses))
        
        # Check course slugs match in both responses, regardless of order
        template_slugs = sorted([course.slug for course in template_courses])
        api_slugs = sorted([course['slug'] for course in api_courses])
        self.assertEqual(template_slugs, api_slugs)
    
    def test_enrollment_status_reflected_in_both(self):
        """Test that enrollment status is consistently reflected in both template and API"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        self.api_client.force_authenticate(user=self.user)
        
        # Get template responses for both courses
        template_url1 = reverse('course-detail', kwargs={'slug': self.course1.slug})
        template_response1 = self.client.get(template_url1)
        
        template_url2 = reverse('course-detail', kwargs={'slug': self.course2.slug})
        template_response2 = self.client.get(template_url2)
        
        # Get API responses for active enrollments
        api_url = '/api/courses/enrolled/'
        api_response = self.api_client.get(api_url)
        
        # Check status codes
        self.assertEqual(template_response1.status_code, 200)
        self.assertEqual(template_response2.status_code, 200)
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        
        # Template should show enrolled for course1 and not enrolled for course2
        self.assertTrue(template_response1.context['is_enrolled'])
        self.assertFalse(template_response2.context['is_enrolled'])
        
        # API should list only course1 as enrolled
        enrolled_course_ids = [enrollment['course'] for enrollment in api_response.data]
        self.assertIn(self.course1.id, enrolled_course_ids)
        self.assertNotIn(self.course2.id, enrolled_course_ids)
        
        # Now enroll in course2 via API
        self.api_client.post(f'/api/courses/courses/{self.course2.slug}/enroll/')
        
        # Check template response for course2 again
        template_response2 = self.client.get(template_url2)
        self.assertTrue(template_response2.context['is_enrolled'])
        
        # Check API response again
        api_response = self.api_client.get(api_url)
        enrolled_course_ids = [enrollment['course'] for enrollment in api_response.data]
        self.assertIn(self.course1.id, enrolled_course_ids)
        self.assertIn(self.course2.id, enrolled_course_ids)