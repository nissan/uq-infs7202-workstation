from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
import random
import time

from courses.models import Course, Module, Quiz, Enrollment
from courses.views import CourseCatalogView, CourseDetailView, ModuleDetailView, QuizDetailView, enroll_course, unenroll_course

User = get_user_model()

class DjangoViewsTestCase(TestCase):
    """Tests for Django template views with DRF authentication disabled"""
    
    def setUp(self):
        # Call parent setUp
        super().setUp()
        
        # Create request factory for direct view testing
        self.factory = RequestFactory()
        
        # Generate unique usernames for each test run
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create an instructor user
        self.instructor = User.objects.create_user(
            username=f'instructor_{unique_id}',
            email=f'instructor_{unique_id}@example.com',
            password='instructorpass'
        )
        self.instructor.profile.is_instructor = True
        self.instructor.profile.save()
        
        # Create a student user
        self.student = User.objects.create_user(
            username=f'student_{unique_id}',
            email=f'student_{unique_id}@example.com',
            password='studentpass'
        )
        
        # Create courses
        self.published_course = Course.objects.create(
            title='Published Course',
            slug='published-course',
            description='Description for published course',
            instructor=self.instructor,
            status='published',
            enrollment_type='open',
            max_students=10
        )
        
        self.draft_course = Course.objects.create(
            title='Draft Course',
            slug='draft-course',
            description='Description for draft course',
            instructor=self.instructor,
            status='draft',
            enrollment_type='open',
            max_students=10
        )
        
        # Create modules
        self.module = Module.objects.create(
            course=self.published_course,
            title='Test Module',
            description='Module description',
            order=1
        )
        
        # Create quiz
        self.quiz = Quiz.objects.create(
            module=self.module,
            title='Test Quiz',
            description='Quiz description',
            is_survey=False
        )
        
        # Create enrollment for student
        self.enrollment = Enrollment.objects.create(
            user=self.student,
            course=self.published_course,
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
            
        return request
    
    def test_course_catalog_anonymous(self):
        """Test course catalog view as anonymous user"""
        # Create a request to the view
        request = self.factory.get(reverse('course-catalog'))
        request = self._authenticate_request(request)
        
        # Get the response directly from the view
        response = CourseCatalogView.as_view()(request)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Since we're using the RequestFactory, we need to attach the response
        # to a test client response for template assertion
        from django.test.client import Client
        client = Client()
        client.cookies = {}
        response.client = client
        
        # Check context data
        self.assertIn('courses', response.context_data)
        
        # Only published courses should be visible
        self.assertEqual(len(response.context_data['courses']), 1)
        self.assertEqual(response.context_data['courses'][0].title, 'Published Course')
    
    def test_course_catalog_instructor(self):
        """Test course catalog view as instructor with status filter"""
        # Create a request with status filters that instructors can see
        url = reverse('course-catalog') + '?status=draft&status=published'
        request = self.factory.get(url)
        request = self._authenticate_request(request, user=self.instructor)
        
        # Get the response directly from the view
        response = CourseCatalogView.as_view()(request)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Attach test client for template assertions
        from django.test.client import Client
        client = Client()
        client.cookies = {}
        response.client = client
        
        # Both courses should be visible with status filter
        self.assertEqual(len(response.context_data['courses']), 2)
    
    def test_course_detail_published(self):
        """Test course detail view for published course"""
        url = reverse('course-detail', kwargs={'slug': self.published_course.slug})
        request = self.factory.get(url)
        request = self._authenticate_request(request)
        
        # Get the response directly from the view
        response = CourseDetailView.as_view()(request, slug=self.published_course.slug)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Attach test client for template assertions
        from django.test.client import Client
        client = Client()
        client.cookies = {}
        response.client = client
        
        # Verify the course details
        self.assertEqual(response.context_data['course'].title, 'Published Course')
    
    def test_course_detail_enrolled(self):
        """Test course detail view when user is enrolled"""
        url = reverse('course-detail', kwargs={'slug': self.published_course.slug})
        request = self.factory.get(url)
        request = self._authenticate_request(request, user=self.student)
        
        # Get the response directly from the view
        response = CourseDetailView.as_view()(request, slug=self.published_course.slug)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Attach test client for template assertions
        from django.test.client import Client
        client = Client()
        client.cookies = {}
        response.client = client
        
        # Verify student is shown as enrolled
        self.assertTrue(response.context_data['is_enrolled'])
    
    def test_module_detail_unauthenticated(self):
        """Test module detail view redirects unauthenticated users to login"""
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        request = self.factory.get(url)
        request = self._authenticate_request(request)
        
        # Get the response directly from the view
        response = ModuleDetailView.as_view()(request, pk=self.module.pk)
        
        # Verify the redirection to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_module_detail_enrolled_student(self):
        """Test module detail view for enrolled student"""
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        request = self.factory.get(url)
        request = self._authenticate_request(request, user=self.student)
        
        # Get the response directly from the view
        response = ModuleDetailView.as_view()(request, pk=self.module.pk)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Attach test client for template assertions
        from django.test.client import Client
        client = Client()
        client.cookies = {}
        response.client = client
        
        # Verify student has access and is shown as enrolled
        self.assertTrue(response.context_data['is_enrolled'])
    
    def test_module_detail_instructor(self):
        """Test module detail view for instructor (not enrolled but has access)"""
        url = reverse('module-detail', kwargs={'pk': self.module.pk})
        request = self.factory.get(url)
        request = self._authenticate_request(request, user=self.instructor)
        
        # Get the response directly from the view
        response = ModuleDetailView.as_view()(request, pk=self.module.pk)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
    
    def test_quiz_detail_unauthenticated(self):
        """Test quiz detail view redirects unauthenticated users to login"""
        url = reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        request = self.factory.get(url)
        request = self._authenticate_request(request)
        
        # Get the response directly from the view
        response = QuizDetailView.as_view()(request, pk=self.quiz.pk)
        
        # Verify the redirection to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_quiz_detail_enrolled_student(self):
        """Test quiz detail view for enrolled student"""
        url = reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        request = self.factory.get(url)
        request = self._authenticate_request(request, user=self.student)
        
        # Get the response directly from the view
        response = QuizDetailView.as_view()(request, pk=self.quiz.pk)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
    
    def test_quiz_detail_instructor(self):
        """Test quiz detail view for instructor"""
        url = reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        request = self.factory.get(url)
        request = self._authenticate_request(request, user=self.instructor)
        
        # Get the response directly from the view
        response = QuizDetailView.as_view()(request, pk=self.quiz.pk)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
    
    def test_enroll_unauthenticated(self):
        """Test enrollment redirects unauthenticated users to login"""
        url = reverse('course-enroll', kwargs={'slug': self.published_course.slug})
        request = self.factory.post(url)
        request = self._authenticate_request(request)
        
        # Pass the request to the function-based view
        response = enroll_course(request, slug=self.published_course.slug)
        
        # Verify the redirection to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_enroll_new_student(self):
        """Test successful enrollment for a new student"""
        # Create new student with unique username
        unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        new_student = User.objects.create_user(
            username=f'newstudent_{unique_id}',
            email=f'new_{unique_id}@example.com',
            password='newpass'
        )
        
        url = reverse('course-enroll', kwargs={'slug': self.published_course.slug})
        request = self.factory.post(url)
        request = self._authenticate_request(request, user=new_student)
        
        # Pass the request to the function-based view
        response = enroll_course(request, slug=self.published_course.slug)
        
        # Verify the redirection after enrollment
        self.assertEqual(response.status_code, 302)
        
        # Verify enrollment was created
        self.assertTrue(
            Enrollment.objects.filter(
                user=new_student,
                course=self.published_course,
                status='active'
            ).exists()
        )
    
    def test_enroll_already_enrolled(self):
        """Test enrollment for user already enrolled shows message"""
        url = reverse('course-enroll', kwargs={'slug': self.published_course.slug})
        request = self.factory.post(url)
        request = self._authenticate_request(request, user=self.student)
        
        # Pass the request to the function-based view
        response = enroll_course(request, slug=self.published_course.slug)
        
        # Verify the redirection after attempted enrollment
        self.assertEqual(response.status_code, 302)
        
        # Check that no additional enrollments were created
        self.assertEqual(
            Enrollment.objects.filter(
                user=self.student,
                course=self.published_course
            ).count(),
            1
        )
    
    def test_unenroll_enrolled_student(self):
        """Test successful unenrollment for an enrolled student"""
        url = reverse('course-unenroll', kwargs={'slug': self.published_course.slug})
        request = self.factory.post(url)
        request = self._authenticate_request(request, user=self.student)
        
        # Pass the request to the function-based view
        response = unenroll_course(request, slug=self.published_course.slug)
        
        # Verify the redirection after unenrollment
        self.assertEqual(response.status_code, 302)
        
        # Verify enrollment status is updated
        enrollment = Enrollment.objects.get(
            user=self.student,
            course=self.published_course
        )
        self.assertEqual(enrollment.status, 'dropped')