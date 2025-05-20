from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from courses.models import Course, Module, Quiz, Enrollment

User = get_user_model()

class CourseAPITests(TestCase):
    """Test case for course-related API endpoints"""
    
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
        # Setup instructor profile (assuming a UserProfile model exists)
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
        
        # Create test module
        self.module = Module.objects.create(
            title='Test Module',
            course=self.course,
            order=1
        )
        
        # Create test quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            module=self.module,
            time_limit=30
        )
        
        # Set up API client
        self.client = APIClient()

    def test_course_catalog_api(self):
        """Test course catalog API endpoint"""
        # Login as regular user
        self.client.force_authenticate(user=self.user)
        
        # Get the response
        url = reverse('course-catalog')
        response = self.client.get(url)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response data
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.course.title)
        self.assertEqual(response.data['results'][0]['slug'], self.course.slug)

    def test_course_search_api(self):
        """Test course search API endpoint"""
        # Login as regular user
        self.client.force_authenticate(user=self.user)
        
        # Get the response with a search query
        url = reverse('course-search') + '?q=test'
        response = self.client.get(url)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response data - should find our test course
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.course.title)
        
        # Search with a term that shouldn't match
        url = reverse('course-search') + '?q=nonexistent'
        response = self.client.get(url)
        
        # Still returns success, but with empty results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        
        # Search without a query should return error
        url = reverse('course-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_course_detail_api(self):
        """Test course detail API endpoint"""
        # Login as regular user
        self.client.force_authenticate(user=self.user)
        
        # Create enrollment so user can see the course
        Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
        
        # Get the response
        url = reverse('course-detail', kwargs={'slug': self.course.slug})
        response = self.client.get(url)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response data
        self.assertEqual(response.data['title'], self.course.title)
        self.assertEqual(response.data['slug'], self.course.slug)
        
        # Check modules data is included (CourseDetailSerializer should include modules)
        self.assertEqual(len(response.data['modules']), 1)
        self.assertEqual(response.data['modules'][0]['title'], self.module.title)

    def test_course_enrollment_api(self):
        """Test course enrollment API functionality"""
        # Login as regular user
        self.client.force_authenticate(user=self.user)
        
        # Enroll in the course
        url = reverse('course-enroll', kwargs={'slug': self.course.slug})
        response = self.client.post(url)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check enrollment was created
        self.assertTrue(
            Enrollment.objects.filter(
                user=self.user,
                course=self.course,
                status='active'
            ).exists()
        )
        
        # Try to enroll again - should fail
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Unenroll from the course
        url = reverse('course-unenroll', kwargs={'slug': self.course.slug})
        response = self.client.post(url)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check enrollment was updated
        self.assertTrue(
            Enrollment.objects.filter(
                user=self.user,
                course=self.course,
                status='dropped'
            ).exists()
        )
        
        # Try to unenroll again - should fail
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_active_enrollments_api(self):
        """Test active enrollments API endpoint"""
        # Create enrollment
        Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
        
        # Login as regular user
        self.client.force_authenticate(user=self.user)
        
        # Get the response
        url = reverse('enrolled-courses')
        response = self.client.get(url)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response data
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['course'], self.course.id)
        self.assertEqual(response.data[0]['status'], 'active')

    def test_api_and_template_consistency(self):
        """Test that API and template views return consistent data"""
        # Create enrollment so user can access the course
        Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
        
        # Login for both API and template access
        self.client.login(username='testuser', password='testpassword')
        
        # Get API response
        api_url = reverse('course-detail', kwargs={'slug': self.course.slug})
        api_response = self.client.get(api_url, HTTP_ACCEPT='application/json')
        
        # Get template response
        template_url = reverse('course-detail', kwargs={'slug': self.course.slug})
        template_response = self.client.get(template_url, HTTP_ACCEPT='text/html')
        
        # Compare data
        self.assertEqual(api_response.status_code, status.HTTP_200_OK)
        self.assertEqual(template_response.status_code, status.HTTP_200_OK)
        
        # API should return JSON, template should return HTML
        self.assertIn('application/json', api_response['Content-Type'])
        self.assertIn('text/html', template_response['Content-Type'])
        
        # Template response should include context with course object
        self.assertIn('course', template_response.context)
        template_course = template_response.context['course']
        
        # Check core data consistency - API data vs template context data
        self.assertEqual(api_response.data['title'], template_course.title)
        self.assertEqual(api_response.data['slug'], template_course.slug)
        self.assertEqual(api_response.data['description'], template_course.description)