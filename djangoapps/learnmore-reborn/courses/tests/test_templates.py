from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
import random
import time

from courses.models import Course, Module, Quiz, Enrollment
from courses.views import CourseCatalogView, CourseDetailView, ModuleDetailView, QuizDetailView, enroll_course, unenroll_course

User = get_user_model()

class CourseTemplateTests(TestCase):
    """Test case for course-related templates"""
    
    def setUp(self):
        # Create request factory for direct view testing
        self.factory = RequestFactory()
        
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
        
        # Create test quiz - without time_limit
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            module=self.module,
            description='Test quiz description'
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

    def test_course_catalog_renders(self):
        """Test course catalog page renders correctly"""
        # Create a request to the view
        url = reverse('course-catalog')
        request = self.factory.get(url)
        request = self._authenticate_request(request)
        
        # Get the response directly from the view
        response = CourseCatalogView.as_view()(request)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Attach test client for template assertions
        from django.test.client import Client
        client = Client()
        client.cookies = {}
        response.client = client
        
        # Check context data
        self.assertIn('courses', response.context_data)
        self.assertEqual(list(response.context_data['courses']), [self.course])

    def test_course_detail_renders(self):
        """Test course detail page renders correctly"""
        # Create a request to the view
        url = reverse('course-detail', kwargs={'slug': self.course.slug})
        request = self.factory.get(url)
        request = self._authenticate_request(request)
        
        # Get the response directly from the view
        response = CourseDetailView.as_view()(request, slug=self.course.slug)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Attach test client for template assertions
        from django.test.client import Client
        client = Client()
        client.cookies = {}
        response.client = client
        
        # Check context data
        self.assertEqual(response.context_data['course'], self.course)
        self.assertFalse(response.context_data['is_enrolled'])

    def test_module_detail_requires_login(self):
        """Test module detail page requires login"""
        # Create a request to the view without authentication
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        request = self.factory.get(url)
        request = self._authenticate_request(request)  # Anonymous user
        
        # Get the response directly from the view
        response = ModuleDetailView.as_view()(request, pk=self.module.pk)
        
        # Check redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_module_detail_requires_enrollment(self):
        """Test module detail page requires enrollment"""
        # Create a request from an authenticated user who is not enrolled
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        request = self.factory.get(url)
        request = self._authenticate_request(request, user=self.user)  # Not enrolled
        
        # Set flag to enable enrollment check even in test mode
        request._require_enrollment_check = True
        
        # Get the response directly from the view
        from django.conf import settings
        old_test_mode = getattr(settings, 'TEST_MODE', False)
        settings.TEST_MODE = False  # Temporarily disable test mode
        
        try:
            response = ModuleDetailView.as_view()(request, pk=self.module.pk)
            # Check redirect to course detail
            self.assertEqual(response.status_code, 302)
        finally:
            # Restore previous test mode setting
            settings.TEST_MODE = old_test_mode

    def test_module_detail_renders_when_enrolled(self):
        """Test module detail page renders when enrolled"""
        # Create enrollment
        Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='active'
        )
        
        # Create a request from an enrolled user
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        request = self.factory.get(url)
        request = self._authenticate_request(request, user=self.user)
        
        # Get the response directly from the view
        response = ModuleDetailView.as_view()(request, pk=self.module.pk)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Attach test client for template assertions
        from django.test.client import Client
        client = Client()
        client.cookies = {}
        response.client = client
        
        # Check context data
        self.assertEqual(response.context_data['module'], self.module)
        self.assertTrue(response.context_data['is_enrolled'])

    def test_quiz_detail_requires_login(self):
        """Test quiz detail page requires login"""
        # Create a request to the view without authentication
        url = reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        request = self.factory.get(url)
        request = self._authenticate_request(request)  # Anonymous user
        
        # Get the response directly from the view
        response = QuizDetailView.as_view()(request, pk=self.quiz.pk)
        
        # Check redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_enrollment_functionality(self):
        """Test enrollment and unenrollment functionality"""
        # Test enrollment
        url = reverse('course-enroll', kwargs={'slug': self.course.slug})
        request = self.factory.post(url)
        request = self._authenticate_request(request, user=self.user)
        
        # Get the response directly from the view
        response = enroll_course(request, slug=self.course.slug)
        
        # Check redirect after enrollment
        self.assertEqual(response.status_code, 302)
        
        # Check enrollment was created
        self.assertTrue(
            Enrollment.objects.filter(
                user=self.user,
                course=self.course,
                status='active'
            ).exists()
        )
        
        # Test unenrollment
        url = reverse('course-unenroll', kwargs={'slug': self.course.slug})
        request = self.factory.post(url)
        request = self._authenticate_request(request, user=self.user)
        
        # Get the response directly from the view
        response = unenroll_course(request, slug=self.course.slug)
        
        # Check redirect after unenrollment
        self.assertEqual(response.status_code, 302)
        
        # Check enrollment status was updated
        self.assertTrue(
            Enrollment.objects.filter(
                user=self.user,
                course=self.course,
                status='dropped'
            ).exists()
        )